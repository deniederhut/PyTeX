import re
from PyTeX import tex

def loads(f):
    return tex.Parser(tex.tokenize(tex.FileIn(f).read())).parse()

def find(term, obj):
    result = []
    if type(obj) == str:
        if re.search(term, obj):
            result.append(obj)
    if type(obj) == list:
        for item in obj:
            search = find(term, item)
            if search:
                result.append({item : search})
    if type(obj) == dict:
        for key in obj:
            search = find(term, key)
            if search:
                result.append({key : search})
            search = find(term, obj[key])
            if search:
                result.append({key : search})
    return result
