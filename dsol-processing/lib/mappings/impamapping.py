# -*- mode: python -*-
# pylint: disable = C0301

import sys, os, re
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib'))
sys.path.append('/packages/dsol/lib/python')

import datetime

from mappings.abstractmapping import AbstractMapping
from commonUtils import dateUtils, langUtils, textUtils
from cstoreerrors import SkipRecordException
from SequenceDict import SequenceDict #pylint: disable=F0401

from mixin import mixin
from mixinmodules.fulltext import FullTextMixin as fulltext

from mappings.impadatastructures import productElementNames
from mappings.impadatastructures import documentTypes
from mappings.impadatastructures import iimpInno, iipaInno
from mappings.impadatastructures import paopdfPageCounts
from mappings.impadatastructures import futzIDs

import lxml.etree as ET

import logging
log = logging.getLogger('tr.mapping.impa')


class IMPAMapping(AbstractMapping):
    def __init__(self, rawrecord):
        super(IMPAMapping, self).__init__(rawrecord)
        mixin(self, fulltext)
        self._documentTypes = documentTypes

        self._productElementNames = productElementNames
        self._missingDIDs = futzIDs

        self._dtable = {
            'abstract':              IMPAMapping.abstract,
            'altjournaltitles':      IMPAMapping.noop,  # computed. altJournalTitles,
            'articleid':             IMPAMapping.setLegacyDocumentID,  # noop,
            'author':                IMPAMapping.noop,  # We need to use a computedValues callback as we have author data in two fields.
            'autoftflag':            IMPAMapping.noop, #'RECORD/Product/CHIMPA/autoftflag',
            'body':                  'RECORD/ObjectInfo/TextInfo/Text[@Source]',
            'char':                  IMPAMapping.noop, # computed.
            'cloc':                  IMPAMapping.noop, # computed 'Term, "Geo"',
            'cnam':                  IMPAMapping.noop,  # computed 'Term, "Personal"',
            'coauthor':              IMPAMapping.noop,  # See above, for 'author'
            'corg':                  IMPAMapping.noop, # computed 'Terms, "CompanyName"',
            'csbj':                  IMPAMapping.noop,  #computed 'FlexTerm, "Thes"',
            'csup':                  IMPAMapping.noop,  # computed 'FlexTerm, "Suppl"',
            'documentlanguage':      IMPAMapping.noop,   #language,
            'documenttype':          IMPAMapping.searchObjectType,
            'elecissn':              IMPAMapping.noop,  # The Electronic ISSN, where it differs from the print one. computed, _objectIDs
            'elecissntrim':          IMPAMapping.noop,  # Not used.
            'ftnotes':               'What are we doing with this? Mapping doc asks if we can ignore it.',
            'fulltextflag':          IMPAMapping.noop,  # computed fullTextFlag,
            'issn':                  IMPAMapping.noop,
            'issntrim':              IMPAMapping.noop,
            'issuenote':             IMPAMapping.nonStandardCitation,
            'journalid':             IMPAMapping.journalID,
            'journalissue':          IMPAMapping.issue,
            'journaltitle':          IMPAMapping.pubTitle, #None,
            'journaltitleinitial':   IMPAMapping.noop,
            'journalvolume':         IMPAMapping.volume,
            'jstor':                 IMPAMapping.noop,  # Computed value
            'language':              IMPAMapping.noop,  # computed language,
            'loisort':               IMPAMapping.noop,
            'museurl':               IMPAMapping.noop, # computed, _links
            'musecollection':        IMPAMapping.noop, # computed, Product
            'narrowsubjectnavfield': IMPAMapping.noop, # Not required
            'naxoscomposer':         IMPAMapping.noop, # computed 'FlexTerm, "NaxosComposer", @FlexTermOpt=NAXOSID:{ID}',
            'naxosartist':           IMPAMapping.noop,  # NOT REQUIRED 'FlexTerm, "NaxosArtist"',
            'naxosconductor':        IMPAMapping.noop,  # NOT REQUIRED 'FlexTerm, "NaxosConductor"',
            'naxosorchestra':        IMPAMapping.noop,  # NOT REQUIRED 'FlexTerm, "NaxosOrchestra"',
            'naxosensemble':         IMPAMapping.noop,  # NOT REQUIRED 'FlexTerm, "NaxosEnsemble"',
            'naxoschoir':            IMPAMapping.noop,  # NOT REQUIRED 'FlexTerm, "NaxosChoir"',
            'onlineurl':             IMPAMapping.noop,  # computed - _links
            'pagedisplay':           IMPAMapping.pagination,
            'paoarticleid':          IMPAMapping.noop,  # objectIDs
            'pdftxtflag':            'What are we doing with this?',
            'peerreviewflag':        IMPAMapping.peerReviewed,
            'pqarticleimageid':      IMPAMapping.noop,  # computed, _objectIDs
            'pqpageimageid':         IMPAMapping.noop,
            'pmurl':                 IMPAMapping.noop,  # computed, _links.
            'productid':             IMPAMapping.productid,  #'RECORD/ObjectInfo/LegacyProductMapping/GroupName',
            'pubdisplaydate':        IMPAMapping.rawPubDate,
            'publishcountry':        IMPAMapping.noop,  # NO LONGER REQUIRED. PublicationInfo inteferes with TRACS feed. publisherCountry,
            'publishedenddate':      IMPAMapping.noop,
            'publishedstartdate':    IMPAMapping.noop,
            'publishedyear':         IMPAMapping.noop,
            'publisher':             IMPAMapping.noop,  # NO LONGER REQUIRED. PublicationInfo inteferes with TRACS feed. publisher,
            'royaltiesid':           IMPAMapping.noop, #'RECORD/Product/CHIMPA/royaltiesid',
            'sequencenum':           IMPAMapping.nonStandardCitation,
            'sortjournaltitle':      IMPAMapping.noop,
            'specialfeatures':       IMPAMapping.documentFeatures,
            'spub':                  IMPAMapping.supplement,
            'subject':               IMPAMapping.noop, # computed 'FlexTerm[@FlexTermName=BroadSubject.]',
            'title':                 IMPAMapping.title,
            'tngflag':               IMPAMapping.noop,
            'translatedtitle':       IMPAMapping.alternateTitle,
            'volissue':              IMPAMapping.noop,
            'volissuesort':          IMPAMapping.noop,
            'workassubject':         IMPAMapping.noop, # computed FlexTerm
            'DID':                   IMPAMapping.did,  # For the Full text check, using the DID exported in the data.
            'UPDATED':               IMPAMapping.noop, # Not sure what this is for. It appeared in the early Jan 2011 handover.
            }

        self._componentTypes['InnoImgReprs'] = IMPAMapping._buildInnoImgReprs

        for element in rawrecord.data.xpath('.//*[@name]'):
            # We don't use the contents of the //element[@name="body"], so we can
            # just remove it from the etree document.
            if element.attrib['name'] == 'body':
                rawrecord.data.remove(element)
                continue
            field_name = element.attrib.values()[0]
            self._fields.append(field_name)
            setattr(self.record, field_name, unicode(element.xpath('value')[0].text))

        # So that we have early access to the document ID, insert it as a member on self.
        setattr(self, "documentID", self.record.articleid)

        # These definitions have been moved out into a separate module so that they are only
        # called once, when the module is imported, and not each time a new Mapping object is
        # instantiated. BIG time savings follow...!
        if self.record.productid == 'iimp':
