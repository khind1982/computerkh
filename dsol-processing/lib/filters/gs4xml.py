#!/usr/local/bin/python2.6
# -*- mode: python -*-
#pylint: disable = no-member

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

import lxml.etree as ET
import warnings

import commonUtils

from StringIO import StringIO

# We have known deprecations in Cheetah.
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from Cheetah.Template import Template

from cstoreerrors import InvalidTransformationError
from filters.abstractfilter import AbstractFilter

class GS4Xml(AbstractFilter):
    # Get a parser object. Don't strip CDATA (preserve
    # tags in the full text element), and remove blank
    # text so that pretty printing works properly.
    parser = ET.XMLParser(strip_cdata=False,
                          remove_blank_text=True)

    def __init__(self, obj):
        self.object = obj.gs4
        self._template = Template(file=os.path.join(
            os.path.dirname(__file__),
            '../views/gs4xml/gs4template.tmpl'),
            searchList = [self.object])
        self._cfg = obj._cfg  #pylint:disable=W0212

    def print_record(self):
        while True:
            try:
                return self._printable_record # commonUtils.textUtils.fixamps(self._printable_record)
            except AttributeError:
                # xml = ET.parse(StringIO(self._template), self.parser)
                try:
                    xml = ET.parse(StringIO(self._template), self.parser)
                    #pylint:disable=W0201
                    self._printable_record = ET.tostring(xml, pretty_print=True,
                                                         xml_declaration=True,
                                                         encoding='UTF-8')
                except TypeError:
                    for f in sorted(self.object.fields()):
                        print '%s - %s' % (f, type(getattr(self.object, f)))
                    raise

                except ET.XMLSyntaxError as e:
                    print "filter error: %s" % e
                    raise InvalidTransformationError(
                        "Transformed record is invalid. Perhaps it contains an invalid character? (Most likely is a bare '&')",
                        record=self._template,
                        original_msg=e.msg,
                        lineno=e.lineno
                    )
