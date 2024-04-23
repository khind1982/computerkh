#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Script to output log and titlelists
# Remember to copy this over with an underscore!!!

import os
import re
import sys

sys.path.append('/packages/dsol/platform/lib')
sys.path.append('/packages/dsol/platform/libdata/eeb')
sys.path.append('/packages/dsol/opt/lib/python2.7/site-packages')

import lxml.etree as ET
import xlrd

from StringIO import StringIO
from commonUtils.fileUtils import locate, buildLut
from HTMLParser import HTMLParser

h = HTMLParser()

libraries = buildLut('/dc/eurobo/utils/libraries.lut')
countries = buildLut('/dc/eurobo/utils/country_codes_notags.lut')
languages = buildLut('/dc/eurobo/utils/langs_notags.lut')
collections = buildLut('/dc/eurobo/utils/collection_allrecs.lut')
prodlookup = buildLut('/dc/eurobo/utils/marc_utils/eeb-legid-goid.lut')


def file_to_list(input_f):
    with open(input_f) as inf:
        return [line.strip() for line in inf.readlines()]


female_author = file_to_list('/dc/eurobo/editorial/female_publishers/female_authors_lookup.txt')
female_printer = file_to_list('/dc/eurobo/editorial/female_publishers/female_printers_lookup.txt')


# Script enhancements:
# Add USTC enrichment check
# Add presenter link for titlelists? if published use product link else presenter?

try:
    indir = sys.argv[1]
    outputtype = sys.argv[2]
    outfile = sys.argv[3]
except IndexError:
    print "Usage: eeb-log_titles.py [input directory] [output type (titlelist, producttitles, pre-enrichment or log)] [output file] [options]\n"
    print "Options:\n-r 'Date received/released'\n-d 'Last updated'\n"
    exit(1)

acceptouts = ['titlelist', 'log', 'producttitles', 'pagecontents', 'enrichment_fix', 'pagenumbers', 'pre-enrichment']

if outputtype not in acceptouts:
    print "Usage: eeb-log_titles.py [input directory] [output type (titlelist, pre-enrichment or log)] [output file] [options]\nOutput type must be one of: titlelist, producttitles, log, pagecontents"
    exit(1)

# Import the OptionParser and define options, which the user calls with switches on the command line:

from optparse import OptionParser

parsey = OptionParser()
parsey.add_option("-r", "--recvd", dest="deliverydate", help="Delivery Date", metavar="STRING")
parsey.add_option("-d", "--updated", dest="lastupdated", help="Last Update", metavar="STRING")
(options, args) = parsey.parse_args()

parser = ET.XMLParser(remove_blank_text=True)

'''Title list output type
PQID	Unit    Library	Title	Author  Other author	Pubdate	Imprint	Shelfmark	Country	Language	Subject Classification	Link Pages
'''

'''Incoming log output type
Delivery Date   PQID    Pages   Library	Title	Author	Pubdate	Imprint Shelfmark	Country Language    Location

'''
'''Pre-enrichment output type
PQID	Unit    Library	Title	Author  Other author    Pubdate Imprint Publisher   Shelfmark   Country Language    Location    Subject Classification  Link    Pages
'''

outls = []
if outputtype == 'titlelist':
    outls.append('PQID\tCollection\tLibrary\tTitle\tAuthor\tOther Authors\tPubdate\tImprint\tShelfmark\tCountry\tLanguage\tSubject\tUSTC Classification 1\tUSTC Classification 2\tUSTC Classification 3\tPages\tiNumber\tbNumber\tLink\tRelease Date\n')
if outputtype == 'producttitles':
    outls.append('PQID\tSource Library\tTitle\tAuthor\tDate of publication\tPublisher printer\tShelfmark\tCountry of publication\tLanguage\tUSTC classification\tLink\tDate Added\tLast Updated\n')
if outputtype == 'pre-enrichment':
    outls.append('PQID\tCollection\tLibrary\tTitle\tAlt_title\tAuthor\tOther Authors\tPubdate\tImprint\tPublisher printer\tShelfmark\tCountry of publication\tPlace of publication\tLanguage\tSubject\tpages\tUSTC Classifications\tPagination\tBibliographic reference\tUSTC_bibliographic reference\tContent notes\tGeneral Notet\tEdition note\tSection note\tIncipit notes\tExplicit note\tObservations\tPage detail note\tLink\tFemale author\tFemale printer\n')
    outfile = '/dc/eurobo/editorial/title_lists/%s' % os.path.basename(sys.argv[3])

