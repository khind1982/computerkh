#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib'))
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../commonUtils'))
sys.path.append('/packages/dsol/lib/python')

"""
What you need to do to set up a new product's mapping process:

add it to cstore.config
put mapping in mappingregistry
put stream, if a new type, in streamregistry
create new mapping class
create new stream class if necessary
"""

from abstractmapping import *
from commonUtils import *
from time import gmtime
from bpentityconverter import *

class BPMapping(AbstractMapping):

    def __init__(self, bprecord):
        AbstractMapping.__init__(self, bprecord)
        self._fields = bprecord.requiredFields
        self._fields.extend(bprecord.optionalFields)
        self._record = bprecord
        self.record = bprecord
        self._dtable =  {
            'bpid': BPMapping.bpid,
            'sourcefilename': BPMapping.noop,
            'journalid': BPMapping.journalid,
            'pmid': BPMapping.noop,
            'author': BPMapping.noop,
            'title': BPMapping.title,
            'type': BPMapping.objtype,
            'volume': BPMapping.volume, 
            'issue': BPMapping.issue,
            'date': BPMapping.noop,
            'month': BPMapping.noop,
            'nopages': BPMapping.noop,
            'startpage': BPMapping.noop,
            'endpage': BPMapping.noop,
            'todaydate': BPMapping.noop,
            'categoryid': BPMapping.noop,        # value put in by fiction categoriser tool, used by bprecord
            'numericpage': BPMapping.noop,       # this and next two used internally by bprecord
            'numericendpage': BPMapping.noop,
            'pagetype': BPMapping.noop,
            'enumeration': BPMapping.noop,       # the vol + iss string; not used
            'numericvolume': BPMapping.noop,
            'numericissue': BPMapping.noop,
            'page_sequence_start': BPMapping.noop,
            'page_sequence_end': BPMapping.noop,
            'startpage_conv': BPMapping.startpage,
            'endpage_conv': BPMapping.endpage,
            'add_attribution_desc': BPMapping.noop,
            'add_attribution_shortname': BPMapping.noop,
            'add_attribution_notes': BPMapping.add_attribution_notes,
            'issuedetail': BPMapping.noop,
            'PartJournalTitleSet': BPMapping.journaltitle,
            'PartJournalEditorSet': BPMapping.noop,
            'abstract': BPMapping.abstract,
            'WellesleySet': BPMapping.noop,
            'CoauthorSet': BPMapping.noop,
            'IllustrationSet': BPMapping.illustrationtypes,
            'ContributorSet': BPMapping.noop,
            'CurranSet': BPMapping.noop,
            'ThreadSet': BPMapping.noop,
            'zones': BPMapping.noop,
            'wordcount': BPMapping.noop,
            'illustrated': BPMapping.noop,
            'blocked': BPMapping.noop,            # do we need to check this?
            'excluded': BPMapping.noop,           # we don't extract excluded records
            'hlcindexing': BPMapping.noop
            }
        self.dayfrequencies = {
                            'Weekly': '',
                            'Daily': '',
                            'Bi-monthly': '',
                            'Bi-weekly': '',
                            'Semi-weekly': '',
                            'Tri-weekly': '',
                            'Semi-monthly': ''
                            }
        self._computedValues = [
                                '_pagination',
                                '_authors',
                                '_dirtyAscii',
                                '_language',
                                '_setDates',
                                '_illustrationData',
                                '_publicationFrequency',
                                '_publisher',
                                '_issn',
                                '_publicationPlace',
                                '_subjects',                                      
                                '_components',
                                '_pagecount',
                                '_cover',
                                '_bundleData',
                                '_ssid',
                                '_wellesleyID',
                                '_hlcindexing'
                                ]
        self._componentTypes['CHImageIDs'] = BPMapping._buildCHImagIDs
        self._componentTypes['ImageOrder'] = BPMapping._buildImageOrder
        
        self.entityConverter = bpEntityConverter()
        
        self.gs4.productid = 'British Periodicals'
        
        self._cfg['basename'] = self.record.journalid

        # As we need to differentiate between full text and non-full text, we'll redefine the
        # SteadyStateHandler here.
        if 'wellesley' in self.cfg['mappingOptions']:
            self.ssTableName = 'bpwellesley'
        else:
            self.ssTableName = 'bp'

        self._after_hooks = [
            BPMapping._set_steady_state_token,
            BPMapping._lastUpdateTime
            ]

    def _set_steady_state_token(self):
        self.setSteadyStateToken(self.gs4.__dict__)


    """
    def after_hooks(self):

        [
        self._lastUpdateTime()
    """
    
    def do_mapping(self):
    
        print self.record
        print self._record
        #print self._fields
        for field in self._fields:

            if hasattr(self.record, field):
                data = getattr(self.record, field)
                self._dtable[field](self, data)
        self.computedValues()
        self._increment_seen()
    
    def bpid(self, data):
        legacyid = 'bp' + data
        if 'wellesley' in self.cfg['mappingOptions']:
            self.gs4.relatedLegacyID = legacyid
            self.gs4.relatedLegacyPlatform = 'CH'
            legacyid += '-1'
        self.gs4.legacyID = unicode(legacyid)
        self.gs4.objectIDs = []
        self.gs4.objectIDs.append({'value': unicode(legacyid),
                                   u'IDOrigin': u'CH',
                                   u'IDType': u'CHLegacyID'})
        self.gs4.originalCHLegacyID = unicode(data)
        self.gs4.objectIDs.append({'value': unicode(data),
                                   u'IDOrigin': u'CH',
                                   u'IDType': u'CHOriginalLegacyID'})
        
    def journalid(self, data):
        self.gs4.journalID = data
        
    def journaltitle(self, data):
        # 'data' here is a PartJournalTitleSet from bprecord.py
        # PartJournalTitleSet is populated by getting part journals within whose date range the
        # current record's date falls - so there should only be one per record
        if len(data) > 1:
            sys.exit("too many part journals! " + self.record.bpid)
        else:
            print "data:", data
            pubtitle = unicode(data[0].journaltitle)
            self.gs4.pubTitle = textUtils.cleanAndEncode(pubtitle)
        
    def issuedetail(self, data):
        self.gs4.nonStandardCitation = textUtils.cleanAndEncode(data)
        
    def objtype(self, data):
        # If field contains 'Cover' needs to be standardised to 'Covers'
        self.gs4.searchObjectType = [unicode(data.replace('Cover', 'Covers'))]
        
    def title(self, data):
        if data == '':
            self.gs4.title = u'[Untitled item]'
        else:
            self.gs4.title = unicode(self.entityConverter.convert(data))
    
    #Page count is now to be handled by a computedValue as we're using length
    # of record.ThreadSet, not record.nopages.
    #def pagecount(self, data):
    #    self.gs4.pageCount = unicode(data)
        
    def startpage(self, data):
        self.gs4.startpage = unicode(data)
        
    def endpage(self, data):
        self.gs4.endpage = unicode(data)
        
    def illustrationtypes(self, data):
        # if other things use docfeatures move this to computedvalues
        # 'data' here is an IllustrationSet from bprecord.py
        illustypes = {}
        self.gs4.docFeatures = []
        for ill in data:
            illustypes[ill.illusname] = 1
        for illustype in illustypes.keys():
            self.gs4.docFeatures.append(unicode(illustype))

    def abstract(self, data):
        if data != None:
            self.gs4.abstract = {'abstractText': unicode(self.entityConverter.convert(data)),
                             'abstractType': u'Excerpt'}

    def add_attribution_notes(self, data):
        if data != '':
            self.gs4.notesData = {'NoteText': unicode(data),
                              'NoteType': u'PQAttribution'}
                              
    def volume(self, data):
        if data:
            self.gs4.volume = textUtils.cleanAndEncode(data)
                              
    def issue(self, data):
        if data:
            self.gs4.issue = textUtils.cleanAndEncode(data)
            
                              
    #def threading(self, data):
    #    # data is a ThreadSet
    #    self.gs4.imageSet = [image.imageid.replace('.tif', '.grayscale.jpg') for image in data]
        
    def _pagination(self):
        self.gs4.pagination = unicode('-'.join([self.record.startpage_conv, self.record.endpage_conv]))

    def _authors(self):
        authorcount = 0
        self.gs4.contributors = []

        if self.record.author != None:
            authorcount +=1
            self.gs4.contributors.append({u'ContributorRole': 'Author',
                                          u'ContribOrder': unicode(authorcount),
                                          u'contribvalue': textUtils.cleanAndEncode(self.entityConverter.convert(self.record.author))})
                                          
        for coauth in self.record.CoauthorSet:
            authorcount +=1
            self.gs4.contributors.append({u'ContributorRole': 'CoAuth',
                                          u'ContribOrder': unicode(authorcount),
                                          u'contribvalue': textUtils.cleanAndEncode(self.entityConverter.convert(coauth.coauthor))})
        if 'wellesley' in self.cfg['mappingOptions']:
            for well in self.record.ContributorSet:
                authorcount +=1
                self.gs4.contributors.append({u'ContributorRole': 'WellesleyAttribution',
                                              u'ContribOrder': unicode(authorcount),
                                              u'contribvalue': textUtils.cleanAndEncode(self.entityConverter.convert(well.shortname)),
                                              u'ContribDesc': entityToItalicsTag(textUtils.cleanAndEncode(self.entityConverter.convert(' '.join([well.surname, well.details]))))})
            for curr in self.record.CurranSet:
                authorcount +=1
                self.gs4.contributors.append({u'ContributorRole': 'CurranAttribution',
                                              u'ContribOrder': unicode(authorcount),
                                              u'contribvalue': textUtils.cleanAndEncode(self.entityConverter.convert(curr.shortname)),
                                              u'ContribDesc': entityToItalicsTag(textUtils.cleanAndEncode(self.entityConverter.convert(' '.join([curr.surname, curr.details]))))})
        if self.record.add_attribution_desc != '':
            for attr in self.record.add_attribution_desc.split('|'):
                authorcount +=1
                self.gs4.contributors.append({u'ContributorRole': 'PQAttribution',
                                              u'ContribOrder': unicode(authorcount),
                                              u'contribvalue': textUtils.cleanAndEncode(self.entityConverter.convert(attr))})
        for ptjedrecord in self.record.PartJournalEditorSet:
            for ptjed in ptjedrecord.editor.split('|'):
                authorcount +=1
                self.gs4.contributors.append({u'ContributorRole': 'Editor',
                                              u'ContribOrder': unicode(authorcount),
                                              u'contribvalue': textUtils.cleanAndEncode(self.entityConverter.convert(ptjed))})
    
    def _dirtyAscii(self):
        self.gs4.textInfo = {}
        dirtystring = ''
        for zone in self.record.zones:
            for word in zone.words:
                #print word.text
                dirtystring += word.text + ' '
        dirtystring = dirtystring.replace(']]&gt;', '')
        self.gs4.textInfo['dirtyAscii'] = unicode(dirtystring[:-1])

    def _language(self):
        # call this english; real languages only exist in raw BP xml at present and may be untrustworthy
        self.language('English')
                
    def _setDates(self):
        self.gs4.rawPubDate = ' '.join([self.record.month, str(self.record.date)[0:4]])
        if len(self.record.PartJournalTitleSet) > 0:
            if self.dayfrequencies.has_key(self.record.PartJournalTitleSet[0].freqpub):
                self.gs4.rawPubDate = ' '.join([str(self.record.date)[6:].lstrip('0'), self.gs4.rawPubDate])
        else:
            sys.exit("no partjournaltitle set for journal " + self.journalid)
        AbstractMapping._setDates(self)

    def _illustrationData(self):
        if len(self.record.IllustrationSet) > 0:
            self.gs4.legacyData = {}
            self.gs4.legacyData['illustrationData'] = unicode(self.record.IllustrationSet.noillustrations)

    def _publicationFrequency(self):
        if len(self.record.PartJournalTitleSet) > 0:
            if self.gs4.legacyData == None:
                self.gs4.legacyData = {}
            self.gs4.legacyData['publicationFrequency'] = unicode(self.record.PartJournalTitleSet[0].freqpub)

    def _publisher(self):
        if self.record._journaldetails.has_key('publisher'):
            self.gs4.publisher = unicode(self.record._journaldetails['publisher'])
        
    def _issn(self):
        if self.record._journaldetails.has_key('issn'):
            self.gs4.objectIDs.append({'value': unicode(self.record._journaldetails['issn']),
                                       u'IDType': u'ISSN'})
                
    def _publicationPlace(self):
        self.gs4.publicationCities = [unicode(city) for city in self.record.PartJournalTitleSet[0].placepub.split('|')]
        
    def _subjects(self):
        if self.record._journaldetails.has_key('subjects'):
            self.gs4.terms = []
            for subj in self.record._journaldetails['subjects']:
                self.gs4.terms.append({u'TermType': u'FlexTerm',
                                       u'attrs': {u'FlexTermName': u'DerivedSubject'},
                                       u'values': {u'FlexTermValue': textUtils.cleanAndEncode(subj)}})
                                                   
    def _pagecount(self):
	self.gs4.pageCount = unicode(len(self.record.ThreadSet))
    
    def _components(self):

        self.gs4.components = []

        # These parts never change.
        values = {u'MimeType': u'text/xml', u'Resides': u'FAST'}

        #Every record needs one of these:
        self.gs4.components.append(self._buildComponent(u'Citation', 
                                                        {u'Representation': {u'RepresentationType': u'Citation',
                                                         'values': values}}))
        if self.record.abstract != None:
            self.gs4.components.append(self._buildComponent(u'Abstract', 
                                                            {u'Representation': {u'RepresentationType': u'Abstract',
                                                             'values': values}}))

        self.gs4.components.append(self._buildComponent(u'FullText', 
                                                            {u'Representation': {u'RepresentationType': u'BackgroundFullText',
                                                             'values': values}}))
        
        pdfsize = 0
        for image in self.record.ThreadSet:
            pdfsize += image.imagesize
        
        self.gs4.components.append(self._buildComponent(u'FullText',
                                                            {u'CHImageIDs': {'values': {u'CHID': self.record.bpid}},
                                                            u'Representation': {u'RepresentationType': u'PDFFullText',
                                                            'values': {u'MimeType': u'application/pdf',
                                                                        u'Resides': u'CH/BP',
                                                                        u'Color': u'grayscale',
                                                                        u'Scanned': u'true',
                                                                        u'Options': u'PageRange',
                                                                        u'Bytes': unicode(pdfsize),
                                                                        u'CHImageHitHighlighting': u'true'
                                                                        }}}))
        
        imageidre = re.compile('..../(EBP_[0-9_]*)\.tif')
        #imageerrfile = open('/dc/scratch/bp/missing_images.log', 'a')
        
        pagesComponent = {u'CHImageIDs': {'values': {u'CHID': self.record.bpid}},
                            u'PageCount': unicode(len(self.record.ThreadSet)),
                            u'Representation': {u'RepresentationType': u'Normal',
                                                'values': {u'MimeType': u'image/jpeg',
                                                            u'Resides': u'CH/BP',
                                                            u'Color': u'grayscale'
                                                                        }}}
        if len(self.record.IllustrationSet) > 0:
            pagesComponent['Representation']['values'][u'IllustrationInfo'] = unicode(self.record.IllustrationSet.noillustrations)
        
        
        self.gs4.components.append(self._buildComponent(u'Pages', pagesComponent))

