# -*- mode: python -*-
# pylint:disable=W0201, C0301, C0103, C0111, R0902, R0903, E1101

import atexit
import codecs
import hashlib
import lxml.etree as ET
import os
import re
import sys

from collections import defaultdict

from bsddb.db import DBNoSuchFileError
from ConfigParser import ConfigParser, NoSectionError

from commonUtils import fileUtils
from commonUtils.textUtils import cleanAndEncode as clean
from commonUtils.textUtils import xmlescape
from cstoreerrors import (
    PagefileEmptyWordError, RescaleFactorUndefinedError, CorruptXMLError
)
from cstoreerrors import ImageFileMismatchError
from dbcache import DBCacheManager
from xpaths import get_xpaths

conf_file = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../etc/cstore.config'))
config = ConfigParser()
config.read(conf_file)


def flush_pagefiles():
    # We can safely instantiate PagefileContainer with dummy arguments
    # since all we want to do is call the flush_pagefiles() method,
    # which clears the shared-state pagefiles directory, and doesn't
    # need real values to do so.
    PagefileContainer(None).flush_pagefiles()


atexit.register(flush_pagefiles)


class PagefileHandler(object):
    def __init__(self, document, articleid, product):
        self.document = Document(document, articleid, product)
        self.articleid = articleid
        self.product = product

    def update_or_create_pagefiles(self):
        self.document.update_pagefiles()

    def generate_hit_highlighting_tables(self):
        self.document.hit_highlighting()

# Document class holds the ElementTree instance, from which we can extract
# zones.
# We must also capture document-level metadata that needs to be specified with
# each zone:
#
# articleid (currently passed in explicitly, since we can't work out what it is
#  from the XML...)
# doctitle
# pcid

# We need access to the rescale factors for a page from multiple locations.
# Rather than passing it around, or assigning it everywhere it's needed,
# this class should be able to fetch the required value, given the page id
# and the type of rescale factor.


class RescaleCache(object):
    def __init__(self, pageid, which):
        dps = PageProperties(pageid)

        try:
            self.cachefile = DBCacheManager(
                '%s_%s' % (dps.journalid, dps.date), which,
                os.path.join(dps.rescalecacheroot, dps.journalid,
                             '%s.%s' % (dps.year, which)))
        except DBNoSuchFileError:
            print >> sys.stderr, \
                "\nDB cache file %s.%s does not exist for %s. Cannot continue." % (  # noqa
                dps.year, which, dps.journalid)
            exit(1)

    # Delegate all item access attempts to the underlying DBCacheManager
    # instance.
    def __getitem__(self, item):
        return self.cachefile[item]


class Properties(object):
    def __init__(self, subject):
        self.subject = subject
        self.product = os.environ.get('TR_PROD_NAME')
        # self.product = self.subject[0:3].lower()
        self.journalid = self.subject.split('_')[0]
        self.date = self.subject.split('_')[1].split('-')[0]
        while True:
            try:
                self.rescalecacheroot = config.get(
                    self.product, 'rescalecacheroot')
            except NoSectionError:
                self._setup_for_eima()
                continue
            break
        self.year = self.date[0:4]
        self.month = self.date[4:6]

    def _setup_for_eima(self): pass


class DocumentProperties(Properties):
    def __init__(self, documentid):
        self.documentid = documentid
        super(self.__class__, self).__init__(documentid)

    def _setup_for_eima(self):
        self.product = 'eima'


class PageProperties(Properties):
    def __init__(self, pageid):
        self.pageid = pageid
        super(self.__class__, self).__init__(pageid)
        if self.pageid.startswith('APS_'):
            self._setup_for_eima()

    def _setup_for_eima(self):
        self.product = 'eima'
        self.journalid = self.pageid.split('_')[1]
        self.date = self.pageid.split('_')[2].split('-')[0]
        self.year = self.date[0:4]


