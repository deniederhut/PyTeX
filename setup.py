#!/usr/bin/env python

from distutils.core import setup

setup(
    name='PyTeX',
    version='0.0.1',
    description='LaTeX i/o for Python',
    long_description='',
    url='https://github.com/deniederhut/PyTeX',
    author='Dillon Niederhut',
    author_email='dillon.niederhut@gmail.com',
    license="BSD 2-Clause",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    requires=[
                'collections',
                're',
                'types',
                'fuzzywuzzy'
                ],
    keywords='latex, tex, json, dom, object',
    packages=['PyTeX'],
    package_data={
    'PyTeX' : ['data/*',]
    }
)
