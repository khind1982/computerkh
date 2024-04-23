#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Script to output mods files from a spreadsheet

import os
import sys

if os.path.isdir('../../../lib'):
    sys.path.append('../../../lib')
if os.path.isdir('/packages/dsol/opt/lib/python2.7/site-packages'):
    sys.path.append('/packages/dsol/opt/lib/python2.7/site-packages')

import boto3
import lxml.etree as ET
import xlrd

from StringIO import StringIO
from huTools import structured

# try:
#     infile = sys.argv[1]
#     outdir = sys.argv[2]
# except IndexError:
#     print "Usage: eeb-excel_to_mods.py [inputfile] [output directory]\n"
#     exit(1)

s3_client = boto3.client('s3')

inbucket = 'content-digitisation-incoming-dev'
outbucket = 'content-digitisation-outgoing-dev'

def processdata(inf):
    sheet = xlrd.open_workbook(inf).sheet_by_index(0)
    for rownum in range(1, sheet.nrows):
        rowdict = {}
        for col, cell in enumerate(sheet.row(rownum)):
            tag = sheet.cell_value(0, col).encode('latin-1')
            text = sheet.cell_value(rownum, col)
            if type(text) is float:
                text = str(int(text))
            if text is not '':
                rowdict[tag] = text
        if 'PublicationDateEnd' in rowdict.keys():
            rowdict['dateIssued'] = '%s-%s' % (rowdict['PublicationDateStart'], rowdict['PublicationDateEnd'])
            

        d = structured.dict2xml(rowdict, roottag='mod', pretty=True)
        xml_data = ET.fromstring(d)

        print ET.tostring(xml_data)

        try:
            mods_format = ET.XSLT(ET.parse('mods-eeb-scanlist.xsl'))
        except IOError:
            mods_format = ET.XSLT(ET.parse('//mclaren/eurobo/utils/mods-eeb-scanlist.xsl'))
        
        out_rec = mods_format(xml_data)

        if os.path.exists('/tmp') is True:
            outfile = '/tmp/%s.xml' % rowdict['pqid']
        else:
            outfile = '//mclaren/eurobo/incoming/from-scanlist/%s.xml' % rowdict['pqid']

        with open(outfile, 'w') as out:
            out.write(ET.tostring(out_rec, pretty_print=True))

def lambda_handler(event, context):
    src_file_full = event['Records'][0]['s3']['object']['key'] # gets the file path on s3
    dst_file = '/tmp/%s' % os.path.basename(src_file_full)
    s3_client.download_file(inbucket, src_file_full, dst_file)
    processdata(dst_file)

if __name__ == '__main__':
    try:
        processdata('2017-02-08_bnf_dep.xlsx')
    except IOError:
        processdata('//mclaren/eurobo/utils/input_scanlists/2017-02-08_bnf_dep.xlsx')