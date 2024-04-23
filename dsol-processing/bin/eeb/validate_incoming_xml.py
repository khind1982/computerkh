# -*- coding:utf-8 -*-
import os
import sys
import re
import optparse
import lxml.etree as etree
sys.path.insert(0, "/packages/dsol/lib/python")

parser = optparse.OptionParser()
parser.add_option('-l', '--libr', dest="libr", help='Name of the library. i.e. copenhagen OR wellcome OR paris OR florence OR kbnl')
parser.add_option('-b', '--bnum', dest="bnum", help='Batch date. i.e. 20140501, 20131225, etc')
parser.add_option('-c', '--cnum', dest="cnum", help='Collection number. i.e. 4, 5, 6, etc')
(options, args) = parser.parse_args()

if options.libr is None or options.bnum is None or options.cnum is None:
    parser.print_help()
    exit(1)

library = options.libr.lower()

while library not in ['copenhagen', 'wellcome', 'paris', 'florence', 'kbnl']:
    print 'Please select correct library: copenhagen OR wellcome OR paris OR florence'
    exit(1)

batch_number = options.bnum
collection_number = options.cnum
base_dir = '/dc/%s-coll%s' % (library, collection_number)
incoming_directory = '%s/Incoming/%s' % (base_dir, batch_number)

if library in ['wellcome']:
    regex_pattern = 'hin-wel-all-[0-9]{8}-[0-9]{3}.xml'
elif library in ['copenhagen']:
    regex_pattern = 'den-kbd-all-[0-9]{11}[0-9|A-Z]-[0-9]{3}.xml'
elif library in ['paris']:
    regex_pattern = 'fra-bnf-rlr-[0-9]{8}-[0-9]{3}.xml'
elif library in ['florence']:
    regex_pattern = 'ita-bnc-mag-[0-9]{8}-[0-9]{3}.xml'
elif library in ['kbnl']:
    regex_pattern = 'ned-kbn-all-[0-9]{8}-[0-9]{3}.xml'


def yield_xml_file(in_directory):
    for root, dirs, files in os.walk(in_directory):
        for f in files:
            match = re.search(regex_pattern, f)
            if match:
                if f.endswith('.xml'):
                    yield os.path.join(root, f)


print 'Checking files:'

