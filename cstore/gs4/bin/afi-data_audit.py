#!/usr/bin/env python2.7
# coding=utf-8
import codecs
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import datetime
import lxml.etree as ET
from xml.sax.saxutils import unescape
import HTMLParser

from commonUtils.fileUtils import locate, buildLut

try:
    indir = sys.argv[1]
except IndexError:
    print("Usage: %s {indirectory}\nMaybe one of these is missing from your command?" % __file__)
    exit()

with codecs.open('/dc/afi/utils/movietitles.lut') as idlup:
    idlookup = {}
    for line in idlup:
        key, value = line.split('|')
        idlookup[key.strip()] = value.strip()

iddict = {}

for f in locate('NameIndex*.xml', indir):
    tree = ET.iterparse(f, remove_blank_text=True)

    for _, record in tree:

        # Checking for null values in person records
        if record.tag == "PERSONAL_NAME":
            pnid = record.find('./ID').text
            nametest = [i.text for i in record.findall('.//FULL_NAME')]
            for i in nametest:
                if i == None:
                    print('\033[93mWarning:\033[0m Null value detected for person name record %s, file %s' % (pnid, f))

for f in locate('AFI*.xml', indir):
    root = ET.parse(f, ET.XMLParser(remove_blank_text=True, encoding='utf-8'))
    for record in root.xpath('//MOVIE'):
        # Checking IDs in the records
        try:
            record_title = record.xpath('.//TITLE')[0].text.strip().encode('utf-8')
            lookup_title = idlookup[record.xpath('./MOVIE_ID')[0].text]
            if record_title != lookup_title:
                print('\033[93mWarning!\033[0m ID-Title: %s %s mismatch with legacy title: %s (file: %s)' % (record.find('.//MOVIE_ID').text, record_title, lookup_title, f))
        except KeyError:
            pass
        except UnicodeEncodeError:
            print(f, record.xpath('.//MOVIE_ID')[0].text)
            raise

        # Checking dates in the records
        day = record.find('.//RELEASE_DAY').text
        month = record.find('.//RELEASE_MONTH').text
        year = record.find('.//RELEASE_YEAR').text

        if day == None or day == '0':
            day = '01'
        else:
            day = day.zfill(2)
        if month == None or month == '0':
            month = '01'
        else:
            month = month.zfill(2)

        try:
            datetime.datetime.strptime('%s-%s-%s' % (year, month, day), '%Y-%m-%d')
        except ValueError:
            print('\033[91mError!\033[0m Invalid date in record %s: %s %s %s' % (record.find('.//MOVIE_ID').text, ET.tostring(record.find('.//RELEASE_DAY')), ET.tostring(record.find('.//RELEASE_MONTH')), ET.tostring(record.find('.//RELEASE_YEAR'))))
