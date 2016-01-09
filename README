---
Title : PyTeX -- LaTeX i/o for Python
Author : Dillon Niederhut
---

## Description

** In development **

Easy-ish translation between data objects and the DOM we know as LaTeX.

## Usage

~~~{.input}
from pprint import pprint
from PyTeX import json

with open('data/simple.tex', 'r') as f:
    data = json.loads(f)
pprint(data)
~~~

~~~{.output}
[{'arguments': [['article']], 'command': 'documentclass'},
 {'arguments': [['document']], 'command': 'begin'},
 'This is a LaTeX document.',
 {'arguments': [['document']], 'command': 'end'}]
~~~
