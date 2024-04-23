#!/usr/bin/env python

# Open each file that matches the specified suffix (or 'xml' if none
# given), parse it as XML, copy the original out of the way with a suffix
# of .bak, and print out the XML again to the original file name, using
# the pretty print feature.

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import shutil

import lxml.etree as ET
from commonUtils.fileUtils import locate  #pylint:disable=F0401

try:
    if sys.argv[1] == '-s':
        suffix = '*.%s' % sys.argv[2]
        target_directory = sys.argv[3]
    else:
        suffix = '*.xml'
        target_directory = sys.argv[1]
except IndexError:
    print >> sys.stderr, "%s: Usage:" % os.path.basename(__file__)
    print >> sys.stderr, "%s [-s <suffix>] <directory>" % os.path.basename(__file__)
    exit(1)

for filename in locate(suffix, root=target_directory):
    try:
        xml = ET.parse(filename, ET.XMLParser(remove_blank_text=True))
    except:
        try:
            xml = ET.parse(filename, ET.HTMLParser(remove_blank_text=True))
        except Exception as e:  #pylint:disable=W0703
            print >> sys.stderr, "Invalid XML in %s" % filename
            print >> sys.stderr, e
            continue

    bakfile = os.path.join(os.path.dirname(filename), "%s.bak" % os.path.basename(filename))

    shutil.copy(filename, bakfile)
    with open(filename, 'w') as outf:
        outf.write(ET.tostring(xml, pretty_print=True).replace('\r\n', '\n'))
        # xml.write(outf, pretty_print=True)
