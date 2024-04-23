#!/usr/bin/env python2.6
# -*- coding:utf-8 -*-

import os
import re
import time
import sys
sys.path.insert(0, "/packages/dsol/lib/python2.6/site-packages")
sys.path.insert(0, "/packages/dsol/opt/lib/python2.7/site-packages")
import lxml.etree as ET
import subprocess
import pymongo
import datetime
import pprint

jpeg_image_final_directory = '/dc/dsol/eurobo/validation_images'

today = datetime.date.today()
year = time.strftime("%Y")

image_details_lookup = {}

client = pymongo.MongoClient('mongodb://mongodb-node1')
db = client.eeb

db.records.drop()

recs = [{
            'pid': 'ned-kbn-all-00008012-001',
            'high': 10082,
            'lid': '(ID:537175904)|843487260',
            'library': 'wel',
            'collection': 5,
            'authors':  [
                            {
                                'name': 'Schmidt, Ch',
                                'type': 'main'
                            },
                            {
                                'name': 'Strijdom, D',
                                'type': 'other'
                            }

                        ],
            'titles':  [
                            {
                                'name': 'Sluys, onder den Prins van Parma',
                                'type': ''
                            },
                            {
                                'name': 'Prins van Parma, onder den Sluys',
                                'type': 'alt'
                            }
                        ],
            'city': 'Amsterdam',
            'country': 'Netherlands',
            'country_code': 'nl',
            'date': '1799',
            'publisher': 'By de Weduwe van Joannes van Someren',
            'dimensions': '36 cm',
            'pagination': '27, 895 p',
            'imprint': 'Amsterdam: By de Weduwe van Joannes van Someren, Abraham Wolfgangh, Hendrick en Dirck Boom',
            'notes' :   [
                            'Gegrav. titel: Historie der Nederlandtsche oorlogen; franse titel',
                            'Historie der Nederlandtsche oorlogen'
                        ],
            'shelfmark': '1004 A 8',
            'subject': 'Literature',
            'languages':    [
                                'Dutch',
                                'English'
                            ],
            'languages_code':    [
                                'dut',
                                'eng'
                            ],
            'path': '/dc/kbnl-coll4/Incoming/Delivery12/ned-kbn-all-00008012',
            'mets_received': '2015-11-06',
            'mods_generated': '2015-11-06',
            'images_processed_validation': '',
            'images_validated': '2015-11-06',
            'images_processed_handover': '',
            'dates_validated': '',
            'authors_validated': ''
        },
        {
            'pid': 'ned-kbn-all-00021163-001',
            'high': 10082,
            'lid': '(ID:537175904)|843487260',
            'library': 'wel',
            'collection': 7,
            'authors':  [
                            {
                                'name': 'Schmidt, Ch',
                                'type': 'main'
                            },
                            {
                                'name': 'Strijdom, D',
                                'type': 'other'
                            }

                        ],
            'titles':  [
                            {
                                'name': 'Sluys, onder den Prins van Parma',
                                'type': ''
                            },
                            {
                                'name': 'Prins van Parma, onder den Sluys',
                                'type': 'alt'
                            }
                        ],
            'city': 'Amsterdam',
            'country': 'Netherlands',
            'country_code': 'nl',
            'date': '1799',
            'publisher': 'By de Weduwe van Joannes van Someren',
            'dimensions': '36 cm',
            'pagination': '27, 895 p',
            'imprint': 'Amsterdam: By de Weduwe van Joannes van Someren, Abraham Wolfgangh, Hendrick en Dirck Boom',
            'notes' :   [
                            'Gegrav. titel: Historie der Nederlandtsche oorlogen; franse titel',
                            'Historie der Nederlandtsche oorlogen'
                        ],
            'shelfmark': '1004 A 8',
            'subject': 'Literature',
            'languages':    [
                                'Dutch',
                                'English'
                            ],
            'languages_code':    [
                                'dut',
                                'eng'
                            ],
            'path': '/dc/wellcome-coll6/Incoming/20140602/hin-wel-all-00000380',
            'mets_received': '2015-11-06',
            'mods_generated': '2015-11-06',
            'images_processed_validation': '2015-03-08',
            'images_validated': '',
            'images_processed_handover': '',
            'dates_validated': '',
            'authors_validated': ''
        }]

