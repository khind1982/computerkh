#!/usr/bin/env python2.7

# App to convert delivered DNSA chronologies to Lev-DNSA format

import os
import sys
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import lxml.etree as ET

from commonUtils.fileUtils import locate, buildLut
from optparse import OptionParser

parser = OptionParser()

(options, args) = parser.parse_args()

chronrec = []
textlist = []

shortcollections = buildLut('dnsa_shortcols.lut')
longcollections = buildLut('dnsa_longcols.lut')

try:
    orifile = args[0]
except IndexError:
    print "Please specify a directory containing file(s) to convert"
    parser.print_help()
    exit(1)

for nfile in locate('*_chron.txt', orifile):
    path = '%s/chronology/' % (os.path.dirname(nfile))
    if not os.path.exists(path):
        os.makedirs(path)
    with open(nfile, 'r') as file2convert:
        chronrec.append('<?xml version="1.0" encoding="iso-latin-1"?>\n<document>\n<record>\n<rec_format formattype="Chronology">\n')
        textlist.append('\n</rec_format></record>\n<bodytext>\n')
        for line in file2convert:
            try:
                tagvalue = re.split('^[A-Z][A-Z]  ', line)[1].translate(None, '\n')
            except IndexError:
                pass
            if line.startswith('OC  '):
                outfilename = '%sT%s00001.xml' % (path, tagvalue)
                chronrec.append(('<collection_code>%s</collection_code>\n<docid>T%s00001</docid>\n<title>Chronology: %s</title>\n<collection_names>\n<long>%s</long>\n<short>%s</short>\n</collection_names>\n<object_dates>\n<object_numdate>0001-01-01</object_numdate>\n<object_rawdate>Jan 1, 1</object_rawdate>\n</object_dates>\n') % (tagvalue, tagvalue, longcollections[tagvalue], longcollections[tagvalue], shortcollections[tagvalue]))
            if line.startswith('DA  '):
                textlist.append(('<p><b>%s:</b></p>\n') % tagvalue)
            if line.startswith('TX  '):
                textlist.append(('<p>%s</p>\n') % tagvalue)
        textlist.append('</bodytext>\n')
        for item in textlist:
            chronrec.append(item)
        textlist = []
        chronrec.append('</document>\n')

        with open(outfilename, 'w') as out:
            for item in chronrec:
                out.write(item)
        chronrec = []

tree = ET.parse(outfilename, ET.XMLParser(remove_blank_text=True, resolve_entities=True))
