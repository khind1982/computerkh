# -*- mode: python -*-

from singleton import Singleton

# An abstract object to hold congifuration information about the stream being
# processed.

class Config(Singleton):
    def __init__(self, _dict=None):
        super(self.__class__, self).__init__()
        if _dict is not None:
            for k, v in _dict.items():
                self[k] = v

    def __contains__(self, item):
        if item in self.__dict__:
            return True
        else:
            return False

    def __setitem__(self, attr, value):
        self.__dict__[attr] = value

    def __getitem__(self, attr):
        return self.__dict__[attr]

    def insert_from_config_file(self, section):
        # section comes in as a list of 2-tuples from the
        # ConfigParser.items() method.
        for k, v in dict(section).items():
            self[k] = v
