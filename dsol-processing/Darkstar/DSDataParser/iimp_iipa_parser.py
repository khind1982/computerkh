''' IIMP/IIPA parser.
A field parser for IIMP/IIPA. (They both appear to have the same data format.)

Split the input file into xpath objects at the '/data/doc' level. These
can then be passed off one at a time to the PrismaRecord factory, which allows
us to manipulate the records at the level of each element.

'''
import sys, os, re
import amara
from amara import binderytools
from abstract_parser import *

class IIMPAParser(AbstractParser):
    def __init__(self, iDoc, xpath):
        AbstractParser.__init__(self, iDoc, xpath)

class IIMPARecord(AbstractRecord):
    def __init__(self, parsedDoc, fields):
        AbstractRecord.__init__(self, parsedDoc, fields)

