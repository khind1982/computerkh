''' IIMP/IIPA mapping '''

import amara, re, os
from ds_abstract_mapping import DSAbstractMapping
import sys
sys.path.append(str(__file__ + '/../'))
from miscUtils import *
from EntityShield import protect, unprotect
import codecs
from iimprids import iimp_rids
from iiparids import iipa_rids

docTypes = {
    'Biographical Profile': u'Biography',
    'Profile': u'Biography',
    'Discography': u'Discography/Filmography',
    'Filmography': u'Discography/Filmography',
    'Essay (Text)': u'Essay',
    'Literary Criticism': u'Essay',
    'Photoessay': u'Essay',
    'Correspondence (Text)': u'Letter',
    'Letter to the Editor': u'Letter',
    'Eulogy': u'Obituary',
    'Book Excerpt': u'Book Chapter',
    'Play (Text)': u'Fiction',
    'Screenplay': u'Fiction',
    'Story (Text)': u'Fiction',
    'Text Excerpt': u'Fiction',
    'Book Illustrations': u'Illustration',
    'Memoirs': u'Memoir/Personal Document',
    'Tbl of Contents': u'Table of Contents',
    'Poem (Text)': u'Poem',
    'Musical Catalog': u'Catalog',
    'Organizational Profile': u'Company Profile',
    'Instruction/Guidelines': u'Instruction/Guidelines',
    'Listening Guide': u'Instruction/Guidelines',
    'Statistics': u'Statistics/Data Report',
    'Recording Review': u'Audio Review',
    'Radio Review': u'Audio Review',
    'Music Review': u'Audio Review',
    'Exhibit Review': u'Exhibition Review',
    'General Review': u'Review',
    'Multimedia/Software Review': u'Software Review',
    'Lecture': u'Speech/Lecture',
    'Speech': u'Speech/Lecture',
    'Roundtable Discussion': u'Transcript',
    }


journalsWithoutLanguage = {
    'Variety': u'English',
    'Opernwelt - das internationale Opernmagazin': u'German',
    'The Journal of Aesthetics and Art Criticism': u'English',
    'The Village Voice': u'English',
    'Medical Problems of Performing Artists': u'English'
    }