#            self._rids = impadatastructures.iimprids
            self._innoDataIDs = iimpInno
        else:
#            self._rids = impadatastructures.iiparids
            self._innoDataIDs = iipaInno
        self._paopdfPageCounts = paopdfPageCounts


        self._computedValues = [
            IMPAMapping._components,
            IMPAMapping._terms,
            IMPAMapping._legacyID,
            IMPAMapping._futzDIDs,
            IMPAMapping._objectIDs,
            IMPAMapping._setDates,
            IMPAMapping._objectBundleData,
            IMPAMapping._authors,
            IMPAMapping._impaProductInfo,
            IMPAMapping._languages,
            IMPAMapping._links,
            ]

        self._after_hooks = [
            IMPAMapping._set_search_object_type,
            IMPAMapping._fix_empty_title,
            IMPAMapping._do_full_text_if_configured,
            IMPAMapping._set_steady_state_token,
            ]

        self._after_hooks_always_run = [
            IMPAMapping._lastUpdateTime,
            ]

        self._journalsWithoutLanguage = {
            # All these have been fixed in the source data.
            #'Variety': u'English',
            #'Opernwelt - das internationale Opernmagazin': u'German',
            #'The Journal of Aesthetics and Art Criticism': u'English',
            #'The Village Voice': u'English',
            #'Medical Problems of Performing Artists': u'English'
            }

        self._dateSpecialCases = {
            # Added this as a general rule to dateUtils module, line 192
            # 'JID09667180': {'Christmas 2009': 'December 2009',
            #                 'Christmas 2010': 'December 2010'},
            }

        self._journalsWithExtFTLinks = {
            # Journals that should have a FullTextLinkID ObjectID from
            # the ProQuest ft feed. So far, only affects the Village
            # Voice. If in future it applies to more journals, add
            # them to the appropriate product's list. If it ever
            # applies to a journal in some collection other than
            # IIMP/IIPA, move this structure to AbstractMapping.
            'iipa': ['JID00426180'],
            'iimp': ['JID00426180'],
            }

        self._journalAbbrevs = {}
        # Gotta love list comprehensions! We take the first three
        # columns from the lookup file, then place the first two in a
        # tuple to use as the lookup key, and the third as the value.
        # This approach is necessary in order to correctly handle
        # journals that changed title and ISSN (and therefore
        # abbreviated name) during their run.
        for line in [
                line.rstrip().split('\t')[0:3] for line
                in open(
                    self._cfg['app_root'] +
                    '/libdata/impajournalabbrevs/' +
                    self.record.productid + '.lup'
                ) if not line == '']:
            if line[1] == '':
                continue
            self._journalAbbrevs[(line[0], line[1],)] = line[2].rstrip()

        self.ssid = self.record.articleid
        # As we need to differentiate between full text and non-full
        # text, we'll redefine the SteadyStateHandler here.
        if 'fulltext' in self._cfg['mappingOptions']:
            self.ssTableName = ''.join([self._cfg['product'], 'ft'])
            self.productId = ''.join([self.productId, 'ft'])
        else:
            self.ssTableName = self._cfg['product']
            self.productId = self._cfg['product']

        # An empty dict used for storing chids later.
        self.chids = {}

        # We need to key the journal abbreviation lookup on ISSN and
        # JID, since some journals change title and ISSN part way
        # through a run. Create a tuple holding each here
        self.issn_jid = (self.record.issn, self.record.journalid,)

