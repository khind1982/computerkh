#!/usr/bin/env python2.6
# coding=utf-8
import sys
sys.path.insert(0, "/packages/dsol/lib/python2.6/site-packages")
sys.path.insert(0, "/packages/dsol/opt/lib/python2.7/site-packages")
from huTools import structured
import xml.etree.cElementTree as ET
import lxml.etree as etree
from StringIO import StringIO
import os
import re
import pymarc
import pprint
import datetime
import pymongo
import json

import xlwt
today = datetime.date.today()
#print type(today)
client = pymongo.MongoClient('mongodb://mongodb-node1')

db = client.eeb

db.lookups_collection.drop()
db.lookups_library.drop()

out_dir = '/home/rschumac/work/eeb_new/xslt'


pagecontent_lookup = {  "A":"Coat of arms",
                        "B":"Chart",
                        "C":"Form",
                        "D":"Genealogical table",
                        "E":"Handwritten page/insert",
                        "F":"Illuminated lettering",
                        "G":"Illustration",
                        "H":"Map",
                        "I":"Manuscript (i.e. handwritten) marginalia and other annotation",
                        "J":"Printed marginalia",
                        "K":"Musical notation",
                        "L":"Plate",
                        "M":"Plan",
                        "N":"Portrait",
                        "O":"Printers Mark - Colophon",
                        "P":"Printers Mark - Title Page",
                        "Q":"Rubricated text",
                        "R":"Illustrated page borders",
                        "S":"Clasps, ties or other closures"
                    }

pagetype_000_lookup = {
    'F': 'Front board',
    'S': 'Spine',
    'B': 'Back board',
    'X': 'Head edge',
    'Y': 'Tail edge',
    'Z': 'Foredge',

}

db.records.drop()

recs = [{
            'pid': 'hin-wel-all-00010082-001',
            'high': 10082,
            'lid': '(ID:537175904)|843487260',
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
            'path': '/dc/kbnl-coll6/Incoming/20151106/ned-kbn-all-00021163',
            'mets_received': '2015-11-06',
            'mods_generated': '2015-11-06',
            'images_processed__validation': '',
            'images_validated': '',
            'images_processed_handover': '',
            'dates_validated': '',
            'authors_validated': ''
        },
        {
            'pid': 'hin-wel-all-00000380-001',
            'high': 10082,
            'lid': '(ID:537175904)|843487260',
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
            'images_processed__validation': '2015-03-08',
            'images_validated': '',
            'images_processed_handover': '',
            'dates_validated': '',
            'authors_validated': ''
        }]


for rec in recs:
    db.records.insert_one(rec)

library = [
            {   'id': 'kbn',
                'library': 'Koninklijke Bibliotheek, Nationale bibliotheek van Nederland'
            },
            {   'id': 'wel',
                'library': 'Wellcome library'
            }
          ]

for lib in library:
    db.lookups_library.insert_one(lib)


collection = [
                {   'id': 'kbn-all',
                    'collection': 'KB (Den Haag), Netherlands'
                },
                {   'id': 'bnc-mag',
                    'collection': 'Magliabechiano Colleciton, BNCF (Florence), Italy'
                }
             ]
for coll in collection:
    db.lookups_collection.insert_one(coll)

# /dc/kbnl-coll6/Incoming/20151106/ned-kbn-all-00021163/ned-kbn-all-00021163-000/
# Book: f, b, s, x, y, z l1, r2, l3, r4
# Pamphlet: b, f, u
# sometimes no 000 folder: kbnl/6/20151106/641
#temp_mets_dir = '/dc/kbnl-coll6/Incoming/20151106'
temp_mets_dir = '/dc/wellcome-coll5/Incoming/20140204'

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

