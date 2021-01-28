from __future__ import annotations
from typing import List, Optional, Dict, Union, Tuple
from json import load, dump
import os.path
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
    def load_json(cls,
                  file_path: str) -> list:
        """ Load a JSON object from file.

        :param file_path: complete path to file including filename and extension
        """

        with open(file_path, encoding="utf-8") as file:
            loaded = load(file)

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
        """ Convert XML file to JSON file.
        
        :param file_path: complete path to file including filename and extension
        :param save_path: complete path to save folder including filename without extension
        """
        file = cls.load_xml(file_path)

        cls.save_json(file, save_path)


class _Keywords:
    """ A collection of functions for manipulating keywords. """

    @classmethod
    def extract_keywords(cls,
                         *file_paths: str) -> List[str]:
        """ Extract keywords per item from JSON file.

        :param file_paths: complete paths to file including filename and extension
        """

        keywords = []
        for file_path in file_paths:
            data = _Utility.load_json(file_path)
            print(f"Working on {file_path}...", end=" ")
            for item in data:
                keywords.append(item.get("keywords"))
            print(" done.")

        return keywords

    @classmethod
    def clean_keyword(cls,
                      keyword: str) -> str:
        """ Clean a keyword.

        :param keyword: the keyword
        """

        # make lower case:
        keyword = keyword.lower()
        # remove *:
        keyword = keyword.replace("*", "")
        # remove whitespace:
        keyword = keyword.strip()

        return keyword

    @classmethod
    def make_histogram(cls,
                       keywords: List[str]) -> List[Dict]:
        """ Make a histogram for keywords.

        :param keywords: the keywords
        """
        histogram = dict()
        for keyword in keywords:
            if keyword in histogram:
                histogram[keyword] = histogram[keyword] + 1
            else:
                histogram[keyword] = 1

        openrefine_histogram = []
        for entry in histogram:
            openrefine_histogram.append({"keyword": entry, "occurrences": histogram.get(entry)})

        return openrefine_histogram

    @classmethod
    def slices2histogram(cls,
                         *file_paths: str,
                         save_path: str = DIR + "/refined/histogram.json"):
        """ Turn slices of records into histogram based on keywords.

        :param file_paths: complete paths to file including filename and extension
        :param save_path: complete path to save folder including filename without extension
        """

        keywords = _Keywords.extract_keywords(*file_paths)
        clean_keywords = []
        for keyword in keywords:
            clean_keywords.append(_Keywords.clean_keyword(keyword))
        histogram = _Keywords.make_histogram(clean_keywords)
        _Utility.save_json(histogram, save_path)

        
