import pandas as pd
import os
from utils.io import *
from utils.constants import *


class FacebookData:

    # all kinds of data store in FacebookData objects
    data_to_save = [{'friends_and_contacts', 'comments', 'search_history', 'posts', 'messages',
                     'other_messages', 'calls', 'reactions', 'participants', 'groups'},
                    {'interests'}]

    def __init__(self):
        self.friends_and_contacts = pd.DataFrame()
        self.comments = pd.DataFrame()
        self.search_history = pd.DataFrame()
        self.posts = pd.DataFrame()
        self.messages = pd.DataFrame()
        self.other_messages = pd.DataFrame()
        self.calls = pd.DataFrame()
        self.reactions = pd.DataFrame()
        self.participants = pd.DataFrame()
        self.groups = pd.DataFrame()
        self.interests = []

    def save(self, path):
        """
        Save loaded Facebook data to CSV files.

        Parameters
        ----------
        path: pathlib.Path or path-like
            Directory to save data.

        Returns
        -------
        Saves data in the directory.
        """
        path = check_if_path(path)
        for filename in FacebookData.data_to_save[0]:
            f = getattr(self, filename, pd.DataFrame())
            f.to_csv(path.joinpath(filename + '.csv'), **SAVE_PROPERTIES)
        for filename in FacebookData.data_to_save[1]:
            with open(path.joinpath(filename + '.txt'), 'w') as f:
                for element in getattr(self, filename, []):
                    f.write(element + "\n")

    def restore(self, path):
        """
        Reload saved data from disk.

        Parameters
        ----------
        path: pathlib.Path or path-like
            Directory with saved data in CSV.

        Returns
        -------
        Saves data in object attributes.
        """
        path = check_if_path(path)
        loaded_data = {}
        for f in os.listdir(path):
            if f.endswith('.txt'):
                with open(path.joinpath(pathlib.Path(f))) as data:
                    data_list = []
                    for line in data.readlines():
                        data_list.append(line.replace('\n', ''))
                    loaded_data[f.replace('.txt', '')] = data_list
            elif f.endswith('.csv'):
                loaded_data[f.replace('.csv', '')] = pd.read_csv(path.joinpath(pathlib.Path(f)), **LOAD_PROPERTIES)
        for key, value in loaded_data.items():
            setattr(self, key, value)
