''' BP mapping '''

import amara, re
from ds_abstract_mapping import DSAbstractMapping
from bpRecord import *
from ZoneTemplate import ZoneTemplate

""" Tasklist:

Component tag for dirtyascii - done
Normalise dates - done

dates: use freqpub to identify noday ones; tweak alphanum generator to produce month only
check george eliot in reviewauth
journals file 3130 has a journaleditor that looks like it should be a city...
object sequence number
journal data - subject, publisher, place
part journal publisher/printer? So we can put place of pub in? in contributor?
add pagecount to components?
rename image type - done but untested
using os.spawn errors get lost - you only spot them if record count falls short

how was dan deleting empty tags?
look for insert_afters - should these be put in abstract mapping?
speeeeed!
Test folding the two page image component functions together - faster?
wellesley details desc contains entreffed tags
abstract contains mangled entrefs

languages - not used in current product so v. low priority
Do non-wellesley version too????? not for helios

QUERY:
question marks in attributes
Title language attribute - anything other than english? format?

QUERY LATER:
Legacypubid - using this instead of publocator means we lose part-journal info - does part-journal
info matter in product?


"""

"""
from bp_mapping import test
test()
"""

"""
Get number of records for each journal from bp database:
SELECT journalid, COUNT(*) FROM indexrecord GROUP BY journalid;
"""


def test():

    outf = open('ea00.txt', 'w')

    j = BPJournal()
    for rec in j.helios('ea00', partsize=5000, startpart=0):
        mappedrec = BPMapping(rec)
        mappedrec.do_mapping()
        outf.write(mappedrec.xmlDoc.xml(indent='yes'))
    outf.close()

def process_journal(journalid, outfile):

    outf = open(outfile, 'w')
    
    j = BPJournal()
    for rec in j.helios(journalid):
        mappedrec = BPMapping(rec)
        mappedrec.do_mapping()
        outf.write(mappedrec.xmlDoc.xml(indent='yes'))
    outf.close()
            
def compilejournalmap():

    inf = open('bp_norm.xml', 'r')
    jdata = inf.read()
    inf.close()
    
    jdocs = jdata.split('</document>')
    jidre = re.compile('<element name="journalid">(.*?)</element>')
    publre = re.compile('<element name="publisher">(.*?)</element>')
    subjre = re.compile('<element name="subject">(.*?)</element>')
    
    jmap = {}
    
    for doc in jdocs:
        if jidre.search(doc) != None:
            jid = jidre.search(doc).group(1)
            jmap[jid] = {}
            if publre.search(doc) != None:
                jmap[jid]['publisher'] = publre.search(doc).group(1)
            if subjre.search(doc) != None:
                jmap[jid]['subjects'] = subjre.search(doc).group(1).split('|')
                
    return jmap

global journalmap
journalmap = compilejournalmap()

global nodayfrequencies
nodayfrequencies = {
                            'Weekly': '',
                            'Daily': '',
                            'Bi-monthly': '',
                            'Bi-weekly': '',
                            'Semi-weekly': '',
                            'Tri-weekly': '',
                            'Semi-monthly': ''
                            }


class BPMapping(DSAbstractMapping):

    def __init__(self, record):
        DSAbstractMapping.__init__(self, record)
        self.journalmap = journalmap
        self.preparedates()
