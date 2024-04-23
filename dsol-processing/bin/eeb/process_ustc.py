#!/usr/local/bin/python2.6

import os
import re
import lxml.etree as etree
import optparse
import sys
import pprint
import xlrd
import subprocess
import site
site.addsitedir('/packages/dsol/lib/python2.6/site-packages')
site.addsitedir('/home/rschumac/svn/trunk/cstore/gs4/lib')
import namedentities
import codecs
from commonUtils import charUtils
from collections import defaultdict


parser = optparse.OptionParser()
parser.add_option('-s', '--source', dest="source", help='existing EEB data location')
parser.add_option('-d', '--destination', dest="destination", help='destination where new files will be created')
parser.add_option('-i', '--input', dest="input", help='full path to USTC spreadsheet')
parser.add_option('-x', '--sheet', dest="sheet", help='Name of XLS sheet containing data')
(options, args) = parser.parse_args()

if options.source is None or options.destination is None or options.input is None or options.sheet is None:
    parser.print_help()
    exit(1)

if not os.path.isdir(options.source) or not os.path.isdir(options.destination):
    print 'Directory not found!'
    exit(1)

if not os.path.isfile(options.input):
    print 'Spreadsheet not found. Please check path'
    exit(1)

data_lookup = {}
roots = []
t = []
temp_place = []
def fix_hex(char):
    fixed_char = '&#x00%s;' % char.group(0)[3:-1].upper()
    return fixed_char

def create_lookup(xls, sheet):
    spread_sheet = xlrd.open_workbook(xls)
    sheet1 = spread_sheet.sheet_by_name(sheet)
    for rownum in range(sheet1.nrows):
        temp = {}
        classifs = []
        pid = sheet1.cell(rowx=rownum, colx=0).value
        # print pid
        temp['place'] = sheet1.cell(rowx=rownum, colx=1).value
        temp['year'] = sheet1.cell(rowx=rownum, colx=2).value
        temp['language'] = sheet1.cell(rowx=rownum, colx=3).value

        c1 = sheet1.cell(rowx=rownum, colx=4).value
        temp['classification1'] = c1
        if c1 != '':
            classifs.append(c1)

        c2 = sheet1.cell(rowx=rownum, colx=5).value
        temp['classification2'] = c2
        if c2 != '':
            classifs.append(c2)

        c3 = sheet1.cell(rowx=rownum, colx=6).value
        temp['classification3'] = c3
        if c3 != '':
            classifs.append(c3)

        temp['classifications'] = ' - '.join(classifs)
        data_lookup[pid] = temp
    return data_lookup

def mkdir(s, d):
    if not s.endswith('/'):
        s = '%s/' % s
    newdir = '/'.join([d.rstrip('/'), s.replace(options.source, '').rstrip('/')])
    if not os.path.isdir(newdir):
        command = 'mkdir %s' % newdir
        subprocess.check_call(command, shell=True)

def main():
    ustc_lookup = create_lookup(options.input, options.sheet)

    #pprint.pprint(ustc_lookup)
    count = 0
    pqids = {}
    pids = []
    for root, dirs, files in os.walk(options.source):
        if 'Collection' in root and 'old' not in root:
            if root not in roots:
                roots.append(root)
                mkdir(root, options.destination)
            for f in files:
                if f.endswith('.xml') and f[:-4] in data_lookup:
                    #print f
                    input_file = os.path.join(root, f)

                    pqid = os.path.splitext(f)[0]
                    '''
                    if pqid not in pqids:
                        pqids[pqid] = [input_file]
                    else:
                        #pqids[pqid] = pqids[pqid].append(input_file)
                        pqids.setdefault(pqid, []).append(input_file)
                        if pqid not in pids:
                            pids.append(pqid)

                    '''
                    if pqid not in ustc_lookup:
                        print 'file not in lookup: %s' % input_file

                    dest_file = input_file.replace('/handover/eurobo/', options.destination)
                    in_data = open(input_file, 'r')
                    out = open(dest_file, 'w')
                    for line in in_data:
                        if line.strip().startswith('<place_of_publication>'):
                            cerl_split = line.split('</place_of_publication>')
                            cerl_data = cerl_split[1]
                            place_utf8 = namedentities.hex_entities(data_lookup[pqid]['place'])
                            place_utf8_converted = re.sub(r'&#x(.{2,3});', fix_hex, place_utf8)
                            if place_utf8_converted == '':
                                out.write(line)
                            else:
                                new_place = '<place_of_publication>%s</place_of_publication>\n' % (place_utf8_converted)
                                if cerl_split[0].split('>')[1] != place_utf8_converted:
                                    temp_val = '%s%s' % (cerl_split[0].split('>')[1], place_utf8_converted)
                                    if temp_val not in temp_place:
                                        temp_place.append(temp_val)
                                        #print '%s\t%s\t%s' % (pqid, cerl_split[0].split('>')[1].strip(), place_utf8_converted.strip())
                                #print '%s\t%s\t%s' % (pqid, cerl_split[0].replace('<place_of_publication>', ''), place_utf8_converted)
                                #print new_place
                                out.write(new_place)
                                if cerl_data != '':
                                    out.write(cerl_data)
                        elif line.strip().startswith('<language>'):
                            #print '%s\t%s\t%s' % (pqid, line.replace('<language>', '').replace('</language>', '').strip(), data_lookup[pqid]['language'].encode('utf-8'))
                            if data_lookup[pqid]['language'] != '':
                                if line.strip()[10:-11] != data_lookup[pqid]['language']:
                                    #printline = '%s\t%s\t%s' % (pqid, line.strip()[10:-11], data_lookup[pqid]['language'])
                                    #print printline
                                    new_lang = '<language>%s</language>\n' % (data_lookup[pqid]['language'].encode('utf-8'))
                                    out.write(new_lang)
                            else:
                                out.write(line)

                        elif line.strip().startswith('<displaydate>'):
                            #print '%s\t%s\t%s' % (pqid, line.replace('<displaydate>', '').replace('</displaydate>', '').strip(), data_lookup[pqid]['year'].encode('utf-8'))

                            if data_lookup[pqid]['year'] is '':
                                out.write(line)
                            else:
                                new_date = '<displaydate>%s</displaydate>\n' % (data_lookup[pqid]['year'].encode('utf-8'))
                                out.write(new_date)
                            #print new_date
                        elif line.strip().endswith('</rec_search>'):
                            c1 = data_lookup[pqid]['classification1'].encode('utf-8')
                            c2 = data_lookup[pqid]['classification2'].encode('utf-8')
                            c3 = data_lookup[pqid]['classification3'].encode('utf-8')
                            cs = data_lookup[pqid]['classifications'].encode('utf-8')
                            if c1 != '':
                                c1_line = '<classification1>%s</classification1>\n' % c1
                                out.write(c1_line)
                            if c2 != '':
                                c2_line = '<classification2>%s</classification2>\n' % c2
                                out.write(c2_line)
                            if c3 != '':
                                c3_line = '<classification3>%s</classification3>\n' % c3
                                out.write(c3_line)
                            if cs != '':
                                cs_line = '<classifications>%s</classifications>\n' % cs
                                out.write(cs_line)
                            out.write('</rec_search>\n')
                        #else:
                        #    out.write(line)

                    dest_file
                    count += 1
                    if (count % 100) == 1:
                        print pqid, count

    print 'done'

if __name__ == '__main__':
    main()




#/dc/dsol/eurobo/ustc_build/Collection4/kbdk/den-kbd-all-110408010217-001.xml
