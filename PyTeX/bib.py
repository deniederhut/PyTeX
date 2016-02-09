import collections
from PyTeX import error
import re

# Character Escaping

ESC_MAP = {r'@' : r'\\@'}
REV_ESC_MAP = {value : key for key, value in ESC_MAP.items()}
SUB_DICT = {'\n', ' '}

# Regular Expression Patterns

regex = collections.namedtuple('regex', ['name', 'pattern'])

P_ASSIGN = regex('Assign', re.compile(r'='))
P_END = regex('End', re.compile(r'\}'))
P_ITEM = regex('Item', re.compile(r'@[a-z]+', flags=re.I))
P_NEXT = regex('Next', re.compile(r','))
P_NUMBER = regex('Number', re.compile(r'[0-9]+'))
P_QUOTE = regex('Quote', re.compile(r"'"))
P_DQUOTE = regex('DoubleQuote', re.compile(r'"'))
P_START = regex('Start', re.compile(r'\{'))
P_TEXT = regex('Text', re.compile(r"[\w/`\'\:\.\(\)=@\*\-]+", flags=re.I))

REGEX_LIST = [P_ASSIGN, P_END, P_ITEM, P_NEXT, P_NUMBER, P_QUOTE, P_DQUOTE, P_START, P_TEXT]

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

    def __parse_text__(self):
        result = self.current.data
        self.next()
        while self.current.name == 'Text':
            self.next()
            if self.current.name == 'Text':
                result += ' ' + self.current.data
        return result

    def __parse_object__(self, condition):
        result = []
        self.next()
        while self.current.name != condition:
            self.__parse_text__()
            result.append(self.next())
        if self.current.name != condition:
            raise error.TeXError(E_SYNTAX.format(self.current.name, condition))
        self.next()
        return ' '.join(result)

    def __parse_assignments__(self):
        while self.current.name != 'End':
            key = self.current.data
            self.next()
            if self.current.name != 'Assign':
                raise error.TeXError(E_SYNTAX.format(self.current.data, '='))
            self.next()
            if self.current.name == 'Number':
                return key, self.current.data
            elif self.current.name == 'Text':
                return key, self.__parse_text__()
            elif self.current.name in ('Quote', 'DoubleQuote', 'Start'):
                return key, self.__parse_object__(condition=self.current.name)
        self.next()

    def __parse_items__(self):
        result = []
        while self.current.name != 'EOF':
            if self.current.name == 'Item':
                item = {'type' : self.current.data.replace('@','')}
                self.next()
                if self.current.name != 'Start':
                    raise error.TeXError(E_SYNTAX.format(self.current.data, '{'))
                self.next()
                if self.current.name != 'Text':
                    raise error.TeXError(E_SYNTAX.format(self.current.data, 'text'))
                item['label'] = self.__parse_text__()
                self.next()
                if self.current.name != 'Next':
                    raise error.TeXError(E_SYNTAX.format(self.current.data, ','))
                self.next()
                for key, value in self.__parse_assignments__():
                    item[key] = value
                self.next()
            else:
                raise error.TeXError(E_SYNTAX.format(self.current.data, condition))
        return result

    def parse(self):
        self.next()
        return self.__parse_items__()