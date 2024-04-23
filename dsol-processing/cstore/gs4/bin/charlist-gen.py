#!/usr/local/bin/python

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

from optparse import OptionParser

parser = OptionParser()

(options, args) = parser.parse_args()

charlist = []

try:
    orifile = args[0]
except IndexError:
    print "Please specify file(s) to check"
    parser.print_help()
    exit(1)

with open(orifile, 'r') as file2convert:
    for line in file2convert:
        for character in line:
            charlist.append(character)

charlist = list(set(charlist))
outfile = 'charlistcheck.logs'

print charlist

with open(outfile, 'w') as out:
    for item in charlist:
        out.write('%s\n' % item)
charlist = []
