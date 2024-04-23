#!/usr/bin/env python2.7

# Sampler for selecting records to validate

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import json
import lxml.etree as ET

from datetime import date
from commonUtils.fileUtils import locate

try:
    inputdir = sys.argv[1]
    outdir = sys.argv[2]
    dpmiin = sys.argv[3]
    jsonindir = sys.argv[4]
except:
    print 'Usage: eeb-ingest_proc.py [input directory] [output directory] [dpmi directory] [json dir]'
    exit(1)

if not os.path.exists(outdir):
    os.makedirs(outdir)

xslt = ET.parse('/dc/migrations/eeb/samples/eeb_ingest.xsl')
transform = ET.XSLT(xslt)

'''script structure: 
- get a list of input ingest records
- for each one in list:
     - open the dpmi record, find the thumbnail image name for title page and store  in var
     - open the json and find the right dpmi/pdf/thum image
     - open the ingest record and add the keys to the file.
     '''

inputfiles = [f for f in locate('*.xml', inputdir)]
dpmifiles = [f for f in locate('*.xml', dpmiin)]

recstowrite = []

for f in inputfiles:
    # first we transform the input eeb handover records using the stylesheet:
    root = ET.parse(f)
    froot = transform(root).getroot()

    # get the basename of the file and the bookID to use later
    filebase = os.path.basename(f)
    bookid = os.path.basename(f)[:-8]

    # find all the dpmi files in the dpmi directory and extract the name of the thumbnail image that is the title page
    # look at caching title page from xml not dpmi...
    try:
        dpmi = [i for i in dpmifiles if filebase.replace('.xml', '') in i][0]
        dpmiroot = ET.parse(dpmi).getroot()
    except IndexError:
        print 'One or more DPMI files for input records are missing from dpmi directory. Generate DPMI and run again.'
    try:
        titletag = [i for i in dpmiroot.findall('.//tag') if 'Title page' in i.text][0]
        thumimage = titletag.find('../rep/path').text[:-5]
    except IndexError:
        thumimage = dpmiroot.find('.//path').text[:-5]
        print 'Missing title page value in %s - using first image as default' % dpmi
    
    # get a list of the elements called 'Representation' to use later
    reps = froot.findall('.//Representation')
    
    # get the json file we need based off the bookid
    jsonfile = '%s/%s.json' % (jsonindir, bookid)
    jsonext = {}

    # as long as the jsonfile exists, we want to extract the relevant keys from the json file and add them to the representation elements in the ingest XML
    if os.path.isfile(jsonfile):
        json_data = json.load(open(jsonfile))
        for i in json_data:
            objdict = i['objects'] # this is a list of the dictionaries of objects associated with an hmsid
            for obj in objdict:
            #set the PDF, DPMI and Title THUM ids:
                if obj['type'] == 'PFT': # I think you will need to add this when changes are made to the PDF media key location in the json: and filebase.replace('.xml', '') in obj['objectId']:  
                    jsonext['PDF'] = obj['retrieveKey']
                    jsonext['PDFbytes'] = obj['size']
                elif obj['type'] == 'DPMI' and filebase.replace('.xml', '') in obj['objectId']:
                    jsonext['DPMI'] = obj['retrieveKey']
                elif obj['type'] == 'THUM' and thumimage in obj['objectId']:
                    jsonext['THUM'] = obj['retrieveKey']
            
        for rep in reps:
            if rep.get('RepresentationType') == 'PDFFullText':
                rep.find('.//MediaKey').text = '/media%s' % jsonext['PDF']
                rep.find('.//Bytes').text = jsonext['PDFbytes']
                # print ET.tostring(rep)
            elif rep.get('RepresentationType') == 'Thumb':
                rep.find('.//MediaKey').text = '/media%s' % jsonext['THUM']
                # print ET.tostring(rep)
            elif rep.get('RepresentationType') == 'DPMI':
                rep.find('.//MediaKey').text = '/media%s' % jsonext['DPMI']
                # print ET.tostring(rep)

    # if the jsonfile doesn't exist we want to remove the representations that require keys from the ingest XML.
    else:
        compstorm = [c for c in froot.findall('.//Component') if c.get('ComponentType') != 'Citation']
        for comps in compstorm:
            comps.getparent().remove(comps)
    
    recstowrite.append(froot)

    outfile = '%s/%s' % (outdir, filebase)
    with open(outfile, 'w') as out:
        out.write(ET.tostring(froot, pretty_print=True))
