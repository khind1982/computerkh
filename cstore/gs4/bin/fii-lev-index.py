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
contenttypes = {'fii': 'film'}
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

soundcolsys = ['                    Sound',
               'Combined Magnetic Sound',
               'Combined Optical Sound',
               'Digital Stereo',
               'Dolby Digital Surround EX',
               'Dolby Digital',
               'Dolby SR',
               'Dolby Stereo SR',
               'Dolby',
               'DTS Sound (Optical)',
               'DTS',
               'Mono sound',
               'Mute',
               'Separate Magnetic Sound',
               'Silent',
               'Sound',
               'Stereo',
               'Surround Stereo',
               'Ultra-Stereo']

product = 'fii'

try:
    indir = sys.argv[1]
    outdir = sys.argv[2]
except IndexError:
    print "Usage: %s {indirectory} {output directory}\nMaybe one of these is missing from your command?" % __file__
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


def fiitransform(data):
    document = levxml(data, contenttypes[product], 'fiitolev-fields.lut')
    document.attrib['delbatch'] = '2015_3'

    parent = document.xpath('/document/record/film')

    doctypes = ET.SubElement(parent[0], 'doctypes')
    ET.SubElement(doctypes, 'doctype1').text = 'Film'

    subjects = ET.SubElement(parent[0], 'subjects')

    contribcount = 0
    refcount = 0

    if data.find('.//RELYEAR') is not None and data.find('.//RELYEAR').text is not None:
        pubdates = ET.SubElement(parent[0], 'pubdates')
        dates = datescleanup(data.find('.//RELYEAR').text)
        ET.SubElement(pubdates, 'originaldate').text = dates['oridate'].strip()
        ET.SubElement(pubdates, 'numdate').text = dates['numdate']
    else:
        if data.find('.//YEAR') is not None and data.find('.//YEAR').text is not None:
            pubdates = ET.SubElement(parent[0], 'pubdates')
            ET.SubElement(pubdates, 'originaldate').text = data.find('.//YEAR').text
            ET.SubElement(pubdates, 'numdate').text = '%s-01-01' % data.find('.//YEAR').text
        else:
            pubdates = ET.SubElement(parent[0], 'pubdates')
            ET.SubElement(pubdates, 'originaldate', undated="true").text = '0001'
            ET.SubElement(pubdates, 'numdate', undated="true").text = '0001-01-01'
    if data.find('.//TITLE') is not None and data.find('.//TITLE').text is not None:
        ET.SubElement(parent[0], 'title').text = data.find('.//TITLE').text.strip()
        ET.SubElement(subjects, 'subject', type="production").text = data.find('.//TITLE').text.strip()
    else:
        ET.SubElement(parent[0], 'title').text = '[Title not known]'

    for element in data:
        if element.tag == 'AWARD':
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
            if element.find('.//PERS') is not None and element.find('.//PERS').text is not None:
                ET.SubElement(award, 'award_recipient').text = element.find('.//PERS').text

        if element.tag == 'KW':
            for node in element:
                # if node.tag == 'TITLE':
                #     ET.SubElement(parent[0], 'title').text = node.text.strip()
                #     ET.SubElement(subjects, 'subject', type="production").text = node.text.strip()
                if node.tag == 'ALTTITLE':
                    if node.text == document.find('.//title').text:
                        pass
                    else:
                        ET.SubElement(parent[0], 'alternate_title').text = node.text.strip()
                        ET.SubElement(subjects, 'subject', type="production").text = node.text.strip()
                if node.tag == 'CTRY':
                    ET.SubElement(parent[0], 'country_of_production').text = node.text.strip()
                    ET.SubElement(subjects, 'subject', type="location").text = node.text.strip()
                if node.tag == 'SYNOPSIS' or node.tag == 'Synopsis':
                    ET.SubElement(parent[0], 'synopsis').text = cleanup(node.text)

                if node.tag == 'PRODCOMP':
                    contribcount += 1
                    contributor = ET.SubElement(parent[0], 'contributor')
                    contributor.attrib['role'] = 'ProductionCompany'
                    contributor.attrib['order'] = str(contribcount)
                    ET.SubElement(contributor, 'organisation_name').text = node.text

                if node.tag == 'NOTES':
                    if 'CAST' in node.text:
                        if node.find('.//CASTNAME') is not None or node.find('.//CASTROLE') is not None:
                            contribcount += 1
                            contributor = ET.SubElement(parent[0], 'contributor')
                            contributor.attrib['role'] = 'Cast'
                            contributor.attrib['order'] = str(contribcount)
                        if node.find('.//CASTNAME') is not None and node.find('.//CASTNAME').text is not None:
                            ET.SubElement(contributor, 'originalform').text = node.find('.//CASTNAME').text
                        else:
                            ET.SubElement(contributor, 'originalform').text = '[Name unknown]'
                        altnames = node.findall('.//ALTNMSTD')
                        if len(altnames) is not 0:
                            for item in altnames:
                                ET.SubElement(contributor, 'altoriginalform').text = item.text
                        if contributor.find('.//contributor_notes') is None:
                            contributor_notes = ET.SubElement(contributor, 'contributor_notes')
                        else:
                            contributor_notes = contributor.find('.//contributor_notes')
                        try:
                            if node.find('.//CASTROLE').text not in ['(*)', '.', '?', '[,]', '[.]', '[?]', '[]', ',', '[ ]', '[.?]']:
                                ET.SubElement(contributor_notes, 'character_played').text = node.find('.//CASTROLE').text
                        except AttributeError:
                            pass

                    if 'REFS' in node.text:
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
                        if node.find('.//ATITLE') is not None and node.find('.//ATITLE').text is not None:
                            object_citationdict['citation_title'] = node.find('.//ATITLE').text
                        if node.find('.//AUTHOR') is not None and node.find('.//AUTHOR').text is not None:
                            object_citationdict['citation_author'] = node.find('.//AUTHOR').text
                        if node.find('.//REFNOTES') is not None and node.find('.//REFNOTES').text is not None:
                            object_citationdict['citation_notes'] = node.find('.//REFNOTES').text
                        if node.find('.//ISSUE') is not None and node.find('.//ISSUE').text is not None:
                            object_citationdict['citation_issue'] = node.find('.//ISSUE').text
                        if node.find('.//ADATE') is not None and node.find('.//ADATE').text is not None:
                            object_citationdict['citsource_date'] = node.find('.//ADATE').text
                        if node.find('.//PAGES') is not None and node.find('.//PAGES').text is not None:
                            object_citationdict['citsource_pagination'] = node.find('.//PAGES').text
                        if node.find('.//JTITLE') is not None and node.find('.//JTITLE').text is not None:
                            object_citationdict['citation_source'] = node.find('.//JTITLE').text
                        if node.find('.//VOL') is not None and node.find('.//VOL').text is not None:
                            object_citationdict['citation_volume'] = node.find('.//VOL').text
                        if node.find('.//LANG') is not None and node.find('.//LANG').text is not None:
                            object_citationdict['citsource_lang'] = node.find('.//LANG').text
                        if node.find('.//ISSN') is not None and node.find('.//ISSN').text is not None:
                            object_citationdict['citsource_issn'] = node.find('.//ISSN').text
                        if node.find('.//ILLUS') is not None and node.find('.//ILLUS').text is not None:
                            if node.find('.//ILLUS').text == 'Y':
                                object_citationdict['citation_illus'] = 'illus'
                        for elementkey in object_citationdict.keys():
                            if object_citationdict[elementkey] is not '':
                                ET.SubElement(object_citation, elementkey).text = object_citationdict[elementkey]

                    if 'TECH' in node.text:
                        lengthlist = []
                        if parent[0].find('productions') in parent[0]:
                            productions = parent[0].find('productions')
                            production_details = productions.find('production_details')
                        else:
                            productions = ET.SubElement(parent[0], 'productions')
                            production_details = ET.SubElement(productions, 'production_details')
                        if node.find('.//RUNTIME') is not None and node.find('.//RUNTIME').text is not None:
                            ET.SubElement(production_details, 'duration').text = node.find('.//RUNTIME').text
                        if node.find('.//LENGTHF') is not None and node.find('.//LENGTHF').text is not None:
                            lengthlist.append('%s feet' % node.find('.//LENGTHF').text)
                        if node.find('.//LENGTHM') is not None and node.find('.//LENGTHM').text is not None:
                            lengthlist.append('%s m.' % node.find('.//LENGTHM').text)
                        if node.find('.//COLCODE') is not None and node.find('.//COLCODE').text is not None:
                            ET.SubElement(production_details, 'colcode').text = node.find('.//COLCODE').text
                        if node.find('.//COLSYS') is not None and node.find('.//COLSYS').text is not None:
                            if node.find('.//COLSYS').text in soundcolsys:
                                ET.SubElement(production_details, 'soundsys').text = node.find('.//COLSYS').text.strip()
                            else:
                                ET.SubElement(production_details, 'colsys').text = node.find('.//COLSYS').text
                        if len(lengthlist) is not 0:
                            if len(document.xpath('/document/record/film/notes')) != 0:
                                notes = document.find('.//notes')
                            else:
                                notes = ET.SubElement(parent[0], 'notes')
                            ET.SubElement(notes, 'note', type="PhysDesc").text = ' '.join(lengthlist)
                    if 'DATE' in node.text:
                        if parent[0].find('productions') in parent[0]:
                            productions = parent[0].find('productions')
                            production_details = productions.find('production_details')
                        else:
                            productions = ET.SubElement(parent[0], 'productions')
                            production_details = ET.SubElement(productions, 'production_details')
                        if node.find('.//PRODYEAR') is not None and node.find('.//PRODYEAR').text is not None:
                            dates = datescleanup(node.find('.//PRODYEAR').text)
                            ET.SubElement(production_details, 'production_dates').text = dates['oridate'].strip()
                        if node.find('.//COPYYEAR') is not None and node.find('.//COPYYEAR').text is not None:
                            dates = datescleanup(node.find('.//COPYYEAR').text)
                            ET.SubElement(production_details, 'production_crdate').text = dates['oridate'].strip()
                        if node.find('.//TRANYEAR') is not None and node.find('.//TRANYEAR').text is not None:
                            dates = datescleanup(node.find('.//TRANYEAR').text)
                            ET.SubElement(production_details, 'production_transdate').text = dates['oridate'].strip()

        if element.tag == 'CREDIT':
            contributor = ET.SubElement(parent[0], 'contributor')
            contribcount += 1
            contributor.attrib['order'] = str(contribcount)
            if element.find('.//CREDNAME') is not None:
                if element.find('.//CREDNAME').text is not None:
                    ET.SubElement(contributor, 'originalform').text = element.find('.//CREDNAME').text
                else:
                    ET.SubElement(contributor, 'originalform').text = '[Name unknown]'
            altnames = element.findall('.//ALTNMSTD')
            if len(altnames) is not 0:
                for item in altnames:
                    ET.SubElement(contributor, 'altoriginalform').text = item.text
            if element.find('.//CREDROLE') is not None and element.find('.//CREDROLE').text is not None:
                if element.find('.//CREDROLE').text in roledcrew.keys():
                    dupecontrib = ET.fromstring(ET.tostring(contributor))
                    dupecontrib.attrib['role'] = 'Crew'
                    contribcount += 1
                    dupecontrib.attrib['order'] = str(contribcount)
                    if dupecontrib.find('.//contributor_notes') is None:
                        contributor_notes = ET.SubElement(dupecontrib, 'contributor_notes')
                    else:
                        contributor_notes = dupecontrib.find('.//contributor_notes')
                    ET.SubElement(contributor_notes, 'production_role').text = element.find('.//CREDROLE').text
                    parent[0].append(dupecontrib)
                    contributor.attrib['role'] = roledcrew[element.find('.//CREDROLE').text]
                else:
                    contributor.attrib['role'] = 'Crew'
                    if contributor.find('.//contributor_notes') is None:
                        contributor_notes = ET.SubElement(contributor, 'contributor_notes')
                    else:
                        contributor_notes = contributor.find('.//contributor_notes')
                    ET.SubElement(contributor_notes, 'production_role').text = element.find('.//CREDROLE').text

    '''Assigning contributor fields to contributors parent'''
    if parent[0].find('contributor') in parent[0]:
        contributors = ET.SubElement(parent[0], 'contributors')
        for item in parent[0]:
            if item.tag == 'contributor':
                contributors.append(parent[0].find('contributor'))

    '''Assigning language if not assigned'''
    if len(document.xpath('/document/record/film/languages')) == 0:
        languages = ET.SubElement(parent[0], 'languages')
        ET.SubElement(languages, 'language').text = 'English'

    '''Assigning vendor field, source institution, projectcode'''
    ET.SubElement(parent[0], 'vendor').text = product
    ET.SubElement(parent[0], 'sourceinstitution').text = product.upper()
    ET.SubElement(parent[0], 'projectcode').text = 'fiifilm'

    finaldoc = levorder(document, contenttypes[product])
    # print ET.tostring(finaldoc, pretty_print=True)
    return finaldoc

