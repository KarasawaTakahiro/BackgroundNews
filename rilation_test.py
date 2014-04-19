#! /usr/bin/env python
# coding: utf-8

from subprocess import Popen, PIPE

p = Popen(["./a.out"], stdout=PIPE);
c = p.communicate()[0]
print c
p.wait();
print p
