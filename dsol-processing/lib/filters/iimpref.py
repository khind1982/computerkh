#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

import warnings

# We have known deprecations in Cheetah.
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from Cheetah.Template import Template

from abstractfilter import AbstractFilter
from gs4xml import GS4Xml

class IIMPRef(GS4Xml):
    def __init__(self, obj):
        GS4Xml.__init__(self, obj)
        self._template = Template(file='../lib/views/iimpref/iimpreftemplate.tmpl', searchList = [self.object])

