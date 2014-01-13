hakkan
======

発刊 hakkan - to publish

Hakkan is going to be a loose collection of tools that will allow me to keep a generated static site but have the infrastructure around it to make it behave like it was dynamic site.

Goals
=====
The project is going to answer the question - how can you get a static site
to behave and feel like it's one of those single-page-apps that are all
web-ish without losing the focus: it's all staticly served!

Keep to a minimum those items that have to run as a daemon or web app. I know
that I cannot completely remove them - after all there has to be something on
the receiving end of a HTML delivered web mention. Well, I could make it a
python CGI app!

In reality it will mostly be two items: one a daemon to handle file events and
a Python Flask web app for web hooks and other HTML triggered events.

Roadmap
=======

Working
-------
* none! well, not really but none that are in this repo.

Planned
-------
* daemon to monitor content directory for changes
** trigger site generate for changes to markdown files
** send webmention when content file changes
* webhook for incoming webmentions
* tool to allow POST of markdown file for new
** articles
** notes
** events
* POSSE tools

Requires
========
Python v2.6+ but see requirements.txt for a full list

For testing I use:
    [nosetests](https://pypi.python.org/pypi/nose/) to run/manage tests
    [httmock](https://pypi.python.org/pypi/httmock/) to stub the web calls

Web facing daemons require [Flask](http://flask.pocoo.org/docs/)
