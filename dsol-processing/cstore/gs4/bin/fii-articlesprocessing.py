#!/usr/bin/env python2.7
# coding=utf-8

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import lxml.etree as ET

try:
    infile = sys.argv[1]
    recID = sys.argv[2]
except IndexError:
    print "Usage: %s {recordID}\nPlease enter a valid record ID to view}" % __file__
    exit()

tree = ET.iterparse(infile, tag="record", huge_tree=True)

for _, record in tree:
    if record.find('.//priref').text == recID:
        print ET.tostring(record, pretty_print=True)
