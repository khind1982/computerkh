# -*- mode: python -*-
# pylint: disable = C0111, no-member
# pylint: disable = invalid-name

import datetime
import logging
import re

from collections import OrderedDict
from xml.sax.saxutils import unescape

import lxml.etree as ET
from lxml.builder import E  # pylint: disable = no-name-in-module

from cstoreerrors import SkipRecordException
from commonUtils import langUtils
from commonUtils.listUtils import uniq
from commonUtils.textUtils import remove_unwanted_chars
from commonUtils.textUtils import strip_control_chars
from commonUtils.textUtils import fix_named_ents
from commonUtils.textUtils import xmlescape
from datetool.dateparser import parser as dateparser
from datetool.dateparser import ParserError
# from mappings.abstractmapping import AbstractMapping
from mappings.abstractetreemapping import AbstractEtreeMapping
from mappings.protoapsmapping import ProtoAPSMapping

log = logging.getLogger('tr.mapping.leviathan')

# Set a new default XML parser that won't strip out CDATA markup and text
ET.set_default_parser(parser=ET.XMLParser(strip_cdata=False))


# a simple convenience to convert "false, on, off, true, yes, no" etc to
# boolean
def to_bool(value):
    if value in ['1', 'yes', 'on', 'true']:
        return True
    elif value in ['0', 'no', 'off', 'false']:
        return False
    return None


special_key_journals = [
    'FER000001',
    'EIM000069',
    'EIM000070',
    'EIM000071',
    'EIM000073',
    'EIM000074',
    'EIM000075',
    'EIM000076',
    'EIM000077',
    'EIM000078',
    'EIM000079',
    'EIM000080',
    'EIM000081',
    'EIM000082',
    'EIM000083',
    'EIM000084',
    'EIM000085',
    'EIM000086',
    'EIM000087',
    'EIM000088',
    'EIM000089',
    'EIM000092',
    'EIM000093',
    'EIM000094',
    'EIM000095',
    'EIM000096',
    'EIM000097',
    'EIM000099',
    'EIM000100',
    'EIM000101',
    'EIM000102',
    'EIM000103',
    'EIM000104',
    'EIM000108',
    'EIM000109',
    'EIM000110',
    'EIM000111',
    'EIM000113',
    'EIM000114',
    'EIM000115',
    'EIM000116',
    'EIM000117',
    'EIM000118',
    'EIM000119',
    'EIM000120',
    'EIM000121',
    'EIM000122',
    'EIM000123',
    'EIM000124',
    'EIM000125',
    'EIM000126',
    'EIM000127',
    'EIM000128',
    'EIM000129',
    'EIM000130',
    'EIM000131',
    'EIM000132',
    'EIM000133',
]


def get_copyright_key(journalid, year):
    if journalid in special_key_journals:
        return '%s_%s' % (journalid, year)
    return journalid

