# -*- mode: python -*-
# pylint: disable = F0401

# forceUpdate - update the current token for the record without
#               checking its value first
#
# checkForUpdate - check the current token against the stored one.
#                  If it's different, update the database and return
#                  "change". If it's the same, return "unchanged".
#                  If there isn't a token for the current doc ID,
#                  store this one and return "add"

import os

from dbcache import DBCacheManager

class SteadyStateHandler(object):
    '''
    A BSDDB-backed steady state tracking system.
    '''
    def __init__(self, product, ssroot):
        self.product = product
        self.ssroot = ssroot

    def tokenstash(self, jid):
        return DBCacheManager(
            context=jid,
            cachetype="steadystate",
            filename=os.path.join(self.ssroot, self.product, jid)
        )

    def checkForUpdate(self, record, token, jid):
        stored_token = self.tokenstash(jid)[record]
        if stored_token == None:
            self.tokenstash(jid)[record] = token
            return "add"
        elif stored_token == token:
            return "unchanged"
        else:
            self.tokenstash(jid)[record] = token
            return "change"

    def forceUpdate(self, record, token, jid):
        self.tokenstash(jid)[record] = token
