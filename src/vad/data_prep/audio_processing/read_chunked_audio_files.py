import json
import os
from os.path import join

from src.folder_audio_utils.audio_management import AudioUtils
from src.folder_audio_utils.folder_management import FolderUtils
from src.vad.data_prep.annotations import Annotations


class ReadTrim:
    """Class for handling the trimming and manifest creation of audio segments.

    This class is responsible for reading trimmed audio segments and creating Nemo-compliant manifest files.
    It takes in a 'data_folder_head' which contains the trimmed audio segments and an 'annotations_obj'
    containing the annotation data for those segments. The class provides methods to handle the generated
    folders, create Nemo-compliant manifest files for speech and non-speech segments, and convert data to
    Nemo-compliant format.

    Args:
        data_folder_head (str): The path to the folder containing the trimmed audio segments.
        annotations_obj (Annotations): An instance of the Annotations class containing annotation data.

    Attributes:
        data_folder_head (str): The path to the folder containing the trimmed audio segments.
        annotations (dict): A dictionary containing the loaded annotation data for the audio segments.
        trimmed_directories (list): A list of folder paths containing the trimmed audio segments.

    Example:
        # Usage of the ReadTrim class
        from src.folder_audio_utils.audio_management import AudioUtils
        from src.folder_audio_utils.folder_management import FolderUtils
        from src.vad.data_prep.annotations import Annotations

        # Assume 'annotations_obj' is an instance of the Annotations class
        data_folder = "trimmed_audio_segments/"
        read_trim = ReadTrim(data_folder, annotations_obj)

        # Call the 'handle_generated_folders' method to create Nemo-compliant manifest files
        save_manifest_folder = "manifest_files/"
        read_trim.handle_generated_folders(duration=0.63, manifest_folder_path=save_manifest_folder)
    """

    def __init__(self, data_folder_head, annotations_obj):
        self.data_folder_head = data_folder_head
        annote_ = annotations_obj.annotations_loader()
        keys_which_are_empty = [key for key in annote_.keys() if not annote_[key]]
        for _ in keys_which_are_empty:
            del annote_[_]
        self.annotations = annote_
        self.trimmed_directories = FolderUtils.classify_folders_for_use(
            data_folder_head
        )

    def handle_generated_folders(
        self, duration: float = 0.63, manifest_folder_path: str = None
    ):
        """Handle generated folders and create Nemo-compliant manifest files.

        This method processes the audio segments in the generated folders and creates Nemo-compliant
        manifest files for speech and non-speech segments. It uses the provided 'duration' for each segment
        and saves the manifest files to the 'manifest_folder_path'.

        Args:
            duration (float, optional): The duration (in seconds) to consider for each segment. Defaults to 0.63.
            manifest_folder_path (str, optional): The path to the folder where the manifest files will be saved.
                                                  Defaults to None.

        Example:
            # Usage of the handle_generated_folders method
            save_manifest_folder = "manifest_files/"
            read_trim.handle_generated_folders(duration=0.63, manifest_folder_path=save_manifest_folder)
        """
        if self.trimmed_directories:
            for folder_path in self.trimmed_directories:
                (
                    annotation_dict_compatible_key,
                    trim_info,
                ) = FolderUtils.info_from_files_of_trimmed_folders(folder_path)
                manifest_path_speech = join(
                    manifest_folder_path,
                    f"{annotation_dict_compatible_key}_speech_manifest.json",
                )
                manifest_path_non_speech = join(
                    manifest_folder_path,
                    f"{annotation_dict_compatible_key}_non_speech_manifest.json",
                )
                collector_of_information_speech = []
                collector_of_information_non_speech = []
                for file_path, info in trim_info.items():
                    try:
                        filename_org, timings = list(info.items())[0]
                    except Exception as e:
                        print(
                            f"{annotation_dict_compatible_key} is out of dictionary range and failed with {e}"
                        )

                    speech_segments = self.annotations[annotation_dict_compatible_key][
                        filename_org
                    ]["segments"]

                    overlap_bool, offset = AudioUtils.check_overlap(
                        timings, speech_segments
                    )
                    if overlap_bool:
                        to_nemo_file = self._nemo_compliant_dict(
                            file_path,
                            offset,
                            duration,
                            label="speech",
                        )
                        collector_of_information_speech.append(to_nemo_file)
                    else:
                        to_other_nemo_file = self._nemo_compliant_dict(
                            file_path,
                            offset,
                            duration,
                            label="background",
                        )
                        collector_of_information_non_speech.append(to_other_nemo_file)

                with open(manifest_path_speech, "w", encoding="UTF-8") as outfile:
                    for information in collector_of_information_speech:
                        json.dump(information, outfile)
                        outfile.write("\n")
                    del collector_of_information_speech
                with open(manifest_path_non_speech, "w", encoding="UTF-8") as outfile:
                    for information in collector_of_information_non_speech:
                        json.dump(information, outfile)
                        outfile.write("\n")
                    del collector_of_information_non_speech

    def _nemo_compliant_dict(self, file_path, offset, duration, label=None):
        """Convert data to Nemo-compliant dictionary format.

        This private method takes in 'file_path', 'offset', 'duration', and an optional 'label',
        and converts this information to a Nemo-compliant dictionary format.

        Args:
            file_path (str): The path to the audio file.
            offset (float): The offset (in seconds) where speech starts for the audio segment.
            duration (float): The duration (in seconds) of the audio segment.
            label (str, optional): The label for the audio segment. Defaults to None.

        Returns:
            dict: A Nemo-compliant dictionary containing the audio file information.

        Example:
            # Usage of the _nemo_compliant_dict method
            file_path = "path/to/audio.wav"
            offset = 1.5
            duration = 0.63
            label = "speech"
            manifest_item = read_trim._nemo_compliant_dict(file_path, offset, duration, label)
        """
        manifest_item = {
            "audio_filepath": file_path,
            "duration": duration,
            "label": label,
            "text": "_",
            "offset": offset,
        }
        return manifest_item