# pylint: disable = too-many-instance-attributes
class LeviathanMapping(AbstractEtreeMapping, ProtoAPSMapping):
    term_keys = {
        'activity': 'activity',
        'author': 'author',
        'color': 'color',
        'company': 'corporation',
        'designer': 'designer',
        'fashionitem': 'fashionitem',
        'geographic': 'location',
        'general': 'general',
        'material': 'material',
        'personal': 'person',
        'pictured': 'pictured',
        'photographerillustrator': 'photographerillustrator',
        'production': 'production',
        'trend': 'trend',
        'work': 'work'
    }

    __simpleAttrs = [
        ['journal/accnum'],
        ['journal/journalid', 'jid'],
        ['journal/docid', 'docid'],
        ['journal/supplement', 'supplement'],
        ['journal/title', 'doc_title'],
        ['journal/subhead[1]', 'subtitle'],
        ['journal/series', 'series'],
        ['journal/pubdates/numdate', 'numeric_date'],
        ['journal/pubdates/originaldate', 'originaldate'],
        ['journal/doctypes/doctype1', 'doctype1'],
        ['journal/doctypes/doctype2', 'doctype2'],
        ['journal/volume', 'volume'],
        ['journal/issue', 'issue'],
        ['journal/abstract', 'abstract'],
        ['journal/apdf_available', 'apdf_available']
    ]

    __imageAttrs = (
        ['category'],
        ['credit'],
        ['caption'],
        ['display_pagenumber'],
    )

    __imageMapping = {
        'credit': 'Credits',
        'category': 'ImageCategory',
        'display_pagenumber': 'ImageStartPage',
    }

    list_attrs = [
        'alternate_titles',
        'doc_notes',
        'doctypes',
        'editorial_notes',
        'phys_desc_notes',
        'bio_notes',
        # 'role_terms',
        'supplemental_notes',
    ]
    term_attrs = [
        'activity_terms',
        'author_terms',
        'color_terms',
        'designer_terms',
        'fashionitem_terms',
        'general_terms',
        'genre_terms',
        'geographic_terms',
        'material_terms',
        'nationality_terms',
        'personal_terms',
        'pictured_terms',
        'photographerillustrator_terms',
        'production_terms',
        'trend_terms',
        'work_terms',
    ]

    def __init__(self, rawrecord, extra_simpleAttrs=None):
        super(LeviathanMapping, self).__init__(rawrecord)
        self.log = log
        # XPath expressions used elsewhere in the mapping
        self.xpaths = self.get_xpaths()

        # get the values from the input record
        self.xml = self.rawrecord.data

        # This is a way of injecting more simpleAttrs into the __simpleAttrs
        # list. Using a __ attribute turns out to have been a bad design
        # choice.
        if extra_simpleAttrs:
            # pylint: disable = invalid-name
            self.__simpleAttrs = self.__simpleAttrs + extra_simpleAttrs
        self.assignSimpleAttrs(self.__simpleAttrs)

        self.assign_languages()

        self.record.section_headings = []
        for section_heading in self.getTextFromXML('//journal/sectionheads/*'):
            self.record.section_headings.append(section_heading)

        self.assign_contributors()
        self.assign_company_and_brand()

        # Get the pagenumbers from the pagezone tree
        self.record.pagenumbers = self.set_page_numbers()

        self.pages_with_layout = {}
        for page_ref in self.xml.xpath('//pagezones/zone/page_ref'):
            self.pages_with_layout[page_ref.text] = page_ref.attrib['layout']

        self.record.pages = sorted(self.pages_with_layout.keys())

        self.assign_doc_features()

        self.record.text = self.getTextFromXML('//bodytext/p')

        self._dtable = {
            'abstract': self.__class__.abstract,
            'apdf_available': self.__class__.noop,
            'author_terms': self.__class__.noop,
            'brands': self.__class__.noop,
            'company_terms': self.__class__.noop,
            'contributors': self.__class__.contributors,
            'color_terms': self.__class__.noop,
            'designer_terms': self.__class__.noop,
            'doc_features': self.__class__.doc_feature,
            'doc_title': self.__class__.title,
            'docid': self.__class__.legacyID,
            'doctype1': self.__class__.noop,
            'doctype2': self.__class__.noop,
            'fashionitem_terms': self.__class__.noop,
            'images': self.__class__.noop,
            'issue': self.__class__.issue,
            'jid': self.__class__.journalID,
            'languages': self.__class__.noop,
            'material_terms': self.__class__.noop,
            'numeric_date': self.__class__.numeric_date,
            'originaldate': self.__class__.rawPubDate,
            'pagenumbers': self.__class__.pagenumbers,
            'pages': self.__class__.noop,
            'pictured_terms': self.__class__.noop,
            'photographerillustrator_terms': self.__class__.noop,
            'section_headings': self.__class__.noop,
            'series': self.__class__.series,
            'subtitle': self.__class__.subtitle,
            'supplement': self.__class__.supplement,
            'text': self.__class__.hiddenText,
            'trend_terms': self.__class__.noop,
            'volume': self.__class__.volume,
            'work_terms': self.__class__.noop,
        }

        self._computedValues = [  # pylint: disable = invalid-name
            # pylint:disable = protected-access
            self.__class__._lastUpdateTime,
            self.__class__._objectIDs,
            self.__class__._setDates,
            self.__class__._objectTypes,
            self.__class__._languages,
            self.__class__._legacy_parent_id,
            self.__class__._section_headings,
            self.__class__._copyright_statement,
            self.__class__._cover,
            self.__class__._components,
            self.__class__._images,
            self.__class__._page_count,
            self.__class__._company_and_brand_terms,
            self.__class__._build_terms,
        ]

        self.copyright_statements = self.fetch_copyright_statements()
        self.copyright_lookup_key = get_copyright_key(self.record.jid, self.record.numeric_date[:4])

        self.imageAttrs = self.__imageAttrs
        self.imageMapping = self.__imageMapping
        self.assignImages('//pagezones/zone[@type="feature"]')
        self.assign_work_terms()
        self.assign_author_terms()
        self.assign_color_terms()
        self.assign_designer_terms()
        self.assign_fashionitem_terms()
        self.assign_material_terms()
        self.assign_pictured_terms()
        self.assign_photographerillustrator_terms()
        self.assign_trend_terms()
        # self.assign_product_terms()

    # This handles various "assign_<something>" methods. Those that can't be
    # implemented here must be implemented as real methods in the appropriate
    # place.
    def __getattr__(self, attr):
        if attr.startswith('assign_'):
            attrname = attr.replace('assign_', '')
            if attrname in self.list_attrs:
                def _assign(xpath, fn=None):  # pylint: disable = invalid-name
                    setattr(self.record, attrname, [])
                    if fn is None:
                        def fn(x): return uniq(self.getTextFromXML(x))
                        # fn = lambda x: uniq(self.getTextFromXML(x))
                    for thing in fn(xpath):
                        getattr(self.record, attrname).append(thing)
                return _assign
            elif attrname in self.term_attrs:
                term_type = attrname.split('_')[0]

                def _assign(xpath=None):
                    self._assign_terms(term_type, xpath)
                return _assign
            else:
                raise RuntimeError("Unknown term type '%s'" % attrname)
        else:
            super(LeviathanMapping, self).__getattr__(attr)

    def _assign_terms(self, termtype, xpath=None):
        terms = []
        if xpath is None:
            xpath = '//subjects/subject[@type="%s"]' % self.term_keys[termtype]
        for term in self.xml.xpath(xpath):
            text = term.text
            attrs = term.attrib
            try:
                del attrs['type']
            except KeyError:
                pass
            if attrs == {}:
                attrs = None
            terms.append({'value': text, 'attrs': attrs})
        if len(terms) > 0:
            setattr(self.record, '%s_terms' % termtype, terms)
        else:
            setattr(self.record, '%s_terms' % termtype, [])

    def assign_doc_features(self):
        self.record.doc_features = []
        for feature in uniq(self.getTextFromXML('//imagefeatures/feature')):
            self.record.doc_features.append(feature)

    def assign_contributors(self):
        self.record.contributors = self.xml.find('.//contributors')

    def assign_languages(self):
        self.record.languages = []
        for lang in self.getTextFromXML('//languages/language'):
            self.record.languages.append(lang)

    # The various methods called to build terms are just simple delegates that
    # call this method. It takes the term name, and uses that to fetch the
    # right set of terms from the self.record member. It extracts term value
    # and additional attributes, if any, then looks up the term type in the
    # self.term_types, passing in the term value and search object type as
    # arguments to the lambda. The resultant dict is then finally passed on to
    # self.add_term.
    def _build_term(self, term_name=None, termtype=None, termvalue=None, termattr=None):  # noqa
        if any([termtype, termvalue, termattr]):
            # pylint: disable = bad-super-call
            return super(AbstractEtreeMapping, self)._build_term(
                    termtype, termvalue, termattr)
        else:
            self._build_term_leviathan(term_name)

    def _build_term_leviathan(self, term_name):
        for term in getattr(self.record, '%s_terms' % term_name):
            try:
                term_value = term['value']
                additional_attrs = self._translate_term_attrs(term['attrs'])
            except TypeError:
                term_value = term
                additional_attrs = None
            term_data = self.term_structures[term_name](
                term_value, self.gs4.searchObjectTypeOrigin)
            if additional_attrs is not None:
                try:
                    term_data['attrs'] = term_data['attrs'] + additional_attrs
                except KeyError:
                    term_data['attrs'] = additional_attrs
            self.add_term(term_data)

    term_structures = OrderedDict([
        ('company', lambda value, origin: {
            'TermType': 'CompanyTerm',
            u'values': {u'CompanyName': value},
            u'attrs': {
                u'TermSource': origin}
        }),
        ('product', lambda value, _: {
            u'TermType': u'Term',
            u'attrs': {u'TermType': u'Product'},
            u'values': {u'TermValue': value}
        }),
        ('personal', lambda value, origin: {
            'TermType': 'Term',
            u'values': {u'TermValue': value},
            u'attrs': {
                'TermType': 'Personal',
                'TermSource': origin}
        }),
        ('production', lambda value, _: {
            'TermType': 'FlexTerm',
            u'values': {u'FlexTermValue': value},
            u'attrs': {u'FlexTermName': u'ProductionTitle'}
        }),
        ('geographic', lambda value, _: {
            'TermType': 'Term',
            u'values': {u'TermValue': value},
            u'attrs': {u'TermType': 'Geographic'}
        }),
        ('general', lambda value, _: {
            'TermType': 'GenSubjTerm',
            u'values': {u'GenSubjValue': value}
        }),
        ('genre', lambda value, _: {
            'TermType': 'FlexTerm',
            u'values': {u'FlexTermValue': value},
            u'attrs': {u'FlexTermName': u'ProductionGenre'}
        }),
        ('activity', lambda value, _: {
            'TermType': 'FlexTerm',
            u'values': {u'FlexTermValue': value},
            u'attrs': {u'FlexTermName': u'Activity'}
        }),
        ('nationality', lambda value, _: {
            'TermType': 'FlexTerm',
            u'values': {u'FlexTermValue': value},
            u'attrs': {u'FlexTermName': u'Nationality'}
        }),
        ('work', lambda value, _: {
            'TermType': 'FlexTerm',
            u'values': {u'FlexTermValue': value},
            u'attrs': {u'FlexTermName': u'SubjWork'}
        }),
        ('author', lambda value, _: {
            'TermType': 'FlexTerm',
            u'values': {u'FlexTermValue': value},
            u'attrs': {u'FlexTermName': u'SubjAuth'}
        }),
        # These are new ones for Vogue Italia
        ('designer', lambda value, origin: {
            'TermType': 'FlexTerm',
            u'values': {u'FlexTermValue': value},
            u'attrs': {u'FlexTermName': u'Designer'}
        }),
        ('fashionitem', lambda value, _: {
            'TermType': 'FlexTerm',
            u'values': {u'FlexTermValue': value},
            u'attrs': {u'FlexTermName': u'FashionItem'}
        }),
        ('color', lambda value, _: {
            'TermType': 'FlexTerm',
            u'values': {u'FlexTermValue': value},
            u'attrs': {u'FlexTermName': u'ItemColor'}
        }),
        ('material', lambda value, _: {
            'TermType': 'FlexTerm',
            u'values': {u'FlexTermValue': value},
            u'attrs': {u'FlexTermName': u'ItemMaterial'}
        }),
        ('pictured', lambda value, _: {
            'TermType': 'FlexTerm',
            u'values': {u'FlexTermValue': value},
            u'attrs': {u'FlexTermName': u'PersonDepicted'}
        }),
        ('photographerillustrator', lambda value, _: {
            'TermType': 'FlexTerm',
            u'values': {u'FlexTermValue': value},
            u'attrs': {u'FlexTermName': u'SubjCreator'}
        }),
        ('trend', lambda value, _: {
            'TermType': 'FlexTerm',
            u'values': {u'FlexTermValue': value},
            u'attrs': {u'FlexTermName': u'Trend'}
        }),
    ])
    term_names = term_structures.keys()

    # Delegate methods to build the nested data structures that get passed to
    # the view layer and helper to build out the Terms groups.
    # Should these be squished further into the __getattr__, above?
    def _build_terms(self):
        for term_type in self.term_names:
            self._build_term(term_type)

    def _translate_term_attrs(self, attrs):
        # The subject attributes used in Leviathan don't always match the
        # permitted attribute names in IngestSchema. This method translates
        # Leviathan attribute names to their IngestSchema equivalent, using the
        # mapping held in self.term_attr_translation.
        if attrs is None:
            return
        for k, v in attrs.items():  # pylint: disable = invalid-name
            if k in self.term_attr_translation.keys():
                del attrs[k]
                attrs[self.term_attr_translation[k]] = v
        return attrs

    @property
    def productCode(self):  # pylint: disable = invalid-name
        if self._cfg['product'].startswith('bp'):
            return 'BPC'
        elif self._cfg['product'] == 'art':
            return 'AAA'
        return self.get_product_code(lambda s: s.upper())

    def numeric_date(self, data):
        self.gs4.numericStartDate = ''.join(data.split('-'))

    def series(self, data):
        self.gs4.series = data

    def supplement(self, data):
        self.gs4.parentInfoSupplement = self.cleanAndEncode(data)

    def legacyID(self, data):  # pylint: disable = invalid-name
        self.gs4.legacyID = self._prefixedLegacyId(data)
        self.gs4.originalCHLegacyID = data
        self.setLegacyDocumentID(data)

    def subtitle(self, data):
        self.gs4.subtitle = self.cleanAndEncode(data)

    def contributors(self, data):
        if data is None:
            return
        self.gs4.contributors = []
        # Set this so that the helper method buildContributors knows to do the
        # right thing.
        self.gs4.preformattedContributors = True
        try:
            for index, contributor in enumerate(
                    data.xpath('.//contributor'), start=1):
                self.gs4.contributors.append(
                    self._build_contributor(index, contributor))
        except AttributeError:
            # We get here if we have no contributors to add to the doc.
            # TODO: is this always acceptable, or should it be considered a
            # problem in some content sets?
            self.msq.append_to_message(
                'Empty or missing contributor (non-fatal)',
                self._cfg['filename']
            )
            log.warning(
                '%s: empty or missing contributors group',
                self._cfg['filename']
            )
        # for contrib in self.gs4.contributors:
        #     for elem in contrib:
        #         print elem.text

    elems_with_html = [
        ['production_role', 'ContribDesc'],
        ['introductory_text', 'ContribDescPre'],
    ]

    contributor_elems = {
        'lastname': 'LastName',
        'firstname': 'FirstName',
        'organisation_name': 'OrganizationName',
        'originalform': 'OriginalForm',
        'altoriginalform': 'AltOriginalForm',
        'role_desc': 'MiscRoleDesc',
        'character_played': 'CharacterRole',
    }

    def _build_contributor(self, index, contributor):
        # print index, ET.tostring(contributor) Contributor string is correct
        # at this point
        contrib_fragment = E.Contributor(
            ContribOrder=str(index),
            ContribRole=contributor.get('role')
        )

        # Leviathan //contributor/altoriginalform is multiply-occurring, and
        # maps to the singly-occurring //Contributor/AltOriginalForm in Ingest
        # Therefore, if the current element includes any instances, join
        # their values with '/', and replace all occurrences here with the
        # joined version. It can then quite happily go through the rest of
        # the method as a single element.
        altoriginalforms = contributor.xpath('.//altoriginalform')
        if altoriginalforms:
            elem = ET.Element('altoriginalform')
            elem.text = '/'.join([e.text for e in altoriginalforms])
            for element in altoriginalforms:
                contributor.remove(element)
            contributor.append(elem)
        for elem in contributor.iterdescendants():
            if elem.tag in self.contributor_elems.keys():
                contrib_fragment.append(
                    self._build_contributor_elem(elem)
                )

        for name in ['elems_in_contrib_desc', 'elems_in_contrib_desc_pre']:
            if hasattr(self, name):
                elem = self._build_contributor_contrib_desc_elems(
                    contributor, name
                )
                if elem is not None:
                    contrib_fragment.append(elem)
                else:
                    pass
        return contrib_fragment

    def _build_contributor_elem(self, src_elem):
        # print src_elem.text correct here as well
        elem = ET.Element(self.contributor_elems[src_elem.tag])
        elem.text = fix_named_ents(src_elem.text)
        return elem

    def _build_contributor_contrib_desc_elems(self, contributor, elem_name):
        contrib_children = [c.tag for c in contributor.iterdescendants()]
        value = ''
        for elem in getattr(self, elem_name):
            if elem in contrib_children:
                value = '; '.join(
                    [value] + [c.text.strip() for c
                               in contributor.xpath('.//%s' % elem)]
                )

        value = value.strip('; ')
        if value != '':
            tag = ''.join([x.capitalize() for x in elem_name.split('_')[2:]])
            # Only include the HTMLContent attribute if we really do appear
            # to have HTML in the content...
            if re.search(r'.*<.*>', value):
                elem = ET.Element(tag, HTMLContent="true")
                elem.text = unescape(value)
            else:
                elem = ET.Element(tag)
                elem.text = xmlescape(value)
            return elem

    def abstract(self, data, abstract_type=None, htmlcontent=None):
        if abstract_type is None:
            abstract_type = u'Summary'
        self.gs4.abstract = self._abstract(data, abstract_type, htmlcontent)

    def doc_feature(self, data):
        self.gs4.docFeatures = [
            self.cleanAndEncode(feature) for feature in data
        ]

    def hiddenText(self, data):  # pylint: disable = invalid-name
        data = [strip_control_chars(word) for word in data]
        data = [remove_unwanted_chars(word) for word in data]
        data = [fix_named_ents(word) for word in data]
        self.gs4.hiddenText = data

    # Computed Values
    def _setDates(self):
        """Set the Numeric, and AlphaNumeric dates."""
        parsed_date = dateparser.parse(self.gs4.numericStartDate).start_date
        self.gs4.normalisedAlphaNumericDate = parsed_date.normalised_alnum_date
        self.gs4.numericStartDate = parsed_date.normalised_numeric_date

    def _objectTypes(self):  # pylint: disable = invalid-name
        if self.record.doctypes:
            self.gs4.searchObjectType = self.record.doctypes
        else:
            self.gs4.searchObjectType = [self.record.doctype1]
        if getattr(self.record, 'doctype2') != '':
            self.gs4.searchObjectType.append(self.record.doctype2)

    def _languages(self):
        self.gs4.languageData = langUtils.lang_iso_codes(self.record.languages)

    def _legacy_parent_id(self):
        self.gs4.legacyParentID = '%s_%s' % (
            self.gs4.journalID, ('_').join(
                self._cfg['pruned_basename'].split('_')[1:3]
            )
        )

    def _section_headings(self):
        self.gs4.section_headings = [
            self.cleanAndEncode(sect_head) for sect_head
            in self.record.section_headings
        ]
        self.gs4.doc_section = (' : ').join(self.gs4.section_headings)

    def _copyright_statement(self):
        def interpolate_year(t):
            return t.replace("<CURYEAR>", str(datetime.datetime.now().year))
        if isinstance(self.copyright_statements, basestring):
            self.gs4.copyrightData = interpolate_year(
                    self.copyright_statements)
        else:
            try:
                self.gs4.copyrightData = interpolate_year(
                    self.copyright_statements[self.copyright_lookup_key]
                )
            except KeyError:
                log.error(
                    '%s: No copyright statement for %s. Skipping records',
                    self.gs4.originalCHLegacyID, self.gs4.journalID)
                self.msq.append_to_message(
                    'No copyright statement (records omitted)',
                    self.gs4.journalID)
                raise SkipRecordException(
                    'No copyright statement for %s' % self.gs4.journalID)
        self.gs4.copyrightData = self.gs4.copyrightData.replace(
                ' & ', ' &amp; ')

    def _cover(self):
        if self.gs4.originalCHLegacyID.endswith('0001'):
            self.gs4.cover = u'true'
        else:
            self.gs4.cover = u'false'

    # +++ helper methods.
    # I considered lifting the _buildLayout definition from
    # apsmapping.py up into abstractetreemapping.py, but that
    # uses pages numbers, while Leviathan explicitly encodes
    # "recto" and "verso" in the record.

    # pylint: disable = invalid-name
    def _buildLayoutInfo(self):
        layoutInfo = ''
        for page in sorted(self.pages_with_layout.keys()):
            layoutInfo += self.pages_with_layout[page].capitalize()
        return layoutInfo
