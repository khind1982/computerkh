#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

'''# Check for:
- Date (and format)
- Check if country codes have been seen before
- Check if language codes have been seen before
- Check for missing boundwiths in master
- Malformed ent refs - done &amp;..., what else can go wrong with ent refs?'''

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'libdata/eeb'))
sys.path.append('/packages/dsol/opt/lib/python2.7/site-packages')

import datetime
import lxml.etree as ET
import xlrd

from StringIO import StringIO
from commonUtils.fileUtils import locate, buildLut
from HTMLParser import HTMLParser
from eebDates import std_date

h = HTMLParser()
xmlschema = ET.XMLSchema(file='/dc/eurobo/utils/schema/mets.xsd')
parser = ET.XMLParser(schema=xmlschema, remove_blank_text=True)

libraries = buildLut('/dc/eurobo/utils/libraries.lut')
countries = buildLut('/dc/eurobo/utils/country_codes_notags.lut')
languages = buildLut('/dc/eurobo/utils/langs_notags.lut')
collections = buildLut('/dc/eurobo/utils/collection_allrecs.lut')

try:
    indir = sys.argv[1]
    outfile = sys.argv[2]
except IndexError:
    print "Usage: eeb-data_audit.py [input directory] [output file]\n"
    exit(1)

badents = ['(&[A-z0-9#;]+;)', '&amp;#x', ' #x0026;']
errorlog = []
entlog = []
threadlog = []
images = []

recs = 0

for f in locate('*[0-9][0-9][0-9].xml', indir):
    recs += 1
    
# Grep all &; strings (Checking for malformed ents)
    with open(f, 'r') as thefile:
        for line in thefile:
            try:
                for ent in badents:
                    entstring = re.findall(ent, line)

                    for i in entstring:
                        if i.count(';') > 1:
                            print 'entity error, %s' % f
                            entlog.append('%s: %s' % (f, i))
            except AttributeError:
                pass
            

# Parse the xml
    try:
        root = ET.parse(f).getroot()
        xmlschema.validate(root)
        if xmlschema.validate(root) is False:
            errorlog.append(xmlschema.error_log)

        try:
            pqid = root.find('.//{*}recordIdentifier').text
        except AttributeError:
            pqid = '<blank>'
        fbase = os.path.basename(f).replace('.xml','')

    # Check that title field exists
        if root.find('.//{*}title') is None:
            errorlog.append('DATA ERROR: File %s has no title' % f)
        elif root.find('.//{*}title').text is None:
            errorlog.append('DATA ERROR: File %s has no title' % f)

    # Check that shelfmark exists
        shelfmark = [i for i in root.findall('.//{*}identifier') if i.attrib['type'] == 'coteoriginal']
        if len(shelfmark) < 1:
            errorlog.append('DATA ERROR: File %s has no shelfmark' % f)

    # Checking that pqid matches filename:
        if pqid != fbase:
            errorlog.append('DATA ERROR: Filename %s (without extension) does not match record ID %s' % (f, pqid))

    # Check that date can be converted to machine date:
        if root.find('.//{*}dateIssued') is not None:
            date = root.find('.//{*}dateIssued').text
            machine = std_date(date)
            if machine == '':
                errorlog.append('DATA ERROR: Date <mods:dateIssued>%s</mods:dateIssued> in %s does not convert to 16 digit machine date' % (date, f))
            try:
                start = machine.split('-')[0]
                end = machine.split('-')[1]
                try:
                    datetime.datetime(year=int(start[0:4]),month=int(start[5:6]),day=int(start[7:8]))
                    datetime.datetime(year=int(end[0:4]),month=int(end[5:6]),day=int(end[7:8]))
                except ValueError:
                    errorlog.append('DATA ERROR: Date <mods:dateIssued>%s</mods:dateIssued> in %s does not convert to 16 digit machine date' % (date, f))
            except IndexError:
                pass

            
    # Checking the threading pt1:
        threads = [i.text for i in root.findall('.//{*}objectIdentifierValue')]
        for i in threads:
            threadlog.append(i)
        
        sys.stdout.write('Number of records checked: \033[92m%s\r' % recs)
        sys.stdout.flush()
    
    except ET.XMLSyntaxError as e:
        errorlog.append('SCHEMA ERROR: %s: %s' % (f, e))
        pass
    
# Checking the threading pt2:
print '\nThread check running...'
for f in locate('*.jp2', indir):
    images.append(os.path.basename(f))

for i in threadlog:
    if i not in images:
        errorlog.append('THREADING ERROR: %s thread does not have a corresponding image file' % i)

for i in images:
    if i not in threadlog:
        errorlog.append('THREADING ERROR: %s image does not have a corresponding thread in an XML file' % i)

entlog = list(set(entlog))

if len(entlog) > 0:
    errorlog.append('DATA ERROR: Possible malformed entity references:\n%s' % '\n'.join(entlog)) 

insplit = indir.split('/')
# outfile = '/dc/eurobo/incoming/%s_audit.out' % insplit[-1]

if len(errorlog) > 0:
    print 'Errors detected - log output in %s' % outfile
    with open(outfile, 'w') as out:
        for i in errorlog:
            out.write('%s\n' % i)
else:
    print '\nNo errors detected'