for xml_file in yield_xml_file(incoming_directory):
    print xml_file
    schema = etree.parse('/packages/dsol/eeb/mets.xsd')
    xsd = etree.XMLSchema(schema)
    xml = etree.parse(xml_file)
    xsd.validate(xml)
    if xsd.error_log:
        print xsd.error_log

    if library == 'paris':
        shelfmark = xml.xpath('//mods:identifier[@type="coteoriginal"]', namespaces={'mods': 'http://www.loc.gov/mods/v3'})
        try:
            shelf = shelfmark[0].text
        except IndexError:
            print 'Shelfmark not found'

    if library == 'copenhagen' or library == 'wellcome' or library == 'kbnl' or library == 'florence':
        shelfmark = xml.xpath('//mods:physicalLocation', namespaces={'mods': 'http://www.loc.gov/mods/v3'})
        physicalLocation_all = [i.text for i in shelfmark]
        physicalLocation_all = ' '.join(i for i in physicalLocation_all)
        print physicalLocation_all
        if 'SHELFMARK' not in physicalLocation_all:
            print 'Cannot find Shelfmark. Check data.'

        ''' make sure that the shelfmark is not "None" '''
        for item in shelfmark:
            if 'SHELFMARK' in item.text:
                if 'None' in item.text:
                    print 'Shelfmark is "None", please check'

    ''' check for the word SHELFMARK present in the physicalLocation tags (wellcome) '''
    if library == 'wellcome':
        try:
            language_tag = xml.xpath('//mods:languageTerm', namespaces={'mods': 'http://www.loc.gov/mods/v3'})
            lang = language_tag[0].text
            if len(lang) > 3 or len(lang) < 3:
                print 'Language incorrect: %s' % lang
                match = re.search('([A-Z])', lang)
                if match:
                    print 'Check language field %s' % lang
        except:
            print('Please check the language tag')
        '''check for b number and i number'''
        try:
            b_i_num_tag = xml.xpath('//mods:recordContentSource', namespaces={'mods': 'http://www.loc.gov/mods/v3'})[0]
            if not b_i_num_tag.text.split('|')[0].startswith('i'):
                print 'i-number not found!'
            if not b_i_num_tag.text.split('|')[-1].startswith('b'):
                print 'b-number not found!'
        except IndexError:
            print '//mods:recordContentSource tag not found'
        sourcer = xml.xpath('//mods:recordContentSourcer', namespaces={'mods': 'http://www.loc.gov/mods/v3'})
        if sourcer:
            print 'found //mods:recordContentSourcer. Fix!'

    image_details = xml.xpath('//mix:mix', namespaces={'mix': 'http://www.loc.gov/mix/v20'})
    for element in image_details:
        objectid = element.xpath('.//mix:objectIdentifierValue', namespaces={'mix': 'http://www.loc.gov/mix/v20'})
        image_name = objectid[0].text
        image_base_name = os.path.splitext(image_name)[0]
        image_base_name_split = image_base_name.split('-')
        image_full_path = '%s/%s/%s/%s' % (incoming_directory, image_base_name.rsplit('-', 2)[0], image_base_name.rsplit('-', 1)[0], image_name)
        # print image_full_path
        ''' check if the image actually exists '''
        if not os.path.isfile(image_full_path):
            print('please make sure this image exists: %s' % (image_full_path))
            exit(1)

        resolutions = element.xpath('.//mix:SpatialMetrics', namespaces={'mix': 'http://www.loc.gov/mix/v20'})
        image_dpi_xy = resolutions[0].xpath('.//mix:numerator', namespaces={'mix': 'http://www.loc.gov/mix/v20'})
        image_dpi_x = image_dpi_xy[0].text
        image_dpi_y = image_dpi_xy[1].text
        ''' make sure the x resolution is an integer '''
        try:
            int(image_dpi_x)
        except ValueError:
            print('please check the //mix:SpatialMetrics/numerator[0] value for this image: %s' % (image_full_path))
            print('value should be an integer')
            exit(1)
        ''' make sure the resolution x is not bonkers '''
        if int(image_dpi_x) > 600 or int(image_dpi_x) < 200:
            print('please check the //mix:SpatialMetrics/numerator[0] value for this image: %s' % (image_full_path))
            print('value should be between 200 and 600')
            exit(1)
        # print image_dpi_x
        image_dpi_y = resolutions[0].xpath('.//mix:numerator', namespaces={'mix': 'http://www.loc.gov/mix/v20'})[1].text
        # print image_dpi_y
        ''' make sure the y resolution is an integer '''
        try:
            int(image_dpi_y)
        except ValueError:
            print('please check the //mix:SpatialMetrics/numerator[1] value for this image: %s' % (image_full_path))
            print('value should be an integer')
            exit(1)
        ''' make sure the resolution is not bonkers '''
        if int(image_dpi_y) > 600 or int(image_dpi_y) < 200:
            print('please check the //mix:SpatialMetrics/numerator[1] value for this image: %s' % (image_full_path))
            print('value should be between 200 and 600')
            exit(1)
        image_dimensions = element.xpath('.//mix:BasicImageCharacteristics', namespaces={'mix': 'http://www.loc.gov/mix/v20'})
        image_width = image_dimensions[0].xpath('.//mix:imageWidth', namespaces={'mix': 'http://www.loc.gov/mix/v20'})[0].text
        image_height = image_dimensions[0].xpath('.//mix:imageHeight', namespaces={'mix': 'http://www.loc.gov/mix/v20'})[0].text
        ''' make sure the //mix:BasicImageCharacteristics/imageWidth resolution is an integer '''
        try:
            int(image_width)
        except ValueError:
            print('please check the //mix:SpatialMetrics/numerator[1] value for this image: %s' % (image_full_path))
            print('value should be an integer')
            exit(1)
        # print image_width
        image_height = image_dimensions[0].xpath('.//mix:imageHeight', namespaces={'mix': 'http://www.loc.gov/mix/v20'})[0].text
        # print image_height
        ''' make sure the image_height resolution is an integer '''
        try:
            int(image_height)
        except ValueError:
            print('please check the //mix:SpatialMetrics/numerator[1] value for this image: %s' % (image_full_path))
            print('value should be an integer')
            exit(1)
