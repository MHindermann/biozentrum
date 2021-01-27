from __future__ import annotations
from typing import List, Optional, Dict, Union, Tuple
from json import load, dump
from datetime import datetime
from annif_client import AnnifClient
import os.path
import urllib3
import xmltodict


DIR = os.path.dirname(__file__)


class _Utility:
    """ A collection of utility functions. """

    @classmethod
    def load_xml(cls,
                 file_path: str) -> list:
        """ Load XML file.

        Superfluous information from Endnote is removed.

        :param file_path: complete path to file including filename and extension
        """

        with open(file_path, encoding="utf-8") as file:
            loaded = xmltodict.parse(file.read().replace('<style face="normal" font="default" size="100%">', "").replace('</style>', ""))

            return loaded

    @classmethod
    def save_json(cls,
                  data: Union[List, Dict],
                  file_path: str) -> None:
        """ Save data as JSON file.
        :param data: the data to be saved
        :param file_path: complete path to file including filename and extension
        """

        with open(file_path, "w") as file:
            dump(data, file)

    @classmethod
    def xml2json(cls,
                 file_path: str,
                 save_path: str) -> None:
        """ Bla
        :param file_path: complete path to file including filename and extension
        :param save_path: complete path to save folder including filename without extension
        """
        file = cls.load_xml(file_path)

        cls.save_json(file, save_path)
