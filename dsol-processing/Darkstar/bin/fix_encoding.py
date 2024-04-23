#!/usr/local/bin/python2.6

'''
Take a file with bad characters and try to convert them to UTF-8
'''

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

import re
import codecs

lutdata = [line for line in open('/packages/dsol/libdata/latin2utf8.lut')]

l2u8 = [line.strip().split('\t') for line in lutdata]

#print l2u8

def fixEnc(files):
    """
    
    Arguments:
    - `f`: the file to clean
    """

    reg = re.compile(u'\x83\xc2', re.U)

    for f in files:
        sys.stderr.write(f + '\n')
        with codecs.open(f, 'r') as datafile:
            for line in datafile:
                line = reg.sub('', line)
#                line = re.sub(r'\x04', '', line)

                print line.rstrip()


if __name__ == '__main__':
    fixEnc(sys.argv[1:])