class Document(object):
    def __init__(self, xml, srcfile, product):
        self.product = product
        if self.product == "wgs":
            self.product = "lgb"
        if config.get(self.product, 'mappingname') in ['leviathan', 'gerritsen']:
            _rules = __import__('mappings.rules.LeviathanRules',
                                globals(), locals(),
                                ['title', 'articleid', 'pmid'], -1)
        else:
            _rules = __import__('mappings.rules.APSRules',
                                globals(), locals(),
                                ['title', 'articleid', 'pmid'], -1)
        self._title = _rules.title
        self._articleid = _rules.articleid
        self._pmid = _rules.pmid

        self.xml = xml
        self.srcfile = srcfile
        self.articleid = self._articleid(
            os.path.splitext(os.path.basename(self.srcfile))[0])
        self.issue = ('_').join(self.articleid.split('_')[0:-1])
        self.journalid = self._pmid(self.product, self.xml)
        self.apdf = _rules.apdf(self.product, self.xml)

        self.doc_level_attrs = {
            'coordstyle': config.get(self.product, 'coordstyle'),
            'doctitle':  self.doctitle,
            'articleid': self.articleid,
            'product':   self.product,
            'journalid': self.journalid,
            'srcfile':   self.srcfile,
            'apdf':      self.apdf,
        }

        images = [img.text for img
                  in self.xml.findall(get_xpaths(self.product)['images'])]
        imgset = [img.split('-')[0].replace('APS_', '') for img in images]
        if self.issue not in imgset:
            raise ImageFileMismatchError(
                'Doc ID %s,  image IDs %s' % (
                    self.articleid, ' '.join(images)))

        self.zones = [Zone(zone, self.doc_level_attrs) for zone
                      in self.xml.findall(
                          ".%s" % get_xpaths(self.product)['zone'])]

    @property
    def doctitle(self):
        return self._title(self.xml)

    # self.pages returns a list of Page objects, which represent
    # all the words for the current article split according to the
    # page on which they appear in the printed matter.
    @property
    def pages(self):
        while True:
            try:
                return self._pages
            except AttributeError:
                self._pages = []
                _pages_d = {}
                for zone in self.zones:
                    try:
                        _pages_d[zone.pageid] += zone.words
                    except KeyError:
                        _pages_d[zone.pageid] = zone.words
                    except AttributeError:
                        # An empty word in the source data can get us here...
                        pass
                for k, v in sorted(_pages_d.items()):
                    self._pages.append(Page(k, v))

    def update_pagefiles(self):
        for zone in self.zones:
            # Does the zone appear in its pagefile already?
            # If not, add it.
            # If it does, move on.
            # If there is no pagefile, create it and add the zone.

            zone.update_pagefile()

    @property
    def update_needed(self):
        # If GENMSMETADATA_REBUILD is set in the environment,
        # return True and cause hit highlighting files to be rewritten
        # if they already exist.
        if 'GENMSMETADATA_REBUILD' in os.environ.keys():
            print >> sys.stderr, "overwriting existing hit highlighting files."
            return True

        xmlfile_age = os.path.getmtime(self.srcfile)
        try:
            lockfile_age = os.path.getmtime(
                self.build_output_file_path('lock'))
        except OSError:
            # No lock file for this article id. Run the code to generate hit
            # highlighting.
            return True

        # If the xml source file is older than the lockfile (i.e., its
        # age is less), return False.
        # Otherwise, return True
        return xmlfile_age > lockfile_age

    def hit_highlighting(self):
        if self.update_needed:
            # word_offsets = {}
            word_offsets = defaultdict(list)
            page_offsets = ['0']
            article_word_coords = ''

            for page_count, page in enumerate(self.pages, start=1):
                image_file_name = page.pageid

                rescalecache = RescaleCache(image_file_name, 2880)

                page_word_coords = ''

                if len(page.words) > 0:
                    for word in page.words:
                        coords = {}
                        for k in word.abs_coords.iterkeys():
                            try:
                                coords[k] = str(int(int(word.abs_coords[k]) / float(rescalecache[image_file_name])))
                            except TypeError:
                                coords[k] = str(
                                    int(int(word.abs_coords[k]) / 1))
                                # print image_file_name
                                # print word.abs_coords[k]
                                # print rescalecache[image_file_name]
                                # raise

                        coords_for_display = "%s:%s:%s:%s" % tuple(
                            [str(coords[point]) for point
                             in ['ulx', 'uly', 'lrx', 'lry']])
                        # offset = self.offset(article_word_coords, page_word_coords)
                        word_offsets[word.text].append(
                            self.offset(article_word_coords, page_word_coords))
                        # try:
                        #     word_offsets[word.text].append(offset)
                        # except KeyError:
                        #     word_offsets[word.text] = [offset]
                        page_word_coords = ''.join(
                            [page_word_coords, "%s:%s\n" % (
                                word.text, coords_for_display)])

                    article_word_coords = ''.join(
                        [article_word_coords, page_word_coords])
                page_offsets.append(str(int(len(article_word_coords))))

            if len(article_word_coords) > 0:
                self.write_pos_file(article_word_coords)
                self.write_idx_file(page_offsets, page_count, word_offsets)
                self.create_lockfile()

    @staticmethod
    def offset(awc, pwc):
        return str(int(len(awc) + len(pwc)))

    def create_lockfile(self):
        while True:
            try:
                fileUtils.touch(self.build_output_file_path('lock'))
            except IOError:
                os.makedirs(os.path.dirname(
                    self.build_output_file_path('lock')))
                continue
            break

    def write_pos_file(self, word_coords):
        with self.open_pos_file() as outf:
            try:
                outf.write("%s" % word_coords)
            except (UnicodeDecodeError, UnicodeEncodeError):
                outf.write(codecs.encode(word_coords, 'UTF-8'))

    def write_idx_file(self, page_offsets, page_count, word_offsets):
        with self.open_idx_file() as outf:
            offsets_for_all_pages = ':'.join(page_offsets)
            outf.write("%s:%s:\n" % (str(page_count), offsets_for_all_pages))
            for word in sorted(word_offsets.keys()):
                try:
                    outf.write(
                        "%s:%s\n" % (word, ':'.join(word_offsets[word])))
                except (UnicodeDecodeError, UnicodeEncodeError):
                    outf.write(
                        "%s:%s\n" % (codecs.encode(word, 'UTF-8'),
                                     ':'.join(word_offsets[word])))

    def open_pos_file(self):
        return self.open('pos')

    def open_idx_file(self):
        return self.open('idx')

    def open(self, extension):
        filename = self.build_output_file_path(extension)
        directory = os.path.dirname(filename)
        while True:
            try:
                return open(filename, 'w')
            except IOError:
                os.makedirs(directory)

    def build_output_file_path(self, extension):
        dps = DocumentProperties(self.articleid)
        if extension == 'lock':
            fileroot = os.path.abspath(
                os.path.join(config.get(self.product, 'pagefileroot'),
                             '..', '.lock', self.product))
        else:
            fileroot = config.get(self.product, 'msroot')
        directory = os.path.join(
            fileroot, self.journalid, dps.year, dps.month, 'coords')
        filename = '.'.join([self.articleid, extension])
        return os.path.join(directory, filename)


