#!/usr/bin/env python2.7
# coding=utf-8

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import lxml.etree as ET
import shutil

from commonUtils.fileUtils import locate
from leviathanUtils import levorder

coprodlist = []

try:
    indir = sys.argv[1]
except IndexError:
    print "Usage: %s {indirectory}\nMaybe one of these is missing from your command?" % __file__
    exit()

parser = ET.XMLParser(remove_blank_text=True)

reccount = 0

for f in locate('*.xml', indir):
    reccount += 1
    shutil.copyfile(f, f.replace('.xml', '.old'))
    tree = ET.parse(f, parser)
    journal = tree.find('.//journal')
    title = tree.find('.//title')

    for elem in journal:
        if elem.tag == 'company':
            if 'company|%s' % elem.text not in coprodlist:
                coprodlist.append('company|%s' % elem.text)
            elem.getparent().remove(elem)
        elif elem.tag == 'product':
            if 'product|%s' % elem.text not in coprodlist:
                coprodlist.append('product|%s' % elem.text)
            elem.getparent().remove(elem)

    for coprod in coprodlist:
        ET.SubElement(journal, '%s' % coprod.split('|')[0]).text = ''.join(coprod.split('|')[1:])

    if journal.find('.//doctype1').text == 'Advertisement':
        if len(journal.findall('.//company')) == 1:
            company = '(%s)' % journal.find('.//company').text
        elif len(journal.findall('.//company')) > 1:
            company = '(%s and others)' % journal.find('.//company').text
        else:
            company = ''

        if len(journal.findall('.//product')) == 1:
            product = '%s ' % journal.find('.//product').text
        elif len(journal.findall('.//product')) == 2:
            product = '%s, %s ' % (journal.findall('.//product')[0].text, journal.findall('.//product')[1].text)
        elif len(journal.findall('.//product')) > 2:
            product = '%s, %s ... ' % (journal.findall('.//product')[0].text, journal.findall('.//product')[1].text)
        else:
            product = ''

        if product == '' and company == '':
            title.text = 'Advertisement'
        else:
            text = 'Advertisement: %s%s' % (product, company)
            title.text = text.strip()
        
        tree = levorder(tree, 'journal')

        with open(f, 'w') as out:
            out.write(ET.tostring(tree, pretty_print=True, xml_declaration=True, encoding='utf-8'))

    coprodlist = []
    sys.stdout.write('Seen: \033[92m%s (%s)\r' % (f, reccount))
    sys.stdout.flush()

print '\nRecord count: %s' % reccount
