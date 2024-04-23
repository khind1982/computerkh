# -*- mode: python -*-
# pylint:disable=W0612,C0301

import os, re

from stat import ST_SIZE

from commonUtils import dateUtils, langUtils
from commonUtils.listUtils import uniq  #, uniq_sort
from mappings.abstractetreemapping import AbstractEtreeMapping

from commonUtils.fileUtils import buildLut  #pylint:disable=F0401

from extensions.total_ordering import total_ordering

import logging
log = logging.getLogger('tr.mapping.vogue')

class VogueMapping(AbstractEtreeMapping):

    # a nested class to sort page image names correctly. For most cases,
    # this is simply a matter of sorting the page image names alphanumerically,
    # but this won't work for pages with foldouts - the numbers after the 'r' and
    # 'v' that indicate recto/verso are significant.
    # The approach is quite crude - if there are digits after the r/v indicator,
    # we reassemble the imagename so that those numbers appear before the r/v
    # indicator, and then sort the names. Seems to work, but needs testing in
    # preprod before we apply it to the whole data set.
    # The @total_ordering decorator was taken from ASPN, and provides the full
    # set of rich comparison operators, provided the decorated class implements
    # at least one of them, usually __lt__. This allows us to sort instances of
    # the class.
    @total_ordering
    class ImagePageName(object):
        def __init__(self, imagename):
            self.imagename = imagename
            if re.search(r'.*_[rv]_[0-9]+', self.imagename):
                name_parts = re.search(r'(.*)_([rv])_([0-9]+)', self.imagename).groups()
                self.sortable_name = '_'.join([name_parts[0], name_parts[2], name_parts[1]])
            else:
                self.sortable_name = self.imagename

        def __lt__(self, other):
            return self.sortable_name < other.sortable_name

    # These two tuples hold arrays of XPath and optional attribute name,
    # used within __init__() to populate the self.record object from the
    # rawrecord passed in from the stream.

    # The first is for simple attrs that occur only once within a Vogue
    # record.
    __simpleAttrs = (
        ['head/cnp:adCategory'],
        ['head/pam:media/cnp:pictured'],
        ['head/cnp:pictured'],
        ['pam:status'],
        ['pam:article/@xml:lang', 'rawLang'],
        ['dc:identifier'],
        ['x:head/prism:issueIdentifier'],
        ['dc:title'],
        ['pq:subtitle'],
        ['prism:coverDate'],
        ['prism:coverDisplayDate'],
        ['prism:volume'],
        ['prism:issueName'],
        ['prism:number'],
        ['prism:startingPage'],
        ['prism:pageRange'],
        ['pq:editor'],
        ['prism:section'],
        ['prism:subsection'],
        ['prism:genre'],
        ['prism:object'],
        ['prism:copyright'],
        ['cnp:abstract'],
        )

    # The second is for images, which have a nested structure. Each of the
    # elements here occurs once in each image in a record.
    __imageAttrs = (
        # These need to be anchored relative to //pam:article/body/pam:article,
        # NOT to the root element.
        ['dc:type', 'imageFeature'],
        ['pam:mediaReference/@pq:pageRef'],
        ['pam:credit'],
        ['pam:caption'],
        ['pam:textDescription'],
        ['pur:rightsOwner'],
        ['cnp:pictured'],
        ['cnp:keywords'],
        ['cnp:designerBrand'],
        ['cnp:designerPerson'],
        ['cnp:material'],
        ['cnp:trend'],
        ['cnp:color'],
        ['cnp:print', 'printTerm'], # To avoid the obvious name clash...
        ['cnp:imageCreator'],
        ['cnp:tags'],  # non-hierarchical tags
        ['cnp:imageCategory'],  # Deep indexing hierarchy top level.
        )

    # Mapping of imageAttrs to the ImageInfo elements used in the GS4 output
    # Only those that can't be derived by capitalising the __imageAttr key are
    # included here.
    __imageMapping = {
        'credit':          'Credits',
        'designerBrand':   'DesignerBrand',
        'designerPerson':  'DesignerPerson',
        'imageFeature':    'ImageCategory', #Feature',
        'keywords':        'ImageKeyword',
        'pageRef':         'ImageStartPage',
#        'pictured':        'PersonPictured',
        'printTerm':       'Print',
        'rightsOwner':     'Copyright',
        'textDescription': 'Description',
        'imageCreator':    'ImageCreator',
        'tags':            'ImageTag',
        'imageCategory':   'ImageKeywords',
        }

    # A dict containing the namespace mappings used in the Vogue/apex
    # source data.
    _nsmap = buildLut('mstar/vogue_xml_namespaces.lut', delimiter='|')
    
    __unicode_replacements = {
        u'\u201C': '"',
        u'\u201D': '"',
        u'\u201E': '',
        }

    # This is to help clean up unicode in the data.
    char_replacements = re.compile(u'(%s)' % ('|').join(__unicode_replacements.keys()))


    def __init__(self, rawrecord):
        super(VogueMapping, self).__init__(rawrecord)
        simpleAttrs = self.__simpleAttrs

        log.debug("starting file %s", self._srcFile)

        self.xml = self.rawrecord.data

        # The Vogue media services page collection data is rooted at
        # /media/ch/vogue/issue. /media/ch is (at the moment) immutable.
        # vogue is detected from the data, but the final part differs between
        # products, hence the need to set it explicitly here.
        # This variable is used in _components in voguish.py.
        self.ms_page_collection_root = 'issue'

        # +++ populate self.record

        # Extract data from self.rawrecord and populate self.record
        # These are simple string values:
        self.assignSimpleAttrs(simpleAttrs)

        # These are a little more tricky - there are multiple instances of these on each record,
        # so they cannot be handled as simple attributes.
        self.record.keywords = self.getTextFromXML('//x:head/cnp:keyword')
        self.record.docFeatures = uniq([self.docFeatureName(df) for df in self.getTextFromXML('//x:body//dc:type')])

        # These two, creators and contributors, go into Contributors
        self.record.creators = []
        for creator in self.getTextFromXML('//dc:creator'):
            for name in creator.split(';'):
                self.record.creators.append(name)

        self.record.contributors = []
        for contributor in self.getTextFromXML('//dc:contributor'):
            for name in contributor.split(';'):
                self.record.contributors.append(name)

        # HiddenText is messy and needs special handling
        self.record.hiddenText = [self.cleanAndEncode(re.sub(self.char_replacements, self.replace_, line)) for
                                  line in self.getTextFromXML('//x:body//x:p')]

        # Images
        self.assignImages()

        # Get the page image filenames from the pagemap section
        #self.record.pages = uniq_sort([image for image in self.xml.xpath('//x:pagemap/x:page/@image', namespaces=self.nsmap)])
        pages = uniq([self.ImagePageName(image) for image in self.xml.xpath('//x:pagemap/x:page/@image', namespaces=self.nsmap)])
        self.record.pages = [page.imagename for page in sorted(pages)]
        #self.record.pages = uniq_sort([self.ImagePageName(image) for image in self.xml.xpath('//x:pagemap/x:page/@image', namespaces=self.nsmap)])
        #print self.record.pages

        # Collect values from all instances of prism:industry, removing duplicates.
        self.record.industry = uniq(self.getTextFromXML('//prism:industry'))

        # TEST - we need to get a sequence number to aid in sorting in the views
        self.gs4.seq = self.gs4.genericData = self.xml.xpath('//x:page/@seq', namespaces=self.nsmap)[0]

        # --- populate self.record

        self._dtable = {
            'abstract':         VogueMapping.abstract,
            'adCategory':       'None of these seen in the data we have.',
            'contributors':     VogueMapping.noop,  # Contributors
            'copyright':        VogueMapping.copyright,
            'coverDate':        VogueMapping.numericPubDate,
            'coverDisplayDate': VogueMapping.rawPubDate,
            'creators':         VogueMapping.noop,  # Contributors
            'docFeatures':      VogueMapping.noop,  # Computed value - dc:type
            'editor':           VogueMapping.noop,  # Contributors
            'genre':            VogueMapping.genre,
            'hiddenText':       VogueMapping.noop,  # Computed value
            'identifier':       VogueMapping.legacyID,
            'images':           VogueMapping.noop,  # Computed value
            'industry':         VogueMapping.noop,  # Terms
            'issueIdentifier':  VogueMapping.nonStandardCitation,
            'issueName':        VogueMapping.noop,  # parentTitle, - needs to be "Vogue" or prepended with "Vogue - "
            'keywords':         VogueMapping.noop,  # Terms - GenSubjTerm
            'number':           VogueMapping.issue, # parentIssue,
            'object':           VogueMapping.noop,  # Term
            'pageRange':        VogueMapping.pagination,
            'pages':            VogueMapping.noop,  # Computed value - pagemap.
            'pictured':         VogueMapping.noop,  # Term - person pictured (in advertisements)
            'rawLang':          VogueMapping.language,
            'section':          VogueMapping.docSection,
            'startingPage':     VogueMapping.startpage,
            'status':           VogueMapping.action,
            'subsection':       VogueMapping.docSubSection,
            'title':            VogueMapping.title,
            'volume':           VogueMapping.volume,
            }

        self._computedValues = [
            VogueMapping._objectIDs,
            VogueMapping._docFeatures,
            VogueMapping._legacyPubID,
            VogueMapping._legacyParentID,
            VogueMapping._parentTitle,
            VogueMapping._lastUpdateTime,
            VogueMapping._terms,
            VogueMapping._buildContributors,
            VogueMapping._hiddenText,
            VogueMapping._components,
            VogueMapping._cover,  # Is the page in question an issue cover?
            VogueMapping._images, # The photos in an article
            VogueMapping._page_count,
            ]

        self._after_hooks = [
            VogueMapping._fill_in_blank_title, # Ensure no Title element goes
                                               # through empty
            ]

        # In order to correctly handle two Representations per
        # Component.
        self._componentTypes['MultipleComponents'] = VogueMapping._buildMultipleComponents

    @property
    def productCode(self):
        return self.get_product_code(lambda s: s.capitalize())

    # ++ helpers used in __init__()

    def docFeatureName(self, name):
        # Takes a document feature string in Prism format and converts
        # it to GS format. Simply turns 'photo' into 'Photograph' and
        # fixes capitalisation on all other values passed in.
        if name.endswith('hoto'): # Catches both 'photo' and 'Photo'
            return 'Photograph'
        else:
            return name.capitalize()

    # This function is passed in to various calls to re.sub. It's just
    # a simple dict lookup, which returns the value corresponding to
    # the key in mathcobj from the __unicode_replacements dict,
    # defined above.
    @staticmethod
    def replace_(matchobj):
        return VogueMapping.__unicode_replacements[matchobj.group(0)]

    def assignImages(self):
        self.record.images = []
        # Grab all the image sections from the source.
        for rawimage in self.xml.xpath('//pam:media', namespaces=self.nsmap):
            image = {}
            for ary in self.__imageAttrs:
                elem, attribute = self.nameAttr(ary)
                value = []
                try:
                    # Limit the xpath operation to the scope of the
                    # current element.  We must use a relative xpath
                    # (omitting the leading '/')
                    xpath_return = rawimage.xpath('%s' % elem, namespaces=self.nsmap)  #[0]
                except IndexError:
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
                                value[index] = re.sub(self.char_replacements, self.replace_, self.cleanAndEncode(item))
                            except TypeError:
                                continue
                        # These elements can occur an umlimited number of times.
                        # We want to capture each instance in the data.
                        if attribute in '''keywords imageCategory color designerBrand designerPerson material pictured print trend tags'''.split():
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

    # -- helpers

    # ++ computedValues

    def _objectIDs(self):
        # Item 10 in mapping doc - ObjSeqNum - need to keep track of
        # position in issue.
        self.gs4.objectIDs = []
        self.gs4.objectIDs.append({'value':     self.gs4.legacyID,
                                   u'IDOrigin': u'CH',
                                   u'IDType':   u'CHLegacyID'})
        self.gs4.objectIDs.append({'value':     self.gs4.originalCHLegacyID,
                                   u'IDOrigin': u'CH',
                                   u'IDType':   u'CHOriginalLegacyID'})

    def _docFeatures(self):
        self.gs4.docFeatures = self.record.docFeatures

    def _legacyPubID(self):
        self.gs4.journalID = u'VOGUE001'

    def _legacyParentID(self):
        # This is set to the same value as self.gs4.numericStartDate,
        # which is the first 8 digits of the article ID. It is used as
        # the group LegacyID (that is, an issue level identifier).
        # This is needed to allow us to render ParentInfo/Title only
        # for those issues that have an issue level title.
        self.gs4.legacyParentID = self.gs4.numericStartDate

    def _parentTitle(self):
        # If an issue has an issue title, include it.  Previously,
        # this field was always rendered, even for issues without an
        # issue title (these would render as "Vogue", which was raised
        # as a bug.)  This new approach requires that we have a
        # ParentInfo/LegacyID corresponding to the issue as well.
        if getattr(self.record, 'issueName'):
            self.gs4.pubTitle = getattr(self.record, 'issueName')

    def _lastUpdateTime(self):
        self.gs4.lastUpdateTime = unicode(dateUtils.fourteenDigitDate())

    def _terms(self):
        self.gs4.terms = []

        for term in self.record.industry:
            self.gs4.terms.append(
                self._build_term(
                    termtype='CompanyTerm',
                    termvalue=self.cleanAndEncode(term, escape=True)
                )
            )
            # self.gs4.terms.append({u'TermType': u'CompanyTerm',
            #                        u'values': {u'CompanyName': self.cleanAndEncode(term, escape=True)}})

        if getattr(self.record, 'object'):
            self.gs4.terms.append(
                self._build_term(
                    termtype='Term',
                    termattr='Product',
                    termvalue=self.cleanAndEncode(getattr(self.record, 'object'))
                )
            )
            # self.gs4.terms.append({u'TermType': u'Term',
            #                        u'attrs': {u'TermType': u'Product'},
            #                        u'values': {u'TermValue': self.cleanAndEncode(getattr(self.record, 'object'))}})

        if getattr(self.record, 'pictured'):
            self.gs4.terms.append(
                self._build_term(
                    termtype='Term',
                    termvalue=self.cleanAndEncode(getattr(self.record, 'pictured')),
                    termattr='Personal'
                )
            )
            # self.gs4.terms.append({u'TermType': u'Term',
            #                        u'attrs': {u'TermType': u'Personal'},
            #                        u'values': {u'TermValue': self.cleanAndEncode(getattr(self.record, 'pictured'))}})

        if getattr(self.record, 'keywords'):
            for keyword in self.record.keywords:
                self.gs4.terms.append(
                    self._build_term(
                        termtype='GenSubjTerm',
                        termvalue=self.cleanAndEncode(keyword)
                    )
                )
                # self.gs4.terms.append({u'TermType': u'GenSubjTerm',
                #                        u'values': {u'GenSubjValue': self.cleanAndEncode(keyword)}})

    def _buildContributors(self):
        contributors = []
        cumulativeIndex = 0
        if self.record.creators:
            for index, creator in enumerate(self.record.creators):
                if index == 0:
                    contribrole = u'Author'
                else:
                    contribrole = u'CoAuth'
                contributors.append({u'ContributorRole': contribrole,
                                     u'ContribOrder': unicode(index + 1),
                                     'contribvalue': self.cleanAndEncode(creator)})
                cumulativeIndex = index + 1
        if self.record.contributors:
            for index, contributor in enumerate(self.record.contributors):
                contributors.append({u'ContributorRole': u'SectionEditor',
                                     u'ContribOrder': unicode(cumulativeIndex + index + 1),
                                     'contribvalue': self.cleanAndEncode(contributor)})
                cumulativeIndex += 1
        if self.record.editor:
            contributors.append({u'ContributorRole': u'Editor',
                                 u'ContribOrder': unicode(cumulativeIndex + 1),
                                 'contribvalue': self.cleanAndEncode(self.record.editor)})
        self.gs4.contributors = contributors

    def _hiddenText(self):
        self.gs4.hiddenText = self.record.hiddenText
        # If hiddenText is empty, insert a fake one. This is necessary
        # because the webapp expects all records in Vogue to have full
        # text. Inserting a fake one here ensures that all the
        # required Component and Representation elements are added to
        # the rendered output.
        if len(self.gs4.hiddenText) is 0:
            self.gs4.hiddenText = ['  ']
            log.warning("Apex record has no full text: %s in file %s", self.gs4.originalCHLegacyID, self._srcFile)

