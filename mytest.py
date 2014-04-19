#! /usr/bin/env python
# coding: utf-8

import random
import time

def foo():
    j = 0
    for i in xrange(3):
        for k in xrange(1,11):
            time.sleep(random.randint(1,5))
            yield j
            j += 1

gen = foo()
for i in xrange(10):
    print gen.next()
    print "oooo"