#                                                            {u'CHImageIDs': {'values': {u'CHID': self.record.bpid}},
#                                                            u'PageCount': unicode(len(self.record.ThreadSet)),
#                                                            u'Representation': {u'RepresentationType': u'Normal',
#                                                            'values': {u'MimeType': u'image/jpeg',
#                                                                        u'Resides': u'CH/BP',
#                                                                        u'Color': u'grayscale'
#                                                                        }}}))
        
#        for image in range(0, len(self.record.ThreadSet)):
#            imageorder = unicode(image + 1)
#            
#            imageid = imageidre.search(self.record.ThreadSet[image].imageid).group(1)
#            
#                            
#            self.gs4.components.append(self._buildComponent(u'Part',
#                                                            {u'ImageOrder': {'values': {u'Name': imageorder,
#                                                                                        u'Order': imageorder,
#                                                                                        u'OrderCategory': 'PART'}},
#                                                            u'CHImageIDs': {'values': {u'CHID': self.record.bpid}},
#                                                            u'Representation': {u'RepresentationType': u'Normal',
#                                                            'values': {u'MimeType': u'image/jpeg',
#                                                                        u'Resides': u'CH/BP',
#                                                                        u'Color': u'grayscale',
#                                                                        u'Bytes': unicode(imageid),
#                                                                        u'CHImageHitHighlighting': u'true'
#                                                                        }}}))
    
    def _lastUpdateTime(self):
        self.gs4.lastUpdateTime = dateUtils.fourteenDigitDate()

    def _buildCHImagIDs(self, comp):
        return comp
        
    def _buildImageOrder(self, comp):
        return comp
        
    def _cover(self):
        if self.record.type == 'Cover':
            self.gs4.cover = 'true'
        else:
            self.gs4.cover = 'false'
            
    def _bundleData(self):
        bundlevalue = 'BP'
        if 'wellesley' in self.cfg['mappingOptions']:
            bundlevalue += 'WELL'
        bundlevalue += 'C' + self.record._journaldetails['collection']
        self.objectBundleData(bundlevalue)
        
    def _ssid(self):
        self.ssid = self.gs4.legacyID

    def _wellesleyID(self):
        if hasattr(self.record, 'WellesleySet'):
            for well in self.record.WellesleySet:
                self.gs4.objectIDs.append({'value': unicode(well.wellesleyid),
                                        u'IDOrigin': u'CH',
                                        u'IDType': u'WellesleyID'})

    def _hlcindexing(self):
        if self.gs4.terms == None:
            self.gs4.terms = []
        if hasattr(self.record, 'hlcindexing'):
            for indexingitem in self.record.hlcindexing:
                if indexingitem['subjauthor'] != '':
                    self.gs4.terms.append({u'TermType': u'FlexTerm',
                                           u'attrs': {u'FlexTermName': u'SubjAuth'},
                                           u'values': {u'FlexTermValue': textUtils.cleanAndEncode(indexingitem['subjauthor'])}})
                if indexingitem['subjwork'] != '':
                    self.gs4.terms.append({u'TermType': u'FlexTerm',
                                           u'attrs': {u'FlexTermName': u'SubjWork'},
                                           u'values': {u'FlexTermValue': textUtils.cleanAndEncode(indexingitem['subjwork'])}})

