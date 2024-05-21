import os
import shutil
from os.path import isdir, join

import numpy as np


class FolderUtils:
    @staticmethod
    def classify_folders_for_use(data_folder_head):
        """
        Classifies folders in the given data_folder_head based on their names.

        Args:
            data_folder_head (str): The path to the data folder.

        Returns:
            tuple: A tuple containing two lists:
                - trim_directories: A list of paths to folders with 'trim' in their names.
                - artifacts: A list of paths to folders without 'trim' in their names.
        """

        trim_directories = [
            join(data_folder_head, folder_name)
            for folder_name in os.listdir(data_folder_head)
            if "trim" in folder_name and isdir(join(data_folder_head, folder_name))
        ]

        return trim_directories

    @staticmethod
    def info_from_files_of_trimmed_folders(trimmed_folder_path):
        """
        Extracts information from the files in a trimmed folder.

        Args:
            trimmed_folder_path (str): The path to the trimmed folder.

        Returns:
            tuple: A tuple containing two values:
                - annotation_dict_compatible_key: A string representing a compatible key for annotation.
                - dictionary_of_files: A dictionary containing file information. The keys are file paths,
                  and the values are dictionaries with the file name split into three parts.
        """
        folder_path_base_name = os.path.basename(trimmed_folder_path)
        annotation_dict_compatible_key = folder_path_base_name[
            : folder_path_base_name.index("_trimmed")
        ]
        all_files_in_folder = os.listdir(trimmed_folder_path)
        dictionary_of_files = {
            join(trimmed_folder_path, filename): {
                filename.split("__")[0]: (
                    filename.split("__")[1].split(".wav")[0].split("-")
                )
            }
            for filename in all_files_in_folder
        }
        return annotation_dict_compatible_key, dictionary_of_files

    @staticmethod
    def remove_folders_with_files(folder_path):
        """
        Removes a folder and its contents.

        Args:
            folder_path (str): The path to the folder to be removed.
        """
        shutil.rmtree(folder_path)

    @staticmethod
    def random_samp_index(larger_num: int, smaller_num: int):
        """
        Creating random indices for sampling

        Args:
            larger_num (int): usually is length of list to be sampled
            smaller_num (int): usually is the number of sampled you want to get
        """

        rand_index = np.random.choice(larger_num, smaller_num, replace=False).tolist()
        return rand_index
