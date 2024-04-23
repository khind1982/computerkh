#!/usr/bin/env python2.7

# Script to restructure eeb data in directories

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.append('/packages/dsol/lib/python2.6/site-packages')

import lxml.etree as ET
import shutil

from collections import OrderedDict

from commonUtils.fileUtils import locate
from leviathanUtils import eeboutorder

parser = ET.XMLParser(remove_blank_text=True)

try:
    indir = sys.argv[1]
    outdir = sys.argv[2]
except IndexError:
    print 'Usage: eeb-restructure.py [input directory] [output dir]\n'
    exit()


for f in locate('*.xml', indir):
    root = ET.parse(f, parser).getroot()

    coll = root.find('.//unit').text
    libfolder = root.find('.//pqid').text[4:7]

    outpath = '%s/%s/%s' % (outdir, coll, libfolder)

    if not os.path.exists(outpath):
        os.makedirs(outpath)

    try:
        shutil.move(f, os.path.abspath(outpath))
    except shutil.Error:
        pass