pqidcheck = []
contentswewant = ['Chart', 'Coat of arms', 'Genealogical table', 'Illustration', 'Map', 'Musical notation', 'Plate', 'Plan', 'Portrait']

def presenceTestSingle(element):
    if element is not None and element.text is not None:
        return element.text
    else:
        return ''

def modsdata(datafile):
    logdict = {}
    if options.deliverydate:
        logdict['deliverydate'] = options.deliverydate
    else:
        logdict['deliverydate'] = datafile.split('/')[4]

    root = ET.parse(datafile).getroot()

    dmdrec = root.find('.//{*}dmdSec') # assumption that the first dmdSec in the record is the print record

    logdict['pqid'] = presenceTestSingle(dmdrec.find('.//{*}recordIdentifier')).replace('.xml', '')

    if logdict['pqid'] == '':
        logdict['pqid'] = os.path.basename(datafile).replace('.xml', '')

    logdict['bookid'] = logdict['pqid'][0:-4]

    logdict['department'] = logdict['pqid'].split('-')[2]

    logdict['unit'] = presenceTestSingle(root.find('.//unit'))

    # Setting the status
    if logdict['pqid'] in collections.keys():
        logdict['status'] = 'Published: %s' % collections[logdict['pqid']]
    elif os.path.basename(f).replace('.xml', '') in collections.keys():
        logdict['status'] = 'Published: %s' % collections[os.path.basename(datafile).replace('.xml', '')]
    else:
        logdict['status'] = 'Unpublished'

    librarycode = os.path.basename(datafile).split('-')[1]

    logdict['library'] = libraries[librarycode].decode('latin-1').encode('utf-8')

    logdict['title'] = presenceTestSingle(dmdrec.find('.//{*}title')).encode('utf-8')

    # try:
    logdict['author'] = ' ; '.join([i.find('../../{*}namePart').text.encode('utf-8') for i in dmdrec.findall('.//{*}roleTerm') if i.text == 'mainauthor' and i.find('../../{*}namePart').text is not None])
    if logdict['author'] == '':
        try:
            logdict['author'] = [i.find('../../{*}namePart').text.encode('utf-8') for i in dmdrec.findall('.//{*}roleTerm') if i.text == 'author' or i.text == 'otherauthor'][0]
        except IndexError:
            logdict['author'] == ''

    otherauthors = [i.find('../../{*}namePart').text.encode('utf-8') for i in dmdrec.findall('.//{*}roleTerm') if i.find('../../{*}namePart').text is not None and i.find('../../{*}namePart').text not in logdict['author'].decode('utf-8') and i.text == 'otherauthor']
    roleauthors = [i.find('../../{*}namePart').text.encode('utf-8') for i in dmdrec.findall('.//{*}roleTerm') if i.find('../../{*}namePart').text is not None and i.find('../../{*}namePart').text not in logdict['author'].decode('utf-8') and i.text == 'author']

    logdict['otherauthor'] = ' ; '.join(otherauthors + roleauthors)

    # pages
    if not datafile.endswith('-001.xml'):
        pages = [i for i in root.findall('.//{*}objectIdentifierValue') if i.text.endswith('.jp2') and i.text.split('-')[4] != '000']
    else:
        pages = [i for i in root.findall('.//{*}objectIdentifierValue') if i.text.endswith('.jp2')]

    logdict['pages'] = len(pages)

    # pubdate
    logdict['pubdate'] = presenceTestSingle(dmdrec.find('.//{*}dateIssued')).encode('utf-8')

    # incunabula finding
    try:
        if int(logdict['pubdate']) < 1500:
            logdict['incunabula'] = 'x'
        else:
            logdict['incunabula'] = ''
    except ValueError:
        logdict['incunabula'] = ''

    # imprint finding
    try:
        logdict['imprint'] = [i.text.replace('IMPRINT: ', '').encode('utf-8') for i in dmdrec.findall('.//{*}note') if 'IMPRINT: ' in i.text][0]
    except IndexError:
        logdict['imprint'] = ''

    logdict['publisher'] = presenceTestSingle(dmdrec.find('.//{*}publisher'))

    try:
        logdict['shelfmark'] = [i.text.replace('SHELFMARK: ', '').encode('utf-8') for i in dmdrec.findall('.//{*}physicalLocation') if 'SHELFMARK: ' in i.text][0]
    except IndexError:
        try:
            logdict['shelfmark'] = [i.text.encode('utf-8') for i in dmdrec.findall('.//{*}identifier') if i.get('type') == 'coteoriginal'][0]
        except IndexError:
            logdict['shelfmark'] = ''

    logdict['countrycode'] = '|'.join([i.text.replace('COUNTRY:', '') for i in dmdrec.findall('.//{*}placeTerm') if i.text != None and 'COUNTRY:' in i.text])

    try:
        logdict['country'] = '|'.join([countries[i.text.replace('COUNTRY:', '')] for i in dmdrec.findall('.//{*}placeTerm') if i.text != None and 'COUNTRY:' in i.text])
    except KeyError:
        logdict['country'] = '|'.join([i.text.replace('COUNTRY:', '') for i in dmdrec.findall('.//{*}placeTerm') if i.text != None and 'COUNTRY:' in i.text])

    try:
        logdict['language'] = '|'.join([languages[i.text] for i in dmdrec.findall('.//{*}languageTerm')])
    except KeyError:
        logdict['language'] = '|'.join([i.text for i in dmdrec.findall('.//{*}languageTerm')])
    except AttributeError:
        logdict['language'] = ''

    # subject
    logdict['subject'] = '|'.join([i.text.encode('utf-8') for i in dmdrec.findall('.//{*}topic') if i.text != None])

    # ustc classification
    logdict['classification'] = '|'.join([i.text for i in dmdrec.findall('.//classification1') if i.text != None])


    # link
    logdict['link'] = 'http://gateway.proquest.com/openurl?url_ver=Z39.88-2004&res_dat=xri:eurobo:&rft_dat=xri:eurobo:rec:%s' % logdict['pqid']

    # logdict['present'] = 'http://presenter.private.chadwyck.co.uk/wellcome3/Presenter/Delivery9-hin-wel-all-00000195.html'

    # location
    logdict['location'] = os.path.abspath(datafile)

    # repeat delivery
    if logdict['pqid'] in pqidls:
        logdict['repeat'] = 'Y'
    else:
        logdict ['repeat'] = ''

    if options.deliverydate:
        logdict['release'] = options.deliverydate
    else:
        logdict['release'] = ''

    if librarycode == 'wel':
        iandb = dmdrec.find('.//{*}recordContentSource').text.split('|')
        logdict['inumber'] = ''.join([i for i in iandb if 'i' in i])
        logdict['bnumber'] = ''.join([i for i in iandb if 'b' in i])
    else:
        logdict['inumber'] = ''
        logdict['bnumber'] = ''

    return logdict

