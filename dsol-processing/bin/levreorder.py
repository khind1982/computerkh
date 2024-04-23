#!/usr/bin/env python2.7
# coding=utf-8

import os
import sys
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import collections
import lxml.etree as ET

from StringIO import StringIO

from commonUtils.fileUtils import locate, buildLut, buildListLut
from filmtransformfunc import levxml
from datetool.dateparser import parser as dateparser
from datetool.dateparser import ParserError

infile = sys.argv[1]


def levorder(data):
    document = ET.Element('document')
    record = ET.SubElement(document, 'record')
    journ = ET.SubElement(record, 'journal')

    levdict = collections.OrderedDict([('journalid', ''),
                                       ('srcid', ''),
                                       ('docid', ''),
                                       ('accnum', ''),
                                       ('supplement', ''),
                                       ('country_of_publication', ''),
                                       ('print_issn', ''),
                                       ('sectionheads', ''),
                                       ('title', ''),
                                       ('subhead', ''),
                                       ('doctypes', ''),
                                       ('docfeatures', ''),
                                       ('imagefeatures', ''),
                                       ('contributors', ''),
                                       ('subjects', ''),
                                       ('productions', ''),
                                       ('series', ''),
                                       ('volume', ''),
                                       ('issue', ''),
                                       ('pubdates', ''),
                                       ('pagination', ''),
                                       ('vendor', ''),
                                       ('sourceinstitution', ''),
                                       ('languages', ''),
                                       ('abstract', ''),
                                       ('scantype', '')])

    for element in data:
      if element.tag in levdict.keys():
        levdict[element.tag] = element

    for elementkey in levdict.keys():
      if levdict[elementkey] is not '':
        journ.append(levdict[elementkey])

    return document

fs = StringIO(open(infile, 'r').read())
tree = ET.parse(fs)
root = tree.getroot()
journal = root.find('.//journal')

print levorder(journal)

### This module needs to be extracted to film transform and need to figure out why journalid is not on separate line

