#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib'))
sys.path.append('/packages/dsol/lib/python')

from EntityShield import *
from mappings.abstractmapping import AbstractMapping
from commonUtils import dateUtils, textUtils

from mixin import mixin
#from mixinmodules.fulltext import FullTextMixin as fulltext
from mixinmodules.misc import MiscMixin as misc
import mad

class IMPARefMapping(AbstractMapping):
    def __init__(self, rawrecord):
        super(IMPARefMapping, self).__init__(rawrecord)
        mixin(self, misc)
        self._dtable = {
            'body':    IMPARefMapping.body,     #noop,
#            'BODY':    IMPARefMapping.body1,
            'group':   IMPARefMapping.noop,     # Doesn't appear to be needed
            'id':      IMPARefMapping.noop,     # handled as a computed value in ObjectIDs
            'links':   IMPARefMapping.links,    #IMPARefMapping.noop,
            'mp3':     IMPARefMapping.mp3,      # Only occurs in pronunciation guide
            'name':    IMPARefMapping.title,    # In pronunciation guide instead of title.
            'nat':     IMPARefMapping.noop,     # Only occurs in pronunciation guide and handled in _terms
            'refwork': 'What are we doing with this? Will it interfere with data out of TRACS?',
            'subtype': IMPARefMapping.subtype,  # handled in _terms
            'title':   IMPARefMapping.title,    # This occurs in all but the pronunciation guide, where we find name instead
            'type':    IMPARefMapping.types,    # handled in _terms
            'url':     IMPARefMapping.linkData,
            }

        elements = '''refwork type id title body subtype nat name mp3 links url group '''.split()
        for element in elements:
            self._fields.append(str(element))

        for field in self.fields:
            try:
                setattr(self.record, field, unicode(getattr(rawrecord, field)))
            except AttributeError:
                pass

        self.productId = u'IIMPREF'

        self._computedValues = [
            '_legacyID',
            '_objectTypes',
            '_objectIDs',
            '_terms',
            '_lastUpdateTime',
            '_alphaPubDate',
            '_numericDate',
            '_components',
            ]


    def after_hooks(self):
        self.visualFeedBack(self)
