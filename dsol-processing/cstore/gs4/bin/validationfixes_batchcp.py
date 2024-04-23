#!/usr/bin/env python2.7

# Batch copying xml files that need correcting.

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import lxml.etree as ET
import shutil

from commonUtils.fileUtils import locate

# User specified options; input directory and output directory.


try:
    product = sys.argv[1]
    batch = sys.argv[2]
except IndexError:
    print "Usage: sampler.py [product] [batch]\n"
    exit(1)

infile = '/home/cmoore/prob-solve/bpd-feedbackreview/files.lut'

xmlstofix = list(set([i.strip() for i in open(infile).readlines()]))
xmlstocopy = list(set([f for f in locate('*.xml', root="/dc/%s-images/editorial/%s" % (product, batch)) if os.path.basename(f) in xmlstofix]))

for f in xmlstocopy:
    print f, f.replace(batch, 'fixing%s' % batch)
