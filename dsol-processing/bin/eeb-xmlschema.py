#!/usr/bin/env python2.7

# Script to parse eeb handover records without changing them

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'libdata/eeb'))

import lxml.etree as ET

from StringIO import StringIO

from commonUtils.fileUtils import locate
from leviathanUtils import eeboutorder

try:
    inschema = sys.argv[1]
    indir = sys.argv[2]

except IndexError:
    print "Usage: eeb-xmlschema.py [input schema] [input directory]\n"
    exit(1)

xmlschema = ET.XMLSchema(file=inschema)
parser = ET.XMLParser(schema=xmlschema, remove_blank_text=True)

val = []

for f in locate('*.xml', indir):
    #print "Checking file %s" % f
    # print f

    # try:
    #     root = ET.parse(f).getroot()
    #     ordroot = ET.ElementTree(eeboutorder(root))
    #     xmlschema.validate(ordroot)
    # except Exception as exc:
    #     print exc
    #     print xmlschema.error_log
    try:
        root = ET.parse(f).getroot()
        ordroot = ET.ElementTree(eeboutorder(root))

        xmlschema.validate(ordroot)
        log = xmlschema.error_log
    except ET.XMLSyntaxError as e:
        print '%s: %s' % (f, e)
        pass
try:
    print log
except:
    pass