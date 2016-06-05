from pkg_resources import resource_filename
import pytest
from PyTeX import latex, lexer, tex

@pytest.fixture
def simple():
    with open(resource_filename('test', 'data/simple.tex'), 'r') as f:
        return lexer.FileIn(f, tex.SUB_DICT)

@pytest.fixture
def standard():
    with open(resource_filename('test', 'data/standard.tex'), 'r') as f:
        return lexer.FileIn(f, tex.SUB_DICT)

def test_FileIn(f=simple):
    assert f().read() == """\\documentclass{article}\n\n\\begin{document}\n\nThis is a LaTeX document.\n\n\\end{document}"""

def test_simple_Parser(f=simple):
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

def test_standard_Parser(f=standard):
    token_list = []
    for token in f().tokenize(tex.REGEX_LIST):
        token_list.append(token.name)
    assert 'Beginequation' in token_list
    assert 'Section' in token_list
    assert len(token_list) >= 1500

def test_compiler(f=simple):
    parser = tex.Parser(f().tokenize(tex.REGEX_LIST))
    assert parser.parse() == [
    {'documentclass': {'arguments': ['article']}},
    {'document': {'data': ['This is a LaTeX document.']}}
    ]
