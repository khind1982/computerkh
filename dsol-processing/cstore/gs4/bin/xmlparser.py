#!/usr/bin/env python

# Check that each file is correctly formed XML and then parse it against the user specified schema.

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import shutil

import lxml.etree as ET

from optparse import OptionParser

parser = OptionParser()

parser.add_option("-d", "--dir", dest="foo", help="Target directory", metavar="DIRECTORY")
parser.add_option("-x", "--proj", dest="po", help="Name of schema", metavar="NAME")
parser.add_option("-e", "--ext", dest="bee", help="Name of extension", metavar="NAME")

(options, args) = parser.parse_args()

errlst=[]

dir = options.foo

schema_du = ET.parse(options.po)
xmlschema = ET.XMLSchema(schema_du)

outfilename = '%s/validation.log' % options.foo

for root, dirs, files in os.walk(dir):
    for xmls in files:
        if xmls.endswith(options.bee):
            njpg = os.path.join(root, xmls)

   	    with open(outfilename, 'w') as output:


                try:
                    doc = ET.parse(njpg, ET.XMLParser(remove_blank_text=True))
                    xmlschema.validate(doc)

                    log = xmlschema.error_log
                    error = log.last_error
	    	    log= str(log)
		    errlst.append(log)

            	except:
            	    print "Error with XML: %s. %s" % (njpg, sys.exc_info()[1])

    	        for item in errlst:
                    output.write(item)

errlst=[]
