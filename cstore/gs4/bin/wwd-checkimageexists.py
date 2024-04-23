#!/usr/local/bin/python2.6
import re
import os

imglst = []
imglst2 = []
badlst = []
badlst2 = []
imref = []

# Section to determine what to do with option switches that are input by user

from optparse import OptionParser

parser = OptionParser()

parser.add_option("-o", "--out", dest="bar", help="Directory for outputfiles", metavar="DIR")
parser.add_option("-d", "--dir", dest="foo", help="Target directory for XMLs", metavar="DIR")

(options, args) = parser.parse_args()


# Makes a list of all the jpegs in the target directory

for root, dirs, images in os.walk(options.foo):
    for jpgs in images:
        matchj = re.search(r'-[0-9][0-9][0-9].jpg', jpgs)
        if matchj is not None:
            imglst2.append(jpgs)


# Lists all the XML files and stores them in the variable "nfile"

for root, dirs, files in os.walk(options.foo):
    for xmls in files:
        if xmls.endswith('.xml'):
            nfile = os.path.join(root, xmls)

# Pulls out all the APS_page_image fields from the xml files in the target directory and adds them to a list

            with open(nfile, 'r') as thefile:
                for line in thefile:
                    match1 = re.search(r'<APS_page_image layout=".">(.*)</APS_page_image>', line)

                    if match1 is not None:
                        img = match1.group(1)
                        imglst.append(img)
                        imref.append(nfile + '\t' + img)

                    else:
                        pass

imref = list(set(imref))
out = options.bar + 'imrefs.txt'

with open(out, 'w') as imreffile:
    for item in imref:
        imreffile.write(item + '\n')

newimList = list(set(imglst))

# Compares the list of page_images and the list of actual images and writes missing ones to an outputfile

outfilename = options.bar + 'missingims.out'
with open(outfilename, 'w') as outfile:
    for item in newimList:

        if item in imglst2:
            pass

        else:
            badlst.append(item)

    badlst = list(set(badlst))

    for item in badlst:
        outfile.write(item + ' not found\n')

outfilename2 = options.bar + 'missingthreads.out'

with open(outfilename2, 'w') as outfile2:
    for item in imglst2:

        if item in newimList:
            pass

        else:
            badlst2.append(item)

    badlst2 = list(set(badlst2))

    for item in badlst2:
        outfile2.write(item + ' not threaded\n')
