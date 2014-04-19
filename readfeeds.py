#! /usr/bin/env python
# coding: utf-8

import HTMLParser, feedparser
import datetime

url = "https://news.google.com/news/feeds?ned=us&ie=UTF-8&oe=UTF-8&q&output=rss&num=30&hl=ja"

class MyParser(HTMLParser.HTMLParser):
    def handle_data(self, data):
        print data

feed = feedparser.parse(url)

myparser = MyParser()
for n in xrange(len(feed.entries)):
    myparser.feed(feed.entries[n].description)
    print
