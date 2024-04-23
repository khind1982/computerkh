#!/usr/bin/env python2.7
# coding=utf-8

import sys
sys.path.insert(0, "/packages/dsol/lib/python2.6/site-packages")
sys.path.insert(0, "/packages/dsol/lib/python")
from lutbuilder import buildLut
import time
import os
import lxml.etree as etree
import sys
import re
import optparse
from StringIO import StringIO
parser = optparse.OptionParser()
parser.add_option('-i', '--input', dest="input", help='Name(with full path) to input file.')
parser.add_option('-o', '--output', dest="output", help='Destination directory')
parser.add_option('-d', '--delbatch', dest="delbatch", help='Destination directory')
(options, args) = parser.parse_args()

if options.input is None or options.output is None or options.delbatch is None:
    parser.print_help()
    print('')
    print('If you are experiencing difficulties with this script, ')
    print('check that you have removed the XML declaration from the ')
    print('input file. The root tag should be "<FMPDSORESULT>".')
    print('')
    exit(1)

inf = options.input
dest_dir = options.output
delbatch = options.delbatch

global idlut
idlut = buildLut('/home/rschumac/svn/trunk/cstore/gs4/libdata/fiaftre-ids.lut')

global data_tags
data_tags = {'accnum': 'AN', 'country_of_production': 'FC', 'numdate': 'FY', 'originaldate': 'FY',
             'filmtitle': 'FT', 'director': 'FD',
             'prodcomp': 'PC', 'producer': 'FP', 'cast': 'CA', 'writer': 'FW', 'photography': 'PH',
             'credit': 'CR', 'archive': 'AR', 'access': 'AH', 'nonaccess': 'NH', 'note': 'NT'}
accnum_country_list = ['accnum', 'country_of_production']
year_list = ['numdate', 'originaldate']
productions_list = ['numdate', 'originaldate']
notes = {'archive': {'xpath': 'AR', 'attributes': {'type': 'document', 'contentlabel': 'archive'}},
         'access': {'xpath': 'AH', 'attributes': {'type': 'document', 'contentlabel': 'Access Holdings'}},
         'nonaccess': {'xpath': 'NH', 'attributes': {'type': 'document', 'contentlabel': 'Non-access holdings'}},
         'note': {'xpath': 'NT', 'attributes': {'type': 'document'}}}
contributors = {'director': {'xpath': 'FD', 'attributes': {'role': 'Director'}, 'sub_tag': 'originalform'},
                'productioncompany': {'xpath': 'PC', 'attributes': {'role': 'ProductionCompany'}, 'sub_tag': 'organisation_name'},
                'producer': {'xpath': 'FP', 'attributes': {'role': 'Producer'}, 'sub_tag': 'originalform'},
                'cast': {'xpath': 'CA', 'attributes': {'role': 'Cast'}, 'sub_tag': 'originalform'},
                'crew_writer': {'xpath': 'FW', 'attributes': {'role': 'Crew'}, 'sub_tag': 'originalform', 'contribdesc': 'Writer'},
                'crew_photography': {'xpath': 'PH', 'attributes': {'role': 'Crew'}, 'sub_tag': 'originalform', 'contribdesc': 'Photography'},
                'crew_credit': {'xpath': 'CR', 'attributes': {'role': 'Crew'}, 'sub_tag': 'originalform', 'contribdesc': 'Credit'}}


