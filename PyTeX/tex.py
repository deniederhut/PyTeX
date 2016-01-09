import collections
import re
import types

# Character Escaping

ESC_MAP = {r'&' : r'\\&', r'%' : r'\\%', r'$' : r'\\$', r'#' : r'\\#', r'_' : r'\\_', r'{' : r'\\{', r'}' : r'\\{', r'~' : r'\\~', r'^' : r'\\^', r'<' : r'/<', r'>' : r'\>'}
REV_ESC_MAP = {value : key for key, value in ESC_MAP.items()}
FROM_TEX_SUB = {r'\\\\' : r'\n'}

# Error Messages

E_ENCODING = 'File in unexpected coding: {}'
E_INPUT = 'Unrecognized input'
E_SYNTAX = '{} where {} was expected'
E_EOF = 'Unexpected end of {}'

# Regular Expression Patterns
regex = collections.namedtuple('regex', ['name', 'pattern'])

P_COMMENT = regex('Comment', re.compile(r'%.+\n', flags=re.I))
P_END_ARG = regex('EndOfArgument', re.compile(r'\}'))
P_END_EQ = regex('EndOfEquation', re.compile(r'\\end\{equation\}'))
P_END_LI = regex('EndOfList', re.compile(r'\\end\{itemize\}'))
P_END_OPT = regex('EndOfOption', re.compile(r'\]'))
P_ESCAPED = regex('Escaped', re.compile(r'\\' + '|'.join(REV_ESC_MAP.keys())))
P_FUNCTION = regex('Function', re.compile(r'\\'))
P_ITEM = regex('Item', re.compile(r'\\item'))
P_MATH = regex('Math', re.compile(r'\$'))
P_NEWLINE = regex('Newline', re.compile(r'\n|\\\\'))
P_SECTION = regex('Section', re.compile(r'\\section'))
P_SUBSECTION = regex('Subsection', re.compile(r'\\subsection'))
P_START_ARG = regex('StartOfArgument', re.compile(r'\{'))
P_START_EQ = regex('StartOfEquation', re.compile(r'\\begin\{equation\}'))
P_START_LI = regex('StartOfList', re.compile(r'\\begin\{itemize\}'))
P_START_OPT = regex('StartOfOption', re.compile(r'\['))
P_TEXT = regex('Text', re.compile(r'[\w`\'\,\.\(\)]+', flags=re.I))

RE_LIST = [P_COMMENT, P_NEWLINE, P_MATH, P_ESCAPED, P_SECTION, P_SUBSECTION, P_START_EQ, P_START_LI, P_END_EQ, P_END_LI, P_ITEM, P_FUNCTION, P_START_ARG, P_START_OPT, P_END_ARG, P_END_OPT, P_TEXT]

class TeXError(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)

class Token(object):

    def __init__(self, string, name):
        self.data = string
        self.name = name

class FileIn(object):

    def __init__(self, f):
        self.data = f.read().strip()
        if f.encoding not in ['UTF-8', 'ASCII']:
            raise TeXError(E_ENCODING.format(f.encoding))
        for pattern, replacement in FROM_TEX_SUB.items():
            self.data = re.sub(pattern, replacement, self.data)
        self.newline_char = f.newlines
        self.length = len(self.data)

    def read(self):
        return self.data

    def read_lines(self):
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
            raise TeXError(E_INPUT)
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

    def __parse_comment__(self):
        result = {self.current.name : self.current.data}
        self.next()
        return result

    def __parse_text__(self):
        result = self.current.data
        while self.current.name == 'Text':
            self.next()
            if self.current.name == 'Text':
                result += ' ' + self.current.data
            if self.current.name == 'Newline':
                self.next()
                if self.current.name == 'Text':
                    result += self.current.data
                else:
                    return result
        return result

    def __parse_options__(self):
        while self.current.name != 'EndOfOption':
            self.next()
            if self.current.name == 'Text':
                result = self.__parse_text__()
        self.next()
        return result.split(',')

    def __parse_arguments__(self):
        while self.current.name != 'EndOfArgument':
            self.next()
            result = self.__recursive_parse__('EndOfArgument')
        self.next()
        return result

    def __parse_function__(self):
        self.next()
        if self.current.name != 'Text':
            raise TeXError(E_SYNTAX.format(self.current.name, 'Text'))
        result = {'command' : self.current.data}
        argument_list = []
        self.next()
        while self.current.name in ['StartOfOption', 'StartOfArgument']:
            if self.current.name == 'StartOfOption':
                result['options'] = self.__parse_options__()
            elif self.current.name == 'StartOfArgument':
                argument_list.append(self.__parse_arguments__())
        if argument_list:
            result['arguments'] = argument_list
        return result

    def __recursive_parse__(self, condition):
        result = []
        while self.current.name != condition:
            if self.current.name == 'Comment':
                result.append(self.__parse_comment__())
            elif self.current.name == 'Text':
                result.append(self.__parse_text__())
            elif 'Begin' in self.current.name:
                end_condition = self.current.name.replace('Begin','End')
                result.append(self.__recursive_parse__(end_condition))
            elif self.current.name == 'Function':
                result.append(self.__parse_function__())
            elif self.current.name == 'Newline':
                self.next()
            elif self.current.name == condition:
                break
            else:
                raise TeXError(E_INPUT)
        return result

    def parse(self):
        self.next()
        return self.__recursive_parse__(condition='EOF')
