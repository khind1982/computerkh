#!/usr/local/bin/python2.5

''' Convert amara-friendly element tags (CHIMPA_Markup, etc) and convert them
to GSv3-friendly element tags (CHIMPA-Markup, etc). Results are printed to 
STDOUT so need to captured using shell redirects '''

import re, sys, os, shutil

if sys.argv[1] == '-':
    infile = sys.stdin
else:
    infile = open(sys.argv[1])

done = [0]
for line in infile:
    line = re.sub(r'CHIMPA_', 'CHIMPA-', line)
    print line.rstrip()
    done[0] += 1
    if infile is not sys.stdin:  # means we're not reading from STDIN, but
                                 # from a file. Don't interfere with any other
                                 # output from the pipeline.
        if done[0] % 1000 == 0:
            sys.stderr.write('.')
    
if infile is file:
    file(infile).close()

sys.stderr.write('\n')
