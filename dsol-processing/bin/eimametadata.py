#!/usr/local/bin/python2.6
# -*- mode: python -*-
# pylint:disable=W0201,W0212

import sys, os, re
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib'))

import codecs

##from sqlalchemy import orm, MetaData, create_engine
#from sqlalchemy.ext.sqlsoup import SqlSoup

from optparse import OptionParser

from streams.etreestream import EtreeStream
from commonUtils.listUtils import uniq

RESIZE_FACTORS = {}

def get_resize_factors(file_path):
    ''' Calculate the factor by which images have been resized. These
    values are stored and used later to calculate the correct values
    for the coordinate points. '''
    with open(file_path) as resize:
        for line in [line.strip() for line in resize]:
            filename, original, new = line.split()
            RESIZE_FACTORS[filename.split('/')[-1].split('.')[0]] = \
                float(original)/float(new)


##Session = orm.sessionmaker()

# class DBConn(object):
#     __state = {
#         'dbconn': SqlSoup('mysql://root:@mysql-server/eima')
#         }
#     def __init__(self, state=None):
#         if state is not None:
#             self.__dict__ = state
#         else:
#             self.__dict__ = self.__state




# #     # Holds the connection to the database, and all associated
# #     # SQLAlchemy bits.
# #     __state = {
# #         'metadata': MetaData(),
# #         'engine': create_engine('mysql://root:@mysql-server/eima'),
# #         'session': Session()
# #         }

# #     def __init__(self, state=None):
# #         if state is not None:
# #             self.__dict__ = state
# #         else:
# #             self.__dict__ = self.__state
        
# #         self.metadata.reflect(bind=self.engine)
# #         self.session.configure(bind=self.engine)
# #         self.tables = self.metadata.tables
        

class EIMAPageCollection(object):
    ''' Holds an instance of EIMADocument for each document in the 
    directory '''
    def __init__(self):
        pass

class EIMADocument(object):
    ''' Represents the contents of an EIMA document file '''
    def __init__(self, record):
        #self.dbconn = DBConn()

        self.src_filename = record._cfg['filename']
        self.dest_root = record._cfg['dest_root']
        self.raw_record = record
        self.record_filename = record._cfg['basename']

        self.identifier = os.path.splitext(self.record_filename)[0].replace('APS_', '')
        self.cover_date = self._get_element_text_or_default('*/APS_date_8601')
        self.title = self._get_element_text_or_default('APS_title', default="[UNTITLED]")
        self.pmid = self.identifier[0:6]
        self.pcid = ('').join(self.identifier.split('_'))
        self.issue_path = os.path.join(self.dest_root, self.pmid, self.cover_date[0:4], self.cover_date[4:6])
        self.page_images = uniq(sorted([image.text for image in self.raw_record.data.xpath('//APS_page_image')]))

        # Within each zone, the zone coordinates are in //APS_zone_coord/APS_ULX,APS_ULY,APS_LRX,APS_LRY
        self.zones = [PageZone(_zone) for _zone in self.raw_record.data.xpath('.//APS_zone')]

    @property
    def pages(self):
        while True:
            try:
                return self._pages
            except AttributeError:
                self._pages = {}
                for zone in self.zones:
                    for word in zone.words:
                        try:
                            self._pages[word.page].append(word)
                        except KeyError:
                            self._pages[word.page] = [word]

    def _get_element_text_or_default(self, xpath, default=None):
        try:
            return self.raw_record.data.xpath(xpath)[0].text
        except IndexError:
            # If there is no suitable default, reraise the exception that got us here...
            if default is None:
                raise
            return default

    def do_threading_map(self):
        self.threadingmap = ThreadingMap(self).pages
        tf_file = ThreadingFile(self.issue_path, self.cover_date)
        tf_file.write(self.threading_data)

    @property
    def threading_data(self):
        ret = ''
        for image in [page for page in self.threadingmap]:
            ret += "%s\t%s\n" % (self.identifier, image)
        return ret

    def do_coords_map(self):
        # get the word coords data from the words in each zone of the doc.
        # build the coords map.
        # rewind and work out the idx map.
        word_offsets = {}
        page_offsets = ['0']
        page_count = 0
        wcf = WordCoordsFile(self.issue_path, self.identifier)
        for p in sorted(self.pages.keys()):
            page = self.pages[p]
            page_count += 1
            if len(page) > 0:
                for word in page:
                    if not word.value.strip() == '':
                        offset = str(int(wcf.tell()))
                        try:
                            word_offsets[word.sanitized_value].append(offset)
                        except KeyError:
                            word_offsets[word.sanitized_value] = [offset]
                        wcf.write("%s\n" % word.value_and_coords)
            page_offsets.append(str(int(wcf.tell())))

        # This if block needs to be at the same indent level as the
        # outer for block above (i.e. for p in self.pages)
        if len(page_offsets) > 1:
            offsets_for_all_pages = (':').join(page_offsets)
            wci = WordCoordsIndex(self.issue_path, self.identifier)
            wci.write("%s:%s:\n" % (str(page_count), offsets_for_all_pages))
            for word in sorted(word_offsets.keys()):
                offsets = (':').join(word_offsets[word])
                wci.write("%s:%s\n" % (word, offsets))

        ## Now insert the IDs and paths into the SQL database. What fun...
        #print dir(self.dbconn)

