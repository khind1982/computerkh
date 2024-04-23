import os
import re

from commonUtils.fileUtils import buildLut
from mappings.leviathanmapping import LeviathanMapping


REELS = buildLut(os.path.join(
    os.path.dirname(__file__), '../../libdata/gerritsen_reels.lut')
)

class GerritsenMapping(LeviathanMapping):
    """Custom class for Gerritsen periodicals, which are
    leviathan format but have an extra requirements."""

    def __init__(self, rawrecord):
        super(GerritsenMapping, self).__init__(rawrecord)
        self.assign_accnum()
        self.assign_reels()

    def assign_accnum(self):
        self.gs4.accNum = [
            s for s in self.xml.xpath('.//sourceid/text()')
            if re.match(r'\d+', s)
        ][0]

    def assign_reels(self):
        note = {
            'NoteType': 'Publication',
            'NoteText': 'Reel/Fiche Number: %s' % REELS[self.xml.xpath(".//journalid/text()")[0]]
        }
        self.gs4.notesData = [note]

    def _objectIDs(self):
        super(GerritsenMapping, self)._objectIDs()
        self.gs4.objectIDs.append({'value': self.gs4.accNum,
                                   u'IDOrigin': u'CH',
                                   u'IDType': u'AccNum'})
