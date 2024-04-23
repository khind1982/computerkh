# -*- mode: python -*-

"""
    A very simple wrapper class to encapsulate records from a stream
that don't have a built-in __dict__ object. We need to be able to
attach the _cfg dict to the record object somehow, so this is an easy
solution. As an example, records emitted by the etreestream need to be
wrapped, as the lxml.etree._ElementTree object doesn't have a
__dict__.
"""

class AbstractRecord(object):
    def __init__(self, data):
        self.__dict__ = {}
        self.__dict__['data'] = data