#        self.alphadate = ' '.join([str(self.record.date)[6:].lstrip('0'), self.record.month, str(self.record.date)[0:4]])
#        self.normaldate = self.helper_normalise_date(self.alphadate)
#        self.pqnumericdate = self.pq_numeric_date(self.normaldate)
        self.contribcounter = 0
        
    def do_mapping(self):
        xmlCstruct, xmlObject = DSAbstractMapping.do_mapping(self)
        
        ''' Build the ControlStructure '''
        self.buildControlStructure(xmlCstruct)
        
        ''' Build the ObjectInfo '''
        self.buildObjectInfo(xmlObject)
        
        """
        xmlAttach = self.xmlDoc.RECORD.xml_append(
                    self.xmlDoc.xml_create_element(u'Attachments'))
        """
        
        xmlLegacy = self.xmlDoc.RECORD.xml_append(
                    self.xmlDoc.xml_create_element(u'LegacyData'))
        
        """
        ''' Build the Attachments section - for threading info '''
        self.buildAttachments(xmlAttach)
        """
        
        ''' Build the LegacyData section - for full text '''
        self.buildLegacyData(xmlLegacy)
        
        return [self.xmlDoc.RECORD.ControlStructure, 
                self.xmlDoc.RECORD.ObjectInfo]
                
    """
    def buildAttachments(self, xmlAttach):
        self.build_part(xmlAttach, 'at')
    """

    def buildLegacyData(self, xmlLegacy):
        self.build_part(xmlLegacy, 'ld')
        
    def preparedates(self):
        self.alphadate = ' '.join([self.record.month, str(self.record.date)[0:4]])
        if len(self.record.PartJournalTitleSet) > 0:
            if nodayfrequencies.has_key(self.record.PartJournalTitleSet[0].freqpub):
                self.alphadate = ' '.join([str(self.record.date)[6:].lstrip('0'), self.alphadate])
        self.normaldate = self.helper_normalise_date(self.alphadate)
        self.pqnumericdate = self.pq_numeric_date(self.normaldate)
            
    def cs_101_bpid(self, xmlCstruct):
        xmlCstruct.LegacyID.xml_append(unicode(self.record.bpid))

    def cs_102_journalid(self, xmlCstruct):
        xmlCstruct.PublicationInfo.xml_append(self.xmlDoc.xml_create_element(u'LegacyPubID',
           content=self.record.journalid))

    def cs_103_journaltitle(self, xmlCstruct):
        
        if len(self.record.PartJournalTitleSet) > 1:
            print "too many part journals! " + self.record.bpid
            sys.exit()
        else:
            pubtitle = unicode(self.record.PartJournalTitleSet[0].journaltitle)
        xmlCstruct.Parent.ParentInfo.xml_insert_after(xmlCstruct.Parent.ParentInfo.LegacyPlatform,
            self.xmlDoc.xml_create_element(u'Title',
            content=pubtitle))
    
    def cs_104_date(self, xmlCstruct):        
        xmlCstruct.Parent.ParentInfo.AlphaPubDate.xml_append(unicode(self.normaldate))
        
    def cs_105_startdate(self, xmlCstruct):
        xmlCstruct.Parent.ParentInfo.StartDate.xml_append(unicode(self.pqnumericdate))
        
    def cs_106_volume(self, xmlCstruct):
        if self.record.volume != None:
            xmlCstruct.Parent.ParentInfo.Volume.xml_append(unicode(self.record.volume))
        
    def cs_107_issue(self, xmlCstruct):
        if self.record.issue != None:
            xmlCstruct.Parent.ParentInfo.Issue.xml_append(unicode(self.record.issue))

    def cs_108_issuedetail(self, xmlCstruct):
        if self.record.issuedetail != None:
            xmlCstruct.Parent.ParentInfo.xml_append(self.xmlDoc.xml_create_element(u'NonStdCit',
                content=unicode(self.record.issuedetail)))
                
    """
    def cs_109_nopages(self, xmlCstruct):
        xmlCstruct.xml_append(self.xmlDoc.xml_create_element(u'Component'))
        xmlCstruct.xml_append(self.xmlDoc.xml_create_element(u'PageCount',
                content=unicode(self.record.nopages)))
    """        

    def cs_110_insert_Abstract_Component(self, xmlCstruct):
        if self.record.abstract != None:
            xmlCstruct.xml_append(self.component_template())
            
    def cs_111_insert_dirtyascii_Component(self, xmlCstruct):
        representation = self.xmlDoc.xml_create_element(u'Representation',
            attributes = {u'RepresentationType':u'BackgroundFullText'})
        mimetype = self.xmlDoc.xml_create_element(u'MimeType', content = u'text/xml')
        resides = self.xmlDoc.xml_create_element(u'Resides', content = u'FAST')
        representation.xml_append(mimetype)
        representation.xml_append(resides)
        component = self.xmlDoc.xml_create_element(u'Component',
            attributes={u'ComponentType': u'FullText'})
        component.xml_append(representation)
        
        xmlCstruct.xml_append(component)
    
    def cs_112_insert_PDF_Component(self, xmlCstruct):
        
        chimageids = self.xmlDoc.xml_create_element(u'CHImageIds')
        for image in self.record.ThreadSet:
            chimageids.xml_append(self.xmlDoc.xml_create_element(u'chid',
                content=unicode(image.imageid.replace('.tif', '.grayscale.jpg'))))
        
        representation = self.xmlDoc.xml_create_element(u'Representation',
            attributes = {u'RepresentationType':u'PDFFullText'})
        mimetype = self.xmlDoc.xml_create_element(u'MimeType', content = u'application/pdf')
        resides = self.xmlDoc.xml_create_element(u'Resides', content = u'CH/BP')
        color = self.xmlDoc.xml_create_element(u'Color', content = u'grayscale')
        option = self.xmlDoc.xml_create_element(u'Options', content = u'PageRange')
        scanned = self.xmlDoc.xml_create_element(u'Scanned', content = u'yes')
        representation.xml_append(mimetype)
        representation.xml_append(resides)
        representation.xml_append(color)
        representation.xml_append(option)
        representation.xml_append(scanned)
        
        component = self.xmlDoc.xml_create_element(u'Component',
            attributes={u'ComponentType': u'FullText'})
        component.xml_append(chimageids)
        component.xml_append(representation)
        
        xmlCstruct.xml_append(component)
        
    def cs_113_insert_pageimage_components(self, xmlCstruct):
    
        imagecounter = 0
        for image in self.record.ThreadSet:
            
            imagecounter += 1
            
            chid = self.xmlDoc.xml_create_element(u'chid', content=unicode(image.imageid.replace('.tif', '.grayscale.jpg')))
            chimageids = self.xmlDoc.xml_create_element(u'CHImageIds', content=chid)
            
            representation = self.xmlDoc.xml_create_element(u'Representation',
            attributes = {u'RepresentationType':u'Normal'})
            mimetype = self.xmlDoc.xml_create_element(u'MimeType', content = u'image/jpeg')
            resides = self.xmlDoc.xml_create_element(u'Resides', content = u'CH/BP')
            color = self.xmlDoc.xml_create_element(u'Color', content = u'grayscale')
            chimagehithighlighting = self.xmlDoc.xml_create_element(u'CHImageHitHighlighting', content = u'true')
            representation.xml_append(mimetype)
            representation.xml_append(resides)
            representation.xml_append(color)
            representation.xml_append(chimagehithighlighting)
            
            component = self.xmlDoc.xml_create_element(u'Component',
                attributes={u'ComponentType': u'Part'})
            component.xml_append(self.xmlDoc.xml_create_element(u'ObjectSeqNumber', content=unicode(imagecounter)))
            component.xml_append(chimageids)
            component.xml_append(representation)
            
            xmlCstruct.xml_append(component)
        
    
    def oi_101_type(self, xmlObject):
        objtype = self.record.type.replace('Cover', 'Covers')
        xmlObject.xml_insert_before(xmlObject.Title, self.xmlDoc.xml_create_element(u'SearchObjectType',
            attributes={u'SourceName': u'CH'},
            content=unicode(objtype)))
    
    
    def oi_102_title(self, xmlObject):
        
        if self.record.title == '':
            xmlObject.Title.cht.xml_append(u'[Untitled item]')
        else:
            xmlObject.Title.cht.xml_append(unicode(self.record.title))

    
    """
    def oi_103_date(self, xmlObject):
        xmlObject.xml_append(self.xmlDoc.xml_create_element(u'ObjectAlphaDate',
                content=unicode(self.record.date)))
    """

    def oi_104_nopages(self, xmlObject):
        xmlObject.xml_insert_after(xmlObject.Title, self.xmlDoc.xml_create_element(u'PageCount',
                content=unicode(self.record.nopages)))
                
    def oi_107_printLocation(self, xmlObject):
        xmlObject.PrintLocation.StartPage.xml_append(unicode(self.record.startpage_conv))
        xmlObject.PrintLocation.EndPage.xml_append(unicode(self.record.endpage_conv))
        xmlObject.PrintLocation.Pagination.xml_append(unicode('-'.join([self.record.startpage_conv, self.record.endpage_conv])))

    def oi_108_bpid(self, xmlObject):
        xmlObject.ObjectIds.xml_append(self.xmlDoc.xml_create_element(u'ObjectId',
           attributes={u'IdType': u'DOC_ID', u'IdSource': u'CH'},
           content=unicode(self.record.bpid)))
           
    """
    def oi_109_journalid(self, xmlObject):
        xmlObject.ObjectIds.xml_append(self.xmlDoc.xml_create_element(u'ObjectId',
           attributes={u'IdType': u'??', u'IdSource': u'DsolFIXME'},
           content=unicode(self.record.journalid)))
    """
    
    def oi_110_illustypes(self, xmlObject):
        illustypes = {}
        for ill in self.record.IllustrationSet:
            illustypes[ill.illusname] = 1
        for illustype in illustypes.keys():
            xmlObject.xml_insert_after(xmlObject.ObjectIds, self.xmlDoc.xml_create_element(u'DocFeature',
               content=unicode(illustype)))
               
    def oi_111_mainauthor(self, xmlObject):
        
        if self.record.author != None:
            authorwrapper = self.xmlDoc.xml_create_element(u'Contributor', attributes={u'RoleName': u'Author'})
        
            self.contribcounter += 1
            authorwrapper.xml_append(self.xmlDoc.xml_create_element(u'ContribData',
                attributes={u'MarkupIndicator': u'AuthorOrder'},
                content=unicode(self.contribcounter)))
                    
            authorwrapper.xml_append(self.xmlDoc.xml_create_element(u'ContribData',
                attributes={u'MarkupIndicator': u'OriginalForm'},
                content=unicode(self.record.author)))
                    
            xmlObject.Contributors.xml_append(authorwrapper)
        
    def oi_112_coauthors(self, xmlObject):
    # all the author stuff works in a similar way so maybe first five or so inserts could be folded together
    
        for coauth in self.record.CoauthorSet:
            coauthwrapper = self.xmlDoc.xml_create_element(u'Contributor', attributes={u'RoleName': u'Author'})
            self.contribcounter += 1
            coauthwrapper.xml_append(self.xmlDoc.xml_create_element(u'ContribData',
                attributes={u'MarkupIndicator': u'AuthorOrder'},
                content=unicode(self.contribcounter)))
            coauthwrapper.xml_append(self.xmlDoc.xml_create_element(u'ContribData',
                attributes={u'MarkupIndicator': u'OriginalForm'},
                content=unicode(coauth.coauthor)))
            xmlObject.Contributors.xml_append(coauthwrapper)
            
    def oi_113_wellesleynames(self, xmlObject):
     
        for well in self.record.ContributorSet:
            wellwrapper = self.xmlDoc.xml_create_element(u'Contributor', attributes={u'RoleName': u'WellesleyAttribution'})
            self.contribcounter += 1
            wellwrapper.xml_append(self.xmlDoc.xml_create_element(u'ContribData',
                attributes={u'MarkupIndicator': u'AuthorOrder'},
                content=unicode(self.contribcounter)))
            wellwrapper.xml_append(self.xmlDoc.xml_create_element(u'ContribData',
                attributes={u'MarkupIndicator': u'OriginalForm'},
                content=unicode(well.shortname)))
            wellwrapper.xml_append(self.xmlDoc.xml_create_element(u'ContribDesc'))
            wellwrapper.ContribDesc.xml_append(self.xmlDoc.xml_create_element(u'paragraph'))
            wellwrapper.ContribDesc.paragraph.xml_append(self.xmlDoc.xml_create_element(u'cht',
                content=unicode(' '.join([well.surname, well.details]))))
            xmlObject.Contributors.xml_append(wellwrapper)
    
    def oi_114_currannames(self, xmlObject):
    
        for curr in self.record.CurranSet:
            currwrapper = self.xmlDoc.xml_create_element(u'Contributor', attributes={u'RoleName': u'CurranAttribution'})
            self.contribcounter += 1
            currwrapper.xml_append(self.xmlDoc.xml_create_element(u'ContribData',
                attributes={u'MarkupIndicator': u'AuthorOrder'},
                content=unicode(self.contribcounter)))
            currwrapper.xml_append(self.xmlDoc.xml_create_element(u'ContribData',
                attributes={u'MarkupIndicator': u'OriginalForm'},
                content=unicode(curr.shortname)))
            currwrapper.xml_append(self.xmlDoc.xml_create_element(u'ContribDesc'))
            currwrapper.ContribDesc.xml_append(self.xmlDoc.xml_create_element(u'paragraph'))
            currwrapper.ContribDesc.paragraph.xml_append(self.xmlDoc.xml_create_element(u'cht',
                content=unicode(' '.join([curr.surname, curr.details]))))
            xmlObject.Contributors.xml_append(currwrapper)

    def oi_115_additionalattributions(self, xmlObject):
    
        if self.record.add_attribution_desc != '':
            for attr in self.record.add_attribution_desc.split('|'):
                attwrapper = self.xmlDoc.xml_create_element(u'Contributor', attributes={u'RoleName': u'PQAttribution'})
                self.contribcounter += 1
                attwrapper.xml_append(self.xmlDoc.xml_create_element(u'ContribData',
                    attributes={u'MarkupIndicator': u'AuthorOrder'},
                    content=unicode(self.contribcounter)))
                attwrapper.xml_append(self.xmlDoc.xml_create_element(u'ContribData',
                    attributes={u'MarkupIndicator': u'OriginalForm'},
                    content=unicode(attr)))
                xmlObject.Contributors.xml_append(attwrapper)

    def oi_116_ptjournaleditor(self, xmlObject):
        
        for ptjedrecord in self.record.PartJournalEditorSet:
            for ptjed in ptjedrecord.editor.split('|'):
                ptjedwrapper = self.xmlDoc.xml_create_element(u'Contributor', attributes={u'RoleName': u'Editor'})
                self.contribcounter += 1
                ptjedwrapper.xml_append(self.xmlDoc.xml_create_element(u'ContribData',
                    attributes={u'MarkupIndicator': u'AuthorOrder'},
                    content=unicode(self.contribcounter)))
                ptjedwrapper.xml_append(self.xmlDoc.xml_create_element(u'ContribData',
                    attributes={u'MarkupIndicator': u'OriginalForm'},
                    content=unicode(ptjed)))
                xmlObject.Contributors.xml_append(ptjedwrapper)
    
    def oi_117_publisher(self, xmlObject):
    
        if self.journalmap.has_key(self.record.journalid):
            self.contribcounter += 1
            if self.journalmap[self.record.journalid].has_key('publisher'):
                xmlObject.Contributors.xml_append(self.contributor_template('Publisher', 
		    {'AuthorOrder': unicode(self.contribcounter),
		    'Publisher' : unicode(self.journalmap[self.record.journalid]['publisher']),
		    'PlaceName' : unicode(self.record.PartJournalTitleSet[0].placepub)}))
            else:
                xmlObject.Contributors.xml_append(self.contributor_template('Publisher',
                    {'AuthorOrder': unicode(self.contribcounter),
                    'PlaceName' : unicode(self.record.PartJournalTitleSet[0].placepub)}))
    
    def oi_118_subjects(self, xmlObject):
    
        if self.journalmap.has_key(self.record.journalid):
            if self.journalmap[self.record.journalid].has_key('subjects'):
                xmlObject.xml_insert_after(xmlObject.Contributors, self.xmlDoc.xml_create_element(u'Terms'))
                for subj in self.journalmap[self.record.journalid]['subjects']:
                    term = self.xmlDoc.xml_create_element(u'Term',
                        attributes={u'TermType': u'DerivedSubject'})
                    term.xml_append(self.xmlDoc.xml_create_element(u'TermElem',
                        attributes={u'ElemType':u'Term'},
                        content=unicode(subj)))
                    xmlObject.Terms.xml_append(term)
    
    def oi_119_abstract(self, xmlObject):
        if self.record.abstract != None:
            #xmlObject.xml_append(self.xmlDoc.xml_create_element(u'Abstracts'))
            xmlObject.Abstracts.xml_append(self.xmlDoc.xml_create_element(u'Abstract',
               attributes={u'AbstType': u'excerpt'}))
            xmlObject.Abstracts.Abstract.xml_append(self.xmlDoc.xml_create_element(u'paragraph'))
            xmlObject.Abstracts.Abstract.paragraph.xml_append(self.xmlDoc.xml_create_element(u'cht',
               content=unicode(self.record.abstract)))
           
    
    def oi_120_dirtyascii(self, xmlObject):
    
        dirtystring = ''
        for zone in self.record.zones:
            for word in zone.words:
                #print word.text
                dirtystring += word.text + ' '
        xmlObject.xml_append(self.xmlDoc.xml_create_element(u'TextInfo'))
        xmlObject.TextInfo.xml_append(self.xmlDoc.xml_create_element(u'text'))
        xmlObject.TextInfo.text.xml_append(self.xmlDoc.xml_create_element(u'dirtyascii',
            content=unicode(dirtystring[:-1])))
    
    
    def oi_121_attributionnotes(self, xmlObject):
    
        if self.record.add_attribution_notes != '':
            xmlObject.xml_append(self.xmlDoc.xml_create_element(u'Notes'))
            xmlObject.Notes.xml_append(self.xmlDoc.xml_create_element(u'Note',
                attributes={u'NoteType': u'PQAttribution'},
                content=unicode(self.record.add_attribution_notes)))
                
    def oi_122_languageinfo(self, xmlObject):
    
        xmlObject.Language.RawLang.xml_append(u'eng')
        xmlObject.Language.ISO.ISOCode.xml_append(u'ENG')
        
    def oi_123_copyright(self, xmlObject):
    
        xmlObject.Copyright.CopyrightData.cht.xml_append(u'Copyright ProQuest LLC')
        
    def oi_124_legacyproductmapping(self, xmlObject):
    
        xmlObject.LegacyProductMapping.GroupName.xml_append(u'British Periodicals')
                            
    """
    def at_101_threadinginfo(self, xmlAttach):
    
        for image in self.record.ThreadSet:
            imagewrapper = self.xmlDoc.xml_create_element(u'Attachment')
            imagewrapper.xml_append(self.xmlDoc.xml_create_element(u'AttachName',
                content=unicode(image.imageid)))
            xmlAttach.xml_append(imagewrapper)
    """

    def ld_001_ch(self, xmlLegacy):
    
        xmlLegacy.xml_append(self.xmlDoc.xml_create_element(u'CH'))
    
    def ld_101_noillustrations(self, xmlLegacy):
    
        if len(self.record.IllustrationSet) > 0:
            xmlLegacy.CH.xml_append(self.xmlDoc.xml_create_element(u'DocMarkup',
                attributes={u'DocMrkInd': u'DocFeatures'},
                content=unicode(self.record.IllustrationSet.noillustrations)))
        
    def ld_102_freqpub(self, xmlLegacy):
    
        if len(self.record.PartJournalTitleSet) > 0:
            xmlLegacy.CH.xml_append(self.xmlDoc.xml_create_element(u'DocMarkup',
                attributes={u'DocMrkInd': u'Frequency'},
                content=unicode(self.record.PartJournalTitleSet[0].freqpub)))
    
    """
    def ld_103_sftwithcoords(self, xmlLegacy):

        for zone in self.record.zones:
            template = ZoneTemplate()
            template.zone = zone
            template.journalid = self.record.journalid
            
            xmlLegacy.CH.xml_append(unicode(template.respond()))
            
            #apszone = str(template.respond())
            #xmlLegacy.CH.xml_append_fragment(apszone)
    """            



