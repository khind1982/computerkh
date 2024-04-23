#!/usr/bin/env python2.7
# coding=utf-8

# Script to log incoming batches of EEB content, creating a tab delimited log file at book level, counting pages and records

import os
import sys
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../lib'))

from optparse import OptionParser

# Importing locate function from the commonUtils.fileUtils module located in /packages/dsol/platform/lib

from commonUtils.fileUtils import locate
from collections import defaultdict

imglist = []
imlst2 = []
loclist = []
reclst = []

d1 = defaultdict(list)
d2 = defaultdict(list)

parser = OptionParser()

parser.add_option("-d", "--dir", dest="directory", help="Target directory for files", metavar="DIR")
parser.add_option("-b", "--batch", dest="batch", help="Type of image", metavar="DIR")
parser.add_option("-o", "--output", dest="output", help="Output directory", metavar="DIR")

(options, args) = parser.parse_args()

# Setting the name of the output file

batchlog = options.output + '.log'

# Finding the files in the user specified directory and pulling out the parts needed for each column of the spreadsheet

for afile in locate('*', root=options.directory):
    nfile = os.path.basename(afile)
    matchrecs = re.search(r'([0-9].xml)', nfile)
    if nfile.endswith('.jp2') is True or nfile.endswith('.tif') is True:
        if nfile.split('-')[-2] == '000':
            pass
        else:
            imglist.append(nfile[0:-10])
            coll = afile.split('/')[2]
    elif matchrecs is not None:
        if nfile.endswith(matchrecs.group(1)) is True:
            reclst.append(nfile[0:-4])
            locpath = nfile[0:-4], afile.rsplit('/', 1)[0]
            loclist.append(locpath)

# Getting the record count

reclst2 = list(set([(i, reclst.count(i)) for i in reclst]))

loclist = list(set(loclist))
# reclst2 = list(set(reclst2))

# Creating the dictionaries for applying locations and record counts to the image list

for k, v in loclist:
    d1[k].append(v)

for k, v in reclst2:
    d2[k].append(v)

# Getting the page count and creating the other parts necessary for the spreadsheet

libraries = {'bnf': 'Bibliotheque National Du France',
             'kbn': 'Koninklijke Bibliotheek, Nationale bibliotheek van Nederland'}

for item in imglist:
    library = libraries[item.split('-')[1]]
    countis = str(imglist.count(item))
    locpath = str(d1[item]).translate(None, '[]\'')
    reccount = str(d2[item]).translate(None, '[]\'')
    '''PQID Library  Title   Author  Date    Imprint Country Shelfmark   Language    Subject local path  no. of pages'''
    imlst2.append('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (item, library, 'title', 'author', 'date', 'imprint', 'country', 'shelfmark', 'language', 'subject', locpath, countis, reccount))

imlst2 = list(set(imlst2))

# Writing the final list to the batch log file

with open(batchlog, 'w') as outf:
    for item in imlst2:
        outf.write('%s\n' % (item))
