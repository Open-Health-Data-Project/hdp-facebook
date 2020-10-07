import pandas as pd
import json
from utils.constants import *
from utils.io import *
import os
import glob
from data.FacebookData import FacebookData


class FacebookDataReader:
    def __init__(self):
        self.data = FacebookData()
        self._loaded_threads = set()

    @staticmethod
    def _load_friends(friends_file):
        """
        Read friends list.

        Parameters
        ----------
        friends_file: pathlib.Path or path-like

        Returns
        -------
        DataFrame with loaded data
        """
        with open(friends_file) as f:
            friends = json.load(f)
        friends_list = [
            {'name': better_fix_text(element['name']), 'timestamp': pd.Timestamp(element['timestamp'], unit='s')} for
            element in friends['friends']]
        friends_df = pd.DataFrame(friends_list)
        friends_df = friends_df.set_index('timestamp')
        friends_df['kind'] = 'friend'
        return friends_df

    @staticmethod
    def _load_contacts(contacts_file):
        """
        Read contacts list.

        Parameters
        ----------
        contacts_file: pathlib.Path or path-like

        Returns
        -------
        DataFrame with loaded data
        """
        with open(contacts_file) as f:
            contacts = json.load(f)
        contacts_list = [
            {'name': better_fix_text(element['name']),
             'timestamp': pd.Timestamp(element['created_timestamp'], unit='s')}
            for element in contacts['address_book']['address_book']]
        contacts_df = pd.DataFrame(contacts_list)
        contacts_df = contacts_df.set_index('timestamp')
        contacts_df['kind'] = 'contact'
        return contacts_df

    def _load_friends_and_contacts(self, path):
        """
        Join friends with contacts data.

        Parameters
        ----------
        path: pathlib.Path

        Returns
        -------
        Saves data as a DataFrame to object attribute.
        """
        friends_path = path.joinpath(FRIENDS_PATH)
        contacts_path = path.joinpath(CONTACTS_PATH)
        friends_df = FacebookDataReader._load_friends(friends_path)
        contacts_df = FacebookDataReader._load_contacts(contacts_path)
        self.data.friends_and_contacts = friends_df.append(contacts_df).sort_index()

    def _load_comments(self, path):
        """
        Read comments data.

        Parameters
        ----------
        path: pathlib.Path

        Returns
        -------
        Saves data as a DataFrame to object attribute.

        Notes
        -----
        Regex is used to read additional information. Key name contain author's name. If comment is an answer
         key answer_for should contain original comment author.
        KeyError catches comments which from what ever reason does not contain data.
        """
        comments_path = path.joinpath(COMMENTS_PATH)
        with open(comments_path) as f:
            comments = json.load(f)
        comments_list = []
        for element in comments['comments']:
            try:
                comment = element['data'][0]['comment']
                comment['answer_for'] = ""
                comment['timestamp'] = pd.Timestamp(comment['timestamp'], unit='s')
                title = better_fix_text(element['title'])
                name = re.search(PATTERN_AUTHOR, title).group("name")
                keys = list(comment.keys())
                keys.remove('timestamp')
                results = re.search(PATTERN_USER, title)
                if results:
                    comment['answer_for'] = results.group("name")
                else:
                    for text in OWN_COMMENTS:
                        if title.find(text) != -1:
                            comment['answer_for'] = name
                            break
                for key in keys:
                    comment[key] = better_fix_text(comment[key])
                comments_list.append(comment)
            except KeyError:
                pass
        comments_df = pd.DataFrame(comments_list)
        comments_df = comments_df.set_index('timestamp').sort_index()
        self.data.comments = comments_df

    def _load_interests(self, path):
        """
        Read interests data.

        Parameters
        ----------
        path: pathlib.Path

        Returns
        -------
        Saves data as a list to object attribute.
        """
        interests_path = path.joinpath(INTERESTS_PATH)
        with open(interests_path) as f:
            interests = json.load(f)
        self.data.interests = [better_fix_text(topic) for topic in interests['topics']]

    def _load_search_history(self, path):
        """
        Read search history data.

        Parameters
        ----------
        path: pathlib.Path

        Returns
        -------
        Saves data as a DataFrame to object attribute.

        Notes
        -----
        KeyError catches searches which have their data in attachments key instead of data key.
        """
        search_history_path = path.joinpath(SEARCH_HISTORY_PATH)
        with open(search_history_path) as f:
            search_history = json.load(f)
        search_list = []
        for search in search_history['searches']:
            try:
                search = {'timestamp': pd.Timestamp(search['timestamp'], unit='s'),
                          'text': better_fix_text(search['data'][0]['text'])}
            except KeyError:
                search = {'timestamp': pd.Timestamp(search['timestamp'], unit='s'),
                          'text': better_fix_text(search['attachments'][0]['data'][0]['text']).replace("\"", "")}
            search_list.append(search)
        search_history_df = pd.DataFrame(search_list)
        self.data.search_history = search_history_df.set_index('timestamp').sort_index()

    def _load_posts(self, path):
        """
        Read posts data.

        Parameters
        ----------
        path: pathlib.Path

        Returns
        -------
        Saves data as a DataFrame to object attribute.

        Notes
        -----
        Regex is used to get information about: group, event or user connected to post and author of the post.
        KeyError catches posts without 'data' key. IndexError catches posts with empty lists under the key 'data'.
        """
        posts_path = path.joinpath(POSTS_PATH)
        post_list = []
        for element in os.listdir(posts_path):
            with open(posts_path.joinpath(pathlib.Path(element))) as f:
                posts = json.load(f)
            for post in posts:
                try:
                    post_final = {'timestamp': pd.Timestamp(post['timestamp'], unit='s'),
                                  'text': better_fix_text(post['data'][0]['post'])}
                    title = better_fix_text(post['title'])
                    name = re.search(PATTERN_POST_AUTHOR, title).group("name")
                    post_final['author'] = name
                    for pattern in POST_PATTERNS:
                        results = re.search(pattern, title)
                        if results:
                            kind = list(results.groupdict().keys())[0]
                            kind_name = results[kind]
                            if kind_name.endswith("."):
                                kind_name = kind_name[:-1]
                            elif title.find(OWN_PATTERN) != -1:
                                kind_name = name
                            post_final['in'] = kind_name
                            post_final['kind'] = kind
                    post_list.append(post_final)
                except (KeyError, IndexError):
                    pass
        self.data.posts = pd.DataFrame(post_list).set_index('timestamp').sort_index()

    def _load_messages(self, path):
        """
        Read messages data.

        Parameters
        ----------
        path: pathlib.Path

        Returns
        -------
        Saves data as a DataFrame to object attributes:
        messages - text from messages
        reactions - reactions to messages
        other_messages - messages with photos, stickers, audio_files, files, links and all not text data
        calls - voice calls history
        participants - conversations participants
        groups - groups information

        Notes
        -----
        Path is not multi-system because trailing slash is required for iglob function.
        Regex is used to get information about data other than text.
        """
        messages_path = str(path.joinpath(MESSAGES_PATH)) + "\\"
        messages_list = []
        reactions = []
        others = []
        calls = []
        participants = []
        groups = []
        for filename in glob.iglob(messages_path + '**\*.json', recursive=True):
            with open(filename) as f:
                messages = json.load(f)

            def __count_reactions(m):
                if 'reactions' in list(m.keys()):
                    return len(m['reactions'])
                else:
                    return 0

            current_participants = [{'name': better_fix_text(d['name']), 'thread_id': messages['thread_path']} for d in
                                    messages['participants']]
            if messages['thread_path'] not in self._loaded_threads:
                participants.extend(current_participants)
            if len(current_participants) > 2:
                kind = 'group'
                if messages['thread_path'] not in self._loaded_threads:
                    groups.append({'thread_id': messages['thread_path'], 'title': better_fix_text(messages['title']),
                                   'participants': len(current_participants)})
            else:
                kind = 'dialog'
            self._loaded_threads.add(messages['thread_path'])
            for message in messages['messages']:
                message_data = {'author': better_fix_text(message['sender_name']),
                                'timestamp': pd.Timestamp(message['timestamp_ms'], unit='ms'),
                                'thread_id': messages['thread_path'], 'thread_kind': kind}
                original_message = message_data.copy()
                other_messages = []
                key_set = set(message.keys())
                if 'content' in key_set and message['type'] in ('Generic', 'Share'):
                    message_data['text'] = better_fix_text(message['content'])
                    message_data['reactions'] = __count_reactions(message)
                    messages_list.append(message_data)
                if message['type'] == 'Call':
                    call = original_message.copy()
                    call_duration = message['call_duration']
                    if call_duration:
                        call['call_duration'] = call_duration
                        calls.append(call)
                    elif 'missing' in message.keys():
                        call['call_duration'] = 0
                        calls.append(call)
                if 'reactions' in list(message.keys()):
                    for reaction in message['reactions']:
                        reaction_dict = {'timestamp': pd.Timestamp(message['timestamp_ms'], unit='ms'),
                                         'author': better_fix_text(reaction['actor']),
                                         'thread_id': messages['thread_path'],
                                         'thread_kind': kind, 'reaction': better_fix_text(reaction['reaction'])}
                        reactions.append(reaction_dict)
                for key in OTHER_MESSAGE_KEYS:
                    if key in key_set:
                        other_message = original_message.copy()
                        other_message['count'] = len(message[key])
                        other_message['kind'] = key
                        other_message['reactions'] = __count_reactions(message)
                        other_messages.append(other_message)
                if other_messages:
                    others.extend(other_messages)
        self.data.messages = pd.DataFrame(messages_list).set_index("timestamp").sort_index()
        self.data.reactions = pd.DataFrame(reactions).set_index("timestamp").sort_index()
        self.data.other_messages = pd.DataFrame(others).set_index("timestamp").sort_index()
        self.data.calls = pd.DataFrame(calls).set_index("timestamp").sort_index()
        self.data.participants = pd.DataFrame(participants).sort_values('thread_id').reset_index().drop(columns='index')
        self.data.groups = pd.DataFrame(groups).sort_values('thread_id').reset_index().drop(columns='index')

    def load(self, path, what=()):
        """
        Load data from Facebook exported data.

        Parameters
        ----------
        path: pathlib.Path or path-like
            Path to main directory extracted from zip file.
        what: tuple (optional)
            Tuple of keys that consist data to read from directory. Possible keys are: 'friends_and_contacts',
            'interests', 'comments', 'search_history', 'posts', 'messages'
            Default: all data is read.

        Returns
        -------
        FacebookData object with loaded data.
        """
        read = {'friends_and_contacts': self._load_friends_and_contacts,
                'comments': self._load_comments,
                'interests': self._load_interests,
                'search_history': self._load_search_history,
                'posts': self._load_posts,
                'messages': self._load_messages}
        if not what:
            what = LOAD_ALL
        path = check_if_path(path)
        for element in what:
            read[element](path)
        return self.data



