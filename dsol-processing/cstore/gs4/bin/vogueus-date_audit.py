#!/usr/bin/env python2.7

# Script to validate incoming Vogue US data

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import fileinput
import lxml.etree as ET

from commonUtils.fileUtils import locate
from datetool.dateparser import parser as dateparser
from datetool.dateparser import ParserError

# User specified options; input directory and output file.

try:
    directory = sys.argv[1]
    outfile = sys.argv[2]
except IndexError:
    print "Usage: ./vogueus-data_audit.py {target directory} {output file}\nPlease specify a delivery batch directory and an output file (including full path) for the error log"
    exit(1)

prefixes = {'pam': 'http://prismstandard.org/namespaces/pam/2.0/', 'dc': 'http://purl.org/dc/elements/1.1/', 'prism': 'http://prismstandard.org/namespaces/basic/2.0/', 'ocr': 'http://www.innodata.com/', 'pq': 'http://www.proquest.co.uk'}

# Creating a list of all the images.

imglst = [os.path.basename(n) for n in locate('*', root=directory) if n.endswith('.jpg')]
thrdlst = []

# Parsing the XML and creating a list of threads

for nfile in locate('*.xml', root=directory):

    tree = ET.parse(nfile, ET.XMLParser(remove_blank_text=True, resolve_entities=True))
    root = tree.getroot()

    thrdlst.append([page.get('{%s}src' % prefixes['pq']) for page in root.findall(".//{%s}page" % prefixes['pq'])])

thrdlst = ['%s.jpg' % l for i in thrdlst for l in i]

for thread in thrdlst:
    if thread not in imglst:
        print thread

for image in imglst:
    if image not in thrdlst:
        print image
