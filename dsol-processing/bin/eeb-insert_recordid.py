#!/usr/bin/env python2.7

# Script to parse eeb handover records without changing them

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'libdata/eeb'))

import lxml.etree as ET
import shutil

from StringIO import StringIO

from commonUtils.fileUtils import locate
from leviathanUtils import eeboutorder

parser = ET.XMLParser(remove_blank_text=True)

try:
    indir = sys.argv[1]
except IndexError:
    print "Usage: eeb-insert_recordid.py [inputfile] [input directory]\n"
    exit(1)

val = []

for f in locate('*.xml', indir):
    root = ET.parse(f, parser).getroot()
    if root.find('.//{http://www.loc.gov/mods/v3}recordInfo') is None:
        shutil.copyfile(f, f.replace('.xml', '.bak'))
        for ele in root.findall('.//{http://www.loc.gov/mods/v3}identifier'):
            # print ele
            if ele.get('type') == 'coteoriginal':
                contsource = ele.text

        recInf = ET.Element(ET.QName('http://www.loc.gov/mods/v3', 'recordInfo'), nsmap={'mods':'http://www.loc.gov/mods/v3'})
        ET.SubElement(recInf, ET.QName('http://www.loc.gov/mods/v3', 'recordIdentifier'), nsmap={'mods':'http://www.loc.gov/mods/v3'}).text = os.path.basename(f).replace('.xml', '')
        ET.SubElement(recInf, ET.QName('http://www.loc.gov/mods/v3', 'recordContentSource'), nsmap={'mods':'http://www.loc.gov/mods/v3'}).text = contsource
        root.find('.//{http://www.loc.gov/mods/v3}mods').insert(0, recInf)
    

    with open(f, 'w') as out:
        out.write(ET.tostring(root, pretty_print=True))
        