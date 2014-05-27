#!/usr/bin/env python

import unittest
import datetime

from context import hakkan


class TestSiteGeneration(unittest.TestCase):
    def runTest(self):
        site = hakkan.Site('./tests/hakkan.cfg')

        assert site.templateEnv is not None
        assert len(site.posts) == 4
        assert len(site.tags) == 1

        # yes, these variables must match the test content
        # easier to cut-n-paste than gunk up tests with a lot of
        # parsing to test the parsing 
        # (just don't look at testTools.py cause I kinda do that there ;)

        headerKeys     = [ "20140101140100.test-content-2014-001-Jan-1-2014", 
                           "20140301140100.test-content-2014-060-Mar-1-2014",
                           "20131101140100.test-content-2013-305-Nov-1-2013",
                           "20140201140100.test-content-2014-032-Feb-1-2014"
                         ]
        headerCheckKey = "20140301140100.test-content-2014-060-Mar-1-2014"
        headerChecks   = [ ("title",   "Test Content 2014 060 Mar 1 2014"),
                           ("date",    datetime.datetime.strptime("2014-03-01 14:01:00", '%Y-%m-%d %H:%M:%S')),
                           ("tags",    "mutterings"),
                           ("author",  "bear"), 
                           ("slug",    "test-content-2014-060-Mar-1-2014"),
                           ("summary", "Test Content 2014 060 Mar 1 2014")
                         ]
        contentCheck   = """Test Content for March 1st 2014 - paragraph one

paragraph two
"""
        htmlCheck      = """<p>Test Content for March 1st 2014 - paragraph one</p>

<p>paragraph two</p>
"""

        for key in headerKeys:
            assert key in site.posts

        post = site.posts[headerCheckKey]
        assert len(post.headers) == len(headerChecks)

        for key, value in headerChecks:
            assert key in post.attribs
            assert post.attribs[key] == value

        assert len(post.lines) == 3
        assert len(post.content) == len(contentCheck)
        assert post.content == contentCheck
        assert len(post.html) == len(htmlCheck)
        assert post.html == htmlCheck

        self.generatePosts()

        assert False

        # site.generate()
