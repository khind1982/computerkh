#!/usr/bin/env python

# Inspect an AAA XML file, looking for "image" zones that should be
# "caption" zones.

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import shutil

import lxml.etree as ET

from commonUtils.fileUtils import locate  #pylint:disable=F0401

try:
    target_directory = sys.argv[1]
except IndexError:
    print >> sys.stderr, "No directory given"
    exit(1)

for filename in locate('*.xml', root=target_directory):
    xml = ET.parse(filename, ET.XMLParser(remove_blank_text=True))

    print os.path.basename(filename)
    # move each file out of the way, in case something goes wrong.
    bakfile = os.path.join(os.path.dirname(filename), "%s.bak" % os.path.basename(filename))

    # get each zone assigned the type "image"
    for zone in xml.findall('.//APS_zone[@type="image"]'):
        try:
            # If the zone contains an APS_zone_imagetype element, it's
            # fine and needs nothing to be done to it.
            zone.find('.//APS_zone_imagetype').text
        except AttributeError:
            # However, if we get here, there is no APS_zone_imagetype element
            # in the zone, and so it needs to have its type set to "caption"
            zone.attrib['type'] = "caption"

    shutil.copy(filename, bakfile)
    with open(filename, 'w') as outf:
        xml.write(outf, pretty_print=True)