#        print >> sys.stderr, (self.gs4)
#        exit(1)

    # Computed values.
    def _components(self):
        self.gs4.components = []
        values = {u'MimeType': u'text/xml', u'Resides': u'FAST'}
        self.gs4.components.append(self._buildComponent(u'Citation',
                                                           {u'Representation': {u'RepresentationType': u'Citation',
                                                                                'values': values}}))
        if self.gs4.pubTitle in ['Glossary', 'Opera Synopses', 'Music Fundamental Terms']:
            self.gs4.components.append(self._buildComponent(u'FullText',
                                                            {u'Representation': {u'RepresentationType': u'FullText',
                                                                                 'values': values}}))

        if self.record.mp3:
            mp3path = os.path.join('/products/impa/release/webroot/sounds', self.record.mp3)
            mediapath = os.path.join('/media/ch/iimpa/sounds', self.record.mp3)
            self.gs4.components.append(self._buildComponent(u'Audio',
                                                            {u'Representation': {u'RepresentationType': u'Embed',
                                                                                 'values': {u'MimeType': u'application/mp3',
                                                                                            u'Resides': u'CH/IIMPA',
                                                                                            u'Seconds': str(mad.MadFile(mp3path).total_time()/1000),
                                                                                            u'Bytes': str(os.path.getsize(mp3path)),
                                                                                            u'MediaKey': unicode(mediapath)
                                                                                            }}}))

    def _alphaPubDate(self):
        self.gs4.alphaPubDate = dateUtils.today_pqan()

    def _numericDate(self):
        self.gs4.numericDate = dateUtils.pq_numeric_date(self.gs4.alphaPubDate)

    def _objectTypes(self):
        self.gs4.searchObjectType = [u'Reference Work']
        self.gs4.objectSourceType = [u'Encyclopedias and Reference Works']
        if self.record.type == 'Pronunciation Guide':
            self.gs4.searchObjectType.append(u'Audio Clip')
            self.gs4.objectSourceType.append(u'Audio and Video Works')
        

    def _objectIDs(self):
        self.gs4.objectIDs = []
        self.gs4.objectIDs.append({'value': self.gs4.originalCHLegacyID,
                                   u'IDOrigin': u'CH',
                                   u'IDType': u'CHOriginalLegacyID'})

    def _legacyID(self):
        self.gs4.legacyID = self._prefixedLegacyId(textUtils.cleanAndEncode(self.record.id))
        self.gs4.originalCHLegacyID = unicode(self.record.id)
        
    def _terms(self):
        self.gs4.terms = []
        self.gs4.terms.append({u'TermType': u'GenSubjTerm',
                               #u'attrs': {u'FlexTermName': u'ArtsHumanities'},
                               u'values': {u'GenSubjValue': self.record.type}})
        if not self.record.nat == '':
            self.gs4.terms.append({u'TermType': u'FlexTerm',
                                   u'attrs': {u'FlexTermName': u'Nationality'},
                                   u'values': {u'FlexTermValue': self.record.nat}})
        if not self.record.subtype == '':
            self.gs4.terms.append({u'TermType': u'FlexTerm',
                                   u'attrs': {u'FlexTermName': u'NaxosSubType'},
                                   u'values': {u'FlexTermValue': self.record.subtype}})
            # Compound subtype: name/subtype: title
            if self.record.type == "Pronunciation Guide":
                extra = self.record.name
                kind = u'NaxosComposer'
            else:
                extra = self.record.title
                kind = u'NaxosSubType'
            self.gs4.terms.append({u'TermType': u'FlexTerm',
                                   u'attrs': {u'FlexTermName': kind},
                                   u'values': {u'FlexTermValue': ': '.join([self.record.subtype, extra])}})

    def _lastUpdateTime(self):
        self.gs4.lastUpdateTime = dateUtils.fourteenDigitDate()

    # title NOT inherited from AbstractMapping, since we have two fields here that could be the title
    # `name' occurs only in the pronunciation guide, and `title' elsewhere.
    def title(self, data):
        if self.record.type == "Pronunciation Guide":
            title = self.record.name
        else:
            title = self.record.title
        self.gs4.title = textUtils.cleanAndEncode(title)

    def types(self, data):
        self.gs4.pubTitle = textUtils.cleanAndEncode(data)
        if self.gs4.pubTitle == 'Music Fundamental Terms':
            self.gs4.legacyPubID = u'IIMP_001_FUND'
        elif self.gs4.pubTitle == 'Glossary':
            self.gs4.legacyPubID = u'IIMP_002_GLOSS'
        elif self.gs4.pubTitle == 'Pronunciation Guide':
            self.gs4.pubTitle = u'Pronunciation Guides'
            self.gs4.legacyPubID = u'IIMP_003_PRON'
        elif self.gs4.pubTitle == 'Opera':
            self.gs4.pubTitle = u'Opera Synopses'        
            self.gs4.legacyPubID = u'IIMP_004_OPERA'
        elif self.gs4.pubTitle == 'Naxos Link':
            self.gs4.pubTitle = u'Naxos Links'
            self.gs4.legacyPubID = u'IIMP_005_LINKS'
        self.gs4.journalID = self.gs4.legacyPubID

    def subtype(self, data):
        if self.record.subtype == "Composer":
            self.record.subtype = "Composers"

    def body(self, data):
        self.gs4.fullTextData = self.record.body

    def refwork(self, data):
        self.gs4.companyname = u'Naxos Music Library'

    def links(self, data):
        self.gs4.xRefLinks = []
        for link in data.split('\n'):
            if link == '':
                continue
            self.gs4.xRefLinks.append(['-'.join([self.productId, link[0:11]]), link[11:]])
#        print >> sys.stderr, (self.gs4.xRefLinks)
        

    def linkData(self, data):
        self.gs4.linkData = []
        if self.record.url:
            self.gs4.linkData.append({u'linkType': u'OtherLink',
                                      'attrs': {u'LinkType': 'DocUrl'},
                                      u'linkValue': textUtils.cleanAndEncode(self.record.url)})


    def mp3(self, data):
        pass
#        mp3path = os.path.join('/products/impa/release/webroot/sounds', data)
#        mediapath = os.path.join('/media/ch/iimpa/sounds', data)
#        self.gs4.components = []
#        self.gs4.components.append(self._buildComponent(u'Audio',
#                                                        {u'Representation': {u'RepresentationType': u'Embed',
#                                                                             'values': {u'MimeType': u'application/mp3',
#                                                                                        u'Resides': u'CH/IIMPA',
#                                                                                        u'Seconds': str(mad.MadFile(mp3path).total_time()/1000),
#                                                                                        u'Bytes': str(os.path.getsize(mp3path)),
#                                                                                        u'MediaKey': unicode(mediapath)
#                                                                                        }}}))
