#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Script to check handover data for various things

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

libraries = buildLut('/dc/eurobo/utils/libraries.lut')
countries = buildLut('/dc/eurobo/utils/country_codes_notags.lut')
languages = buildLut('/dc/eurobo/utils/langs_notags.lut')
collections = buildLut('/dc/eurobo/utils/collection_allrecs.lut')

try:
    indir = sys.argv[1]
    outfile = sys.argv[2]
except IndexError:
    print "Usage: eeb-data_audit_handover.py [input directory] [output file]\n"
    exit(1)

def presenceTestSingle(element):
    if element is not None and element.text is not None:
        return element.text
    else:
        return ''


def modsdata(datafile):
    root = ET.parse(datafile).getroot()
    dmdrec = root.find('.//{*}dmdSec')
    
 
def handoverdata(datafile):
    errorlog = []
    linkslog = []
    root = ET.parse(datafile).getroot()
    pages = root.find('.//itemimagefiles')

    # comparing illustration and pagecontent fields
    listofillus = list(set([i.text for i in root.findall('.//illustration') if i.text is not None]))
    listofpcontent = list(set([i.text for i in pages.findall('.//pagecontent') if i.text is not None]))
    
    nomatchesill = [i for i in listofillus if i not in listofpcontent]
    nomatchespc = [i for i in listofpcontent if i not in listofillus]

    if len(nomatchesill) != 0:
        for i in nomatchesill:
            errorlog.append('DATA ERROR: illustration: %s does not have a corresponding pagecontent field (%s)\n' % (i, datafile))

    if len(nomatchespc) != 0:
        for i in nomatchespc:
            errorlog.append('DATA ERROR: pagecontent: %s does not have a corresponding illustration field (%s)\n' % (i, datafile))

    # check for missing boundwiths.
    # allfiles = [os.path.basename(i) for i in list(allfiles)]
    
    filepath = os.path.dirname(datafile)
    
    linkids = [i.text for i in root.findall('.//linkid')]
    if len(linkids) > 0:
        for linkid in linkids:
            if not os.path.isfile('%s/%s.xml' % (filepath, linkid)):
                errorlog.append('DATA ERROR: Link %s in %s does not have a matching file in directory' % (linkid, datafile))
    

    return errorlog

# def linkcheck(files):
    

def processing(f):
    # detecting input type:
    if ET.parse(f).getroot().tag != 'rec':
        log = modsdata(f)
    else:
        log = handoverdata(f)
    return log

allerrs = []
alllinks = []

listoffiles = locate('*.xml', indir)
listofbooks = [os.path.basename(i[0:-8]) for i in list(listoffiles)]


for fl in locate('*.xml', indir):
    # print fl
    errors = processing(fl)
    if len(errors) > 0:
        for i in errors:
            allerrs.append(i)

with open(outfile, 'w') as out:
    for i in allerrs:
        out.write(i)
