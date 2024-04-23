''' PQPrisma - PQ Prisma records

'''

from prisma_mapping import PrismaMapping
import amara, re


class PQPrismaMapping(PrismaMapping):
    def __init__(self, record):
        ''' Take a PrismaRecord object, and output a PQ Prisma record '''
        
        self.record = record
        PrismaMapping.__init__(self, record)
        
    def do_mapping(self):
        xmlCstruct, xmlObject = PrismaMapping.do_mapping(self)
        
        self.buildControlStructure(xmlCstruct)
        self.buildObjectInfo(xmlObject)
        
        ''' Handle HAPI and PQ ids '''
        hapiid = self.record.hapiid
        pqid = self.record.pqid
        if hapiid != '':
            xmlObject.ObjectIds.xml_append(self.xmlDoc.xml_create_element(u'ObjectId', 
                attributes={u'IdType':u'DOC_ID', u'IdSource':u'HAPI'}, content=hapiid))
        if pqid != '':
            xmlObject.ObjectIds.xml_append(self.xmlDoc.xml_create_element(u'ObjectId', 
                attributes={u'IdType':u'DOC_ID', u'IdSource':u'PQ'}, content=pqid))
        
        return self.xmlDoc
        
    