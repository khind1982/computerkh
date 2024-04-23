#!/usr/local/bin/python2.6

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import lxml.etree as ET

from StringIO import StringIO

from commonUtils.fileUtils import locate

fielddict = {}

for f in locate('CT_intro3.htm', '/dc/migrations/dnsa/data/master/CT'):

# work on CT_intro2

    fs = StringIO(open(f, 'r').read())

    tree = ET.parse(fs)
    root = tree.getroot()

    p = root.findall('.//p')
    table = root.findall('.//table')

    for key, value in fielddict:
        key[value] =

    print p, table

    # for item in body:
    #     print ET.tostring(item)

    #tree = ET.iterparse(fs, remove_blank_text=True)

    # for _, tags in tree:
    #     for k in tags.nsmap:
    #         o = '{%s}' % tags.nsmap[k]

    #     if o in tags.tag:
    #        tags.tag = tags.tag.replace(o, '')

    #     if tags.tag == 'head':
    #         tags.getparent().remove(tags)

    #     for attrib in tags.attrib:
    #         del tags.attrib[attrib]

    #     if tags.tag == 'span':
    #         try:
    #             ET.strip_tags(tags.getparent(), tags.tag)
    #         except:
    #             pass
    #     if tags.tag == 'i':
    #         tags.tag = 'em'

    #     if tags.text == None:
    #         ET.strip_tags(tags.getparent(), tags.tag)



    # #print ET.tostring(tags, pretty_print=True)




    # with open('/dc/migrations/dnsa/data/master/CT/CT_intro.txt', 'w') as out:
    #     out.write(ET.tostring(tags, pretty_print=True).replace('&amp;nbsp;', '&nbsp;'))


