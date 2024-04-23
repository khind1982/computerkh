#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

import codecs
from abstractfilter import AbstractFilter

class VogueFilter(AbstractFilter):
    def __init__(self, obj):
        self.object = obj.gs4
        #self._template = Template(file='../lib/views/gs4xml/gs4template.tmpl', searchList = [self.object])
        self._cfg = obj._cfg

    def print_record(self):
#        print >> sys.stderr, ("DEBUG: VogueFilter.print_record() : %s" % self.object)
#        return str(self.object)
        print self.object.fields()
 #       for item in self.object.fields():
 #           try:
 #               setattr(self.object, item, codecs.encode(getattr(self.object, item), 'utf8'))
 #           except TypeError:
 #               pass

        for item in self.object.fields():
            print "DEBUG: field: %s, type: %s" % (item, type(getattr(self.object, item)))
        #print codecs.decode(str(self.object), 'utf8', 'xmlcharrefreplace')
        print self.object.title
        return str(self.object.fields())  #codecs.encode(str(self.object), 'utf8', 'xmlcharrefreplace')
