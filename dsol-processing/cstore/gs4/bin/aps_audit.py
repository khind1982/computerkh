#!/usr/bin/env python
# -*- mode: python -*-

# Walk a directory tree containing APS style xml, and check for
# spelling errors in the APS_title element, and ensure
# APS_article[@type] contains one of the permitted values.

import os
import sys
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'lib'))

import re

from datetime import datetime

import lxml.etree as ET

#pylint:disable=F0401
from commonUtils.fileUtils import locate
from ispell import ispell

try:
    directory_to_check = sys.argv[1]
except IndexError:
    directory_to_check = os.path.curdir

print directory_to_check

valid_doc_types = {
    'aaa': [
        'Advertisement', 'Article', 'Back Matter', 'Correspondence',
        'Editorial Cartoon/Comic', 'Front Page', 'Image/Photograph',
        'News', 'Illustration', 'Poem', 'Recipe', 'Review',
        'Statistics/Data Report', 'Obituary', 'Table Of Contents',
        'Undefined'
        ],
    }

log = open(os.path.join(os.path.expanduser('~'), 'aps_audit.log'), 'a')

spellchecker = ispell()

for f in locate('*.xml', root=directory_to_check):
    filename = os.path.basename(f)
    if not filename[0:3] in ['AAA', 'WWD', 'TRJ', 'APS_']: continue

    log.write("\n============================================\n\n")
    log.write("Checked %s\n" % datetime.strftime(datetime.now(), "%Y %m %d, %H:%M"))
    log.write("%s\n\n" % f)

    status = ''

    try:
        xml = ET.parse(f, ET.XMLParser(remove_blank_text=True))
    except ET.XMLSyntaxError as e:
        #pylint:disable=E1101
        if e.msg.startswith("xmlParseEntityRef: no name"):
            log.write("Unescaped entity reference (probably a bare '&' character)")
            status += " invalid entity reference;"
        elif e.msg.startswith("Opening and ending tag mismatch:"):
            log.write("Tag mismatch, %s" % e)
            status += " tag mismatch;"
        else:
            print f
            print e
            raise

    doc_type = xml.getroot().attrib['type']
    if doc_type not in valid_doc_types[filename[0:3].lower()]:
        log.write("Invalid doc type %s\n" % doc_type)
        status += " invalid doc_type;"

    aps_title = xml.find('.//APS_title')
    if aps_title is None:
        log.write("No APS_title element\n")
        status += " no title element;"
    elif aps_title.text == None:
        log.write("Empty APS_title element\n")
        status += " empty title element;"
    else:
        # convert '-' to 'HHYYPPHHEENN'
        try:
            title_words = [re.sub(r'-', 'HHYYPPHHEENN', word) for word in aps_title.text.split(' ') if not '&' in word]
        except AttributeError:
            print f
            raise
        # convert "'" to 'AAPPOOSS'
        title_words = [re.sub(r"'", 'AAPPOOSS', word) for word in title_words]
        # remove any punctuation marks.
        title_words = [re.sub(r'\W+', '', word) for word in title_words]
        # remove any words containing numbers
        title_words = [word for word in title_words if not re.search(r'\d', word)]
        # Restore HHYYPPHHEENN and AAPPOOSS
        title_words = [word.replace('HHYYPPHHEENN', '-') for word in title_words]
        title_words = [word.replace('AAPPOOSS', "'") for word in title_words]
        # Get rid of -- and '' (this can really happen...)
        title_words = [word.replace('--', '') for word in title_words]
        title_words = [word.replace("''", '') for word in title_words]
        # and finally remove any blank "words"
        title_words = [word.strip() for word in title_words if not word == '']

        for word in title_words:
            spelling = spellchecker(word)
            if spelling[0][1] == None:
                continue
            elif spelling[0][1] == ['']:
                log.write("spelling, no suggestions: %s\n" % word)
                status += " spelling (%s)" % word
            else:
                log.write("spelling: %s. Possible corrections: %s\n" % (word, spelling[0][1]))
                status += " spelling (%s)" % word

    if status is not '':
        print '%s %s' % (filename, status)