class IIMPAMapping(DSAbstractMapping):
    def __init__(self, record):
        DSAbstractMapping.__init__(self, record)
        if self.record.journaltitle in journalsWithoutLanguage.keys():
            if self.language() == '':
                self.record.language = journalsWithoutLanguage[self.record.journaltitle]


    def do_mapping(self):
        xmlCstruct, xmlObject = DSAbstractMapping.do_mapping(self)
        
        self.buildControlStructure(xmlCstruct)
        self.buildObjectInfo(xmlObject)
        
        xmlProduct = self.xmlDoc.RECORD.xml_append(
            self.xmlDoc.xml_create_element(u'Product'))
        self.build_part(xmlProduct, 'pr')
        
        return self.xmlDoc
        
        
    def oi_101_title(self, xmlObject):
        if self.record.title == '':
            title = u'[untitled]'
        else:
            title = protect(unprotect(self.record.title, pad=False))
        xmlObject.Title.cht.xml_append(self.replace_entityrefs(title))
        #sys.stderr.write(codecs.encode(title, 'UTF8') + '\n')
          
    def oi_102_author(self, xmlObject):
        if self.record.author:
            self.author_count += 1
            xmlObject.Contributors.xml_append(
                self.contributor_template('Author',
                {'OriginalForm': self.replace_entityrefs(self.record.author)}))
        
    def oi_103_coauthor(self, xmlObject):
        if self.record.coauthor:
            coauthors = [author.rstrip() for author in self.record.coauthor.split('|') if author.rstrip()]
            for coauthor in coauthors:
                self.author_count += 1
                xmlObject.Contributors.xml_append(
                    self.contributor_template('Author',
                    {'OriginalForm': self.replace_entityrefs(coauthor)}))
                
                
    def oi_104_printLocation(self, xmlObject):
        pagedisplay = unicode(self.record.pagedisplay.rstrip())
        pagedisplay = re.sub(r"[]'., +-]+?$", '', pagedisplay)
        #pagedisplay = re.sub(r'(\d+) -(\d+)', r'\1-\2', pagedisplay)
        pagedisplay = re.sub(r'(\d+) ?- ?(\d+)', r'\1-\2', pagedisplay)
        if re.search(r'^[0-9-,]+ ff\.', pagedisplay):
            startPage = self.helper_startPage(pagedisplay)
            endPage = u''
        elif re.search(r'^[0-9-]+ \[sic\]', pagedisplay):
            display = re.search(r'^([0-9-]+) \[sic\]', pagedisplay).group(1)
            sys.stderr.write(display + '\n')
            startPage = self.helper_startPage(display)
            endPage = self.helper_endPage(display)
        elif re.search(r'^[0-9+-,]+', pagedisplay):
            startPage = self.helper_startPage(pagedisplay)
            endPage = self.helper_endPage(pagedisplay)
        elif re.search(r'[sS]ec(tion)? [iI]nsert', pagedisplay):
            startPage = pagedisplay
            endPage = pagedisplay
        elif re.search(r'Front\.?', pagedisplay):
            startPage = pagedisplay
            endPage = u''
        elif re.search(r'\[\d+\]( ff\.)?', pagedisplay):
            startPage = pagedisplay
            endPage = u''
        elif re.search(r'\d+ ?-$', pagedisplay):
            startPage = re.match(r'\d+', pagedisplay).group(0)
            endPage = startPage
        elif re.search(r'^[^A-Za-z0-9 -]+', pagedisplay):
            startPage = pagedisplay
            endPage = u''
        elif re.search(r'[A-Za-z0-9]+.*', pagedisplay):
            startPage = pagedisplay
            endPage = u''
        else:
            startPage = self.helper_startPage(pagedisplay)
            endPage = self.helper_endPage(pagedisplay)
        xmlObject.PrintLocation.StartPage.xml_append(unicode(startPage))
        if endPage == '':
            xmlObject.PrintLocation.xml_remove_child(
                xmlObject.PrintLocation.EndPage)
        else:
            xmlObject.PrintLocation.EndPage.xml_append(unicode(endPage))
        xmlObject.PrintLocation.Pagination.xml_append(unicode(pagedisplay))
        
    def oi_105_copyright(self, xmlObject):
        xmlObject.Copyright.CopyrightData.cht.xml_append(u'Copyright ProQuest LLC')
        
    def Xoi_106_dates(self, xmlObject):
        self.helper_set_dates()
        
        xmlObject.xml_insert_before(xmlObject.Language,
            self.xmlDoc.xml_create_element(u'ObjectAlphaDate',
                content=self.normAlnumDate))
        
        xmlObject.xml_insert_before(xmlObject.ObjectAlphaDate,
            xmlObject.xml_create_element(u'ObjectStartDate',
                content=self.numStartDate))
                
        ##xmlObject.xml_insert_after(xmlObject.ObjectStartDate,
        ##    xmlObject.xml_create_element(u'ObjectEndDate',
        ##    content=self.numEndDate))
        
        if self.alnumDate != self.normAlnumDate:
            xmlObject.xml_insert_after(xmlObject.Contributors,
                self.xmlDoc.xml_create_element(u'DateInfo'))
            xmlObject.DateInfo.xml_append(self.xmlDoc.xml_create_element(
                u'Dates', attributes ={u'DateType':u'Publ'}, 
                content=self.alnumDate))
        
    def oi_107_publisher(self, xmlObject):
        publisherData = {}
        if self.record.publisher:
            publisherData['Publisher'] = self.replace_entityrefs(self.record.publisher)
        if self.record.publishcountry:
            publisherData['CountryName'] = self.replace_entityrefs(self.record.publishcountry)
        if len(publisherData) > 0:
            xmlObject.Contributors.xml_append(
                self.contributor_template('Publisher',
                publisherData))
                
        
    
    def oi_108_journalid(self, xmlObject):
        objectId = xmlObject.xml_create_element(u'ObjectId',
            attributes = {u'IdType':u'DOC_ID', 
                          u'IdSource':u'CH'},
            content = self.replace_entityrefs(self.record.articleid))
            #content = self.record.journalid)
        xmlObject.ObjectIds.xml_append(objectId)
        
    def oi_109_abstract(self, xmlObject):
        if self.record.abstract:
            abstract = self.xmlDoc.xml_create_element(u'Abstract',
                attributes={u'AbstType':u'excerpt'}) #,
                    #u'Lang':self.language(),
                    #u'isocode':self.lang_iso()})
            para = abstract.xml_append(self.xmlDoc.xml_create_element(u'paragraph'))
            cht = para.xml_append(self.xmlDoc.xml_create_element(u'cht',
                content=self.replace_entityrefs(self.record.abstract)))
            xmlObject.Abstracts.xml_append(abstract)
        if len(xmlObject.Abstracts.xml_child_elements) is 0:
            xmlObject.xml_remove_child(xmlObject.Abstracts)

    def oi_110_terms_container(self, xmlObject):
        terms = self.xmlDoc.xml_create_element(u'Terms')
        if 'DateInfo' in xmlObject.xml_child_elements:
            xmlObject.xml_insert_after(xmlObject.DateInfo, terms)
        else:
            xmlObject.xml_insert_after(xmlObject.Contributors, terms)
        
    def oi_111_term(self, xmlObject):
        term_attrs = {
            'subject':'GenSubj',
            'cloc':'Geo',
            'cnam':'Personal',
            'corg':'Company',
            'csbj':'Thes',
            'csup':'Suppl'
            }
        for term in '''subject cloc cnam corg csbj csup'''.split():
            if eval('self.record.'+term):
                if term in term_attrs.keys():
                    attrName = term_attrs[term]
                else:
                    attrName = term.capitalize()
                for word in eval('self.record.'+term).split('|'):
                    xmlObject.Terms.xml_append(
                        self.helper_create_term(attrName, 
                            self.replace_entityrefs(word)))
                            
    
    def oi_112_naxos_terms(self, xmlObject):
        for termName in '''naxosartist naxoschoir naxoscomposer
                    naxosconductor naxosensemble naxosorchestra'''.split():
            if eval('self.record.'+termName):
                for item in eval('self.record.'+termName).split('|'):
                    term, termId = item.split(':')
                    naxosCaps = "Naxos" + re.match('naxos(.*)', termName).group(1).capitalize()
                    xmlObject.Terms.xml_append(
                        self.helper_create_term(naxosCaps,
                            self.replace_entityrefs(term)))
                    xmlObject.Terms.xml_append(
                        self.helper_create_term(naxosCaps, termId))

    def oi_113_peer_reviewed(self, xmlObject):
        if self.record.peerreviewflag:
            if re.match(r'1|Yes', self.record.peerreviewflag):
                flag = u'Yes'
            else:
                flag = u'No'
            peer = xmlObject.xml_create_element(u'PeerReviewed',
                content=flag)
            xmlObject.xml_insert_after(xmlObject.PrintLocation, peer)

    def oi_120_insert_productid(self, xmlObject):
        xmlObject.LegacyProductMapping.GroupName.xml_append(self.record.productid)
        
    def Xoi_130_insert_DarkStar_markup(self, xmlObject):
        ''' If this is a member of the DarkStar data set, mark it up accordingly '''
        if self.journalid in iimp_iipa_darkstar:
            pass
        
    def oi_150_issn(self, xmlObject):
        if self.record.issn:
            issn = self.xmlDoc.xml_create_element(u'ObjectId',
                attributes={u'IdType':u'ISSN'}, content=self.replace_entityrefs(self.record.issn))
            xmlObject.ObjectIds.xml_append(issn)
    
    def oi_151_docFeatures_container(self, xmlObject):
        if self.record.specialfeatures:
            for docfeature in self.record.specialfeatures.split('|'):
                feature = xmlObject.xml_create_element(u'DocFeature',
                    content = self.replace_entityrefs(docfeature))
                xmlObject.xml_insert_before(xmlObject.Contributors, feature)
        
    def Xoi_152_docFeatures(self, xmlObject):
        if 'DocFeatures' in xmlObject.xml_child_elements:
            feature = xmlObject.xml_create_element(u'DocFeature',
                content=self.record.specialfeatures)
            xmlObject.DocFeatures.xml_append(feature)
    
    def oi_153_insert_documenttype(self, xmlObject):
        for thing in self.record.documenttype.split('|'):
            if thing:
                if thing in docTypes:
                    docType = docTypes[thing]
                else:
                    docType = thing
                xmlObject.xml_insert_before(xmlObject.Title, 
                    xmlObject.xml_create_element(u'SearchObjectType', 
                        content=self.replace_entityrefs(docType)))

    def Xoi_154_insert_articleid(self, xmlObject):
        objId = self.xmlDoc.xml_create_element(u'ObjectId',
            attributes={u'IdType':u'DOC_ID',
                        u'IdSource':u'DsolArticleid'},
            content = self.record.articleid)
        xmlObject.ObjectIds.xml_append(objId)
    
    
    def oi_200_insertLinks(self, xmlObject):
        links = xmlObject.xml_create_element(u'Links')
        for linkType in ['Jstor', 'museurl', 'onlineurl', 'Pmurl']:
            if eval('self.record.'+linkType):
                link = xmlObject.xml_create_element(u'Link',
                    content = eval('self.record.'+linkType),
                    attributes={u'LinkType':u'docurl'})
                links.xml_append(link)
        if 'Link' in links.xml_child_elements:
            xmlObject.xml_append(links)
        
    def Xoi_201_Jstor_links(self, xmlObject):
        if self.record.Jstor:
            link = xmlObject.xml_create_element(u'Link',
                attributes = {u'LinkType':u'DsolJstor'},
                content=self.record.Jstor)
            xmlObject.Links.xml_append(link)
            
    def Xoi_202_museurl_link(self, xmlObject):
        if self.record.museurl:
            link = xmlObject.xml_create_element(u'Link',
                attributes = {u'LinkType':u'DsolMuseurl'},
                content=self.record.museurl)

    def oi_300_insert_alternate_title(self, xmlObject):
        if self.record.translatedtitle:
            altTitle = xmlObject.xml_create_element(u'AlternateTitle')
            cht = xmlObject.xml_create_element(u'cht',
                content = self.replace_entityrefs(self.record.translatedtitle))
            altTitle.xml_append(cht)
            xmlObject.xml_insert_after(xmlObject.Title, altTitle)
            
    def oi_320_insert_pqarticlimageid(self, xmlObject):
        if self.record.pqarticleimageid:
            imgId = xmlObject.xml_create_element(u'ObjectId', 
                attributes={u'IdType':u'DOC_ID', u'IdSource':u'idsource'},
                content=self.replace_entityrefs(self.record.pqarticleimageid))
            xmlObject.ObjectIds.xml_append(imgId)
                
    def oi_500_insert_FullText_data(self, xmlObject): # USE THIS NORMALLY
        # A new day, a new approach...
        if not re.search(r'-', self.record.articleid):
            prod = self.record.productid
            ch_id = re.search(r'ii(mp|pa)[A-Za-z]*0*([0-9_-]+)', self.record.articleid).group(2)
            if ch_id in eval(prod+'_rids.keys()'):
                pq_id = eval(prod+'_rids["'+ch_id+'"]')
                #ftBasePath = '/dc/helios/prisma/hashed'
                ftBasePath = '/dc/helios/pqfulltextfeeds'
                ftDir1 = pq_id[-3]
                ftDir2 = pq_id[-3:-1]
                ftFileName = pq_id + '.xml'
                ftFullPath = os.path.join(ftBasePath, ftDir1, ftDir2, ftFileName)
                if os.path.exists(ftFullPath):
                    for ftData in amara.binderytools.pushbind(ftFullPath, u'RECORD'):
                        if 'TextInfo' in ftData.ObjectInfo.xml_child_elements:
                            fullText = ftData.ObjectInfo.TextInfo
                            if 'Links' in xmlObject.xml_child_elements:
                                xmlObject.xml_insert_before(xmlObject.Links, fullText)
                            else:
                                xmlObject.xml_append(fullText)
                            
                            self.add_fulltext_components(ftData, unicode(pq_id))
                            
                            self.add_graphics_components(ftData, unicode(pq_id))
                            
                            relLegacyID = self.xmlDoc.xml_create_element(u'RelatedLegacyID')
                            legacyPlatform = self.xmlDoc.xml_create_element(u'LegacyPlatform', 
                                content = u'PQ')
                            legacyID = self.xmlDoc.xml_create_element(u'LegacyID',
                                content = unicode(pq_id))
                            relLegacyID.xml_append(legacyPlatform)
                            relLegacyID.xml_append(legacyID)
                            self.xmlDoc.RECORD.ControlStructure.xml_insert_before(
                                self.xmlDoc.RECORD.ControlStructure.PublicationInfo,
                                relLegacyID)
                            
            
    def Xoi_500_insert_FullText_data(self, xmlObject):
        ''' First, derive the CH id from the articleid field. Strip off the iimp/iipa
        marker, and any leading 0's '''
        if not re.search(r'-', self.record.articleid):
            prodId = self.record.productid
            ch_id = re.search(r'ii(mp|pa)[BF]?0*([0-9_-]+)', self.record.articleid).group(2)
            if ch_id in eval(prodId+'_rids.keys()'):
                pqid = eval(prodId+'_rids["'+ch_id+'"]')
                
                if self.record.journaltitle in eval(prodId+'_journals.keys()'):
                    jrnl = eval(prodId+'_journals['+self.record.journaltitle+']')
                else:
                    jrnl = 'NONESUCH'
                vol = self.record.journalvolume
                iss = self.record.journalissue
                base_path = os.path.join(jrnl, vol, iss, pqid)
                
                ''' FullText'''
                ftComp = self.xmlDoc.xml_create_element(u'Component',
                    attributes = {u'ComponentType': u'FullText'})
                ftCHImageId = self.xmlDoc.xml_create_element(u'CHImageIds')
                chidElem = self.xmlDoc.xml_create_element(u'chid',
                    content=unicode(base_path))
                ftCHImageId.xml_append(chidElem)
                ftComp.xml_append(ftCHImageId)
                
                ftRepr = self.xmlDoc.xml_create_element(u'Representation',
                    attributes = {u'RepresentationType':u'FullText'})
                mime = self.xmlDoc.xml_create_element(u'MimeType', content = u'text/html')
                resides = self.xmlDoc.xml_create_element(u'Resides', content = u'CH/html')
                
                ftRepr.xml_append(mime)
                ftRepr.xml_append(resides)
                
                ftComp.xml_append(ftRepr)
                self.xmlDoc.RECORD.ControlStructure.xml_append(ftComp)
                
                ''' PDFFullText '''
                pdfComp = self.xmlDoc.xml_create_element(u'Component',
                    attributes = {u'ComponentType':u'FullText'})
                pdfCHImageId = self.xmlDoc.xml_create_element(u'CHImageIds')
                pqidElem = self.xmlDoc.xml_create_element(u'pqid', content = unicode(pqid))
                
                pdfCHImageId.xml_append(pqidElem)
                
                pdfRepr = self.xmlDoc.xml_create_element(u'Representation',
                    attributes = {u'RepresentationType':u'PDFFullText'})
                legacyFmt = self.xmlDoc.xml_create_element(u'LegacyFormat',
                    content = u'PageImage')
                mime = self.xmlDoc.xml_create_element(u'MimeType', content = u'application/pdf')
                resides = self.xmlDoc.xml_create_element(u'Resides', content = u'PQ')
                pdfRepr.xml_append(mime)
                pdfRepr.xml_append(resides)
                pdfRepr.xml_append(legacyFmt)
                
                pdfComp.xml_append(pdfCHImageId)
                pdfComp.xml_append(pdfRepr)
                
                self.xmlDoc.RECORD.ControlStructure.xml_append(pdfComp)
            
            
    def oi_900_remove_Terms_if_empty(self, xmlObject):
        if len(xmlObject.Terms.xml_child_elements) is 0:
            xmlObject.xml_remove_child(xmlObject.Terms)
    
    def oi_901_remove_Contributors_if_empty(self, xmlObject):
        if len(xmlObject.Contributors.xml_child_elements) is 0:
            xmlObject.xml_remove_child(xmlObject.Contributors)

    
    def cs_101_insert_PublicationInfo(self, xmlCstruct):
        if self.record.journalid:
            legacyPubID = xmlCstruct.xml_create_element(u'LegacyPubID',
                content = self.replace_entityrefs(self.record.journalid))
            xmlCstruct.PublicationInfo.xml_append(legacyPubID)
        else:
            xmlCstruct.PublicationInfo.xml_append(self.xmlDoc.xml_create_element(
                u'PubLocators'))
            xmlCstruct.PublicationInfo.PubLocators.xml_append(
                xmlCstruct.xml_create_element(u'PubTitle', 
                content = self.replace_entityrefs(self.record.journaltitle)))
            locator = xmlCstruct.xml_create_element(u'Locator')
            locType = xmlCstruct.xml_create_element(u'LocType', content = u'ISSN')
            locValue = xmlCstruct.xml_create_element(u'LocValue', 
                content = self.replace_entityrefs(self.record.issn))
            
            locator.xml_append(locType)
            locator.xml_append(locValue)
            
            xmlCstruct.PublicationInfo.PubLocators.xml_append(locator)
            #xmlCstruct.PublicationInfo.PubLocators.Locator.LocType.xml_append(
            #    unicode('ISSN'))
            #xmlCstruct.PublicationInfo.PubLocators.Locator.LocValue.xml_append(
            #    self.record.issn)
        
    def cs_102_dates(self, xmlCstruct):
        self.helper_set_dates()
        xmlCstruct.Parent.ParentInfo.StartDate.xml_append(self.numStartDate)
        ##xmlCstruct.Parent.ParentInfo.EndDate.xml_append(self.numEndDate)
        xmlCstruct.Parent.ParentInfo.AlphaPubDate.xml_append(self.normAlnumDate)
        xmlCstruct.Parent.ParentInfo.RawPubDate.xml_append(self.alnumDate)

    def cs_103_Volume(self, xmlCstruct):
        xmlCstruct.Parent.ParentInfo.Volume.xml_append(self.record.journalvolume)
        
    def cs_104_Issue(self, xmlCstruct):
        xmlCstruct.Parent.ParentInfo.Issue.xml_append(self.record.journalissue)
    
    
    def cs_106_issuenote(self, xmlCstruct):
        if self.record.issuenote:
            xmlCstruct.Parent.ParentInfo.xml_append(self.xmlDoc.xml_create_element(
                u'NonStdCit', content=self.replace_entityrefs(self.record.issuenote)))
            
    def cs_120_insert_spub(self, xmlCstruct):
        if self.record.spub:
            spub = xmlCstruct.xml_create_element(u'Supplement',
                content = self.replace_entityrefs(self.record.spub))
            if 'NonStdCit' in xmlCstruct.Parent.ParentInfo.xml_child_elements:
                xmlCstruct.Parent.ParentInfo.xml_insert_before(
                    xmlCstruct.Parent.ParentInfo.NonStdCit, spub)
            else:
                xmlCstruct.Parent.ParentInfo.xml_append(spub)
    
    def cs_130_insert_legacyID(self, xmlCstruct):
        xmlCstruct.LegacyID.xml_append(self.record.articleid)
        #xmlCstruct.Parent.ParentInfo.LegacyID.xml_append(self.record.articleid)
        
    def cs_135_insert_ParentInfo_Title(self, xmlCstruct):
        piTitle = xmlCstruct.xml_create_element(u'Title',
            content = self.replace_entityrefs(self.record.journaltitle))
        xmlCstruct.Parent.ParentInfo.xml_insert_after(
            xmlCstruct.Parent.ParentInfo.LegacyPlatform, piTitle)
        
    def cs_200_insert_Abstract_Component(self, xmlCstruct):
        if self.record.abstract:
            xmlCstruct.xml_append(self.component_template())
        
    def pr_101_insert_CHIMPA_section(self, xmlProduct):
        xmlProduct.xml_append(self.xmlDoc.xml_create_element(
            u'CHIMPA'))
        
    def pr_102_insert_CHIMPA_Markup(self, xmlProduct):
        for item in ['royaltiesid', 'autoftflag', 'fulltextflag', 
                'musecollection', 'char', 'workassubject', 'tngflag']:
            value = eval('self.record.'+item)
            if value:
                for thing in value.split('|'):
                    chMarkup = self.xmlDoc.xml_create_element(u'CHIMPA_Markup',
                        attributes={u'CHIMPA-MarkupInd':unicode(item)})
                    chMarkup.xml_append(self.xmlDoc.xml_create_element(u'cht',
                        content=self.replace_entityrefs(thing)))
                    xmlProduct.CHIMPA.xml_append(chMarkup)
                
    
    def pr_103_insert_CHIMPA_AltJrnlTitles(self, xmlProduct):
        for thing in self.record.altjournaltitles.split('|'):
            if thing:
                altJrnlTitles = xmlProduct.xml_create_element(u'CHIMPA_AltJrnlTitles')
                altTitle = xmlProduct.xml_create_element(u'CHIMPA_AltJrnlTitle',
                    content=self.replace_entityrefs(thing))
                altJrnlTitles.xml_append(altTitle)
                xmlProduct.CHIMPA.xml_append(altJrnlTitles)
        for thing in self.record.altjournalinfo.split('|'):
            if thing:
                altJrnlTitles = xmlProduct.xml_create_element(u'CHIMPA_AltJrnlTitles')
                altTitle = xmlProduct.xml_create_element(u'CHIMPA_AltJrnlTitle',
                    content=self.replace_entityrefs(thing))
                altJrnlTitles.xml_append(altTitle)
                xmlProduct.CHIMPA.xml_append(altJrnlTitles)
        
        
    def Xpr_103_insert_CHIMPA_AltJrnlTitles_container(self, xmlProduct):
        if self.record.altjournalinfo or self.record.altjournaltitles:
            xmlProduct.CHIMPA.xml_append(self.xmlDoc.xml_create_element(
                u'CHIMPA_AltJrnlTitles'))
    
    def Xpr_104_insert_CHIMPA_altJournalInfo_record(self, xmlProduct):
        if 'CHIMPA_AltJrnlTitles' in xmlProduct.CHIMPA.xml_child_elements:
            for thing in self.record.altjournalinfo.split('|'):
                if thing:
                    xmlProduct.CHIMPA.CHIMPA_AltJrnlTitles.xml_append(self.xmlDoc.xml_create_element(
                        u'CHIMPA_AltJrnlTitle', content=thing))
            for thing in self.record.altjournaltitles.split('|'):
                if thing:
                    xmlProduct.CHIMPA.CHIMPA_AltJrnlTitles.xml_append(self.xmlDoc.xml_create_element(
                        u'CHIMPA_AltJrnlTitle', content=thing))
    
    #==================================
    
    def helper_set_dates(self):
        
        import sys
        
        transDate = self.translateDate(self.record.pubdisplaydate)
        
        # Some records have the date in twice, separated by a vertical bar.
        # We need to preserve this in the alnumDate value (output as RawDate),
        # but ignore it when working out the normalised date.
        
        self.alnumDate = self.record.pubdisplaydate
        
        #sys.stderr.write(self.alnumDate)
        
        ##self.numStartDate = self.record.publishedstartdate
        ##self.numEndDate = self.record.publishedenddate
        
        #self.normAlnumDate = self.helper_normalise_date(self.alnumDate.split('|')[0])
        self.normAlnumDate = self.helper_normalise_date(transDate.split('|')[0])
        
        self.numStartDate = self.pq_numeric_date(self.normAlnumDate)
        
        ## Make sure we don't have month and day values of '00'
        ##if re.search('0000$', self.numStartDate):
        ##   self.numStartDate = re.sub('0000$', '0101', self.numStartDate)
        ##if re.search('0000$', self.numEndDate):
        ##    self.numEndDate = re.sub('0000$', '0101', self.numEndDate)
        ##if re.search('00$', self.numStartDate):
        ##    self.numStartDate = re.sub('00$', '01', self.numStartDate)
        ##if re.search('00$', self.numEndDate):
        ##    self.numEndDate = re.sub('00$', '01', self.numEndDate)
        
    def helper_create_term(self, termType, termElemContent):
        term = self.xmlDoc.xml_create_element(u'Term',
            attributes={u'TermType':unicode(termType), u'TermSource':u'CH'})
        term.xml_append(term.xml_create_element(u'TermElem',
            content=termElemContent,
            attributes={u'ElemType': self.determineElemType(termType)})) 
        return term
    
    def determineElemType(self, termType):
        elemtypes = {u'Company':u'CompanyName'}
        if termType in elemtypes.keys():
            return elemtypes[termType]
        else:
            return u'Term'

    def translateDate(self, datestring):
        ''' Edge cases go here. These are things that will take too much time to
        try and fix elegantly, so they'll have to be hacks. '''
        dateMatch = re.match('June/Juin (\d{2,4})', datestring)
        if dateMatch:
            return "June " + dateMatch.group(1)
        
        dateMatch = re.match('Awards (\d{4})', datestring)
        if dateMatch:
            return dateMatch.group(1)
        dateMatch = re.match('Special (\d{4})', datestring)
        if dateMatch:
            return dateMatch.group(1)
        dateMatch = re.match('^Proms (\d{4})$', datestring)
        if dateMatch:
            return u'Summer ' + dateMatch.group(1)
        
        ''' Take a date string in a foreign language, and attempt to translate it
        into English. '''
        ''' It turns out there's absolutely no point in trying to be clever here.
        Some records claim to be in French, but have German dates, some are apparently
        English and have foreign dates...''' 
        re.U
        datestring = codecs.encode(datestring, 'utf8')
        
        datestring = re.sub(r'^.{2}t.{2} ', 'Summer ',    datestring)
        
        datestring = re.sub(r'janv\.',    'January',   datestring)
        datestring = re.sub(r'f.*vr\.',   'February',  datestring)
        datestring = re.sub(r'mars',      'March',     datestring)
        datestring = re.sub(r'avril',     'April',     datestring)
        datestring = re.sub(r'[Mm]ai',    'May',       datestring)
        datestring = re.sub(r'juin',      'June',      datestring)
        datestring = re.sub(r'juil\.',    'July',      datestring)
        datestring = re.sub(r'ao.{2}t',   'August',    datestring)
        datestring = re.sub(r'sept\.',    'September', datestring)
        datestring = re.sub(r'oct\.',     'October',   datestring)
        datestring = re.sub(r'nov\.',     'November',  datestring)
        datestring = re.sub(r'd.*c\.',    'December',  datestring)
        
        datestring = re.sub(r'genn\.',  'January', datestring)
        datestring = re.sub(r'mar\.',   'March', datestring)
        datestring = re.sub(r'apr\.',   'April', datestring)
        datestring = re.sub(r'giugno',  'June', datestring)
        datestring = re.sub(r'luglio',  'July', datestring)
        datestring = re.sub(r'sett\.',  'September', datestring)
        datestring = re.sub(r'ott\.',   'October', datestring)
        
        
        
        datestring = re.sub(r'Jan\.', 'January', datestring)
        datestring = re.sub(r'M.*rz', 'March', datestring)
        datestring = re.sub(r'Juli', 'July', datestring)
        datestring = re.sub(r'Sept\.', 'September', datestring)
        datestring = re.sub(r'Okt\.', 'October', datestring)
        datestring = re.sub(r'Dez\.', 'December', datestring)
        return codecs.decode(datestring)
        

    def lang_delimiter(self):
        return '|'
