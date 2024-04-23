# -*- encoding: utf-8 -*-
import sys
sys.path.insert(0, "/packages/dsol/lib/python2.6/site-packages")
sys.path.insert(0, "/packages/dsol/lib/python")
from lutbuilder import buildLut
import time
import os
import lxml
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


if options.output is None or options.input is None or options.delbatch is None:
    parser.print_help()
    exit(1)

# inf = options.input

dest_dir = options.output
delbatch = options.delbatch

# inf = '/dc/migrations/film/fiaf/data/incoming/references/ref_critical_ideas_in_television_studies.xml'
in_dir = options.input

dates = []
section_tags = ['part', 'chapter', 'letter']


class processRecord(object):
    def __init__(self):
        self.main_id = element.xpath('id')[0].text
        delbatch_tag = etree.SubElement(element, 'delbatch')
        delbatch_tag.text = delbatch
        for tag in section_tags:
            if element.xpath(tag) is not None:
                if not element.xpath('sectionheads'):
                    section_tag = etree.SubElement(element, 'sectionheads')
        # el = Element('content')
        # el.text = CDATA('a string')
        issn_tag = element.xpath('ISBN')[0]
        issn_tag.text = issn_tag.text.replace('ISBN ', '')
        raw_text = element.xpath('text')[0].text
        bodytext_tag = etree.SubElement(element, "cdata")
        bodytext_tag.text = etree.CDATA(raw_text)

    def make_directry(self, directory_to_create):
        if not os.path.isdir(directory_to_create):
            os.mkdir(directory_to_create)
            os.chmod(directory_to_create, 0777)

    def out_filename(self):
        self.output_directory_root = dest_dir
        self.output_directory_sub = 'fiafref%s' % (self.main_id.split('/')[0])
        self.output_directory_create = os.path.join(dest_dir, self.output_directory_sub)
        self.make_directry(self.output_directory_create)

        id_for_outfile = self.main_id.replace('/', '-')
        output_filename = '%s/%s.xml' % (self.output_directory_create, id_for_outfile)
        return output_filename

    def save_record(self, save_filename):
        self.outfilename = save_filename
        # test_record = '%s.xml' % self.outfilename
        # out_test = open(test_record, 'w')
        # recordtest = etree.tostring(element, pretty_print=True, xml_declaration=False, encoding='utf-8')
        xslt = etree.parse('/home/rschumac/work/treasurers/fiaf_references.xsl')
        transform = etree.XSLT(xslt)
        newdom = transform(element)
        record = etree.tostring(newdom, pretty_print=True, xml_declaration=True, encoding='utf-8')
        print record
        record = record.replace('<bodytext>', '<bodytext><![CDATA[')
        record = record.replace('</bodytext>', ']]></bodytext>')
        # print record
        out = open(self.outfilename, 'w')
        out.write(record)
        out.close()
        os.chmod(self.outfilename, 0777)


if __name__ == '__main__':
    f = 0
    for fle in os.listdir(in_dir):
        if fle.endswith('.xml'):
            inf = os.path.join(in_dir, fle)
            print inf
            for event, element in etree.iterparse(inf, tag="record", remove_blank_text=True):
                record = processRecord()
                name = record.out_filename()
                print name
                record.save_record(name)
                # record.save_record(name)
                # print record.record_name()
                # record.process_tags()
                # record.save_record(record.record_name())
                f += 1
                # if f == 55:
                #    exit(1)




