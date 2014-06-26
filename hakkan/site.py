#!/usr/bin/env python

"""
:copyright: (c) 2014 by Mike Taylor
:license: MIT, see LICENSE for more details.

generate a website
"""

import os, sys
import json
import shutil
import datetime
import argparse

from tools import normalizeFilename, loadConfig, mkpath

import jinja2
import misaka

import pprint
pp = pprint.PrettyPrinter(indent=2)

markdownExtras = misaka.EXT_FENCED_CODE | misaka.EXT_NO_INTRA_EMPHASIS
markdownFlags  = misaka.HTML_SMARTYPANTS


class Post(object):
    """A single post.

    Created by pointing to a filename that is contains the markdown+ content.

    markdown+ in my use is a block of key:value metadata, a blank line and the
    markdown formated content.
    """
    def __init__(self, postFilename, baseurl):
        self.filename = normalizeFilename(postFilename)
        self.baseurl  = baseurl

        self.clear()
        self.load()

    def clear(self):
        self.key       = None
        self.lines     = []
        self.content   = ''
        self.headers   = []
        self.metadata  = {}
        self.frontpage = False
        self.attribs   = { 'baseurl': self.baseurl }

    def load(self, filename=None):
        if filename is not None:
            self.filename = normalizeFilename(filename)

        self.clear()

        if os.path.exists(self.filename):
            header = True
            for line in open(self.filename, 'r').readlines():
                item = line.decode('utf-8', 'xmlcharrefreplace')

                if header and len(item.strip()) == 0:
                    header = False

                if header:
                    item = item.strip() # remember, newlines bad in headers, good in body content
                    self.headers.append(item)

                    key, value = item.split(':', 1)
                    key        = key.lower()
                    value      = value.strip()

                    if key == 'date':
                        self.attribs[key] = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    else:
                        self.attribs[key] = value
                else:
                    self.lines.append(item)

            self.lines               = self.lines[1:]  # remove header/body separator
            self.attribs['modified'] = os.path.getmtime(self.filename)
            self.attribs['created']  = os.path.getctime(self.filename)
            self.attribs['index']    = self.attribs['date'].strftime('%Y%m%d%H%M%S')
            self.attribs['year']     = self.attribs['date'].strftime('%Y')
            self.attribs['doy']      = self.attribs['date'].strftime('%j')
            self.attribs['baseurl']  = self.baseurl
            self.attribs['url']      = '%(baseurl)s%(year)s/%(doy)s/%(slug)s' % self.attribs
            self.content             = ''.join(self.lines)
            self.html                = misaka.html(self.content, extensions=markdownExtras, render_flags=markdownFlags)
            self.key                 = '%(index)s.%(slug)s' % self.attribs 


