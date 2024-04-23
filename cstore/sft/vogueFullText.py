#!/usr/local/bin/python2.6
# -*- mode: python -*-

"""Create a tree of objects: document contains pages which contain zones which contain words.
Each is aware of the chunk of XML it and its children need.
"""

import amara
from Cheetah.Template import *
import sys
import codecs

def readVogue(inputfile):
    docxml = amara.parse(inputfile, prefixes={'x': 'http://www.w3.org/1999/xhtml'})
    doc = document(docxml)
    doc.populate()
    return doc

class node:

    def __init__(self, xmlfragment):
        self.children = []
        self.xmlfragment = xmlfragment
        
    def populate(self):
        for element in self.xmlfragment.xml_xpath(self.childxpath):
            child = self.childtype(element) 
            if hasattr(child, 'populate'):
                child.populate()
            self.children.append(child) 

class document(node):

    def __init__(self, xmlfragment):
        node.__init__(self, xmlfragment)
        self.childxpath = 'pam:message/pam:article/x:ocr_content/pq:content/pq:page'
        self.childtype = page
        #I want the children list given a more specific name to make the output template
        #more readable - is there a better way to do this?
        self.pages = self.children

class page(node):

    def __init__(self, xmlfragment):
        node.__init__(self, xmlfragment)
        self.childxpath = 'pq:zone'
        self.childtype = zone
        self.zones = self.children
        
class zone(node):

    def __init__(self, xmlfragment):
        node.__init__(self, xmlfragment)
        self.childxpath = 'pq:zoneWord'
        self.childtype = word
        self.words = self.children
        
class word(node):

    def __init__(self, xmlfragment):
        node.__init__(self, xmlfragment)
        
    def populate(self):
        self.text = self.xmlfragment.wordPos.word.xml_child_text
        self.ulx = self.xmlfragment.wordPos.ulx
        self.uly = self.xmlfragment.wordPos.uly
        self.lrx = self.xmlfragment.wordPos.lrx
        self.lry = self.xmlfragment.wordPos.lry
        
voguetemplate = """
#for $page in $doc.pages
#for $zone in $page.zones
#for $word in $zone.words
$word.text:$word.ulx:$word.uly:$word.lrx:$word.lry
#end for
#end for
#end for
"""

def outputVogue(doc):

    t = Template(voguetemplate)
    t.doc = doc
    return t.respond()


if __name__ == '__main__':

    for fi in sys.argv[1:]:
        doc = readVogue(fi)
        newdoc = outputVogue(doc)
        newfi = codecs.open(fi[:-4] + '_vogueformat' + fi[-4:], 'w', 'utf8')
        newfi.write(newdoc)
        newfi.close()