#     def before_hooks(self):
#         if self._cfg['verbose']:
#             print >> sys.stderr, self._cfg['filename'] + ' ' + self.record.articleid


    ## Hooks
    def _set_search_object_type(self):
        if 'searchObjectType' not in self.gs4.fields():
            self.gs4.searchObjectType = [u'Article']

    def _fix_empty_title(self):
        # If we get a record with no Title (there are a few)
        if getattr(self.gs4, 'title') == '' or getattr(self.gs4, 'title') == None:
            self.gs4.title = "[untitled]"

    def _do_full_text_if_configured(self):
        if 'fulltext' in self._cfg['mappingOptions']:
            self._fullText()

    def _set_steady_state_token(self):
        if self.record.UPDATED == '':
            self.record.UPDATED = 'UNDATED'
        self.setSteadyStateToken(self.record.UPDATED)

    def chid(self):
        while True:
            try:
                return self.chids[self.record.articleid]
            except KeyError:
                _chid = re.search(r'ii(mp|pa)[A-Za-z]*0*([0-9_-]+)', self.record.articleid).group(2)
                self.chids[self.record.articleid] = _chid
                log.debug("CHID for %s determined to be %s ", self.record.articleid, _chid)

    # Insert fulltext from one of its many possible sources...
    # It requires that the DID method is enabled in the dtable
    # so that self.gs4.relatedid is defined.

    # Many changes here to handle PDF only journals, and to take
    # Innodata IDs from an external list, and not by looking at the
    # crawled web farm content. That former approach led to some
    # records incorrectly pulling in PQ data - there is no distinction
    # in the crawled data between Innodata and PQ data. By relying on
    # an external list, we know we are only pulling in Innodata
    # content where it is appropriate to do so.
    def _fullText(self):
        # The value held here determines whether or not we add the related ID object IDs.
        do_related_ids = True

        # Find the PDF Only Journals section in the user config files.
        userConfig = self._cfg['usertunables']
        cfgSect = "PDF Only Journals"

        # Check to see if the article ID is in the list of InnoData articles.
        if self.gs4.originalCHLegacyID in self._innoDataIDs:
            log.debug(
                "%s: InnoData full text from list (%s)",
                self.gs4.originalCHLegacyID, self._cfg['basename']
            )
            try:
                log.debug(
                    "Attempting to insert InnoData full text for %s...",
                    self.gs4.originalCHLegacyID
                )
                self.insertFullText(self.chid(), fttype='inno')
                self.gs4.fttype = 'inno'
            except KeyError:
                log.error(
                    "No abbreviation found for %s. Skipping record %s",
                    self.record.journaltitle, self.gs4.originalCHLegacyID
                )
                raise SkipRecordException

        # If it's not explicitly listed as an InnoData record, check
        # if it's explicitly listed as a PDF-only record
        elif userConfig.has_option(cfgSect, self.record.journalid) and self.gs4.numericStartDate >= userConfig.get(cfgSect, self.record.journalid):
            log.debug(
                "%s: PDF only journal record (%s)",
                self.gs4.originalCHLegacyID, self._cfg['basename']
            )
            if self.gs4.relatedid:
                log.debug(
                    "Adding PDF link for %s (%s)",
                    self.gs4.originalCHLegacyID, self.gs4.relatedid
                )
                self.insertFullText(self.gs4.relatedid, fttype='pdf')
                self.gs4.fttype = 'pdf'
            else:
                log.debug(
                    "No associated PDF for %s",
                    self.gs4.originalCHLegacyID
                )
