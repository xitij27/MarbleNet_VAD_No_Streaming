import logging
import os

import numpy as np
import soundfile as sf

from src.vad.data_prep.annotations import Annotations

logger = logging.getLogger(__name__)


class SoundfileWrapper:
    def __init__(
        self,
        annotations: dict,
        output_dir: str = "",
        durations: float = 0.63,
    ):
        """
        A class that uses Soundfile to stream and chunk audiofiles into smaller size

        Args:
            annotations (dict): A dictionary of annotations.
            far (bool, optional): Whether to use 'far' annotations. Defaults to False.
            num_train_file (int, optional): The number of train files to use. Defaults to 1.
            num_validation_file (int, optional): The number of validation files to use. Defaults to 1.
            num_test_file (int, optional): The number of test files to use. Defaults to 1.
            output_dir (str, optional): The output directory for the segmented files. Defaults to "".
            durations (float, optional): The duration of each segment in seconds. Defaults to 0.63.
            hard_limit (float, optional): The hard limit for the number of segments. Defaults to None.
        """
        self.lvl_1_keys = list(annotations.keys())
        self.annotations = annotations
        self.train_val_test_meta_info = self._meta_data_of_files()
        self.output_dir = output_dir
        self.durations = durations

    def segmentation_loader(self):
        logger.info("Starting audio segmentation...")
        """
        Performs audio segmentation using soundfile in parallel for the specified files.
        """
        try:
            new_fold_loc_w_aud_files = self._make_trim_folder_appear()
        except Exception as error:
            logger.error(
                f"Unable to create output files for trimmed files due to: {error}"
            )
        try:
            for new_output_fold, corr_aud_files in new_fold_loc_w_aud_files.items():
                param_for_sf_chop_func = [
                    (new_output_fold, audio_file)
                    for audio_file in corr_aud_files
                    if ("R1021_M1947" not in audio_file)
                    and ("EN2005a.Headset-3" not in audio_file)
                    and ("ES2011c.Headset-2" not in audio_file)
                ]

                for outfold_aud_file in param_for_sf_chop_func:
                    logger.info(f"new_output_fold and corr file is: {outfold_aud_file}")
                    try:
                        self._soundfile_chopping(
                            outfold_aud_file[0], outfold_aud_file[1]
                        )
                        logger.info(f"chunking done for {outfold_aud_file[1]}")
                    except Exception as error:
                        logger.error(
                            f"chunking for {outfold_aud_file[1]} failed due to {error}"
                        )
            logger.info("Audio segmentation completed.")

        except Exception as error:
            logger.error(f"Unable to trim files due to: {error}")

    def _meta_data_of_files(self):
        logger.info("Retrieving metadata of files for segmentation...")
        """
        Retrieves the metadata of the files for segmentation.

        Returns:
            dict: A dictionary of file metadata organized by folder names.
        """

        sf_digestable_format = {}
        for key in self.lvl_1_keys:
            sf_digestable_format[key] = self._create_list_of_dict_for_meta_data(key)
        return sf_digestable_format

    def _create_list_of_dict_for_meta_data(self, key):
        logger.info(f"Creating metadata for key: {key}")
        """
        Creates a list of metadata for the specified number of files.

        Args:
            key (str): The key for the annotation.
            num_of_files_to_use (int): The number of files to select.

        Returns:
            numpy.ndarray: A numpy array containing the metadata for the selected files.
        """
        digestable_format = np.array(
            [self.annotations[key][_] for _ in self.annotations[key]]
        )
        return digestable_format

    def _deriving_snippets(self, audio_length):
        logger.info("Processing audio file...")
        """
        Calculates number of snippets and remainder duration given audio_length

        Args:
            audio_length (float) : The length of audio_length to be chunked
        """
        number_of_snippets = int(audio_length / self.durations)
        remainder_duration = round(audio_length - (number_of_snippets * self.durations))
        if remainder_duration > 0:
            number_of_snippets += 1
        return number_of_snippets, remainder_duration

    def _soundfile_chopping(self, output_fold_path, audio_file):
        logger.info(f"chunking {os.path.basename(audio_file)}...")
        """
        Performs audio chunking using soundfile for a single audio file.

        Args:
            audio_file (str): The path to the audio file.
        """
        audio_data, sample_rate = sf.read(audio_file)
        audio_duration = len(audio_data) / sample_rate
        duration_to_use = audio_duration

        number_of_snippets, remainder_duration = self._deriving_snippets(
            duration_to_use
        )

        for snippet_index in range(number_of_snippets):
            start_sample = round(self.durations * snippet_index * sample_rate)
            end_sample = round(self.durations * (snippet_index + 1) * sample_rate)

            if snippet_index == number_of_snippets - 1 and remainder_duration > 0:
                end_sample = len(audio_data)
            snippet_data = audio_data[start_sample:end_sample]
            snippet_duration = len(snippet_data) / sample_rate
            padding_samples = round((self.durations - snippet_duration) * sample_rate)
            padded_snippet_data = snippet_data

            if padding_samples > 0:
                padding_data = np.zeros((padding_samples,))
                padded_snippet_data = np.concatenate((snippet_data, padding_data))

            name_of_output_audio_file = (
                os.path.basename(audio_file).split(".wav")[0]
                + f"__{round(start_sample/sample_rate,2)}-{round(end_sample/sample_rate,2)}.wav"
            )

            output_file = os.path.join(output_fold_path, name_of_output_audio_file)

            sf.write(output_file, padded_snippet_data, sample_rate)

    def _make_trim_folder_appear(self):
        logger.info("creating output folders for trimmed files")
        """
        Creates trim folders as output for trimmed files

        Returns:
            list: paths of trim folders.
        """
        meta_info_keys = self.train_val_test_meta_info.keys()

        location_of_trim_folders = {}
        for potential_folder_name in meta_info_keys:
            folder_name_for_trim_files = potential_folder_name + "_trimmed"
            folder_path_for_trim_files = os.path.join(
                self.output_dir, folder_name_for_trim_files
            )
            if not os.path.isdir(folder_path_for_trim_files):
                os.mkdir(folder_path_for_trim_files)
            meta_info_list = self.train_val_test_meta_info[potential_folder_name]
            location_of_trim_folders[folder_path_for_trim_files] = [
                info["audio_path"] for info in meta_info_list
            ]
        return location_of_trim_folders
