#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Script to output mods files from a spreadsheet

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'libdata/eeb'))
sys.path.append('/packages/dsol/opt/lib/python2.7/site-packages')

import lxml.etree as ET
import xlrd

from StringIO import StringIO
from huTools import structured
from excelUtils import ssrecords

try:
    infile = sys.argv[1]
    outdir = sys.argv[2]
except IndexError:
    print "Usage: eeb-excel_to_mods.py [inputfile] [output directory]\n"
    exit(1)

sheet = xlrd.open_workbook(infile).sheet_by_index(0)

for rownum in range(1, sheet.nrows):
    rowdict = {}
    for col, cell in enumerate(sheet.row(rownum)):
        tag = sheet.cell_value(0, col).encode('latin-1')
        text = sheet.cell_value(rownum, col)
        if type(text) is float:
            text = str(int(text))
        if text is not '':
            rowdict[tag] = text
    if 'PublicationDateEnd' in rowdict.keys():
        rowdict['dateIssued'] = '%s-%s' %s (rowdict['PublicationDateStart'], rowdict['PublicationDateEnd'])
        

    d = structured.dict2xml(rowdict, roottag='mod', pretty=True)
    xml_data = ET.fromstring(d)

    print ET.tostring(xml_data)

    mods_format = ET.XSLT(ET.parse('/dc/eurobo/utils/mods-eeb-scanlist.xsl'))
    
    out_rec = mods_format(xml_data)
    print ET.tostring(out_rec, pretty_print=True)