#                do_related_ids = False

        # Does the record have a paoarticleid field? The legacy
        # product only considers records that have a paoarticleid
        # field. We will adopt the same strategy.
        elif self.record.paoarticleid:
            log.debug(
                "%s: checking for PAO PDF content",
                self.gs4.originalCHLegacyID
            )
            self._paoPdfComponent()
            do_related_ids = False

        # Otherwise, check in the PQ feed
        else:
            if not self.gs4.relatedid == None:
                log.debug(
                    "%s: PQ full text (%s)",
                    self.gs4.originalCHLegacyID, self._cfg['basename']
                )
                self.insertFullText(self.gs4.relatedid)
                self.gs4.fttype = 'pq'
            else:
                log.debug(
                    "%s: No DID in source data or lookup",
                    self.gs4.originalCHLegacyID
                )

#         # Perhaps it is just an ordinary PQ full text record...
#         elif not re.search('-', self.gs4.originalCHLegacyID):
#             if not self.gs4.relatedid == None:
#                 log.debug("%s: PQ full text (%s)" % (self.gs4.originalCHLegacyID, self._cfg['basename'],))
#                 self.insertFullText(self.gs4.relatedid)
#                 self.gs4.fttype = 'pq'
#             else:
#                 log.debug("%s: No DID in source data or lookup" % self.gs4.originalCHLegacyID)
# #                do_related_ids = False
#         else:
#             log.debug("%s: checking for PAO PDF content" % self.gs4.originalCHLegacyID)
#             self._paoPdfComponent()
#             do_related_ids = False

        if do_related_ids == True:
            self._relatedLegacyIDs()


    # End Hooks

    def _languages(self):
        languages = self.record.language if self.record.language else self.record.documentlanguage
        self.language(languages)

    def language(self, data):
        if self.record.journaltitle in self._journalsWithoutLanguage.keys():
            if data == '':
                log.warning(
                    "%s: journal has no language or documentlanguage attributes (%s)",
                    self.record.journaltitle, self.legacyDocumentID
                )
                data = self._journalsWithoutLanguage[self.record.journaltitle]
        languages = langUtils.languages(data, delimiter=self._defaultDelimiter)
        self.gs4.languageData = langUtils.lang_iso_codes(languages)

    def abstract(self, data):
        if data:
            self.gs4.abstract = self._abstract(data, u'Synopsis')

    def searchObjectType(self, data):
        objectTypes = []
        # stringToList()
        for objtype in data.split(self._defaultDelimiter):
            if objtype in self._documentTypes.keys():
                objectTypes.append(self._documentTypes[objtype])
            else:
                objectTypes.append(objtype)
        self.gs4.searchObjectType = objectTypes

    def alternateTitle(self, data):
        self.gs4.alternateTitle = self.cleanAndEncode(data)

    def supplement(self, data):
        self.gs4.parentInfoSupplement = self.cleanAndEncode(data)

    def productid(self, data):
        self.productId = self.cleanAndEncode(data)
        self.gs4.productid = self.productId

