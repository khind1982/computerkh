# -*- mode: python -*-

import sys, os, re
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib'))
sys.path.append('/packages/dsol/lib/python')

from mappings.abstractmapping import AbstractMapping
from commonUtils import dateUtils, langUtils

# Include mixin functions for handling full text.
from mixin import mixin
from mixinmodules.fulltext import FullTextMixin as fulltext
from mixinmodules.misc import MiscMixin as misc

#import hashlib

class PRISMAMapping(AbstractMapping): # pylint: disable = R0902, R0904
    def __init__(self, rawrecord):
        for mod in (misc, fulltext):
            mixin(self, mod)
        super(PRISMAMapping, self).__init__(rawrecord)
        self._defaultDelimiter = '\t'

        if self._cfg['prismaType'] in ['hapi', 'pqhapi']:
            self.useHapi = True
        else:
            self.useHapi = False

        self._dtable = {
            'abstract':       PRISMAMapping.abstract,
            'aid':            PRISMAMapping.noop,
            'allissues':      PRISMAMapping.noop,
            'article_title':  PRISMAMapping.noop,  # title,
            'author':         PRISMAMapping.noop,  #author, _computedValues
            'authors':        PRISMAMapping.noop,  #authors, _computedValues
            'bkr':            PRISMAMapping.searchObjectType,
            'copyright':      PRISMAMapping.copyright,
            'country':        PRISMAMapping.noop,
            'descriptors':    PRISMAMapping.noop,
            'displaypage':    PRISMAMapping.noop,
            'doctype':        PRISMAMapping.noop,
            'ft':             PRISMAMapping.noop,
            'ftsource':       PRISMAMapping.noop,
            'haid':           PRISMAMapping.noop,
            'hapiid':         PRISMAMapping.setLegacyDocumentID,  #noop,
            'harticle_title': PRISMAMapping.noop,  # title,
            'hlanguage':      PRISMAMapping.noop,  #language, _computedValues
            'hpage':          PRISMAMapping.noop,  #startpage, _computedvalue
            'hpagecount':     PRISMAMapping.noop,  #pagination, _computedvalue
            'hsp':            PRISMAMapping.ethnicity,
            'iid':            PRISMAMapping.noop,
            'issn':           PRISMAMapping.issn,
            'isu':            PRISMAMapping.issue,
            'jid':            PRISMAMapping.journalID,
            'jtitle':         PRISMAMapping.noop,
            'language':       PRISMAMapping.noop,  #language, _computedValues
            'newdata':        PRISMAMapping.newdata,
            'notes':          PRISMAMapping.documentFeatures,
            'other_authors':  PRISMAMapping.otherAuthors,
            'page':           PRISMAMapping.noop,  #startpage, _computedvalue
            'pagecount':      PRISMAMapping.noop,  #pagination, _computedvalue
            'pageimage':      PRISMAMapping.noop,
            'peer':           PRISMAMapping.peerReviewed,
            'pqid':           PRISMAMapping.setLegacyDocumentID,  #pqid,
            'pqjid':          PRISMAMapping.noop,
            'pq_publication': PRISMAMapping.noop,
            'publication':    PRISMAMapping.noop,
            'publisher':      PRISMAMapping.noop,
            'ref':            PRISMAMapping.noop,   #reference,
            'sdt':            PRISMAMapping.sdt,
            'subjects':       PRISMAMapping.noop,
            'udt':            PRISMAMapping.rawPubDate,
            'updated':        PRISMAMapping.noop,
            'vol':            PRISMAMapping.volume,
            }


        self.record = rawrecord
        self.record._fields = rawrecord.keys  #pylint:disable=W0212
        self._computedValues = [
            PRISMAMapping._title,
            PRISMAMapping._authors,
            PRISMAMapping._language,
            PRISMAMapping._startpage,
            PRISMAMapping._pagination,
            PRISMAMapping._relatedLegacyID,
            PRISMAMapping._getPublicationTitle,
            PRISMAMapping._setDates,
            PRISMAMapping._objectIDs,
            PRISMAMapping._terms,
            PRISMAMapping._objectBundleData,
            PRISMAMapping._components,
            PRISMAMapping._lastUpdateTime
            ]

        self._after_hooks = [
            PRISMAMapping._fullText,
            PRISMAMapping._make_copy_for_steady_state,
            ]

        self.productId = self._cfg['product']
        self.gs4.productId = self.productId

        # Call this here so that self.gs4.originalCHLegacyID is set
        # early enough that we can use it to set
        # self.gs4.originalCHLegacyID, which is in turn used by the
        # visualFeedBack and in the fulltext mixin logging messages.
        self._getLegacyID()

        self._cfg['basename'] = self.gs4.originalCHLegacyID

        # Concatenate self.record._cfg['prismaType'] and one of
        # self.record.pqid or self.record.hapiid to ensure unique
        # ssids across the different product variants.
        #ssid_prefix = self.record._cfg['prismaType']
        ssid_prefix = self._cfg['prismaType']
        if not self.record.pqid == '':
            ssid = self.record.pqid
        else:
            ssid = self.record.hapiid
        self.ssid = "%s-%s" % (ssid_prefix, ssid,)

        self.record.journalid = self.record.jid

    def _fullText(self):
        if not self.record.pqid == '':
            self.insertFullText(self.record.pqid)

    def _make_copy_for_steady_state(self):
        if self.doSteadyState == True:
            self.setSteadyStateToken(self.record.updated)
            ## steady_state_data = copy.deepcopy(self.gs44.__dict__)
            ## del(steady_state_data['lastUpdateTime'])
            ## self.setSteadyStateToken(steady_state_data)


    # Set the doc id early so we can use it in do_mapping to check if
    # the record in question is in a list of ids that may be passed in
    # as a command line argument. Given how quickly PRISMA runs
    # though, it is questionable whether anyone would want to do
    # that...
    def setLegacyDocumentID(self, data):
        # If it's already set, leave it alone!
        if hasattr(self, 'legacyDocumentID'):
            pass
        elif self.useHapi:
            self.legacyDocumentID = self.record.hapiid
        else:
            self.legacyDocumentID = self.record.pqid

    def issue(self, data):
        if not data == '0':
            super(PRISMAMapping, self).issue(data)

    def volume(self, data):
        if not data == '0':
            super(PRISMAMapping, self).volume(data)

    def abstract(self, data):
        if data and not data.strip() == '':
            if re.search('MABS', data):
                abstType = u'Medium'
            elif re.search('SABS', data):
                abstType = u'Short'
            else:
                print >> sys.stderr, ("DEBUG: %s (%s)" % (data, type(data),))
            cleanedAbstract = self.cleanPrismaAbstractMarkup(data)
            if not cleanedAbstract.strip() == '':
                self.gs4.abstract = self._abstract(
                    self.cleanPrismaAbstractMarkup(data), abstType
                )

    def _startpage(self):
        if self.useHapi:
            data = self.record.hpage
        else:
            data = self.record.page
        super(PRISMAMapping, self).startpage(data)

    def _pagination(self):
        if self.useHapi:
            data = self.record.hpagecount
        else:
            data = self.record.pagecount
        super(PRISMAMapping, self).pagination(data)
        super(PRISMAMapping, self).endpage(data)

    def otherAuthors(self, data):
        if data == 'Y':
            self.gs4.otherAuthors = 'true'

    def newdata(self, _): # data):
        if self.newdata == 'N':
            self.gs4.action = u'change'
        elif self.newdata == 'Y':
            self.gs4.action = u'add'

