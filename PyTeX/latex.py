from fuzzywuzzy import fuzz
from PyTeX import bib, lexer, tex
import re

def load(f):
    P_BIB = re.compile(r'.+\.bib')
    P_TEX = re.compile(r'.+\.tex')
    if P_BIB.match(f.name):
        return bib.Parser(lexer.FileIn(f, bib.SUB_DICT).tokenize(bib.REGEX_LIST)).parse()
    elif P_TEX.match(f.name):
        return tex.Parser(lexer.FileIn(f, tex.SUB_DICT).tokenize(tex.REGEX_LIST)).parse()
    else:
        raise OSError("File {} does not have a valid extension".format(f.name))

class Finder(object):

    def __init__(self, match_strength):
        self.match_strength = match_strength
        self.results = []

    def find(self, term, obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict):
                    if fuzz.ratio(term, key) > self.match_strength:
                        self.results.append(obj)
                    else:
                        self.find(term, value)
                else:
                    key_match = fuzz.ratio(term, key)
                    val_match = fuzz.ratio(term, value)
                    if key_match | val_match > self.match_strength:
                        self.results.append(obj)
        elif isinstance(obj, list):
            for item in obj:
                self.find(term, item)
        else:
            raise TypeError("Expected dict or list")

def find(term, obj, match_strength=75):
    search = Finder(match_strength)
    search.find(term, obj)
    return search.results
