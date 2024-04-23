#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

from abstractstream import AbstractStream

class SqlStream(AbstractStream):
    def __init__(self):
        pass
