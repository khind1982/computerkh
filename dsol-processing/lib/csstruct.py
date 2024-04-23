# -*- mode: python -*-
from commonUtils import textUtils
import codecs

class CSStruct(object):
    __init__ = lambda self, **kwargs: setattr(self, '__dict__', kwargs)
    def _fields(self):
        return [f for f in self.__dict__ if not f.startswith('_')]
    def __str__(self):
        string = u''
        for field in sorted(self._fields()):
            try:
                val = codecs.decode(self.__dict__[field], 'utf8')
            except UnicodeDecodeError:
                val = self.__dict__[field]
            except UnicodeEncodeError:
                val = codecs.encode(self.__dict__[field], 'utf8')
            except TypeError:
                val = str(self.__dict__[field])
            try:
                string += u"%s -> %s" % (unicode(field), unicode(val),)
            except UnicodeDecodeError:
                string += u'%s -> [unprintable on a terminal]' % field
            string += '\n'
        string = "(" + string.strip() + ")\n"
        return string

    fields = _fields

class LegacyRecord(CSStruct):
    # Return an empty string for any undefined attributes instead of bailing.

    def __getattr__(self, attrname):
        if attrname == 'fields':
            return self._fields()
        return u''

class GS4Record(CSStruct):
    def fields(self):
        return self._fields()
    def __getattr__(self, attrname):
        dictname = '_' + attrname
        if attrname == 'fields':
            raise AttributeError('Instance has no attribute ' + attrname)