for rec in recs:
    db.records.insert_one(rec)

libraries = {
                'wel': 'The Wellcome Trust, London',
                'kbd': 'The Royal Library, Copenhagen',
                'bnc': 'The Biblioteca Nazionale Centrale di Firenze',
                'kbn': 'Koninklijke Bibliotheek, National library of the Netherlands',
                'bnf': 'Bibliothèque nationale de France, Paris'
            }


def get_image_details(xml_directory):
    image_loopkup = {}
    for root, directories, files in os.walk(xml_directory):
        for xml_file in files:
            if xml_file[-3:].upper().endswith('XML'):
                if len(xml_file.split('-')) == 5:
                    xml_file_full = os.path.join(root, xml_file)
                    xml = ET.parse(xml_file_full)
                    items = xml.xpath('//mix:mix', namespaces={'mix': 'http://www.loc.gov/mix/v20'})
                    for element in items:
                        objectid = element.xpath('.//mix:objectIdentifierValue', namespaces={'mix': 'http://www.loc.gov/mix/v20'})
                        image = objectid[0].text
                        resolutions = element.xpath('.//mix:SpatialMetrics', namespaces={'mix': 'http://www.loc.gov/mix/v20'})
                        x_dpi = resolutions[0].xpath('.//mix:numerator', namespaces={'mix': 'http://www.loc.gov/mix/v20'})[0].text
                        y_dpi = resolutions[0].xpath('.//mix:numerator', namespaces={'mix': 'http://www.loc.gov/mix/v20'})[1].text
                        objectid = element.xpath('.//mix:BasicImageCharacteristics', namespaces={'mix': 'http://www.loc.gov/mix/v20'})
                        image_width = objectid[0].xpath('.//mix:imageWidth', namespaces={'mix': 'http://www.loc.gov/mix/v20'})[0].text
                        image_height = objectid[0].xpath('.//mix:imageHeight', namespaces={'mix': 'http://www.loc.gov/mix/v20'})[0].text
                        image_loopkup[image] = {'x': x_dpi, 'y': y_dpi, 'w': image_width, 'h': image_height}
    return image_loopkup


def tile_list(x, y, l=[]):
    l.append([x, y])
    if (x/2) > 256 or (y/2) > 265:
        tile_list(x/2, y/2, l)
    else:
        l.append([x/2, y/2])
    return l

def num_of_tiles(l):
    n = 0
    for i in l:
        n = n + ((int(i[0] / float(256)) + 1) * (int(i[1] / float(256)) + 1))
        #print i[0] / float(256), i[1] / float(256)
        #print (int(i[0] / float(256)) + 1), (int(i[1] / float(256)) + 1)
        #print ((int(i[0] / float(256)) + 1) * (int(i[1] / float(256)) + 1))
    return n

def create_xml(x, y, n, d):
    ''' <IMAGE_PROPERTIES WIDTH="1536" HEIGHT="2216" NUMTILES="78" NUMIMAGES="1" VERSION="1.8" TILESIZE="256" /> '''

    print x, y, n, d
    print '<IMAGE_PROPERTIES WIDTH="1536" HEIGHT="2216" NUMTILES="178" NUMIMAGES="1" VERSION="1.8" TILESIZE="256" />'
    root = ET.Element("IMAGE_PROPERTIES")
    root.attrib['WIDTH'] = str(x)
    root.attrib['HEIGHT'] = str(y)
    root.attrib['NUMTILES'] = str(n)
    root.attrib['NUMIMAGES'] = '1'
    root.attrib['VERSION'] = '1.8'
    root.attrib['TILESIZE'] = '256'
    xml = ET.tostring(root, pretty_print=False, xml_declaration=False, encoding='utf-8')
    out = os.path.join(d, 'ImageProperties.xml')
    print xml
    print out

