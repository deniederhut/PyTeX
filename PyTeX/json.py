from fuzzywuzzy import fuzz
from PyTeX import tex

def loads(f):
    return tex.Parser(tex.tokenize(tex.FileIn(f).read())).parse()

class Finder(object):

    def __init__(self, match_strength):
        self.match_strength = match_strength
        self.results = []

    def find(self, term, obj):
        if isinstance(obj, dict):
            for item in obj.items():
                if len(item[1]) <= 1:
                    key_match = fuzz.ratio(term, item[0])
                    val_match = fuzz.ratio(term, item[1])
                    if key_match | val_match > self.match_strength:
                        self.results.append(obj)
                elif isinstance(item[1][0], dict):
                    self.find(term, item[1])
        elif isinstance(obj, list):
            for item in obj:
                self.find(term, item)
        else:
            raise TypeError("Expected dict or list")

def find(term, obj, match_strength=50):
    search = Finder(match_strength)
    return search.find(term, obj).results
