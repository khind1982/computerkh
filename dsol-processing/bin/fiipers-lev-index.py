#!/usr/bin/env python2.7
# coding=utf-8

import os
import sys
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import collections
import lxml.etree as ET
import HTMLParser
import time

from StringIO import StringIO

from commonUtils.fileUtils import locate, buildLut, buildListLut
from filmtransformfunc import levxml, levorder
from datetool.dateparser import parser as dateparser
from datetool.dateparser import ParserError

fiioutloc = '/dc/migrations/film/fii/data/processing/'
contenttypes = {'fiipers': 'biography'}
roledcrew = {'Director': 'Director',
             'Diredted by': 'Director',
             'Directed by': 'Director',
             'Director?': 'Director',
             'Producer': 'Producer',
             'Produced  by': 'Producer',
             'Produced By': 'Producer',
             'Produced by': 'Producer'}
months = {'01': 'January',
          '02': 'February',
          '03': 'March',
          '04': 'April',
          '05': 'May',
          '06': 'June',
          '07': 'July',
          '08': 'August',
          '09': 'September',
          '10': 'October',
          '11': 'November',
          '12': 'December',
          '00': ''}

filedict = {'peopleab.xml': 'A-B',
            'peopleae-f.xml': 'E-F',
            'peopleaw.xml':  'U-Z',
            'peopleam-1.xml': 'L-M',
            'peopleac.xml': 'C-D',
            'peopleag-h.xml': 'G-H',
            'peoplead.xml': 'C-D',
            'peopleam-2.xml': 'L-M',
            'peopleapqr.xml': 'P-R',
            'peopleaw-z.xml': 'U-Z',
            'peopleaa.xml': 'A-B',
            'peoplean-o.xml': 'N-O',
            'peopleai-k.xml': 'I-K',
            'peopleat.xml': 'S-T',
            'peopleas.xml': 'S-T',
            'testxmls2.xml': 'testout'}

try:
    product = sys.argv[1]
    indir = sys.argv[2]
    files = sys.argv[3]
except IndexError:
    print "Usage: %s {product} {indirectory} {file(s)}\nMaybe one of these is missing from your command?" % __file__
    exit()

reccount = 0


def cleanup(data):
    '''A function to clean up strings with unwanted whitespace'''
    strlst = []
    data = re.split(' |\n', data)
    for item in data:
        if item is not '':
            strlst.append(item)
    data = ' '.join(strlst)
    return data


def datescleanup(data):
    datelist = {}
    year = data[0:4]
    month = data[4:6]
    if month == '':
        month = '00'
    day = data[6:]

    if day == '00':
        normday = ''
    elif day == '':
        normday = ''
    elif day[0] == '0':
        normday = '%s, ' % day[1]
    else:
        normday = '%s, ' % day
    try:
        datelist['oridate'] = '%s %s%s' % (months[month], normday, year)
    except KeyError:
        print data
    datelist['numdate'] = '%s-%s-%s' % (year, month.replace('00', '01'), day.replace('00', '01'))
    return datelist


