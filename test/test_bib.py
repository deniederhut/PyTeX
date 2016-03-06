import pytest
from PyTeX import latex, lexer, bib

@pytest.fixture
def simple():
    with open('test/data/simple.bib') as f:
        return lexer.FileIn(f, bib.SUB_DICT)

def test_FileIn(f=simple):
    assert f().read() == """@article{test,   author = {Dillon Niederhut},   title={Structured data with PyTeX},   year=2016 }"""

def test_Parser(f=simple):
    token_list = []
    for token in f().tokenize(bib.REGEX_LIST):
        token_list.append(token.name)
    assert token_list == [
        'Item',
        'Start',
        'Text',
        'Next',
        'Text',
        'Assign',
        'Start',
        'Text',
        'Text',
        'End',
        'Next',
        'Text',
        'Assign',
        'Start',
        'Text',
        'Text',
        'Text',
        'Text',
        'End',
        'Next',
        'Text',
        'Assign',
        'Number',
        'End',
        'EOF'
    ]

def test_compiler(f=simple):
    parser = bib.Parser(f().tokenize(bib.REGEX_LIST))
    assert parser.parse() == {
    'test' : {
        'author' : 'Dillon Niederhut',
        'title' : 'Structured data with PyTeX',
        'type' : 'article',
        'year' : '2016'
        }
    }
