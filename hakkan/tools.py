#!/usr/bin/env python

"""
:copyright: (c) 2014 by Mike Taylor
:license: MIT, see LICENSE for more details.
"""

import os, sys
import json
import types


_configPaths = (os.getcwd(), '~/', '~/.hakkan/')
_configName  = 'hakkan.cfg'


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
    result = os.path.normpath(result)
    return result

def findFile(filename, paths):
    result = filename

    if isinstance(paths, types.TupleType) or isinstance(paths, types.ListType):
        checkPaths = paths
    else:
        checkPaths = [ paths, ]

    if not os.path.exists(filename):
        for path in checkPaths:
            possibleFilename = normalizeFilename(os.path.join(path, filename))
            if os.path.exists(possibleFilename):
                result = possibleFilename
                break
    else:
        possibleFilename = normalizeFilename(filename)
        if os.path.exists(possibleFilename):
            result = possibleFilename

    return result

def loadConfig(configFilename=_configName, configPaths=_configPaths):
    result   = {}
    filename = findFile(configFilename, configPaths)

    if os.path.exists(filename):
        result = json.load(open(filename, 'r'))

    return result
