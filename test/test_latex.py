#!/bin/env python

from PyTeX import latex
import pytest

def test_load_tex():
    with open('test/data/simple.tex') as f:
        data = latex.load(f)
    assert len(data) > 1
    assert data[0] == {'documentclass': {'arguments': ['article']}}

def test_load_bib():
    with open('test/data/simple.bib') as f:
        data = latex.load(f)
    assert 'test' in data
    assert 'author' in data['test']

def test_search():
    data = [{'textit' : {'arguments' : [{'textbf' : {'arguments' : ['word']}}]}}]
    results = latex.find('arguments', data)
    assert 'arguments' in results[0]
