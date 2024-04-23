'''
A field parser for PRISMA.

Split the input file into xpath objects at the '/data/doc' level. These
can then be passed off one at a time to the PrismaRecord factory, which allows
us to manipulate the records at the level of each element.

'''
import sys, os, re
from amara import binderytools
from abstract_parser import *

class PrismaParser(AbstractParser):
    '''Construct an object representing a collection of Prisma records from an
    arbitrary source.
    
    Arguments:
        prismaDoc - an XML file containing Prisma data records.
        xpath - an XPath specification, the axis at which the input XML can be
            broken into individual records.
    '''
    def __init__(self, prismaDoc, xpath):
        AbstractParser.__init__(self, prismaDoc, xpath)
    
class PrismaRecord(AbstractRecord):
    '''Object representing an individual record from a Prisma XML source.
    
    Contructed from the items held in PrismaParser.records.
    Arguments:
        parsedDoc - in item from PrismaParser.records
        fields - a list of XPath specifications of the fields to extract from the
            record. These get automatically turned into attributes on the object
            holding the data in the field in question. See AbstractRecord.__init__
            for the magic.
    '''
    def __init__(self, parsedDoc, fields):
        self.fields = fields
        AbstractRecord.__init__(self, parsedDoc, self.fields)
        
        
    def udt_date(self):
        return [line for line in 
          unicode(AbstractRecord.__getitem__(self, self.fields[1])).split('\n') 
          if re.search('name="udt"', line)][0].split('>')[1].split('&')[0]

