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
    def get_publishers(cls) -> list:
        """ Return list of publishers resp. related terms. """

        publishers = [
            "blackwell",
            "rights",
            "reserved",
            "publishing",
            "american",
            "press",
            "inc.",
            "society",
            "wiley",
            "copyright",
            "john",
            "gmbh",
            "verlag",
            "wiley",
            "wiley-vch",
            "& co.",
            "springer",
            "nature limited",
            "oxford",
            "science+business media",
            "license",
            "author",
            "macmillan",
            "elsevier",
            "ltd.",
            "ltd",
            "sons",
            "kgaa",
            "academic",
            "credited",
            "licence"
        ]

        return publishers

    @classmethod
    def save_text2ngram(cls,
                        *file_paths: str,
                        n: int,
                        save_path: str,
                        include_abstract: bool = True) -> None:
        """ Similar to _Data.text2ngram.

        :param file_paths: complete paths to file including filename and extension
        :param n: 0 < n < 4
        :param save_path: complete path to save folder including filename and extension
        :param include_abstract: toggle inclusion of abstract, defaults to True
        """

        output = cls.text2ngram(*file_paths, n=n, include_abstract=include_abstract)
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
                   n: int,
                   include_abstract: bool = True) -> Dict:
        """ Turn text from files into histogram of ngram.

        :param file_paths: complete paths to file including filename and extension
        :param n: 0 < n < 4
        :param include_abstract: toggle inclusion of abstract, defaults to True
        """

        assert (0 < n < 4)

        if n == 1:
            return cls.text2histogram(*file_paths, include_abstract=include_abstract)

        text = cls.extract_text(*file_paths, include_abstract=include_abstract)

        stopwords = nltk.corpus.stopwords.words("english")
        punctuation = [".", ",", ")", "(", ":", ";", "©", "%"]
        publishers = cls.get_publishers()
        stopwords = stopwords + punctuation + publishers

        clean_text = []
        for word in nltk.tokenize.word_tokenize(text):
            clean_word = _Keywords.clean_keyword(word)
            if clean_word not in set(stopwords):
                clean_text.append(clean_word)

        if n == 2:
            return nltk.probability.FreqDist(nltk.bigrams(clean_text))
        if n == 3:
            return nltk.probability.FreqDist(nltk.trigrams(clean_text))

    @classmethod
    def text2histogram(cls,
                       *file_paths: str,
                       include_abstract: bool = True) -> Dict:
        """ Turn text from files into histogram.

        :param file_paths: complete paths to file including filename and extension
        :param include_abstract: toggle inclusion of abstract, defaults to True
        """
        nltk.download('punkt')
        nltk.download('stopwords')
        text = cls.extract_text(*file_paths, include_abstract=include_abstract)

        stopwords = nltk.corpus.stopwords.words("english")
        punctuation = [".", ",", ")", "(", ":", ";", "©", "%"]
        numbers = ["1", "2", "3"]
        publishers = cls.get_publishers()
        stopwords = stopwords + punctuation + numbers + publishers

        histogram = nltk.probability.FreqDist()

        for word in nltk.tokenize.word_tokenize(text):
            if word.lower() not in set(stopwords):
                histogram[word.lower()] += 1

        return histogram

    @classmethod
    def extract_text(cls,
                     *file_paths: str,
                     include_abstract: bool = True) -> str:
        """ Extract text per item from JSON file.

        A text is the concatenation of title and an abstract (if any).

        :param file_paths: complete paths to file including filename and extension
        :param include_abstract: toggle inclusion of abstract, defaults to True
        """

        texts = []
        for file_path in file_paths:
            data = _Utility.load_json(file_path)
            for item in data:
                title = item.get("Title")
                abstract = item.get("Abstract")
                if include_abstract is True:
                    try:
                        texts.append(title + " " + abstract)
                    except TypeError:
                        texts.append(title)
                else:
                    texts.append(title)

        return " ".join(texts)

    @classmethod
    def extract_by_decade(cls,
                       file_path: str):
        """ Extract documents by decace and save the output as JSON.

        :param file_path: complete path to file including filename and extension, MUST be Citavi export
        :return:
        """

        file = _Utility.load_json(file_path)
        data = file.get("Documents").get("Document")

        bin_1971 = []
        bin_1982 = []
        bin_1992 = []
        bin_2002 = []
        bin_2012 = []

        for document in data:
            try:
                if int(document.get("Year")) < 1982:
                    bin_1971.append(document)
                elif int(document.get("Year")) < 1992:
                    bin_1982.append(document)
                elif int(document.get("Year")) < 2002:
                    bin_1992.append(document)
                elif int(document.get("Year")) < 2012:
                    bin_2002.append(document)
                else:
                    bin_2012.append(document)
            except TypeError:
                continue

        _Utility.save_json(bin_1971, DIR + "/refined/20210301/1971-1981.json")
        _Utility.save_json(bin_1982, DIR + "/refined/20210301/1982-1991.json")
        _Utility.save_json(bin_1992, DIR + "/refined/20210301/1992-2001.json")
        _Utility.save_json(bin_2002, DIR + "/refined/20210301/2002-2011.json")
        _Utility.save_json(bin_2012, DIR + "/refined/20210301/2012-2021.json")

    @classmethod
    def super_ngram(cls):
        """ Save histograms of n-grams for all combinations. """

        files = os.listdir(DIR + "/refined/20210301/metadata")
        for file in files:
            for n in [1, 2, 3]:
                for include_abstract in [True, False]:
                    print(f"Working on {n}gram_{include_abstract}_{file}...", end=" ")
                    cls.save_text2ngram(DIR + f"/refined/20210301/metadata/{file}",
                                        n=n,
                                        save_path=DIR + f"/refined/20210301/ngrams/{n}gram_{include_abstract}_{file}",
                                        include_abstract=include_abstract)
                    print(" done.")