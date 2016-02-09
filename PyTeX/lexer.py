from PyTeX import error
import re

class Token(object):

    def __init__(self, string, name):
        self.data = string
        self.name = name

class FileIn(object):

    def __init__(self, f, substitute_dict):
        self.data = f.read().strip()
        if f.encoding not in ['UTF-8', 'ASCII']:
            raise error.TeXError(error.E_ENCODING.format(f.encoding))
        for pattern, replacement in substitute_dict.items():
            self.data = re.sub(pattern, replacement, self.data)
        self.newline_char = f.newlines
        self.length = len(self.data)

    def read(self):
        return self.data

    def tokenize(self, regex_list):
        skip_list = [' ']
        while self.data:
            while self.data[0] in skip_list:
                self.data = self.data[1:]
            i = 0
            for item in regex_list:
                match = re.match(item.pattern, self.data)
                if match:
                    i += 1
                    self.data = self.data[match.end():]
                    if 'Generic' in item.name:
                        p = re.compile(r'(?:\{)(\w+)(?:\})')
                        container = re.search(p, match.group()).group(1)
                        name = item.name.replace('Generic', container)
                        yield Token(match.group(), name)
                    else:
                        yield Token(match.group(), item.name)
            if i == 0:
                raise error.TeXError(error.E_INPUT)
        yield Token('', 'EOF')
