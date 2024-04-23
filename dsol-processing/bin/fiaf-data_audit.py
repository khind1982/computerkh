#!/usr/bin/env python2.7
# coding=utf-8

import codecs
import os
import re
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import datetime
import lxml.etree as ET
import HTMLParser

from commonUtils.fileUtils import locate, buildLut
from datetool.dateparser import parser as dateparser
from datetool.dateparser import ParserError
from StringIO import StringIO
from io import BytesIO

newjourns = []
jidsdict = buildLut('/dc/fiaf/utils/jid-title_fiaf-issn_rewrite.lut')

try:
    indir = sys.argv[1]
except IndexError:
    print "Usage: %s {indirectory}\nMaybe one of these is missing from your command?" % __file__
    exit()

h = HTMLParser.HTMLParser()
recs = 0


def strip_issn_delimiter(issn):
    return str('-'.join(re.findall('[0-9A-z]+', issn)))


for f in locate('*.xml', indir):
    with open(f) as fs:
        tree = ET.iterparse(fs, tag="record", remove_blank_text=True)

        for _, record in tree:
            recs += 1
            datelist = []

            # Checking dates in the records
            try:
                datelist.append(record.find('.//Source_Month').text)
            except AttributeError:
                datelist.append('Jan')
            datelist.append(record.find('.//Source_PY').text)

            try:
                parsed_date = dateparser.parse(' '.join(datelist)).start_date
            except ValueError:
                print '\033[91mError!\033[0m Invalid date in record %s: %s %s' % (record.find('.//ID').text, ET.tostring(record.find('.//Source_Month')), ET.tostring(record.find('.//Source_PY')))
            except ParserError:
                print '\033[91mError!\033[0m Unrecognised date in record %s: %s %s' % (record.find('.//ID').text, ET.tostring(record.find('.//Source_Month')), ET.tostring(record.find('.//Source_PY')))

            # Checking journals in the delivered file
            journal = strip_issn_delimiter(record.find('Source_ISSN').text)
            try:
                # Try and match ISSN to a legacy journal ID
                jid = jidsdict[journal].replace('/', '-')
            except KeyError:
                try:
                    # If that doesn't work, match it to a legacy journal title
                    journal = record.find('Source_Journal').text
                    jid = jidsdict[journal.encode('utf-8')].replace('/', '-')
                except KeyError:
                    # If that still doesn't work, identify the last ID that was assigned to a journal and create a new one that's unique.
                    print(ET.tostring(record, pretty_print=True), journal)
                    newjourns.append('(ISSN) %s (Journal) %s' % (record.find('Source_ISSN').text, record.find('Source_Journal').text))

            # sys.stdout.write('\033[92mNumber of records seen:\033[0m %s\r' % recs)
            # sys.stdout.flush()

        print '\n'
        newjourns = list(set(newjourns))
        if len(newjourns) > 0:
            print '\033[93mWarning\033[0m - new journal(s) encountered:'
            for item in newjourns:
                print item.encode('utf-8')
