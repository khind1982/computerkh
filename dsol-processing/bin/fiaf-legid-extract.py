#!/usr/bin/env python2.7
# coding=utf-8

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import lxml.etree as ET

from StringIO import StringIO

from commonUtils.fileUtils import locate, buildLut, buildListLut
from filmtransformfunc import levxml
from datetool.dateparser import parser as dateparser
from datetool.dateparser import ParserError

idlookup = []

try:
    infile = sys.argv[1]
    path = os.path.dirname(infile)
    indoc = os.path.basename(infile)
except IndexError:
    print "Usage is {script} {in file}\nPlease specify an input file"

for f in locate(indoc, path):
    hs = StringIO('%s%s' % ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "/home/cmoore/svn/trunk/cstore/gs4/bin/xhtml1-strict.dtd">', open(f, 'r').read()))
    tree = ET.iterparse(hs, load_dtd=True)

    for _, element in tree:
        print element
    #     if element.tag == "record":
    #         if element.find('Film_ID').text != None:
    #             filmid = '%s' % (element.find('Film_ID').text)
    #             idlookup.append('%s|%s' % (filmid, element.find('id').text.replace('/', '-')))
    #         else:
    #             print 'Missing Film_ID:', ET.tostring(element, pretty_print=True)

    # with open('/home/cmoore/svn/trunk/cstore/gs4/libdata/fiaf-ids-latest.lut', 'w') as out:
    #     for item in idlookup:
    #         out.write('%s\n' % item)

    # hs.close()
    # exit()
