#!/usr/bin/env python

"""
:copyright: (c) 2014 by Mike Taylor
:license: MIT, see LICENSE for more details.
"""

import os, sys
import argparse

from hakkan import Site


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('configFilename')

    args = parser.parse_args()
    site = Site(args.configFilename)

    site.generate()