#!/usr/local/bin/python

# Script to create a spreadsheet friendly view of particular elements from all the WWD XML files in a directory the user specifies.

import os
import sys
import codecs

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import datetime
from optparse import OptionParser

import lxml.etree as ET

# Importing from modules usually goes here
from commonUtils.fileUtils import locate

# Import the OptionParser and define options, which the user calls with switches on the command line:

parser = OptionParser()

parser.add_option("-o", "--out", dest="bar", help="Output file", metavar="FILE")
parser.add_option("-d", "--dir", dest="foo", help="Target directory", metavar="DIRECTORY")

(options, args) = parser.parse_args()

alllist = []

# Adds the column headers to alllist:

alllist.append("ID\tArticle Type\tMaterial Type\tSupplement Title\tTitle\tSubheads\tAuthors\tFeatures\tVolume\tIssue\tPdate\tNdate\tAbstract\tAbstract Length\tCompany\tBrand\tCaptions\tCredits\tPages\n")

# Function specifing what to do with an element that occurs once in a single document:

def singlenode(node):
  it = root.find(node)
  try:
    if it is not None:
      newit = it.text.encode("utf-8")
      newit = newit.strip()
      return newit
    else:
      newit = ''
      return newit
  except AttributeError:
    print "Error in record:%s with field type %s" % (nxml, it)

# Function specifing what to do with an element that occurs more than once in a single document:

def multinode(node):
  nodelist = []
  for it in root.findall(node):
    try:
      if it is not None:
        newit = it.text.encode("utf-8")
        nodelist.append(newit.strip())
      else:
        newit = ''
        nodelist.append(newit)
    except AttributeError:
      print "Error in record:%s with field type %s" % (nxml, it)
      pass
  nodelist = set(nodelist)
  allvalues = "; ".join(nodelist)
  return allvalues

def getdate(s):
    return s[0:10]


# Finds each XML file in the user-specified directory and stores in a variable:

for nxml in locate('*.xml', root=options.foo):

# Parses the XML file using lxml and stores the parent element in 'root':

  tree = ET.parse(nxml, ET.XMLParser(remove_blank_text=True, resolve_entities=True))
  root = tree.getroot()

# Instructions for each element we want to pull out of the file, using the functions defined above:

  ids = singlenode('APS_identifier')
  arttype = root.get("type")
  mattype = singlenode('APS_mattype')
  suppl = singlenode('APS_supplement')
  title = singlenode('APS_title')
  subhead = multinode('APS_subhead')
  author = multinode('APS_author')
  features = multinode('APS_feature')
  volume = singlenode('APS_ident/APS_volume')
  issue = singlenode('APS_ident/APS_issue')
  pdate = singlenode('APS_issue_date/APS_printed_date')
  ndate = singlenode('APS_issue_date/APS_date_8601')
  abstract = singlenode('APS_abstract')
  abslen = str(len(abstract))
  company = multinode('APS_company')
  brand = multinode('APS_brand')
  caption = multinode('APS_zone/APS_content/APS_zone_caption')
  credit = multinode('APS_zone/APS_content/APS_zone_credit')
  pages = multinode('APS_zone/APS_page_image')

# Gets the current data and strips the time, storing the date in 'recdate':

  now = datetime.datetime.now()
  recdate = str(now)
  recdate = getdate(recdate)

# Appends all of the values in each variable above in a tab delimited line, one line for each XML file:

  alllist.append("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (ids, arttype, mattype, suppl, title, str(subhead), author, features, volume, issue, pdate, ndate, abstract, abslen, company, brand, caption, credit, pages))

# Defines the output file name:

outfile = options.bar

# Opens the output file and writes all the lines in alllist to the file:

with open(outfile, 'w+') as out:
  for item in alllist:
    out.write(item)
  alllist = []
