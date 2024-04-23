#!/usr/local/bin/python2.7

import os
import sys

import lxml.etree as et

parser = et.XMLParser(remove_blank_text=True)

ns = {"re": "http://exslt.org/regular-expressions"}

def main(args):

    try:
        indir = args[0]
        element = args[1]
    except:
        print "usage: get-elements.py [input directory] [xpath element]"
        exit(1)

    outfile = open('%s.txt' % ('_'.join(element.split('[')[0].split('/')[-2:])), 'w')

    countlist = []
    for f in walk_indir(indir):
        print "Checking file %s..." % (f)
        countlist.append(f)
        try:
            elemlist = [et.tostring(item) for item in getelem(f, element) if len(getelem(f, element)) > 0]
            for i in elemlist:
                outfile.write('%s\t%s\n' % (f, i.strip('\n\r')))
        except TypeError:
            xmldata = et.parse(f, parser)
            elemlist = [et.tostring(item) for item in xmldata.xpath(f'{element}') if len(xmldata.xpath(f'{element}')) > 0]
            for i in elemlist:
                outfile.write('%s\t%s\n' % (f, i.strip('\n\r')))
        print "Checked %s files for xpath %s..." % (len(countlist), element)


def getelem(f, element):
    xmldata = et.parse(f, parser)
    return xmldata.xpath('//%s' % (element), namespaces=ns)


def walk_indir(indir):
    for root, dirs, files in os.walk(indir):
        for f in files:
            if f.endswith('.xml') or f.endswith('.txt'):
                yield os.path.join(root, f)


if __name__ == '__main__':
    main(sys.argv[1:])