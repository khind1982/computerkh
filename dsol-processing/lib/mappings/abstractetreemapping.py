# -*- mode: python -*-

''' A parent class for mappings whose rawrecord members are lxml.etree
instances. This includes Vogue and EIMA. '''

import os
import sys
import re

from stat import ST_SIZE
from types import NoneType

from commonUtils.textUtils import xmlescape
from mappings.abstractmapping import AbstractMapping

img_attributes = [
        'keywords', 'imageCategory', 'color', 'designerBrand',
        'designerPerson', 'material', 'pictured', 'print', 'trend', 'tags']


class AbstractEtreeMapping(AbstractMapping):
    def __init__(self, rawrecord):
        super(AbstractEtreeMapping, self).__init__(rawrecord)

    @property
    def nsmap(self):
        try:
            return self._nsmap
        except AttributeError:
            return None

    @staticmethod
    def nameAttr(ary):
        # Takes a list and tries to split it into an xpath and
        # attribute name.  If that fails (because the list has only
        # one element), uses the list's sole value as the xpath and
        # takes from it the part after the final ':', '/', or '@'
        try:
            xpath, attribute = ary
        except ValueError:
            xpath = ary[0]
            attribute = re.split(':|/|@', xpath)[-1]
        return (xpath, attribute,)

    def getTextFromXML(self, xpath):
        # Only send back real values - drop empty values (i.e., those
        # that come out of xpath() as NoneType).
        return [xmlescape(unicode(elem.text)) for elem
                in self.xml.xpath(xpath, namespaces=self.nsmap)
                if type(elem.text) is not NoneType]

    def assignSimpleAttrs(self, attrs):
        for ary in attrs:
            elem, attr = self.nameAttr(ary)
            # We need to handle cases with attribute accesses differently to
            # plain element retrieval.
            # Grab the xpath data for the element.
            try:
                xpath_return = self.xml.xpath(
                    '//%s' % elem, namespaces=self.nsmap)[0]
            except IndexError:
                # Record has no element "elem". This is probably not a
                # fatal error, so continue.
                continue

            # If the value returned by the xpath expression is a string,
            # we had an attribute access and can use the string.
            if isinstance(xpath_return, basestring):
                value = xpath_return
            else:
                # Otherwise, we must explicitly retrieve the text.
                value = xpath_return.text

            # Don't set the attribute if its value is None. Doing so breaks
            # stuff and makes no sense anyway.
            if value is not None:
                setattr(self.record, attr, self.cleanAndEncode(value))

    def assignImages(self, XPath):
        self.record.images = []
        # Grab all the image sections from the source.
        for rawimage in self.xml.xpath(XPath, namespaces=self.nsmap):
            image = {}
            for ary in self.imageAttrs:
                elem, attribute = self.nameAttr(ary)
                value = []
                try:
                    # Limit the xpath operation to the scope of the
                    # current element.  We must use a relative xpath
                    # (omitting the leading '/')
                    xpath_return = rawimage.xpath(
                            './/%s' % elem, namespaces=self.nsmap)
                except IndexError:
                    print "continuing"
                    continue

                for xml_elem in xpath_return:
                    if self.isStringy(xml_elem):
                        value.append(xml_elem)
                    elif xml_elem.tag.endswith('imageCategory'):
                        value = xpath_return
                    else:
                        value.append(xml_elem.text)
                    if value != []:
                        for index, item in enumerate(value):
                            try:
                                value[index] = re.sub(
                                    self.char_replacements,
                                    self.replace_, self.cleanAndEncode(item))
                            except TypeError:
                                continue
                            except AttributeError:
                                continue
                        # These elements can occur an umlimited number of times
                        # We want to capture each instance in the data
                        if attribute in img_attributes:
                            image[attribute] = value
                        # This needs special handling
                        elif attribute == 'imageFeature':
                            image[attribute] = self.docFeatureName(value[0])

                        # Everything else may only occur a maximum of once,
                        # so we just need to grab the first element of the
                        # list in `value'.
                        else:
                            if value[0] is not None:
                                image[attribute] = value[0]
            self.record.images.append(image)

    def docFeatureName(self, name):
        # Takes a document feature string in Prism format and converts
        # it to GS format. Simply turns 'photo' into 'Photograph' and
        # fixes capitalisation on all other values passed in.
        if name.endswith('hoto'):  # Catches both 'photo' and 'Photo'
            return 'Photograph'
        else:
            return name.capitalize()

    # After hooks shared by Vogue and EIMA. If others need them, they should be
    # lifted up into AbstractMapping.
    def _fill_in_blank_title(self):
        if self.gs4.title == '' or self.gs4.title is None:
            self.gs4.title = '[untitled]'

    # Set up image level details.
    def _images(self):
        imageMapping = self.imageMapping
        self.gs4.images = []
        for idx, image in enumerate(self.record.images):
            imageInfo = {}
            imageInfo['ImageSequence'] = idx + 1
            for k, v in image.items():
                if not v == '':
                    try:
                        imageInfo[imageMapping[k]] = v
                    except KeyError:
                        imageInfo[k.capitalize()] = v
            self.gs4.images.append(imageInfo)

    def _get_page_count(self):
        return str(len(self.record.pages))

    def _page_count(self):
        ''' Only set pageCount if it's anything other than "0" '''
        pc = self._get_page_count()
        if pc == '0':
            return
        self.gs4.pageCount = pc

    #######
    # These used to live in vogueish.py, until I tried to refactor
    # _computedValues to hold either a string or a method reference,
    # as is done in the _dtable. It seems that having these tucked away
    # in a mixin module just doesn't work in Python - it is incapable of
    # properly extending the bse class with the functions in the mixin
    # module. Message to self: remember this is Python, not Ruby...
    def _resides(self):
        '''Checks the product code and returns an appropriate value for
        the Resides attribute. Necessary because of EIMA3 using the
        product code "eim"'''
        if self.productCode == 'EIM':
            return 'EIMA'
        return self.productCode

    def _components(self):
        # Code already exists to do Citation and Abstract, so let's use it.
        AbstractMapping._components(self)

        # The film products only need Citation and Abstract Components,
        # so we can return here to avoid building anything else.
        # if self.productId == 'film':
        #     return

        # This is where it gets a bit gnarly. Vogue Page Images have two
        # Representation Components, and a PageCount Component. I wanted to do
        # this in one method (well, one method here - I have had to add one to
        # the helper module as well...)
        # First off, the values hash that will go, unaltered, in both
        # Representations.
        baseValues = {
                u'MimeType': u'image/jpeg',
                u'Resides': u'CH/%s' % self._resides(),
                u'Color': u'color'}

        # These dicts represent the differences between the two types of
        # Representation
        normalValues = {u'MediaKey': unicode(  # noqa
            self._mediaKey(self.gs4.originalCHLegacyID, 'page')),
                         u'LayoutInfo': unicode(self._buildLayoutInfo())}
        thumbValues = {u'MediaKey': unicode(  # noqa
            self._mediaKey(self.gs4.originalCHLegacyID, 'thumb'))}

        # representations: dict holding all the different Representations
        # required by a Vogue record (PageCount, RepresentationTypes Normal and
        # Thumb. Insert PageCount as a simple dict - it needs no fancy
        # preprocessing.
        representations = {'MultipleComponents': []}

        if ('no_page_images' in self._cfg.keys() and
                self._cfg['no_page_images'] == 'true'):
            pass
        else:
            representations = {'MultipleComponents': [
                {u'PageCount': self._get_page_count()}]}

        # Now for each of the RepresentationTypes, make a copy of baseValues...
            for reprType in ['Normal', 'Thumb']:
                values = baseValues.copy()

            # and merge in the appropriate differences dict...
                values.update(eval("%sValues" % reprType.lower()))

            # use that updated values dict to create a new Representation
            # object suitable for the Helper module's consumption and append it
            # to the list keyed in representations by the string
            # 'MultipleComponents':
                representations['MultipleComponents'].append(
                    {u'Representation':
                        {u'RepresentationType': reprType,
                            'values': values}})

        # Now we have all our Representations in place, so can pass them off to
        # self._buildComponents - which seems to be completely redundant, but
        # would no doubt break stuff if I refactored it out...
            self.gs4.components.append(
                    self._buildComponent(u'Pages', representations))

            # A new type of Component that is required for the page navigation
            # views.
            # ## REMOVE THIS WHEN VIA PRODUCT CODE IS SET UP.
            # if self.productCode == "VIA":
            #     issueID = self.gs4.legacyParentID.replace(
            #         "VOGUE001", "VIA000001")
            # else:
            #     issueID = self.gs4.legacyParentID
            issueID = self.gs4.legacyParentID
            self.gs4.components.append(
                self._buildComponent(
                    u'IssueMedia', {
                        u'Representation': {
                            u'RepresentationType': u'PCMediaIndex',
                            'values': {
                                u'MimeType': u'application/xml',
                                u'Resides': u'CH/%s' % self._resides(),
                                u'MediaKey': self._mediaKey(
                                    issueID, 'pcmi')}}}))

        # And now the FullText Components and its Representations
        # (BackgroundFullText if TextInfo is defined on the the gs4 object) and
        # PDFFullText for each record.  Set this up as another
        # MultipleComponents Component, since we will always have a PDFFullText
        # Representation preceded by an optional BackgroundFullText
        # Representation within the same Component element.
        representations = {'MultipleComponents': []}

        # if self.gs4.hiddenText is defined, insert the BackgroundFullText
        # Representation.  This will always trigger, since we are inserting a
        # whitespace-only full text component in the event the source record
        # has no full text. See the implementation of _hiddenText in
        # voguemapping.py.
        if self.gs4.hiddenText:
            representations['MultipleComponents'].append(
                {u'CHImageIDs':
                 {'values':
                  {u'CHID': self.gs4.legacyID}}})

            representations['MultipleComponents'].append(
                {u'Representation':
                    {u'RepresentationType': 'BackgroundFullText',
                        'values': {
                            u'MimeType': u'text/xml',
                            u'Resides': u'FAST'}}})

        if self.gs4.fullText:
            representations['MultipleComponents'].append(
                {u'Representation':
                    {u'RepresentationType': 'FullText',
                        'values': {
                            u'MimeType': u'text/xml',
                            u'Resides': u'FAST'}}})

        # +++NOTE+++

        # We no longer want to display PDF links, so we're not generating them
        # in the data.  We DO want PDFs for Trench Journals, so enable it
        # conditionally, depending on the value of
        # self.pdf_representation_required (True or False)
        try:
            if self.pdf_representation_required:
                representations['MultipleComponents'].append(
                    {u'Representation':
                     {u'RepresentationType': 'PDFFullText',
                      'values': {u'MimeType': u'application/pdf',
                                 u'Resides': u'CH/%s' % self._resides(),
                                 u'Color': u'color',
                                 u'Options': u'PageRange',
                                 u'Bytes': self._pdfSizeEstimate(),
                                 u'Scanned': u'true',
                                 u'CHImageHitHighlighting': u'true',
                                 u'ImageType': u'JPEG',
                                 u'PDFType': u'300PDF',
                                 u'MediaKey': self._mediaKey(
                                     self.gs4.originalCHLegacyID, 'pdf')}}})
        except AttributeError:
            raise
            pass

        # Add accessible PDFs, if present
        if self.record.apdf_available == 'true':
            representations['MultipleComponents'].append(
                    {u'Representation':
                        {u'RepresentationType': 'PDFFullText',
                            'values': {
                                u'MimeType': u'application/pdf',
                                u'Resides': u'CH/%s' % self._resides(),
                                u'Color': u'color',
                                u'Bytes': self._apdf_size(
                                    self.gs4.originalCHLegacyID),
                                u'ImageType': u'PDF',
                                u'PDFType': 'APDF',
                                u'MediaKey': self._mediaKey(
                                    self.gs4.originalCHLegacyID, 'apdf'
                                    )}}})

        if len(representations['MultipleComponents']) > 0:
            self.gs4.components.append(
                self._buildComponent(u'FullText', representations))

    # --- computedValues

    def _objectIDs(self):
        self.gs4.objectIDs = []
        self.gs4.objectIDs.append({'value': self.gs4.legacyID,
                                   u'IDOrigin': u'CH',
                                   u'IDType': u'CHLegacyID'})
        self.gs4.objectIDs.append({'value': self.gs4.originalCHLegacyID,
                                   u'IDOrigin': u'CH',
                                   u'IDType': u'CHOriginalLegacyID'})

    def _mediaKey(self, legacyID, kind):
        if kind not in ['page', 'thumb', 'pdf', 'pcmi', 'apdf']:
            print >> sys.stderr, ("Invalid mediakey type: %s" % kind)
            sys.exit(1)
        if self._cfg['product'].startswith('bp'):
            prod_key = 'bpc'
        elif self._cfg['product'] == 'art':
            prod_key = 'aaa'
        elif self._cfg['product'] == 'eim':
            prod_key = 'eima'
        else:
            prod_key = self._cfg['product']
        mKeyRoot = '/media/ch/%s' % prod_key  # self._cfg['product']
        mKeyRoot = mKeyRoot + '/%s/%s/%s'
        if kind == 'pcmi':
            return mKeyRoot % (
                self.ms_page_collection_root, legacyID, 'mindex.xml')
        # PDFs have a slightly different specification:
        elif kind == 'pdf':
            return mKeyRoot % ('doc', legacyID, 'doc.pdf')
        elif kind == 'apdf':
            return mKeyRoot % ('doc', legacyID, 'ada.pdf')
        else:
            return mKeyRoot % ('doc', legacyID, kind + '/pg.jpg')

    def _apdf_size(self, legacyID):
        if os.environ.get('TESTING'):
            return '3.5'
        journalID = self.gs4.journalID
        issueID = self.gs4.legacyParentID
        if self.productCode == "EIM":
            dataset = "eima"
        else:
            dataset = self.productCode.lower()
        pdfpath = '/sd/web/images/%s/%s/%s/apdf/%s.pdf' % (
            dataset, journalID,
            issueID, self.legacyDocumentID)
        return str(os.stat(pdfpath)[ST_SIZE])
