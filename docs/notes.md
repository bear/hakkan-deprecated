Notes
=====

Ideas an doodles about how things will interact

file change daemon
==================
* monitor content source directory for change events
* monitor "inbound" directory for new items - this allows the web facing side to not have any knowledge of how to generate the site
* ???

web app
=======
* Python Flask based
* url map
** /webmention - receive incoming webmention requests
** /event - receive inbound events for new items, updates, whatever - json payload driven?
** /subscribe - ?? webhook to allow pubsub events?

directory layout

'''
/hakkan
    hakkan.cfg
    Makefile
    /static
        robots.txt
        humans.txt
        /css
        /images
    /templates
    /content
        index.md
        /articles
            index.md
            index.html
            tags.md
            tags.html
            /YYYY
                /DDD
                    article-slug.md
                    article-slug.refs
                    article-slug.html
'''