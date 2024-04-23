''' Prisma mapping '''

import amara, re, os
from ds_abstract_mapping import DSAbstractMapping
import sys
sys.path.append(str(__file__ + '/../'))
from DateConverter import *
from miscUtils import *
from EntityShield import protect, unprotect
import findutils as fu

prisma_ds_ids = [line.rstrip() for line in open(os.path.join(os.path.expanduser('~'), 'prisma_ds_ids.txt'))]


class PrismaMapping(DSAbstractMapping):
    '''Base implementation. Contains field mappings common to both PQ and HAPI
    Prisma records.
    
    See PQPrismaMapping and HAPIPrismaMapping for specifics about the subclasses.
    '''
    def __init__(self, record):
        DSAbstractMapping.__init__(self, record)
        # Set the languages member to a list of the languages associated with the 
        # record. Used later to populate the language template.
        #self.languages = str_to_list(self.language(), '\t')
        
    def do_mapping(self):
        xmlCstruct, xmlObject = DSAbstractMapping.do_mapping(self)
        
        #return [self.xmlDoc.RECORD.ControlStructure, 
        #        self.xmlDoc.RECORD.ObjectInfo]
        self.buildControlStructure(xmlCstruct)
        self.buildObjectInfo(xmlObject)
        
        return self.xmlDoc
            
    def oi_101_title(self, xmlObject):
        #if self.mappingClass() == "PQPrismaMapping":
        #    title = self.record.article_title
        #elif self.mappingClass() == "HAPIPrismaMapping":
        #    title = self.record.harticle_title
        title = self.cleanLegacyMarkup(self.record.harticle_title if self.record.harticle_title else self.record.article_title)
        title = self.replace_entityrefs(protect(unprotect(title, pad=False)))
        if title == '': 
            title = u'[untitled]'
        xmlObject.Title.cht.xml_append(title)
        
    def oi_102_abstract(self, xmlObject):
        if self.record.abstract:
            if re.search('MABS', self.record.abstract):
                abstType = u'med'
            elif re.search('SABS', self.record.abstract):
                abstType = u'short'
            abstract = xmlObject.xml_create_element(u'Abstract', 
                attributes={u'AbstType':abstType})  
            abstract.xml_append(xmlObject.xml_create_element(u'paragraph'))
            abstract.paragraph.xml_append(xmlObject.xml_create_element(u'cht',
                content = self.replace_entityrefs(self.cleanLegacyMarkup(self.record.abstract))))
            xmlObject.Abstracts.xml_append(abstract)
        else:
            xmlObject.xml_remove_child(xmlObject.Abstracts)
          
        
    def oi_104_printLocation(self, xmlObject):
        #if self.mappingClass() == "PQPrismaMapping":
        #    xmlObject.PrintLocation.StartPage.xml_append(self.record.page)
        #    xmlObject.PrintLocation.EndPage.xml_append(self.helper_endPage(self.record.pagecount))
        #    xmlObject.PrintLocation.Pagination.xml_append(self.record.pagecount)
        #elif self.mappingClass() == "HAPIPrismaMapping":
        #    pagecount = self.record.hpagecount if self.record.hpagecount else self.record.pagecount
        #    xmlObject.PrintLocation.StartPage.xml_append(self.record.hpage)
        #    xmlObject.PrintLocation.EndPage.xml_append(self.helper_endPage(pagecount))
        #    xmlObject.PrintLocation.Pagination.xml_append(self.record.hpagecount)
        if self.record.hpage:
            xmlObject.PrintLocation.StartPage.xml_append(self.record.hpage)
            xmlObject.PrintLocation.EndPage.xml_append(self.helper_endPage(self.record.hpagecount))
            xmlObject.PrintLocation.Pagination.xml_append(self.record.hpagecount)
        
    def oi_105_contributors(self, xmlObject):
        
        #if self.mappingClass() == "PQPrismaMapping":
        #    authors = self.record.author
        #elif self.mappingClass() == "HAPIPrismaMapping":
        #    authors = self.record.authors
        
        #if self.record.author:
        #    authors = [author.rstrip() for author in self.record.author.split('\t') if author.rstrip()]
        #else:
        #authors = [author.rstrip() for author in self.record.authors.split('\t')] # if author.rstrip()]
        authors = self.record.authors.split('\t')
        
        #authors = (self.record.author if self.record.author else self.record.authors)
        if len(authors) == 0:
            xmlObject.xml_remove_child(xmlObject.Contributors)
        else:
            for contributor in authors:  #.split('\t'):
                contributor = protect(unprotect(self.replace_entityrefs(contributor.strip()), pad=False))
                if contributor:
                    #if self.record.bkr:
                    #    xmlObject.Contributors.xml_append(self.contributor_template(
                    #        'ReviewAuth', {'OriginalForm': contributor}))
                    #else:
                    self.author_count += 1
                    xmlObject.Contributors.xml_append(self.contributor_template(
                        'Author', {'OriginalForm':contributor}))

    # def oi_106_contrib_publisher(self, xmlObject):
    #     if self.country or self.city or self.publisher:
            

    def oi_110_insert_LegacyProductMapping(self, xmlObject):
        xmlObject.LegacyProductMapping.GroupName.xml_append(u'PRISMA')

    

    # Taken from HAPIPrismaMapping, which is now no longer included in the
    # import chain. We are only producing one type of output record now, not
    # two, making subclasses of this class redundant.

    def oi_201_insert_ObjectId(self, xmlObject):
        ''' Set the ObjectId tags '''
        xmlObject.ObjectIds.xml_append(self.xmlDoc.xml_create_element(u'ObjectId',
          attributes={u'IdType': u'DOC_ID', u'IdSource':u'HAPI'}, content=self.record.hapiid))
        if self.record.pqid:
            self.prisma132 = self.record.pqid
            xmlObject.ObjectIds.xml_append(self.xmlDoc.xml_create_element(u'ObjectId',
              attributes={u'IdType': u'DOC_ID', u'IdSource':u'PQ'}, content = self.record.pqid))
        else:
            self.prisma132 = self.record.hapiid
        xmlObject.ObjectIds.xml_append(self.xmlDoc.xml_create_element(u'ObjectId',
          attributes={u'IdType':u'DOC_ID', u'IdSource':u'Prisma132'}, content = self.prisma132))
        
        
        #if self.record.pqid == '':
        #    xmlObject.ObjectIds.xml_append(self.xmlDoc.xml_create_element(u'ObjectId',
        #      attributes={u'IdType':u'DOC_ID', u'IdSource': u'Prisma132'}, content=self.record.hapiid))
        #else:
        #    xmlObject.ObjectIds.xml_append(self.xmlDoc.xml_create_element(u'ObjectId',
        #      attributes={u'IdType':u'DOC_ID', u'IdSource':u'PQ'}, content=self.record.pqid))
          
        
    def Xoi_202_insert_DarkStar_markup(self, xmlObject):
        ''' If we have a DarkStar record, put the relevant markup in to distinguish
        it from the rest of the data set. '''
        if self.prisma132 in prisma_ds_ids:
            docIntGrp = xmlObject.xml_create_element(u'DocInternalGrouping',
                attributes = {u'GroupType':u'PqXsearch'})
            grpName = xmlObject.xml_create_element(u'GroupName', content = u'data_darkstar')
            docIntGrp.xml_append(grpName)
            xmlObject.xml_insert_before(xmlObject.LegacyProductMapping, docIntGrp)
            

        
        # These are particular to HAPI records
    def oi_210_insert_DocFeature(self, xmlObject):
        docFeature = xmlObject.xml_create_element(u'DocFeature', content=self.record.notes)
        xmlObject.xml_insert_after(xmlObject.ObjectIds, docFeature)
        
    def oi_220_insert_Terms(self, xmlObject):
        if self.record.subjects or self.record.descriptors:
            terms = xmlObject.xml_create_element(u'Terms')
            xmlObject.xml_insert_after(xmlObject.Contributors, terms)
            
    def oi_221_insert_Terms_subjects(self, xmlObject):
        for termitem in [self.replace_entityrefs(self.record.subjects)]: #, 
                #self.replace_entityrefs(self.record.descriptors)]:
            if termitem:
                for subitem in termitem.split('\t'):
                    if subitem:
                        term = xmlObject.xml_create_element(u'Term',
                            attributes={u'TermType':u'GenSubj', u'TermSource':u'HAPI'})
                        termElem = xmlObject.xml_create_element(u'TermElem',
                            content=subitem, attributes={u'ElemType':u'Term'})
                        term.xml_append(termElem)
                        xmlObject.Terms.xml_append(term)
                    
    def oi_222_insert_Terms_subjects(self, xmlObject):
        for termitem in [self.replace_entityrefs(self.record.descriptors)]: #, 
                #self.replace_entityrefs(self.record.descriptors)]:
            if termitem:
                for subitem in termitem.split('\t'):
                    term = xmlObject.xml_create_element(u'Term',
                        attributes={u'TermType':u'OtherTerms', u'TermSource':u'HAPI'})
                    termElem = xmlObject.xml_create_element(u'TermElem',
                        content=subitem, attributes={u'ElemType':u'Term'})
                    term.xml_append(termElem)
                    xmlObject.Terms.xml_append(term)
            
    # END #
                

        
    def oi_107_bkr(self, xmlObject):
        ''' If this is a book review (i.e. if self.record.bkr == 1) then output
        "Book Review". Otherwise, it is a "Journal Article" '''
        searchObjType = xmlObject.xml_create_element(u'SearchObjectType',
            content=unicode(("Book Review" if self.record.bkr != '' else "Article")))
        xmlObject.xml_insert_before(xmlObject.Title, searchObjType)
        
    def oi_108_copyright(self, xmlObject):
        if self.record.copyright == '':
            copyright = u"Copyright ProQuest LLC"
        else:
            copyright = self.record.copyright
        xmlObject.Copyright.CopyrightData.cht.xml_append(copyright)
        
    def oi_109_dates(self, xmlObject):
        '''  '''
        alnumDate = self.record.udt
        numDate = self.record.sdt
        normAlnumDate = self.helper_normalise_date(alnumDate)
        
        xmlObject.xml_insert_before(xmlObject.Language,
          self.xmlDoc.xml_create_element(u'ObjectAlphaDate',
          content = normAlnumDate))
          
        xmlObject.xml_insert_before(xmlObject.ObjectAlphaDate, 
          self.xmlDoc.xml_create_element(u'ObjectStartDate',
          content = numDate))
        
        if alnumDate != normAlnumDate:
            xmlObject.xml_insert_after(xmlObject.Contributors,
              self.xmlDoc.xml_create_element(u'DateInfo',
              content = alnumDate))
    
    def oi_110_peer_reviewed(self, xmlObject):
        peer = xmlObject.xml_create_element(u'PeerReviewed',
            content=(u"Yes" if self.record.peer == "Y" else u"No"))
        xmlObject.xml_insert_after(xmlObject.PrintLocation, peer)

          
    # START Full Text
    def oi_300_get_FullText(self, xmlObject):
        if self.record.ft == 'Y' or self.record.ft == 'G':
            import sys, os
            #ftBasePath = '/dc/helios/prisma/hashed'
            ftBasePath = '/dc/helios/pqfulltextfeeds'
            ftDir1 = self.record.pqid[-3]
            ftDir2 = self.record.pqid[-3:-1]
            ftFileName = self.record.pqid + '.xml'
            ftFullPath = os.path.join(ftBasePath, ftDir1, ftDir2, ftFileName)
            if os.path.exists(ftFullPath):
                for ftData in amara.binderytools.pushbind(ftFullPath, u'RECORD'):
                    if 'TextInfo' in ftData.ObjectInfo.xml_child_elements:
                        fullText = ftData.ObjectInfo.TextInfo
                        xmlObject.xml_append(fullText)
                        self.add_fulltext_components(ftData, self.record.pqid)
                        self.add_graphics_components(ftData, self.record.pqid)

    # END Full Text
    
    def oi_400_Ethnicity(self, xmlObject):
        if self.record.hsp == "Y":
            ethnicity = u'US Hispanics'
        elif self.record.hsp == "N" or self.record.hsp == '':
            ethnicity = u'Hispanics'
            
        ethnicityElem = xmlObject.xml_create_element(u'Ethnicity',
            content = ethnicity)
        xmlObject.xml_append(ethnicityElem)
    
    def cs_101_insert_dates(self, xmlCstruct):
        self.helper_set_dates()
        xmlCstruct.Parent.ParentInfo.AlphaPubDate.xml_append(
            unicode(self.normAlnumDate))
        xmlCstruct.Parent.ParentInfo.StartDate.xml_append(
            unicode(self.numStartDate))
        xmlCstruct.Parent.ParentInfo.RawPubDate.xml_append(
            self.record.udt)
        
    def Xcs_101_insert_AlphaPubDate(self, xmlCstruct):
        xmlCstruct.Parent.ParentInfo.AlphaPubDate.xml_append(
            unicode(self.helper_normalise_date(self.record.udt)))
    def Xcs_102_insert_StartDate(self, xmlCstruct):
        xmlCstruct.Parent.ParentInfo.StartDate.xml_append(
            unicode(self.record.sdt))
        # ''' As we don't have an explicit end date to use, put in the 
        # start date again. '''
        #xmlCstruct.Parent.ParentInfo.EndDate.xml_append(
        #    unicode(self.record.sdt))
            
    def Xcs_103_insert_RawPubDate(self, xmlCstruct):
        xmlCstruct.Parent.ParentInfo.RawPubDate.xml_append(self.record.udt)

    def Xcs_104_publication(self, xmlCstruct):
        pubTitle = (self.record.publication if self.mappingClass() == 'HAPIPrismaMapping' else self.record.pq_publication)
        xmlCstruct.PublicationInfo.PubLocators.PubTitle.xml_append(pubTitle)
        
    def cs_105_issue(self, xmlCstruct):
        xmlCstruct.Parent.ParentInfo.Issue.xml_append(self.record.isu)

    def cs_106_volume(self, xmlCstruct):
        xmlCstruct.Parent.ParentInfo.Volume.xml_append(self.record.vol)
    
    def Xcs_107_insert_issn(self, xmlCstruct):
        publoc = xmlCstruct.xml_create_element(u'PubLocators')
        
        xmlCstruct.PublicationInfo.PubLocators.Locator.LocType.xml_append(u'ISSN')
        xmlCstruct.PublicationInfo.PubLocators.Locator.LocValue.xml_append(
            unicode(self.record.issn))
        
    def cs_120_insert_legacyId(self, xmlCstruct):
        if self.record.pqid:
            legacyid = self.record.pqid
        else:
            legacyid = self.record.hapiid
        relatedLegacyId = xmlCstruct.xml_create_element(u'RelatedLegacyID')
        legacyPlatform = xmlCstruct.xml_create_element(u'LegacyPlatform',
            content = u'PQ')
        legacyId = xmlCstruct.xml_create_element(u'LegacyID',
            content = legacyid)
        relatedLegacyId.xml_append(legacyPlatform)
        relatedLegacyId.xml_append(legacyId)
        xmlCstruct.xml_insert_before(xmlCstruct.PublicationInfo, relatedLegacyId)
        
        xmlCstruct.LegacyID.xml_append(legacyid)
        
    def cs_121_insert_ParentInfo_Title(self, xmlCstruct):
        if self.record.pq_publication:
            pubTitle = self.record.pq_publication
        else:
            pubTitle = self.record.jtitle
        piTitle = xmlCstruct.xml_create_element(u'Title',
            content = self.replace_entityrefs(pubTitle))
        xmlCstruct.Parent.ParentInfo.xml_insert_before(
            xmlCstruct.Parent.ParentInfo.AlphaPubDate, piTitle)
            
            
    def cs_125_insert_LegacyPubID(self, xmlCstruct):
        if self.record.jid:
            legacyPubID = xmlCstruct.xml_create_element(u'LegacyPubID',
                content = self.record.jid)
            xmlCstruct.PublicationInfo.xml_append(legacyPubID)
        
    def cs_200_insert_Abstract_Component(self, xmlCstruct):
        if self.record.abstract:
            xmlCstruct.xml_append(self.component_template())
            
        
    ''' A helper method that returns the class of a PrismaMapping '''
    def mappingClass(self):
        if re.search('PQPrismaMapping', str(self.__class__)):
            return 'PQPrismaMapping'
        elif re.search('HAPIPrismaMapping', str(self.__class__)):
            return 'HAPIPrismaMapping'
        else:
            return 'PrismaMapping'
            
    def language(self):
        return (self.record.language if self.record.language else self.record.hlanguage)


    def languages(self):
        languages = DSAbstractMapping.languages(self)
        # Because we have some weirdness in the formatting in PRISMA.
        # Better to handle it here than in the superclass, which should
        # have no knowledge of its descendents' internal structure.
        for index, lang in enumerate(languages):
            if re.match("French-based", lang):
                languages[index] = u"Creoles and Pidgins, French-based"
        return languages

    def lang_delimiter(self):
        return '\t'
        
    def cleanLegacyMarkup(self, string):
        return re.sub('(<|&(amp;&)?lt;)/?((S|M)ABS|PARA)(>|&(amp;&)?gt;)', '', string)
        
    def helper_set_dates(self):
        self.alnumDate = self.record.udt
        self.normAlnumDate = self.helper_normalise_date(self.alnumDate)
        self.numStartDate = self.pq_numeric_date(self.normAlnumDate)
