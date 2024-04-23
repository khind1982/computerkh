# -*- mode: python -*-

import re

from commonUtils.dateUtils import numeric_to_alpha_date
from cstoreerrors import SkipRecordException
from datetool.dateparser import parser as dateparser
from mappings.apsmapping import APSMapping
from mappings.rules.APSRules import pmid as APSpmid

import logging
log = logging.getLogger('tr.mapping.wwd')

class WWDMapping(APSMapping):

    _copyright_statements = {}
    __imageAttrs = (
        ['APS_zone_credit',     'credit'],
        ['APS_zone_pagenumber', 'pageref'],
        ['APS_zone_imagetype',  'imageFeature'],
        ['APS_zone_caption',    'caption'],
        ['APS_image_caption',   'caption'],
        )

    __imageMapping = {
        'credit':        'Credits',
        'pageref':       'ImageStartPage',
        'imageFeature':  'ImageCategory',
        }

    # Document Type mappings.
    __documentTypes = {
        'aaa': [
            'Advertisement',
            'Article',
            'Back Matter',
            'Correspondence',
            'Editorial Cartoon/Comic',
            'Front Page',
            'Image/Photograph',
            'Illustration',
            'News',
            'Obituary',
            'Poem',
            'Recipe',
            'Review',
            'Statistics/Data Report',
            'Table of Contents',
            'Undefined',
            ],
        'trj': [
            'Ad',
            'Article',
            'Back matter',
            'Comic',
            'Cover',
            'Drama',
            'Editorial cartoon',
            'Fiction/Narrative',
            'Front matter',
            'Illustration',
            'Letter',
            'Obituary',
            'Other',
            'Photograph',
            'Poem',
            'Recipe',
            'Review',
            'Statistics',
            'Tbl of contents',
            ],
        'wwd': [
            'Accessories',
            'Advertisement',
            'Arts and Culture',
            'Beauty',
            'Business',
            'Correspondence',
            'Eye',
            'Fashion',
            'Front Page',
            'Media',
            'Obituary',
            'Retail',
            'Runway',
            'Table Of Contents',
            'Undefined',
            ],
        }

    def __init__(self, rawrecord):
        super(self.__class__, self).__init__(rawrecord)

        # product-specific modifications to the dispatch table.
        _local_dtables = {
            'wwd': {'abstract':    self.__class__.abstract,
                    'brands':       self.__class__.noop,
                    'company_terms': self.__class__.noop,
                    'images':      self.__class__.noop,
                    'pmid':        self.__class__.journalID,
                    'subheadings': self.__class__.subheading,
                    'supplement':  self.__class__.supplement,
                    },
            'aaa': {'abstract':    self.__class__.noop,
                    'brands':       self.__class__.noop,
                    'companyterms': self.__class__.noop,
                    'images':      self.__class__.noop,
                    'pmid':        self.__class__.journalID,
                    'subheadings': self.__class__.subheading,
                    'supplement':  self.__class__.supplement,
                    'volume':      self.__class__.volume,
                    },
            'trj': {'abstract':           self.__class__.abstract,
                    'images':             self.__class__.noop,
                    'pmid':               self.__class__.journalID,
                    'source_institution': self.__class__.source_institution,
                    'subheadings':        self.__class__.subheading,
                    },
            }
        # Merge our local dtable into the inherited one.
        self._merge_dtables(_local_dtables[self.productId])

        # WWD specific additions to the list of computed values
        self._computedValues.append(self.__class__._company_and_brand_terms)   # pylint: disable = W0212
        self._computedValues.append(self.__class__._images)  # pylint: disable = W0212
        self._computedValues.append(self.__class__._page_count)  # pylint: disable = W0212

        self.assignSubHeadings()
        self.assign_company_and_brand()

        self.imageMapping = self.__imageMapping
        self.imageAttrs = self.__imageAttrs

        self.assignImages('//APS_zone[@type="image"]')

        self.documentTypes = self.__documentTypes[self._cfg['product']]

        # Setup specific to Trench Journals
        if self.productId == 'trj':
            # A mapping of the short forms from the vendor to the full
            # source institution names stored in TRACS
            self.source_institutions = {
                'BL':  'British Library',
                'IWM': 'Imperial War Museum',
                'LOC': 'Library of Congress',
                'MEPL': 'Mary Evans Picture Library',
                'SBB': 'Staatsbibliothek zu Berlin',
                }

            # Trench Journals has a requirement to provide downloadable PDFs,
            # so we some way of triggering the creation of the appropriate
            # Component & Representation in the method _components in
            # AbstractEtreeMapping.
            self.pdf_representation_required = True

            # We need to include Abstract for Trench Journals, but
            # abstract information is captured in
            # .//APS_abstract/APS_para. Extract the content of
            # APS_para elements and put it all in self.record.abstract
            abstract = ' '.join([para.text for para in self.xml.findall('.//APS_abstract/APS_para')])
            if abstract is not '':
                self.record.abstract = abstract

            # Fix the article type for the document.
            self.record.article_type = self.record.article_type.replace('_', ' ')
            if self.record.article_type == 'Fiction':
                self.record.article_type = 'Fiction/Narrative'

    def assignSubHeadings(self):
        subheadings = []
        for subhead in self.xml.xpath('//APS_subhead', namespaces=self.nsmap):
            try:
                subheadings.append(self.cleanAndEncode(subhead.text))
            except TypeError:
                self.msq.append_to_message("Empty APS_subhead element (non fatal)", self._cfg['basename'])
                log.warning("(non fatal) Empty APS_subhead element in %s", self._cfg['basename'])
        if len(subheadings) > 0:
            self.record.subheadings = subheadings

    @property
    def pmid(self):
        while True:
            try:
                return self._pmid
            except AttributeError:
                setattr(self, '_pmid', APSpmid(self._cfg['product'], self.xml))


    # WWD and AAA have different requirements for the
    # copyright statements.
    def _copyright_statement(self):
        getattr(self, '_copyright_%s' % self._cfg['product'])()

    def _copyright_aaa(self):
        try:
            self.gs4.copyrightData = self.cleanAndEncode(
                self.copyright_statements[self.gs4.journalID]
            )
        except KeyError:
            log.error(
                '%s: No copyright statement for %s. Skipping record.',
                self.gs4.originalCHLegacyID, self.gs4.journalID
            )
            self.msq.append_to_message(
                'No copyright statement (records omitted)', self.gs4.journalID
            )
            raise SkipRecordException(
                'No copyright statement for %s' % self.gs4.journalID
            )

    def _copyright_trj(self):
        try:
            self.gs4.copyrightData = self.copyright_statements[self.record.source_institution]
        except KeyError:
            log.error("No source institution found in %s. Record skipped.", self.gs4.originalCHLegacyID)
            self.msq.append_to_message("No source institution in record", self.gs4.originalCHLegacyID)
            raise SkipRecordException

    def _copyright_wwd(self):
        self.gs4.copyrightData = self.copyright_statements

    def _legacy_parent_id(self):
        if self._cfg['product'] == 'wwd':
            self.gs4.legacyParentID = '_'.join(self._cfg['pruned_basename'].split('_')[0:3])
        else:
            super(self.__class__, self)._legacy_parent_id()

    def _images(self):
        # In WWD at least, we don't want to include any ImageInfo
        # for documents identified as adverts.
        if 'Advertisement' in self.gs4.searchObjectType:
            return
        super(self.__class__, self)._images()

    def _terms(self):
        for companyterm in self.record.companyterms:
            self.add_term({u'TermType': u'CompanyTerm',
                 u'values': {
                     u'CompanyName': self.cleanAndEncode(
                         companyterm, escape=True)}})

        for brand in self.record.brands:
            self.add_term({u'TermType': u'Term',
                 u'attrs': {u'TermType': u'Product'},
                 u'values': {u'TermValue': self.cleanAndEncode(brand)}})

    def _setDates(self):
        if self.productId == 'trj':
            if self.record.numeric_date == '00010101':
                self.gs4.undated = True
            parsed_date = dateparser.parse(self.record.numeric_date).start_date
        elif self.gs4.journalID == 'AAA133979':
            self.gs4.numericStartDate = self.record.numeric_date
            return
        elif self.gs4.rawPubDate:
            rawdate = re.sub(r',$', '', self.gs4.rawPubDate)
            try:
                parsed_date = dateparser.parse(rawdate).start_date
            except AttributeError as e:
                log.error("Unhandled date format in %s (%s)",
                          self._cfg['filename'], self.gs4.rawPubDate)
                self.msq.append_to_message(
                    "Unhandled date",
                    "%s: %s" % (self._cfg['pruned_basename'], rawdate)
                )
                raise SkipRecordException
        else:
            log.warn(
                "%s has no printed_date. Using the numeric date (%s) instead",
                self._cfg['filename'], self.record.numeric_date)
            self.msq.append_to_message(
                "No printed_date in file (using numeric date instead)",
                self._cfg['pruned_basename']
            )
            parsed_date = dateparser.parse(self.record.numeric_date).start_date

        try:
            self.gs4.normalisedAlphaNumericDate = parsed_date.normalised_alnum_date
        except:
            print self.gs4.legacyID
            print parsed_date.normalised_numeric_date
            exit()
        self.gs4.numericStartDate = parsed_date.normalised_numeric_date


        # if self.productId == 'trj':
        #     self.gs4.numericStartDate = self.record.numeric_date
        #     if self.gs4.numericStartDate == '00010101':
        #         self.gs4.undated = True
        #     print self.record.printed_date
        #     self.gs4.normalisedAlphaNumericDate = dateparser.parse(
        #         self.gs4.numericStartDate).start_date.normalised_alnum_date
        #     #numeric_to_alpha_date(self.gs4.numericStartDate)
        # else:
        #     parsed_date = dateparser.parse(self.gs4.rawPubDate).start_date
        #     self.gs4.normalisedAlphaNumericDate = parsed_date.normalised_alnum_date
        #     self.gs4.numericStartDate = parsed_date.normalised_numeric_date
        #     #super(WWDMapping, self)._setDates()

    # def _pdfSizeEstimate(self):
    #     imagepath = '/sd/web/images/%s/%s/%s/jpeg/' % (self.productId, self.gs4.journalID, self.gs4.legacyParentID)
    #     pdfSize = 0
    #     for page in self.record.pages:
    #         try:
    #             pdfSize += os.stat(imagepath + page)[ST_SIZE]
    #         except OSError:
    #             pass
    #     return str(int(pdfSize * 1.1))

    def supplement(self, data):
        self.gs4.parentInfoSupplement = self.cleanAndEncode(data)

    def subheading(self, data):
        self.gs4.subtitle = self.cleanAndEncode(data[0])

    def abstract(self, data):
        self.gs4.abstract = self._abstract(data, "Summary")

    def searchObjectType(self, data):
        if data in self.documentTypes:
            self.gs4.searchObjectType = [data]
        else:
            log.warning("Unknown document type %s in %s. Skipping record", data, self._cfg['pruned_basename'])
            raise SkipRecordException


    def source_institution(self, data):
        self.gs4.brandingInstitution = self.source_institutions[data]

    # journalID needs to go through the normalisation code to ensure
    # it starts with the right sequence of letters to denote the
    # current product.
    def journalID(self, data):
        data = self.pmid
        super(self.__class__, self).journalID(data)

    def volume(self, data):
        if self.pmid == 'AAA125850':
            pass
        else:
            super(self.__class__, self).volume(data)