def handoverdata(datafile, prodlookup):
    logdict = {}
    if options.deliverydate:
        logdict['deliverydate'] = options.deliverydate
    else:
        logdict['deliverydate'] = ''

    if options.lastupdated:
        logdict['lastupdated'] = options.lastupdated
    else:
        logdict['lastupdated'] = ''

    root = ET.parse(datafile).getroot()
    dmdrec = root.find('.//rec_search')

    logdict['pqid'] = presenceTestSingle(root.find('.//itemid'))

    if logdict['pqid'] == '':
        logdict['pqid'] = os.path.basename(datafile).replace('.xml', '')

    if logdict['pqid'] in female_author:
        logdict['female_author'] = "Female_author"
    else:
        logdict['female_author'] = ''

    if logdict['pqid'] in female_printer:
        logdict['female_printer'] = "Female_printer"
    else:
        logdict['female_printer'] = ''

    logdict['bookid'] = logdict['pqid'][0:-4]

    logdict['department'] = logdict['pqid'].split('-')[2]

    # Setting the status
    if logdict['pqid'] in collections.keys():
        logdict['status'] = 'Published: %s' % collections[logdict['pqid']]
    elif os.path.basename(f).replace('.xml', '') in collections.keys():
        logdict['status'] = 'Published: %s' % collections[os.path.basename(datafile).replace('.xml', '')]
    else:
        logdict['status'] = 'Unpublished (Processed)'

    logdict['unit'] = presenceTestSingle(root.find('.//unit'))
    logdict['library'] = libraries[os.path.basename(datafile).split('-')[1]].decode('latin-1').encode('utf-8')
    logdict['title'] = presenceTestSingle(dmdrec.find('.//title')).encode('utf-8')

    logdict['author'] = presenceTestSingle(dmdrec.find('.//author_main/author_corrected')).encode('utf-8')
    if logdict['author'] == '':
        logdict['author'] == presenceTestSingle(dmdrec.find('.//author_main/author_name'))

    logdict['viaf'] = presenceTestSingle(dmdrec.find('.//author_main/author_viaf')).encode('utf-8')

    if not datafile.endswith('-001.xml'):
        logdict['pages'] = len([i for i in root.findall('.//itemimagefile1') if i.text.split('-')[4] != '000'])
    else:
        logdict['pages'] = len([i for i in root.findall('.//itemimagefile1')])

    logdict['pubdate'] = presenceTestSingle(dmdrec.find('.//displaydate')).encode('utf-8')

    # incunabula finding
    try:
        if int(logdict['pubdate']) < 1500:
            logdict['incunabula'] = 'x'
        else:
            logdict['incunabula'] = ''
    except ValueError:
        logdict['incunabula'] = ''

    logdict['imprint'] = presenceTestSingle(dmdrec.find('.//imprint')).encode('utf-8')
    logdict['publisher'] = '|'.join([i.text for i in dmdrec.findall('.//publisher_printer') if i.text is not None]).encode('utf-8')
    logdict['shelfmark'] = presenceTestSingle(dmdrec.find('.//shelfmark')).encode('utf-8')
    logdict['countrycode'] = ''
    logdict['country'] = '|'.join([i.text for i in dmdrec.findall('.//country_of_publication') if i.text is not None]).encode('utf-8')
    logdict['pop'] = '|'.join([i.text for i in dmdrec.findall('.//place_of_publication') if i.text is not None]).encode('utf-8')
    logdict['language'] = '|'.join([i.text for i in dmdrec.findall('.//language')])
    logdict['subject'] = '|'.join([i.text for i in dmdrec.findall('.//subject') if i.text != None]).encode('utf-8')
    logdict['classification'] = '|'.join([i.text for i in dmdrec.findall('.//classification1') if i.text != None])
    logdict['otherauthor'] = '|'.join([i.text for i in dmdrec.findall('.//author_other/author_corrected') if i.text != None]).encode('utf-8')
    logdict['bibliographic_reference'] = '|'.join([i.text for i in dmdrec.findall('.//bibliographic_reference') if i.text != None])
    logdict['content_note'] = '|'.join([i.text for i in dmdrec.findall('.//content_note') if i.text != None]).encode('utf-8')
    logdict['alt_title'] = '|'.join([i.text for i in dmdrec.findall('.//alt_title') if i.text != None]).encode('utf-8')
    logdict['collection'] = '|'.join([i.text for i in dmdrec.findall('./subscription/unit') if i.text != None])
    logdict['pagination'] = '|'.join([i.text for i in dmdrec.findall('.//pagination') if i.text != None])
    logdict['general_note'] = '|'.join([i.text for i in dmdrec.findall('.//general_note') if i.text != None]).encode('utf-8')
    logdict['edition_note'] = '|'.join([i.text for i in dmdrec.findall('.//edition_note') if i.text != None]).encode('utf-8')
    logdict['section_note'] = '|'.join([i.text for i in dmdrec.findall('.//section_note') if i.text != None]).encode('utf-8')
    logdict['page_detail_note'] = '|'.join([i.text for i in dmdrec.findall('.//page_detail_note') if i.text != None]).encode('utf-8')
    logdict['incipit_note'] = '|'.join([i.text for i in dmdrec.findall('.//incipit') if i.text != None]).encode('utf-8')
    logdict['explicit_note'] = '|'.join([i.text for i in dmdrec.findall('.//explicit') if i.text != None]).encode('utf-8')
    logdict['ustc_bibliographic_reference'] = '|'.join([i.text for i in dmdrec.findall('.//ustc_bibliographic_reference') if i.text != None])
    logdict['observations'] = '|'.join([i.text for i in dmdrec.findall('.//commentcode') if i.text != None]).encode('utf-8')

    if fetchGoid(logdict['pqid'], prodlookup) is not None:
        logdict['link'] = 'https://search.proquest.com/docview/%s' % (fetchGoid(logdict['pqid'], prodlookup))
    else:
        logdict['link'] = ''
    logdict['location'] = ''

    # repeat delivery
    if logdict['pqid'] in pqidls:
        logdict['repeat'] = 'Y'
    else:
        logdict ['repeat'] = ''

    if options.deliverydate:
        logdict['release'] = options.deliverydate
    else:
        logdict['release'] = ''

    if options.lastupdated:
        logdict['lastupdated'] = options.lastupdated
    else:
        logdict['lastupdated'] = ''

    # image info - durl syntax is http://gateway.proquest.com/openurl?url_ver=Z39.88-2004&res_dat=xri:eurobo:&rft_dat=xri:eurobo:jpeg:ned-kbn-all-00000062-001:14
    # http://eeb.chadwyck.co.uk/search/displayImageItemFromId.do?FormatType=fulltextimages&ItemID=ned-kbn-all-00000062-001&ImageNumber=14&DurUrl=Yes
    logdict['pagecontent'] = {}
    for image in root.findall('.//itemimage'):
        pcontent = "|".join([i.text for i in image.findall('.//pagecontent') if i.text in contentswewant])
        if pcontent != '':
            name = image.find('.//itemimagefile1').text
            number = image.find('.//imagenumber').text
            pagelink = "http://eeb.chadwyck.co.uk/search/displayImageItemFromId.do?FormatType=fulltextimages&ItemID=%s&ImageNumber=%s&DurUrl=Yes" % (logdict['pqid'], number)
            logdict['pagecontent'][name] = pcontent, pagelink

    logdict['inumber'] = ''
    logdict['bnumber'] = ''

    return logdict

