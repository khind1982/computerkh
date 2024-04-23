#!/usr/bin/env python2.7

# Script to extract fields from human readable marc records.

import os
import sys
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
import codecs

import lxml.etree as ET

from collections import defaultdict, OrderedDict
from StringIO import StringIO

from lxml import etree as ET

from commonUtils.fileUtils import stream_as_records, locate, buildLut
from commonUtils.textUtils import fix_named_ents
from xmlUtils import presenceTestSingle
from genrecord import GenRecord
from streams.genfilestream import GenFileStream
from streams.filestream import FileStream
from streams.abstractstream import AbstractStream

from extensions.itertoolsextensions import grouped

# Script to-do
# Supress Anon if no marc version
# Supress Anon in nicmarks
# Add standardise column DONE
# Prem marcs should be default?

try:
    infile = sys.argv[1]
    indir = sys.argv[2]
except IndexError:
    print 'Usage: %s [input marc] [input xml dir]\n' % __file__
    exit()

pqidict = defaultdict(list)
collections = buildLut('/dc/eurobo/utils/collection_allrecs.lut')

'''need to create a dict of the authors then append it to the pqid'''

def extract(data, target, id, targname):
    tardict = {}
    tarlist = []
    if targname not in pqidict[id][0].keys():
        pqidict[id][0][targname] = []
    for i in target:
        for value in data[i]:
            if value.split('$a')[1].strip() != 'Anon' and value.split('$a')[1].strip() != 'Anon.':
                pqidict[id][0][targname].append(value.split('$a')[1].strip())
                pqidict[id][0][targname] = list(set(pqidict[id][0][targname]))
       

# Defining the marc fields that contain different types of data
main_author = ['=100', '=110', '=111']
alt_author = ['=700', '=710', '=711']

# Streaming the records one at a time

for f in locate('*.mrk', infile):
    print f
    fs = StringIO(codecs.open(f, 'r', 'utf-8').read())   

    for r in grouped(stream_as_records(fs, '=LDR  '), 2):
        record = defaultdict(list)

        record['=LDR  '] = [r[0][1][0][3:]]
        for i in r[1][1]:
            key = i[0:4]
            val = i[4:]
            record[key].append(val)
        for i in record['=856']:
            try:
                pqid = i.split(':rec:')[1].strip()
                if pqid not in pqidict.keys():
                    pqidict[pqid] = [{}]      
                extract(record, main_author, pqid, 'mrk_main')
                # extract(record, alt_author, pqid, 'mrk_other')
            except IndexError:
                print i
                pass

tabfile = []
tabfile.append('PQID\tUnit\tStandardise\tMrk Main\tXml Name|Corrected|Uninverted\tLink to title page in product\n')
authfields = ['author_name', 'author_corrected', 'author_uninverted']

for d in os.listdir(indir):
    if 'Collection' in d:
        print d
        for f in locate('*.xml', os.path.join(indir, d)):
            xmldict = {}
            root = ET.parse(f).getroot()
            # Multiple authors, keeping it all together.... Name|Corrected
            mainls = []
            # otherls = []
            maincorrect = ''
            for main in root.findall('.//author_main'):
                if presenceTestSingle(main.find('.//author_name')) != 'Anon.' and presenceTestSingle(main.find('.//author_name')) != 'Anon':
                    name = presenceTestSingle(main.find('.//author_name'))
                    maincorrect = presenceTestSingle(main.find('.//author_corrected'))
                    xmldict['auth_to_standard'] = maincorrect
                    uninverted = presenceTestSingle(main.find('.//author_uninverted'))
                    mainls.append('%s|%s|%s' % (name, maincorrect, uninverted))
            # for other in root.findall('.//author_other'):
            #     if presenceTestSingle(other.find('.//author_name')) != 'Anon.' and presenceTestSingle(main.find('.//author_name')) != 'Anon':
            #         name = presenceTestSingle(other.find('.//author_name'))
            #         correct = presenceTestSingle(other.find('.//author_corrected'))
            #         uninverted = presenceTestSingle(other.find('.//author_uninverted'))
            #         otherls.append('%s|%s|%s' % (name, correct, uninverted))
            xmldict['main_author'] = mainls
            # xmldict['other_author'] = otherls
            # xmldict['collection'] = d
            pqidict[root.find('.//itemid').text].append(xmldict)
            

for pqid in pqidict.keys():
    for dict in pqidict[pqid]:
        pqidict[pqid][0].update(dict)
    try:
        pqidict[pqid] = pqidict[pqid][0]
        print pqidict['ita-bnc-in1-00001058-001']
    except IndexError:
        print pqid
        print pqidict[pqid]
        raise
    if ''.join([''.join(i) for i in pqidict[pqid].values()]) != '':
        for key in ['mrk_main', 'main_author', 'auth_to_standard']:
            if key not in pqidict[pqid].keys():
                pqidict[pqid][key] = ''
            try:
                colle = collections[str(pqid)]
            except KeyError:
                colle = ''
        tabfile.append('%s\t%s\t%s\t%s\t%s\thttp://eeb.chadwyck.co.uk/search/displayImageItemFromId.do?FormatType=fulltextimgsrc&ItemID=%s&ImageNumber=0&BackTo=\n' % (pqid, colle, pqidict[pqid]['auth_to_standard'], ' ; '.join(pqidict[pqid]['mrk_main']), ' ; '.join(pqidict[pqid]['main_author']), pqid))

outfile = '/dc/eurobo/editorial/standardisation/author.out'

with open(outfile, 'w') as out:
    for i in tabfile:
        out.write(i.encode('utf-8'))
