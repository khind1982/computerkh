'''
Collects all records, post mapping, and then binds them into a single output
document.

'''

import amara
import sys
#from GS3Mappings.proxy_mapping import ProxyMapping

class FullDocumentMapping:
    '''A class that implements a semi-intelligent list, that knows how to format
    itself as a complete GSv3 document.'''

    def __init__(self, mappingList=None, outfile=None, docRoot=u'RECORD'):
        ''' Takes a list of Mapping objects (i.e. an object that has a do_mapping()
        method) and an optional output file name. If no filename is given, use
        STDOUT.'''
        self.mappingList = mappingList  # Pre-built list of Mappings
        self.outfile = open(outfile, 'w') if outfile else sys.stdout
        self.xmlDoc = amara.create_document(unicode(docRoot))
        
    def buildDocument(self):
        for record in self.mappingList:
            xml = record.do_mapping()
            self.outfile.write(xml.xml(indent='y', omitXmlDeclaration='y')+'\n')
        if self.outfile != sys.stdout:
            self.outfile.close()
