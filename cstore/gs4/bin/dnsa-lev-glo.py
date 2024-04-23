#!/usr/bin/env python2.7

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import codecs

import lxml.etree as ET

from collections import defaultdict
from StringIO import StringIO

from commonUtils.fileUtils import stream_as_records, locate, buildLut, _buildPath
from extensions.itertoolsextensions import grouped

shortcollections = buildLut('/dc/dnsa/utils/dnsa_shortcols.lut')
longcollections = buildLut('/dc/dnsa/utils/dnsa_longcols.lut')
nglosscross = _buildPath('/dc/dnsa/utils/dnsa_glosscross.txt')

try:
    orifile = sys.argv[1]
except IndexError:
    print 'Usage: %s <input directory>\n' % __file__
    print 'Please specify a directory containing files to convert'
    exit()

docidlist = []
glosslist = []

# This part allows a user to specify a list of names
# from other glossary collections and add them as new records to the latest collection.
# FIXME: rethink this as a separate funtion


def addoldgloss():

    with open(nglosscross, 'r') as lutfile:
        for line in lutfile:
            docid = line.strip().split('|')[0]
            newcoll = docid[0:2]
            path = '/dc/dnsa/data/master/%s/glossaries' % newcoll
            if not os.path.exists(path):
                os.makedirs(path)
            homecoll = line.strip().split('|')[1]
            homecollval = line.strip().split('|')[2]
            forappend = docid, homecoll, homecollval
            docidlist.append(forappend)
            try:
                rename = line.strip().split('|')[3]
            except:
                pass
            for gf in locate('*.xml', '/dc/dnsa/data/master/%s/glossaries' % homecoll):
                gfs = StringIO(open(gf, 'r').read())
                tree = ET.parse(gfs, ET.XMLParser(remove_blank_text=True))
                root = tree.getroot()
                if root.find('.//title').text == homecollval:
                    root.find('.//docid').text = 'G%s' % docid
                    root.find('.//collection_code').text = newcoll
                    root.find('.//collection_names/long').text = longcollections[docid[0:2]]
                    root.find('.//collection_names/short').text = shortcollections[docid[0:2]]
                    outf = '/dc/dnsa/data/master/%s/glossaries/G%s.xml' % (docid[0:2], docid)
                    glosslist.append(docid)
                    with open(outf, 'w') as outfile:
                        outfile.write(ET.tostring(root, pretty_print=True))
    for item in docidlist:
        if item[0] in glosslist:
            pass
        else:
            print 'The following glossary entry could not be matched: %s' % str(item)

def writexml(data):
    path = '%s/glossaries' % (os.path.dirname(f))
    if not os.path.exists(path):
        os.makedirs(path)
    collcode = os.path.basename(f).split('_')[0]
    if collcode not in data['FS']:
        outf = '%s/G%s%s.xml' % (path, collcode, data['FS'])
        data['FS'] = 'G%s%s' % (collcode, data['FS'])
    else:
        outf = '%s/%s.xml' % (path, data['FS'])
    root = ET.Element('document')
    rec = ET.SubElement(root, 'record')
    rec_format = ET.SubElement(rec, 'rec_format', formattype="Glossary")
    ET.SubElement(rec_format, 'docid').text = data['FS']
    ET.SubElement(rec_format, 'collection_code').text = collcode
    collection_names = ET.SubElement(rec_format, 'collection_names')
    ET.SubElement(collection_names, 'long').text = longcollections[collcode]
    ET.SubElement(collection_names, 'short').text = shortcollections[collcode]
    ET.SubElement(rec_format, 'title').text = data['GL']
    try:
        ET.SubElement(rec_format, 'glosstype').text = data['TY']
    except TypeError:
        print 'Record format does not match expectations:'
        print data
        print 'Processing incomplete. Review the record and correct the data.'
        exit()
    object_dates = ET.SubElement(rec_format, 'object_dates')
    ET.SubElement(object_dates, 'object_numdate').text = '0001-01-01'
    ET.SubElement(object_dates, 'object_rawdate').text = 'Jan 1, 1'
    bodytext = ET.SubElement(root, 'bodytext')
    for i in data['TX']:
        try:
            ET.SubElement(bodytext, 'p').text = i
        except ValueError:
            print i
            raise
    if data['TY'] == 'Names':
        names = ET.SubElement(rec_format, 'names')
        ET.SubElement(names, 'personal').text = data['GL']
    elif data['TY'] == 'Organizations':
        names = ET.SubElement(rec_format, 'names')
        ET.SubElement(names, 'corporate').text = data['GL']
    else:
        subjects = ET.SubElement(rec_format, 'subjects')
        ET.SubElement(subjects, 'subject').text = data['GL']

    with open(outf, 'w') as outfile:
        outfile.write(ET.tostring(root, pretty_print=True, encoding='iso-latin-1', xml_declaration=True).replace('amp;amp;', 'amp;')) # adding will work but we don't want to use it: .replace('amp;amp;', 'amp;')

def checkrecs(data):
    badrecs = []
    for item in data:
        if item[0] == True:
            if len(item[1]) > 1:
                for rec in item[1]:
                    badrecs.append(rec)
    if len(badrecs) > 0:
        print 'Warning - the following records have errors and will not be output correctly:'
        for item in badrecs:
            print item.strip()

for f in locate('*_gloss.txt', orifile):
    recs = 0

    fs = StringIO(codecs.open(f, 'r', 'latin-1').read())

    if 'OC  ' in fs.getvalue()[0:4]:

# Grab the values from the first two lines
        oc = fs.next()
        cn = fs.next()

# and seek past the next, blank, line
        fs.next()

# register the position in the StringIO stream, in case we need to
# rewind
        start_of_stream = fs.tell()

        for r in grouped(stream_as_records(fs, 'FS  '), 2):
            record = defaultdict(list)

            record['FS'] = r[0][1][0].replace('FS  ', '').strip()
            for i in r[1][1]:
                key = i[0:2]
                val = i[3:].strip()
                if key == 'TX':
                    record[key].append(val)
                else:
                    record[key] = val

            writexml(record)
    else:
        reccount = 0
        gllist = []

        for r in grouped(stream_as_records(fs, 'GL  '), 2):
            reccount += 1
            record = defaultdict(list)
            record['GL'] = r[0][1][0].replace('GL  ', '').strip()
            record['FS'] = str(reccount).zfill(5)
            for i in r[1][1]:
                key = i[0:2]
                val = i[3:].strip()
                if key == 'TX':
                    record[key].append(val)
                else:
                    record[key] = val
            writexml(record)
            recs += 1
            sys.stdout.write('Number of records created: \033[92m%s\r' % recs)
            sys.stdout.flush()
        records = [r for r in stream_as_records(fs, 'GL  ')]
        checkrecs(records)
        print '\n'
addoldgloss()