class ThreadingMap(object):
    def __init__(self, doc):
#        print doc
        self.pages = doc.page_images
#        print "pages = %s" % self.pages


class PageZone(object):
    # Represents the zone coordinates for each zone in the document.
    def __init__(self, xml):
        self.xml = xml

        # The name of the image file where this zone is found.
        self.page = self.xml.xpath('APS_page_image')[0].text        
        self.zone_type = self.xml.xpath('@type')[0]
        self.coords = {}
        for coord in ['ulx', 'uly', 'lrx', 'lry']:
            self.coords[coord] = xml.xpath('.//APS_%s' % coord.upper())[0].text

        # A list of all words in the document. Pass in self.coords, because
        # each word needs to report its absolute coordinates.
        self.words = [APSWord(_word, self) for _word in xml.xpath('.//APS_word')]

    def __str__(self):
        return "%s: coords %s, page %s" % (self.zone_type, self.coords, self.page)

class APSWord(object):
    # zone_coords is a dict containing the parent zone's coordinates. 
    # This hack is needed so we can calculate the absolute values of the
    # word level coords (the supplied data provides word coords relative
    # to the containing zone)
    def __init__(self, xml, zone):
        self.xml = xml
        self.parent_zone = zone
        self.coords = xml.xpath('APS_wc')[0].attrib
        self.value = self.xml.xpath('APS_text')[0].text
        self.page = self.parent_zone.page

    def __str__(self):
        return self.sanitized_value  #self.xml.xpath('APS_text')[0].text

    # Return the word, lower-cased, with punctuation removed and
    # extended characters normalised.
    @property
    def sanitized_value(self):
        while True:
            try:
                return self._sanitized_value
            except AttributeError:
                # Remove these punctuation characters from the string
                self._sanitized_value = re.sub(r'["~/$^(){};,\\?-]', '', self.value)
                # Removed these from the end:
                self._sanitized_value = re.sub(r"[.,:;!']$", '', self._sanitized_value)
                # And remove these from the beginning:
                self._sanitized_value = re.sub(r"^['.]", '', self._sanitized_value)
                # And finally convert to lower case:
                self._sanitized_value = codecs.encode(self._sanitized_value.lower(), 'utf-8')

    # Return the calculated absolute coordinates as a list.
    # Calculate it first, if necessary, and store it on self.
    @property
    def abs_coords(self):
        while True:
            try:
                return self._abs_coords
            except AttributeError:
                # 
                abs_coords = {
                    'ulx': int(self.coords['ulx']) + int(self.parent_zone.coords['ulx']),
                    'uly': int(self.coords['uly']) + int(self.parent_zone.coords['uly']),
                    'lrx': int(self.coords['lrx']) + int(self.parent_zone.coords['ulx']),
                    'lry': int(self.coords['lry']) + int(self.parent_zone.coords['uly']),
                    }
                self._abs_coords = ':'.join([str(abs_coords[point]) for point in ['ulx', 'uly', 'lrx', 'lry']])

    # Return the sanitized representation of the word itself, followed by
    # the four coord points returned by the abs_coords property.
    @property
    def value_and_coords(self):
        return "%s:%s" % (self.sanitized_value, self.abs_coords)

class MediaServiceMetaDataFile(object):
    filename = ''
    __sharedState = {
        'suffix': 'txt',
        'subDirPath': '',
        'filename': filename,
        'filehandle': ''
        }
    def __init__(self, state=None):
        if state is not None:
            self.__dict__ = state
        else:
            self.__dict__ = self.__sharedState
        self.output_directory = os.path.join(self.issue_path, self.subDirPath)

    def __getattr__(self, attr):
        if attr in self.__dict__.keys():
            return self.__dict__[attr]
        elif attr in self.__sharedState.keys():
            return self.__sharedState[attr]

    def setup(self, filename):
        if not filename == self.filename:
            self.filename = "%s.%s" % (filename, self.suffix)
            self.rotate()

    def rotate(self):
        self.close()
        self.open()

    def close(self):
        try:
            self.filehandle.close()
        except:
            pass

    def open(self):
        while True:
            try:
                self.filehandle = open(os.path.join(
                        self.output_directory, self.filename), 'w')
            except IOError:
                os.makedirs(self.output_directory)
                continue
            break

    def write(self, data):
        self.filehandle.write(data)
        self.filehandle.flush()

