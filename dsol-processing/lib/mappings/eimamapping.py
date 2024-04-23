# -*- mode: python -*-

from cstoreerrors import SkipRecordException
from mappings.apsmapping import APSMapping

import logging
log = logging.getLogger('tr.mapping.eima')

class EIMAMapping(APSMapping):
    def __init__(self, rawrecord):
        super(self.__class__, self).__init__(rawrecord)

        # EIMA has a LegacyPlatform of HNP (Historical NewsPapers)
        self.gs4.legacy_platform = u'HNP'

        # Now that we've taught the APSMapping class about the APS_abstract
        # element, we need to tell EIMAMapping to ignore it.
        _dtable_eima = {
            'abstract': self.__class__.noop
            }

        self._merge_dtables(_dtable_eima)

    def _copyright_statement(self):
        try:
            self.gs4.copyrightData = self.copyright_statements[self.gs4.journalID]
        except KeyError:
            self.msq.append_to_message("No copyright statement for journal",
                                       self.gs4.journalID)
            log.error("No copyright statement for %s (%s)", self.gs4.legacyID,
                      self.gs4.journalID)
            raise SkipRecordException