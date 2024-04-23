# -*- mode: python -*-

''' Find and return the XPath patterns for the specified
product. Looks in the ../etc/cstore.config file  '''

from ConfigParser import NoOptionError
from commonUtils import fileUtils
from confreader import ConfReader

config = ConfReader()

# Return a dictionary of names and XPath expressions for the given
# product. The first time this is used, it stashes the resulting
# dictionary in _xpaths so we only load the external file once.
def get_xpaths(product):
    while True:
        try:
            return _xpaths
        except NameError:
            _xpaths = _build_xpaths(product)

# Build the lookup of names/XPaths for the given product. If no
# 'xpaths' key is found in the global config file section for
# [product], use the default 'aps.xpath' file.
def _build_xpaths(product):
    while True:
        try:
            return fileUtils.buildLut(config.get(product, 'xpaths'))
        except NoOptionError:
            return fileUtils.buildLut('aps.xpath')
