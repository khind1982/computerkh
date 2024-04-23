#!/usr/bin/env python2.7

# App to convert delivered DNSA bibliographies to Lev-DNSA format

import os
import sys
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import lxml.etree as ET

from commonUtils.fileUtils import locate, buildLut
from optparse import OptionParser

parser = OptionParser()

(options, args) = parser.parse_args()

bibrec = []
citlist = []
filetypes = {'_bib.txt': 'bibliography',
             '_chron.txt': 'chronology'}

shortcollections = buildLut('dnsa_shortcols.lut')
longcollections = buildLut('dnsa_longcols.lut')

try:
    orifile = args[0]
except IndexError:
    print "Please specify a directory containing file(s) to convert"
    parser.print_help()
    exit(1)

for filetype in filetypes.keys():
    for nfile in locate('*%s' % filetype, orifile):

        fs = open(nfile, 'r').readlines()

        path = '%s/%s/' % (os.path.dirname(nfile), filetypes[filetype])
        if not os.path.exists(path):
            os.makedirs(path)
        outfilename = '%s.xml' % nfile.split('.')[0]
        collection_code = os.path.basename(nfile).split('_')[0]
        if filetypes[filetype] is 'chronology':
            fileprefix = 'T'
        else:
            fileprefix = 'B'
        bibrec.append('<?xml version="1.0" encoding="iso-latin-1"?>\n<document>\n<record>\n<rec_format formattype="%s">\n' % filetypes[filetype].capitalize())
        bibrec.append(('<collection_code>%s</collection_code>\n<docid>%s%s00001</docid>\n<title>%s: %s</title>\n<collection_names>\n<long>%s</long>\n<short>%s</short>\n</collection_names>\n<object_dates>\n<object_numdate>0001-01-01</object_numdate>\n<object_rawdate>Jan 1, 1</object_rawdate>\n</object_dates>\n') % (collection_code, fileprefix, collection_code, filetypes[filetype].capitalize(), longcollections[collection_code], longcollections[collection_code], shortcollections[collection_code]))
        if filetype is '_bib.txt':
            citlist.append('</rec_format>\n</record>\n<bodytext>\n<ul>\n')
        else:
            citlist.append('</rec_format>\n</record>\n<bodytext>\n')
        for line in fs:
            try:
                tagvalue = re.split('^[A-Z][A-Z]  ', line)[1].translate(None, '\n')
            except IndexError:
                pass
            if line.startswith('TY  '):
                citlist.append(('<li><b>%s:</b> ') % tagvalue)
            if line.startswith('CI  '):
                citlist.append(('%s</li><br/>\n') % tagvalue)
            if line.startswith('DA  '):
                citlist.append(('<p><b>%s:</b></p>\n') % tagvalue)
            if line.startswith('TX  '):
                citlist.append(('<p>%s</p>\n') % tagvalue)
        if filetype is '_bib.txt':
            citlist.append('</ul>\n</bodytext>\n')
        else:
            citlist.append('</bodytext>\n')
        for item in citlist:
            bibrec.append(item)
        citlist = []
        bibrec.append('</document>\n')
        outfilename = '%s%s%s00001.xml' % (path, fileprefix, collection_code)
        with open(outfilename, 'w') as out:
            for item in bibrec:
                out.write(item)
        bibrec = []

    tree = ET.parse(outfilename, ET.XMLParser(remove_blank_text=True, resolve_entities=True))



# for nfile in locate('*_bib.txt', orifile):
#     path = '%s/bibliography/' % (os.path.dirname(nfile))
#     if not os.path.exists(path):
#         os.makedirs(path)
#     with open(nfile, 'r') as file2convert:
#         outfilename = '%s.xml' % nfile.split('.')[0]
#         collection_code = os.path.basename(nfile).split('_')[0]
#         bibrec.append('<?xml version="1.0" encoding="iso-latin-1"?>\n<document>\n<record>\n<rec_format formattype="Bibliography">\n')
#         bibrec.append(('<collection_code>%s</collection_code>\n<docid>B%s00001</docid>\n<title>Bibliography: %s</title>\n<collection_names>\n<long>%s</long>\n<short>%s</short>\n</collection_names>\n<object_dates>\n<object_numdate>0001-01-01</object_numdate>\n<object_rawdate>Jan 1, 1</object_rawdate>\n</object_dates>\n') % (collection_code, collection_code, longcollections[collection_code], longcollections[collection_code], shortcollections[collection_code]))
#         citlist.append('</rec_format>\n</record>\n<bodytext>\n<ul>\n')
#         for line in file2convert:
#             try:
#                 tagvalue = re.split('^[A-Z][A-Z]  ', line)[1].translate(None, '\n')
#             except IndexError:
#                 pass
#             if line.startswith('TY  '):
#                 citlist.append(('<li><b>%s:</b> ') % tagvalue)
#             elif line.startswith('CI  '):
#                 citlist.append(('%s</li><br/>\n') % tagvalue)
#         citlist.append('</ul>\n</bodytext>\n')
#         for item in citlist:
#             bibrec.append(item)
#         citlist = []
#         bibrec.append('</document>\n')

#     outfilename = '%sB%s00001.xml' % (path, collection_code)
#     with open(outfilename, 'w') as out:
#         for item in bibrec:
#             out.write(item)
#     bibrec = []

# tree = ET.parse(outfilename, ET.XMLParser(remove_blank_text=True, resolve_entities=True))
