tools.py
#!/usr/bin/env python

"""
:copyright: (c) 2014 by Mike Taylor
:license: MIT, see LICENSE for more details.
"""

import os, sys
import json

def mkpath(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def normalizeFilename(filename):
    result = os.path.expanduser(filename)
    result = os.path.abspath(result)
    return result

def loadConfig(cfgFilename):
    result = {}

    if not os.path.exists(cfgFilename):
        for cfgpath in configPaths:
            possibleFile = normalizeFilename(os.path.join(cfgpath, configName))
            if os.path.exists(possibleFile):
                result = json.load(open(possibleFile, 'r'))
                break
    else:
        possibleFile = normalizeFilename(cfgFilename)
        if os.path.exists(possibleFile):
            result = json.load(open(possibleFile, 'r'))

    return result