def fiipertransform(data):
    document = levxml(data, contenttypes[product], 'fiitolev-fields.lut')
    document.attrib['delbatch'] = '2015_3'

    parent = document.xpath('/document/record/biography')

    doctypes = ET.SubElement(parent[0], 'doctypes')
    ET.SubElement(doctypes, 'doctype1').text = 'Person'

    subjects = ET.SubElement(parent[0], 'subjects')

    refcount = 0

    if data.find('.//NAME') is not None and data.find('.//NAME').text is not None:
        ET.SubElement(parent[0], 'title').text = data.find('.//NAME').text.strip()
        ET.SubElement(subjects, 'subject', type="person").text = data.find('.//NAME').text.strip()
    else:
        print "Name unavaliable: %s" % data.find('.//PERSID').text

    for element in data:
        if element.tag == 'AWARDS':
            if parent[0].find('productions') in parent[0]:
                productions = parent[0].find('productions')
                production_details = productions.find('production_details')
            else:
                productions = ET.SubElement(parent[0], 'productions')
                production_details = ET.SubElement(productions, 'production_details')
            if production_details.find('awards') in production_details:
                awards = production_details.find('awards')
            else:
                awards = ET.SubElement(production_details, 'awards')
            award = ET.SubElement(awards, 'award')
            if element.find('.//AWDSER') is not None and element.find('.//AWDSER').text is not None:
                ET.SubElement(award, 'award_event').text = element.find('.//AWDSER').text
            if element.find('.//AWDYEAR') is not None and element.find('.//AWDYEAR').text is not None:
                ET.SubElement(award, 'award_year').text = element.find('.//AWDYEAR').text
            if element.find('.//AWDCAT') is not None and element.find('.//AWDCAT').text is not None:
                ET.SubElement(award, 'award_category').text = element.find('.//AWDCAT').text
            if element.find('.//TITLE') is not None and element.find('.//TITLE').text is not None:
                ET.SubElement(award, 'award_production').text = element.find('.//TITLE').text
        if element.tag == 'BIRTH':
            birth_details = ET.SubElement(parent[0], 'birth_details')
            if element.find('.//BDATE') is not None and element.find('.//BDATE').text is not None:
                ET.SubElement(birth_details, 'birthdate').text = element.find('.//BDATE').text
            if element.find('.//BTOWN') is not None and element.find('.//BTOWN').text is not None:
                ET.SubElement(birth_details, 'birthtown').text = element.find('.//BTOWN').text
            if element.find('.//BCOUNTRY') is not None and element.find('.//BCOUNTRY').text is not None:
                ET.SubElement(birth_details, 'birthcountry').text = element.find('.//BCOUNTRY').text
        if element.tag == 'DEATH':
            death_details = ET.SubElement(parent[0], 'death_details')
            if element.find('.//DDATE') is not None and element.find('.//DDATE').text is not None:
                ET.SubElement(death_details, 'deathdate').text = element.find('.//DDATE').text
            if element.find('.//DTOWN') is not None and element.find('.//DTOWN').text is not None:
                ET.SubElement(death_details, 'deathtown').text = element.find('.//DTOWN').text
            if element.find('.//DCOUNTRY') is not None and element.find('.//DCOUNTRY').text is not None:
                ET.SubElement(death_details, 'deathcountry').text = element.find('.//DCOUNTRY').text

        if element.tag == 'REFS':
            object_citationdict = collections.OrderedDict([('citation_title', ''),
                                                           ('citation_author', ''),
                                                           ('citation_notes', ''),
                                                           ('citation_issue', ''),
                                                           ('citation_volume', ''),
                                                           ('citation_illus', ''),
                                                           ('citation_source', ''),
                                                           ('citsource_date', ''),
                                                           ('citsource_pagination', ''),
                                                           ('citsource_lang', ''),
                                                           ('citsource_issn', '')])

            if parent[0].find('object_citations') in parent[0]:
                object_citations = parent[0].find('object_citations')
            else:
                object_citations = ET.SubElement(parent[0], 'object_citations')
            refcount += 1

            object_citation = ET.SubElement(object_citations, 'object_citation')
            object_citation.attrib['citorder'] = str(refcount)
            if element.find('.//ATITLE') is not None and element.find('.//ATITLE').text is not None:
                object_citationdict['citation_title'] = element.find('.//ATITLE').text
            if element.find('.//AUTHOR') is not None and element.find('.//AUTHOR').text is not None:
                object_citationdict['citation_author'] = element.find('.//AUTHOR').text
            if element.find('.//REFNOTES') is not None and element.find('.//REFNOTES').text is not None:
                object_citationdict['citation_notes'] = element.find('.//REFNOTES').text
            if element.find('.//ISSUE') is not None and element.find('.//ISSUE').text is not None:
                object_citationdict['citation_issue'] = element.find('.//ISSUE').text
            if element.find('.//ADATE') is not None and element.find('.//ADATE').text is not None:
                object_citationdict['citsource_date'] = element.find('.//ADATE').text
            if element.find('.//PAGES') is not None and element.find('.//PAGES').text is not None:
                object_citationdict['citsource_pagination'] = element.find('.//PAGES').text
            if element.find('.//JTITLE') is not None and element.find('.//JTITLE').text is not None:
                object_citationdict['citation_source'] = element.find('.//JTITLE').text
            if element.find('.//VOL') is not None and element.find('.//VOL').text is not None:
                object_citationdict['citation_volume'] = element.find('.//VOL').text
            if element.find('.//LANG') is not None and element.find('.//LANG').text is not None:
                object_citationdict['citsource_lang'] = element.find('.//LANG').text
            if element.find('.//ISSN') is not None and element.find('.//ISSN').text is not None:
                object_citationdict['citsource_issn'] = element.find('.//ISSN').text
            if element.find('.//ILLUS') is not None and element.find('.//ILLUS').text is not None:
                if element.find('.//ILLUS').text == 'Y':
                    object_citationdict['citation_illus'] = 'illus'
            for elementkey in object_citationdict.keys():
                if object_citationdict[elementkey] is not '':
                    ET.SubElement(object_citation, elementkey).text = object_citationdict[elementkey]

        if element.tag == 'KW':
            for node in element:
                if node.tag == 'NOTES':
                    if len(document.xpath('/document/record/film/notes')) != 0:
                        notes = document.find('.//notes')
                    else:
                        notes = ET.SubElement(parent[0], 'notes')
                    ET.SubElement(notes, 'note', type="Biography").text = cleanup(node.text)

        if element.tag == 'FILMLIST':
            if parent[0].find('productions') in parent[0]:
                productions = parent[0].find('productions')
            else:
                productions = ET.SubElement(parent[0], 'productions')
            films = element.findall('.//PFILM')
            for film in films:
                production_details = ET.SubElement(productions, 'production_details')
                if film.find('.//PTITLE') is not None and film.find('.//PTITLE').text is not None:
                    ET.SubElement(production_details, 'production_title').text = film.find('.//PTITLE').text
                    if parent[0].find('subjects') in parent[0]:
                        subjects = parent[0].find('subjects')
                    else:
                        subjects = ET.SubElement(parent[0], 'subjects')
                    ET.SubElement(subjects, 'subject', type="production").text = film.find('.//PTITLE').text
                if film.find('.//PYEAR') is not None and film.find('.//PYEAR').text is not None:
                    ET.SubElement(production_details, 'release_year').text = film.find('.//PYEAR').text
                if film.find('.//PCSTROLE') is not None and film.find('.//PCSTROLE').text is not None:
                    ET.SubElement(production_details, 'person_castrole').text = film.find('.//PCSTROLE').text
                if film.find('.//PCRDROLE') is not None and film.find('.//PCRDROLE').text is not None:
                    ET.SubElement(production_details, 'person_credrole').text = film.find('.//PCRDROLE').text

    '''Assigning language if not assigned'''
    if len(document.xpath('/document/record/film/languages')) == 0:
        languages = ET.SubElement(parent[0], 'languages')
        ET.SubElement(languages, 'language').text = 'English'

    '''Assigning pubdates'''
    pubdates = ET.SubElement(parent[0], 'pubdates')
    ET.SubElement(pubdates, 'originaldate', undated="true").text = 'Jan 1, 0001'
    ET.SubElement(pubdates, 'numdate', undated="true").text = '0001-01-01'

    '''Assigning vendor field, source institution, projectcode'''
    ET.SubElement(parent[0], 'vendor').text = 'bfi'
    ET.SubElement(parent[0], 'sourceinstitution').text = 'bfi'
    ET.SubElement(parent[0], 'projectcode').text = 'fiipers'

    finaldoc = levorder(document, contenttypes[product])
    # print ET.tostring(finaldoc, pretty_print=True)
    return finaldoc


