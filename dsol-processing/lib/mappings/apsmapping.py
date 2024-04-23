# -*- mode: python -*-
# pylint: disable = invalid-name, missing-docstring

import bsddb
import logging
import os

from commonUtils import dateUtils
from commonUtils.fileUtils import buildLut
from commonUtils.listUtils import uniq_sort
from commonUtils.textUtils import remove_unwanted_chars
from commonUtils.textUtils import strip_control_chars
from cstoreerrors import CorruptXMLError
from cstoreerrors import RescaleFactorUndefinedError
from cstoreerrors import SkipRecordException
from dbcache import DBCacheManager
from mappings.abstractetreemapping import AbstractEtreeMapping
from mappings.protoapsmapping import ProtoAPSMapping
# Common transformations for APS-derived content sets that are used outside
# the transformation app (metadata generation, etc.)
from mappings.rules.APSRules import pmid as APSpmid
from mappings.rules.APSRules import title as APStitle
from mappings.rules.APSRules import articleid as APSarticleid

from mappings.rules.general import get_last_digit
from pagefilehandler import PagefileHandler  #, Document  #, Word
from pagination import Pagination


log = logging.getLogger('tr.mapping.aps')

class APSMapping(AbstractEtreeMapping, ProtoAPSMapping):
    # pylint: disable = too-many-instance-attributes
    # This tuple holds arrays of XPAth specifications and optional attribute
    # name. Used in __init__() to populate the self.record object from the
    # rawrecord passed in from the stream.
    # At the moment, it is necessary to put additional values required by
    # subclasses here, because the call to assignSimpleAttrs()

    __simpleAttrs = [
        ['APS_article/@pmid', 'pmid'],
        ['APS_article/@type', 'article_type'],
        ['APS_title', 'title'],
        ['APS_volume', 'volume'],
        ['APS_issue', 'issue'],
        ['APS_printed_date', 'printed_date'],
        ['APS_date_8601', 'numeric_date'],
        ['APS_source', 'source_institution'],
        ['APS_language', 'language'],
        ['APS_author', 'author'],
        ['APS_abstract', 'abstract'],
        ['APS_supplement', 'supplement'],
        ]

    language_codes = buildLut('iso-2-letter-lang-codes.txt')

    def __init__(self, rawrecord):
        super(APSMapping, self).__init__(rawrecord)
        self.log = log

        # XPath expressions used elsewhere in the mapping
        self.xpaths = self.get_xpaths()

        self.xml = self.rawrecord.data # well, it's shorter, innit?

        # The EIMA media services page collection data is rooted at
        # /media/ch/eima/pc. /media/ch is (at the moment) immutable.
        # eima is detected from the data, but the final part differs between
        # products, hence the need to set it explicitly here.
        # This variable is used in _mediaKey() in AbstractEtreeMapping.
        #self.ms_page_collection_root = 'pc'

        self.simpleAttrs = self.__simpleAttrs

        self.assignSimpleAttrs(self.simpleAttrs)

        self.record.text = (' ').join(self.getTextFromXML('//APS_text'))
        self.record.pages = uniq_sort(
            [image.replace('jp2', 'jpg') for
             image in self.getTextFromXML('//APS_page_image')]
        )

        # doc_feature may occur any number of times within a record.
        self.record.doc_features = '|'.join(
            uniq_sort(
                [feature for feature in self.getTextFromXML('.//APS_feature')]
            )
        )

        # Grab the page numbers from the //APS_zone sections.
        self.record.pagenumbers = self.set_page_numbers()

        # Preprocess the title element. If it is empty, take the value
        # of article_type, and pass it through the normalise method.
        #if self.record.title == '':
        #    self.record.title = self.normalise_article_type(self.record.article_type)

        self._dtable = {
            'article_type': self.__class__.searchObjectType,
            'author':       self.__class__.authors,
            'doc_features': self.__class__.doc_feature,
            'issue':        self.__class__.issue,
            'language':     self.__class__.language,
            'numeric_date': self.__class__.noop,
            'pages':        self.__class__.noop, #pages,
            'pagenumbers':  self.__class__.pagenumbers,
            'pmid':         self.__class__.journalID,
            'printed_date': self.__class__.noop,  #rawPubDate,
            'text':         self.__class__.hiddenText,
            'title':        self.__class__.title,
            'volume':       self.__class__.volume,
        }

        #pylint:disable=W0212
        self._computedValues = [
            self.__class__._insertRawPubDate,
            self.__class__._legacyID,
            self.__class__._setDates,
            self.__class__._legacy_parent_id,
            self.__class__._objectIDs,
            self.__class__._lastUpdateTime,
            self.__class__._components,
            self.__class__._copyright_statement,
            self.__class__._cover,
            ]


        # Some documents don't have a title encoded in the source.
        # For such cases, use the after_hooks to add '[untitled]'
        self._after_hooks = [
            self.__class__._fill_in_blank_title,
            #self.__class__._update_pagefiles,
            #self.__class__._build_hithighlighting_tables,
            ]

        # DBCache file for 700 and 2880 rescale factors
        year = self.record.numeric_date[0:4]
        cache_path = os.path.join(
            self._cfg['rescalecacheroot'], self.pmid, '%s.2880' % year)
        try:
            self.rescalecache_2880 = DBCacheManager(
                '%s_%s' % (self.pmid, self.record.numeric_date), '2880',
                cache_path)
        except bsddb.db.DBNoSuchFileError:
            self.msq.append_to_message(
                "Missing cache.2880", [self._cfg['pruned_basename'], cache_path])
            log.error("Missing rescale cache file for %s (%s)", self._cfg['filename'], cache_path)
            raise SkipRecordException
        # Remove '_final' from the value in cfg['pruned_basename']
        self._cfg['pruned_basename'] = self._cfg[
            'pruned_basename'].replace('_final', '')

        # Get the copyright statements for the record Copyright
        # statements for TRJ, AAA and EIMA are loaded from external
        # modules. The implementation is independent, as long as the
        # copyright statements are returned as a dict keyed
        # appropriately for the product. In the case of TRJ, the key
        # is the source institution identifier. In all other cases,
        # the key is the journal ID. Since WWD has a single statement
        # for the whole collection, we don't really need to move it
        # out to a separate module, but for the sake of consistency
        # and to enable its use in other tools, we'll do it anyway...
        self.copyright_statements = self.fetch_copyright_statements()

    @property
    def productCode(self):
        return self.get_product_code(lambda s: s.upper())

    @property
    def pmid(self):
        while True:
            try:
                return self._pmid
            except AttributeError:
                setattr(self, '_pmid', APSpmid(self._cfg['product'], self.xml))


    # +++ populate self.record
    # This is all handled by methods defined in AbstractEtreeMapping.
    # Except the pagenumbers, which are peculiar(!) to EIMA.
    # Store the values of APS_zone_pagenumber (the actual print page numbers)
    # keyed by the value of APS_page_sequence, which is guaranteed to be
    # a numerical value. We then sort the dict by its keys, and append each
    # value to self.record.pagenumbers, which is used to produce the pagination
    # information for the record.
    ## def set_page_numbers(self):
    ##     pages = {}
    ##     pagenumbers = []
    ##     for zone in self.xml.xpath('//APS_zone'):
    ##         # Cast the value of APS_page_sequence to an integer so it can be used to
    ##         # retrieve the values of APS_zone_pagenumber in the correct order
    ##         pages[int(zone.xpath(
    ##             './/APS_page_sequence')[0].text)] = zone.xpath(
    ##                 './/APS_zone_pagenumber')[0].text
    ##     for pagenum in sorted(pages.keys()):
    ##         pagenumbers.append(pages[pagenum])
    ##     return pagenumbers

    @staticmethod
    def normalise_article_type(string):
        words = string.split('_')
        words[0] = words[0].capitalize()
        words[-1] = words[-1].capitalize()
        return (' ').join(words)

    # --- populate self.record

    def _merge_dtables(self, other):
        # Merge a child class's _dtable into the parent.
        # If both the child and parent have the same key, the one
        # in the child's replaces the parent's.
        self._dtable = dict(self._dtable.items() + other.items())

    # +++ mapping rules

    def title(self, data):
        self.gs4.title = APStitle(self.xml)

    def searchObjectType(self, data):
        self.gs4.searchObjectType = [self.cleanAndEncode(data)]

    def hiddenText(self, data):
        data = remove_unwanted_chars(strip_control_chars(data))
        self.gs4.hiddenText = self.cleanAndEncode(data).split('\n')

    def language(self, data):
        try:
            super(APSMapping, self).language(self.language_codes[data])
        except KeyError:
            log.error(
                "Unkown language code: '%s' in %s",
                data, self._cfg['pruned_basename'])
            self.msq.append_to_message(
                "Unknown language code",
                "%s: %s" % self._cfg['pruned_basename'], data)
            raise SkipRecordException

    def pagenumbers(self, data):
        try:
            self.gs4.startpage = self.helper_startPage(data[0])
        except IndexError:
            log.error(
                'No pagination information in %s. Skipping record',
                self._cfg['filename'])
            self.msq.append_to_message(
                'No pagination information for record (omitted from output)', self._cfg['filename'])
            raise SkipRecordException
        except TypeError:
            log.error(
                'Problem setting page numbers for %s. Skipping record',
                self._cfg['pruned_basename'])
            raise SkipRecordException
        self.gs4.pagination = self.cleanAndEncode(
            Pagination(self.record.pagenumbers).formatted_string)

    def doc_feature(self, data):
        self.gs4.docFeatures = [
            self.cleanAndEncode(feature)
            for feature in data.split('|') if not data == '']

    # ---

    # +++ computedValues

    def _insertRawPubDate(self):
        if self.record.printed_date.strip() != '':
            self.gs4.rawPubDate = self.cleanAndEncode(self.record.printed_date)

    def _legacyID(self):
        # The source data doesn't contain a usable legacy ID, so we need
        # to take it from the source file name instead.
        self.gs4.originalCHLegacyID = APSarticleid(self._cfg['pruned_basename'])
        self._set_legacy_id()

    def _set_legacy_id(self):
        self.gs4.legacyID = "%s-%s" % (self.productId, self.gs4.originalCHLegacyID)

    def _objectIDs(self):
        self.gs4.objectIDs = []
        self.gs4.objectIDs.append({'value': self.gs4.legacyID,
                                   u'IDOrigin': u'CH',
                                   u'IDType': u'CHLegacyID'})
        self.gs4.objectIDs.append({'value': self.gs4.originalCHLegacyID,
                                   u'IDOrigin': u'CH',
                                   u'IDType': u'CHOriginalLegacyID'})

    def _copyright_statement(self):  # pylint: disable = no-self-use
        raise AssertionError(
            "Please teach your children how to handle copyright statements")

    def _legacy_parent_id(self):
        self.gs4.legacyParentID = ('_').join([self.gs4.journalID, self.record.numeric_date])

    def _cover(self):
        # If the current document's filename ends '0001', treat it as the first
        # page of the issue, and set cover to True. Otherwise, cover is False.
        #if self._cfg['pruned_basename'].endswith('0001'):
        if self.gs4.originalCHLegacyID.endswith('0001'):
            self.gs4.cover = u'true'
        else:
            self.gs4.cover = u'false'

    def _setDates(self):
        # If the APS_date_8601 ends with '00', we need to do dates differently.
        if self.record.numeric_date.endswith('00'):
            if self.record.numeric_date.endswith('0000'):
                numeric_date = '%s0101' % self.record.numeric_date[0:4]
            else:
                numeric_date = '%s01' % self.record.numeric_date[0:6]
            self.gs4.normalisedAlphaNumericDate = dateUtils.DateConverter.USdate2pqan(numeric_date)
            self.gs4.numericStartDate = numeric_date
        else:
            super(APSMapping, self)._setDates()

    # --- computedValues

    # +++ helper methods

    def _buildLayoutInfo(self):
        layoutInfo = ''
        for page in self.record.pages:
            # page image names look like this:
            # APS_151436_19871001-001.jpg
            # We need to grab the final digit before the extension ([-5])
            # and see if it's odd or even. That'll tell us if we have a
            # recto page (odd) or a verso page (even)
            layoutInfo += (int(get_last_digit(os.path.splitext(page)[0])) & 1) and "R" or "V"
        return layoutInfo

    # --- helper methods

    # +++ after_hooks
    def _fill_in_blank_title(self):
        if self.gs4.title == '' or self.gs4.title is None:
            self.gs4.title = APStitle(self.xml)

    def _update_pagefiles(self):
        if 'skipms' in self._cfg['mappingOptions']:
            return
        else:
            pfh = PagefileHandler(
                self.xml, self._cfg['pruned_basename'], self.productId)

            try:
                pfh.update_or_create_pagefiles()
            except RescaleFactorUndefinedError:
                self.msq.append_to_message(
                    'No rescale factor for IDs (No pagefile generated)',
                    self.gs4.originalCHLegacyID)
                return
            except CorruptXMLError:
                self.msq.append_to_message(
                    'Corrupt XML - illegal characters in source file',
                    self.gs4.originalCHLegacyID)
                log.error(
                    'Corrupt XML - illegal characters in source file: %s',
                    self.gs4.originalCHLegacyID)
                raise SkipRecordException
            pfh.generate_hit_highlighting_tables()
