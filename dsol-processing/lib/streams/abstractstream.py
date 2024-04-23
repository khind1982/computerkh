# -*- mode: python -*-

import os
import sys

class AbstractStream(object):
    def __init__(self, cfg):
        self._cfg = cfg
        self._stream = cfg['stream']
        self._count = 0
        self.streamOpts = {}
        self.parse_stream_opts()

    def __getattr__(self, attrname):
        dictname = '_' + attrname
        if dictname in self.__dict__:
            return self.__dict__[dictname]
        else:
            raise AttributeError('Instance has no attribute ' + attrname)

    def streamdata(self):
        ''' Subclasses need to know how to handle the stream logic. '''
        assert False, "Implement streamdata() in your subclass"

    def set_filenames_in_config(self, curFile):
        self._cfg['filename'] = curFile
        self._cfg['basename'] = os.path.basename(curFile)
        self._cfg['pruned_basename'] = os.path.splitext(self._cfg['basename'])[0]

        if 'product' not in self._cfg.keys():
            if self._cfg['pruned_basename'].startswith('APS_'):
                self._cfg['product'] = 'eima'
            else:
                self._cfg['product'] = self._cfg['pruned_basename'][:3].lower()

    def parse_stream_opts(self):
        if self._cfg['streamOpts'] is not None:
            try:
                for k, v in [opt.split('=') for opt in self._cfg['streamOpts'].split(',')]:
                    self.streamOpts[k] = v
            except ValueError:
                print >> sys.stderr, "stream options must be key=value pairs, separated by commas."
                print >> sys.stderr, "Spaces are not allowed."
                sys.exit(1)