#    def relatedid(self):
#        return self.record.DID

    def did(self, data):
        self.gs4.relatedid = data

    # Computed Values A temporary hack (!) to include some 20 thousand
    # DIDs that are not currently held in STAR. It only triggers if
    # the self.gs4.relatedid member is empty or undefined, so when
    # DISs get added to STAR, this check will do nothing. One day, we
    # can remove it altogether...
    def _futzDIDs(self):
        if self.gs4.originalCHLegacyID in self._missingDIDs:
            log.warning(
                "Missing DID inserted from lookup: legacy ID: %s, DID: %s",
                self.gs4.originalCHLegacyID,
                self._missingDIDs[self.gs4.originalCHLegacyID]
            )
            self.did(self._missingDIDs[self.gs4.originalCHLegacyID])


    def _relatedLegacyIDs(self):
        self.gs4.relatedLegacyIDs = [[
            'CH', self._prefixedLegacyId(self.record.articleid),
            'DerivedFrom'
        ]]
        if self.gs4.fttype == 'pq' or self.gs4.fttype == 'pdf':
            self.gs4.relatedLegacyIDs.append(
                ['PQ', self.gs4.relatedid, 'DerivedFrom']
            )

    def _setDates(self):
        try:
            translatedDate = self._dateSpecialCases[self.record.journalid][self.record.pubdisplaydate]
            print >> sys.stderr, ("DEBUG: Odd date - check _dateSpecialCases")

        except KeyError:
            translatedDate = textUtils.translateDate(self.record.pubdisplaydate)

        try:
            self.gs4.normalisedAlphaNumericDate = dateUtils.normaliseDate(
                translatedDate
            )
        except ValueError:
            log.error(
                "Unhandled date format: %s: %s: %s",
                self.gs4.legacyID, self.gs4.journalID, translatedDate
            )
            raise SkipRecordException
        if self.gs4.normalisedAlphaNumericDate == "Jan 1, 1":
            log.warning(
                "Date set to default: %s: %s: %s, %s",
                self.gs4.legacyID, self.gs4.journalID,
                self.gs4.normalisedAlphaNumericDate, translatedDate
            )
        self.gs4.numericStartDate = dateUtils.pq_numeric_date(
            self.gs4.normalisedAlphaNumericDate
        )
        if self.gs4.numericStartDate.startswith("UNKNOWN DATE FORMAT"):
            log_msg = "%s: %s: %s" % (
                self.gs4.legacyID,
                self.gs4.journalID,
                self.gs4.numericStartDate
            )
            log.error("Unhandled date format: %s", log_msg)
            self._cfg['msq'].append_to_message(
                "Invalid date format (record skipped)", log_msg
            )
            raise SkipRecordException

        # Test to see if the pub date on the record is more than 365 days in the
        # future. This probably indicates a typo, which needs to be fixed
        # upstream. The limit of 365 days was specified by Richelle Treves in
        # the Louisville editorial team.

        # Break the current date into components to pass to the datetime.date
        # function
        t_year = int(dateUtils.today()[0:4])
        t_month = int(dateUtils.today()[4:6])
        t_day = int(dateUtils.today()[6:8])
        today = datetime.date(t_year, t_month, t_day)

        # Same with the publication date
        p_year = int(self.gs4.numericStartDate[0:4])
        p_month = int(self.gs4.numericStartDate[4:6])
        p_day = int(self.gs4.numericStartDate[6:8])
        pubdate = datetime.date(p_year, p_month, p_day)

        # subtract today from the pub date to work out if it's within the
        # specified limit
        if (pubdate - today).days > 365:
            log_msg = "%s: %s: %s" % (
                self.gs4.legacyID,
                self.gs4.journalID,
                self.gs4.numericStartDate
            )
            log.error(
                "Pub date is too far in the future! %s",
                log_msg
            )
            self._cfg['msq'].append_to_message(
                "Pub date too far in the future (record skipped)", log_msg
            )
            raise SkipRecordException

    def _objectIDs(self):
        self.gs4.objectIDs = []
        self.gs4.objectIDs.append({'value':     self.gs4.legacyID,
                                   u'IDOrigin': u'CH',
                                   u'IDType':   u'CHLegacyID'})
        if not getattr(self.record, 'issn') == '':
            self.gs4.objectIDs.append({'value':     self.record.issn,
                                       u'IDType': u'ISSN'})
        if not getattr(self.record, 'elecissn') == '':
            self.gs4.objectIDs.append({'value':     self.record.elecissn,
                                       u'IDType': u'ElecISSN'})
        if not getattr(self.record, 'pqpageimageid') == '':
            self.gs4.objectIDs.append({'value':     self.record.pqpageimageid,
                                       u'IDOrigin': unicode(self.record.productid),
                                       u'IDType':   u'PQID'})
        if not getattr(self.record, 'paoarticleid') == '':
            self.gs4.objectIDs.append({'value':     self.record.paoarticleid,
                                       u'IDOrigin': unicode(self.record.productid),
                                       u'IDType':   u'PAOArticleID'})
        if not getattr(self.record, 'pqarticleimageid') == '':
            self.gs4.objectIDs.append({'value':     self.record.pqarticleimageid,
                                       u'IDOrigin': unicode(self.record.productid),
                                       u'IDType':   u'PQID'})
        if not getattr(self.record, 'jstor') == '':
            self.gs4.objectIDs.append({'value':     self.record.jstor,
                                       u'IDType': u'JSTORSICI'})
        self.gs4.objectIDs.append({'value':     self.gs4.originalCHLegacyID,
                                   u'IDOrigin': unicode(self.productId),
                                   u'IDType':   u'CHOriginalLegacyID'})
        if self.record.journalid in self._journalsWithExtFTLinks[self._cfg['product']]:
            ftlinkid = self._getFTLinkIDFromFeed(self.gs4.relatedid)
            #print "ftlinkid = %s " % ftlinkid
            if ftlinkid is not None:
                self.gs4.objectIDs.append({'value': ftlinkid,
                                           u'IDType': u'FullTextLinkID'})

    def _getFTLinkIDFromFeed(self, docID):
        # Not all records that trigger this code have a DID. Return
        # None as early as possible in those cases.
        if docID is None or docID == '':
            return None

        try:
            return ET.parse(
                self.id2FullTextPath(docID),
                ET.XMLParser()
            ).xpath('.//ObjectID[@IDType="FullTextLinkID"]')[0].text
        except IndexError:
            # Feed file found, but contains no FullTextID link.
            return None
        except IOError:
            # File not found in feed.
            return None

    def _legacyID(self):
        if 'fulltext' not in self._cfg['mappingOptions']:
            suffix = '-1'
        else:
            suffix = ''
        self.gs4.legacyID = self._prefixedLegacyId(
            ''.join([self.record.articleid, suffix])
        )
        self.gs4.originalCHLegacyID = self.record.articleid

    def _authors(self):
        if self.record.coauthor:
            authorData = self._defaultDelimiter.join(
                [self.record.author, self.record.coauthor]
            )
        else:
            authorData = self.record.author
        self.gs4.contributors = self._contributors(authorData)

    def _links(self):
        self.gs4.linkData = []
        if self.record.museurl:
            self.gs4.linkData.append({u'linkType': u'FullTextLink',
                                      'attrs': {u'LinkSource': 'MUSE'},
                                      u'linkValue': self.cleanAndEncode(self.record.museurl)})
        if self.record.pmurl:
            self.gs4.linkData.append({u'linkType': u'OtherLink',
                                      'attrs': {u'LinkType': u'DocUrl'},
                                      u'linkValue': self.cleanAndEncode(self.record.pmurl)})
        if self.record.onlineurl:
            self.gs4.linkData.append({u'linkType': u'OtherLink',
                                      'attrs': {u'LinkType': u'DocUrl'},
                                      u'linkValue': self.cleanAndEncode(self.record.onlineurl)})

    def _terms(self):
        self.gs4.terms = []
        if self.record.corg:
            for term in self.stringToList(self.record.corg):
                self.gs4.terms.append({u'TermType': u'CompanyTerm',
                                       u'values': {u'CompanyName': self.cleanAndEncode(term, escape=True)}})
        if self.record.cloc:
            for term in self.stringToList(self.record.cloc):
                self.gs4.terms.append({u'TermType': u'Term',
                                       u'attrs': {u'TermType': u'Geographic'},
                                       u'values': {u'TermValue': self.cleanAndEncode(term)}})

        if self.record.cnam:
            for term in self.stringToList(self.record.cnam):
                self.gs4.terms.append({u'TermType': u'Term',
                                       u'attrs': {u'TermType': u'Personal'},
                                       u'values': {u'TermValue': self.cleanAndEncode(term)}})

        if self.record.subject:
            for term in self.stringToList(self.record.subject):
                self.gs4.terms.append({u'TermType': u'FlexTerm',
                                       u'attrs': {u'FlexTermName': u'BroadSubject'},
                                       u'values': {u'FlexTermValue': self.cleanAndEncode(term)}})

        if self.record.csbj:
            for term in self.stringToList(self.record.csbj):
                self.gs4.terms.append({u'TermType': u'FlexTerm',
                                       u'attrs': {u'FlexTermName': u'Thes'},
                                       u'values': {u'FlexTermValue': self.cleanAndEncode(term)}})

        if self.record.csup:
            for term in self.stringToList(self.record.csup):
                self.gs4.terms.append({u'TermType': u'FlexTerm',
                                       u'attrs': {u'FlexTermName': u'Suppl'},
                                       u'values': {u'FlexTermValue': self.cleanAndEncode(term)}})

        if self.record.workassubject:
            for term in self.stringToList(self.record.workassubject):
                self.gs4.terms.append({u'TermType': u'FlexTerm',
                                       u'attrs': {u'FlexTermName': u'WorkAsSubject'},
                                       u'values': {u'FlexTermValue': self.cleanAndEncode(term)}})

        if self.record.naxoscomposer:
            for term in self.stringToList(self.record.naxoscomposer):
                composer, naxosid = term.split(':')
                self.gs4.terms.append({u'TermType': u'FlexTerm',
                                       u'attrs': {u'FlexTermName': u'NaxosComposer',
                                                  u'FlexTermOpt': self.cleanAndEncode('NAXOSID: ' + naxosid)},
                                       u'values': {u'FlexTermValue': self.cleanAndEncode(composer)}})

