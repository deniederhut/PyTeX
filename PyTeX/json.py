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
