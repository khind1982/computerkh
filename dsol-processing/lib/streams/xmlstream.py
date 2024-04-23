# -*- mode: python -*-

import logging
import os

import lxml.etree as ET

from abstractrecord import AbstractRecord
from cstoreerrors import CStoreDataStreamError
from cstoreerrors import CStoreDataStreamSuffixError
from cstoreerrors import XmlStreamArgumentError
from streams.abstractstream import AbstractStream

log = logging.getLogger('tr.streams.xml')

class XmlStream(AbstractStream):
    def __init__(self, cfg):
        AbstractStream.__init__(self, cfg)
        self._stream = cfg['stream']
        try:
            self._docdelimiter = cfg['docdelimiter']
        except KeyError:
            raise XmlStreamArgumentError(
                'Required property missing: docdelimiter'
            )
        suffix = cfg['suffix'] if 'suffix' in cfg else '.xml'

        if os.path.isfile(self._stream):
            self._files = [self._stream]
        elif os.path.isdir(self._stream):
            self._files = [os.path.join(self._stream, fn) for fn in os.listdir(self._stream) if fn.endswith(suffix)]
            if len(self._files) == 0:
                raise CStoreDataStreamSuffixError(
                    'No files found ending with %s' % suffix
                )
        else:
            raise CStoreDataStreamError('Invalid data stream: %s' % self.stream)

        if 'file_checksum_check' in self._cfg.keys():
            if 'fulltext' in self._cfg['mappingOptions']:
                product = "%sft" % self._cfg['product']
            else:
                product = self._cfg['product']
            from dbcache import DBCacheManager
            self.file_checksum_cache = DBCacheManager(
                context="src_file_checksums",
                cachetype="src_file_checksums",
                filename=os.path.join(
                    self._cfg['ssroot'], '%s.file_checksums' % product
                )
            )


    def streamdata(self):
        '''Determine if the named stream is a single file, or
        a directory containing multiple files. Yields the XML record,
        to which it attaches the current file name and the current
        position in the stream to the caller.

        If self._cfg contains a key "file_checksum_check" containing a
        function, that function is used to calculate a checksum for
        each source file. This is then checked in a BSDDB file, by
        means of the DBCacheManager, to determine whether the file
        needs to be opened and streamed.

        '''

        for curFile in sorted(self._files):
            log.info("Starting file %s", curFile)

            if self._check_file_checksum(curFile) is False:
                log.info("File %s is unchanged. Skipping.", curFile)
                continue

            # iterparse returns a double. We are only interested in the
            # second element, so assign the first to _.
            try:
                for _, doc in ET.iterparse(curFile, tag=self._docdelimiter, remove_blank_text=True):
                    record = AbstractRecord(doc)
                    self._count += 1
                    self.set_filenames_in_config(curFile)
                    self._cfg['index'] = self._count
                    record.__dict__['_cfg'] = self._cfg
                    yield record
                    # clear the doc variable to conserve memory
                    doc.clear()
            except:
                #print curFile
                raise


    def _check_file_checksum(self, filename):
        if 'fileChecks' in self.streamOpts:
            return True
        try:
            fn = self._cfg['file_checksum_check']
        except KeyError:
            return True

        current_checksum = fn(filename)
        file_basename = os.path.basename(filename)
        if current_checksum == self.file_checksum_cache[file_basename]:
            return False
        else:
            self.file_checksum_cache[file_basename] = current_checksum
            return True
