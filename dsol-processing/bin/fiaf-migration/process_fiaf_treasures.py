#!/packages/dsol/s11-test/python2.7/bin/python2
# encoding=utf-8

# import optparse
import argparse
import os
import re
import sys
import time

from StringIO import StringIO

sys.path.insert(0, "/packages/dsol/lib/python2.6/site-packages")
sys.path.insert(0, "/packages/dsol/lib/python")
sys.path.insert(0, "/packages/dsol/cstore/gs4/lib")
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import lxml.etree as etree

from commonUtils.fileUtils import buildLut


# parser = optparse.OptionParser()
# parser.add_option('-i', '--input', dest="input", help='Name(with full path) to input file.')
# parser.add_option('-o', '--output', dest="output", help='Destination directory')
# parser.add_option('-d', '--delbatch', dest="delbatch", help='Delivery batch')
# parser.add_option('-n', '--endrecs', dest="endrecs", help='End rec output at...')
# parser.add_option('--debug', dest="debug", help='Switch on debugging')
# (options, args) = parser.parse_args()

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', dest="input", help='Name(with full path) to input file.', required=True)
parser.add_argument('-o', '--output', dest="output", help='Destination directory', required=True)
parser.add_argument('-d', '--delbatch', dest="delbatch", help='Delivery batch', required=True)
parser.add_argument('-n', '--endrecs', dest="endrecs", help='End rec output at...')
parser.add_argument('--debug', dest="debug", action='store_true', help='Switch on debugging')
options = parser.parse_args(sys.argv[1:])


# if options.input is None or options.output is None or options.delbatch is None:
#     parser.print_help()
#     print('')
#     exit(1)

inf = options.input
dest_dir = options.output
delbatch = options.delbatch
if options.endrecs:
    numrecs = options.endrecs
else:
    numrecs = 10000000


global idlut
idlut = buildLut('/packages/dsol/platform/libdata/fiaftre-ids.lut')
global countrylut
countrylut = buildLut('/packages/dsol/platform/libdata/fiaftre-countries.lut')
pipes = ['FT', 'PC', 'FP', 'CA', 'FW', 'PH', 'CR', 'FD']
notes = ['AH', 'NH', 'NT']
productions = ['FI', 'SE']


def strip_char(country):
    rv = country
    if '?' in rv:
        rv = rv.split('?')[0]
    if '[' in rv:
        rv = rv.split('[')[0]
    rv = rv.strip()
    return countrylut[rv]


