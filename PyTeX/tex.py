import collections
from PyTeX import error, tokenizer
import re
import types

# Character Escaping

ESC_MAP = {r'&' : r'\\&', r'%' : r'\\%', r'$' : r'\\$', r'#' : r'\\#', r'_' : r'\\_', r'{' : r'\\{', r'}' : r'\\{', r'~' : r'\\~', r'^' : r'\\^', r'<' : r'\\<', r'>' : r'\\>'}
REV_ESC_MAP = {value : key for key, value in ESC_MAP.items()}
FROM_TEX_SUB = {r'\\\\' : r'\n'}

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

REGEX_LIST = [P_COMMENT, P_NEWLINE, P_MATH, P_ESCAPED, P_START_GEN, P_END_GEN, P_FUNCTION, P_START_ARG, P_START_OPT, P_END_ARG, P_END_OPT, P_TEXT]


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

    @staticmethod
    def del_empty_keys(dictionary):
        result = {}
        for key in dictionary:
            if dictionary[key]:
                result[key] = dictionary[key]
        return result

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
        result = {'arguments' : [], 'options' : []}
        self.next()
        while self.current.name in ('StartOption', 'StartArgument'):
            if self.current.name == 'StartOption':
                result['options'] += self.__parse_options__()
            elif self.current.name == 'StartArgument':
                result['arguments'] += self.__parse_arguments__()
        result = self.del_empty_keys(result)
        return {command : result}

    def __parse_math__(self):
        self.next()
        return {'equation' : self.__recursive_parse__('Math')}

    def __parse_object__(self):
        result = {'options':[]}
        command = self.current.name.replace('Begin', '')
        condition = self.current.name.replace('Begin', 'End')
        self.next()
        if self.current.name == 'StartOption':
            result['options'] += self.__parse_options__()
        result['data'] = (self.__recursive_parse__(condition))
        if self.current.name == condition:
            self.next()
        else:
            raise error.TeXError(error.E_SYNTAX.format(self.current.name, condition))
        result = self.del_empty_keys(result)
        return {command : result}

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
                raise error.TeXError(error.E_SYNTAX.format(self.current.name, condition))
        return result

    def parse(self):
        self.next()
        return self.__recursive_parse__(condition='EOF')
