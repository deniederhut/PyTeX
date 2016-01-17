import collections
import re
import types

# Character Escaping

ESC_MAP = {r'&' : r'\\&', r'%' : r'\\%', r'$' : r'\\$', r'#' : r'\\#', r'_' : r'\\_', r'{' : r'\\{', r'}' : r'\\{', r'~' : r'\\~', r'^' : r'\\^', r'<' : r'\\<', r'>' : r'\\>'}
REV_ESC_MAP = {value : key for key, value in ESC_MAP.items()}
FROM_TEX_SUB = {r'\\\\' : r'\n'}

# Error Messages

E_ENCODING = 'File in unexpected coding: {}'
E_INPUT = 'Unrecognized input'
E_SYNTAX = '{} where {} was expected'
E_EOF = 'Unexpected end of {}'

# Regular Expression Patterns
regex = collections.namedtuple('regex', ['name', 'pattern'])

P_START_GEN = regex('BeginGeneric', re.compile(r'\\begin\{\w+\}'))
P_COMMENT = regex('Comment', re.compile(r'%.+\n', flags=re.I))
P_END_ARG = regex('EndArgument', re.compile(r'\}'))
P_END_GEN = regex('EndGeneric', re.compile(r'\\end\{\w+\}'))
P_END_OPT = regex('EndOption', re.compile(r'\]'))
P_ESCAPED = regex('Escaped', re.compile(r'|'.join(REV_ESC_MAP.keys())))
P_FUNCTION = regex('Function', re.compile(r'\\\w+'))
# P_ITEM = regex('Item', re.compile(r'\\item'))
P_MATH = regex('Math', re.compile(r'\$'))
P_NEWLINE = regex('Newline', re.compile(r'\n|\\\\'))
#P_SECTION = regex('Section', re.compile(r'\\section'))
#P_SUBSECTION = regex('Subsection', re.compile(r'\\subsection'))
P_START_ARG = regex('StartArgument', re.compile(r'\{'))
P_START_OPT = regex('StartOption', re.compile(r'\['))
P_TEXT = regex('Text', re.compile(r'[\w/`\'\,\.\(\)=@\*\-]+', flags=re.I))

RE_LIST = [P_COMMENT, P_NEWLINE, P_MATH, P_ESCAPED, P_START_GEN, P_END_GEN, P_FUNCTION, P_START_ARG, P_START_OPT, P_END_ARG, P_END_OPT, P_TEXT]

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
                if 'Generic' in item.name:
                    p = re.compile(r'(?:\{)(\w+)(?:\})')
                    container = re.search(p, match.group()).group(1)
                    name = item.name.replace('Generic', container)
                    yield Token(match.group(), name)
                else:
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
            self.current = Token(REV_ESC_MAP['\\'+item.data], 'Text')
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
        while self.current.name != 'EndOption':
            self.next()
            if self.current.name == 'Text':
                result = self.__parse_text__()
        self.next()
        return result.split(',')

    def __parse_arguments__(self):
        while self.current.name != 'EndArgument':
            self.next()
            result = self.__recursive_parse__('EndArgument')
        self.next()
        return result

    def __parse_function__(self):
        command = re.search(r'\w+', self.current.data).group()
        result = {'command' : command}
        self.next()
        while self.current.name in ('StartOption', 'StartArgument'):
            if self.current.name == 'StartOption':
                result['options'] = self.__parse_options__()
            elif self.current.name == 'StartArgument':
                result['arguments'] = (self.__parse_arguments__())
        return result

    def __parse_math__(self):
        self.next()
        return self.__recursive_parse__('Math')

    def __parse_object__(self):
        result = ({'object' : self.current.name.replace('Begin', '')})
        condition = self.current.name.replace('Begin', 'End')
        self.next()
        if self.current.name == 'StartOption':
            result['options'] = self.__parse_options__()
        result['data'] = (self.__recursive_parse__(condition))
        if self.current.name == condition:
            self.next()
        else:
            raise TeXError(E_SYNTAX.format(self.current.name, condition))
        return result

    def __recursive_parse__(self, condition):
        result = []
        while self.current.name != condition:
            if self.current.name == 'Comment':
                result.append(self.__parse_comment__())
            elif self.current.name == 'Text':
                result.append(self.__parse_text__())
            elif self.current.name == 'Math':
                result.append(self.__parse_math__())
            elif 'Begin' in self.current.name:
                result.append(self.__parse_object__())
            elif self.current.name == 'Function':
                result.append(self.__parse_function__())
            elif self.current.name == 'Newline':
                self.next()
            elif self.current.name in condition:
                break
            else:
                raise TeXError(E_SYNTAX.format(self.current.name, condition))
        return result

    def parse(self):
        self.next()
        return self.__recursive_parse__(condition='EOF')