def process_image(image, collection):
    image_base_name = os.path.split(image)[1]
    image_split = image_base_name.split('-')
    image_without_ext = image_base_name[:-4]
    x_resolution = image_details_lookup[image_base_name]['x']
    y_resolution = image_details_lookup[image_base_name]['y']
    x_dimension = image_details_lookup[image_base_name]['w']
    y_dimension = image_details_lookup[image_base_name]['h']
    #pid = '-'.join(image_base_name.split('-', 4))
    pid = '-'.join(image_base_name.split('-')[:5])
    print 'pid ', pid, x_dimension, y_dimension

    jpeg_directory = '%s/jpeg/Collection%s/%s/%s/%s/%s/%s' \
        % (jpeg_image_final_directory, collection, image_split[0], image_split[1], image_split[2], image_split[3], image_split[4])
    if not os.path.isdir(jpeg_directory):
        os.makedirs(jpeg_directory)
    tile_directory = '%s/zoomify/Collection%s/%s/%s/%s/%s/%s/%s/TileGroup0' \
        % (jpeg_image_final_directory, collection, image_split[0], image_split[1], image_split[2], image_split[3], image_split[4], os.path.splitext(image_base_name)[0])
    if not os.path.isdir(tile_directory):
        os.makedirs(tile_directory)
    #print jpeg_directory
    #print tile_directory

    copy_location = '/dc/dsol/eurobo/validation_images/%s-copy.tif' % pid
    output_full_jpg = '%s.jpg' % os.path.join(jpeg_directory, image_without_ext)
    output_300_dpi_jpg = '%s_300.jpg' % os.path.join(jpeg_directory, image_without_ext)
    output_96_dpi_jpg = '%s_96.jpg' % os.path.join(jpeg_directory, image_without_ext)
    output_thumb_jpg = '%s.thumb.jpg' % os.path.join(jpeg_directory, image_without_ext)


    create_full_size_jpg_command = '/usr/local/versions/ImageMagick-6.6.8b/bin/convert \
-density %sx%s -background black %s %s -append -strip -quality 75 %s' \
    % (x_resolution, y_resolution, image, copy_location, output_full_jpg)
    # subprocess.check_call(create_full_size_jpg_command, shell=True)
    print create_full_size_jpg_command
    tile_dimensions = tile_list(2428, 3228)
    create_xml(2428, 3228, num_of_tiles(tile_dimensions), jpeg_directory)

    for i, l in enumerate(reversed(tile_dimensions)):
        create_tiles(l[0], l[1], i, output_full_jpg, tile_directory)
        #print i, l[0], l[1]

    create_300dpi_jpg_command = '/usr/local/versions/ImageMagick-6.6.8b/bin/convert \
-density %sx%s -background black %s %s -append -strip -quality 75 \
-resample 300x300 -density 300x300 %s' \
    % (x_resolution, y_resolution, image, copy_location, output_300_dpi_jpg)
    # print create_300dpi_jpg
    #process_file.write('%s\n' % create_300dpi_jpg)
    # subprocess.check_call(create_300dpi_jpg_command, shell=True)
    print create_300dpi_jpg_command


    create_96dpi_jpg_command = '/usr/local/versions/ImageMagick-6.6.8b/bin/convert \
-density %sx%s -background black %s %s -append -strip \
-quality 75 -resample 96x96 -density 96x96 %s' \
    % (x_resolution, y_resolution, image, copy_location, output_96_dpi_jpg)
    # subprocess.check_call(create_96dpi_jpg_command, shell=True)
    print create_96dpi_jpg_command
    # process_file.write('%s\n' % create_96dpi_jpg)

    create_thumbnail_jpg_command = '/usr/local/versions/ImageMagick-6.6.8b/bin/convert \
-density %sx%s -background black %s %s -append -strip -quality 75 \
-resize \'143x143>\' %s' \
    % (x_resolution, y_resolution, image, copy_location, output_thumb_jpg)
    # subprocess.check_call(create_thumbnail_jpg_command, shell=True)
    print create_thumbnail_jpg_command
    # process_file.write('%s\n' % create_thumbnail_jpg)
    exit(1)