#    def lastUpdateTime(self, data):
#        cleanedDate = unicode(re.sub('[^0-9]', '', data))
#        try:
#            if int(cleanedDate) is 0:
#                cleanedDate = dateUtils.fourteenDigitDate()
#        except ValueError:
#            cleanedDate = dateUtils.fourteenDigitDate()
#        self.gs4.lastUpdateTime = unicode(cleanedDate)

    def sdt(self, data):
        self.gs4.startDate = self.cleanAndEncode(data)

#     def descriptors(self, data):
#         self.gs4.flexTerms = []
#         for descriptor in data.split('\t'):
#             print >> sys.stderr, ("DEBUG: %s" % descriptor)

#             if descriptor.strip() == '':
#                 continue
#             if re.match(r'^AT', descriptor):
#                 print >> sys.stderr, (descriptor)

#             self.gs4.flexTerms.append({u'FlexTermValue': textUtils.cleanAndEncode(descriptor),
#                                        u'FlexTermName': u'HAPIDescriptor'})

    def ethnicity(self, data):
        if data == 'Y':
            self.gs4.ethnicity = u'US Hispanics'
        elif data == 'N' or data == '':
            self.gs4.ethnicity = u'Hispanics'

    def searchObjectType(self, data):
        self.gs4.searchObjectType = ([u'Book Review'] if not data == '' else
                                     [u'Article'])

    def copyright(self, data):
        self.gs4.copyrightData = self.cleanAndEncode(data)

    def rawPubDate(self, data):
        data = data.replace('Spet', 'Sept')
        super(PRISMAMapping, self).rawPubDate(data)

    #### computedValues
    #
    # These methods are called by AbstractMapping.computedValues. They must
    # be registered in self._computedValues to be included. Note that
    # methods registered in self.computedValues are run in the order they
    # are registered, so if output order is significant, be sure to
    # register your callbacks in the right order!

    def _title(self):
        if self.useHapi:
            super(PRISMAMapping, self).title(self.record.harticle_title)
        else:
            super(PRISMAMapping, self).title(self.record.article_title)


    def _authors(self):
        if self.useHapi:
            data = self.record.authors
        else:
            data = self.record.author
        #print self.record._data, data
        super(PRISMAMapping, self).authors(data)

    def _language(self):
        if self.useHapi:
            languageData = self.record.hlanguage
        else:
            languageData = self.record.language
        if languageData == '':
            languageData = u'Undetermined'
        languages = langUtils.languages(languageData)
        for index, lang in enumerate(languages):
            if re.match("French-based", lang):
                languages[index] = u"Creoles and Pidgins, French-based"
        self.gs4.languageData = langUtils.lang_iso_codes(languages)

    def _terms(self):
        self.gs4.terms = []
        if self.record.subjects:
            for subj in self.stringToList(self.record.subjects):
                if not subj == '':
                    subj = re.sub('<<', unichr(171), subj)
                    subj = re.sub('>>', unichr(187), subj)
                    self.gs4.terms.append({
                        u'TermType': u'GenSubjTerm',
                        u'attrs': {u'TermSource': u'HAPI'},
                        u'values': {
                            u'GenSubjValue': self.cleanAndEncode(subj)
                        }
                    })
        if self.record.descriptors:
            for descr in self.record.descriptors.strip().split('\t'):
                if not descr == '':
                    self.gs4.terms.append({
                        u'TermType': u'FlexTerm',
                        u'attrs': {u'FlexTermName': u'HAPIDescriptor'},
                        u'values': {
                            u'FlexTermValue': self.cleanAndEncode(descr)
                        }
                    })

    def _objectIDs(self):
        self.gs4.objectIDs = []
        if self.gs4.issn:
            self.gs4.objectIDs.append({'value': self.gs4.issn,
                                       u'IDType': u'ISSN'})
        if not self.record.hapiid == '':
            self.gs4.objectIDs.append({'value': self.record.hapiid,
                                       u'IDOrigin': u'HAPI',
                                       u'IDType': u'HAPIID'})
        if self.record.pqid:
            self.prisma132 = self.record.pqid
            self.gs4.objectIDs.append({'value': self.prisma132,
                                       u'IDOrigin': u'PQ',
                                       u'IDType': u'PQID'})
        else:
            self.prisma132 = self.record.hapiid  # pylint: disable=W0201
        self.gs4.objectIDs.append(
            {'value': self._prefixedLegacyId(self.prisma132),
             u'IDOrigin': u'Prisma132',
             u'IDType': u'CHLegacyID'}
        )
        self.gs4.objectIDs.append({'value': self.gs4.originalCHLegacyID,
                                   u'IDOrigin': unicode(self.productId),
                                   u'IDType': u'CHOriginalLegacyID'})

    def _getLegacyID(self):
        if self.useHapi:
            self.gs4.legacyID = self._prefixedLegacyId(self.record.hapiid)
            self.gs4.originalCHLegacyID = self.record.hapiid
            if self._cfg['prismaType'] == 'pqnohapi':
                self.gs4.legacyID = '-'.join([self.gs4.legacyID, '1'])
        else:
            self.gs4.legacyID = self._prefixedLegacyId(self.record.pqid)
            self.gs4.originalCHLegacyID = self.record.pqid

    def _relatedLegacyID(self):
        if self.record.pqid is not '':
            self.gs4.relatedLegacyID = self.record.pqid

    def _getPublicationTitle(self):
        if getattr(self.record, 'pq_publication') is not '' and \
           getattr(self.record, 'publication') is not '':
            pubtitle = self.record.publication
        elif getattr(self.record, 'pq_publication') is not '':
            pubtitle = self.record.pq_publication
        elif getattr(self.record, 'publication') is not '':
            pubtitle = self.record.publication
        else:
            pubtitle = self.record.jtitle
        self.pubTitle(pubtitle)

    def _objectBundleData(self):
        self.gs4.objectBundleData = []
        if self._cfg['prismaType'] == 'pqonly':
            self.gs4.objectBundleData.append(self.hapiBundle())
            self.gs4.objectBundleData.append(self.pqBundle())
        elif self.useHapi:
            self.gs4.objectBundleData.append(self.hapiBundle())
        else:
            self.gs4.objectBundleData.append(self.pqBundle())


    #### Helper methods and functions.
    def cleanPrismaAbstractMarkup(self, string):
        return self.cleanAndEncode(
            re.sub(
                '(<|&(amp;&)?lt;)/?((S|M)ABS|PARA)(>|&(amp;&)?gt;)', '', string
            )
        )

#    def setNamedAttr(self, attr, value):
#        self.gs4.__setattr__(attr, textUtils.cleanAndEncode(value))
#        self.gs4.__setattr__(attr, self.cleanAndEncode(value))


    ### To handle the ObjectBundleData settings
    @staticmethod
    def bundle(bundleType):
        return {
            u'ObjectBundleType': u'CHProductCode',
            u'ObjectBundleValue': unicode(bundleType)
        }
    def hapiBundle(self):
        return self.bundle('PrismaHAPI')
    def pqBundle(self):
        return self.bundle('Prisma')
