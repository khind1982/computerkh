#!/usr/bin/env python2

# Sampler for selecting records to validate

import os
import re
import sys
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.append('/packages/dsol/lib/python2.6/site-packages')

import lxml.etree as ET
import shutil
import xlrd
import xlwt
from xlutils.copy import copy

from collections import OrderedDict
from datetime import datetime, date
from decimal import *
from random import sample

from commonUtils.fileUtils import locate

# User specified options; input directory and output directory.

# Script enhancements:

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'product',
        help='Name of the product as it appears appended to the "-images" directory')
    parser.add_argument(
        'batch',
        help='Name of the batch, e.g. HBA0001, VIA0099, etc.')
    parser.add_argument(
        'level',
        choices=['loose', 'average', 'tight'], help='Inspection level (loose/average/tight')
    parser.add_argument(
        '--pdflevel',
        dest='pdflevel', choices=['loose', 'average', 'tight'])
    return parser.parse_args()

args = parse_args(sys.argv[1:])

if args.pdflevel is None:
    pdflevel = args.level
else:
    pdflevel = args.pdflevel

if args.product == 'via':
    product = 'vogueitalia'
else:
    product = args.product

if not os.path.exists('/dc/%s-images' % product):
    print 'Product code is not valid or /dc/%s-images does not exist. Choose from:\nbpc\nbpd\nwma\nwmb\nvia\nhba' % product
    exit(1)

if not os.path.exists('/dc/%s-images/editorial/%s' % (product, args.batch)):
    print 'Directory %s does not exist. Please ensure batch is in editorial directory and run again' % '/dc/%s-images/editorial/%s' % (product, args.batch)
    exit(1)

# We don't want sample sizes to get too big by accident, so this part forces the user to make it continue.

if os.path.exists('/dc/%s-images/samplings/%s' % (product, args.batch)):
    resp = raw_input('A sample already exists for %s in %s. Continue? (y/n):' % (args.batch, '/dc/%s-images/editorial/%s' % (product, args.batch)))
    if resp == 'y':
        pass
    elif resp == 'n':
        exit(1)
    else:
        print 'Response not recognised: %s. Exiting...' % resp
        exit(1)

loosedict = {(2, 15): (2, '0'),
             (16, 25): (3, '0'),
             (26, 90): (5, '0'),
             (91, 150): (8, '0'),
             (151, 280): (13, '0'),
             (281, 500): (20, '1'),
             (501, 1200): (32, '2'),
             (1201, 3200): (50, '3'),
             (3201, 10000): (80, '4'),
             (10001, 35000): (125, '5'),
             (35001, 150000): (200, '7'),
             (150001, 500000): (315, '9'),
             (500001, 1000000): (500, '12')}


averagedict = {(2, 8): (2, '0'),
               (9, 15): (3, '0'),
               (16, 25): (5, '0'),
               (26, 50): (8, '0'),
               (51, 90): (13, '0'),
               (91, 150): (20, '0'),
               (151, 280): (32, '0'),
               (281, 500): (50, '1'),
               (501, 1200): (80, '2'),
               (1201, 3200): (125, '3'),
               (3201, 10000): (200, '5'),
               (10001, 35000): (315, '7'),
               (35001, 150000): (500, '10'),
               (150001, 500000): (800, '14'),
               (500001, 1000000): (1250, '21')}


tightdict = {(2, 8): (2, '0'),
             (9, 15): (3, '0'),
             (16, 25): (8, '0'),
             (26, 50): (13, '0'),
             (51, 90): (20, '0'),
             (91, 150): (32, '0'),
             (151, 280): (50, '0'),
             (281, 500): (80, '1'),
             (501, 1200): (125, '2'),
             (1201, 3200): (200, '3'),
             (3201, 10000): (315, '7'),
             (10001, 35000): (500, '8'),
             (35001, 150000): (800, '12'),
             (150001, 500000): (1250, '18'),
             (500001, 1000000): (2000, '20')}

leveldict = {'loose': loosedict, 'average': averagedict, 'tight': tightdict}

level = leveldict[args.level]
pdfleveldict = leveldict[pdflevel]

# Make a list of all the xml in the target directory
allreclst = [n for n in locate('*', root='/dc/%s-images/editorial/%s' % (product, args.batch)) if n.endswith('.xml')]
allpdflst = [n for n in locate('*', root='/dc/%s-images/editorial/%s' % (product, args.batch)) if n.endswith('.pdf')]
reclst = []
pdflst = []
adlst = []

for f in allreclst:
    root = ET.parse(f).getroot()
    doctype = root.find('.//doctype1').text
    if doctype != 'Advertisement' and doctype != 'Covers':
        reclst.append(f)
    elif doctype == 'Advertisement':
        adlst.append(f)

# level = the type of sampling used.

# Calculate samplesize

for key in level.keys():
    if len(allreclst) in range(key[0], key[1] + 1):
        samplesize = level[key][0]
        majorminor = level[key][1]
    if len(adlst) in range(key[0], key[1] + 1):
        print(adlst)
        adsample = len(adlst) / 5
        admajorminor = level[key][1]

for key in pdfleveldict.keys():
    if len(allpdflst) in range(key[0], key[1] + 1):
        pdfsamplesize = pdfleveldict[key][0]
        pdfmajorminor = pdfleveldict[key][1]


# Sample adlist then add to reclist
if len(adlst) == 0:
    print "Batch %s does not contain any advertisements in sample." % (args.batch)
