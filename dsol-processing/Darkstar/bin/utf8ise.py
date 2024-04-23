#!/usr/local/bin/python

''' Read a file in and write it back out as UTF-8. '''

import sys, os, shutil, codecs

infile = sys.argv[1]
outfile = infile + 'OUT'
outf = codecs.open(outfile, 'w', 'utf-8')
for line in codecs.open(infile, 'r', 'utf-8'):
    outf.write(line)
outf.close()