class Page(object):
    def __init__(self, pageid, words):
        self.pageid = pageid
        self.words = words


# Encapsulates each zone in a Document instance. Note that we pass in
# document-level values in a dictionary, and use __getattr__ to allow
# access as though they were defined on Zone itself.

class Zone(object):
    def __init__(self, xml, doc_level_attrs):
        self.xml = xml
        self.doc_level_attrs = doc_level_attrs
        # self.pageid = self.xml.find(
        #     get_xpaths(self.product)['images']).text.split('.')[0]
        self.pageid = self.xml.find(
            get_xpaths(self.product)['images']).text[:-4]
        self.pcid = self.pageid.split('-')[0].replace('APS_', '')
        self.pagenumber = self.xml.xpath(
            get_xpaths(self.product)['page_number'])[0].text
        self.pagesequence = self.xml.xpath(
            get_xpaths(self.product)['page_sequence'])[0].text
        self.checksum = hashlib.sha256(
            ET.tostring(self.xml)).hexdigest()
        self.pagefile = PagefileContainer(self.pcid).get_pagefile_for_zone(
            self.pageid, self.journalid,
            self.product, self.coordstyle)

    def __getattr__(self, attr):
        if attr in self.doc_level_attrs.keys():
            # ['doctitle', 'articleid', 'product', 'journalid', 'coordstyle']
            return self.doc_level_attrs[attr]
        else:
            raise AttributeError('Zone object has no attribute "%s"' % attr)

    @property
    def coords(self):
        zc = {}
        try:
            zc['top'] = zc['uly'] = self.xml.xpath(
                get_xpaths(self.product)['zculy'])[0].text
            zc['left'] = zc['ulx'] = self.xml.xpath(
                get_xpaths(self.product)['zculx'])[0].text
            zc['bottom'] = self.xml.xpath(
                get_xpaths(self.product)['zclry'])[0].text
            zc['right'] = self.xml.xpath(
                get_xpaths(self.product)['zclrx'])[0].text
        except KeyError:
            # The Leviathan approach to zone coords is not compatible
            # with the above block of code. If a KeyError is raised,
            # it means that XPaths for the individual coords are not
            # available, so revert to using the zonecoords XPath and
            # extract values from its attributes.
            zc['top'] = zc['uly'] = self.xml.xpath(
                get_xpaths(self.product)['zonecoords'])[0].attrib['uly']
            zc['left'] = zc['ulx'] = self.xml.xpath(
                get_xpaths(self.product)['zonecoords'])[0].attrib['ulx']
            zc['bottom'] = self.xml.xpath(
                get_xpaths(self.product)['zonecoords'])[0].attrib['lry']
            zc['right'] = self.xml.xpath(
                get_xpaths(self.product)['zonecoords'])[0].attrib['lrx']

        return zc

    @property
    def words(self):
        while True:
            try:
                return self._words
            except AttributeError:
                self._words = []
                for _word in self.xml.xpath(get_xpaths(self.product)['word']):
                    if self.coordstyle == "relative":
                        parent_coords = self.coords
                    else:
                        parent_coords = None
                    try:
                        self._words.append(
                            Word(_word, get_xpaths(self.product),
                                 parent_coords))
                    except (IndexError, PagefileEmptyWordError):
                        continue
                    except CorruptXMLError as e:
                        # we need to attach the failing word's APS_word
                        # element, so it's easier to track down the problem in
                        # the source data.
                        # Simply modify the exception message, and reraise the
                        # error.
                        e = "%s, zone:\n%s" % (
                            e, ET.tostring(_word, pretty_print=True))
                        raise CorruptXMLError(e)

    def update_pagefile(self):
        # Get the current zone's pagefile
        try:
            if self.checksum not in self.pagefile.checksums:
                self.pagefile.append_zone(self)
        except TypeError:
            self.pagefile.create_new_pagefile(self)

    @property
    def element(self):
        zoneE = ET.Element('zone', {'articleid': self.articleid})
        ET.SubElement(zoneE, 'zonesha256').text = self.checksum
        title = ET.SubElement(zoneE, 'article_title')
        title.text = xmlescape(self.doctitle)
        ET.SubElement(zoneE, 'zonecoords', self.coords)

        for _word in self.words:
            zoneE.append(_word.element)
        return zoneE


