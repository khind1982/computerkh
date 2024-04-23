#!/usr/local/bin/python2.5

''' Clean up any leftover entity references in the generated output. '''

import sys
sys.path.append('/home/dbye/svn/dsol/trunk/lib/python')
from EntityShield import *

if len(sys.argv) == 1:
    sys.stderr.write("No file to tidy!\n")
    exit(1)
else:
    infile = sys.argv[1]
    
data = [unprotect(line) for line in open(infile)]
outfile = infile

outf = open(outfile, 'w')
for line in data:
    if re.search(r'&(?!(amp|lt|gt|quot|apos);)', line):
        line = protect(line)
    outf.write(line)
outf.close()
