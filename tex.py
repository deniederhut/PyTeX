import collections
import re
import types

# Character Escaping

ESC_MAP = {'&' : '\\&', '%' : '\\%', '$' : '\\$', '#' : '\\#', '_' : '\\_', '{' : '\\{', '}' : '\\{', '~' : '\\~', '^' : '\\^', '<' : '/<', '>' : '\>'}
REV_ESC_MAP = {value : key for key, value in ESC_MAP.items()}
FROM_TEX_SUB = {r'\\\\' : r'\n'}

# Error Messages

E_ENCODING = 'File not in valid TeX encoding'
E_INPUT = 'Unrecognized input'
E_SYNTAX = 'Unexpected {} where {} was expected'

# Regular Expression Patterns
regex = collections.namedtuple('regex', ['name', 'pattern'])

P_COMMENT = regex('Comment', re.compile(r'%.+\n', flags=re.I))
P_END_ARG = regex('EndOfArgument', re.compile(r'\}'))
P_END_OPT = regex('EndOfOption', re.compile(r'\]'))
P_ESCAPED = regex('Escaped', re.compile(r'\\' + '|'.join(REV_ESC_MAP.keys())))
P_FUNCTION = regex('Function', re.compile(r'\\'))
P_NEWLINE = regex('Newline', re.compile(r'\n|\\\\'))
P_START_ARG = regex('StartOfArgument', re.compile(r'\{'))
P_START_OPT = regex('StartOfOption', re.compile(r'\['))
P_TEXT = regex('Text', re.compile(r'[\w`\'\,\.\(\)]+'))

RE_LIST = [P_COMMENT, P_NEWLINE, P_ESCAPED, P_FUNCTION, P_START_ARG, P_START_OPT, P_END_ARG, P_END_OPT, P_TEXT]

class TeXError(Exception):

    def __init__(self, msg, stm=None, pos=0):
        if stm:
            msg += ' at position {}, "{}"'.format(pos, repr(stm.substr(post, 32)))
        Exception.__init__(self, msg)

class Token(object):

    def __init__(self, string, name):
        self.data = string
        self.name = name

class FileIn(object):

    def __init__(self, f):
        self.data = f.read()
        if f.encoding not in ['UTF-8', 'ASCII']:
            raise TexError(E_ENCODING)
        for pattern, replacement in FROM_TEX_SUB.items():
            self.data = re.sub(pattern, replacement, self.data)
        self.newline_char = f.newlines
        self.length = len(self.data)

    def read():
        return self.data

    def read_lines():
        for line in self.data.split(newline_char):
            yield line

def tokenize(string):
    skip_list = [' ']
    while string:
        while string[0] in skip_list:
            string = string[1:]
        i = 0
        for item in RE_LIST:
            match = re.match(item.pattern, string)
            if match:
                i += 1
                string = string[match.end():]
                yield Token(match.group(), item.name)
        if i == 0:
            raise TexError(' - '.join([E_INPUT, string[:25]]))
    yield Token('', 'EOF')

class Parser(object):

    def __init__(self, lexer):
        self.lexer = lexer
        self.current = None

    def next():
        item = self.lexer.__next__()
        if item.name == 'Escaped':
            self.current = Token(REV_ESC_MAP[item.data], 'Text')
        else:
            self.current = item

    def _parse_comment(self):
        result =  {self.current.name : self.current.data}
        self.next()
        return result

    def _parse_text(self):
        result = self.current.data
        while self.current.name == 'Text':
            self.next()
            if self.current.name == 'Text':
                result += self.data.name
            # if newline
            # if function
        self.next()
        return result

    def _parse_option(self):
        while self.current.name != 'EndofOption':
            self.next()
            if self.current.name == 'Text':
                result = _parse_text(self)
        self.next()
        return {'Option' : result.split(', ')}

    def _parse_argument(self):
        result = []
        while self.current.name != 'EndofArgument':
            self.next()
            if self.current.name == 'Text':
                result.append(_parse_text(self))
        self.next()
        return result

    def _parse_function(self):
        pass

    def _parse(self):
        result = []
        while self.current.name != 'EOF':
            if self.current.name == 'Comment':
                result.append(_parse_comment(self))
            elif self.current.name == 'Text':
                result.append(_parse_text(self))

        return result

    def parse(self):
        self.next()
        return _parse(self)

def loads(f):
    return Parser(tokenize(FileIn(f))).parse()

def dumps(obj, f):
    return True

def find(obj):
    return True
