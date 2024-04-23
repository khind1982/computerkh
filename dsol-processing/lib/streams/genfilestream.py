# -*- mode: python -*-

'''
This stream is for the PIO GEN file transformation
'''

import codecs
import sys

#import logging
#log = logging.getLogger('tr.streams.etree')

from streams.filestream import FileStream
from abstractrecord import AbstractRecord

#from dbcache import DBCacheManager

class GenFileStream(FileStream):
    def __init__(self, cfg):
        super(self.__class__, self).__init__(cfg)

    def streamdata(self, **kwargs):
        for curFile in self._files:
            self.new_record()
            with open(curFile) as readfile:
                for line in readfile:
                    try:
                        k, v = line.split(' ', 1)
                    except ValueError:
                        if line.strip() == '':
                            continue
                        else:
                            print >> sys.stderr, "Data error in %s, line containing '%s'" % (curFile, line.strip())
                            raise
                    v = v.strip()
                    if k == '947':
                        self.insertValue(k, v)
                        self._count += 1
                        # Set the filename related keys in _cfg
                        self.set_filenames_in_config(curFile)
                        self._cfg['index'] = self._count
                        self.record.__dict__['_cfg'] = self._cfg
                        yield self.record
                        self.new_record()
                    else:
                        self.insertValue(k, v)

    def insertValue(self, k, v):
        if not k == '035':
            try:
                v = codecs.decode(v, 'utf-8')
            except UnicodeDecodeError:
                v = v
        if k in ['600', '700', '710']:
            try:
                self.record.data[k].append(v)
            except KeyError:
                self.record.data[k] = [v]
        # If we have a 490, remove the leading "0 $a"
        elif k == '490':
            try:
                self.record.data[k].append(v[4:])
            except KeyError:
                self.record.data[k] = [v[4:]]
        else:
            self.record.data[k] = v

    def new_record(self):
        setattr(self, 'record', AbstractRecord({}))
