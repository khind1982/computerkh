#!/usr/bin/env python2.7
# coding=utf-8

import os
import re
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import lxml.etree as ET

from datetime import datetime
from lxml.builder import E

from commonUtils.fileUtils import locate
from datetool.dateparser import parser as dateparser
from datetool.dateparser import ParserError

try:
    indir = sys.argv[1]
except:
    print "Usage: %s {indirectory}" % __file__

from optparse import OptionParser

parser = OptionParser()

parser.add_option("-r", "--recid", dest="recid", help="Target record", metavar="RECORD")

(options, args) = parser.parse_args()

fiiids = [line.rstrip('\n') for line in open('/home/cmoore/svn/trunk/cstore/gs4/libdata/fii-ids.lut')]

for f in locate('*.xml', indir):
    tree = ET.iterparse(f, huge_tree=True)
    # for _, record in tree:
    #     if options.recid:
    #         docids = record.findall('utb/utb.content')
    #         sifts = [sift.text for sift in record.findall('utb/utb.fieldname')]
    #         if 'SIFT ID' not in sifts:
    #             rid = record.find('.//priref').text
    #         else:
    #             for docid in docids:
    #                 if docid.find('./../utb.fieldname').text == 'SIFT ID':
    #                     if docid.text.zfill(8) in fiiids:
    #                         rid = docid.text.zfill(8)
    #                     elif docid.text in fiiids:
    #                         rid = docid.text
    #         if options.recid == rid:
    #             print ET.tostring(record, pretty_print=True)

    # Output a pretty print version of the input file
    outfile = '/dc/fii/data/validation/tocheck_%s' % os.path.basename(f)

    with open(outfile, 'w') as out:
        for _, record in tree:
            if record.tag == 'cast' or record.tag == 'credits':
                out.write(ET.tostring(record, pretty_print=True))
