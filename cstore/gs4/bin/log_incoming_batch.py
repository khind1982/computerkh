#!/usr/local/bin/python2.6

# Script to log incoming batches of AAA, WWD or EIMA content, creating a tab delimited log file at issue level, counting pages and records,

import os
import re
import datetime

# Defining lists to be used further down:

imglst2 = []
xmllst = []
outlist = []
reclst = []
reclst2 = []
imlst = []
imlst2 = []

# Import the OptionParser and define options, which the user calls with switches on the command line:

from optparse import OptionParser

parser = OptionParser()

parser.add_option("-d", "--dir", dest="foo", help="Target directory", metavar="DIRECTORY")
parser.add_option("-p", "--proj", dest="po", help="Name of project, e.g. aaa", metavar="NAME")

(options, args) = parser.parse_args()

# Functions for pulling out specific parts of a list

def getissue(s):
    return s[0:-8]

def getish(s):
    return s[0:-9]


def getpmid(s):
    return s[0:9]

def getishcode(s):
    return s[1:19]

def getdate(s):
    return s[0:10]

# Function for building a dictionary from a file specified in the script:

def lookup(filename, delimiter, comment='#'):
    luTable = {}
    with open(filename, 'r') as lutfile:
        for line in lutfile:
            if line.startswith(comment):
                continue
            else:
                split_line = line.split(delimiter, 1)
                luTable[split_line[0]] = split_line[1].rstrip()
    return luTable

# If the user specifies either -p wwd or -p aaa on the command line then...

if options.po == "wwd" or options.po == "aaa":

# ...Walk through the directories inside the specified root directory and create lists of the jpgs and xmls (including the directory path to each file)

    for root, dirs, files in os.walk(options.foo):
        for jpgs in files:
            if jpgs.endswith('.jpg'):
                njpg = os.path.join(root, jpgs)
                imglst2.append(njpg)

        for xmls in files:
            if xmls.endswith('.xml'):
                nxml = os.path.join(root, xmls)
                xmllst.append(nxml)

# Same as above for -p eima, but a special case because eima has extra types of jpgs that we don't want to create a list of:

elif options.po == "eima":

    for root, dirs, files in os.walk(options.foo):
        for jpgs in files:
            matchjpg = re.search(r'(.*-...\.jpg)', jpgs)
            if matchjpg is not None:
                njpg = os.path.join(root, jpgs)
                imglst2.append(njpg)

        for xmls in files:
            if xmls.endswith('.xml'):
                nxml = os.path.join(root, xmls)
                xmllst.append(nxml)


# Variables that create files for use later:

outfilename = options.foo + '.log'
reclup = 'reclup.lup'
imlup = 'imlup.lup'


# Creating dictionaries using the function defined above, and a couple of files already set up:

titledict = lookup('/dc/content_ops_management/Utils/pmid-title.lut', '|')
blockdict = lookup('/packages/dsol/platform/libdata/pmid-blocked.lut', '|')


# Open the log file created above so that we can write to it:

with open(outfilename, 'w') as outfile:

# For each line in the xmllst, split the line wherever it finds '/xml', and append the relevant parts of the split line to the reclst (project dependant):

    for item in xmllst:
        if options.po == "wwd" or options.po == "aaa":
            path3 = item.split('/xml')
            reclst.append(path3[0])
        elif options.po == "eima":
            path3 = item.split('/')
            reclst.append(path3[0] + '/' + path3[1] + '/' + path3[2])

# Count the number of records listed in reclst and store in a lookup style file (reclup.lup) for use later:

    for item in reclst:
        reccount = reclst.count(item)

        reclst2.append(item + '|' + str(reccount) + '\n')

    reclst2 = set(reclst2)

    with open(reclup, 'w') as lup:
        for item in reclst2:
            lup.write(item)
        reclst2 = []

# Turn the finished reclup.lup file into a python dictionary for use later:

    recdict = lookup('reclup.lup', '|')

# Look at each line in imglst2 and split it whenever python finds '/images' '/jpeg' or '/Page'

    for item in imglst2:
        path2 = re.split('/images|/jpeg|/Page', item)
        imlst.append(path2[0])

# Count the number of images listed in imlst and store in a lookup style file (imlup.lup) for use later:

    for item in imlst:
        pagecount = imlst.count(item)

        imlst2.append(item + '|' + str(pagecount) + '\n')
    imlst2 = set(imlst2)

    with open(imlup, 'w') as lup2:
        for item in imlst2:
            lup2.write(item)
        imlst2 = []

# Turn the finished imlup.lup file into a python dictionary for use later:

    imdict = lookup('imlup.lup', '|')

# The part where we start assembling each line, to be written to the batch log file:

# For each line in imglst2, split the line whenever a '/' is found, and store different parts of the line in variables

    for item in imglst2:
        nitem = item.split('/')
        media = options.foo
        if options.po == "wwd" or options.po == "aaa":
            batch = options.foo
        elif options.po == "eima":
            batch = nitem[1]

# Splitting the 'nitem' variable again whenever a _ or a - is found, and storing bits of the split:

        filesplit = re.split('_|-', nitem[-1])

        if options.po == "wwd" or options.po == "aaa":
            PMID = filesplit[0]
            date = filesplit[1]
            ishyear = filesplit[1][0:4]

        elif options.po == "eima":
            PMID = filesplit[1]
            date = filesplit[2]

# Not sure what this bit is for, but I'm guessing it's something AAA/WWD specific that I couldn't be bothered to put options in for.

        for issup in nitem:
            if 'issue' in issup or 'supplement' in issup:
                issuesup = issup
            else:
                pass

# More 'part' collecting for the different columns in the tab file:

        issue = getissue(nitem[-1])

        if options.po == "wwd":
            innoishcode =  date + '_' + issuesup

        else:
            pass
        path = re.split('/images|/jpeg|/Page', item)
        patha = path[0]
        patha = str(patha)
        ims = imdict[patha]
        recs = recdict[patha]
        title = titledict[PMID]
        ishcode = getishcode(path[1])
        now = datetime.datetime.now()
        recdate = str(now)
        recdate = getdate(recdate)

# This part checks if an issue is blocked and assigns a status accordingly:

        if PMID in blockdict:
            blocked = blockdict[PMID]
        else:
            blocked = ''

# Final assembly of the lines that will be written to the log file:

        if options.po == 'aaa':
            outlist.append("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (batch, PMID, patha, title, date, issuesup, recdate, recs, ims, blocked))

        elif options.po == 'wwd':
            outlist.append("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (batch, PMID, patha, ishcode, title, ishyear, date, issuesup, innoishcode, recdate, recs, ims))

        elif options.po == 'eima':
            outlist.append("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (media, batch, PMID, patha, title, date, recdate, recs, ims, blocked))


    outlist = set(outlist)

# Writing what we've just assembled to the log file:

    for item in outlist:
        outfile.write(item)
    outlist = []

os.remove('imlup.lup')
os.remove('reclup.lup')
