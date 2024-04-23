# -*- mode: python -*-

import sys, os

import ConfigParser

from confreader import ConfReader
from streams import streamregistry

# An object representing the transformation from a legacy format to GS4.

class Transformation(object):
    ''' Takes a dict object which should have values for product,
    stream, and an optional configfile. The configfile is used to look
    up the remaining settings required to build the Transformation and
    its contained Stream object. Which type of stream object is built
    depends on the value of streamtype in the config file section for
    the product.
    '''
    def __init__(self, cfg):
        self._cfg = cfg
        # defaultConfig = os.path.join(self._cfg['confdir'], 'cstore.config')
        # self._configfile = cfg['configfile'] if 'configfile' in cfg else defaultConfig

        # self._config = ConfigParser.ConfigParser()
        # self._config.read(self._configfile)

        self._config = ConfReader()

        try:
            for opt in self._config.options(self.product):
                self._cfg[opt] = self._config.get(self.product, opt)
        except ConfigParser.NoSectionError:
            print >> sys.stderr, "Couldn't find a config section for %s" % self.product
            print >> sys.stderr, "The following sections are currently configured:\n"
            for section in self._config.sections():
                print >> sys.stderr, "%s:\t%s" % (section, self._config.get(section, "description"),)
            print >> sys.stderr, "\nTo register a new transformation, write your mapping module,"
            print >> sys.stderr, "register it in the mappings registry, and add a configuration"
            print >> sys.stderr, "section to the configuration file,\n %s" % self._config.config_file_path
            print >> sys.stderr, "Don't forget to check in your changes and tell others!"
            exit(1)


        streamregistry.import_stream(self.streamtype)
        StreamProxy = sys.modules['StreamProxy']
        self._datastream = StreamProxy(self._cfg)

    def __getattr__(self, attrname):
        dictname = '_' + attrname
        if dictname in self.__dict__:
            return self.__dict__[dictname]
        elif attrname in self._cfg:
            return self._cfg[attrname]
        else:
            raise AttributeError('Instance has no attribute ' + attrname)
