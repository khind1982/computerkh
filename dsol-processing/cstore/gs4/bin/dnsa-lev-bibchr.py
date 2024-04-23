#!/usr/bin/env python2.7

# App to convert delivered DNSA bibliographies to Lev-DNSA format

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import codecs

import lxml.etree as ET

from StringIO import StringIO

from commonUtils.fileUtils import stream_as_records, locate, buildLut
from extensions.itertoolsextensions import grouped

citlist = []
filetypes = {'_bib.txt': 'bibliography',
             '_chron.txt': 'chronology'}

shortcollections = buildLut('/dc/dnsa/utils/dnsa_shortcols.lut')
longcollections = buildLut('/dc/dnsa/utils/dnsa_longcols.lut')

try:
    orifile = sys.argv[1]
except IndexError:
    print 'Usage: %s <input directory>\n' % __file__
    print 'Please specify a directory containing files to convert'
    exit()

for filetype in filetypes.keys():
    for nfile in locate('*%s' % filetype, orifile):

        fs = StringIO(codecs.open(nfile, 'r', 'latin-1').read())

        path = '%s/%s/' % (os.path.dirname(nfile), filetypes[filetype])
        if not os.path.exists(path):
            os.makedirs(path)
        outfilename = '%s.xml' % nfile.split('.')[0]
        collection_code = os.path.basename(nfile).split('_')[0]
        if filetypes[filetype] is 'chronology':
            fileprefix = 'T'
        else:
            fileprefix = 'B'

        document = ET.Element('document')
        record = ET.SubElement(document, 'record')
        bodytext = ET.SubElement(document, 'bodytext')
        rec_format = ET.SubElement(record, 'rec_format', formattype="%s" % filetypes[filetype].capitalize())
        ET.SubElement(rec_format, 'collection_code').text = collection_code
        ET.SubElement(rec_format, 'docid').text = '%s%s00001' % (fileprefix, collection_code)
        ET.SubElement(rec_format, 'title').text = '%s: %s' % (filetypes[filetype].capitalize(), longcollections[collection_code])
        collection_names = ET.SubElement(rec_format, 'collection_names')
        ET.SubElement(collection_names, 'long').text = longcollections[collection_code]
        ET.SubElement(collection_names, 'short').text = shortcollections[collection_code]
        object_dates = ET.SubElement(rec_format, 'object_dates')
        ET.SubElement(object_dates, 'object_numdate').text = '0001-01-01'
        ET.SubElement(object_dates, 'object_rawdate').text = 'Jan 1, 1'

        if 'OC  ' in fs.getvalue()[0:4]:

        # Grab the values from the first two lines
            oc = fs.next()
            cn = fs.next()

        # and seek past the next, blank, line
            fs.next()

    # register the position in the StringIO stream, in case we need to
    # rewind
            start_of_stream = fs.tell()

        if filetype is '_bib.txt':
            citlist.append('<ul>')
            for r in grouped(stream_as_records(fs, 'TY  '), 2):
                citlist.append('<li><b>%s</b>: %s</li>' % (r[0][1][0].replace('TY  ', '').strip(), r[1][1][0].replace('CI  ', '').strip()))
            citlist.append('</ul>')
            bodytext.text = ET.CDATA('\n'.join(citlist))
            citlist = []

        if filetype is '_chron.txt':
            for r in grouped(stream_as_records(fs, 'DA  '), 2):
                citlist.append('<p><b>%s</b></p>\n' % (r[0][1][0].replace('DA  ', '').strip()))
                for item in r[1][1]:
                    if 'TX  ' in item:
                        citlist.append('<p>%s</p>\n' % item.replace('TX  ', '').strip())
            bodytext.text = ET.CDATA(''.join(citlist))
            citlist = []

        outfilename = '%s%s%s00001.xml' % (path, fileprefix, collection_code)
        with open(outfilename, 'w') as out:
            out.write(ET.tostring(document, pretty_print=True))
