#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

'''This script prepares a set of EEB content to be added to a collection:
1 - adds the BookIDs to the collection lookup file'''
import argparse
import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.append('/packages/dsol/opt/lib/python2.7/site-packages')

import lxml.etree as ET
import shutil
from commonUtils.fileUtils import locate, buildLut

# try:
#     infile = sys.argv[1]
#     outdir = sys.argv[2]
#     coll = sys.argv[3]
# except IndexError:
#     print "Usage: eeb-handover_prep.py [input file] [output dir] [collection name]\n"
#     exit(1)

parser = argparse.ArgumentParser()
parser.add_argument('infile')
parser.add_argument('outdir')
parser.add_argument('coll', nargs='?', default=None)

args = parser.parse_args(sys.argv[1:])

infile = args.infile
outdir = args.outdir
coll = args.coll

if not os.path.exists(outdir):
    os.makedirs(outdir)

booklist = []
bookdict = buildLut('/dc/eurobo/content/authors/collection_lookup.lut')

colourexclude = ['Back board', 
                 'Back endpaper', 
                 'Foredge', 
                 'Front board', 
                 'Front endpaper', 
                 'Head edge', 
                 'Interior back binding', 
                 'Interior front binding', 
                 'Spine', 
                 'Tail edge']

# Defining labels from which the Marginalia tag should be removed:

labels = ['Front endpaper', 
          'Back endpaper', 
          'Inside back binding', 
          'Inside front binding', 
          'Interior back binding',
          'Interior front binding']

bookdirs = []
locs = []
messagelog = []

print 'Reading file locations...\n'

with open(infile, 'r') as inf:
    '''Split the line to the bookid value, and create a list of files to process from that, warning user'''

    for fl in inf:
        fl = fl.strip()
        if os.path.isfile(fl):
            input_file_type = 'xmls'
            locs.append(fl)
            split = re.split('-....xml', os.path.basename(fl))[0]
            bookdir = '%s%s' % (re.split(split, fl)[0], split)
            bookdirs.append(bookdir)
        else:
            input_file_type = None
            if os.path.isdir(fl):
                bookdirs.append(fl)
            else:
                print('%s has not been found' % fl)
            # print '%s is not a file. Skipping...' % fl

bookdirs = list(set(bookdirs))

print 'Locating files...\n'

for i in bookdirs:        
    for f in locate('*[0-9][0-9][0-9].xml', i):
        root = ET.parse(f).getroot()
        divs = root.findall('.//{*}structMap/{*}div/{*}div')

        # Reporting a boundwith that will be included
        if input_file_type and f not in locs:
            messagelog.append('Additional boundwith: %s' % f)
            
        # Adding missing ID and shelfmark content
        if root.find('.//{*}recordInfo') is None:
            for ele in root.findall('.//{*}identifier'):
                if ele.get('type') == 'coteoriginal':
                   contsource = ele.text

            recInf = ET.Element(ET.QName('http://www.loc.gov/mods/v3', 'recordInfo'), nsmap={'mods':'http://www.loc.gov/mods/v3'})
            ET.SubElement(recInf, ET.QName('http://www.loc.gov/mods/v3', 'recordIdentifier'), nsmap={'mods':'http://www.loc.gov/mods/v3'}).text = os.path.basename(f).replace('.xml', '')
            ET.SubElement(recInf, ET.QName('http://www.loc.gov/mods/v3', 'recordContentSource'), nsmap={'mods':'http://www.loc.gov/mods/v3'}).text = contsource
            root.find('.//{http://www.loc.gov/mods/v3}mods').insert(0, recInf)

        # Promoting author to main if none exists
        authors = root.findall('.//{http://www.loc.gov/mods/v3}name')
        firstauthor = root.find('.//{http://www.loc.gov/mods/v3}name')
        if len(authors) > 0:
            roles = [i.find('.//{*}roleTerm').text for i in authors if i.find('.//{*}roleTerm') is not None and i.find('.//{*}roleTerm').text is not None]
            if len(roles) > 0:
                if 'mainauthor' not in roles and 'author' not in roles:
                    if firstauthor.find('.//{*}roleTerm') is not None and firstauthor.find('.//{*}roleTerm').text is not None:
                        firstauthor.find('.//{*}roleTerm').text = 'mainauthor'

        # Adding colour pagecontent type
        for i in divs:
            if 'colour' in i.attrib['TYPE'] and 'T1' not in i.attrib['TYPE']:
                if i.attrib['ORDER'] != str('0') and i.attrib['LABEL'] not in colourexclude:
                    if '|' in i.attrib['TYPE']:
                        i.attrib['TYPE'] = '%sT1' % i.attrib['TYPE']
                    else:
                        i.attrib['TYPE'] = 'colour|T1'
            # Removing marginalia from relevant records
            for item in labels:
                if item in i.attrib['LABEL']:
                    if 'I1' in i.attrib['TYPE']:
                        i.attrib['TYPE'] = i.attrib['TYPE'].replace('I1', '')
                        if i.attrib['TYPE'] == 'monochrome|' or i.attrib['TYPE'] == 'colour|':
                            i.attrib['TYPE'] = i.attrib['TYPE'].replace('|', '')
            
        # Adding the bookid to the collections dictionary.
        bookid = re.split('-....xml', os.path.basename(f))[0]
        if bookid not in bookdict.keys() and coll is not None:
            booklist.append('%s|%s' % (bookid, coll))
            bookdict[bookid] = coll
        
        if coll is not None and bookdict[bookid] != coll:
            print 'Warning: %s is in collection_lookup.lut for %s. It has not been added to the lookup and will not be copied to %s.' % (bookid, bookdict[bookid], outdir)
        else:
            outfile = '%s/%s' % (outdir, os.path.basename(f))
            with open(outfile, 'w') as out:
                out.write(ET.tostring(root))

        # else:
        #     if bookdict[bookid] == coll:
        #         outfile = '%s/%s' % (outdir, os.path.basename(f))
        #         with open(outfile, 'w') as out:
        #             out.write(ET.tostring(root))
        #     else:
        #         print 'Warning: %s is in collection_lookup.lut for %s. It has not been added to the lookup and will not be copied to %s.' % (bookid, bookdict[bookid], outdir)

print 'Files in place.'

if coll:
    print('Updating collections lookup file')
    with open('/dc/eurobo/content/authors/collection_lookup.lut', 'r') as infile:
        for line in infile:
            booklist.append(line.strip())

    booklist = list(set(booklist))

    shutil.copyfile('/dc/eurobo/content/authors/collection_lookup.lut', '/dc/eurobo/content/backups/collection_lookup.lut'.replace('.lut', '.bak'))

    outfile = '/dc/eurobo/content/authors/collection_lookup.lut'

    with open(outfile, 'w') as out:
        for i in booklist:
            out.write('%s\n' % i) 
 
mlogout = '%s/messagelog.txt' % outdir

if len(messagelog) > 0:
    with open(mlogout, 'w') as mout:
        print 'Additional boundwiths detected. Check %s and change Selection Status in main eeb log' % mlogout
        for i in messagelog:
            mout.write('%s\n' % i)
        