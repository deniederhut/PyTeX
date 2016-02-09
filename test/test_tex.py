import pytest
from PyTeX import json, lexer, tex

@pytest.fixture
def simple():
    with open('data/simple.tex') as f:
        return lexer.FileIn(f, tex.SUB_DICT)

def test_FileIn(f=simple):
    assert f().read() == """\\documentclass{article}\n\n\\begin{document}\n\nThis is a LaTeX document.\n\n\\end{document}"""

def test_Parser(f=simple):
    token_list = []
    for token in f().tokenize(tex.REGEX_LIST):
        token_list.append(token.name)
    assert token_list == ['Function',
                         'StartArgument',
                         'Text',
                         'EndArgument',
                         'Newline',
                         'Newline',
                         'Begindocument',
                         'Newline',
                         'Newline',
                         'Text',
                         'Text',
                         'Text',
                         'Text',
                         'Text',
                         'Newline',
                         'Newline',
                         'Enddocument',
                         'EOF']

def test_compiler(f=simple):
    parser = tex.Parser(f().tokenize(tex.REGEX_LIST))
    assert parser.parse() == [
    {'documentclass': {'arguments': ['article']}},
    {'document': {'data': ['This is a LaTeX document.']}}
    ]
