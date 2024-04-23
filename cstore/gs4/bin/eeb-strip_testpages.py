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
    outdir = sys.argv[2]
except IndexError:
    print "Usage: eeb-strip_testpages.py [input directory] [output dir]\n"
    exit(1)

if indir.replace('/', '') == outdir.replace('/', ''):
    print "Input directory cannot be the same as the output directory\nUsage: %s [input directory] [output dir]\n" % os.path.basename(__file__)
    exit(1)

if not os.path.exists(outdir):
    os.makedirs(outdir)

def strip_testpages(inputdir):
    for f in locate('*.xml', inputdir):
        
        root = ET.parse(f).getroot()

        testpages = [i for i in root.findall('.//pagetype') if i.text == 'Test page']
        if len(testpages) > 0:
            for i in testpages:
                parent = i.getparent()
                parent.getparent().remove(parent)
        
        itemimages = root.findall('.//itemimage')
        volumeimages = root.findall('.//volumeimage')

        for imageblock in itemimages, volumeimages:
            if len(imageblock) > 0:
                if int(imageblock[0].find('.//imagenumber').text) != 1:
                    for i in imageblock:
                        i.find('.//imagenumber').text = str(int(i.find('.//imagenumber').text) - 1)

        outfile = '%s/%s' % (outdir, os.path.basename(f))

        with open(outfile, 'w') as out:
            out.write(ET.tostring(root, pretty_print=True))

if __name__ == '__main__':
    strip_testpages(indir)                    