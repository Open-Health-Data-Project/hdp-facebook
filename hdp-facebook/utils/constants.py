import pathlib
import re
import csv

# relative paths to files with data
FRIENDS_PATH = pathlib.Path(r"friends\friends.json")
CONTACTS_PATH = pathlib.Path(r"about_you\your_address_books.json")
COMMENTS_PATH = pathlib.Path(r"comments\comments.json")
INTERESTS_PATH = pathlib.Path(r"ads_and_businesses\ads_interests.json")
SEARCH_HISTORY_PATH = pathlib.Path(r"search_history\your_search_history.json")
POSTS_PATH = pathlib.Path(r"posts")
MESSAGES_PATH = pathlib.Path(r"messages")

# patterns used for getting author and users names
PATTERN_USER = re.compile(r"użytkownika (?P<name>((\S*( )?)+))\.")
PATTERN_AUTHOR = re.compile(r"^(?P<name>.*) (odpowiedział|skomentował)")
OWN_COMMENTS = ('swój post.', 'swój własny komentarz.')

# patterns used for getting groups, event and users names
POST_PATTERNS = (re.compile(r"grupie(:)? (?P<group>.*)"), re.compile(r"wydarzeniu(:)? (?P<event>.*)\."),
                             re.compile(r"użytkownika(:)? (?P<user>.*)\."))
PATTERN_POST_AUTHOR = re.compile(r"^(?P<name>.*) (dodał|napisał|utworzył|zmienił)")
OWN_PATTERN = 'swój status.'

# pattern to recognize types of other messages
OTHER_MESSAGE_KEYS = {'photos', 'audio_files', 'gifs', 'files', 'share', 'sticker', 'videos'}

# default value to load all Facebook data that FacebookData can handle
LOAD_ALL = ('friends_and_contacts', 'interests', 'comments', 'search_history', 'posts', 'messages')

# parameters for pandas read_csv and to_csv
SAVE_PROPERTIES = {'sep': ';', 'quoting': csv.QUOTE_NONNUMERIC, 'quotechar': "`"}
LOAD_PROPERTIES = SAVE_PROPERTIES.copy()
LOAD_PROPERTIES.update({'index_col': 0, 'keep_default_na': False})