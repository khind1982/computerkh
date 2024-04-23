#!/usr/local/bin/python2.6
# -*- mode: python -*-

import os
import lxml.etree as etree
import optparse
import sys

parser = optparse.OptionParser()
parser.add_option('-i', '--input', dest="input", help='directory containing the XML files to be validated')
(options, args) = parser.parse_args()

if options.input is None:
    parser.print_help()
    exit(1)

xmlfiles = options.input

workfiles = [f for f in os.listdir(xmlfiles) if f.endswith('.xml')]
numfiles = len(workfiles)
workfiles.sort()


def validate_xml(directory):

    for i, f in enumerate(workfiles):
        i += 1
        xml_file = os.path.join(xmlfiles, f)
        try:
            xml = etree.parse(xml_file)
        except etree.XMLSyntaxError as e:
            error_msg = str(e.msg)
            sys.stdout.write('\r')
            print xml_file, error_message(error_msg)

        printout(i, numfiles, xml_file)

def error_message(mgs):
    if "\n" in mgs:
        error_isolated = mgs.split("\n")
        return error_isolated[-1]
    else:
        return mgs

def printout(i, numfiles, xml_file):
    percent = '%s%% ' % str(int(((i * 100) / numfiles)))
    print_line = '%s of %s, %s, %s' % (str(i), str(numfiles), percent.strip(), xml_file)
    sys.stdout.write('\r')
    sys.stdout.write(print_line)
    sys.stdout.flush()

if __name__ == '__main__':

    validate_xml(options.input)

