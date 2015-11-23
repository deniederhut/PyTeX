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
E_SYNTAX = '{} where {} was expected'

# Regular Expression Patterns
regex = collections.namedtuple('regex', ['name', 'pattern'])

# Tokenize begin
P_COMMENT = regex('Comment', re.compile(r'%.+\n', flags=re.I))
# Tokenize end
P_END_ARG = regex('EndOfArgument', re.compile(r'\}'))
P_END_OPT = regex('EndOfOption', re.compile(r'\]'))
P_ESCAPED = regex('Escaped', re.compile(r'\\' + '|'.join(REV_ESC_MAP.keys())))
P_FUNCTION = regex('Function', re.compile(r'\\'))
# Tokenize item
P_NEWLINE = regex('Newline', re.compile(r'\n|\\\\'))
P_START_ARG = regex('StartOfArgument', re.compile(r'\{'))
P_START_OPT = regex('StartOfOption', re.compile(r'\['))
# Tokenize section and subsection
P_TEXT = regex('Text', re.compile(r'[\w`\'\,\.\(\)]+'))

RE_LIST = [P_COMMENT, P_NEWLINE, P_ESCAPED, P_FUNCTION, P_START_ARG, P_START_OPT, P_END_ARG, P_END_OPT, P_TEXT]

class TeXError(Exception):

    def __init__(self, msg, string=None):
        if stm:
            msg += ' at "{}"'.format(string[:25])
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
            raise TexError(E_INPUT, string)
    yield Token('', 'EOF')

class Parser(object):

    def __init__(self, lexer):
        self.lexer = lexer
        self.current = None

    def next(self):
        item = self.lexer.__next__()
        if item.name == 'Escaped':
            self.current = Token(REV_ESC_MAP[item.data], 'Text')
        else:
            self.current = item

    def _parse_comment(self):
        result = {self.current.name : self.current.data}
        self.next()
        return result

    def _parse_text(self):
        result = self.current.data
        while self.current.name == 'Text':
            self.next()
            if self.current.name == 'Text':
                result += self.current.data
            if self.current.name == 'Newline':
                self.next()
                if self.current.name == 'Text':
                    result += self.current.data
                else:
                    return result
        self.next()
        return result

    def _parse_options(self):
        while self.current.name != 'EndofOption':
            self.next()
            if self.current.name == 'Text':
                result = _parse_text(self)
        self.next()
        return result.split(', ')

    def _parse_arguments(self):
        result = []
        while self.current.name != 'EndofArgument':
            self.next()
            if self.current.name == 'Text':
                result.append(_parse_text(self))
            if self.current.name == 'Function':
                result.append(_parse_function(self))
        self.next()
        return result

    def _parse_function(self):
        self.next()
        if self.current.name != 'Text':
            raise TeXError(E_SYNTAX.format(self.current.name, 'Text'))
        result = {'command' : self.data}
        argument_list = []
        self.next()
        while self.name in ['StartOfOption', 'StartOfArgument']:
            if self.name == 'StartOfOption':
                result['options'] = _parse_options(self)
            elif self.name == 'StartOfArgument':
                argument_list.append(_parse_arguments(self))
        if argument_list:
            result['arguments'] = argument_list
            result = _parse_function_generic(self)
        self.next()
        return result

    def _parse(self, condition):
        result = []
        while self.current.name != condition:
            if self.current.name == 'Comment':
                result.append(_parse_comment(self))
            elif self.current.name == 'Text':
                result.append(_parse_text(self))
            elif self.current.name == 'Function':
                result.append(_parse_command(self))
            else:
                raise TeXError(E_INPUT)
        return result

    def parse(self):
        self.next()
        return _parse(self, condition='EOF')

def loads(f):
    return Parser(tokenize(FileIn(f))).parse()

def dumps(obj, f):
    pass

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
