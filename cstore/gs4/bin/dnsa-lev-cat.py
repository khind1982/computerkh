#!/usr/bin/env python2.7

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import codecs
import re

import lxml.etree as ET

from collections import defaultdict
from StringIO import StringIO

from commonUtils.fileUtils import stream_as_records, locate, buildLut
from extensions.itertoolsextensions import grouped

shortcollections = buildLut('/dc/dnsa/utils/dnsa_shortcols.lut')
longcollections = buildLut('/dc/dnsa/utils/dnsa_longcols.lut')
fields = buildLut('dnsa_fields2.lut')
percorp = buildLut('/dc/dnsa/utils/dnsa_percorp.lut')
months = {'01': 'January ',
          '02': 'February ',
          '03': 'March ',
          '04': 'April ',
          '05': 'May ',
          '06': 'June ',
          '07': 'July ',
          '08': 'August ',
          '09': 'September ',
          '10': 'October ',
          '11': 'November ',
          '12': 'December ',
          '00': ''}
days = {'01': '1, ',
        '02': '2, ',
        '03': '3, ',
        '04': '4, ',
        '05': '5, ',
        '06': '6, ',
        '07': '7, ',
        '08': '8, ',
        '09': '9, ',
        '00': ''}

newpercorp = []
doctypes = []
pdfdict = {}


try:
    orifile = sys.argv[1]
except IndexError:
    print 'Usage: %s <input directory>\n' % __file__
    print 'Please specify a directory containing files to convert'
    exit()


# def namepdfs(data):
#     print data['FI']
#     for pdf in locate('*.pdf', orifile):
#         print os.path.basename(pdf)


def writexml(data):
    path = '%s/documents' % (os.path.dirname(f))
    if not os.path.exists(path):
        os.makedirs(path)
    collcode = os.path.basename(f).split('_')[0]

    root = ET.Element('document')
    rec = ET.SubElement(root, 'record')
    rec_format = ET.SubElement(rec, 'rec_format', formattype="Document")
    ET.SubElement(rec_format, 'collection_code').text = collcode
    if 'UI' not in data.keys():
        data['UI'] = 'C%s%s' % (collcode, data['FS'])
    outf = '%s/%s.xml' % (path, data['UI'])

    if collcode not in data['FS']:
        data['FS'] = '%s%s' % (collcode, data['FS'])
    if 'TY' not in data.keys():
        data['TY'] = data['DO']
    for key in data.keys():
        try:
            ET.SubElement(rec_format, fields[key]).text = data[key]
        except KeyError:
            pass
    collection_names = ET.SubElement(rec_format, 'collection_names')
    try:
        ET.SubElement(collection_names, 'long').text = longcollections['%s' % collcode]
    except KeyError:
        print 'No collection long name available: please add to /dc/dnsa/utils/dnsa_longcols.lut and try again'
        exit()
    try:
        ET.SubElement(collection_names, 'short').text = shortcollections['%s' % collcode]
    except KeyError:
        print 'No collection short name available: please add to /dc/dnsa/utils/dnsa_shortcols.lut and try again'
        exit()

    ET.SubElement(rec_format, 'title').text = titlemerge(data)
    object_dates = ET.SubElement(rec_format, 'object_dates')
    if 'WB' in data.keys():
        webpro = data['WB'].split(' ')
        nwebpro = ' '.join([i for i in webpro if 'http' not in i])
        if nwebpro != '':
            ET.SubElement(rec_format, 'loc_of_original_doc').text = nwebpro
        for link in webpro:
            if 'http' in link:
                ET.SubElement(rec_format, 'link').text = link
    if 'DA' in data.keys():
        ET.SubElement(object_dates, 'object_numdate').text = '-'.join(data['DA'].split('/'))
        if 'DV' in data.keys():
            ET.SubElement(object_dates, 'object_rawdate').text = data['DV']
        else:
            if data['DA'].split('/')[2] in days.keys():
                day = days[data['DA'].split('/')[2]]
            else:
                day = '%s, ' % data['DA'].split('/')[2]
            ET.SubElement(object_dates, 'object_rawdate').text = '%s%s%s' % (months[data['DA'].split('/')[1]], day, data['DA'].split('/')[0])
    elif 'CI' in data.keys():
        ET.SubElement(object_dates, 'object_numdate').text = '-'.join(data['CI'].split('/'))
        if data['CI'].split('/')[2] in days.keys():
            day = days[data['CI'].split('/')[2]]
        else:
            day = '%s, ' % data['CI'].split('/')[2]
        ET.SubElement(object_dates, 'object_rawdate').text = 'c. %s%s%s' % (months[data['CI'].split('/')[1]], day, data['CI'].split('/')[0])
    if 'CW' in data.keys():
        for codeword in ORreform(data['CW']):
            if codeword != '':
                ET.SubElement(rec_format, 'code_word').text = codeword.strip()
    if 'OR' in data.keys() or 'SN' in data.keys() or 'PT' in data.keys():
        contributors = ET.SubElement(rec_format, 'contributors')
    if 'OR' in data.keys():
        for name in ORreform(data['OR']):
            contributor = ET.SubElement(contributors, 'contributor', role="CorpAuthor")
            ET.SubElement(contributor, 'originalform').text = name.strip()
    if 'SN' in data.keys():
        data['SN'] = data['SN'].replace('amp;', '')
        for name in SNreform(data['SN']):
            contributor = ET.SubElement(contributors, 'contributor', role="MiscRole")
            ET.SubElement(contributor, 'originalform').text = name.strip()
            ET.SubElement(contributor, 'role_desc').text = 'Signator'
    if 'PT' in data.keys():
        for name in SNreform(data['PT']):
            contributor = ET.SubElement(contributors, 'contributor', role="MiscRole")
            ET.SubElement(contributor, 'originalform').text = name.strip()
            ET.SubElement(contributor, 'role_desc').text = 'Participant'
    if 'DT' in data.keys():
        recipients = ET.SubElement(rec_format, 'recipients')
        for name in SNreform(data['DT']):
            ET.SubElement(recipients, 'recipient').text = name.strip()
    if 'IN' in data.keys():
        names = ET.SubElement(rec_format, 'names')
        data['IN'] = data['IN'].replace('amp;', '')
        if ';' in data['IN']:
            for name in ORreform(data['IN']):
                try:
                    if percorp[name.encode('latin-1').strip()] == 'personal':
                        ET.SubElement(names, 'personal').text = name.strip()
                    else:
                        ET.SubElement(names, 'corporate').text = name.strip()
                except KeyError:
                    if ',' in name.encode('latin-1').strip():
                        ET.SubElement(names, 'personal').text = name.strip()
                        newpercorp.append('%s|personal' % name.strip())
                    else:
                        ET.SubElement(names, 'corporate').text = name.strip()
                        newpercorp.append('%s|corporate' % name.strip())
        else:
            for name in SNreform(data['IN']):
                try:
                    if percorp[name.encode('latin-1').strip()] == 'personal':
                        ET.SubElement(names, 'personal').text = name.strip()
                    else:
                        ET.SubElement(names, 'corporate').text = name.strip()
                except KeyError:
                    if ',' in name.encode('latin-1').strip():
                        ET.SubElement(names, 'personal').text = name.strip()
                        newpercorp.append('%s|personal' % name.strip())
                    else:
                        ET.SubElement(names, 'corporate').text = name.strip()
                        newpercorp.append('%s|corporate' % name.strip())

    if 'KY' in data.keys():
        subjects = ET.SubElement(rec_format, 'subjects')
        for subj in SNreform(data['KY']):
            ET.SubElement(subjects, 'subject').text = subj.strip()
    if 'SU' in data.keys() and 'KY' not in data.keys():
        subjects = ET.SubElement(rec_format, 'subjects')
        for subj in ORreform(data['SU']):
            ET.SubElement(subjects, 'subject').text = subj.strip()

    doctypes.append(root.find('.//doctype1').text.encode('latin-1'))

    with open(outf, 'w') as outfile:
        outfile.write(ET.tostring(root, pretty_print=True, encoding='iso-latin-1', xml_declaration=True).replace('amp;amp;', 'amp;'))  # adding .replace('amp;amp;', 'amp;') will work but we don't want to use it...

    pdfdict[str(data['FI'])] = 'C%s.pdf' % (str(data['FS']))

