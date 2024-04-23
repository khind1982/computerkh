# -*- mode: python -*-

import os.path
import sys

from commonUtils.fileUtils import buildLut
from confreader import ConfReader, NoOptionError

class CLI:
    def __init__(self, product=None, args=None):
        if product is None or args == []:
            CopyrightManager(None).usage()
        else:
            self.product = product
            self.cr_mgr = CopyrightManager(self.product)
            self.args = args
            if len(self.args) == 3:
                if self.args[0] == '-f':
                    self.cr_mgr.modify(key=self.args[1], value=self.args[2])
            elif len(self.args) == 2:
                if self.args[0] == 'del':
                    self.cr_mgr.remove(key=self.args[1])
                else:
                    self.cr_mgr.add(key=self.args[0], value=self.args[1])
            elif len(self.args) == 1:
                print self.cr_mgr.find(key=self.args[0])


class CopyrightManager:
    def __init__(self, product):
        self.product = product
        if product is not None:
            appconfig = ConfReader()
            if product not in appconfig.sections():
                raise RuntimeError("%s - unknown product code" % product)

            try:
                self.data_file = os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        '../libdata/epc_copyrights/%s' %
                        appconfig.get(product, 'copyright_lookup')))

                self.lookup_data = buildLut(self.data_file)
            except NoOptionError:
                raise RuntimeError(
                    "%s - product does not use a copyright lookup table" %
                    product)
                
    def usage(self):
        sys.stderr.write(
            'Usage: copyright <product> [-f] <jid> <"copyright text">\n')
        sys.stderr.write('       copyright <product> <jid>\n')
        sys.stderr.write('       copyright <product> del <jid>\n')
        sys.stderr.write('\n')

    def add(self, key, value):
        if key in self.lookup_data.keys():
            raise RuntimeError(
                "%s already in lookup. Use -f to force update." % key)
        self.modify(key, value)

    def modify(self, key, value):
        self.lookup_data[key] = value
        self.write_file()
        
    def remove(self, key):
        del self.lookup_data[key]
        self.write_file()

    def find(self, key):
        try:
            return "%s:\t%s" % (key, self.lookup_data[key])
        except KeyError:
            return "'%s' - not found" % key

    def write_file(self):
        with open(self.data_file, 'w') as f:
            f.write("# This file is managed by the copyright script.\n")
            f.write("# Beware of manually editing it!\n\n")
            for k in sorted(self.lookup_data.keys()):
                f.write("%s|%s\n" % (k, self.lookup_data[k]))
