#!/usr/bin/env python2.7
# coding=utf-8

import os
import sys
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import collections
import lxml.etree as ET
import time
import HTMLParser


from StringIO import StringIO

from commonUtils.fileUtils import locate, buildLut, buildListLut
from filmtransformfunc import levxml, levorder
from datetool.dateparser import parser as dateparser
from datetool.dateparser import ParserError

fieldlookup = buildListLut('fiaf-fields.lut')
contenttypes = {'fiaf': 'journal', 'fiaftre': 'film', 'fiafref': 'book'}
peerreview = []
# jlist = []
badrecs = []
newrecs = []
# elecs = []
badreccount = 0
h = HTMLParser.HTMLParser()


product = 'fiaf'

try:
    indir = sys.argv[1]
    jdir = sys.argv[2]
    outdir = sys.argv[3]
except IndexError:
    print("Usage: %s {indirectory} {journal directory} {outdirectory}\nMaybe one of these is missing from your command?" % __file__)
    exit()

def strip_issn_delimiter(issn):
    return str('-'.join(re.findall('[0-9A-z]+', issn)))


def fiaftransform(data):
    datelist = []
    document = levxml(data, contenttypes[product], 'fiaf-fields.lut')
    document.attrib['delbatch'] = '2015_3'
    journal = document.xpath('/document/record/journal')

    for element in data:
        '''Defining the legacy journalID from the journal title'''
        try:
            if element.tag == "Source_ISSN":
                new_issn = strip_issn_delimiter(element.text)
                # ET.SubElement(journal[0], 'journalid').text = jidsdict[element.text.encode('latin-1')]
                ET.SubElement(journal[0], 'journalid').text = jidsdict[new_issn]
                if element.text in peerreview:
                    ET.SubElement(journal[0], 'peer_review').text = 'Y'
                else:
                    ET.SubElement(journal[0], 'peer_review').text = 'N'
        except KeyError:
            ET.SubElement(journal[0], 'journalid').text = jidsdict[data.find('.//Source_Journal').text.encode('utf-8')]
        '''Saving PY and Month to append to pubdates'''
        if element.tag == "Source_PY" or element.tag == "Source_Month":
            datelist.append(element.text)
        if element.tag == "Film_Description" or element.tag == "TV_Film_Description":  # the list needs looking at so we can define this at list level. Maybe two types of parent type; shared and single, defined in lookup?
            production_details = ET.SubElement(journal[0], 'production_details')
            ET.SubElement(production_details, 'description').text = element.text  # investigate film description fields to see if they contain all the information needed.
            if re.match('[0-9][0-9][0-9][0-9]', element.text[-5:][0:4]) is not None:
                ET.SubElement(production_details, 'release_year').text = element.text[-5:][0:4]

    '''Assigning e-ISSN'''
    if data.find('.//Source_ISSN').text in eissndict.keys() or data.find('.//Source_Journal').text in eissndict.keys():
        try:
            ET.SubElement(journal[0], 'elec_issn').text = eissndict[data.find('.//Source_ISSN').text]
            # elecs.append('%s: %s' % (data.find('.//Source_Journal').text, eissndict[data.find('.//Source_ISSN').text]))
        except KeyError:
            ET.SubElement(journal[0], 'elec_issn').text = eissndict[data.find('.//Source_Journal').text]
            # elecs.append('%s: %s' % (data.find('.//Source_Journal').text,  eissndict[data.find('.//Source_Journal').text]))

    '''Assigning ISSN excluding 0000-0000'''
    if data.find('.//Source_ISSN').text != '0000-0000':
    #     pass
    # else:
        ET.SubElement(journal[0], 'print_issn').text = data.find('.//Source_ISSN').text

    '''Assigning the sourcetype'''
    try:
        document.attrib['source_type'] = sourcetype[data.find('.//Source_ISSN').text]
    except KeyError:
        document.attrib['source_type'] = sourcetype[data.find('.//Source_Journal').text]

    '''Assigning vendor field, source institution, projectcode'''
    ET.SubElement(journal[0], 'vendor').text = product
    ET.SubElement(journal[0], 'sourceinstitution').text = product.upper()
    ET.SubElement(journal[0], 'projectcode').text = product

    '''Adding title field if none present'''
    if document.find('.//title') is None:
        ET.SubElement(journal[0], 'title').text = '[Title unknown]'

    '''Assigning the saved dateslist to pubdates field'''
    pubdates = ET.SubElement(journal[0], 'pubdates')
    try:
        parsed_date = dateparser.parse(' '.join(datelist)).start_date
        ET.SubElement(pubdates, 'originaldate').text = ', '.join(datelist).replace(',,', ',')
        ET.SubElement(pubdates, 'numdate').text = '%s-%s-%s' % (parsed_date.normalised_numeric_date[0:4], parsed_date.normalised_numeric_date[4:6], parsed_date.normalised_numeric_date[6:8])
    except ParserError:
        badrecs.append("%s from %s (journal %s, source ID %s) is not a recognised date - it has not been added to the record" % (', '.join(datelist), document.xpath('/document/record/journal/docid')[0].text, document.xpath('/document/record/journal/journalid')[0].text, document.xpath('/document/record/journal/srcid')[0].text))
    except ValueError:
        badrecs.append("%s from %s (journal %s, source ID %s) is a badly formatted date - it has not been added to the record" % (', '.join(datelist), document.xpath('/document/record/journal/docid')[0].text, document.xpath('/document/record/journal/journalid')[0].text, document.xpath('/document/record/journal/srcid')[0].text))
    except AttributeError:
        badrecs.append("%s from %s (journal %s, source ID %s) does not have a date - it has not been added to the record" % (', '.join(datelist), document.xpath('/document/record/journal/docid')[0].text, document.xpath('/document/record/journal/journalid')[0].text, document.xpath('/document/record/journal/srcid')[0].text))

    '''Assigning the production_details correctly'''
    if len(document.xpath('/document/record/journal/production_details')) != 0:
        productions = ET.SubElement(journal[0], 'productions')
        for item in document.xpath('/document/record/journal/production_details'):
            productions.append(item)

    # print ET.tostring(document, pretty_print=True)
    finaldoc = levorder(document, contenttypes[product])
    # print ET.tostring(finaldoc, pretty_print=True)

    return finaldoc

