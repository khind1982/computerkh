#!/usr/bin/env python2.6
# -*- mode: python -*-

# Extract PAO PDF page counts from the PAO data, and build a lookup
# table for use in the IMPA transformation.

import sys, os #, re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../lib')))

from streams.genfilestream import GenFileStream

data_root = '/dc/pcinext'

try:
    data_root = sys.argv[1]
except IndexError:
    pass

pao_ids = [line.strip() for line in open('/home/dbye/impa_paoarticles.txt').readlines() if not line.startswith('http')]

target_jids = ['1021', '1076', '1166', '3179', 'b085', 'c432', 
               'e154', 'e280', 'e401', 'h150', 'h433', 'j429', 
               'j590', 'm148', 'p209', 's536', 'v602']

for journal in target_jids:
    print >> sys.stderr, "%s..." % journal
    for record in GenFileStream(
            {'stream': '%s.gen' % journal,
             'streamOpts': 'dataRoot=%s' % data_root}
             ).streamdata():
        aid = record.data['035'][2:]
        if aid in pao_ids:
            if '900' in record.data.keys():
                print "%s %s" % (aid, record.data['900'][2:])
            else:
                print >> sys.stderr, "%s has no pagecount." % aid