# Word - represents the APS_word elements from the source

class Word(object):
    def __init__(self, xml, xpaths, parent_coords=None):
        self.xml = xml
        self.xpaths = xpaths
        self.parent_coords = parent_coords
        self.coords = self.xml.xpath(self.xpaths['wordcoords'])[0].attrib
        self.text = self._text
        self.rawtext = self.xml.find(self.xpaths['wordtext']).text
        self.rawxml = ET.tostring(self.xml, pretty_print=True)

    @property
    def _text(self):
        try:
            _text = codecs.encode(
                self.xml.find(self.xpaths['wordtext']).text.lower(), 'UTF-8')
            _text = re.sub(r'\W', '', _text, re.U)
            # Remove "'s"
            _text = re.sub(r"'s$", '', _text)
            # Remove trailing '.'
            _text = re.sub(r'\.$', '', _text)

            # Remove characters in the control block...
            for _range in [range(0x00, 0x1f), range(0x7f, 0x9f)]:
                for char in _range:
                    _text = _text.replace(chr(char), '')

            # ... and the non-breaking space.
            _text = _text.replace(chr(0xa0), '')

            _text = _text.replace("%s%s" % (chr(0xc2), chr(0xbb)), chr(0xbb))
        except TypeError:
            raise PagefileEmptyWordError
        if _text == '':
            raise PagefileEmptyWordError
        try:
            return clean(_text)
        except UnicodeDecodeError as e:
            raise CorruptXMLError("%s (ignored, text is %s)" % (e, _text))

    @property
    def element(self):
        elem = ET.Element('word', self.coords)
        try:
            elem.text = self.text   # codecs.decode(self.text, 'UTF-8')
        except ValueError as e:
            raise CorruptXMLError(e)
        return elem

    @property
    def abs_coords(self):
        # If the current instance was instantiated with a non-None
        # value for parent_coords, return self.coords altered to
        # represent absolute coordinates. If parent_coords was
        # None, assume the content uses absolute coords and
        # simply return self.coords unaltered.
        if self.parent_coords is None:
            return self.coords

        while True:
            try:
                return self._abs_coords
            except AttributeError:
                self._abs_coords = {
                    'ulx': int(
                        self.coords['ulx']) + int(self.parent_coords['ulx']),
                    'uly': int(
                        self.coords['uly']) + int(self.parent_coords['uly']),
                    'lrx': int(
                        self.coords['lrx']) + int(self.parent_coords['ulx']),
                    'lry': int(
                        self.coords['lry']) + int(self.parent_coords['uly']),
                }


# Pagefile - responsible for parsing and updating pagefiles on disk

