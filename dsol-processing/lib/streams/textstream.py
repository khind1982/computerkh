#!/usr/local/bin/python2.6
# -*- mode: python -*-

''' This stream type takes plain text files (may be HTML or XML) and passes
each one up to the calling code. '''

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

import codecs

from streams.filestream import FileStream

from abstractrecord import AbstractRecord

class TextStream(FileStream):
    def __init__(self, cfg):
        super(TextStream, self).__init__(cfg)

    def streamdata(self):
        ''' '''
        for curFile in sorted(self._files):
            data = codecs.open(curFile, 'r').read()
            self._count += 1
            self._cfg['filename'] = curFile
            self._cfg['basename'] = os.path.basename(curFile)
            self._cfg['index'] = self._count
            record = AbstractRecord(data)
            record.__dict__['_cfg'] = self._cfg
            yield record
