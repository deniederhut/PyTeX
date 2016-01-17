---
Title : PyTeX -- LaTeX i/o for Python
Author : Dillon Niederhut
---

## Description

**In development**

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
[{'arguments': ['article'], 'command': 'documentclass'},
 {'data': ['This is a LaTeX document.'], 'object': 'document'}]
~~~

~~~{.input}
json.find('data', data)
~~~

~~~{.output}
[{'data': ['This is a LaTeX document.']}]
~~~
