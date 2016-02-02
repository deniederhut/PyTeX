#!/bin/env python

def del_empty_keys(dictionary):
    result = {}
    for key in dictionary:
        if dictionary[key]:
            result[key] = dictionary[key]
    return result
