#!/usr/bin/env python2.7
# coding=utf-8

import os
import sys
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import collections
import lxml.etree as ET
import time
import datetime

from copy import deepcopy
from StringIO import StringIO

from commonUtils.fileUtils import locate, buildLut, buildListLut
from filmtransformfunc import levxml, levorder
from datetool.dateparser import parser as dateparser
from datetool.dateparser import ParserError


fieldlookup = buildListLut('legtolev-fields.lut')
rolelookup = buildLut('afi-roles.lut')
rolecorr = buildLut('afi_role_abbr.lut')

format1 = {'MUSIC_TEXT': 'production_music', 'SONG_TEXT': 'production_songs', 'SOURCE_TEXT': 'source_text'}

contriborder = collections.OrderedDict([('CAST', ''),
                                        ('PRODUCTION_COMPANY', ''),
                                        ('PRODUCER', ''),
                                        ('DIRECTOR', ''),
                                        ('WRITER', ''),
                                        ('SOURCE_AUTHOR', ''),
                                        ('DISTRIBUTION_COMPANY', ''),
                                        ('PHOTOGRAPHY', ''),
                                        ('ART_DIRECTOR', ''),
                                        ('FILE_EDITOR', ''),
                                        ('SET_DECORATOR', ''),
                                        ('COSTUMES', ''),
                                        ('MUSIC', ''),
                                        ('SOUND', ''),
                                        ('SPECIAL_EFFECTS', ''),
                                        ('DANCE', ''),
                                        ('MAKEUP', ''),
                                        ('PRODUCTION_MISC', ''),
                                        ('STAND_INS', ''),
                                        ('ANIMATION', ''),
                                        ('COLOR', '')])
contrbnotes = ['INTRODUCTORY_STATEMENT', 'PARENT_CO', 'CHARACTER_NAME', 'COMMENTS_AFTER_NAME', 'OFF_SCREEN_CREDIT', 'PN_OFFSCREEN', 'CHAR_OFFSCREEN', 'PNCHAR_OFFSCREEN']
contenttypes = {'afi': 'film'}
roledcrew = {'Director': 'Director',
             'Production': 'Producer',
             'Cast': 'Cast',
             'ProductionCompany': 'ProductionCompany'}
tags_to_role = {
    'CAST': 'Cast',
    'PRODUCTION_COMPANY': 'ProductionCompany',
    'PRODUCER': 'Producer',
    'DIRECTOR': 'Director'
}
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
namesindex = {}

badrecs = []
reccount = 0

product = 'afi'

try:
    indir = sys.argv[1]
    outdir = sys.argv[2]
except IndexError:
    print "Usage: %s {indirectory} {output directory}\nMaybe one of these is missing from your command?" % __file__
    exit()


def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        return '\033[93mWarning:\033[0m encountered an invalid date %s' % date_text


def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = re.sub(i, j, text)
    return text


def text_or_default(element):
    """Return the text from an element or a blank string"""
    if element is not None:
        return element.text
    return ''


def true_element_test(element):
    if element is not None:
        return element.text == '1' or element.text == 'true'
    return False

## Refactoring idea - base the script around what you're trying to build, rather than what's in the data; e.g have a section for subjects, 1-1 fields, contribs etc.


