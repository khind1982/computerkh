#!/usr/bin/env python
# coding=utf-8

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import lxml.etree as ET
import shutil

from commonUtils.fileUtils import locate

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
                        "S":"Clasps, ties or other closures"}

imagedict = {}
recdict = {}

try:
    filesystem = sys.argv[1]
    batch = sys.argv[2]
except IndexError:
    print "Usage: %s [file system] [batch]\n" % __file__
    exit(1)

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

modsloc = '%s/Incoming/%s' % (filesystem, batch)

for f in locate('*-[0-9][0-9][0-9].xml', modsloc):
    root = ET.parse(f).getroot()
    
    imgrp = [i for i in root.findall('.//{*}file') if i.attrib['ID'].startswith('IMG')]
    struct = [i for i in root.findall('.//{*}structMap/{*}div/{*}div')]
    for i in struct:
        content = i.attrib['TYPE']
        contents = []
        fileid = i.find('.//{*}area').attrib['FILEID']
        if '|' in content:
            for a in chunkstring(content.split('|')[1], 2):
                if a[0].isalpha() and len(a) == 2:
                    try:
                        contents.append(pagecontent_lookup[a[0]])
                    except KeyError:
                        pass
            
            filedets = [i for i in imgrp if i.attrib['ID'] == fileid]
            filename = filedets[0].find('.//{*}FLocat').attrib['{http://www.w3.org/1999/xlink}href']
            convertfn = filename.split('/')[-1].replace('.jp2', '')
            imagedict[convertfn] = ', '.join(contents)

parser = ET.HTMLParser()

presloc = '%s/Presenter' % filesystem

for f in locate('*.html', presloc):
    if os.path.basename(f).startswith('%s-' % batch):
        shutil.copy(f, f.replace('.html', '.bak'))
        root = ET.parse(f, parser).getroot()
        images = root.findall('.//img')
        for i in images:
            if i.attrib['title'] in imagedict.keys():
                # print i.attrib['title']
                i.attrib['title'] = '%s %s' % (i.attrib['title'], imagedict[i.attrib['title']])
        with open(f, 'w') as out:
            out.write(ET.tostring(root))

    
