# -*- mode: python -*-

import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

import bz2
import codecs
import inspect
import logging
import lxml.etree as ET
import re
import roman
import urllib

from commonUtils import textUtils
from cstoreerrors import SkipRecordException
from dbcache import DBCacheManager
from genrecord import GenRecord
from mappings.abstractmapping import AbstractMapping
from stat import ST_SIZE

log = logging.getLogger('tr.mapping.pio')

class PIOMapping(AbstractMapping):
    # To avoid opening and reading the threading file for the journal
    # for each record (yes, we were really doing that...), we'll make
    # a class variable here that we can then attach to each instance.
    # This will really help for the larger journals (ak39, in particular)
    __threading_data = {}

    _colourJournals = '''k101 ak39 p209 p337 q351 q423 x503 m118'''.split(' ')

    _dateConversions = {
        '01': 'Jan',
        '02': 'Feb',
        '03': 'Mar',
        '04': 'Apr',
        '05': 'May',
        '06': 'Jun',
        '07': 'Jul',
        '08': 'Aug',
        '09': 'Sep',
        '10': 'Oct',
        '11': 'Nov',
        '12': 'Dec',
        '20': 'Winter',
        '21': 'Spring',
        '22': 'Summer',
        '23': 'Fall',
        '24': 'Winter',
        }

    # pylint: disable=line-too-long
    _englishMonthNames = r'(?!%s)' % '|'.join([r'%s\w+' % val for val in _dateConversions.values()])

    _seasonToMonth = {
        '20': '01',
        '21': '04',
        '22': '07',
        '23': '10',
        '24': '12',
        }

    _languages = {'GAG':'GLG', 'ESP':'EPO', 'GAE':'GLA',
                  'IRI':'GLE', 'LAN':'OCI', 'MAX':'GLV',
                  'SCR':'HRV', 'TAG':'TGL'}

    def __init__(self, rawrecord):
        super(self.__class__, self).__init__(rawrecord)

        self.gen = GenRecord(self.rawrecord.data)
        self.languages = self._languages

        self.threading_data = self.__threading_data

        # These fields only have a '$a' subfield. We may as well just assign
        # the subfield values to self.record[field].
        simple_fields = set(['035', '245', '520'])
        # These are used by do_mapping to handle _dtable entries.

        for k,v in self.gen.items():
            if '##' in v:
                log.error('Field %s in record %s contains ##, excluded from build', k, self.gen.f_035())
                self.msq.append_to_message(
                    'Source content contains multiple "##", excluded from output',
                    "%s (%s field)" % (self.gen.f_035(), k)
                )
                raise SkipRecordException
            if isinstance(v, basestring):
                try:
                    if k in simple_fields:
                        setattr(self.record, k, getattr(self.gen, 'f_%s' % k)('a'))
                    else:
                        setattr(self.record, k, v)
                except KeyError:
                    log.error('Malformed Gen record: No subfield %s in field %s (%s)', 'a', k, self.gen.f_035('a'))
                    raise
            else:
                try:
                    setattr(self.record, k, [codecs.decode(codecs.encode(i, 'utf-8'), 'ascii') for i in v])
                except UnicodeDecodeError:
                    setattr(self.record, k, [i for i in v])

        self._dtable = {
            '001':  PIOMapping.noop,
            '002':  PIOMapping.noop,
            '008':  PIOMapping.noop,
            '022':  PIOMapping.noop,
            '035':  PIOMapping.legacyID,
            '090':  PIOMapping.noop,
            '091':  PIOMapping.noop,
            '093':  PIOMapping.noop,
            '100':  PIOMapping.noop,
            '110':  PIOMapping.noop,
            '245':  PIOMapping.title,
            '260':  PIOMapping.noop,   # Place of publication. ak39 only. Ignore
            '310':  PIOMapping.noop,   # Frequency of publication. ak39 only. Ignore
            '490':  PIOMapping.noop,
            '520':  PIOMapping.abstract,
            '590':  PIOMapping.noop,   # doctype, ak39 only. Ignore
            '591':  PIOMapping.noop,   # Editors, ak39 only. Ignore
            '596':  PIOMapping.noop,   # No idea. ak39 only. Ignore
            '597':  PIOMapping.noop,   # No idea. ak39 only. Ignore
            '600':  PIOMapping.noop,
            '700':  PIOMapping.noop,
            '710':  PIOMapping.noop,
            '720':  PIOMapping.noop,
            '773':  PIOMapping.noop,
            '900':  PIOMapping.noop,
            '947':  PIOMapping.noop,
        }

        self._computedValues = [
            PIOMapping._lastUpdateTime,
            PIOMapping._insertRawPubDate,
            PIOMapping._setDates,
            PIOMapping._insertRecordType,
            #PIOMapping._seriesvolumeissue,
            PIOMapping._servolumeissue,
            PIOMapping._startendpage,
            PIOMapping._doc_section,
            PIOMapping._pagecount,
            PIOMapping._language,
            PIOMapping._buildContributors,
            PIOMapping._legacyPubID,
            #PIOMapping._objectBundleData,
            PIOMapping._objectIDs,
            PIOMapping._legacyParentID,
        #            PIOMapping._parentTitle,
            PIOMapping._insertFullText,
            PIOMapping._components,
            PIOMapping._add_terms,
        ]

        jid = self._cfg['pruned_basename']
        jid_file = self._cfg['basename']

        # Set the path for the sft full text file for the record. We test it later
        # to see if we really need to do anything
        if jid == 'ak39':
            setattr(self, 'ftfile', '/dc/pao/processed_rel1/sft/ak39/%s.xml' % self.gen.f_035('a'))
        else:
            try:
                setattr(self, 'ftfile', '/dc/pao/pci/build/sft/%s/%s.xml' % (jid, self.gen.f_035('a')))
            except KeyError as e:
                self.msq.append_to_message("Corrupt record", "Field %s missing, %s, %s" % (e, self.gen.data, self._cfg['basename']))
                log.error("Corrupt record in file %s. (Field %s missing in %s)", self._cfg['basename'], e, self.gen.data)
                raise SkipRecordException

        #get cache database for full text and PDF size estimates
        cache_root = self._cfg['cachefileroot']
        pdf_cache_path = os.path.join(cache_root, 'pdfsizecache')
        ft_cache_path = os.path.join(cache_root, 'ftcache')
        if self.has_searchable_ft:
            self.ftcache = DBCacheManager(jid_file, 'ft', os.path.join(ft_cache_path, jid_file))
        if self.has_fulltext:
            self.pdfsizecache = DBCacheManager(jid_file, 'pdf', os.path.join(pdf_cache_path, jid_file))

            try:
                self.threading_lines = self.threading_data[jid]
            except KeyError:
                # If self.threading_data[jid] isn't defined, read in the journal's
                # threading file, and sort it into a dict keyed on article ID, with
                # the image paths in a list as the value. This is only necessary for
                # the first record in each file - self.threading_data is actually
                # a reference to a class-level variable. You will be assimilated.
                self.threading_data.clear()
                tab_data = []
                with open('/dc/pao/pci/build/threading/%s.tab' % jid, 'r') as tabfile:
                    for line in tabfile:
                        thr = line.replace('035   $a', '').strip()
                        if not thr == '':
                            tab_data.append(thr)
                #tab_data = [line.replace('035   $a', '').strip() for line in open('/dc/pao/pci/build/threading/%s.tab' % jid).readlines()
                #            if not line == '']
                tab_dict = {}
                #for aid, img_path in [line.split('\t') for line in tab_data]:
                for line in tab_data:
                    try:
                        aid, img_path = line.split()
                    except ValueError:
                        print "There is something wrong with the tab file."
                        print "line: %s" % line
                        exit(1)
                    try:
                        tab_dict[aid].append(img_path)
                    except KeyError:
                        tab_dict[aid] = [img_path]
                self.threading_data[jid] = tab_dict
                self.threading_lines = self.threading_data[jid]

    @property
    def isColour(self):
        return self._cfg['pruned_basename'] in self._colourJournals

    @property
    def has_searchable_ft(self):
        return os.path.exists(self.ftfile)

    @property
    def has_fulltext(self):
        return self.gen.f_090('a') == 'A'

    @property
    def has_weblink(self):
        return '093' in self.gen.keys()

    # Methods called from the _dtable

    def title(self, data):
        super(self.__class__, self).title(self.cleanAndEncode(data)) # Remove (Book Record) ???
        #print self.gs4.title
        #log.info('added a title test')

    def legacyID(self, data):
        legacyid = data
        self.gs4.originalCHLegacyID = legacyid
        self.gs4.legacyID = '-'.join([self.productId, legacyid])
        self.setLegacyDocumentID(data)

    def abstract(self, data):
        self.gs4.abstract = self._abstract(data, 'Medium')

    # computed values.

    def _doc_section(self):
        try:
            self.gs4.doc_section = ' -- '.join([self.cleanAndEncode(val) for val in self.gen['490']])
        except TypeError:
            pass

    def _insertRawPubDate(self):
        rawpubdate = re.search(r'\((.*?)\)', self.gen['773']).group(1)
        self.gs4.rawPubDate = self.cleanAndEncode(rawpubdate)

    def _setDates(self):
        # 8 digit date from source
        numeric_date = self.gen['947'][3:11]

        # If it ends with '0000', and the raw date contains a word that means 'Winter',
        # replace '0000' with '2001'. Otherwise, replace '0000' with '0101', for a year-only date
        if numeric_date.endswith('0000'):
            if re.search(r'(Winter|Gaeaf|hivern?|Geimhreadh|Hotoke|invi?erno)', self.gs4.rawPubDate):
                numeric_date = re.sub(r'0000$', '2001', numeric_date)
            else:
                numeric_date = re.sub(r'0000$', '0101', numeric_date)

        # If it ends with '00', replace '00' with '01'
        elif numeric_date.endswith('00'):
            numeric_date = re.sub('00$', '01', numeric_date)

        # Now we have an 8 digit date with seasons correctly converted to numbers
        # between 20 Winter and 24 Winter, and the last two digits at least 01.
        yyyy, mm, dd = self._split_datestring(numeric_date)
        if mm in self._seasonToMonth.keys():
            normalised_alnum_date = '%s %s' % (self._dateConversions[mm], yyyy)
            normalised_num_date = '%s%s%s' % (yyyy, self._seasonToMonth[mm], dd)
        else:
            try:
                normalised_alnum_date = '%s %s, %s' % (self._dateConversions[mm], str(int(dd)), yyyy)
            except KeyError:
                self.msq.append_to_message("Malformed date segment in 947 line", self.gs4.originalCHLegacyID)
                log.error("Malformed date segment n 947 line: %s", self.gs4.originalCHLegacyID)
                raise SkipRecordException
            normalised_num_date = '%s%s%s' % (yyyy, mm, dd)
        self.gs4.normalisedAlphaNumericDate = normalised_alnum_date
        self.gs4.numericStartDate = normalised_num_date

    @staticmethod
    def _split_datestring(s):
        return [s[:-4], s[-4:-2], s[-2:]]

    def _insertRecordType(self):
        try:
            if self.gs4.legacyID.endswith('A'):
                object_type = ['Front Matter']
            elif self.gs4.legacyID.endswith('B'):
                object_type = ['Undefined']
            elif self.gs4.legacyID.endswith('C'):
                object_type = ['Back Matter']
            elif self.gen['245'].endswith('(Book Review)'):
                object_type = ['Review']
            # elif re.search(r'editorial', self.gen.f_245('a'), re.I):
            #     object_type = ['Editorial']
            else:
                object_type = ['Article']
            self.gs4.searchObjectType = object_type
        except AttributeError:
            print self.gs4.originalCHLegacyID
            print inspect.trace()
            raise

    def _servolumeissue(self):
        servoliss = self.gen.f_773('g').split()[0]
        series = int(self.gen['947'][11:16])
        if series > 0:
            self.gs4.series = 'Series %s' % series
        self.gs4.volume = str(int(self.gen['947'][17:21]))
        issue = int(self.gen['947'][22:26])
        if issue > 0:
            self.gs4.issue = str(issue)

        if re.search(r'(supplement|beiheft)', self.gen.f_773('g'), re.I):
            self.gs4.parentInfoSupplement = "Supplement"

        if re.search(r'(\[?(?:parts?|teil) .*\]?) \(.*?\)',
                     self.gen.f_773('g'), re.I):
            self.gs4.parentInfoPart = textUtils.xmlEscape(
                re.search(
                    r'(\[?(?:parts?|teil) .*\]?) \(.*?\)',
                    self.gen.f_773('g'), re.I).group(1))

    def _seriesvolumeissue(self):
        servoliss = self.gen.f_773('g').split()[0]
        series = int(self.gen['947'][17:21])
        volume = int(self.gen['947'][22:26])
        issue = int(self.gen['947'][27:31])
        #print series, volume, issue
        # try to figure out what the values from the $g subfield mean.
        if re.search(r'^\d+$', servoliss):
            # a number with no other characters. Can be either a volume or
            # issue enumeration. Need to check the corresponding portion of
            # the 947 line.
            if volume == 0:
                if servoliss == issue:
                    self.gs4.issue = str(servoliss)
            else:
                self.gs4.volume = str(servoliss)
        elif re.search(r'^\d+:', servoliss):
            try:
                vol, iss = servoliss.split(':')
            except ValueError:
                self.msq.append_to_message(
                    "Invalid series/volume/issue enumeration in 773",
                    "%s (%s)" % (self.gs4.originalCHLegacyID, servoliss)
                )
                log.error(
                    "%s: Invalid ser/vol/iss enumeration in 773 field (%s)",
                    (self.gs4.originalCHLegacyID, servoliss)
                )
                raise
            if volume == int(vol) and issue == int(iss):
                self.gs4.volume = vol
                self.gs4.issue = iss
        elif re.search(r'', servoliss):
            pass    
        
            
    def _startendpage(self):
        p_data = re.sub(r'\*', '', self.gen.f_773('g'))

        roman_re = re.compile(r'\(.*?\) (M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3}))(?:-)?(M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3}))?', re.I)
        numbered_pages_re = re.compile(r'\(.*\) (\[?[0-9]+\]?)(?:-)?(\[?[0-9]+\]?)?', re.I)
        page_names_re = re.compile(r'(inside ?)?(front|back) ?(cover)', re.I)
        frontispiece_re = re.compile('[Ff]rontis?piece')

        numbered_pages = numbered_pages_re.search(p_data)
        roman_numbered_pages = roman_re.search(p_data)
        named_pages = page_names_re.search(p_data)
        frontispiece = frontispiece_re.search(p_data)

        try:
            if named_pages:
                self.gs4.startpage = ' '.join([word.strip().capitalize() for word in named_pages.groups() if word is not None])
            elif numbered_pages:
                self.gs4.startpage = numbered_pages.group(1)
                self.gs4.endpage = numbered_pages.group(2)
            elif frontispiece:
                self.gs4.startpage = "Frontispiece"
            elif roman_numbered_pages:
                self.gs4.startpage = roman_numbered_pages.group(1)
                self.gs4.endpage = roman_numbered_pages.group(2)

        except Exception as e:  #pylint:disable=W0703
            print inspect.trace()
            print e
            exit()

    def _pagecount(self):
        if '900' in self.gen.keys():
            self.gs4.pageCount = self.gen.f_900('a')

    def _language(self):
        lang = self.gen['008'].split(' ')[-2].upper()
        if lang in self.languages.keys():
            lang = self.languages[lang]
        self.gs4.languageData = [{'langISOCode': lang}]

    def _buildContributors(self):
        contributors = []
        authIndex = 0
        contrib_descriptors = []
        if '100' in self.gen.keys():
            authIndex = authIndex + 1

            # Get the role information first...
            try:
                role_info = self.gen.f_100('e')
            except KeyError:
                role_info = None
            role, normalised_role = self._guess_role(role_info)
            if normalised_role is False:
                contrib_descriptors.append(role_info)

            # Now check for title ($c)
            try:
                title_info = self.gen.f_100('c')
            except KeyError:
                title_info = None
            title, normalised_title = self._guess_title(title_info)
            if normalised_title is False:
                contrib_descriptors.append(title_info)

            # And finally, check the affiliation ($u)
            try:
                aff_info = self.gen.f_100('u')
            except KeyError:
                aff_info = None
            aff, normalised_aff = self._guess_affiliation(aff_info)
            if normalised_aff is False:
                contrib_descriptors.append(aff_info)

            contributors.append({u'ContributorRole': role,  #self._guess_role(role_info)[0],
                                'ContribOrder': authIndex,
                                'contribvalue': {u'OriginalForm': self.cleanAndEncode(self.gen.f_100('a')),
                                                 u'PersonTitle': title,
                                                 u'ContribCompanyName': aff},
                                'ContribDesc': contrib_descriptors})
        if '700' in self.gen.keys():
