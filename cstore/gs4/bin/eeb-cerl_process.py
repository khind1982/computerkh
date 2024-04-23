#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'libdata/eeb'))

import lxml.etree as ET
from commonUtils.fileUtils import locate


try:
    indir = sys.argv[1]
except IndexError:
    print "Usage: eeb-cerl_process.py [input directory]\n" 
    exit(1)

parser = ET.XMLParser(remove_blank_text=True, encoding='ISO-8859-1', huge_tree=True)


def returnNotMatches(dictlist, newlist):
    comp = [x for x in newlist if x not in dictlist]
    if len(comp) > 0:
        return comp

# Function to make a tab delimited report of what is in the cerl data dump

# def cerl_report(infile):
#     rec = 0
#     root = ET.iterparse(infile, remove_blank_text=True, encoding='ISO-8859-1', huge_tree=True)
#     for _, record in root:
#         if record.tag == '{http://www.loc.gov/MARC21/slim}record':
#             rec += 1
#             if rec == 10:
#                 exit(1)
#             datatype = record.find('./{*}controlfield').text
#             print datatype
#             # print ET.tostring(record, pretty_print=True)

def cerl_fromdata(input_dir):
    cerlfields = ['pop_cerl', 'aut_other_cerl', 'aut_cerl', 'pub_cerl']
    cerldict = {}
    for f in locate('*.xml', input_dir):
        
        root = ET.parse(f).getroot()
        for i in cerlfields:
            pop_cerl = root.findall('.//%s' % i)
            
            if len(pop_cerl) > 0:
                # print ET.tostring(pop_cerl[0], pretty_print=True)
                for ci in pop_cerl:
                    # print ET.tostring(ci)
                    if ci.find('.//%s_mainentry' % i) is not None:
                        key = '%s\t%s' % (i.replace('_other_', '_'), ci.find('.//%s_mainentry' % i).text.encode('utf-8'))
                        try:
                            value = [ele.text.encode('utf-8') for ele in ci.findall('.//%s_variant' % i) if ele.text is not None]
                        except AttributeError:
                            print 'AttributeError: %s' % ET.tostring(ci)
                        if key not in cerldict.keys():
                            cerldict[key] = value
                        else:
                            nomatch = returnNotMatches(cerldict[key], value)
                            if nomatch != None:
                                print 'Not matching:', nomatch
                                for v in value:
                                    print 'Appending values to key: %s' % v
                                    cerldict[key].append(v)

    outfile = '/dc/eurobo/editorial/cerl/cerltabbed.txt'

    with open(outfile, 'w') as out:
        for k in cerldict.keys():
            out.write('%s\t%s\t%s\n' % (k, '; '.join(list(set(cerldict[k]))), len(list(set(cerldict[k])))))
            
if __name__ == '__main__':
    cerl_fromdata(indir)                    