def titlemerge(data):
    if 'TT' in data.keys() and 'CT' in data.keys():
        return '%s %s' % (data['TT'], data['CT'])
    elif 'TT' in data.keys():
        return data['TT']
    elif 'CT' in data.keys():
        return data['CT']
    else:
        return '[%s %s]' % (data['CL'], data['DO'])

def SNreform(data):
    translist = []
    for i in data.split('|'):
        if 'a href' in i:
            translist.append(re.split('<a |">|</a>', i)[2])
        else:
            translist.append(i)
    return translist

def ORreform(data):
    translist = []
    data = data.replace('&amp;', '&')
    for i in data.split(';'):
        if 'a href' in i:
            translist.append(re.split('<a |">|</a>', i)[2])
        else:
            translist.append(i)
    return translist

for f in locate('*_catalog.txt', orifile):
    count = 0
    collcode = os.path.basename(f).split('_')[0]

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
        count += 1

        sys.stdout.write('\033[92mWorking on collection:\033[0m %s, \033[92mRecords seen:\033[0m %s\r' % (collcode, count))
        sys.stdout.flush()

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

    print '\n'

    doctypes = list(set(doctypes))
    with open('/dc/dnsa/utils/dnsa_doctypes.txt', 'r') as doctypesfile:
        legdoctypes = doctypesfile.read().splitlines()
    for item in doctypes:
        if item not in legdoctypes:
            print "New doctype encountered: %s" % item

    if len(newpercorp) > 0:
        newpercorp = list(set(newpercorp))
        print 'The following people/corporations have not been encountered before:'
        for item in newpercorp:
            print '%s' % item.encode('latin-1')
        print 'Validate these and add to /dc/dnsa/utils/dnsa_percorp.lut if any values are incorrect'

    if collcode in os.path.abspath(orifile):
        pdfpath = os.path.abspath(orifile)
    else:
        pdfpath = '%s/%s' % (os.path.abspath(orifile), collcode)

    if os.path.exists('%s' % os.path.join(pdfpath, 'pdf')) is True or os.path.exists('%s' % os.path.join(pdfpath, 'pdfs')) is True:
        for pdf in locate('*.pdf', pdfpath):
            if collcode in os.path.basename(pdf):
                pass
            else:
                try:
                    os.rename('%s/%s' % (os.path.dirname(pdf), os.path.basename(pdf)), '%s/%s' % (os.path.dirname(pdf), pdfdict[os.path.basename(pdf)]))
                except KeyError:
                    pass

    else:
        print 'No pdf directory detected in %s (%s); copy the incoming pdf directory across and run the script again' % (os.path.abspath(orifile), collcode)
