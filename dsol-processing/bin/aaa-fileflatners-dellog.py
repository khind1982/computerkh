#!/usr/local/bin/python2.6

# Script to log incoming batches of AAA from File Flatners

import os
import datetime


from optparse import OptionParser

parser = OptionParser()

parser.add_option("-d", "--dir", dest="directory", help="Target directory", metavar="DIRECTORY")

(options, args) = parser.parse_args()

imglst=[]
loglst=[]

# Walks through the specified directory and finds all the jpgs, adding them to a list. FIXME: convert the os.walk to dsol locate function.

for root, dirs, files in os.walk(options.directory):
    for jpgs in files:
        if jpgs.endswith('.jpg'):
            jpissue = jpgs.split('-')[0]
            imglst.append(jpissue)

# Manipulates the list to get the information needed for the tab file, then adds the information to a new list

for item in imglst:
    issue = item
    batchid = options.directory
    date_rec = datetime.date.today()
    pagecount = imglst.count(item)
    loglst.append('%s\t%s\t%s\t%s\n' % (batchid, date_rec, issue, pagecount))

# Sorts and dedupes the list

loglst = list(set(loglst))

# Defining an output file location and name

outfile = ('%s/%s.log' % (os.getcwd(), options.directory))

# Writing the loglst to the output file

with open(outfile, 'w') as outf:
    for item in loglst:
        outf.write(item)