for i, data in enumerate(db.records.find()):
    #insert_image_data = [{'image': 'ned-kbn-all-00021163-000-0003L.jp2','order': '0','imagenumber': '1','orderlabel': 'BB','label': 'Back endplate','pagetype': 'none','pagecontent': [{'type': 'Illuminated lettering','number': '1'}],'colour': 'monochrome'},{'image': 'ned-kbn-all-00021163-000-0003R.jp2','order': '0','imagenumber': '2','orderlabel': 'BB','label': 'Back endplate','pagetype': 'none','pagecontent': [{'type': 'Illuminated lettering','number': '1'},{'type': 'manuscript','number': '1'}],'colour': 'monochrome'}]
    insert_image_data = []

    pid = data['pid']
    print(pid)
    short_pid = pid[:-4]
    #print short_pid

    mets_dir = os.path.join(temp_mets_dir, short_pid)
    print mets_dir

    mets_files = os.listdir(mets_dir)
    mets_files.sort()
    # print mets_files
    for i, mets_file in enumerate(mets_files[1:]):
        mets_xml_dir = os.path.join(mets_dir, mets_file)
        print mets_xml_dir
        mets_xml_file_name = '%s-%03d.xml' % (short_pid, i+1)
        mets_xml_file = os.path.join(mets_xml_dir, mets_xml_file_name)
        mets_xml_data = etree.parse(mets_xml_file)
        # print mets_xml_file_name, mets_xml_data
        #print etree.tostring(mets_xml_data, pretty_print=True)

        items = mets_xml_data.xpath("//mets:amdSec[starts-with(@ID, 'IMGPARAM')]", namespaces={'mets': 'http://www.loc.gov/METS/'})

        for j, item in enumerate(items):
            image_data = {}
            imageid = item[0].attrib['ID']
            divid = '//mets:div[@ID="DIVP%s"]' % int(re.search('\d+', imageid).group())
            #print divid
            div =  mets_xml_data.xpath(divid, namespaces={'mets': 'http://www.loc.gov/METS/'})
            #print div

            image = item.xpath('//mix:objectIdentifierValue', namespaces={'mix': 'http://www.loc.gov/mix/v20'})
            image_data['image'] = image[j].text[:-4]
            image_data['order'] = div[0].attrib['ORDER']
            orderlabel = div[0].attrib['ORDERLABEL']
            if orderlabel != '':
                if '|' in orderlabel:
                    image_data['orderlabel'] = orderlabel.split('|')[1]
            image_data['label'] = div[0].attrib['LABEL']
            type_tag = div[0].attrib['TYPE']
            if '|' in type_tag:
                image_data['imagenumber'] = j + 1
                image_data['colour'] = type_tag.split('|')[0]
                #print type_tag.split('|')[1]
                pagecontents = []
                for a in chunkstring(type_tag.split('|')[1], 2):
                    if a[0].isalpha() and len(a) == 2:
                        temp_pagecontents = {}
                        temp_pagecontents['type'] = pagecontent_lookup[a[0]]
                        temp_pagecontents['number'] = a[1]
                        #print temp_pagecontents
                        pagecontents.append(temp_pagecontents)
                        #print pagecontent_lookup[a[0]], a[1]
                image_data['pagecontent'] = pagecontents
            else:
                image_data['imagenumber'] = j + 1
                image_data['colour'] = type_tag

            insert_image_data.append(image_data)
    data['itemimagefiles'] = insert_image_data
    # pprint.pprint(data)
    # exit(1)

    lib_code = pid.split('-')[1:]
    #print lib_code
    library_full = db.lookups_library.find({'id': lib_code})
    #print library_full[0]['library']


    d = structured.dict2et(data, roottag='mod', listnames={'authors': 'author', 'titles': 'title', 'notes': 'note', 'languages': 'language', 'itemimagefiles': 'imageitem'})
    xml_raw = ET.tostring(d)
    xml = StringIO(xml_raw)
    xml_data = etree.parse(xml)
    # print etree.tostring(xml_data, pretty_print=True, xml_declaration=True, encoding='utf-8')
    xml_raw = ET.tostring(d)
    xml = StringIO(xml_raw)
    xml_data = etree.parse(xml)
    handover = etree.parse('/home/rschumac/work/eeb_new/handover.xsl')
    read_xsl = etree.XSLT(handover)
    out_rec = read_xsl(xml_data)
    print etree.tostring(out_rec, pretty_print=True, xml_declaration=True, encoding='utf-8')
    '''
    xls_out_filepath = os.path.join(out_dir, xls_filename)
    out = open(xls_out_filepath, 'w')
    xls_record = etree.tostring(xls_output, pretty_print=True, xml_declaration=True, encoding='utf-8')
    #print record
    out.write(xls_record)
    out.close()
    os.chmod(outfilepath, 0777)
    '''



'''
# example_mods = etree.parse('/dc/eurobo/scanlists/kbdk/collection_4_onwards/scanlist/scanlist_4/scanlist_MODS_4/den-kbd-all-130018781698-001.xml')
example_mods = etree.parse('/home/rschumac/work/eeb_new/marcbase_1801-10.xml')
marc_pretransformed = etree.tostring(example_mods, pretty_print=True, xml_declaration=True, encoding='utf-8')
print marc_pretransformed

marc_output = read_xsl(example_mods)

marc_record = etree.tostring(marc_output, pretty_print=True, xml_declaration=True, encoding='utf-8')
print marc_record
exit(1)
writer = pymarc.MARCWriter(file('/home/rschumac/work/eeb_new/marcbinary.mrc', 'w'))

records = pymarc.map_xml(writer.write, marc_record)

writer.close()
# mv ./current/data/dump-music_{date}.txt ./current/data/dump-iimp_{date}.txt



number becomes attribute "number"

'''

'''
[
    {
        'image': 'ned-kbn-all-00021163-000-0003L.jp2',
        'order': '0',
        'imagenumber': '1',
        'orderlabel': 'BB',
        'label': 'Back endplate',
        'pagetype': 'none',
        'pagecontent': [
                            {
                                'type': 'Illuminated lettering',
                                'number': '1'
                            }
                       ],
        'colour': 'monochrome'
    },
    {
        'image': 'ned-kbn-all-00021163-000-0003R.jp2',
        'order': '0',
        'imagenumber': '2',
        'orderlabel': 'BB',
        'label': 'Back endplate',
        'pagetype': 'none',
        'pagecontent': [
                            {
                                'type': 'Illuminated lettering',
                                'number': '1'
                            },
                            {
                                'type': 'manuscript',
                                'number': '1'
                            }
                       ],
        'colour': 'monochrome'
    }
]
'''
'''

import sys
sys.path.insert(0, "/packages/dsol/lib/python2.6/site-packages")
sys.path.insert(0, "/packages/dsol/opt/lib/python2.7/site-packages")
# mongodb 172.18.26.91/eebmaster -u eebmaster -p eebmaster
import pymongo

client = pymongo.MongoClient('mongodb://172.18.26.91')
client.eebmaster.authenticate('eebmaster', 'eebmaster')

db = client.eebmaster

cols = db.collection_names()
for c in cols:
    print c

for i, data in enumerate(db.pqids.find()):
    print data
'''
