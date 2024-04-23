#!/usr/local/bin/python

# Script to check whether BPC has any missing images that have been threaded, or images delivered that haven't been threaded.

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))


from optparse import OptionParser

import lxml.etree as ET

from commonUtils.fileUtils import locate

# User specified options - currently only target directory, but using just in case we want to specify file output directories in future

parser = OptionParser()

parser.add_option("-d", "--dir", dest="directory", help="Target directory for files", metavar="DIR")

(options, args) = parser.parse_args()

imglst = []
thrdlst = []
filelup = {}
fileout = []

# Walks through the specified directory and finds all the jpgs and the xmls.

for nfile in locate('*', root=options.directory):
    if nfile.endswith('.jpg'):
        imglst.append(os.path.basename(nfile))
    if nfile.endswith('.xml'):
        nwfile = nfile

        tree = ET.parse(nwfile, ET.XMLParser(remove_blank_text=True, resolve_entities=True))
        root = tree.getroot()

# Idenfies the <page_ref> tag in the XML files and creates a list of all the values (the 'threads), and a dictionary of value to the file the value comes from:

        for pageref in root.findall(".//page_ref"):
            pageref = pageref.text
            thrdlst.append(pageref)
            filelup[pageref] = nwfile

# Dedupes the list of threads:

thrdlst = list(set(thrdlst))

# Compares the threads to the images and looks for threads that don't appear in the image list

for item in thrdlst:
    if item in imglst:
        pass
    else:
        itemsrc = filelup.get(item)
        fileout.append("Image link %s from %s does not exist as an image" % (item, itemsrc))

# Compares the images to the threads and looks for images that don't appear in the thread list

for item in imglst:
    if item in thrdlst:
        pass
    else:
        fileout.append("%s is not linked to a record" % item)

outfile = os.getcwd() + '/orphan_image_check.txt'

with open(outfile, 'w') as outf:
    for item in fileout:
        outf.write('%s\n' % (item))
