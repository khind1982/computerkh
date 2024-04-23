#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Script to output log and titlelists

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'libdata/eeb'))
sys.path.append('/packages/dsol/opt/lib/python2.7/site-packages')

import lxml.etree as ET
import xlrd

from StringIO import StringIO
from commonUtils.fileUtils import locate, buildLut
from HTMLParser import HTMLParser

h = HTMLParser()

infile = open('/dc/eurobo/editorial/workbook_fixing/log_to_fix.txt', 'r').readlines()
outfile = '/dc/eurobo/editorial/workbook_fixing/fixed_log.txt'


with open(outfile, 'w') as out:
    for i in infile:
        # print i.decode('latin-1')
        out.write(h.unescape(i.decode('latin-1')).encode('utf-8'))
        
        
