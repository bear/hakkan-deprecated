#!/usr/bin/env python

import os
import sys
import unittest

from context import hakkan


class TestNormalize(unittest.TestCase):
    def runTest(self):
        homePath         = os.path.expanduser('~/')
        homeFile         = ''
        fullFilename     = os.path.abspath(__file__)
        fullDir          = os.path.dirname(fullFilename)
        ourFilename      = os.path.basename(fullFilename)
        ourFullname      = os.path.join(fullDir, ourFilename)
        basePath, ourDir = os.path.split(fullDir)
        _, parentDir     = os.path.split(basePath)

        for p in ('.profile', '.bash_profile', '.zprofile', '.bashrc'):
            if os.path.exists(os.path.join(homePath, p)):
                homeFile = p
                break

        #
        # Note: the test runner will make cwd the parent dir of tests/ so
        #       all results need to have '/tests/' (aka ourDir) added to work

        tests    = ( ('~/%s'          % homeFile, os.path.join(homePath, homeFile)),
                     ('../%s/%s/%s'   % (parentDir, ourDir, ourFilename), ourFullname),
                     ('./../%s/%s/%s' % (parentDir, ourDir, ourFilename), ourFullname),
                     ('./%s/%s'       % (ourDir, ourFilename), ourFullname),
                     ('%s/%s'         % (fullDir, ourFilename), fullFilename)
                   )

        assert os.path.join(fullDir, ourFilename) == __file__

        for sample, success in tests:
            assert hakkan.normalizeFilename(sample) == success

class TestFindFile(unittest.TestCase):
    def runTest(self):
        fullDir          = os.path.dirname(os.path.abspath(__file__))
        basePath, ourDir = os.path.split(fullDir)
        _, parentDir     = os.path.split(basePath)

        cfgFile  = 'hakkan.cfg'

        badPaths  = [ '/home/foo', '/foo/bar', '../../' ]
        goodPaths = [ fullDir, 
                      '../%s/%s' % (parentDir, ourDir),
                      './%s/'    % ourDir, 
                    ]

        for testPath in badPaths:
            filename = hakkan.findFile(cfgFile, testPath)
            assert filename == cfgFile

        for testPath in goodPaths:
            sample   = os.path.join(testPath, cfgFile)
            filename = hakkan.findFile(cfgFile, testPath)
            assert hakkan.normalizeFilename(sample) == hakkan.normalizeFilename(filename)
