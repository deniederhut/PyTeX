
# PyTeX -- LaTeX i/o for Python

[![DOI](https://zenodo.org/badge/18094/deniederhut/PyTeX.svg)](https://zenodo.org/badge/latestdoi/18094/deniederhut/PyTeX)  [![Build Status](https://travis-ci.org/deniederhut/PyTeX.svg?branch=master)](https://travis-ci.org/deniederhut/PyTeX)  [![codecov.io](https://codecov.io/github/deniederhut/PyTeX/coverage.svg?branch=master)](https://codecov.io/github/deniederhut/PyTeX?branch=master)

## Description

**In development**

Easy-ish translation between data objects and the DOM we know as LaTeX.

## Usage

#### Compiling a .tex document to a json object:

~~~{.input}
from pprint import pprint
from PyTeX import latex

with open('data/simple.tex', 'r') as f:
    data = latex.load(f)
pprint(data)
~~~

~~~{.output}
[{'documentclass': {'arguments': ['article']}},
 {'document': {'data': ['This is a LaTeX document.']}}]
~~~

#### Compiling a .bib document to a json object

~~~{.input}
from pprint import pprint
from PyTeX import latex

with open('data/simple.bib', 'r') as f:
    data = latex.load(f)
pprint(data)
~~~

~~~{.output}
{'test': {'author': 'Dillon Niederhut',
          'title': 'Structured data with PyTeX',
          'type': 'article',
          'year': '2016'}}
~~~

#### Recursive, fuzzy searching of a json object:

~~~{.input}
for result in latex.find('data', data):
    pprint(result)
~~~

~~~{.output}
{'data': ['This is a LaTeX document.']}
~~~