# Function to match the docid being processed with its corresponding goid.
def fetchGoid(docid, prodlookup):
    for legacyid,goid in prodlookup.items():
        if 'eeb-%s' % (docid) == legacyid:
            return goid
            break

# detecting previous deliveries

def processing(f, prodlookup):
    # detecting input type:
    print "Processing file called %s..." % (f)
    if ET.parse(f).getroot().tag != 'rec':
        log = modsdata(f)
    else:
        log = handoverdata(f, prodlookup)

    if outputtype == 'producttitles':
        outls.append('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (log['pqid'],
                                                                        log['library'].decode('utf-8'),
                                                                        log['title'].decode('utf-8'),
                                                                        log['author'].decode('utf-8'),
                                                                        log['pubdate'].decode('utf-8'),
                                                                        log['publisher'].decode('utf-8'),
                                                                        log['shelfmark'].decode('utf-8'),
                                                                        log['country'].decode('utf-8'),
                                                                        log['language'].decode('utf-8'),
                                                                        log['classification'],
                                                                        log['link'],
                                                                        log['release'],
                                                                        log['lastupdated']))

    if outputtype == 'titlelist':
        outls.append('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t\t\t%s\t%s\t%s\t%s\t%s\n' % (log['pqid'],
                                                                                           log['unit'],
                                                                                           log['library'].decode('utf-8'),
                                                                                           log['title'].decode('utf-8'),
                                                                                           log['author'].decode('utf-8'),
                                                                                           log['otherauthor'].decode('utf-8'),
                                                                                           log['pubdate'].decode('utf-8'),
                                                                                           log['imprint'].decode('utf-8'),
                                                                                           log['shelfmark'].decode('utf-8'),
                                                                                           log['country'].decode('utf-8'),
                                                                                           log['language'].decode('utf-8'),
                                                                                           log['subject'].decode('utf-8'),
                                                                                           log['classification'],
                                                                                           log['pages'],
                                                                                           log['inumber'],
                                                                                           log['bnumber'],
                                                                                           log['link'],
                                                                                           log['release']))
    if outputtype == 'log':
        outls.append('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (log['deliverydate'],
                                                                                            log['location'],
                                                                                            log['bookid'],
                                                                                            log['department'],
                                                                                            log['pqid'],
                                                                                            log['status'],
                                                                                            log['library'].decode('utf-8'),
                                                                                            log['title'].decode('utf-8'),
                                                                                            log['author'].decode('utf-8'),
                                                                                            log['pubdate'].decode('utf-8'),
                                                                                            log['incunabula'],
                                                                                            log['imprint'].decode('utf-8'),
                                                                                            log['shelfmark'].decode('utf-8'),
                                                                                            log['country'].decode('utf-8'),
                                                                                            log['countrycode'],
                                                                                            log['language'].decode('utf-8'),
                                                                                            log['subject'].decode('utf-8'),
                                                                                            log['pages'],
                                                                                            log['repeat'],
                                                                                            log['classification'].decode('utf-8')))

    if outputtype == 'enrichment_fix':
        outls.append('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (log['pqid'],
                                                                               log['unit'],
                                                                               log['library'].decode('utf-8'),
                                                                               log['title'].decode('utf-8'),
                                                                               log['author'].decode('utf-8'),
                                                                               log['viaf'].decode('utf-8'),
                                                                               log['pubdate'].decode('utf-8'),
                                                                               log['imprint'].decode('utf-8'),
                                                                               log['publisher'].decode('utf-8'),
                                                                               log['shelfmark'].decode('utf-8'),
                                                                               log['pop'].decode('utf-8'),
                                                                               log['country'].decode('utf-8'),
                                                                               log['language'].decode('utf-8'),
                                                                               log['classification'].decode('utf-8')))

    if outputtype == 'pre-enrichment':
        outls.append('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (log['pqid'],
                                                                                            log['unit'],
                                                                                            log['library'].decode('utf-8'),
                                                                                            log['title'].decode('utf-8'),
                                                                                            log['alt_title'].decode('utf-8'),
                                                                                            log['author'].decode('utf-8'),
                                                                                            log['otherauthor'].decode('utf-8'),
                                                                                            log['pubdate'].decode('utf-8'),
                                                                                            log['imprint'].decode('utf-8'),
                                                                                            log['publisher'].decode('utf-8'),
                                                                                            log['shelfmark'].decode('utf-8'),
                                                                                            log['country'].decode('utf-8'),
                                                                                            log['pop'].decode('utf-8'),
                                                                                            log['language'].decode('utf-8'),
                                                                                            log['subject'].decode('utf-8'),
                                                                                            log['pages'],
                                                                                            log['classification'].decode('utf-8'),
                                                                                            log['pagination'],
                                                                                            log['bibliographic_reference'],
                                                                                            log['ustc_bibliographic_reference'],
                                                                                            log['content_note'].decode('utf-8'),
                                                                                            log['general_note'].decode('utf-8'),
                                                                                            log['edition_note'].decode('utf-8'),
                                                                                            log['section_note'].decode('utf-8'),
                                                                                            log['incipit_note'].decode('utf-8'),
                                                                                            log['explicit_note'].decode('utf-8'),
                                                                                            log['observations'].decode('utf-8'),
                                                                                            log['page_detail_note'].decode('utf-8'),
                                                                                            log['link']))


    if outputtype == 'pagecontents':
        #append unit, page, content, link
        for k in log['pagecontent']:
            outls.append('%s\t%s\t%s\t%s\n' % (log['unit'], k, log['pagecontent'][k][0], log['pagecontent'][k][1]))

    if outputtype == 'pagenumbers':
        outls.append('%s|%s\t%s\n' % (log['pqid'], log['pqid'], log['pages']))

pqidls = []
updates_sheet = xlrd.open_workbook('/dc/eurobo/documentation/tracking/eeb_incoming_log.xlsx').sheet_by_index(0)

for row in range(1, updates_sheet.nrows):
    pqidls.append(updates_sheet.cell_value(row, 2))

if indir.endswith('.txt'):
    with open(indir, 'r') as flist:
        for f in flist:
            processing(f.strip(), prodlookup)
else:
    for f in locate('*-[0-9][0-9][0-9].xml', indir):
        processing(f, prodlookup)

with open(outfile, 'w') as out:
    for i in outls:
        out.write(h.unescape(i).encode('utf-8'))