#     def _buildTerms(self, legacyElement, termType, attrDict, valDict):
#         if getattr(self.record, legacyElement):
#             for term in self.stringToList(getattr(self.record, legacyElement)):
#                 self.gs4.terms.append({u'TermType': unicode(termType),
#                                        u'attrs': attrDict,
#                                        u'values': valDict})

    def pagination(self, data):
        pagedisplay = data.rstrip()
        pagedisplay = re.sub(r"[]'., +-]+?$", '', pagedisplay)
        pagedisplay = re.sub(r'(\d+) ?- ?(\d+)', r'\1-\2', pagedisplay)
        self.gs4.pagination = super(IMPAMapping, self).pagination(pagedisplay)

        if re.search(r'^[0-9-,]+ ff\.', pagedisplay):
            self.gs4.startPage = self.startpage(pagedisplay)
#            self.gs4.endPage = u''
        elif re.search(r'^[0-9-]+ \[sic\]', pagedisplay):
            display = re.search(r'^([0-9-]+) \[sic\]', pagedisplay).group(1)
            sys.stderr.write(display + '\n')
            self.gs4.startPage = self.startpage(display)
            self.gs4.endPage = self.endpage(display)
        elif re.search(r'^[0-9+-,]+', pagedisplay):
            self.gs4.startPage = self.startpage(pagedisplay)
            if self.startpage(pagedisplay) != self.endpage(pagedisplay):
                self.gs4.endPage = self.endpage(pagedisplay)
            else:
                self.gs4.endPage = u''
        elif re.search(r'[sS]ec(tion)? [iI]nsert', pagedisplay):
            self.gs4.startPage = pagedisplay
            self.gs4.endPage = pagedisplay
        elif re.search(r'Front\.?', pagedisplay):
            self.gs4.startPage = pagedisplay
