#!/usr/local/bin/python

''' Take a file containing multiple GSv3 RECORDs, and print each one out as
an individual file, named for the LegacyID value with '.xml' appended. '''

import sys, os

if len(sys.argv) == 1:
    sys.stderr.write('Args: <file_to_split> [<target_directory>]\n')
    exit(1)
else:
    infile = open(sys.argv[1])
    if len(sys.argv) == 3:
        outdir = sys.argv[2]
    else: outdir = '.'
    
import amara

for record in amara.binderytools.pushbind(infile, u'/ROOT/RECORD'):
    legacyID = unicode(record.ControlStructure.LegacyID)
    outFileName = legacyID + '.xml'
    outfile = open(os.path.join(outdir, outFileName), 'w')
    outfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    outfile.write(record.xml())
    outfile.close()
