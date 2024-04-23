#!/usr/local/bin/python2.6
# -*- mode: python -*-

import re, sys

def hsccrossref(infile):

    recdict = {}
    idre = re.compile('<id>(.*?)</id>')
    titlere = re.compile('<title>(.*?)</title>')
    
    inf = open(infile, 'r')
    for line in inf:
        if line.find('<rec>') != -1:
            id = ''
        if idre.search(line) != None:
            id = idre.search(line).group(1)
        if titlere.search(line) != None:
            if id != '':
                recdict[titlere.search(line).group(1).lower()] = id
            else:
                print "No id found for title: " + titlere.search(line).group(1)
    inf.close()
    
    seealsore = re.compile('<seealso/><p>See also:?(.*)</p>')
    
    inf = open(infile, 'r')
    outf = open(infile + '.test', 'w')
    for line in inf:
        if seealsore.search(line) != None:
            refs = seealsore.search(line).group(1).split('; ')
            linkedrefs = []
            for ref in refs:
                ref = ref.strip()
                if recdict.has_key(ref.lower()):
                    linkedref = ''.join(['<xref id="', recdict[ref.lower()], '" type="ref">', ref, '</xref>'])
                    linkedrefs.append(linkedref)
                else:
                    print "No record found for reference: " + ref
                    linkedrefs.append(ref)
            newseealso = ''.join(['<seealso/><p>See also ', '; '.join(linkedrefs), '</p>'])
            line = seealsore.sub(newseealso, line)
        outf.write(line)
    inf.close()
    outf.close()
    
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Usage: hsccrossref.py filename(s)\nProduces one .test file per input file\nWrites errors to terminal"
    for fi in sys.argv[1:]:
        hsccrossref(fi)