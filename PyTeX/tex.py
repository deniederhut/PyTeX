#!/bin/env python

from __future__ import absolute_import

import collections
from PyTeX import error, utilities
from PyTeX.lexer import Token
import re

# Character Escaping

ESC_MAP = {r'&' : r'\\&', r'%' : r'\\%', r'$' : r'\\$', r'#' : r'\\#', r'_' : r'\\_', r'{' : r'\\{', r'}' : r'\\{', r'~' : r'\\~', r'^' : r'\\^', r'<' : r'\\<', r'>' : r'\\>'}
REV_ESC_MAP = {value : key for key, value in ESC_MAP.items()}
SUB_DICT = {r'\\\\' : r'\n'}

# Regular Expression Patterns
regex = collections.namedtuple('regex', ['name', 'pattern'])

P_START_GEN = regex('BeginGeneric', re.compile(r'\\begin\{\w+\}'))
P_COMMENT = regex('Comment', re.compile(r'%.+\n', flags=re.I))
P_END_ARG = regex('EndArgument', re.compile(r'\}'))
P_END_GEN = regex('EndGeneric', re.compile(r'\\end\{\w+\}'))
P_END_OPT = regex('EndOption', re.compile(r'\]'))
P_ESCAPED = regex('Escaped', re.compile(r'|'.join(REV_ESC_MAP.keys())))
P_FUNCTION = regex('Function', re.compile(r'\\\w+'))
P_INV_FUNCTION = regex('InverseFunction', re.compile(r'\{\s*?\\em[a-z0-9\s\.]+?\}'))
# P_ITEM = regex('Item', re.compile(r'\\item'))
P_MATH = regex('Math', re.compile(r'\$'))
P_NEWLINE = regex('Newline', re.compile(r'\n|\\\\'))
P_SECTION = regex('Section', re.compile(r'\\section'))
P_SUBSECTION = regex('Subsection', re.compile(r'\\subsection'))
P_START_ARG = regex('StartArgument', re.compile(r'\{'))
P_START_OPT = regex('StartOption', re.compile(r'\['))
P_TEXT = regex('Text', re.compile(r'[\w/:~+`\'\,\.\(\)=&@\*\-]+', flags=re.I))

REGEX_LIST = [P_COMMENT, P_NEWLINE, P_SECTION, P_SUBSECTION, P_MATH, P_ESCAPED, P_INV_FUNCTION, P_START_GEN, P_END_GEN, P_FUNCTION, P_START_ARG, P_START_OPT, P_END_ARG, P_END_OPT, P_TEXT]


class Parser(object):

    def __init__(self, lexer):
        self.lexer = lexer
        self.current = None

    def next(self):
        item = next(self.lexer)
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
        while self.current.name not in ['EndOption']:
            self.next()
            if self.current.name == 'Text':
                result = self.__parse_text__()
        self.next()
        return result.split(',')

    def __parse_arguments__(self):
        while self.current.name not in ['EndArgument']:
            self.next()
            result = self.__recursive_parse__(['EndArgument'])
        self.next()
        return result

    def __parse_function__(self):
        command = re.search(r'\w+', self.current.data).group()
        result = {'arguments' : [], 'options' : []}
        self.next()
        while self.current.name in ['StartOption', 'StartArgument']:
            if self.current.name == 'StartOption':
                result['options'] += self.__parse_options__()
            elif self.current.name == 'StartArgument':
                result['arguments'] += self.__parse_arguments__()
        result = utilities.del_empty_keys(result)
        return {command : result}

    def __parse_inverse__(self):
        match = re.search(r'(?:\{)(?P<command>\\\w+)(?P<data>[a-z0-9\.\s]+?)(?:\})', self.current.data)
        command = match.group('command')
        result = {'arguments' : match.group('data')}
        self.next()
        return {command : result}

    def __parse_math__(self):
        self.next()
        return {'equation' : self.__recursive_parse__(['Math'])}

    def __parse_object__(self):
        result = {'options':[]}
        command = self.current.name.replace('Begin', '')
        condition = [self.current.name.replace('Begin', 'End')]
        self.next()
        if self.current.name == 'StartOption':
            result['options'] += self.__parse_options__()
        result['data'] = (self.__recursive_parse__(condition))
        if self.current.name in condition:
            self.next()
        else:
            raise error.TeXError(error.SYNTAX.format(self.current.name, condition))
        result = utilities.del_empty_keys(result)
        return {command : result}

    def __parse_section__(self, conditions):
        command = re.search(r'\w+', self.current.data).group()
        result = {'data' : []}
        self.next()
        result['name'] = self.__parse_arguments__()
        result['data'] = self.__recursive_parse__(conditions)
        result = utilities.del_empty_keys(result)
        return {command : result}

    def __recursive_parse__(self, condition):
        result = []
        while self.current.name not in condition:
            if self.current.name == 'Comment':
                result.append(self.__parse_comment__())
            elif self.current.name == 'Section':
                result.append(self.__parse_section__(['Section', 'Enddocument']))
            elif self.current.name == 'Subsection':
                result.append(self.__parse_section__(['Section', 'Subsection', 'Enddocument']))
            elif self.current.name == 'Text':
                result.append(self.__parse_text__())
            elif self.current.name == 'Math':
                result.append(self.__parse_math__())
            elif 'Begin' in self.current.name:
                result.append(self.__parse_object__())
            elif self.current.name == 'InverseFunction':
                result.append(self.__parse_inverse__())
            elif self.current.name == 'Function':
                result.append(self.__parse_function__())
            elif self.current.name == 'Newline':
                self.next()
            elif self.current.name in condition:
                break
            else:
                raise error.TeXError(error.SYNTAX.format(self.current.name, condition))
        return result

    def parse(self):
        self.next()
        return self.__recursive_parse__(condition=['EOF'])
