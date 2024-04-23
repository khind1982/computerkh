#!/usr/local/bin/python

''' Split a single XML document into multiple record-level "documents".
These will still exist in one physical file, but are suitable fot the
eFeeds thing at the other end. The new document is printed on STDOUT,
so you need to use shell redirection to capture it. '''

import sys

if len(sys.argv) == 1:
    sys.stderr.write('No file to work with!\n')
    exit(1)

import amara
if sys.argv[1] == '-':
    infile = sys.stdin
else:
    infile = sys.argv[1]

done_so_far = [0]
for record in amara.binderytools.pushbind(infile, u'/ROOT/RECORD'):
    done_so_far[0] += 1
    print '<?xml version="1.0" encoding="UTF-8"?>'
    print record.xml()
    if done_so_far[0] % 100 == 0:
        sys.stderr.write(str(done_so_far[0]))
    elif done_so_far[0] % 10 == 0:
        sys.stderr.write('.')
sys.stderr.write('\n')