def afitransform(data):

    # AFI have started adding br tagging, needs to be stripped
    for element in data.iter():
        if element.text and '<br/>' in element.text:
            element.text = element.text.replace('<br/>', '')

    datedict = {}
    lengthlist = []

    document = levxml(data, contenttypes[product], 'legtolev-fields.lut')
    document.attrib['delbatch'] = '2015_3'

    parent = document.xpath('/document/record/film')
    if len(document.xpath('/document/record/film/production_details')) is not 0:
        prod_details = document.find('.//production_details')
    else:
        prod_details = ET.SubElement(parent[0], 'production_details')

    doctypes = ET.SubElement(parent[0], 'doctypes')
    ET.SubElement(doctypes, 'doctype1').text = 'Film'
    docid = document.xpath('.//docid')[0].text


    for element in data:
        if element.text is not None:


            if element.tag == "TITLE":
                ET.SubElement(parent[0], 'title').text = element.text
                if len(document.xpath('/document/record/film/subjects')) != 0:
                    subjects = document.find('.//subjects')
                else:
                    subjects = ET.SubElement(parent[0], 'subjects')
                ET.SubElement(subjects, 'subject', type="production").text = element.text

            if element.tag == "RELEASE_DAY":
                if element.text == '0':
                    pass
                else:
                    if re.match('^[1-9]$', element.text):
                        datedict['day'] = '0%s' % element.text
                    else:
                        datedict['day'] = element.text
                    datedict['normday'] = element.text
            if element.tag == "RELEASE_MONTH":
                if element.text == '0':
                    pass
                elif re.match('^[1-9]$', element.text):
                    datedict['month'] = '0%s' % element.text
                else:
                    datedict['month'] = element.text
            if element.tag == "RELEASE_YEAR":
                if element.text == '0':
                    pass
                else:
                    datedict['year'] = element.text

            if element.tag == "PRINT_VIEWED_BY_AFI":
                if true_element_test(element):
                    notes = ET.SubElement(parent[0], 'notes')
                    ET.SubElement(notes, 'note', type="Editorial").text = "Viewed by AFI"

            if element.tag == "LENGTH_FT":
                lengthlist.append('%s feet' % element.text)
            if element.tag == "LENGTH_REEL":
                lengthlist.append('%s reels' % element.text)
            if element.tag == "MOVIE_LANGUAGE":
                languages = ET.SubElement(parent[0], 'languages')
                langs = re.split(' and |,', element.text)
                for lang in langs:
                    if lang is not '':
                        ET.SubElement(languages, 'language').text = lang.strip()

        elif element.tag == "MPAA":
            if element.find('.//DESCRIPTION') is not None and element.find('.//DESCRIPTION').text is not None:
                ET.SubElement(prod_details, 'mpaa_cert').text = element.find('.//DESCRIPTION').text
        elif element.tag == "SUBJECT":
            for gensubs in element.findall('.//RECORD'):
                mt = 'false'
                if true_element_test(gensubs.find('.//MAJOR_MINOR_CHECK')):
                    mt = 'true'
                ET.SubElement(subjects, 'subject', type="general", majortopic="%s" % mt).text = gensubs.find('.//DESCRIPTION').text

            # Sort the subjects alphabetically
            ingest_subjects = document.xpath('.//subject[@type="general"]')
            ingest_subjects = sorted(ingest_subjects, key=lambda x: x.text)

            for subject in document.xpath('.//subject[@type="general"]'):
                subject.getparent().remove(subject)
            subjects.extend(ingest_subjects)


        elif element.tag == "GEOGRAPHIC_LOCATION":
            for locations in element.findall('.//RECORD'):
                geoloc = collections.OrderedDict([('ADDITIONALLOCATIONINFO', ''), ('CITY', ''), ('STATE', ''), ('COUNTRY', '')])
                geolist = []
                for fields in locations:
                    if fields.tag in geoloc.keys() and fields.text is not None:
                        geoloc[fields.tag] = fields.text
                if len(document.xpath('/document/record/film/subjects')) != 0:
                    subjects = document.find('.//subjects')
                else:
                    subjects = ET.SubElement(parent[0], 'subjects')

                for key in geoloc.keys():
                    if geoloc[key] is not '':
                        geolist.append(geoloc[key])

                geotext = ' '.join(geolist)
                if geotext.strip():
                    ET.SubElement(subjects, 'subject', type="location").text = geotext.strip()

        elif element.tag == 'NOTE':
            if element.find('.//NOTE_TEXT') is not None and element.find('.//NOTE_TEXT').text is not None:
                if len(document.xpath('/document/record/film/notes')) != 0:
                    notes = document.find('.//notes')
                else:
                    notes = ET.SubElement(parent[0], 'notes')
                ET.SubElement(notes, 'note', type="Document").text = ET.CDATA(element.find('.//NOTE_TEXT').text)

        elif element.tag == 'PRODUCTION_QUALIFIER':
            proqual = collections.OrderedDict([('PRODUCTION_TEXT', ''), ('BRAND_NAME', '')])
            for recs in element.findall('.//RECORD'):
                proquallist = []
                for qualifiers in recs:
                    if qualifiers.text is not None and qualifiers.text.strip() is not None and qualifiers.tag in proqual.keys():
                        proqual[qualifiers.tag] = qualifiers.text
                for key in proqual.keys():
                    if proqual[key] is not '':
                        proquallist.append(proqual[key])
                ET.SubElement(prod_details, 'production_qualifiers').text = '; '.join(proquallist)

        elif element.tag in format1.keys():
            if element.find('.//%s' % element.tag) is not None and element.find('.//%s' % element.tag).text is not None and element.find('.//%s' % element.tag).text.strip() is not '':
                ET.SubElement(prod_details, format1[element.tag]).text = element.find('.//%s' % element.tag).text

        elif element.tag == 'SUMMARY':
            if element.find('.//SUMMARY_TEXT') is not None and element.find('.//SUMMARY_TEXT').text is not None:
                ET.SubElement(parent[0], 'synopsis').text = element.find('.//SUMMARY_TEXT').text

        elif element.tag == 'COPYRIGHT_DATA':
            for recs in element.findall('.//RECORD'):
                copy = collections.OrderedDict([('CLAIMANT', ''), ('COPYRIGHT_DAY', ''), ('COPYRIGHT_MONTH', ''), ('COPYRIGHT_YEAR', ''), ('COPYRIGHT_NO', '')])
                copyrightlist = []
                for copies in recs:
                    if copies.text is not None and copies.tag in copy.keys():
                        copy[copies.tag] = copies.text
                for key in copy.keys():
                    if key == 'COPYRIGHT_MONTH' and copy[key] is not '':
                        if re.match('^[0-9]$', copy[key]):
                            copy[key] = months['0%s' % copy[key]]
                        else:
                            copy[key] = months[copy[key]]
                    if copy[key] is not '':
                        copyrightlist.append(copy[key])
                ET.SubElement(prod_details, 'production_copyright').text = ' '.join(copyrightlist)

        elif element.tag == 'ALTERNATE_TITLE':
            for rec in element.findall('.//RECORD'):
                if rec.find('.//ALTERNATE_TITLE') is not None and rec.find('.//ALTERNATE_TITLE').text is not None:
                    ET.SubElement(parent[0], 'alternate_title').text = rec.find('.//ALTERNATE_TITLE').text
                    if len(document.xpath('/document/record/film/subjects')) != 0:
                        subjects = document.find('.//subjects')
                    else:
                        subjects = ET.SubElement(parent[0], 'subjects')
                    ET.SubElement(subjects, 'subject', type="production").text = rec.find('.//ALTERNATE_TITLE').text

        elif element.tag == 'PHYSICAL_PROPERTIES':
            for rec in element.findall('.//RECORD'):
                if rec.find('.//PHY_DES') is not None and rec.find('.//PHY_DES').text is not None:
                    if len(document.xpath('/document/record/film/notes')) != 0:
                        notes = document.find('.//notes')
                    else:
                        notes = ET.SubElement(parent[0], 'notes')
                    phydes = ET.SubElement(notes, 'note', type="PhysDesc")
                    phydes.text = replace_all(rec.find('.//PHY_DES').text, rolecorr)
                if rec.find('.//PROPERTY_DESCRIPTION') is not None and rec.find('.//PROPERTY_DESCRIPTION').text is not None:
                    phydes.text = '%s: %s' % (phydes.text, rec.find('.//PROPERTY_DESCRIPTION').text)

        elif element.tag == 'SOURCE_CITATIONS':
            for role in element.findall('.//ROLE/RECORD'):
                if len(document.xpath('/document/record/film/object_citations')) != 0:
                    object_citations = document.find('.//object_citations')
                else:
                    object_citations = ET.SubElement(parent[0], 'object_citations')
                object_citation = ET.SubElement(object_citations, 'object_citation')
                object_citation.attrib['citorder'] = role.find('.//SEQUENCE').text
                if role.find('./../DESCRIPTION') is not None and role.find('./../DESCRIPTION').text is not None:
                    ET.SubElement(object_citation, 'citation_source').text = role.find('./../DESCRIPTION').text
                else:
                    if role.find('.//OTHER_SOURCE') is not None and role.find('.//OTHER_SOURCE').text is not None:
                        ET.SubElement(object_citation, 'citation_source').text = role.find('.//OTHER_SOURCE').text
                if role.find('.//DATE_SOURCE_TEXT') is not None and role.find('.//DATE_SOURCE_TEXT').text is not None:
                    ET.SubElement(object_citation, 'citsource_date').text = role.find('.//DATE_SOURCE_TEXT').text
                if role.find('.//PAGE') is not None and role.find('.//PAGE').text is not None:
                    ET.SubElement(object_citation, 'citsource_pagination').text = role.find('.//PAGE').text
        elif element.tag == 'GENRES':
            for rec in element.findall('.//RECORD'):
                if document.find('.//production_genres') is not None:
                    prod_genres = document.find('.//production_genres')
                else:
                    prod_genres = ET.SubElement(prod_details, 'production_genres')
                ET.SubElement(prod_genres, 'genre').text = rec.find('.//GENRE_STND').text

        if element.tag in contriborder.keys():
            contriborder[element.tag] = element

    contribnum = 0

    for k in contriborder:
        if contriborder[k] is not '':
            for node in contriborder[k]:
                if node.find('COMPANY_NAME') is not None and node.find('COMPANY_NAME').text is None:
                    pass
                else:
                    contribnum += 1
                    contributor = ET.SubElement(parent[0], 'contributor')

                    fntext = text_or_default(node.find('FIRST_NAME'))
                    lntext = text_or_default(node.find('LAST_NAME'))
                    orgtext = text_or_default(node.find('COMPANY_NAME'))

                    if fntext:
                        ET.SubElement(contributor, 'firstname').text = fntext
                    if lntext:
                        ET.SubElement(contributor, 'lastname').text = lntext
                    if orgtext:
                        ET.SubElement(contributor, 'organisation_name').text = orgtext

                    nametocomp = '%s %s' % (fntext, lntext)
                    nametocomp = nametocomp.strip()
                    if not nametocomp:
                        nametocomp = orgtext

                    if node.find('.//PN_ID') is not None and node.find('.//PN_ID').text is not None:
                        if node.find('.//PN_ID').text in namesindex.keys():
                            for name in namesindex[node.find('.//PN_ID').text]:
                                try:
                                    if name.text.strip() == nametocomp.strip():
                                        pass
                                    else:
                                        ET.SubElement(contributor, 'altoriginalform').text = name.text.strip()

                                except AttributeError:
                                    print name, nametocomp, ET.tostring(node, pretty_print=True), namesindex[node.find('.//PN_ID').text]
                                    raise

                    for note in contrbnotes:
                        if node.find('.//%s' % note) is not None and node.find('.//%s' % note).text is not None and node.find('.//%s' % note).text is not '0':
                            if contributor.find('.//contributor_notes') is None:
                                contributor_notes = ET.SubElement(contributor, 'contributor_notes')

                    role = tags_to_role.get(k)
                    if not role:
                        role = 'Crew'

                    production_role_text = [i.text for i in node.xpath('.//DESCRIPTION|.//OTHER_ROLE_ID')]
                    production_role_text = [i for i in production_role_text if i and i != '0']
                    if production_role_text:
                        production_role_text = replace_all(production_role_text[0], rolecorr)

                    else:
                        production_role_text = k.title().replace('_', ' ')


                    if node.find('.//INTRODUCTORY_STATEMENT') is not None and node.find('.//INTRODUCTORY_STATEMENT').text is not None and node.find('.//INTRODUCTORY_STATEMENT').text.strip() is not '':
                        ET.SubElement(contributor_notes, 'introductory_text').text = node.find('.//INTRODUCTORY_STATEMENT').text.strip()
                    if node.find('.//PARENT_CO') is not None and node.find('.//PARENT_CO').text is not None and node.find('.//PARENT_CO').text.strip() is not '':
                        ET.SubElement(contributor_notes, 'parent_organisation').text = node.find('.//PARENT_CO').text
                    if node.find('.//CHARACTER_NAME') is not None and node.find('.//CHARACTER_NAME').text is not None and node.find('.//CHARACTER_NAME').text.strip() is not '':
                        ET.SubElement(contributor_notes, 'character_played').text = node.find('.//CHARACTER_NAME').text
                    if node.find('.//COMMENTS_AFTER_NAME') is not None and node.find('.//COMMENTS_AFTER_NAME').text is not None and node.find('.//COMMENTS_AFTER_NAME').text.strip() is not '':
                        ET.SubElement(contributor_notes, 'commentary_text').text = node.find('.//COMMENTS_AFTER_NAME').text
                    if true_element_test(node.find('.//OFF_SCREEN_CREDIT')) or true_element_test(node.find('.//PNCHAR_OFFSCREEN')):
                        ET.SubElement(contributor_notes, 'credit_note').text = '[Uncredited]'
                    if true_element_test(node.find('.//PN_OFFSCREEN')):
                        ET.SubElement(contributor_notes, 'credit_note').text = '[Actor uncredited]'
                    if true_element_test(node.find('.//CHAR_OFFSCREEN')):
                        ET.SubElement(contributor_notes, 'credit_note').text = '[Role uncredited]'

                    contributor.attrib['role'] = role
                    contributor.attrib['order'] = str(contribnum)

                    if role == 'Director' or role == 'Producer':
                        contribnum += 1
                        dupecontrib = deepcopy(contributor)
                        dupecontrib.attrib['role'] = 'Crew'
                        dupecontrib.attrib['order'] = str(contribnum)
                        dupe_contributor_notes = dupecontrib.find('.//contributor_notes')
                        if dupe_contributor_notes is None:
                            dupe_contributor_notes = ET.SubElement(dupecontrib, 'contributor_notes')
                        ET.SubElement(dupe_contributor_notes, 'production_role').text = production_role_text
                        parent[0].append(dupecontrib)
                    elif role == 'Crew':
                        contributor_notes = contributor.find('.//contributor_notes')
                        if contributor.find('.//contributor_notes') is None:
                            contributor_notes = ET.SubElement(contributor, 'contributor_notes')
                        ET.SubElement(contributor_notes, 'production_role').text = production_role_text

    for contrib_note in parent[0].xpath('.//contributor_notes'):
        if not len(contrib_note):
            contrib_note.getparent().remove(contrib_note)

    '''Assigning the date content correctly for Leviathan'''
    if 'month' not in datedict.keys():
        datedict['month'] = '00'
    if 'day' not in datedict.keys():
        datedict['day'] = '00'
    if 'normday' not in datedict.keys():
        datedict['normday'] = ''

    if datedict['normday'] is not '':
        datedict['normday'] = '%s, ' % datedict['normday']
    originaldate = '%s %s%s' % (months[datedict['month']], datedict['normday'], datedict['year'])
    pubdates = ET.SubElement(parent[0], 'pubdates')

    parsed_date = dateparser.parse(originaldate).start_date
    ET.SubElement(pubdates, 'originaldate').text = originaldate.strip()
    ET.SubElement(pubdates, 'numdate').text = '%s-%s-%s' % (parsed_date.normalised_numeric_date[0:4], parsed_date.normalised_numeric_date[4:6], parsed_date.normalised_numeric_date[6:8])

    for element in pubdates:
        if element.text == '0001-01-01' or element.text == 'Jan 1, 0001':
            element.attrib['undated'] = 'true'

    if validate(document.find('.//numdate').text) is not None:
        print '%s Record id: %s; must be fixed in data.' % (validate(document.find('.//numdate').text), document.find('.//docid').text)

    if len(lengthlist) is not 0:
        if len(document.xpath('/document/record/film/notes')) != 0:
            notes = document.find('.//notes')
        else:
            notes = ET.SubElement(parent[0], 'notes')
        ET.SubElement(notes, 'note', type="PhysDesc").text = ' '.join(lengthlist)

    '''Assigning individual contributors to the contributors parent element'''
    if parent[0].find('contributor') in parent[0]:
        contributors = ET.SubElement(parent[0], 'contributors')
        for element in parent[0]:
            if element.tag == 'contributor':
                contributors.append(element)

    '''Assigning vendor field, source institution, projectcode'''
    ET.SubElement(parent[0], 'vendor').text = product
    ET.SubElement(parent[0], 'sourceinstitution').text = product.upper()
    ET.SubElement(parent[0], 'projectcode').text = product

    # Assigning individual production_details to the productions parent element
    if parent[0].find('production_details'):
        productions = ET.SubElement(parent[0], 'productions')
        productions.extend(parent[0].xpath('.//production_details'))

    # Fixing nbr elements
    for nbr in parent[0].xpath('.//nbr'):
        if true_element_test(nbr):
            nbr.text = 'Passed by National Board of Review'
        else:
            nbr.getparent().remove(nbr)

    '''Assigning language if non assigned'''
    if len(document.xpath('/document/record/film/languages')) == 0:
        languages = ET.SubElement(parent[0], 'languages')
        ET.SubElement(languages, 'language').text = 'English'

    finaldoc = levorder(document, contenttypes[product])
    return finaldoc