#            print self.gen.f_700('e')
            for idx, item in enumerate(self.gen['700']):
                authIndex = authIndex + 1
#                print self._guess_role(self.gen.f_700('e')[idx])
                contributors.append({u'ContributorRole': 'Author', #self._guess_role(self.gen.f_700('e')[idx])[0],
                                     u'ContribOrder': authIndex,
                                     'contribvalue': self.cleanAndEncode(self.gen.f_700('a')[idx])})

        if '110' in self.gen.keys():
            authIndex = authIndex + 1
            contributors.append({u'ContributorRole': 'CorpAuthor',
                                 u'ContribOrder': authIndex,
                                 'contribvalue': {u'OrganizationName':
                                                  self.cleanAndEncode(self.gen.f_110('a'))}})

        if '710' in self.gen.keys():
            for item in self.gen['710']:
                authIndex = authIndex + 1
                contributors.append({u'ContributorRole': 'CorpAuthor',
                                     u'ContribOrder': authIndex,
                                     'contribvalue': {u'OrganizationName': self.cleanAndEncode(item[4:])}})

        self.gs4.contributors = contributors

    @staticmethod
    def _guess_role(string):
        if string is None:
            return ('Author', False)
        role = None
        try:
            role = re.search(r'(editor|compiler|translat[eo]r)(?:,|$)', string, re.I).group(1)
        except (KeyError, AttributeError):
            pass
        except Exception as e:
            print string
            print type(e)
            raise

        if role is None:
            role = 'Author'
            is_normalised = False
        else:
            if role.lower() == "translater".lower(): role = "translator"
            role = role.capitalize()
            is_normalised = True
        return (role, is_normalised,)

    @staticmethod
    def _guess_title(string):
        if string is None: return (None, False)
        title = None
        try:
            title = re.search(r'(Mr|Dr|Prof(essor)?)', string, re.I).group(1)
        except (KeyError, AttributeError):
            pass
        if title is None:
            return (None, False)
        else:
            return (title, True)


    @staticmethod
    def _guess_affiliation(string):   #pylint:disable=W0613
        #string.strip()
        return (None, False)

    def _legacyPubID(self):
        setattr(self, 'originalPubID', self._cfg['pruned_basename'])
        #self.gs4.journalID = ''.join([u'TST', self.productId.upper(), self.originalPubID])
        self.gs4.journalID = ''.join([self.productId.upper(), self.originalPubID])

    def _objectBundleData(self):
        if self.gen['090'][2:] == 'N':
            objectbundle = 'PIO'
        elif self.gen['090'][2:] == 'A':
            objectbundle = 'PAO'
        else:
            return
        self.objectBundleData(objectbundle)

    def _objectIDs(self):
        self.gs4.objectIDs = []
        self.gs4.objectIDs.append({'value': self.gs4.legacyID,
                                  u'IDOrigin': u'CH',
                                  u'IDType': u'CHLegacyID',})
        if '022' in self.gen.keys():
            # Sometimes, 022 has a $a subfield, and sometimes it doesn't...
            try:
                issn = self.gen.f_022('a')
            except KeyError:
                issn = self.gen.f_022()
            self.gs4.objectIDs.append({'value': issn,
                                        u'IDType': u'ISSN'})
        self.gs4.objectIDs.append({'value':     self.gs4.originalCHLegacyID,
                                   u'IDOrigin': unicode(self.productId),
                                   u'IDType':   u'CHOriginalLegacyID'})

        if self.has_weblink:
            escaped_url = urllib.quote_plus(self.gen.f_093('u').replace('http://', ''), safe='/:')
            self.gs4.objectIDs.append({'value': escaped_url,
                                       u'IDType': u'FullTextLinkID'})


    def _legacyParentID(self):
        # Take the article ID, remove the final group of digits. This leaves
        # journalID-year-volume-issue. To this, to distinguish supplements and parts,
        # add two more groups of digits. Or something.

        # Take the journal ID, year, volume and issue sections.
        parent_id_parts = self.gs4.originalCHLegacyID.split('-')[0:-1]

        # If the issue section is '00', take the month from the 947 field and use
        # it instead. This ensures that even journals with no issue level enumeration
        # in the legacy data get unique issue level group IDs for the new platform.
        if parent_id_parts[-1] == '00':
            parent_id_parts[-1] = self.gs4.numericStartDate[4:6]

        #parent_id_root = '-'.join(self.gs4.originalCHLegacyID.split('-')[0:-1])
        parent_id_root = '-'.join(parent_id_parts)
        if self.gs4.parentInfoSupplement:
            parent_id_root += '-01'
        else:
            parent_id_root += '-00'
        if self.gs4.parentInfoPart:
            enumeration = re.search(r'\[?(?:parts?|teil) ([^ \]/]+)', self.gs4.parentInfoPart, re.I).group(1)
            if re.search(r'[^0-9]+', enumeration):
                try:
                    enumeration = str(roman.fromRoman(enumeration))
                except roman.InvalidRomanNumeralError:
                    enumeration = str(enumeration)
            parent_id_root += '-%s' % enumeration.zfill(2)
        else:
            parent_id_root += '-00'
        self.gs4.legacyParentID = parent_id_root

    ## def _parentTitle(self):
    ##     if '490' in self.gen.keys():
    ##         #self.gs4.pubTitle = ' -- '.join([self.cleanAndEncode(val[4:]) for val in self.gen['490']])
    ##         self.gs4.pubTitle = ' -- '.join([self.cleanAndEncode(val) for val in self.gen['490']])

    def _insertFullText(self):
        # Records with open web links need to have dummy full text inserted.
        if self.has_weblink:
            self.gs4.textInfo = {'fullText': {'value': 'NNOOTT UUSSEEDD'}}
            return

        if not self.has_fulltext: return

        # Only try to get full text from the db if there is a db from which to get full text.
        # If there is none, set cached_ft to None. This is enough to fail the first if test,
        # and self.has_searchable_ft will return False, so we will then skip the else as well.
        try:
            cached_ft = self.ftcache[self.gs4.originalCHLegacyID]
        except AttributeError:
            cached_ft = None
        if cached_ft is not None:
            self.gs4.hiddenPlainText = bz2.decompress(cached_ft)
            log.info('Inserted cached full text for %s', self.gs4.originalCHLegacyID)
        else:
            #if os.path.exists(self.ftfile):
            if self.has_searchable_ft:
                hiddenText = []
                try:
                    try:
                        parser = ET.XMLParser(recover=True)
                        ftfile = ET.parse(self.ftfile, parser)
                    except ET.XMLSyntaxError:
                        parser = ET.XMLParser(recover=True, encoding='iso-latin-1')
                        ftfile = ET.parse(self.ftfile, parser)
                    for word in ftfile.xpath('//APS_word'):
                        try:
                            hiddenText.append(word.text)
                        except UnicodeDecodeError:
                            # Don't worry about unicode errors - just carry on
                            pass
                    concat_text = ' '.join([word for word in hiddenText if word is not None])
                    if len(concat_text) > 0:
                        self.gs4.hiddenPlainText = textUtils.xmlEscape(codecs.encode(concat_text, 'utf-8'))
                        self.ftcache[self.gs4.originalCHLegacyID] = bz2.compress(self.gs4.hiddenPlainText)
                        log.info('Inserted FT from SFT file for %s', self.gs4.originalCHLegacyID)
                    else:
                        log.info('No full text data in SFT file, %s', self.gs4.originalCHLegacyID)
                except ET.XMLSyntaxError as e:
                    self.msq.append_to_message("XML syntax error in full text file", "%s: %s" % (
                        self.gs4.originalCHLegacyID, self.ftfile))
                    log.error("%s: XML syntax error in ft file %s (%s)", self.gs4.originalCHLegacyID,
                        self.ftfile, e.message)
                    raise SkipRecordException
                except TypeError as e:
                    log.error('Invalid data: %s -> %s <%s>', self.gs4.originalCHLegacyID, e, hiddenText)
                    raise SkipRecordException
            else:
                log.info('No SFT file for %s', self.gs4.originalCHLegacyID)

    def _add_terms(self):
        if '600' in self.gen.keys():
            self.gs4.terms = []
            #print "TERMS: %s" % self.gen.f_600()
            for term in [t for t in self.gen.f_600('t') if t]:
                try:
                    term = codecs.decode(term, 'utf-8')
                except Exception as e:
                    raise
                    # TODO: figure out how to convert to UNICODE...
                    # print e
                    # print dir(e)
                    # print e.object
                    # print e.start
                    # print unichr(ord(e.object[e.start]))
                    # print e.reason

                self.gs4.terms.append(
                    {'TermType': 'FlexTerm',
                     u'values': {u'FlexTermValue': codecs.decode(term, 'utf-8')},
                     u'attrs': {u'FlexTermName': u'SubjWork'}}
                )
            for term in [t for t in self.gen.f_600('a') if t]:
                self.gs4.terms.append(
                    {'TermType': 'FlexTerm',
                     u'values': {u'FlexTermValue': codecs.encode(term, 'utf-8')},
                     u'attrs': {u'FlexTermName': u'SubjAuth'}}
                )

    def _components(self):
        # Get the Citation and Abstract components.
        AbstractMapping._components(self)

        # Now we need to add components specific to this record.
        representations = {'MultipleComponents': []}

        if self.gs4.hiddenPlainText:
            log.info('Inserting Component for Hidden Plain Text, %s', self.gs4.originalCHLegacyID)
            representations['MultipleComponents'].append(
                {u'Representation':
                     {u'RepresentationType': 'BackgroundFullText',
                      'values': {u'MimeType': u'text/xml',
                                 u'Resides': u'FAST'}}})
        if self.has_weblink:
            representations['MultipleComponents'].append(
                {u'Representation':
                    {u'RepresentationType': 'FullText',
                     'values': {u'MimeType': u'text/xml',
                                u'Resides': u'FAST'}}})

        if len(representations['MultipleComponents']) is not 0:
            self.gs4.components.append(self._buildComponent(u'FullText', representations))

        if '090' in self.gen.keys():
            self.gs4.preformattedComponents = []
            if self.has_fulltext:
                # We need to check the return value here, so we can short-circuit the
                # entire method if we get None back.
                pdfsize = self.pdfSizeEstimate(self.gs4.originalCHLegacyID)
                if pdfsize is None or pdfsize == '0':
                    log.info('Got None or 0 for PDF size for %s', self.gs4.originalCHLegacyID)
                    return
                legacyID = self.gs4.originalCHLegacyID
                self.gs4.preformattedComponents.append(
'''  <Component ComponentType="FullText">
    <CHImageIDs>
      <CHID>%s</CHID>
    </CHImageIDs>
    <Representation RepresentationType="PDFFullText">
      <MimeType>application/pdf</MimeType>
      <Resides>CH/PAO</Resides>
      <Color>%s</Color>
      <Options>PageRange</Options>
      <Bytes>%s</Bytes>
      <Scanned>true</Scanned>
      <CHImageHitHighlighting>true</CHImageHitHighlighting>
      <MediaKey>%s</MediaKey>
    </Representation>
  </Component>''' % (legacyID, self.color_or_grayscale,
                     pdfsize, self._mediaKey('pdf')))

                self.gs4.preformattedComponents.append(
'''  <Component ComponentType="Pages">
    <PageCount>%s</PageCount>
    <CHImageIDs>
      <CHID>%s</CHID>
    </CHImageIDs>
    <Representation RepresentationType="Normal">
      <MimeType>image/%s</MimeType>
      <Resides>CH/PAO</Resides>
      <Color>%s</Color>
      <MediaKey>%s</MediaKey>
    </Representation>
  </Component>''' % (self.gs4.pageCount, legacyID, self.jpeg_or_gif, self.color_or_grayscale,
                     self._mediaKey('page')))

    def pdfSizeEstimate(self, originalCHLegacyID):
        cachedValue = self.pdfsizecache[originalCHLegacyID]
        if cachedValue is None or cachedValue == '0':
            if cachedValue == '0':
                log.info('Got 0 for %s. Recalculating...', originalCHLegacyID)
            else:
                log.info('Got None for %s. Calculating...', originalCHLegacyID)
            try:
                imageFiles = self.threading_lines[originalCHLegacyID]
            except KeyError:
                log.info('No threading information for %s', originalCHLegacyID)
                return

            pdfSize = 0
            imgPath = '/sd/web/images/pcift'
            for image in imageFiles:
                try:
                    pdfSize += os.stat(imgPath + image)[ST_SIZE]
                except OSError:
                    log.info('Image file not found %s', imgPath + image)

            pdfSize = str(int(pdfSize * 1.1))
            if pdfSize > 0:
                self.pdfsizecache[originalCHLegacyID] = pdfSize
                log.info('Cached PDF size estimate for %s (%s)', originalCHLegacyID, pdfSize)
                return pdfSize
            else:
                log.info('PDF size estimate is 0 for %s', originalCHLegacyID)
                return None
        else:
            log.info('Using cached PDF size for %s (%s)', originalCHLegacyID, cachedValue)
            return cachedValue

    def _mediaKey(self, kind):
        mkroot = '/media/ch/pao/doc/%s' % self.gs4.originalCHLegacyID
        if kind == 'pdf':
            mkpath = '%s/doc.pdf' % mkroot
        elif kind == 'page':
            mkpath = '%s/page/pg.%s' % (mkroot, self.jpg_or_gif)
        return mkpath

    def __getattr__(self, attr):
        # If this is a colour journal, return the part before _or_,
        # otherwise, return the bit after _or_.
        if attr in ['color_or_grayscale', 'jpeg_or_gif', 'jpg_or_gif']:
            if self.isColour:
                return attr.split('_')[0]
            else:
                return attr.split('_')[2]
        else:
            super(self.__class__, self).__getattr__(attr)

    def visual_feedback_printid(self):
        return "%s/%s" % (self._cfg['basename'], self.legacyDocumentID)
