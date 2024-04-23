#!/usr/local/bin/python2.6

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import lxml.etree as ET
import codecs

from StringIO import StringIO

from commonUtils.fileUtils import locate

ahrefsdict = {'Essay': '_essay.pdf',
             'Subject Index': '_subji.pdf',
             'Search this collection': 'dump',
             'Photo Archive': '_photo.pdf',
             'Names List': '_namel.pdf',
             'Subject Index (.PDF format)': '_subji.pdf',
             'Bibliographic Essay': '_bibes.pdf',
             'Names Index (.PDF format)': 'namei.pdf',
             'Subject List': '_subjl.pdf',
             'Acknowledgments': '_ackno.pdf',
             'Names Index': '_namei.pdf',
             'Preview upcoming collections': 'dump'}

for f in locate('*.jsp', '/dc/migrations/dnsa/data/master/00collections_guide/intros'):

    outfilename = '%s.txt' % f.replace('.jsp', '')
    collection = os.path.basename(f).replace('intro.jsp','')

    fs = StringIO(codecs.open(f, 'r', 'latin-1').read())

    tree = ET.parse(fs, ET.XMLParser(remove_blank_text=True, resolve_entities=False))
    root = tree.getroot()

    for Ahref in root.findall('.//A'):
        Ahref.tag = 'a'
        try:
            del Ahref.attrib['HREF']
        except KeyError:
            pass

    for img in root.findall('.//img'):
        img.getparent().remove(img)

    for P in root.findall('.//P'):
        P.tag = 'p'

    for capshref in root.findall('.//a'):
        try:
            del capshref.attrib['HREF']
        except KeyError:
            pass

    for h5 in root.findall('.//h5'):
        h5.tag = 'h4'

    for i in root.findall('.//i'):
        i.tag = 'em'

    for ahrefs in root.findall('.//a'):
        try:
            if 'intro.jsp' in ahrefs.attrib['href']:
                ahrefs.getparent().text = ahrefs.text
                ahrefs.getparent().remove(ahrefs)
            elif ahrefs.text in ahrefsdict.keys():
                if ahrefsdict[ahrefs.text] == 'dump':
                    ahrefs.getparent().remove(ahrefs)
                else:
                    try:
                        ahrefs.attrib['href'] = 'http://www.proquest.com/go/DNSA_%s%s' % (collection, ahrefsdict[ahrefs.text])
                    except KeyError:
                        pass
        except KeyError:
            pass

    with open(outfilename, 'w') as out:
        out.write(ET.tostring(root, pretty_print=True, encoding='iso-latin-1').replace('&amp;', '&'))