class Site(object):
    """A Site.

    The Site contains the configuration items required to manage templates,
    gather Posts and then generate the required output for the site.

    configuration example:
            { "title":        "Hakkan Site",
              "input_dir":    "./content",
              "output_dir":   "./output",
              "static_dir":   "./static",
              "template_dir": "./templates/",
              "baseurl":      "/staticsite/",
              "templates":  { "index":   "index.jinja",
                              "article": "article.jinja",
                              "archive": "archive.jinja",
                              "tags":    "tags.jinja"
                            },
               "meta":      { "description": "a Hakkan generated site",
                              "author":      "bear",
                              "keywords":    "bear,English,USA,Philadelphia,Pennsylvania",
                            }
               }
            }
    """
    def __init__(self, cfgFilename):
        self.cfgFilename = cfgFilename
        self.templateEnv = None
        self.posts       = {}
        self.postFiles   = {}
        self.tags        = {}
        self.years       = {}
        self.cfg         = loadConfig(self.cfgFilename)
        self.templateMap = self.cfg['templates']
        self.indexCount  = getattr(self.cfg, 6)

        for key in ('input_dir', 'output_dir', 'static_dir', 'template_dir'):
            if key in self.cfg:
                if not os.path.exists(normalizeFilename(self.cfg[key])):
                    raise Exception('Configuration path item [%s] [%s] not found.' % (key, self.cfg[key]))
            else:
                raise Exception('Required configuration item [%s] not present.' % key)

        self.outputDir = self.cfg['output_dir']

        if not os.path.exists(self.outputDir):
            mkpath(self.outputDir)

        self.loadTemplates()
        self.findPosts()

    def loadTemplates(self):
        self.templateLoader = jinja2.FileSystemLoader(searchpath=self.cfg['template_dir'])
        self.templateEnv    = jinja2.Environment(loader=self.templateLoader)

        self.articlePage = self.templateEnv.get_template(self.templateMap['article'])
        self.archivePage = self.templateEnv.get_template(self.templateMap['archive'])
        self.tagsPage    = self.templateEnv.get_template(self.templateMap['tags'])
        self.indexPage   = self.templateEnv.get_template(self.templateMap['index'])

    def findByFilename(self, filename):
        postFilename = normalizeFilename(filename)

        if postFilename not in self.postFiles:
            post = Post(postFilename, self.cfg['baseurl'])

            self.postFiles[postFilename] = post.key
            self.posts[post.key]         = post

            taglist = post.attribs['tags'].split(',')

            for s in taglist:
                tag = s.strip()
                if tag not in self.tags:
                    self.tags[tag] = []
                self.tags[tag].append(post.key)

            year = post.attribs['year']
            if year not in self.years:
                self.years[year] = []
            self.years[year].append(post.key)

    def findPosts(self):
        for path, dirlist, filelist in os.walk(self.cfg['input_dir']):
            if len(filelist) == 1 and filelist[0][-3:] == '.md':
                self.findByFilename(os.path.join(path, filelist[0]))

    def copyStatic(self, staticDir, outputDir):
        baseDir    = os.path.abspath(self.cfg['static'])
        targetBase = os.path.abspath(self.outputDir)

        for path, dirlist, filelist in os.walk(baseDir):
            sourceDir = os.path.abspath(path)
            targetDir = '%s/%s' % (targetBase, path.replace(baseDir, ''))

            for filename in filelist:
                if not os.path.exists(targetDir):
                    mkpath(targetDir)
                shutil.copyfile(os.path.join(sourceDir, filename), os.path.join(targetDir, filename))

    def generatePosts(self):
        for key in self.posts.keys():
            post    = self.posts[key]
            postDir = os.path.join(outputDir, post.attribs['year'], post.attribs['doy'])
            page    = articlePage.render(self.cfg)

            open(os.path.join(postDir, '%s.html' % post.attribs['slug']), 'w+').write(page.encode('utf-8'))

    def generateFrontpage(self):
        keys = self.posts.keys()
        keys.sort(reverse=True)

        n = 0
        for key in keys:
            n += 1
            if n <= self.indexCount:
                self.posts[key].frontpage = True
            else:
                break

        page = indexPage.render(self.cfg)
        open(os.path.join(outputDir, 'index.html'), 'w+').write(page.encode('utf-8'))

    def generateTags(self):
        taglist = self.tags.keys()
        taglist.sort()
        self.cfg['taglist'] = taglist

        self.cfg['title'] = '%s :: Tags' % self.cfg['title']
        page = tagsPage.render(self.cfg)
        open(os.path.join(outputDir, 'tags.html'), 'w+').write(page.encode('utf-8'))

    def generateYears(self):
        yearlist = self.years.keys()
        yearlist.sort(reverse=True)
        self.cfg['yearlist'] = yearlist

        for year in yearlist:
            keys = self.cfg['yearlist'][year]
            keys.sort()
            self.cfg['years'][year] = []
            for key in keys:
                self.cfg['years'][year].append(self.posts[key])

    def generateArchives(self):
        self.cfg['title'] = '%s :: Archives' % title
        page = archivePage.render(self.cfg)
        open(os.path.join(outputDir, 'archives.html'), 'w+').write(page.encode('utf-8'))

    def generate(self):
        self.generatePosts()
        self.generateFrontpage()
        self.generateTags()
        self.generateYears()
        self.generateArchives()
        self.copyStatic()
