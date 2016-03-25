#!/bin/env python

# Error Messages

ENCODING = 'File in unexpected coding: {}'
INPUT = 'Unrecognized input'
SYNTAX = '{} where {} was expected'
EOF = 'Unexpected end of {}'

class TeXError(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)
