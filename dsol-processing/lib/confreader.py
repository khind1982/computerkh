# -*-  mode: python -*-

import os

from ConfigParser import ConfigParser, NoOptionError

class ConfReader(object): # pylint: disable = R0903
    def __init__(self, config_file_path=None):
        if config_file_path is None:
            self.config_file_path = os.path.normpath(
                os.path.join(os.path.dirname(__file__),
                             '..', 'etc', 'cstore.config')
            )
        else:
            self.config_file_path = config_file_path

        self.config = ConfigParser()
        self.config.read(self.config_file_path)

    def __getattr__(self, attr):
        return getattr(self.config, attr)
