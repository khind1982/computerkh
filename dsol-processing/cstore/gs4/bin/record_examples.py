#!/usr/bin/env python2.7
# coding=utf-8

# A script to run on XML records that creates a report of the field names and example records where they occur

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import lxml.etree as ET

from collections import defaultdict, OrderedDict
from StringIO import StringIO

from optparse import OptionParser
from commonUtils.fileUtils import locate

parser = OptionParser()

parser.add_option("-f", "--file", dest="infile", help="File(s) to be scanned", metavar="FILE")
parser.add_option("-r", "--recorddel", dest="record", help="Field deliminating records", metavar="NOTE")
parser.add_option("-i", "--id", dest="id", help="Name of ID field", default=True)
parser.add_option("-t", "--type", dest="type", help="Type of file e.g. xml, html", default=True)


(options, args) = parser.parse_args()


fieldlist = []
fielddict = OrderedDict()
reclevfields = []

filetolocate = os.path.basename(options.infile)
rootpath = os.path.dirname(options.infile)

for f in locate(filetolocate, rootpath):

    if options.type == 'xml':
        hs = StringIO(open(f, 'r').read())
    elif options.type == 'html':
        hs = StringIO('%s%s' % ('<?xml version="1.0" encoding="iso-latin-1"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "/home/cmoore/svn/trunk/cstore/gs4/bin/xhtml1-strict.dtd">', open(f, 'r').read()))
    else:
        print "Current acceptable types:\nxml\nhtml\nPlease add a type to the script if needed"


    tree = ET.iterparse(hs, load_dtd=True, huge_tree=True)

    for _, record in tree:
        if record.tag == options.record:
            for element in record.iter():
                if element.text is None:
                    pass
                elif element.tag in fieldlist:
                    pass
                else:
                    fielddict[element.tag] = [record.find(options.id).text, element.text]
                    fieldlist.append(element.tag)

for k in fielddict:
    print k, fielddict[k]
