import pytest
from PyTeX import tex, json

@pytest.fixture
def file_in():
    with open('data/simple.tex') as f:
        return tex.FileIn(f)

def test_FileIn(f=file_in):
    assert f().read() == """\\documentclass{article}\n\n\\begin{document}\n\nThis is a LaTeX document.\n\n\\end{document}"""

def test_Parser(f=file_in):
    token_list = []
    for token in tex.tokenize(f().read()):
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

def test_compiler(f=file_in):
    parser = tex.Parser(tex.tokenize(f().read()))
    assert parser.parse() == [
    {'arguments': ['article'], 'command': 'documentclass'},
    {'data': ['This is a LaTeX document.'], 'object': 'document'}
    ]
