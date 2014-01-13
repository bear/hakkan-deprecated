#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='hakkan',
    version='0.1.0',
    description='Site Publishing Toolkit',
    long_description=readme,
    author='Mike Taylor',
    author_email='bear@bear.im',
    url='https://github.com/bear/hakkan',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)