#!/usr/local/bin/python

# Script to log incoming batches of BP3 and 4 content, creating a tab delimited log file at issue level, counting pages and records

import datetime
import os
import sys
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

# Columns needed are:
# Delivery Date|Batch reference|Batch note|Path|Publication Group ID|Publication Group title|Publication Date|Source Type|Total Pages|Total Records|Cost components|Resupply?|Comments

from commonUtils.fileUtils import _defaultPath, buildLut, locate
from commonUtils.listUtils import uniq
from collections import defaultdict


from optparse import OptionParser

import lxml.etree as ET

parser = OptionParser()

# Option -n adds a note to the notes column, can be something like "Redelivery" or "Benchmark"
# Option -r allows you to specify a delivery date if it's different from the date you're running the script
# Option -s is a switch that allows the user to turn off resupply searching.

parser.add_option("-n", "--batn", dest="batchnote", help="Note on the batch being delivered", metavar="NOTE")
parser.add_option("-r", "--deldate", dest="deldate", help="Date of batch delivery", metavar="NOTE")
parser.add_option("-s", "--searchoff", action="store_false", dest="ressearch", help="Switch resupply search off", default=True)

(options, args) = parser.parse_args()

issuelst = []
imgnums = []
imgnums2 = []
recnums = []
recnums2 =[]
issuelst2 = []
finallst = []

d1 = defaultdict(list)
d2 = defaultdict(list)



if options.batchnote is None:
    options.batchnote = '\t'

if options.deldate is None:
    options.deldate = datetime.datetime.today().strftime('%d/%m/%Y')

try:
    directory = args[0]
except IndexError:
    print "Please specify a delivery batch directory"
    parser.print_help()
    exit(1)

# Lookups which define the journal titles based on journal ID, and the issues we've already received.

pubtitles = buildLut('pmid-title.lut')
supplylist = '/dc/bpc-images/utils/content_supplied_todate.lut'
supplydict = buildLut('/dc/bpc-images/utils/content_supplied_todate.lut')

with open(supplylist, 'r') as updatesl:
    for line in updatesl:
        issuelst2.append(line)

# Finds all the files in the directory specified

for nfile in locate('*', root=directory):
    if nfile.endswith('.jpg'):
        imgnums.append((os.path.basename(nfile))[0:21])
    if nfile.endswith('.xml'):
        recnums.append((os.path.basename(nfile))[0:21])
        if nfile.endswith('0001.xml'):
            issuelst.append(nfile)

for item in recnums:
    reccount = item, str(recnums.count(item))
    recnums2.append(reccount)

for item in imgnums:
    imcount = item, str(imgnums.count(item))
    imgnums2.append(imcount)

recnums2 = list(set(recnums2))
imgnums2 = list(set(imgnums2))

for k, v in recnums2:
    d1[k].append(v)

for k, v in imgnums2:
    d2[k].append(v)

# Collecting up the parts for constructing the log file

for item in issuelst:
    issue = item.split('/')[-1][0:21]
    issuelst2.append(('%s|%s\n') % (issue, options.deldate))
    tree = ET.parse(item, ET.XMLParser(remove_blank_text=True, resolve_entities=True))
    root = tree.getroot()
    xmlbatch = root.get("delbatch")
    path = item[0:-30]
    pubtitle = pubtitles[re.split('/|_', item)[-4]]
    issuedate = item.split('_')[-3]
    jid = re.split('/|_', item)[-4]
    sourcetype = root.find("record/journal/scantype/scansource").text
    pages = str(d2[issue]).translate(None, '[]\'')
    records = str(d1[issue]).translate(None, '[]\'')
    try:
        if options.ressearch is not False:
            resupply = supplydict[issue]
        else:
            resupply = '\t'
    except KeyError:
        resupply = '\t'
    finallst.append(('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n') % (options.deldate, xmlbatch, options.batchnote, path, jid, pubtitle, issuedate, sourcetype, pages, records, resupply))

try:
    outfname = "%s/%s_delivery.log" % (directory, xmlbatch)
except NameError:
    print path

with open(outfname, 'w') as outfile:
    for item in finallst:
        outfile.write(item)

issuelst2 = uniq(issuelst2)

with open(supplylist, 'w') as add2supply:
    for item in issuelst2:
        add2supply.write(item)