class Pagefile(object):
    def __init__(self, pageid, product, path, coordstyle):
        self.pageid = pageid
        self.product = product
        self.relpath = path
        self._memo = {}
        self.path = os.path.join(
            config.get(self.product, 'pagefileroot'), self.relpath)
        self.journalid = self.relpath.split('/')[0]
        self.year = self.date[0:4]
        self.month = self.date[4:6]
        self.coordstyle = coordstyle
        self.xml = self.parse_pagefile()
        self.changed = False

        # If GENMSMETADATA_REBUILD is set in the environment,
        # delete anything at self.path, if it exists.
        if 'GENMSMETADATA_REBUILD' in os.environ.keys():
            try:
                print >> sys.stderr, "removing old pagefile..."
                os.unlink(self.path)
            except OSError:
                # File doesn't exist.
                pass

    def parse_pagefile(self):
        try:
            return ET.parse(self.path, ET.XMLParser(remove_blank_text=True))
        except IOError:
            return None

    @property
    def date(self):
        return self.relpath.split('/')[1].split('_')[1]

    @property
    def checksums(self):
        try:
            return [elem.text for elem in self.xml.xpath('//zonesha256')]
        except AttributeError:
            return None

    def create_new_pagefile(self, zone):
        setattr(self, 'rescalecache_700', RescaleCache(self.pageid, 700))
        setattr(self, 'rescalecache_2880', RescaleCache(self.pageid, 2880))

        rescale_700 = self.rescalecache_700[self.pageid]
        rescale_2880 = self.rescalecache_2880[self.pageid]

        try:
            pfroot = ET.Element('page',
                                {'id': self.pageid,
                                 'rescale700': rescale_700,
                                 'rescale2880': rescale_2880})
        except TypeError:
            print "self.pageid: %s, 700: %s, 2880: %s" % (
                self.pageid, rescale_700, rescale_2880)
            raise RescaleFactorUndefinedError(
                'No rescale factor for page with id %s' % self.pageid)
        self.xml = pfroot
        ET.SubElement(pfroot, 'journalid').text = zone.journalid
        ET.SubElement(pfroot, 'product').text = zone.product
        ET.SubElement(pfroot, 'apdf').text = zone.apdf
        ET.SubElement(pfroot, 'date').text = '%s/%s' % (self.year, self.month)
        ET.SubElement(pfroot, 'pagenumber').text = zone.pagenumber
        ET.SubElement(pfroot, 'pagesequence').text = zone.pagesequence
        ET.SubElement(pfroot, 'pcid').text = zone.pcid
        ET.SubElement(pfroot, 'zones', {'coordstyle': self.coordstyle})
        self.append_zone(zone)

    def append_zone(self, zone):
        zones = self.xml.xpath('//zones')[0]
        try:
            zones.append(self.zone_element(zone))
        except TypeError:
            pass

    def zone_element(self, zone):
        self.changed = True
        try:
            return zone.element
        except AttributeError:
            # If we don't get a value for zone.element, we are looking
            # at a zone in the source XML that contains an empty
            # APS_word/APS_text element, which results in
            return

    def write(self):
        if self.changed is True:
            parent_directory = os.path.dirname(self.path)
            if not os.path.isdir(parent_directory):
                os.makedirs(parent_directory)
            with open(self.path, 'w') as outf:
                outf.write(ET.tostring(self.xml, xml_declaration=True,
                                       encoding='UTF-8', pretty_print=True))


# A simple container class that holds mutliple instances of Pagefile.
# This allows us to manipulate pagefiles in memory, without having
# to constantly read, parse and write them on disk. When the pcid
# changes, we close all currently held pagefiles to avoid running
# out of memory and available file handles.

class PagefileContainer(object):
    __dict = {
        'pagefiles': {},
        'pcid': '',
        }

    # By passing in the pcid to the constructor, we can trigger
    # flushing the cache without needing to explicitly call it
    # elsewhere.
    def __init__(self, pcid):
        self.__dict__ = self.__dict
        if pcid != self.pcid:
            self.flush_pagefiles()
            self.pcid = pcid

    def get_pagefile_for_zone(self, pageid, journalid, product, coordstyle):
        while True:
            try:
                return self.pagefiles[pageid]
            except KeyError:
                pagefile_path = os.path.join(journalid, self.pcid,
                                             '%s.xml' % pageid)
                self.pagefiles[pageid] = Pagefile(pageid, product,
                                                  pagefile_path, coordstyle)

    def flush_pagefiles(self):
        for pagefile in self.pagefiles.keys():
            self.pagefiles[pagefile].write()
            del self.pagefiles[pagefile]
