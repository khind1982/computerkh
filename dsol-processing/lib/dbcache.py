import bsddb.db as thedb
from bsddb.db import DB_BTREE, DB_CREATE
from bsddb.db import DBNoSuchFileError, DBPageNotFoundError

__all__ = ['DBCache', 'DBCacheManager']

class DBCache(object):
    __dbhandles = {}

    def __init__(self, dbfilename):
        self.dbfilename = dbfilename
        self.databases = self.__dbhandles
        self.dbhandle = self._getdbhandle()


    def _getdbhandle(self):
        while True:
            try:
                return self.databases[self.dbfilename]
            except KeyError:
                dbhandle = thedb.DB()
                # It's possible that this operation will raise an
                # exception. We can't catch it here, though, without
                # interfering with others parts of the app. If you
                # need to stop in the event there is no db file to
                # open, catch bsddb.db.DBNoSuchFileError in the scope
                # of the calling code.
                dbhandle.open(self.dbfilename, dbtype=DB_BTREE, flags=DB_CREATE)
                self.databases[self.dbfilename] = dbhandle

    # Remove all currently held database handles, effectively
    # starting from scratch again. DBCache.zero()
    @classmethod
    def zero(cls):
        cls.__dbhandles = {}

    def keys(self):
        return self.dbhandle.keys()

    def items(self):
        return self.dbhandle.items()

    def get(self, item):
        return self.dbhandle.get(item)

    def insert(self, item, value):
        self.dbhandle.put(item, value)
        self.dbhandle.sync()

    def __contains__(self, item):
        return item in self.keys()

    def __setitem__(self, item, value):
        self.insert(item, value)

    def __getitem__(self, item):
        return self.get(item)

    def __delitem__(self, item):
        self.dbhandle.delete(item)

    def close(self):
        self.dbhandle.close()

    # Remove the current database from the global table.
    def clear(self):
        self.close()
        del self.__dbhandles[self.dbfilename]


class DBCacheManager(object): # pylint: disable = R0903
    # A class to sit between the mapping class and the DBCache class.
    # Rationale: we need to write cache data on a per-journal basis to mitigate
    # the risk of corrupted databases. We also need, therefore, to explicitly
    # close a journal's cache files once that journal has been processed. This
    # is easy in the case of PIO/PAO where each source file corresponds to a
    # single journal. We can use this fact to detect when the app starts
    # processing a new journal, and trigger the explicit closing of the cache
    # files.

    __shared_state = {'context': None,
                      'cachetype': {},
                      }

    def __init__(self, context, cachetype, filename):
        self.state = self.__shared_state
        if self.state['context'] != context:
            self.state['context'] = context
            DBCache.zero()
        self.state['cachetype'] = {cachetype: DBCache(filename)}
        self.dbcachefile = self.state['cachetype'][cachetype]

    def __getitem__(self, item):
        return self.dbcachefile[item]

    def __setitem__(self, item, value):
        try:
            self.dbcachefile[item] = value
        except DBPageNotFoundError:
            print "Database file %s appears to be corrupt. Unable to write to it." % self.dbcachefile.dbfilename
            print "Try deleting it or recovering it from a recent snapshot."
            import sys
            sys.exit(1)
