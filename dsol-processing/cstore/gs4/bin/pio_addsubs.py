#!/usr/bin/env python2.7

# Script to insert subjects into PIO records.

import os
import sys
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
import codecs

from collections import defaultdict, OrderedDict
from StringIO import StringIO


from commonUtils.fileUtils import stream_as_records, locate, buildLut
from commonUtils.textUtils import fix_named_ents
from genrecord import GenRecord
from streams.genfilestream import GenFileStream
from streams.filestream import FileStream
from streams.abstractstream import AbstractStream

from extensions.itertoolsextensions import grouped

try:
    directory = sys.argv[1]
    lut = sys.argv[2]
except IndexError:
    print 'Usage: %s [input directory] [lookup]\n' % __file__
    exit()

# Creating a dictionary from the lookup table
subdict = {}

for line in codecs.open(lut, 'r', 'latin-1'):
    subdict[line.split('\t')[0].replace('pio-', '')] = fix_named_ents(line).split('\t')[1:]

# Inserting the values from the lookup
def addsubs(data):
    sixhun = []
    newrec = []
    for k in subdict.keys():
        if k == data['035'][0].replace('$a', '').strip():
            suba1 = ' 10$a%s\n' % (subdict[k][0])
            # try:
            #     suba1 = ' 10$a%s$d1%s\n' % (subdict[k][0].split(', 1')[0], subdict[k][0].split(', 1')[1])
            # except IndexError:
            #     try:
            #         suba1 = ' 10$a%s$dca. 1%s\n' % (subdict[k][0].split(', ca. 1')[0], subdict[k][0].split(', ca. 1')[1])
            #     except IndexError:
            #         suba1 = ' 10$a%s\n' % (subdict[k][0])
            if subdict[k][1]  not in ('', '\n'):
                # suba2 = ' 10$a%s$d1%s\n' % (subdict[k][1].split(', 1')[0], subdict[k][1].split(', 1')[1])
                suba2 = ' 10$a%s\n' % subdict[k][1]
            if subdict[k][2] not in ('', '\n'):
                subw = ' 00$t%s' % subdict[k][2]
            # elif subdict[k][2] != '\n':
            #     pass
            # else:
            #     subw = ' 00$t%s' % subdict[k][2]

            sixhun.append(suba1)
            try:
                sixhun.append(suba2)
            except UnboundLocalError:
                pass
            try:
                sixhun.append(subw)
            except UnboundLocalError:
                pass
    if sixhun:
        data['600'] = sixhun

    for k in data:
        for v in data[k]:
            newrec.append('%s%s' % (k, v))
    return sorted(newrec)


# Streaming the records one at a time
for f in locate('*.gen', root=directory):
    print 'Working with %s...' % f
    newrecs = []
    newfile = '%s' % f.replace('.gen', '.fix')

    fs = StringIO(codecs.open(f, 'r', 'latin-1').read())
    fo = codecs.open(f, 'r', 'latin-1').read()

    recdelimit = re.search('(^001)', fo)

    for r in grouped(stream_as_records(fs, recdelimit.group(1)), 2):
        record = defaultdict(list)

        record['001'] = [r[0][1][0][3:]]
        for i in r[1][1]:
            key = i[0:3]
            val = i[3:]
            record[key].append(val)

        newrec = addsubs(record)
        newrecs.append(''.join(newrec))

    with open(newfile, 'w') as out:
        print 'Writing output to %s...' % newfile
        for i in newrecs:
            out.write(i.encode('latin-1'))
