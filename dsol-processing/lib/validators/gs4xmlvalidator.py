# -*- mode: python -*-

import os
import re

from StringIO import StringIO

from lxml import etree as ET

from cstoreerrors import SkipRecordException
from cstoreerrors import XmlValidationError

# A class to handle validation of GS4 records that are emitted by the
# GS4 format filter.

class GS4XmlValidator(object):
    # A class-level dict that is shared between instances. The first time we want
    # to validate against a schema, we cache it here to avoid having to parse it
    # afresh for each record.
    __dict = {
        'schema_cache': {}
        }

    def __init__(self, config):
        self.__dict__ = GS4XmlValidator.__dict
        self._cfg = config

    def validate(self, xml, schema_path):
        try:
            xmlschema = self.schema_cache[schema_path]  #pylint: disable=E1101
        except KeyError:
            xmlschema = self.schema_cache[schema_path] = ET.XMLSchema(ET.parse(schema_path)) #pylint: disable=E1101

        try:
            xmlschema.assertValid(ET.parse(StringIO(xml)))
        except ET.XMLSyntaxError as exc:
            # NASTY HACK! This is the only way we can handle things like
            # "Ca&amp;Lou;" which the app incorrectly changes to Ca&Lou;
            # I'm sorry, I really am.
            if re.match(r"Entity '.*' not defined, .*", exc.message):
                self._cfg['app_log'].error(
                    "%s: %s (NOTE line/column numbers refer to built data, not source!)" %
                    (self._cfg['filename'], exc.message))
                self._cfg['msq'].append_to_message("Undefined entity", self._cfg['basename'])
                self.writeLog(str(xmlschema.error_log.last_error), xml)
                raise SkipRecordException

            # print xml
            # lines = [l for l in xml]
            # print exc.position
            # print exc.offset
            # print exc.error_log
            # print exc.message
            # print exc.msg
            # print lines[exc.position[0]]
            raise
        except ET.DocumentInvalid:
            self.writeLog(str(xmlschema.error_log.last_error), xml)  #pylint: disable=E1103
            raise XmlValidationError

    def writeLog(self, msg, xml):
        if not os.path.isdir(self._cfg['validationSchemaLogging']):
            os.mkdir(self._cfg['validationSchemaLogging'])
        logfilepath = os.path.join(self._cfg['validationSchemaLogging'],
                                   '.'.join(
                                       [self._cfg['objectid'].replace('/', '-'), 'err']))
        with open(logfilepath, 'w') as logfile:
            logfile.write("%s\n----------------------------------------------\n%s" %
                          (msg, xml,))
