#!/usr/bin/env python2.7
# coding=utf-8

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

incids = []
curids = []

with open('/dc/migrations/film/fii/data/incoming/incfilmids.txt', 'r') as infile:
    for line in infile:
        incids.append(line.strip())

with open('/dc/migrations/film/fii/data/incoming/legids.txt', 'r') as infile:
    for line in infile:
        curids.append(line.strip())

incnotincur = [i for i in incids if i not in curids]
curnotinc = [c for c in curids if c not in incids]

outfile1 = '/dc/migrations/film/fii/data/incoming/missingincfromcur.txt'
outfile2 = '/dc/migrations/film/fii/data/incoming/missingcurfrominc.txt'

with open(outfile1, 'w') as out:
    out.write([i for i in incnotincur])

with open(outfile2, 'w') as out:
    out.write([i for i in curnotinc])
