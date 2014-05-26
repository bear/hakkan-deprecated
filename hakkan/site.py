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
import markdown2

import pprint
pp = pprint.PrettyPrinter(indent=2)

configPaths    = (os.getcwd(), '~/', '~/.hakkan/')
configName     = 'hakkan.cfg'
markdownExtras = ['fenced-code-blocks', 'smarty-pants', 'cuddled-lists']
markdowner     = markdown2.Markdown(extras=markdownExtras)


class Post(object):
    """A single post.

    Created by pointing to a filename that is contains the markdown+ content.

    markdown+ in my use is a block of key:value metadata, a blank line and the
    markdown formated content.
    """
    def __init__(self, postFilename, baseurl):
        self.filename = normalizeFilename(postFilename)
        self.baseurl  = baseurl
        self.lines    = None
        self.content  = None
        self.header   = None
        self.metadata = None
        self.attribs  = None
        self.key      = None

        self.clear()
        self.load()

    def clear(self):
        self.lines    = None
        self.content  = None
        self.header   = None
        self.metadata = None
        self.attribs  = { 'baseurl': self.baseurl }

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
                    self.header.append(item)

                    key, value = item.split(':', 1)
                    key        = key.lower()
                    value      = value.strip()

                    if tag == 'date':
                        self.attribs[tag] = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    else:
                        self.attribs[tag] = value
                else:
                    self.lines.append(item)

            self.attribs['modified'] = os.path.getmtime(self.filename)
            self.attribs['created']  = os.path.getctime(fullname)
            self.attribs['index']    = self.attribs['date'].strftime('%Y%m%d%H%M%S')
            self.attribs['year']     = self.attribs['date'].strftime('%Y')
            self.attribs['doy']      = self.attribs['date'].strftime('%j')
            self.attribs['baseurl']  = self.baseurl
            self.attribs['url']      = '%(baseurl)s%(year)s/%(doy)s/%(slug)s' % self.attribs
            self.content             = ''.join(self.content)
            self.html                = markdowner.convert(self.content)
            self.key                 = '%(index)s.%(slug)s' % self.attribs 


class Site(object):
    """A Site.

    The Site contains the configuration items required to manage templates,
    gather Posts and then generate the required output for the site.

    configuration example:
        { "templates":  "./templates/",
          "static":     "./static",
          "output_dir": "./output",
          "bearlog": { "base_page":    "blog_index.jinja",
             "article_page": "article_index.jinja",
             "archive_page": "archives.jinja",
             "tags_page":    "tags.jinja",
             "input_dir":    "./content",
             "baseurl":      "/bearlog/",
             "title":        "Bear's Log",
             "meta": { "description": "the babbling of a coder and cat herder",
                       "author":      "bear",
                       "keywords":    "bear,English,USA,Philadelphia,Pennsylvania",
                       "microid":     "96ec0c3042a89ca171dc0c6b637047002f632937",
                       "verify-v1":   "prNbHLYias+09NpzFxMTzokcDp9uGo0dcIE4Un9hUtM="
                     }
           }
        }
    """
    def __init__(self, cfgFilename, sitekey):
        self.cfgFilename = normalizeFilename(cfgFilename)
        self.cfg         = loadConfig(self.cfgFilename)
        self.sitekey     = sitekey
        self.templateEnv = None
        self.posts       = {}
        self.postFiles   = {}
        self.tags        = {}
        self.years       = {}

        self.loadTemplates()
        self.findPosts()

    def loadTemplates(self):
        self.templateLoader = jinja2.FileSystemLoader(searchpath=cfg['templates'])
        self.templateEnv    = jinja2.Environment(loader=self.templateLoader)

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
        for path, dirlist, filelist in os.walk(self.cfg['posts_dir']):
            if len(filelist) == 1 and filelist[0][-3:] == '.md':
                findByFilename(os.path.join(path, filelist[0]))

    def copyStatic(self, staticDir, outputDir):
        targetBase = os.path.abspath(outputDir)

        for path, dirlist, filelist in os.walk(baseDir):
            sourceDir = os.path.abspath(path)
            targetDir = '%s/%s' % (targetBase, path.replace(baseDir, ''))

            for filename in filelist:
                if not os.path.exists(targetDir):
                    mkpath(targetDir)
                shutil.copyfile(os.path.join(sourceDir, filename), os.path.join(targetDir, filename))

    def generate(self):
        config      = self.cfg[self.sitekey]
        title       = config['title']
        outputDir   = self.cfg['output_dir']
        indexPage   = self.templateEnv.get_template(config['base_page'])
        articlePage = self.templateEnv.get_template(config['article_page'])
        archivePage = self.templateEnv.get_template(config['archive_page'])
        tagsPage    = self.templateEnv.get_template(config['tags_page'])
        frontpage   = []

        if not os.path.exists(outputDir):
            mkpath(outputDir)

        keys = self.posts.keys()
        keys.sort(reverse=True)

        n = 0
        for key in keys:
            post = self.posts[key]
            if n < 6:
                frontpage.append(key)
            n += 1

            postDir = os.path.join(outputDir, post.attribs['year'], post.attribs['doy'])
            if not os.path.exists(postDir):
                mkpath(postDir)

            page = articlePage.render(config)
            open(os.path.join(postDir, '%s.html' % post.attribs['slug']), 'w+').write(page.encode('utf-8'))

        taglist = self.tags.keys()
        taglist.sort()
        config['taglist'] = taglist

        yearlist = self.years.keys()
        yearlist.sort(reverse=True)
        config['yearlist'] = yearlist

        for year in yearlist:
            keys = config['yearlist'][year]
            keys.sort()
            config['years'][year] = []
            for key in keys:
                config['years'][year].append(self.posts[key])

        self.copyStatic(self.cfg['static'], self.cfg['output_dir'])

        page = indexPage.render(config)
        open(os.path.join(outputDir, 'index.html'), 'w+').write(page.encode('utf-8'))

        config['title'] = '%s :: Archives' % title
        page = archivePage.render(config)
        open(os.path.join(outputDir, 'archives.html'), 'w+').write(page.encode('utf-8'))

        config['title'] = '%s :: Tags' % title
        page = tagsPage.render(config)
        open(os.path.join(outputDir, 'tags.html'), 'w+').write(page.encode('utf-8'))
