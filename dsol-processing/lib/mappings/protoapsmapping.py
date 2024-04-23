# -*- mode: python -*-
'''A class inherited by both APSMapping and LeviathanMapping that
implements certain functionality required by both. Loaded as the
second parent class.

'''

import importlib
import os

from collections import OrderedDict
from stat import ST_SIZE

from commonUtils.fileUtils import buildLut
from cstoreerrors import SkipRecordException
from pagination import Pagination


class ProtoAPSMapping(object):
    '''A class containing methods common to both APS and Leviathan
    mappings. It is intended to be loaded as a mixin, not as a main
    part of the inheritance tree

    '''

    # pylint: disable = E1101
    def add_term(self, term):
        ''' Add the passed <term> to the list in self.gs4.terms, creating it
        first if not already defined.

        The <term> argument must include all relevant information to ensure
        the Term can be correctly constructed when the document output template
        is populated - term element name, the Term's value, any attributes and
        their values.
        '''
        try:
            self.gs4.terms.append(term)
        except AttributeError:
            self.gs4.terms = [term]

    def get_xpaths(self):
        '''Fetch the XPath statements from the config file named in
        self._cfg['xpaths'], or from aps.xpath if unspecified.

        '''
        if 'xpaths' not in self._cfg:
            self._cfg['xpaths'] = 'aps.xpath'
        return buildLut(self._cfg['xpaths'])

    def set_page_numbers(self):
        '''Calculate page numbers from data gathered from page zones. Grab
        the pagenumbers from the source and return them as a list.
        Pagination data can be encoded in a pagination element. If this is
        present in the current record, we'll use it and short-circuit the
        rest of the method.
        '''
        try:
            if self.xml.xpath(self.xpaths['pagination']):
                return [self.xml.xpath(self.xpaths['pagination'])[0].text]
        except KeyError:
            pass
        pages = OrderedDict()
        pagenumbers = []
        for zone in self.xml.xpath(self.xpaths['zone']):
            pages[int(zone.xpath(
                self.xpaths['page_sequence'])[0].text)] = zone.xpath(
                    self.xpaths['page_number'])[0].text
        for pagenum in pages.keys():
            pagenumbers.append(pages[pagenum])
        return pagenumbers

    def pagenumbers(self, data):
        '''Format page numbers so that runs of consecutive pages are
        represented as a hyphenated range. Non-consecutive runs are
        separated by a comma.

        '''
        try:
            self.gs4.startpage = self.helper_startPage(data[0])
        except IndexError:
            self.log.error("No pagination information in %s. Skipping record",
                           self._cfg['filename'])
            self.msq.append_to_message(
                "No pagination information for record (omitted from output)",
                self._cfg['filename'])
            raise SkipRecordException
        except TypeError:
            self.log.error(
                "There was a problem setting page numbers for %s. Skipping.",
                self._cfg['pruned_basename'])
            self.msq.append_to_message(
                "Could not set page numbers (check source file)",
                self._cfg['pruned_basename'])
            raise SkipRecordException
        self.gs4.pagination = unicode(
            Pagination(self.record.pagenumbers).formatted_string)

    def fetch_copyright_statements(self):
        try:
            return importlib.import_module(
                    'mappings.rules.copyrightstatements.%s' %
                    self._cfg['product']).cs
        except ImportError:
            print "No module specifying copyright statements for %s" % self._cfg['product']
            print "This needs to be added to ./lib/mappings/rules/copyrightstatements"
            exit(1)

    def _merge_dtables(self, other):
        # Merge a child class's _dtable into the parent.
        # If both the child and parent have the same key, the one
        # in the child's replaces the parent's.
        # pylint: disable = W0201
        self._dtable = dict(self._dtable.items() + other.items())

    @property
    def ms_page_collection_root(self):  # pylint: disable = R0201
        return 'pc'

    def _pdfSizeEstimate(self):
        ### REMOVE WHEN VIA PRODUCT IS SET UP  # noqa
        if self.productCode == 'VIA':
            journalID = 'VIA000001'
            issueID = self.gs4.legacyParentID.replace('VOGUE001', 'VIA000001')
        else:
            journalID = self.gs4.journalID
            issueID = self.gs4.legacyParentID
        if self.productCode == "EIMA":
            issueID = "APS_%s" % issueID

        if self.productCode == "EIM":
            dataset = "eima"
        else:
            dataset = self.productCode.lower()

        imagepath = '/sd/web/images/%s/%s/%s/jpeg/' % (
            dataset, journalID,
            issueID)
        pdfSize = 0
        if os.environ.get('TESTING'):
            return '3'
        for page in self.record.pages:
            try:
                pdfSize += os.stat(
                        imagepath + page.replace('jp2', 'jpg'))[ST_SIZE]
            except OSError as e:
                if e.errno == 2:
                    self.log.error(
                        """Image file %s does not exist.
                         %s will not be in the final output""",
                        e.filename, self._cfg['pruned_basename'])
                    self.msq.append_to_message(
                        "Error calculating PDF size(%s) - records skipped" %
                        e.message,
                        self._cfg['pruned_basename']
                    )
                    raise SkipRecordException
        return str(int(pdfSize * 1.1))

    def assign_company_and_brand(self):
        company_terms = []
        brands = []
        for company in self.xml.xpath(
                self.xpaths['company'], namespaces=self.nsmap):
            try:
                company_terms.append(self.cleanAndEncode(company.text))
            except TypeError:
                self.msq.append_to_message(
                    "Empty %s element (non fatal)",
                    (self.xpaths['company'], self._cfg['basename']))
                self.log.warning(  # pylint: disable = E0602
                    "(non fatal) Empty %s element in %s",
                    self.xpaths['company'], self._cfg['basename'])
        if len(company_terms) > 0:
            self.record.company_terms = company_terms

        for brand in self.xml.xpath(
                self.xpaths['product'], namespaces=self.nsmap):
            try:
                brands.append(self.cleanAndEncode(brand.text))
            except TypeError:
                self.msq.append_to_message(
                    "Empty %s element (non fatal)",
                    (self.xpaths['product'], self._cfg['basename']))
                self.log.warning(  # pylint: disable = E0602
                    "(non fatal) Empty %s element in %s",
                    self.xpaths['product'], self._cfg['basename'])
        if len(brands) > 0:
            self.record.brands = brands

    def _company_and_brand_terms(self):
        # for company in self.record.company_terms:
        #     self.add_term(
        #             {u'TermType': u'CompanyTerm',
        #              u'values': {u'CompanyName': company}})

        for brand in self.record.brands:
            self.add_term(
                {u'TermType': u'Term',
                 u'attrs': {u'TermType': u'Product'},
                 u'values': {u'TermValue': brand}})