for f in locate('*.xml', indir):
    recfilecount = 0
    h = HTMLParser.HTMLParser()
    hs = StringIO('%s%s' % ('<?xml version="1.0" encoding="iso-latin-1"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "/home/cmoore/svn/trunk/cstore/gs4/bin/xhtml1-strict.dtd">', open(f, 'r').read()))
    tree = ET.iterparse(hs, load_dtd=True, huge_tree=True)

    '''Output directory structure for fii should be in the form staging_fii/fii0001/YYYYMMDD/record1.xml, record2.xml'''

    for _, record in tree:
        if record.tag == "RECORD":
            if record.find('.//RELYEAR') is not None and record.find('.//RELYEAR').text is not None:
                year = '%s0101' % record.find('.//RELYEAR').text[0:4]
            elif record.find('.//VYEAR') is not None and record.find('.//VYEAR').text is not None:
                year = '%s0101' % record.find('.//VYEAR').text
            else:
                year = '00010101'
            path = '%s/fii0001/%s' % (outdir, year[0:4])
            if not os.path.exists(path):
                os.makedirs(path)
            rec = fiitransform(record)
            reccount += 1
            recfilecount += 1
            outfname = '%s/FII_%s_%s.xml' % (path, year[0:4], record.find('TITLEID').text)
            with open(outfname, 'w') as out:
                out.write(ET.tostring(rec, pretty_print=True, xml_declaration=True))

        sys.stdout.write('File: %s \033[92mNumber of records created:\033[0m %s\r' % (f, recfilecount))
        sys.stdout.flush()

    sys.stdout.flush()
    print 'File: %s \033[92mNumber of records created:\033[0m %s' % (f, recfilecount)

print '\nTotal records created: %s' % reccount