def create_tiles(x, y, n, jp, d):

    command = u'/usr/local/versions/ImageMagick-6.7.2/bin/convert \
%s -resize %sx%s\! -crop 256x256 -set filename:tile \'%%[fx:page.x/256]_%%[fx:page.y/256]\' \
+repage +adjoin \'%s/%s_%%[filename:tile].jpg\'' \
    % (jp, x, y, d, n)
    # process_file.write('%s\n' % create_full_size_tiles)
    # subprocess.check_call(command , shell=True)
    print command


def create_copyright_image(caption, pid):
    copy_location = '/dc/dsol/eurobo/validation_images/%s-copy.tif' % pid
    print copy_location
    copy_command = '/usr/local/versions/ImageMagick-6.4.5/bin/convert \
-pointsize 8 -density 200 -font "Futura-Book" -compress LZW \
-bordercolor white -border 10x10 -units PixelsPerInch \
-size 780 caption:"%s" -negate %s' \
% (caption, copy_location)
    # print copy_command
    # subprocess.check_call(copy_command, shell=True)

def copyright_statement(library, pid, sm):
    caption = u"Early European Books, Copyright \u00a9 %s ProQuest LLC.\\nImages reproduced by courtesy of %s.\\n%s" % (year, libraries[library], sm)
    #print pid, pid[-1:], type(int(pid[-1:]))
    # if int(pid[-1:]) == 1:
    if pid.strip().endswith('1'):
        create_copyright_image(caption, pid)
        npid = '%s0' % pid[:-1]
        create_copyright_image(caption, npid)
    else:
        create_copyright_image(caption, pid)


if __name__ == '__main__':

    data = db.records.find({'images_validated': {'$ne': ''}, 'images_processed_handover': ''})

    for record in data:
        print record['_id']
        ##pprint.pprint(record)
        image_details_lookup = get_image_details(record['path'])
        copy_statement = copyright_statement(record['library'], record['pid'], record['shelfmark'])
        print copy_statement
        # pprint.pprint(image_details_lookup)
        for root, directories, files in os.walk(record['path']):
            for jp2_file in files:
                if jp2_file[-3:].upper().endswith('JP2'):
                    jp2_path = os.path.join(root, jp2_file)
                    process_image(jp2_path, record['collection'])

        db.records.update_one(
           {'_id': record['_id']},
           {'$set':
              {'images_processed_for_handover': str(today)}
           }
        )

    # /images/eurobo/jpeg/Collection5/den/kbd/all/110604003786/001/den-kbd-all-110604003786-001-0039R_300.jpg
    # /dc/dsol/eurobo//jpeg/Collection7/ned/kbn/all/000000021163/000/ned-kbn-all-00021163-000-0000F.jp2
    # /images/eurobo/jpeg/Collection5/den/kbd/all/110604003786/001/den-kbd-all-110604003786-001-0039R_96.jpg
    # /images/eurobo/jpeg/Collection5/den/kbd/all/110604003786/001/den-kbd-all-110604003786-001-0039R.thumb.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/ImageProperties.xml
    # <IMAGE_PROPERTIES WIDTH="1536" HEIGHT="2216" NUMTILES="78" NUMIMAGES="1" VERSION="1.8" TILESIZE="256" />
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0
    # /dc/dsl/eurobo/zoomify/Collection7/ned/kbn/all/00021163/000/ned-kbn-all-00021163-000-0000F/TileGroup0
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/0-0-0.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/1-0-0.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/1-0-1.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/2-0-0.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/2-0-1.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/2-0-2.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/2-1-0.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/2-1-1.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/2-1-2.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/3-0-0.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/3-0-1.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/3-0-2.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/3-0-3.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/3-0-4.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/3-1-0.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/3-1-1.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/3-1-2.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/3-1-3.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/3-1-4.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/3-2-0.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/3-2-1.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/3-2-2.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/3-2-3.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/3-2-4.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-0-0.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-0-1.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-0-2.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-0-3.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-0-4.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-0-5.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-0-6.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-0-7.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-0-8.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-1-0.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-1-1.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-1-2.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-1-3.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-1-4.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-1-5.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-1-6.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-1-7.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-1-8.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-2-0.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-2-1.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-2-2.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-2-3.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-2-4.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-2-5.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-2-6.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-2-7.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-2-8.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-3-0.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-3-1.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-3-2.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-3-3.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-3-4.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-3-5.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-3-6.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-3-7.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-3-8.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-4-0.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-4-1.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-4-2.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-4-3.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-4-4.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-4-5.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-4-6.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-4-7.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-4-8.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-5-0.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-5-1.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-5-2.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-5-3.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-5-4.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-5-5.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-5-6.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-5-7.jpg
    # /images/eurobo/zoomify/Collection7/ned/kbn/all/00011121/001/ned-kbn-all-00011121-001-0341L/TileGroup0/4-5-8.jpg



