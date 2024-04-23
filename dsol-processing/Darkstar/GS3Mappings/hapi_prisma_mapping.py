'''HAPIPrismaMapping

'''

from prisma_mapping import PrismaMapping
import amara, re

class HAPIPrismaMapping(PrismaMapping):
    def __init__(self, record):
        self.record = record
        PrismaMapping.__init__(self, record)
        
    def do_mapping(self):
        xmlCstruct, xmlObject = PrismaMapping.do_mapping(self)
        
        self.buildControlStructure(xmlCstruct)
        self.buildObjectInfo(xmlObject)
        return self.xmlDoc
        
    def oi_201_insert_ObjectId(self, xmlObject):
        ''' Set the ObjectId tags '''
        xmlObject.ObjectIds.xml_append(self.xmlDoc.xml_create_element(u'ObjectId',
          attributes={u'IdType': u'DOC_ID', u'IdSource':u'HAPI'}, content=self.record.hapiid))
        if self.record.pqid == '':
            xmlObject.ObjectIds.xml_append(self.xmlDoc.xml_create_element(u'ObjectId',
              attributes={u'IdType':u'DOC_ID', u'IdSource': u'Prisma132'}, content=self.record.hapiid))
        else:
            xmlObject.ObjectIds.xml_append(self.xmlDoc.xml_create_element(u'ObjectId',
              attributes={u'IdType':u'DOC_ID', u'IdSource':u'PQ'}, content=self.record.pqid))
              
        ''' These are particular to HAPI records '''
    def oi_210_insert_DocFeature(self, xmlObject):
        docFeature = xmlObject.xml_create_element(u'DocFeature', content=self.record.notes)
        xmlObject.xml_insert_after(xmlObject.ObjectIds, docFeature)
        
    def oi_220_insert_Terms(self, xmlObject):
        if self.record.subjects or self.record.descriptors:
            terms = xmlObject.xml_create_element(u'Terms')
            xmlObject.xml_insert_after(xmlObject.Contributors, terms)
            
            for termitem in [self.record.subjects, self.record.descriptors]:
                if termitem != '':
                    term = xmlObject.xml_create_element(u'Term',
                        attributes={u'TermType':u'GenSubj'})
                    for subitem in termitem.split('\t'):
                        termElem = xmlObject.xml_create_element(u'TermElem',
                            content=subitem, attributes={u'ElemType':u'DsolFIXME'})
                        term.xml_append(termElem)
                    xmlObject.Terms.xml_append(term)
            
            
    def Xoi_230_add_other_authors(self, xmlObject):
        if self.record.other_authors:
            xmlObject.Contributors.xml_append(self.xmlDoc.xml_create_element(u'Contributor',
              attributes={u'RoleName':u'Author'}))
            xmlObject.Contributors.Contributor.xml_append(self.xmlDoc.xml_create_element(
              u'ContribData', attributes={u'MarkupIndicator':u'PersonName'},
              content=self.record.other_authors))
              