#     def _components(self):
# MOVED to mixinmodules/vogueish.py

    def _cover(self):
        # Check for both "cover" and "Cover"
        try:
            matches = [elem for elem in self.gs4.searchObjectType if re.match('[Cc]over', elem)]
        except Exception as e:
            print e
            raise
        if len(matches) > 0:
            self.gs4.cover = u'true'
        else:
            self.gs4.cover = u'false'

    def _images(self):
        imageMapping = self.__imageMapping
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

    # ++ meta

#     def _buildLayoutInfo(self):
#     def _mediaKey(self, legacyID, kind):
# BOTH MOVED to mixinmodules/vogueish.py

    def _pdfSizeEstimate(self):
        jpegPath = "/dc/vogue-images/%s/%s/jpeg/" % (self._yearAndMonthFromNumericStartDate())
        pdfSize = 0
        for page in self.record.pages:
            try:
                pdfSize += os.stat(jpegPath + page)[ST_SIZE]
            except OSError:
                # In cases where we don't yet have the image file...
                pass
        return str(int(pdfSize * 1.1))

    def _yearAndMonthFromNumericStartDate(self):
        return tuple([self._fetchYear(), self._fetchMonth()])

    def _fetchSlice(self, string, start, stop, step=1):
        return ('').join(list(string)[start:stop:step])

    def _fetchYear(self):
        return self._fetchSlice(self.gs4.numericStartDate, 0, 4)
    def _fetchMonth(self):
        return self._fetchSlice(self.gs4.numericStartDate, 4, 6)

    # -- computedValues

    # ++ _after_hook methods
    #
    # These must be registered in self._after_hooks within the body of
    # the __init__() method.

    # -- _after_hook methods

    # ++ _after_hooks_always_run methods
    # None specific to Vogue.
    # -- _after_hooks_always_run

    ###################################################################

    def action(self, data):
        ''' Row 1 - ActionCode '''
        if data == 'A':
            self.gs4.action = u'add'
        elif data == 'C' or data == 'U':
            self.gs4.action = u'change'

    def language(self, data):
        ''' Row 8 - RawLang. For the moment, all articles have "en-US"
        as their language specification.  This may, of course,
        change... '''
        self.gs4.languageData = langUtils.lang_iso_codes(['English'])

    def legacyID(self, data):
        ''' Row 9 - Identifier '''
        self.gs4.legacyID = self._prefixedLegacyId(data)
        self.gs4.originalCHLegacyID = data
        self.setLegacyDocumentID(data)

    def nonStandardCitation(self, data):
        # if the source data contains the string "9999", ignore it and
        # don't include it in the output - it is an error in Apex's
        # manufacturing process. In future data handovers, it should
        # be fixed so we may be able to remove this again.
        if not data == '9999':
            super(VogueMapping, self).nonStandardCitation(data)

    def copyright(self, data):
        self.gs4.copyrightData = self.cleanAndEncode(data)

    def numericPubDate(self, data):
        self.gs4.numericStartDate = re.sub(r'-', '', data)

    def rawPubDate(self, data):
        self.gs4.rawPubDate = data
        self.gs4.normalisedAlphaNumericDate = dateUtils.normaliseDate(
            self.gs4.rawPubDate.title())

    def parentTitle(self, data):
        # This is used to insert the issue title in
        # //ParentInfo/Title. Since the whole collection is a single
        # publication, this is presumably safe...
        #
        # After some discussion, we have decided to put "Vogue" in
        # where there is no title, and to prepend existing titles with
        # "Vogue - ". A smelly hack, but consistent with previous data
        # sets.
        #
        # This method is now no longer in use - it has been replaced
        # with a _computedValue method instead.
        self.gs4.pubTitle = self.cleanAndEncode(data)

    def parentIssue(self, data):
        pass

    def abstract(self, data):
        self.gs4.abstract = self._abstract(data, 'Summary')

    def genre(self, data):
        self.gs4.searchObjectType = [self.cleanAndEncode(data)]
        self.gs4.searchObjectTypeOrigin = u'PRISM'

    def docSection(self, data):
        self.gs4.docSection = self.cleanAndEncode(data)

    def docSubSection(self, data):
        pass

    def _buildLayoutInfo(self):
        layoutInfo = ''
        basere = r'Vogue_[0-9_]*(%s)[0-9_-]*.jpg'
        recto = re.compile(basere % 'r')
        verso = re.compile(basere % 'v')
        for page in self.record.pages:
            if recto.match(page):
                layoutInfo += 'R'
            elif verso.match(page):
                layoutInfo += 'V'
        return layoutInfo