# /usr/local/versions/ImageMagick-6.7.2/bin/convert /dc/dsol/eurobo/validation_images/jpeg/Collection5/ned/kbn/all/00008012/000/ned-kbn-all-00008012-000-0000B.jpg -resize 151x201\! -crop 256x256 -set filename:tile '%[fx:page.x/256]_%[fx:page.y/256]' +repage +adjoin '/dc/dsol/eurobo/validation_images/zoomify/Collection5/ned/kbn/all/00008012/000/ned-kbn-all-00008012-000-0000B/TileGroup0/0_%[filename:tile].jpg'
# /usr/local/versions/ImageMagick-6.7.2/bin/convert /dc/dsol/eurobo/validation_images/jpeg/Collection5/ned/kbn/all/00008012/000/ned-kbn-all-00008012-000-0000B.jpg -resize 303x403\! -crop 256x256 -set filename:tile '%[fx:page.x/256]_%[fx:page.y/256]' +repage +adjoin '/dc/dsol/eurobo/validation_images/zoomify/Collection5/ned/kbn/all/00008012/000/ned-kbn-all-00008012-000-0000B/TileGroup0/1_%[filename:tile].jpg'
# /usr/local/versions/ImageMagick-6.7.2/bin/convert /dc/dsol/eurobo/validation_images/jpeg/Collection5/ned/kbn/all/00008012/000/ned-kbn-all-00008012-000-0000B.jpg -resize 607x807\! -crop 256x256 -set filename:tile '%[fx:page.x/256]_%[fx:page.y/256]' +repage +adjoin '/dc/dsol/eurobo/validation_images/zoomify/Collection5/ned/kbn/all/00008012/000/ned-kbn-all-00008012-000-0000B/TileGroup0/2_%[filename:tile].jpg'
# /usr/local/versions/ImageMagick-6.7.2/bin/convert /dc/dsol/eurobo/validation_images/jpeg/Collection5/ned/kbn/all/00008012/000/ned-kbn-all-00008012-000-0000B.jpg -resize 1214x1614\! -crop 256x256 -set filename:tile '%[fx:page.x/256]_%[fx:page.y/256]' +repage +adjoin '/dc/dsol/eurobo/validation_images/zoomify/Collection5/ned/kbn/all/00008012/000/ned-kbn-all-00008012-000-0000B/TileGroup0/3_%[filename:tile].jpg'
# /usr/local/versions/ImageMagick-6.7.2/bin/convert /dc/dsol/eurobo/validation_images/jpeg/Collection5/ned/kbn/all/00008012/000/ned-kbn-all-00008012-000-0000B.jpg -resize 2428x3228\! -crop 256x256 -set filename:tile '%[fx:page.x/256]_%[fx:page.y/256]' +repage +adjoin '/dc/dsol/eurobo/validation_images/zoomify/Collection5/ned/kbn/all/00008012/000/ned-kbn-all-00008012-000-0000B/TileGroup0/4_%[filename:tile].jpg'

'''

'''