class processRecord(object):

    def __init__(self):
        root_attribs = {'delbatch': delbatch}
        self.root = etree.Element("document", attrib=root_attribs)
        self.rec_tag = etree.SubElement(self.root, "record")
        self.film_tag = etree.SubElement(self.rec_tag, "film")
        self.docid_tag = etree.SubElement(self.film_tag, "docid")
        self.acc_id = element.xpath('AN')[0].text
        try:
            self.main_id = idlut[self.acc_id]
        except KeyError:
            self.main_id = '003/TRE%08d' % int(self.acc_id)
        self.docid_tag.text = self.main_id
        self.doctypes_tag = etree.SubElement(self.film_tag, "doctypes")
        self.doctype1_tag = etree.SubElement(self.doctypes_tag, "doctype1")
        self.doctype1_tag.text = "Film"

    def process_tags(self):
        for k in data_tags:
            self.name = k
            self.k = element.xpath(data_tags[k])[0].text
            self.process_data(self.name, self.k)
        self.process_productions()
        self.process_notes()
        self.process_contributors()

    def process_contributor(self, tag):
        """ 'director': {'xpath': 'FD', 'attributes': {'role': 'Director'}, 'sub_tag', 'originalform'} """
        text = element.xpath(contributors[tag]['xpath'])[0].text
        if text is not None:
            contrib_tag_attributes = {'role': contributors[tag]['attributes']['role']}
            contrib_tag = etree.SubElement(self.contribs_tag, 'contributor', attrib=contrib_tag_attributes)
            contrib_tag_sub = etree.SubElement(contrib_tag, contributors[tag]['sub_tag'])
            contrib_tag_sub.text = element.xpath(contributors[tag]['xpath'])[0].text
            if tag in ('crew_writer', 'crew_photography', 'crew_credit'):
                desc_tag = etree.SubElement(contrib_tag, 'contribdesc')
                desc_tag.text = contributors[tag]['contribdesc']

    def process_contributors(self):
        self.contribs_tag = etree.SubElement(self.film_tag, 'contributors')
        for k in contributors:
            self.process_contributor(k)

    def process_note(self, tag):
        """ 'archive': {'xpath': 'AR', 'attributes': {'type': 'document', 'contentlabel': 'archive'}} """
        text = element.xpath(notes[tag]['xpath'])[0].text
        if text is not None:
            note_attributes = notes[tag]['attributes']
            note_archive_tag = etree.SubElement(self.notes_tag, "note", attrib=note_attributes)
            note_archive_tag.text = text.replace('|', '; ')

    def process_notes(self):
        self.notes_tag = etree.SubElement(self.film_tag, 'notes')
        for k in notes:
            self.process_note(k)

    def process_productions(self):
        desc = element.xpath('FI')[0].text
        seri = element.xpath('SE')[0].text
        if desc is not None or seri is not None:
            self.productions_tag = etree.SubElement(self.film_tag, 'productions')
            self.production_details_tag = etree.SubElement(self.productions_tag, 'production_details')
        if desc is not None:
            self.insert_data('FI', self.production_details_tag, 'description', desc)
        if seri is not None:
            self.insert_data('SE', self.production_details_tag, 'production_series', seri)

    def insert_data(self, source, root, tag, data):
        record_data = element.xpath(source)[0].text
        record_tag = etree.SubElement(root, tag)
        record_tag.text = data

    def process_data(self, name, data):
        if data is not None:
            if name in accnum_country_list:
                self.insert_data(data_tags[name], self.film_tag, name, data)
            elif name in year_list:
                try:
                    self.root.xpath('./pubdates')
                    self.insert_data(data_tags[name], self.pubdates_tag, name, data)
                except AttributeError:
                    self.pubdates_tag = etree.SubElement(self.film_tag, 'pubdates')
                    self.insert_data(data_tags[name], self.pubdates_tag, name, data)
            elif name is 'filmtitle':
                self.subjects_tag = etree.SubElement(self.film_tag, 'subjects')
                subject_attributes = {"type": "production"}
                self.subject_tag = etree.SubElement(self.subjects_tag, 'subject', attrib=subject_attributes)
                title = element.xpath(data_tags[name])[0].text
                match = re.search(u'§', title)
                if match:
                    title_and_subs = title.split(u'§')
                    self.insert_data(data_tags[name], self.film_tag, 'title', title_and_subs[0])
                    self.subject_tag.text = title_and_subs[0]
                    for title_sub in title_and_subs[1:]:
                        self.insert_data(data_tags[name], self.film_tag, 'alternate_title', title_sub)
                else:
                    self.insert_data(data_tags[name], self.film_tag, 'title', title)
                    self.subject_tag.text = title

    def make_directry(self, directory_to_create):
        if not os.path.isdir(directory_to_create):
            os.mkdir(directory_to_create)
            os.chmod(directory_to_create, 0777)

    def record_name(self):
        self.output_directory_root = dest_dir
        self.output_directory_day = 'treasures_%s' % time.strftime("%Y%m%d", time.gmtime())
        self.output_directory_pt1 = os.path.join(self.output_directory_root, self.output_directory_day)
        self.make_directry(self.output_directory_pt1)

        outdir = 'fiaftre0001'
        self.output_directory_pt2 = os.path.join(self.output_directory_pt1, outdir)
        self.make_directry(self.output_directory_pt2)

        filmyear = element.xpath('FY')[0].text
        if filmyear is None:
            file_year = '0001'
        else:
            year_match = re.search('([0-9]{4})', filmyear)
            if year_match:
                file_year = year_match.group(1)
            else:
                file_year = '0001'
        self.year_directory = '%s/%s0101' % (self.output_directory_pt2, file_year)
        self.make_directry(self.year_directory)

        accnumber = element.xpath('AN')[0].text
        try:
            file_id = idlut[accnumber]
        except KeyError:
            file_id = self.main_id
        id_for_outfile = file_id.replace('/', '-')
        output_filename = '%s/%s.xml' % (self.year_directory, id_for_outfile)
        return (output_filename)

    def save_record(self, save_filename):
        self.outfilename = save_filename
        xslt = etree.parse('/home/rschumac/work/treasurers/leviathan_corrected_order.xsl')
        transform = etree.XSLT(xslt)
        newdom = transform(self.root)
        out = open(self.outfilename, 'w')
        record = etree.tostring(newdom, pretty_print=True, xml_declaration=False, encoding='utf-8')
        out.write(record)
        out.close()
        os.chmod(self.outfilename, 0777)

if __name__ == '__main__':
    for event, element in etree.iterparse(inf, tag="ROW", remove_blank_text=True):
        record = processRecord()
        print record.record_name()
        record.process_tags()
        record.save_record(record.record_name())