else:
    adsamp = sample(adlst, int(adsample))
    for i in adsamp:
        reclst.append(i)

# Take a sample of reclst and return as a list
samplst = sample(reclst, int(samplesize))
coverlst = list(set(['%s0001.xml' % i[0:-8] for i in samplst]))
samplst = list(set(samplst))

# Compile the list of PDFs for the sample
# If the pdf level is the same as the doc level,
# the same needs to contain the same pdfs as xmls
# in the sample.  If it is tighter, get random pdfs.
doclst = [os.path.basename(rec).split('.xml')[0] for rec in samplst]
pdfsamplst = [pdfdoc for pdfdoc in allpdflst if os.path.basename(pdfdoc).split('.pdf')[0] in doclst]

for pdfsamp in pdfsamplst:
    allpdflst.remove(pdfsamp)

if pdflevel != args.level:
    extrapdfs = int(pdfsamplesize) - len(pdfsamplst)
    pdfsamplst.extend(sample(allpdflst, int(extrapdfs)))

print '\n-----------------------------------------\nBatch size: %s\nANSI sample size: %s\nTotal sample size (ANSI + covers): %s\nAccessible PDFs in sample: %s\n-----------------------------------------\n' % (len(allreclst), samplesize, len(samplst) + len(coverlst), len(pdfsamplst))

# Output report on what's in the sample

'''Spreadsheet headings in the form:
Sample Date\tBatch\tNumber of Records/Number in Sample\tNumber of PDFs in Sample\tInspection Level\tMajors/Minors allowed\tMajors/Minors found\tBatch verdict
'''

logdict = OrderedDict([('Sample Date', []),
                       ('Batch', []),
                       ('# of Records/# in Sample', []),
                       ('# of PDFs in Sample', []),
                       ('Inspection Level', []),
                       ('Majors/Minors allowed', []),
                       ('Majors/Minors found', []),
                       ('Batch verdict', [])])

try:
    log = xlrd.open_workbook('/dc/%s-images/editorial/%s_sample-log.xls' % (product, product))
except IOError:
    log = xlwt.Workbook()
    logsheet = log.add_sheet('Log')
    for i, head in enumerate(logdict.keys()):
        logsheet.write(0, i, head)
    log.save('/dc/%s-images/editorial/%s_sample-log.xls' % (product, product))
    log = xlrd.open_workbook('/dc/%s-images/editorial/%s_sample-log.xls' % (product, product))
except Exception as e:
    print 'There was a problem: %s\nExiting...' % e
    exit(1)

log = copy(log)
logsheet = log.get_sheet(0)

emptyrow = logsheet.rows.keys()[-1] + 1

# Creating the list to write to the row
date = date.today().strftime('%Y-%m-%d')

rowls = [date, args.batch, '%s/%s' % (len(reclst), len(samplst)), len(pdfsamplst), args.level, majorminor]

for i, val in enumerate(rowls):
    logsheet.write(emptyrow, i, val)

log.save('/dc/%s-images/editorial/%s_sample-log.xls' % (product, product))

# Calculate and display percentage of doctypes selected in sample
doctypelst = []
imageset = []

for i in coverlst:
    samplst.append(i)

samplst = list(set(samplst))

for f in samplst:
    root = ET.parse(f).getroot()
    if root.find('.//doctype1').text != 'Covers':
        doctypelst.append(root.find('.//doctype1').text)
    imageset.append(['%s/%s' % (os.path.dirname(f).replace('xml', 'images'), i.text) for i in root.findall('.//page_ref')])

imageset = list(set([item for sublist in imageset for item in sublist]))

doctypecount = list(set([(i, doctypelst.count(i)) for i in doctypelst]))

for i in doctypecount:
    percent = Decimal(i[1]) / int(samplesize) * 100
    print i[0], '%s%s' % (percent.quantize(Decimal('.1')), '%')  # if it's less than 1%, add a default to display to half a %

# Copy the records and images out for testing
r = 0
p = 0

for image in imageset:
    outpathjpg = os.path.dirname(image).replace('editorial', 'samplings')
    if not os.path.exists(outpathjpg):
        os.makedirs(outpathjpg)
    shutil.copy(image, outpathjpg)

for pdf in pdfsamplst:
    p += 1
    outpathpdf = os.path.dirname(pdf).replace('editorial', 'samplings')

    if not os.path.exists(outpathpdf):
        os.makedirs(outpathpdf)

    shutil.copy(pdf, '%s/%s' % (outpathpdf, os.path.basename(pdf)))

    sys.stdout.write('Copying to %s: \033[92m%s\r' % (outpathpdf, p))

print '\n'

for rec in samplst:
    r += 1
    outpath = os.path.dirname(rec).replace('editorial', 'samplings')
    # outpathjpg = outpath.replace('xml', 'images')

    if not os.path.exists(outpath):
        os.makedirs(outpath)
        # os.makedirs(outpathjpg)

    shutil.copy(rec, '%s/%s' % (outpath, os.path.basename(rec)))

    os.chmod(outpath, 0777)
    os.chmod('%s/%s' % (outpath, os.path.basename(rec)), 0777)

    # for image in locate('*.jpg', os.path.dirname(rec).replace('xml', 'images')):
    #     if os.path.isfile('%s%s' % (outpathjpg, image)) is False:
    #         shutil.copy(image, outpathjpg)

    sys.stdout.write('Copying to %s: \033[92m%s\r' % (outpath, r))

print '\n'

print "Number of PDFs copied: %s" % p
print "Number of XMLs copied: %s" % r