class processRecord(object):

    def __init__(self):
        filmyear = element.xpath('x:FY', namespaces={'x': 'http://www.filemaker.com/fmpdsoresult'})[0].text
        if filmyear is None:
            self.file_year = '0001'
        else:
            year_match = re.search('([0-9]{4})', filmyear)
            if year_match:
                self.file_year = year_match.group(1)
            else:
                self.file_year = '0001'
        year_tag = etree.SubElement(element, 'year')
        year_tag.text = self.file_year

        self.acc_id = element.xpath('x:AN', namespaces={'x': 'http://www.filemaker.com/fmpdsoresult'})[0].text
        if options.debug:
            print(self.acc_id)
        try:
            self.main_id = idlut[self.acc_id]
        except KeyError:
            self.main_id = '003/TRE%08d' % int(self.acc_id)
        id_tag = etree.SubElement(element, 'id')
        id_tag.text = self.main_id
        place_tag = etree.SubElement(element, 'place')
        place_code = element.xpath('x:FC', namespaces={'x': 'http://www.filemaker.com/fmpdsoresult'})[0].text
        if place_code is None:
            place_tag.text = ''
        else:
            places = []
            if '|' in place_code:
                places_lookup = place_code.split('|')
                for pl in places_lookup:
                    places.append(strip_char(pl))
            else:
                places.append(strip_char(place_code))
            #try:
            place_tag.text = ', '.join(places)
            #except KeyError:
            #    place_tag.text = ''

        delbatch_tag = etree.SubElement(element, 'delbatch')
        delbatch_tag.text = delbatch
        self.split_pipe()
        self.process_notes()
        for contrib in pipes[1:]:
            if element.xpath('x:%s' % contrib, namespaces={'x': 'http://www.filemaker.com/fmpdsoresult'})[0].text is not None:
                if not element.xpath('contributors'):
                    delbatch_tag = etree.SubElement(element, 'contributors')
        for production in productions:
            if element.xpath('x:%s' % production, namespaces={'x': 'http://www.filemaker.com/fmpdsoresult'})[0].text is not None:
                if not element.xpath('productions'):
                    delbatch_tag = etree.SubElement(element, 'productions')
        # print etree.tostring(element, pretty_print=True)

    def process_notes(self):
        for note in notes:
            if element.xpath('x:%s' % note, namespaces={'x': 'http://www.filemaker.com/fmpdsoresult'})[0].text is not None:
                if not element.xpath('x:notes', namespaces={'x': 'http://www.filemaker.com/fmpdsoresult'}):
                    delbatch_tag = etree.SubElement(element, 'notes')
                element.xpath('x:%s' % note, namespaces={'x': 'http://www.filemaker.com/fmpdsoresult'})[0].text = element.xpath('x:%s' % note, namespaces={'x': 'http://www.filemaker.com/fmpdsoresult'})[0].text.replace('|', '; ')

    def split_pipe(self):
        for data in pipes:
            split_data = []
            string = element.xpath('x:%s' % data, namespaces={'x': 'http://www.filemaker.com/fmpdsoresult'})[0].text
            if string is not None:
                string = string.replace(u'§§', u'§')
                string = string.replace(u'§</', u'</')
                parent_tag_name = '%s1' % data
                parent_tag = etree.SubElement(element, parent_tag_name)
                match = re.search(u'§', string)
                if match:
                    split_data = string.split(u'§')
                elif '|' in string:
                    split_data = string.split(u'|')
                if split_data != []:
                    parent_tag.text = split_data[0]
                    for child in split_data[1:]:
                        if child != '':
                            child_tag_name = '%ss' % data
                            child_tag = etree.SubElement(element, child_tag_name)
                            child_tag.text = child
                else:
                    parent_tag.text = string

    def make_directry(self, directory_to_create):
        if not os.path.isdir(directory_to_create):
            os.mkdir(directory_to_create)
            os.chmod(directory_to_create, 0777)

    def out_filename(self):
        self.output_directory_root = dest_dir
        self.output_directory_day = 'treasures_%s' % time.strftime("%Y%m%d", time.gmtime())
        self.output_directory_pt1 = os.path.join(self.output_directory_root, self.output_directory_day)
        self.make_directry(self.output_directory_pt1)

        outdir = 'fiaftre0001'
        self.output_directory_pt2 = os.path.join(self.output_directory_pt1, outdir)
        self.make_directry(self.output_directory_pt2)

        self.year_directory = '%s/%s0101' % (self.output_directory_pt2, self.file_year)
        self.make_directry(self.year_directory)

        id_for_outfile = self.main_id.replace('/', '-')
        output_filename = '%s/%s.xml' % (self.year_directory, id_for_outfile)
        return output_filename

    def save_record(self, save_filename):

        self.outfilename = save_filename
        xslt = etree.parse('/packages/dsol/platform/libdata/fiaf_treasures_mod3.xsl')
        transform = etree.XSLT(xslt)
        newdom = transform(element)
        order = 0
        for item in newdom.findall('.//contributor'):
            order += 1
            item.attrib['order'] = str(order)
        out = open(self.outfilename, 'w')
        record = etree.tostring(newdom, pretty_print=True, xml_declaration=False, encoding='utf-8')
        out.write(record)
        out.close()
        os.chmod(self.outfilename, 0777)


if __name__ == '__main__':
    f = 1
    for event, element in etree.iterparse(inf, tag="{http://www.filemaker.com/fmpdsoresult}ROW", remove_blank_text=True):
        record = processRecord()
        name = record.out_filename()
        record.save_record(name)
        f += 1
        if f == int(numrecs):
            exit(1)

        if not options.debug:
            sys.stdout.write('Number of records created: \033[92m%s\r' % f)
            sys.stdout.flush()
    print '\n'