class ThreadingFile(MediaServiceMetaDataFile):
    _myState = {
        'subDirPath': '',
        'suffix': 'txt',
        'fileCache': [],
        }

    def __init__(self, issue_path, filename):
        self._myState['issue_path'] = issue_path
        super(self.__class__, self).__init__(self._myState)
        self.setup(filename)

    def open(self):
        if not self.filename in self.fileCache:
            self.fileCache.append(self.filename)
            self.filehandle = []
        else:
            self.filehandle = [line for line in codecs.open(os.path.join(
                        self.output_directory, self.filename), 'r', 'utf8')]

    def write(self, data):
        self.filehandle.append(data)
        while True:
            try:
                with codecs.open(os.path.join(
                        self.output_directory, self.filename),
                                 'w', 'utf8') as output_file:
                    output_file.write(('').join(self.filehandle))
            except IOError:
                os.makedirs(self.output_directory)
                continue
            break

class WordCoordsFile(MediaServiceMetaDataFile):
    ''' Word coordinates output file handler. '''
    _myState = {
        'subDirPath': 'coords',
        'suffix': 'pos',
        'fileCache': [],
        }
    def __init__(self, issue_path, filename):
        self._myState['issue_path'] = issue_path
        super(self.__class__, self).__init__(self._myState)
        self.setup(filename)

    # Another case where the output file is not guaranteed to be written in one
    # pass. Due to differences in the contents of the files, we can't easily
    # share the implementation with ThreadingFile, above.
    def open(self):
        if not self.filename in self.fileCache:
            self.fileCache.append(self.filename)
            self.filehandle = []
        else:
            self.filehandle = open(os.path.join(
                    self.output_directory, self.filename), 'r').readlines()

    def write(self, data):
        self.filehandle.append(data)
        while True:
            try:
                with open(os.path.join(
                        self.output_directory, self.filename),
                          'w') as output_file:
                    for line in [line.strip() for line
                                 in self.filehandle if not line.strip() == '']:
                        print >> output_file, line
            except IOError:
                os.makedirs(self.output_directory)
                continue
            except:
                print self.filehandle
                raise
            break

    # We need some way of working out how big the file has got so far, so we can
    # correctly insert the byte offset where required. This is not most elegant
    # solution, but given the way we build output files, is the best fit.
    def tell(self):
        ''' Get the position in the current file. '''
        try:
            with open(os.path.join(
                    self.output_directory, self.filename),
                      'r') as output_file:
                output_file.readlines()
                offset = output_file.tell()
        except IOError:
            offset = '0'
        return offset


class WordCoordsIndex(MediaServiceMetaDataFile):
    ''' Word coordinates index output file handler. '''
    _myState = {
        'subDirPath': 'coords',
        'suffix': 'idx',
        }
    def __init__(self, issue_path, filename):
        self._myState['issue_path'] = issue_path
        super(self.__class__, self).__init__(self._myState)
        self.setup(filename)


if __name__ == '__main__':
    optparser = OptionParser()
    optparser.add_option('-s', dest='data_root', default=None)
    optparser.add_option('-r', dest='resizedImages', default=None)
    optparser.add_option('-d', dest='dest_root', default=None)
    (options, args) = optparser.parse_args()

    if options.dest_root is None:
        print >> sys.stderr, ("Must supply an output directory with the -d flag")
        exit(1)

    if options.data_root is None:
        streamOpts = None
    else:
        streamOpts = "dataRoot=%s" % options.data_root
    path = args[0]

    if options.resizedImages is not None:
        get_resize_factors(options.resizedImages)
    else:
        print >> sys.stderr, "must supply path to image scaling information"
        exit(1)

    for count, record in enumerate(EtreeStream({'stream': path, 'streamOpts': streamOpts}).streamdata(), start=1):
        record._cfg['dest_root'] = options.dest_root
        doc = EIMADocument(record)
        curFile = record._cfg['filename']
        curFileBase = curFile.split('/')[-1]
        doc.do_threading_map()
        doc.do_coords_map()

        sys.stdout.write('\r\033[0K')
        sys.stdout.write('\033[92mSeen\033[0m \033[91m%s (of %s)\033[0m \033[92mrecords.\033[0m \033[93m(\033[0m\033[94m%s\033[0m)' % (count, record._cfg['filesInStream'], curFileBase))

