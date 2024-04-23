#! /usr/bin/env python
# -*- mode: python -*-
# pylint:disable=F0401

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../lib')))

if len(sys.argv) < 2:
    print >> sys.stderr, "Usage: %s file.gen ..." % os.path.basename(__file__)
    exit(1)

from streams.genfilestream import GenFileStream
from genrecord import GenRecord

for f in sys.argv[1:]:
    data_root, filename = os.path.split(f)
    for record in GenFileStream({'stream': filename, 'streamOpts': 'dataRoot=%s' % data_root}).streamdata():
        gen = GenRecord(record.data)
        try:
            docid = gen.f_035('a')
            pagecount = gen.f_900('a')
        except KeyError:
            continue
        print "%s\t%s" % (docid, pagecount)
