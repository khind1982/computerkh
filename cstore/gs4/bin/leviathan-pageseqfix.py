#!/usr/bin/env python2.7

# Script to fix values in page sequence

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import lxml.etree as ET
import shutil

from commonUtils.fileUtils import locate


try:
    directory = sys.argv[1]
except IndexError:
    print "Usage: leviathan-pageseqfix.py [input directory]\n"
    exit(1)


for f in locate('*.xml', root=directory):
    tree = ET.parse(f, ET.XMLParser(remove_blank_text=True, resolve_entities=True))
    root = tree.getroot()

# Testing for docs with a malformed page sequence in them
    pageseqs = [seq.text for seq in root.findall('.//page_sequence') if re.match('0([0-9])', seq.text) is not None]

# Only processing docs with malformed page sequence
    if pageseqs:
        shutil.copy(f, f.replace('.xml', '.seqbak'))  # backing up the xml in case there's a problem.

        for pageseq in root.findall('.//page_sequence'):
            match = re.match('0([0-9])', pageseq.text)
            if match is not None:
                pageseq.text = match.group(1)

        with open(f, 'w') as outxml:  # This overwrites the original xml
            outxml.write(ET.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
