import logging
import os
from os.path import isdir, join
from typing import List, Tuple

import hydra
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.vad.data_prep.dataloadfolders import DataLoadFolders

logger = logging.getLogger(__name__)

class Annotations:
    """
    A wrapper file which reads the root of created samples

    Convert sampled folder and relevant contents into list of annotations dictionary

    Attributes:
        audio_data (str) : absolute path of root folder of sampled data
    """

    def __init__(
        self,
        root_path_of_sampled_data: str,
        root_path_of_primary: str = None,
    ):
        self.root = root_path_of_sampled_data
        self.primary = root_path_of_primary

    def annotations_loader(self):
        """
        TODO: refactor the subpath_data_mix into another class
        subpath_data_mix(self.root) will return [(foldname,fold_path)...]
        """
        logger.info(
            f"Converting {self.root} to list of annotation dict per sub_data_folder"
        )

        list_of_sampled_annote = self.subpath_data_mix(self.root)
        list_of_samp_fold = [item[0] for item in list_of_sampled_annote]
        samp_dict = self._get_annote_dict(list_of_sampled_annote)
        if self.primary:
            list_of_primary_annote = [
                item
                for item in self.subpath_data_mix(self.primary)
                if item[0] in list_of_samp_fold
            ]
            primary_dict = self._get_annote_dict(list_of_primary_annote)
            for key in samp_dict.keys():
                samp_dict[key]["val"] = primary_dict[key]["val"]
                samp_dict[key]["test"] = primary_dict[key]["test"]
        samp_dict_reformat = self._reformat_dict_to_reduct_annot_levels(
            samp_dict, list_of_samp_fold
        )
        return samp_dict_reformat

    def _reformat_dict_to_reduct_annot_levels(self, annote_dict, list_of_samp_fold):
        new_dict = {}
        for fold_name in list_of_samp_fold:
            list_of_tvt = list(annote_dict[fold_name].keys())
            for tvt in list_of_tvt:
                new_dict[f"{fold_name}_{tvt}"] = annote_dict[fold_name][tvt]
        return new_dict

    def _get_annote_dict(self, list_of_annote):
        try:
            annote_dict = {
                path[0]: DataLoadFolders(path[1]).to_dict() for path in list_of_annote
            }
        except Exception as e:
            logger.info(
                f"An unknown error of {e} was encountered during list comprehension subprocess.\nTrying sequantial looping instead"
            )
            annote_dict = {}
            for path in list_of_annote:
                try:
                    annote_dict[path[0]] = DataLoadFolders(path[1]).to_dict()
                except Exception as e:
                    logger.info(f"{path} cannot be converted to annotations due to {e}")
        finally:
            if not annote_dict:
                logger.error("Unable to get annotations.")
        return annote_dict

    def subpath_data_mix(self, root_path):
        """
        TODO: this function should be a general tools independent of annotations
        root is parent, with the immediate subfolders as child
        """
        list_of_child = os.listdir(root_path)
        try:
            list_of_fold_name = [
                item for item in list_of_child if isdir(join(root_path, item))
            ]
        except Exception as e:
            logger.info(
                f"error of {e} encountered when getting subfolders. Will attempt sequantial looping instead"
            )
            list_of_fold_name = []
            try:
                for item in list_of_child:
                    if isdir(join(root_path, item)):
                        list_of_fold_name.append(item)
            except Exception as e:
                logger.error(f"{item} cannot be converted to annotations due to {e}")
        finally:
            if not list_of_fold_name:
                logger.error("Unable to get annotations.")

        list_of_dir = [(item, join(root_path, item)) for item in list_of_fold_name]
        return list_of_dir