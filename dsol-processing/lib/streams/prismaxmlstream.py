#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

import warnings
#import logging
from cstoreerrors import *

from xmlstream import XmlStream

# I know about the deprecations in Amara. Let's not clutter
# the terminal with warnings.
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from amara import binderytools

pqonly_logfile = open("/packages/dsol/var/log/pqonly.log", 'w')
overlap_logfile = open("/packages/dsol/var/log/pqoverlap.log", 'w')

class PrismaXmlStream(XmlStream):
    def __init__(self, cfg):
        XmlStream.__init__(self, cfg)

    def __del__(self):
        # Ensure the logfile gets flushed and closed properly.
        pqonly_logfile.close()
        overlap_logfile.close()

    def streamdata(self):
        ''' Determine if the named stream is a single file, or
        a directory containing multiple files. Yields the XML record,
        to which it attaches the current file name and the current 
        position in the stream to the caller. '''
        for curFile in sorted(self._files):
            for record in binderytools.pushbind(curFile, self._xpath):
                self._count += 1
                if record.xml_xpath('//*[@name="hapiid"]')[0] == '':
                    pqid = record.xml_xpath('//*[@name="pqid"]')[0]
                    pqonly_logfile.write(str(pqid) + '\n')
                    continue
                elif not record.xml_xpath('//*[@name="pqid"]')[0] == '':
                    pqid = record.xml_xpath('//*[@name="pqid"]')[0]
                    overlap_logfile.write(str(pqid) + '\n')
                self._cfg['filename'] = curFile
                self._cfg['index'] = self._count
                record.__dict__['_cfg'] = self._cfg
                yield record