for f in locate(files, indir):
    recfilecount = 0
    h = HTMLParser.HTMLParser()
    hs = StringIO('%s%s' % ('<?xml version="1.0" encoding="iso-latin-1"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "/home/cmoore/svn/trunk/cstore/gs4/libdata/dtds/xhtml/xhtml1-strict.dtd">', open(f, 'r').read()))
    tree = ET.iterparse(hs, load_dtd=True, huge_tree=True)

    '''Output directory structure for fii people should be in the form staging_fiipers/fii0002/Surname initial/record1.xml, record2.xml'''

    for _, record in tree:
        if record.tag == "RECORD":
            path = '/dc/migrations/film/fii/data/processing/staging_fiipers/fiibuild_%s/fii0002/%s/%s%s' % (time.strftime("%Y%m%d"), filedict[os.path.basename(f)], record.find('PERSID').text[-1], record.find('PERSID').text[-3])
            if not os.path.exists(path):
                os.makedirs(path)
            rec = fiipertransform(record)
            reccount += 1
            recfilecount += 1
            outfname = '%s/FII_PERS_%s.xml' % (path, record.find('PERSID').text)
            with open(outfname, 'w') as out:
                out.write(ET.tostring(rec, pretty_print=True, xml_declaration=True))

    print f, recfilecount

print 'Records created: %s' % reccount
