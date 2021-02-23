from __future__ import annotations
from typing import List, Optional, Dict, Union, Tuple
from json import load, dump
import os.path
import xmltodict
import  nltk


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


class _Data:
    """ A collection of data methods. """

    @classmethod
    def save_text2ngram(cls,
                        *file_paths: str,
                        n: int,
                        save_path: str):
        """ Similar to _Data.text2ngram.

        :param file_paths: complete paths to file including filename and extension
        :param n: 0 < n < 4
        :param save_path: complete path to save folder including filename and extension
        """

        output = cls.text2ngram(*file_paths, n=n)
        new_output = []
        if n == 1:
            for key in output.keys():
                new_output.append({"n-gram": key, "occurrences": output.get(key)})
            _Utility.save_json(new_output, save_path)
        else:
            for key in output.keys():
                new_output.append({"n-gram": " ".join(key), "occurrences": output.get(key)})
            _Utility.save_json(new_output, save_path)

    @classmethod
    def text2ngram(cls,
                   *file_paths: str,
                   n: int) -> Dict:
        """ Turn text from files into histogram of ngram.

        :param file_paths: complete paths to file including filename and extension
        :param n: 0 < n < 4
        """

        assert (0 < n < 4)

        if n == 1:
            return cls.text2histogram(*file_paths)

        text = cls.extract_text(*file_paths)

        stopwords = nltk.corpus.stopwords.words("english")
        punctuation = [".", ",", ")", "(", ":", ";", "©", "%"]
        publishers = ["blackwell",
                      "rights",
                      "reserved",
                      "publishing",
                      "american",
                      "press",
                      "inc.",
                      "society",
                      "wiley",
                      "copyright"]
        stopwords = stopwords + punctuation + publishers

        clean_text = []
        for word in nltk.tokenize.word_tokenize(text):
            if word.lower() not in set(stopwords):
                clean_text.append(word)

        if n == 2:
            return nltk.probability.FreqDist(nltk.bigrams(clean_text))
        if n == 3:
            return nltk.probability.FreqDist(nltk.trigrams(clean_text))

    @classmethod
    def text2histogram(cls,
                       *file_paths: str) -> Dict:
        """ Turn text from files into histogram.

        :param file_paths: complete paths to file including filename and extension
        """
        nltk.download('punkt')
        nltk.download('stopwords')
        text = cls.extract_text(*file_paths)

        stopwords = nltk.corpus.stopwords.words("english")
        punctuation = [".", ",", ")", "(", ":", ";", "©", "%"]
        numbers = ["1", "2", "3"]
        publishers = ["blackwell", "rights"]
        stopwords = stopwords + punctuation + numbers + publishers

        histogram = nltk.probability.FreqDist()

        for word in nltk.tokenize.word_tokenize(text):
            if word.lower() not in set(stopwords):
                histogram[word.lower()] += 1

        return histogram

    @classmethod
    def extract_text(cls,
                     *file_paths: str) -> str:
        """ Extract text per item from JSON file.

        A text is the concatenation of title and an abstract (if any).

        :param file_paths: complete paths to file including filename and extension
        """

        texts = []
        for file_path in file_paths:
            data = _Utility.load_json(file_path)
            print(f"Working on {file_path}...", end=" ")
            for item in data:
                texts.append(item.get("title") + " " + item.get("abstract"))
            print(" done.")

        return " ".join(texts)


_Utility.xml2json(DIR + "/refined/20210223/deduplicated_citavi.xml", DIR + "/refined/20210223/deduplicated_citavi.json")