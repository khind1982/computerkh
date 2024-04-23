#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

import re, sys

def audit(filelist):

    audf = open('audit.log', 'w')
    idre = re.compile('<LegacyID>(bp(....)-.*)</LegacyID>')
    actionre = re.compile('<ActionCode>(.*?)</ActionCode>')
    for fi in filelist:
        inf = open(fi, 'r')
        relatedflag = 0
        currentaction = ''
        for line in inf:
            if actionre.search(line) != None:
                currentaction = actionre.search(line).group(1)
            if relatedflag == 0:
                if line.find('<RelatedLegacyID>') != -1:
                    relatedflag = 1
            else:
                if line.find('</RelatedLegacyID>') != -1:
                    relatedflag = 0
            
            if relatedflag == 0:
                idmatch = idre.search(line)
                if idmatch != None:
                    if currentaction == 'delete':
                        audf.write('CH~' + idmatch.group(2) + '~' + idmatch.group(1) + '~DELETE' + '\n')
                    else:
                        audf.write('CH~' + idmatch.group(2) + '~' + idmatch.group(1) + '~DELIVERED' + '\n')
        inf.close()
    audf.close()
    
if __name__ == '__main__':
    audit(sys.argv[1:])
