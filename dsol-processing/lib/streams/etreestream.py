# -*- mode: python -*-

''' An input stream that reads one record from a file, and constructs
an xml.etree.ElementTree object from it.

'''

import logging
import os.path
import sys

import lxml.etree as ET

from abstractrecord import AbstractRecord
from streams.filestream import FileStream

log = logging.getLogger('tr.streams.etree')

class NullQueue(object):
    def append_to_message(self, *args):
        pass


class EtreeStream(FileStream):
    def __init__(self, cfg):
        super(self.__class__, self).__init__(cfg)
        if 'logger' in self._cfg:
            self.log = self._cfg['logger']
        else:
            self.log = log
        try:
            self.msq = self._cfg['msq']
        except KeyError:
            self.msq = NullQueue()

    def streamdata(self):
        for curFile in self._files:
            # pylint: disable = E1101
            if 'encoding' in self.streamOpts.keys():
                parser = ET.XMLParser(remove_blank_text=True,
                                      encoding=self.streamOpts['encoding'])
            else:
                parser = ET.XMLParser(remove_blank_text=True)

            try:
                record = AbstractRecord(ET.parse(curFile, parser).getroot())
            except IOError:
                self.log.warn(
                    "File %s doesn't exist. Perhaps it was deleted or renamed recently?",
                    curFile
                )
                continue
            except ET.XMLSyntaxError as e:
                self.log.warn(
                    "Invalid syntax in %s. Giving up on it. Message from lxml was '%s'",
                    curFile, e.msg)
                self.msq.append_to_message(
                    "Invalid input file (omitted from output)",
                    "%s: %s" % (os.path.basename(curFile), e.msg))
                continue
            except Exception as e:
                print >> sys.stderr, ("\n *** Error in %s:" % curFile)
                raise e

            self._count += 1
            self._cfg['files_in_stream'] = self.count
            self.set_filenames_in_config(curFile)
            self._cfg['index'] = self._count

            # For products where the source holds one record per file,
            # we can possibly speed things up a little by using the
            # source file's contents instead of the transformed record
            # to trigger steady state.

            #with open(curFile) as source:
            #    self._cfg['source_file_checksum'] = hashlib.sha512(source.read()).hexdigest() #pylint:disable=E1101
            record.__dict__['_cfg'] = self._cfg
            yield record
            del record
