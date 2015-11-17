import re

def _parse_command(string):
    p = re.compile(r'\\(?P<command>\w+)((?P<options>[\w,=\.\[\]]+)){0,1}((?P<args>[\w\.\{\}\\ ]+))*', flags=re.IGNORECASE)
    match = re.search(p, string)
    if match:
        command = match.group('command')
        if match.group('options'):
            options = match.group('options').strip('[]').split(',')
        else:
            options = None
        if match.group('args'):
            args = re.findall(r'(?<=\{)[\w\.\\ ]*(?=\})', match.group('args'))
        else:
            args = None
        return {'command' : command,
                'options' : options,
                'args' : args}
    else:
        return None

def _strip(string, pattern, flags):
    """ """
    p = re.compile(pattern, flags)
    match = re.search(p, string).group('match')
    string = string.replace(match, '')
    return string, match

def _parse_comments(string):
    """Strip comments from string, return string and comments"""
    item_list = []
    p = re.compile(r'%.+\n', flags=re.IGNORECASE)
    for comment_line in re.finditer(p, string):
        item_list.append(comment_line.group())
        string = string.replace(comment_line.group(), '')
    return string, item_list

def _parse_header(string):
    """Strip header from string, return string and header"""
    string, header = _strip(string, pattern=r'^(?P<match>.+)\\begin{document}', flags=re.DOTALL|re.IGNORECASE)
    item_list = []
    p = re.compile(r'\\.+')
    for match in re.findall(p, header):
        item_list.append(_parse_command(match))
    return string, item_list

def _parse_body(string):
    """ """


def loads(string):
    """Parse LaTeX-formatted string into nested dictionary"""
    string = string.strip(' \n')
    string, comment_list = _parse_comments(string)
    string, header_list = _parse_header(string)
    string, body_list = _parse_body(string)
    if len(string) > 0:
        print("The algorithm failed to match the following: {}".format(string))
    return {'header' : header_list,
            'body' : body_list,
            'comments' : comment_list}

def dumps(string):
    """Parse dictionary into LaTeX-formatted string"""
