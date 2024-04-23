#!/usr/bin/env python2.7
# coding=utf-8
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

from commonUtils.textUtils import fix_named_ents, buildLut
import time
import lxml.etree as etree
import sys
import re
import optparse
from StringIO import StringIO
import HTMLParser


parser = optparse.OptionParser()
parser.add_option('-i', '--input', dest="input", help='Name(with full path) to input file.')
parser.add_option('-o', '--output', dest="output", help='Destination directory')
parser.add_option('-d', '--delbatch', dest="delbatch", help='Destination directory')
(options, args) = parser.parse_args()


if options.output is None or options.input is None or options.delbatch is None:
    parser.print_help()
    exit(1)

if not os.path.exists(options.output):
    os.makedirs(options.output)

# inf = options.input

dest_dir = options.output
delbatch = options.delbatch

# inf = '/dc/migrations/film/fiaf/data/incoming/references/ref_critical_ideas_in_television_studies.xml'
in_dir = options.input

dates = []
section_tags = ['part', 'chapter', 'letter']


class processRecord(object):
    def __init__(self):
        for elem in element:
            if elem.text is not None:
                elem.text = fix_named_ents(elem.text)
        self.main_id = element.xpath('id')[0].text
        delbatch_tag = etree.SubElement(element, 'delbatch')
        delbatch_tag.text = delbatch
        for tag in section_tags:
            if element.xpath(tag) is not None:
                if not element.xpath('sectionheads'):
                    section_tag = etree.SubElement(element, 'sectionheads')
        issn_tag = element.xpath('ISBN')[0]
        issn_tag.text = issn_tag.text.replace('ISBN ', '')
        raw_text = ''.join([etree.tostring(p).replace(' xmlns:="html"', '') for p in element.xpath('text')[0] if p.tag == 'p'])
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
        xslt = etree.parse('/home/cmoore/svn/trunk/cstore/gs4/libdata/fiaf_references_mod.xsl')
        transform = etree.XSLT(xslt)
        newdom = transform(element)
        record = etree.tostring(newdom, pretty_print=True, xml_declaration=True).replace('amp;amp;', 'amp;')
        record = record.replace('<bodytext>', '<bodytext><![CDATA[')
        record = record.replace('</bodytext>', ']]></bodytext>')
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
             # can I get the HTMLParser to give me a string and pass iterparse a modified stringIO object?
            hs = StringIO('<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "/home/cmoore/svn/trunk/cstore/gs4/libdata/dtds/xhtml/xhtml1-strict.dtd">%s' % open(inf, 'r').read())
            for event, element in etree.iterparse(hs, tag="record", remove_blank_text=True, resolve_entities=False, load_dtd=True):
                record = processRecord()
                name = record.out_filename()
                record.save_record(name)
                f += 1
                # if f == 38:
                #    exit(1)




