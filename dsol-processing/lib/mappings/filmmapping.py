# -*- mode: python -*-
# pylint: disable = R0903
# pylint: disable = W0212, no-member, invalid-name
#
# Overrides and new functionality specific to the film products.
#

import hashlib
import os

from collections import defaultdict
from collections import OrderedDict
from xml.sax.saxutils import unescape

from lxml.builder import E
import lxml.etree as ET

from commonUtils.textUtils import xmlescape
from commonUtils.fileUtils import buildLut
from commonUtils.listUtils import uniq
from cstoreerrors import SkipRecordException
from extensions.osextensions import makedirsp
from hashtools import hash_file
from mappings.leviathanmapping import LeviathanMapping
from mappings.abstractmapping import AbstractMapping
from pagination import Pagination

import logging
log = logging.getLogger('tr.mapping.film')


class FilmMapping(LeviathanMapping):
    # This is pretty hideous, but it has to be done.
    __extra_simpleAttrs = {
        'afi': [
            ['film/synopsis'],
            ['film/country_of_production'],
            ['film/docid'],
            ['film/doctypes/doctype1'],
            ['film/pubdates/numdate', 'numeric_date'],
            ['film/pubdates/originaldate'],
            ['film/title', 'doc_title'],
        ],
        'fiaf': [
            ['journal/elec_issn', 'eissn'],
            ['journal/print_issn', 'issn'],
            ['journal/peer_review', 'peer_review']
        ],
        'fiafref': [
            ['booksection/docid'],
            ['booksection/pubdates/originaldate'],
            ['booksection/pubdates/originaldate/@undated', 'undated'],
            ['booksection/title', 'doc_title'],
            ['bodytext', 'bodytext'],
            ['work_copyright', 'work_copyright']
        ],
        'fiaftre': [
            ['film/docid'],
            ['film/accnum'],
            ['film/country_of_production'],
            ['film/doctypes/doctype1'],
            ['film/pubdates/originaldate'],
            ['film/pubdates/originaldate/@undated', 'undated'],
            ['film/title', 'doc_title'],
        ],
        'fiifilm': [
            ['film/synopsis'],
            #['film/country_of_production'],
            ['film/docid'],
            ['film/doctypes/doctype1'],
            ['film/pubdates/originaldate'],
            ['film/pubdates/originaldate/@undated'],
            ['film/pubdates/numdate', 'numeric_date'],
            ['film/title', 'doc_title'],
        ],
        'fiipers': [
            ['biography/birth_details/birthdate'],
            ['biography/death_details/deathdate'],
            ['biography/birth_details/birthcountry'],
            ['biography/birth_details/birthtown'],
            ['biography/death_details/deathcountry'],
            ['biography/death_details/deathtown'],
            ['biography/docid'],
            ['biography/doctypes/doctype1'],
            ['biography/pubdates/originaldate'],
            ['biography/pubdates/originaldate/@undated'],
            ['biography/pubdates/numdate', 'numeric_date'],
            ['biography/title', 'doc_title'],
        ]
    }


    # note_types is a defaultdict whose default factory is dict. This means that
    # when we test for the existence of the HTMLContent key for a note_type that
    # has no other configuration (and thus does not appear in note_types), we
    # don't get a KeyError, so we can avoid a try/except in an inconvenient
    # place.
    note_types = defaultdict(dict, {
        # The order here reflects the order of the data in the output
        # document. For each key/value pair, the key is the element in
        # the leviathan content, and tne value is the label to use in the
        # HTML blob in the output document.
        'ProductionDetails': OrderedDict([
            ('production_title', 'Production Title'),
            ('description', 'Production Description'),
            ('release_year', 'Release Year'),
            ('production_qualifiers', 'Production Qualifiers'),
            ('premier_info', 'Premier Information'),
            ('production_dates', 'Production Dates'),
            ('production_crdate', 'Copyright'),
            ('production_transdate', 'First Transmission Date'),
            ('production_copyright', 'Copyright Information'),
            ('duration', 'Duration'),
            ('colcode', 'Colour Code'),
            ('colsys', 'Colour System(s)'),
            ('soundsys', 'Sound System(s)'),
            ('mpaa_cert', 'MPAA Certification'),
            ('pca_cert', 'PCA Certificate'),
            ('nbr', None),
            ('source_text', 'Source'),
            ('production_series', 'Series'),
            ('production_songs', 'Songs'),
            ('production_music', 'Music'),
            ('HTMLContent', True),
        ]),
        # Document notes contain HTML but need no other configuration.
        'Document': OrderedDict([
            ('HTMLContent', True),
        ]),
        'Biography': OrderedDict([
            ('HTMLContent', True),
        ]),
        'Supplemental': OrderedDict([
            # For Supplemental notes, we don't need to label the constituent
            # parts of the content, so the dict's values are None.
            ('citation_source', None),
            ('citsource_date', None),
            ('citsource_pagination', None),
            ('HTMLContent', True)
        ]),
        'FIIFilmSupplemental': OrderedDict([
            ('HTMLContent', True)
        ]),
    })

    elems_in_contrib_desc = [
        'parent_organisation',
        'production_role',
        'commentary_text',
        'credit_note',
    ]

    elems_in_contrib_desc_pre = [
        'introductory_text',
    ]

    pub_ids = {
        'afi': 'afi0001',
        'fiaf': 'fiaf004',
        'fiafref': 'fiafref',
        'fiaftre': 'fiaftre0001',
        'fiifilm': 'fii0001',
        'fiipers': 'fii0002',
    }

    def __init__(self, rawrecord):  # pylint: disable = too-many-statements
        # Extract the projectcode from the rawrecord. We need it here, before
        # we call up the MRO, so we can correctly merge the appropriate extra
        # simpleAttrs into the inherited list, so that it's available when
        # assignSimpleAttrs is called.
        self.projectcode = rawrecord.data.xpath(
            '//projectcode')[0].text

        try:
            self._extra_simpleAttrs = self.__extra_simpleAttrs[self.projectcode]
        except KeyError:
            self._extra_simpleAttrs = None
        super(FilmMapping, self).__init__(rawrecord, self._extra_simpleAttrs)

        # Since we get //doctype1 values in a list after calling
        # assign_doctypes, we can safely delete it here, and be sure that when
        # we have multiple values, they will all be included in the output.
        # Not all records will come with a doctype1 element, so we don't want
        # to choke on those cases.
        try:
            del self.record.doctype1
        except AttributeError:
            pass

        # Modify the value stored in self._cfg['basename'] so it includes
        # the current doc's parent journal ID, since it isn't encoded in the
        # doc ID itself, as in other content sets. Useful in the visual
        # feedback display while running.
        if self.projectcode in ['fiaf']:
            baseparent = os.path.split(self._cfg['filename'])[0]
            baseparent = os.path.basename(baseparent)
            basename = os.path.splitext(self._cfg['basename'])[0]
            self.feedback_string = "%s/%s" % (baseparent, basename)
        else:
            self.feedback_string = self._cfg['pruned_basename']

        _film_dtable = {
            'accnum': self.__class__.noop,
            'activity_terms': self.__class__.noop,
            'alternate_titles': self.__class__.alternate_titles,
            'bio_notes': self.__class__.noop,
            'birthdate': self.__class__.noop,
            'birthtown': self.__class__.noop,
            'birthcountry': self.__class__.noop,
            'bodytext': self.__class__.noop,
            'deathtown': self.__class__.noop,
            'deathcountry': self.__class__.noop,
            'company_names_as_terms': self.__class__.noop,
            'country_of_publication': self.__class__.noop,
            'country_of_production': self.__class__.country_of_production,
            'deathdate': self.__class__.noop,
            'doc_notes': self.__class__.noop,
            'doctypes': self.__class__.noop,
            'editorial_notes': self.__class__.noop,
            'eissn': self.__class__.noop,
            'genre_terms': self.__class__.noop,
            'geographic_terms': self.__class__.noop,
            'general_terms': self.__class__.noop,
            'issn': self.__class__.noop,
            # We can't handle this here for all datasets.
            'jid': self.__class__.noop,
            'nationality_terms': self.__class__.noop,
            'peer_review': self.__class__.peerreview,
            'personal_terms': self.__class__.noop,
            'phys_desc_notes': self.__class__.noop,
            'production_details': self.__class__.noop,
            'production_terms': self.__class__.noop,
            'projectcode': self.__class__.noop,
            'supplemental_notes': self.__class__.noop,
            'synopsis': self.__class__.synopsis,
            'undated': self.__class__.undated,
            'work_copyright': self.__class__.noop
        }
        self._merge_dtables(_film_dtable)

        # If we have a FIAF periodical record, we should avoid populating
        # the LegacyID in the ParentInfo group.
        #self._computedValues.remove(self.__class__._legacy_parent_id)
        # And we don't have anything in the source content about covers.
        # pylint: disable = protected-access
        self._computedValues.remove(self.__class__._cover)
        self._computedValues.remove(self.__class__._components)
        # We have our own handling of company names.
        self._computedValues.remove(self.__class__._company_and_brand_terms)

        # We have additional term types to extract for FIAF, and possibly
        # others.
        self._computedValues.append(self.__class__._journalID)
        #self._computedValues.append(self.__class__._general_terms)
        #self._computedValues.append(self.__class__._genre_terms)
        #self._computedValues.append(self.__class__._geographic_terms)
        #self._computedValues.append(self.__class__._personal_terms)
        #self._computedValues.append(self.__class__._production_terms)
        self._computedValues.append(self.__class__._production_details)
        self._computedValues.append(self.__class__._doc_notes)
        self._computedValues.append(self.__class__._editorial_notes)
        self._computedValues.append(self.__class__._phys_desc_notes)
        self._computedValues.append(self.__class__._bio_notes)
        self._computedValues.append(self.__class__._supplemental_notes)
        self._computedValues.append(self.__class__._bio_dates)
        self._computedValues.append(self.__class__._fulltext)
        self._computedValues.append(self.__class__._components)
        self._computedValues.append(self.__class__._source_types)
        self._computedValues.append(self.__class__._refpagenumbers)
        if any([self.is_fiaf, self.is_fiifilm]):
            self._computedValues.append(self.__class__._country_of_origin)

        self.gs4.projectcode = self.projectcode
        self.document_origins = {
            'afi': 'AFI',
            'fiaf': 'FIAF',
            'fiaftre': 'FIAF',
            'fiafref': 'FIAF',
            'fiifilm': 'FII',
            'fiipers': 'FII',
        }

        self.gs4.searchObjectTypeOrigin = self.document_origins[
            self.projectcode
        ]

        if self.is_fiaf:
            self.list_attrs.append('country_of_publication')
        elif self.is_fiifilm:
            self.list_attrs.append('country_of_production')

        # Extract the additional term types and assign them to members on
        # self.record for processing later by the methods added to
        # self._computedValues, above.
        self.assign_production_details()

        self.assign_general_terms()
        self.assign_geographic_terms()
        self.assign_personal_terms()
        self.assign_activity_terms('.//production_roles/activity')
        self.assign_nationality_terms('//nationality')
        self.assign_production_terms()
        self.assign_company_names_as_terms()
        self.assign_genre_terms('.//production_genres/genre')

        self.assign_alternate_titles('//alternate_title')
        self.assign_doc_notes('//notes/note[@type="Document"]',
                              self._extract_notes_data)
        self.assign_editorial_notes('//notes/note[@type="Editorial"]')
        self.assign_doctypes('//doctype1')
        self.assign_phys_desc_notes('//notes/note[@type="PhysDesc"]')
        self.assign_bio_notes('//notes/note[@type="Biography"]')
        self.assign_supplemental_notes('//object_citations/object_citation',
                                       self.xml.xpath)

        # Support multiple instances of country_of_publication in FIAF Index records.
        if self.is_fiaf:
            self.assign_country_of_publication('//journal/country_of_publication')
        elif self.is_fiifilm:
            self.assign_country_of_production('//film/country_of_production')

        # The film databases are unstructured, and so we need this flag to
        # ensure that dates and enumeration information doesn't end up in
        # the //Parent/ParentInfo group, but instead ends up in //ObjectInfo
        # and //PublicationInfo, as appropriate.
        self.gs4.unstructured = True

        # If self.record contains members named in pub_info_fields, set the
        # publisher_info flag to trigger rendering the PublicationInfo group
        # in the output.
        pub_info_fields = [
            'country_of_production',
            'issue',
            'volume',
        ]
        if any(a in self.record.fields() for a in pub_info_fields):
            self.gs4.publisher_info = True

        # Copyright statements are per-dataset. Use the projectcode as the key.
        self.copyright_lookup_key = self.projectcode

        # For FIAF journals content, we need to load the title list lookup.
        # We use the class-level variable _title_list_lookup so we don't
        # repeatedly load and reload the file for each record.
        # We also assign the values here, to save on additional method defs
        # and calls.
        if self.is_fiaf:
            if not hasattr(self.__class__, '_title_list_lookup'):
                self.__class__._title_list_lookup = buildLut(
                    'fiaf_journal_titles.txt')
            title, country = self._title_list_lookup[self.record.jid].split(' ~~ ')
            # We know some titles have an ampersand in them, so let's escape
            # them.
            self.gs4.publication_title = xmlescape(title)
            self.gs4.publisherCountry = country
            # This needs to be set here explicitly in case, as does happen,
            # the pub_info_fields test above doesn't correctly turn on
            # rendering the publisher_info block in the output.
            self.gs4.publisher_info = True

        self.pdf_representation_required = False

        # If IDSFILE exists in the environment, load its contents here. If it
        # isn't set, simply create an empty list.
        if os.getenv('IDSFILE', None) is not None:
            with open(os.getenv('IDSFILE')) as idfile:
                self._force_rebuild_ids = [l.strip() for l in idfile.readlines()]
        else:
            self._force_rebuild_ids = []

    @property
    def is_fiaf(self):
        return self.projectcode == 'fiaf'

    @property
    def is_fiifilm(self):
        return self.projectcode == 'fiifilm'


    def _extract_notes_data(self, xpath):
        # Some notes have a subtype attribute, and some don't. This method
        # builds a list of dicts containing note text and, if present for a
        # particular note, its subtype, captured as a label. This is passed in
        # to the method defined in the __getattr__ upon calling the
        # non-existant assign_doc_notes method.
        notes = []
        for elem in self.xml.xpath(xpath):
            if 'subtype' in elem.attrib.keys():
                note = {'label': elem.attrib['subtype'],
                        'text': elem.text}
            else:
                note = {'text': elem.text}
            notes.append(note)
        return notes

    # assign_doc_features can't be handled through __getattr__, as there's a
    # real method of the same name up the inheritance tree, which prevents
    # __getattr__ being triggered when it's called.
    def assign_doc_features(self):
        self.record.doc_features = []
        for feature in uniq(self.getTextFromXML('//journal/docfeatures/docfeature')):
            self.record.doc_features.append(feature)


    # All of these are now virtual methods, handled in self.__getattr__.
    # When called, it is necessary to pass in the XPath to evaluate, and
    # where the values are not extracted using getTextFromXML, you must also
    # pass in the function or method to use to return the values you want.
    # def assign_alternate_titles(self):
    # def assign_doc_notes(self):
    # def assign_phys_desc_notes(self):
    # def assign_supplemental_notes(self):

    # This one needs an actual implementation, as it doesn't fit the pattern
    # used for the other assignments in the __getattr__.
    def assign_company_names_as_terms(self):
        # For AFI we need to grab company name information from the contributors
        # group and use it to populate additional CompanyTerm elements in the
        # IngestSchema output. We can simply append to
        # self.record.company_terms, since that gets created by the method
        # self.assign_company_and_brand, which is called earlier than this one.
        companynames = []
        for role in ['ProductionCompany', 'Crew']:
            for company_name in self.xml.xpath('.//contributor[@role="%s"]/organisation_name' % role):
                companynames.append(company_name.text)
        companynames = list(set(companynames))
        for item in companynames:
            self.record.company_terms.append(item)


    # Override the default implementation since we need to extract company
    # values from a different XPath in the source.
    def assign_company_and_brand(self):
        self._assign_terms('company')

    def assign_production_details(self):
        '''The production_details group occurs once for each production
        mentioned in the record. We need to capture each instance so we can
        process it into the output stream in an appropriately formatted
        Note field.
        '''
        prod_details = []
        for term in self.xml.xpath('//productions/production_details'):
            prod_details.append(term)
        if len(prod_details) > 0:
            self.record.production_details = prod_details

    def _objectIDs(self):
        # We need to add the accession number to the object IDs.
        super(self.__class__, self)._objectIDs()
        if self.record.accnum:
            self.gs4.objectIDs.append(
                {'value': self.record.accnum,
                 u'IDOrigin': self.gs4.searchObjectTypeOrigin,
                 u'IDType': u'AccNum'})

        # Need to capture ISSN and ElecISSN on gs4 as well as inserting it
        # into the ObjectIDs dict, since we need to include it in the output
        # for FIAF Journals content.
        if self.record.issn:
            self.gs4.issn = self.record.issn
            self.gs4.objectIDs.append(
                {'value': self.record.issn,
                 u'IDType': u'ISSN'}
            )
            self.gs4.build_locators = True

        if self.record.eissn:
            self.gs4.eissn = self.record.eissn
            self.gs4.objectIDs.append(
                {'value': self.record.eissn,
                 u'IDType': u'ElecISSN'}
            )
            self.gs4.build_locators = True

    # Dict to map from legacy (Leviathan) attribute names to their Ingest
    # Schema equivalent. Used by the self._translate_term_attrs method.
    term_attr_translation = {
        'majortopic': 'MajorTopic',
    }

    def _build_production_details(self):
        values = []
        for elem in self.note_types['ProductionDetails'].keys():
            value = ''
            #if elem in prod_children:
            if elem in self.production_details_child_elems():
                value = '; '.join(
                    [c.text.strip('; ') for c
                     in self.xml.findall('.//%s' % elem)])
                if elem == 'duration':
                    value = '%s min.' % value
                if self.note_types['ProductionDetails'][elem] is None:
                    # In the case of the <nbr> elem, we don't want a label,
                    # and we don't want the value from the source, which is
                    # just "Yes". Instead, we need this string.
                    if elem == 'nbr':
                        value = '<p>Passed by National Board of Review</p>'
                else:
                    value = '<p>%s: %s</p>' % (
                        self.note_types['ProductionDetails'][elem], value)
            if value is not '':
                values.append(value)
        if len(values) > 0:
            return values

    def _build_fiipers_production_details(self):
        values = []
        for fields in self.record.production_details:
            valuenest = []
            rolenest = []
            for field in fields:
                if field.tag == 'awards':
                    awards_blob = ''
                    for award in self.xml.xpath('.//awards/award'):
                        if len(award.xpath('self::*/award_category')) is not 0:
                            award_cat = award.xpath('self::*/award_category')[0].text
                        else:
                            award_cat = ''
                        if len(award.xpath('self::*/award_production')) is not 0:
                            award_prod = award.xpath('self::*/award_production')[0].text
                        else:
                            award_prod = ''
                        awards_blob = '%s<li>%s, %s, %s - %s</li>' % (
                            awards_blob,
                            award.xpath('self::*/award_event')[0].text,
                            award.xpath('self::*/award_year')[0].text,
                            award_cat,
                            award_prod,
                        )
                    awards_blob = '<p>Awards:</p><ul>%s</ul>' % awards_blob
                    valuenest.append(awards_blob)
                elif 'person_' not in field.tag:
                    value = '<p>%s: %s</p>' % (self.note_types['ProductionDetails'][field.tag], field.text.strip())
                    valuenest.append(value)
                else:
                    pass
            if len([cred.text for cred in fields.findall('.//person_credrole')]) is not 0:
                rolenest.append('<i>Credit(s): </i>%s' % '; '.join([cred.text for cred in fields.findall('.//person_credrole')]))
            if len([cast.text for cast in fields.findall('.//person_castrole')]) is not 0:
                rolenest.append('<i>Cast:</i> %s' % '; '.join([cast.text for cast in fields.findall('.//person_castrole')]))
            if len(rolenest) is not 0:
                valuenest.append('<p>Production roles: %s</p>' % ', '.join(rolenest))
            values.append(''.join(valuenest))
        return values

    def production_details_child_elems(self):
        try:
            return [
                c.tag for c
                in self.record.production_details[0].iterdescendants()]
        except IndexError:
            return

    def _production_details(self):
        values = []
        if not self.production_details_child_elems():
            return
        if self.projectcode in ['fiipers']:
            for value in self._build_fiipers_production_details():
                values.append(value)
        else:
            values = self._build_production_details()

        # The "Awards" section for FII Film records doesn't fit the pattern, so
        # needs special handling.
        ## FIXME: there should be a more elegant way to test for fields than individual testing.
        if 'awards' in self.production_details_child_elems():
            if self.projectcode == 'fiifilm':
                awards_blob = ''
                for award in self.xml.xpath('.//awards/award'):
                    if len(award.xpath('self::*/award_category')) is not 0:
                        award_cat = award.xpath('self::*/award_category')[0].text
                    else:
                        award_cat = ''
                    awards_blob = '%s<li>%s, %s, %s - %s</li>' % (
                        awards_blob,
                        award.xpath('self::*/award_event')[0].text,
                        award.xpath('self::*/award_year')[0].text,
                        award_cat,
                        award.xpath('self::*/award_recipient')[0].text,
                    )

                awards_blob = '<p>Awards:</p><ul>%s</ul>' % awards_blob
                values.append(awards_blob)
        if values != [] and values is not None:
            note_text = '<br/>'.join([unescape(value) for value in values])
            self._build_note(note_text, 'ProductionDetails')

    def _supplemental_notes(self):
        # The structure of Supplemental notes is not the same across products.
        if self.projectcode in ['fiifilm', 'fiipers']:
            self._fii_supplemental_notes()
        else:
            self._generic_supplemental_notes()

    @staticmethod
    def sortnotes(x, y):
        return cmp(int(x.get('citorder')), int(y.get('citorder')))

    def _fii_supplemental_notes(self):  # pylint: disable = too-many-branches
        values = []
        sorted_notes = sorted(
            [elem for elem
             in self.record.supplemental_notes],
            self.sortnotes)

        second_line = [
            'citation_source', 'citsource_issn', 'citation_volume',
            'citation_issue', 'citsource_date', 'citsource_pagination',
            'citsource_lang', 'citation_illus']

        for note in sorted_notes:
            children = [c.tag for c in note.iterdescendants()]
            value = ''
            line1 = line2 = line3 = ''
            # First line of the Note blob
            if all(a in children for a in ['citation_author', 'citation_title']):
                line1 = '%s: %s<br/>'.strip() % (note.find('.//citation_author').text,
                                                 note.find('.//citation_title').text)

            # Second line. There *must* be a better way to do this...
            if any(a in children for a in second_line):
                for elem in second_line:
                    try:
                        text = note.find('.//%s' % elem).text
                    except AttributeError:
                        continue
                    if elem == 'citation_source':
                        line2 = '<em>%s</em>' % text
                    elif elem == 'citsource_issn':
                        line2 = '%s (%s)' % (line2, text)
                    elif elem == 'citation_volume':
                        line2 = '%s v. %s' % (line2, text)
                    elif elem == 'citation_issue':
                        line2 = '%s n. %s' % (line2, text)
                    elif elem == 'citsource_date':
                        line2 = '%s, %s' % (line2, text)
                    elif elem in ['citsource_pagination', 'citsource_lang', 'citation_illus']:
                        line2 = '%s, %s' % (line2, text)
                if line2.strip() != '':
                    # Strip off leading/trailing hanging commas as well as spaces.
                    line2 = '%s<br/>'.strip() % line2.strip(', ')

            # Third line.
            try:
                line3 = '%s'.strip() % note.find('.//citation_notes').text
            except AttributeError:
                pass

            # Stick the three parts together, and call str.strip() on the
            # result to ensure we don't get unnecessary empty lines in the
            # output.
            value = ('<p>%s%s%s</p>' % (line1, line2, line3)).strip()
            if value != '':
                note_text = unescape('%s\n' % value)
                values.append(note_text)

        if values != []:
            self._build_note(''.join([value for value in values]), 'Supplemental')

    def _generic_supplemental_notes(self):
        values = []
        sorted_notes = sorted(
            [elem for elem
             in self.record.supplemental_notes],
            self.sortnotes)

        for note in sorted_notes:
            children = [c.tag for c in note.iterdescendants()]
            value = ''
            for elem in self.note_types['Supplemental'].keys():
                if elem in children:
                    value = ', '.join(
                        [value, note.find('.//%s' % elem).text])
            if value != []:
                value = '<p>%s</p>' % value.strip(', ')
                values.append(value)
        if values != []:
            note_text = ''.join([unescape(value) for value in values])
            self._build_note(note_text, 'Supplemental')

    def _expand_to_ul(self, note_data, sep='|'):
        html = ["<ul>"]
        [html.append("<li>%s</li>" % li) for li in note_data.split(sep)]
        html.append("</ul>")
        return ''.join(html)

    def _doc_notes(self):
        values = []
        for doc_note in self.record.doc_notes:
            try:
                if self.projectcode == 'fiaftre':
                    values.append(
                        '<p><b>%s:</b></p>%s' %
                        (doc_note['label'], self._expand_to_ul(doc_note['text']))
                    )
                else:
                    values.append(
                        '<p><b>%s:</b> %s</p>' %
                        (doc_note['label'], doc_note['text']))
            except KeyError:
                # We get here if doc_note doesn't have a label in its keys.
                # i.e. we just want the note text in the output.
                values.append('<p>%s</p>' % doc_note['text'])
        if values != []:
            note_text = ''.join([unescape(value) for value in values])
            self._build_note(note_text, 'Document')

    def _editorial_notes(self):
        note_text = '; '.join([i for i in self.record.editorial_notes])
        if note_text != '':
            self._build_note(note_text, 'Editorial')

    def _bio_notes(self):
        birthplace = []
        deathplace = []
        values = []

        for item in ['birthtown', 'birthcountry']:
            if getattr(self.record, item) != '':
                birthplace.append(getattr(self.record, item))

        for item in ['deathtown', 'deathcountry']:
            if getattr(self.record, item) != '':
                deathplace.append(getattr(self.record, item))

        if len(birthplace) > 0:
            values.append('<p>Birth Place: %s<p>' % ', '.join(birthplace))

        if len(deathplace) > 0:
            values.append('<p>Place of Death: %s<p>' % ', '.join(deathplace))

        if len(self.record.bio_notes) > 0:
            values.append('<p>%s</p>' % '; '.join([i for i in self.record.bio_notes]))

        note_text = ''.join(values)

        if note_text != '':
            self._build_note(note_text, 'Biography')

    def _phys_desc_notes(self):
        note_text = '; '.join([i for i in self.record.phys_desc_notes])
        if note_text != '':
            self._build_note(note_text, 'PhysDesc')

    def _build_note(self, note_data, note_type):
        _note = {'NoteType': note_type}
        # We can test for keys membership here without worrying about raising a
        # KeyError in the case of an unspecified note_type, as self.note_types
        # is a defaultdict whose default factory is dict.
        if 'HTMLContent' in self.note_types[note_type].keys():
            _note['NoteText'] = unescape(note_data)
            _note['HTMLContent'] = 'true'
        else:
            # cleanAndEncode just in case we have illegal characters in the text
            _note['NoteText'] = self.cleanAndEncode(note_data)
        self._add_note(_note)

    def _add_note(self, note_data):
        try:
            self.gs4.notesData.append(note_data)
        except AttributeError:
            self.gs4.notesData = [note_data]

    def _setDates(self):
        self.gs4.rawObjectDate = self.record.originaldate
        super(self.__class__, self)._setDates()

    def _journalID(self):
        if self.projectcode == 'fiafref':
            self.gs4.journalID = '%s%s' % (self.pub_ids[self.projectcode], self.record.docid[0:3])
        else:
            self.gs4.journalID = self.pub_ids[self.projectcode]

    def _legacy_parent_id(self):
        self.gs4.legacyParentID = self.record.jid

    def _bio_dates(self):
        bio_dates = {}
        for date in ['birthdate', 'deathdate']:
            if getattr(self.record, date) != '':
                bio_dates[date] = getattr(self.record, date)

        if bio_dates != {}:
            self.gs4.bio_dates = bio_dates


    def _country_of_origin(self):
        if self.is_fiaf:
            values = self.record.country_of_publication
        elif self.is_fiifilm:
            values = self.record.country_of_production
        self.gs4.publisherCountry = ', '.join(values)

    def _fulltext(self):
        if self.record.bodytext:

            textinfo = E.TextInfo(
                    E.Text(HTMLContent="true")
                )

            text_elem = textinfo.xpath('.//Text')[0]

            text_elem.text = '<![CDATA[%s]]>' % self.record.bodytext

            self.gs4.fullText = ET.tostring(textinfo, pretty_print=True)


    # This determines the prefix attached to each record. Its exact form
    # depends in the Film products on the dataset from which each record
    # derives.
    def _prefix(self):
        if self.projectcode.startswith('fiaf'):
            return 'fiaf-'
        return '%s-' % self.projectcode

    def _copyright_statement(self):
        if self.projectcode != "fiafref":
            super(self.__class__, self)._copyright_statement()
        else:
            self.gs4.copyrightData = self.record.work_copyright

    def synopsis(self, data):  # pylint: disable = arguments-differ
        abstract_type = u'Synopsis'
        super(self.__class__, self).abstract(
            data, abstract_type=abstract_type, htmlcontent='true')

    def alternate_titles(self, data):
        self.gs4.alternateTitles = data

    def _source_types(self):
        if self.projectcode == 'fiaf':
            self.gs4.source_origin = "FIAF"
            # We take the FIAF source type from the input doc.
            self.gs4.source_types = self.xml.xpath('@source_type')

    # Override the value used as the legacy Journal ID.
    def journalID(self, data):
        self.gs4.journalID = 'fiaf004'

    def pagenumbers(self, data):
        # If we don't have pagination information, it's safe to carry on.
        try:
            self.gs4.startpage = self.helper_startPage(data[0])
        except IndexError:
            pass
        self.gs4.pagination = xmlescape(Pagination(
            self.record.pagenumbers).formatted_string)

    def country_of_production(self, data):
        self.gs4.publisherCountry = data

    def peerreview(self, data):
        if data == 'Y':
            self.gs4.peerReviewed = 'true'
        else:
            self.gs4.peerReviewed = 'false'

    def undated(self, data):
        if data in ['true', 'True']:
            self.gs4.undated = True

    # We want to alter the display of the doc ID in the visual feedback to
    # include the directory containing the current document - the parent
    # journal ID is not encoded in the document ID, so in order to easily
    # locate a problematic file, we need to include the journal level
    # directory in the display.
    def visual_feedback_printid(self):
        #return self._cfg['pruned_basename']
        return self.feedback_string

    # Temporary function to assign fake page numbers to references records until real page numbers can be researched.
    def _refpagenumbers(self):
        if self.projectcode == 'fiafref':
            self.gs4.startpage = self.record.docid[4:].lstrip('0')

# Local Variables:
# eval: (setq python-shell-extra-pythonpaths (list (expand-file-name (format "%slib" (elpy-project-root)))))
# End:
