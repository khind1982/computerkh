#!/usr/local/bin/python2.6
# -*- mode: python -*-

#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

import codecs
import warnings
from commonUtils import *
import xml.dom.minidom
from tempfile import TemporaryFile

# We have known deprecations in Cheetah.
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from Cheetah.Template import Template

from abstractfilter import AbstractFilter

class OxupFilter(AbstractFilter):
    def __init__(self, obj):
        self.object = obj.gs4
        #self._template = Template(file='../lib/views/gs4xml/gs4template.tmpl', searchList = [self.object])
        self._template = Template(file='../lib/views/oup/ouptemplate.tmpl', searchList = [self.object])
        self._cfg = obj._cfg
        
    def print_record(self):
        # TODO: get pretty printing to work.
        return str(self._template)