newjournals = []

if product == 'fiaf':
    idlookup = buildLut('fiaf-ids.lut')
    jidsdict = buildLut('/dc/fiaf/utils/jid-title_fiaf-issn_rewrite.lut')
    eissndict = {}
    sourcetype = {}

    for f in locate('*.xml', jdir):
        fs = StringIO(open(f, 'r').read())
        tree = ET.iterparse(fs, remove_blank_text=True)

        for _, record in tree:
            if record.tag == "record":
                if record.find('.//Peer-Review').text == 'Y':
                    peerreview.append(record.find('.//ISSN').text)
                if strip_issn_delimiter(record.find('.//ISSN').text) not in jidsdict.keys() and record.find('.//Journal_Title').text.encode('utf-8') not in jidsdict.keys():
                    # This will add journals that were never published in legacy using the incoming data IDs.
                    jidsdict[record.find('.//ISSN').text] = '006/FIAF%s' % record.find('.//ID').text
                    print('Not found in legacy: %s. Will be added as journalid 006/FIAF%s' % (record.find('.//Journal_Title').text.encode('utf-8'), record.find('.//ID').text))
                    newjournals.append('%s|006/FIAF%s' % (record.find('.//ISSN').text, record.find('.//ID').text))
                    # This will make a dictionary that applies e-ISSN to data
                if record.find('.//e-ISSN') is not None and record.find('.//e-ISSN').text is not None:
                    if record.find('.//ISSN').text != '0000-0000':
                        eissndict[record.find('.//ISSN').text] = record.find('.//e-ISSN').text
                    else:
                        eissndict[record.find('.//Journal_Title').text] = record.find('.//e-ISSN').text
                # Making a dictionary for the source types - has to be part based on ISSN, partly journal title, because of different journals having the same journal title
                if record.find('.//ISSN').text != '0000-0000':
                    sourcetype[record.find('.//ISSN').text] = record.find('.//Document_type').text
                else:
                    sourcetype[record.find('.//Journal_Title').text] = record.find('.//Document_type').text

    for f in locate('*.xml', indir):
        reccount = 0
        fs = StringIO(open(f, 'r').read())
        tree = ET.iterparse(fs, remove_blank_text=True)

        for _, record in tree:
            filmortv = os.path.basename(f)[0].upper()
            if record.tag == "record":
                # jlist = list(set([int(x.replace('006/', '')) for x in jidsdict.values()]))
                try:
                    # Try and match ISSN to a legacy journal ID
                    journal = strip_issn_delimiter(record.find('Source_ISSN').text)
                    jid = jidsdict[journal].replace('/', '-')
                except KeyError:
                    # try:
                        # If that doesn't work, match it to a legacy journal title
                    journal = record.find('Source_Journal').text
                    jid = jidsdict[journal.encode('utf-8')].replace('/', '-')
                    # except KeyError:
                    #     # If that still doesn't work, identify the last ID that was assigned to a journal and create a new one that's unique.
                    #     jidsdict[record.find('Source_ISSN').text] = '006/%s' % str(jlist[-1] + 1).zfill(7)
                    #     newjournals.append('%s|006/%s' % (record.find('Source_ISSN').text, str(jlist[-1] + 1).zfill(7)))
                    #     jid = jidsdict[record.find('Source_ISSN').text].replace('/', '-')
                except AttributeError:
                    badrecs.append('Record has no ISSN or Source_Journal field:\n%s' % ET.tostring(record, pretty_print=True))
                    badreccount += 1
                    pass

                path = '%s/%s' % (outdir, jid)

                if not os.path.exists(path):
                    os.makedirs(path)
                if record.find('Old_AdvRev_Code') is not None:
                    matchid = '%s%s' % (record.find('Old_AdvRev_Code').text.split('.')[0].strip(), record.find('Old_AdvRev_Code').text.split('.')[1].strip())
                else:
                    matchid = '%s%s%s' % (filmortv, record.find('Source_PY').text, record.find('ID').text)
                legid = ET.SubElement(record, 'legid')
                try:
                    legid.text = idlookup[matchid]
                except KeyError:
                    legid.text = '004/FIAF%s' % record.find('ID').text
                    newrecs.append('Record has no match legacy ID - using incoming record ID:\n%s' % ET.tostring(record, pretty_print=True, encoding='utf-8', xml_declaration=True))
                record.append(legid)
                rec = fiaftransform(record)
                outfname = '%s/%s.xml' % (path, legid.text.replace('/', '-'))
                reccount += 1
                with open(outfname, 'w') as out:
                    out.write(ET.tostring(rec, pretty_print=True, encoding='iso-latin-1', xml_declaration=True))
            elif record.getparent() is None:
                break

            sys.stdout.write('File: %s \033[92mNumber of records created:\033[0m %s\r' % (f, reccount))
            sys.stdout.flush()

        print('\n')

        if badreccount > 0:
            print('\nRecords skipped or to investigate: %s (see incoming-fiaf_data-errors.txt in %s)' % (badreccount, outdir))
        if len(newjournals) != 0:
            print('\n\033[95mNew journals encountered\033[0m - add to /dc/fiaf/utils/jid-title_fiaf-issn_rewrite.lut:')
            for item in newjournals:
                print(item)

        if len(badrecs) != 0:
            errorslog = '%s/incoming-fiaf_data-errors.txt' % outdir
            print('\n\033[91mErrors encountered!\033[0m See %s for details' % errorslog)

            with open(errorslog, 'w') as out:
                for item in badrecs:
                    out.write(item + '\n')

        if len(newrecs) != 0:
            newrecslog = '%s/fiaf_data-newrecs.txt' % outdir
            with open(newrecslog, 'w') as out:
                for item in newrecs:
                    out.write(item + '\n')

# print list(set(elecs))