print 'Creating index of names from NameIndex files...'

for f in locate('NameIndex*.xml', indir):
    ## FIXME - needs a test if no files are detected in here
    fs = StringIO(open(f, 'r').read())
    tree = ET.iterparse(fs, remove_blank_text=True)

    for _, record in tree:
        if record.tag == "PERSONAL_NAME":
            pnid = record.find('./ID').text
            names = [i for i in record.findall('.//FULL_NAME') if i.text != None]
            namesindex[pnid] = names

            nametest = [i.text for i in record.findall('.//FULL_NAME')]
            for i in nametest:
                if i == None:
                    print '\033[93mWarning:\033[0m Null value detected for person name record %s, file %s' % (pnid, f)

for f in locate('AFI*.xml', indir):
    recfilecount = 0
    fs = StringIO(open(f, 'r').read())
    tree = ET.iterparse(fs, remove_blank_text=True)

    '''Output directory structure for afi should be in the form staging_afi/afi0001/YYYYMMDD/record1.xml, record2.xml'''
    print 'Processing %s...' % f
    for _, record in tree:
        if record.tag == "MOVIE":
            # print record.find('.//MOVIE_ID').text
            year = record.find('RELEASE_YEAR').text
            path = '%s/afi0001/%s0101' % (outdir, year[0:4])
            if not os.path.exists(path):
                os.makedirs(path)
            rec = afitransform(record)
            reccount += 1
            recfilecount += 1
            outfname = '%s/AFI_%s_%s.xml' % (path, year, record.find('MOVIE_ID').text)
            with open(outfname, 'w') as out:
                out.write(ET.tostring(rec, pretty_print=True, ))
    print f, recfilecount

print 'Records created: %s' % reccount
