import re
import types

# Character Escaping

ESC_MAP = {'&' : '\\&', '%' : '\\%', '$' : '\\$', '#' : '\\#', '_' : '\\_', '{' : '\\{', '}' : '\\{', '~' : '\\~', '^' : '\\^'}
REV_ESC_MAP = {value : key for key, value in ESC_MAP.items()}
FROM_TEX_SUB = {r'\\\\' : r'\n'}

# Error Messages

E_ENCODING = 'File not in valid TeX encoding'
E_INPUT = 'Unrecognized input'

# Regular Expression Patterns

# add begin
# add item
P_ARGUMENTs = re.compile(r'\{((?P<arguments>[\w\.\{\}\\ ]+)\})*', flags=re.I)
P_COMMAND = re.compile(r'\\(?P<command>\w+)', flags=re.I)
P_COMMENT = re.compile(r'%(?P<comment>.+)\n', flags=re.I)
P_TEXT = re.compile(r'(?P<text>([\w ]+[\n]{0,1})+)', flags=re.I)
P_OPTIONS = re.compile(r'(\[(?P<options>[\w,=\.]+)\])', flags=re.I)

class TeXError(Exception):

    def __init__(self, msg, stm=None, pos=0):
        if stm:
            msg += ' at position {}, "{}"'.format(pos, repr(stm.substr(post, 32)))
        Exception.__init__(self, msg)

class ArgumentsToken(object):

    def __init__(self, string):
        self.data = string.split('}{')

class CommandToken(object):

    def __init__(self, string):
        self.data = string

class CommentToken(object):

    def __init__(self, string):
        self.data = string

class EOFToken(object):
    pass

class TextToken(object):

    def __init__(self, string):
        self.data = string

class OptionsToken(object):

    def __init__(self, string):
        pass

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
    skip_list = [' ', '\n']
    while string:
        while string[0] in skip_list:
            string = string[1:]
        comment_match = P_COMMENT.match(string)
        if comment_match:
            string = string[comment_match.end():]
            yield CommentToken(comment_match.group('comment'))
        else:
            command_match = P_COMMAND.match(string)
            if command_match:
                string = string[command_match.end():]
                yield CommandToken(command_match.group('command'))
            else:
                options_match = P_OPTIONS.match(string)
                if options_match:
                    string = string[options_match.end():]
                    yield OptionsToken(options_match.group('options'))
                else:
                    arguments_match = P_ARGUMENTs.match(string)
                    if arguments_match:
                        string = string[arguments_match.end():]
                        yield ArgumentsToken(arguments_match.group('arguments'))
                    else:
                        tmp_string = copy(string)
                        for key, value in REV_ESC_MAP:
                            tmp_string = re.sub(key, value, tmp_string)
                        text_match = P_TEXT.match(string)
                        if text_match:
                            n_missing = len(string) - len(tmp_string)
                            string = string[text_match.end() + n_missing:]
                            yield TextToken(text_match.group('text'))
                        else: raise TexError(' - '.join([E_INPUT, string[:25]]))
    yield EOFToken()

class Parser(object):

    def next():
        self.current = self.lexer.__next__()

    def __init__(self, lexer):
        self.lexer = lexer
        self.next()

    def parse(self):
        stack = []
        result = []
        state = 1
        while state != 0:
            if state == 1:
                self.next()
                if is.instance(self.current, CommentToken):
                    result.append(self.current)
                if is.instance(self.current, CommandToken):
                    pass
                if is.instance(self.current, TextToken):
                    pass
                state = 1
            if state == 2:
                if is.instance(self.current, OptionsToken):
                    pass
                    self.next()
                if is.instance(self.current, ArgumentsToken):
                    pass
                    self.next()
                state = 0
        return result

def loads(f):
    return Parser(tokenize(FileIn(f))).parse()

def dumps(obj, f):
    return True

def find(obj):
    return True