#            self.gs4.endPage = u''
        elif re.search(r'\[\d+\]( ff\.)?', pagedisplay):
            self.gs4.startPage = pagedisplay
#            self.gs4.endPage = u''
        elif re.search(r'\d+ ?-$', pagedisplay):
            self.gs4.startPage = re.match(r'\d+', pagedisplay).group(0)
            self.gs4.endPage = self.gs4.startPage
        elif re.search(r'^[^A-Za-z0-9 -]+', pagedisplay):
            self.gs4.startPage = pagedisplay
#            self.gs4.endPage = u''
        elif re.search(r'[A-Za-z0-9]+.*', pagedisplay):
            self.gs4.startPage = pagedisplay
#            self.gs4.endPage = u''
        elif self.startpage(pagedisplay) == self.endpage(pagedisplay):
            self.gs4.startPage = self.startpage(pagedisplay)
        else:
            self.gs4.startPage = self.startpage(pagedisplay)
            self.gs4.endPage = self.endpage(pagedisplay)


    def _startPage(self, pagedisplay):
        #if 'pagination' in self.gs4.fields():
        #    self.startpage(self.gs4.pagination)
        self.startpage(pagedisplay)

    def _endPage(self):
        self.endpage(self.gs4.pagination)

    def _lastUpdateTime(self):
        self.gs4.lastUpdateTime = dateUtils.fourteenDigitDate()

    def _impaProductInfo(self):
        productParts = SequenceDict()
        for part in '''char fulltextflag autoftflag musecollection royaltiesid tngflag'''.split():
            if not getattr(self.record, part) == '':
                productParts[
                    self._productElementNames[part]
                ] = self.cleanAndEncode(getattr(self.record, part))

        if not self.record.altjournaltitles == '':
            productParts[u'CHIMPA-AltJrnlTitles'] = []
            altJrnTitles = self._altJournalTitles(self.record.altjournaltitles)
            for title in altJrnTitles:
                productParts[u'CHIMPA-AltJrnlTitles'].append(title)
        self.gs4.product = {u'CHIMPA': productParts}

    def _objectBundleData(self):
        if 'fulltext' in self._cfg['mappingOptions']:
            ft = 'FT'
        else:
            ft = ''
        super(IMPAMapping, self).objectBundleData(
            ''.join([self.productId.upper(), ft])
        )

    def _altJournalTitles(self, data):
        altJournalTitles = []
        if self._defaultDelimiter in data:
            delimiter = self._defaultDelimiter
        else:
            delimiter = '/'
        for item in data.split(delimiter):
            if item:
                altJournalTitles.append(self.cleanAndEncode(item))
        return altJournalTitles

    def _paoPdfComponent(self):
        if self.record.paoarticleid in self._paopdfPageCounts:
            log.info(
                "inserted PAO PDF content for %s in file %s",
                self.gs4.originalCHLegacyID, self._cfg['basename']
            )
            self.gs4.preformattedComponents = []
            self.gs4.preformattedComponents.append(
'''  <Component ComponentType="FullText">
    <CHImageIDs>
      <CHID>%s</CHID>
    </CHImageIDs>
    <Representation RepresentationType="PDFFullText">
      <MimeType>application/pdf</MimeType>
      <Resides>CH/PAO</Resides>
      <Color>BW</Color>
      <Scanned>true</Scanned>
    </Representation>
  </Component>
  <Component ComponentType="Pages">
    <PageCount>%s</PageCount>
    <CHImageIDs>
      <CHID>%s</CHID>
    </CHImageIDs>
    <Representation RepresentationType="Normal">
      <MimeType>image/jpeg</MimeType>
      <Resides>CH/PAO</Resides>
      <Color>BW</Color>
    </Representation>
  </Component>''' % (
      self.record.paoarticleid,
      self._paopdfPageCounts[self.record.paoarticleid],
      self.gs4.originalCHLegacyID))

        else:
            log.warning(
                "%s not in pagecount lookup table. Omitted from output",
                self.gs4.originalCHLegacyID
            )


    @staticmethod
    def _buildInnoImgReprs(componentData, _):
        # Simply pass back what we're given. I don't remember why I
        # did it like this, but it seems to have stuck. I suppose
        # having different names for these methods helps remind me
        # what each one is for, and which helper method it gets passed
        # to...
        return componentData

    @staticmethod
    def _constructMediaKey(pathinfo):
#        pathinfo = re.sub(r'/figures/ch/ii(pa|mp)ft/docs', '/media/ch/iimpa', pathinfo)
#        pathinfo = pathinfo[0:-4]
        pathinfo = '/media/ch/iimpa' + pathinfo
        return pathinfo
