#!/usr/local/bin/python2.6
# -*- mode: python -*-

'''
A set of classes to abstract database sessions.

Given a valid connection string, including database name, an instance
of DBBase autodiscovers the names of tables in the database, and the
names and details of columns in each table.

These can then be addressed using dot notation as dicts:

db = DBBase(connectionString)
db.tables['table_name'] => DBTable instance corresponding to table_name
db.tables['table_name'].columns => DBColumns instance
db.tables['table_name'].columns['column_name'] => DBColumn
db.tables['table_name'].columns['column_name'].value # Only AFTER a query!

db.find([list of fields], [list of tables],
        [conditions], [limit], [fieldnames]) => DBResultSet containing
  one DBResultRow for each retrieved record.

rs = db.find(...)
rs.

'''


import lxml.etree as ET

# We need these so we can wait for the database to come back in the event it
# goes away...
import random
import time

import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import MySQLdb  # pylint: disable = F0401

from commonUtils.textUtils import cleanAndEncode  # noqa


class DBToolsException(Exception):
    pass


class InvalidConnectionString(DBToolsException):
    pass


class NotFoundError(DBToolsException):
    pass


class DBBase(object):
    def __init__(self, connectionString):
        if connectionString is None:
            raise InvalidConnectionString
        else:
            self.connectionString = connectionString
        if hasattr(self, 'connection') and self.connection.__class__ is DBBase:
            pass
        else:
            self.getConnection()
#            self.connection = DBConnection(connectionString)
#            self.cursor = self.connection.cursor
        self.debuglogfile = open('/home/dbye/dbtools_debug_log.log', 'a+')

    def introspect(self):
        ''' Creating an instance of DBTables causes the db to be inspected.
        DBTables contains a DBTable for each table, each DBTable contains an
        instance of DBColumns, which in turn contain instances of DBColumn for
        each column. '''
        if not hasattr(self, 'tables'):
            self.tables = DBTables(self)

    def find(
            self, fields, tables,
            conditions=None, limit=None, fieldnames=None):
        # fieldnames is a list of names to set as attributes on the
        # returned results objects.  This needs to be rewritten to
        # happen automatically, but for now, we'll have to live with
        # it.  If the names of the fields should be the same as the
        # values in `fields', use that.
        if fieldnames is None:
            fieldnames = fields
        queryString = '''SELECT '''
        queryString += '%s ' % (', ').join(fields)
        queryString += 'FROM %s' % (', ').join(tables)
        if conditions is not None:
            queryString += " WHERE "
            queryString += ''' %s ''' % (', ').join(conditions)
        if limit is not None:
            queryString += " LIMIT %s" % (', ').join(limit)
        try:
            self.cursor.execute(queryString)
        except:  # noqa
            date = time.localtime()
            formattedDate = "%s %s-%s %s:%s:%s" % (
                date.tm_year, date.tm_mon, date.tm_mday,
                date.tm_hour, date.tm_min, date.tm_sec,)
            print >> self.debuglogfile, (
                "Exception triggered - limit = %s, %s" % (
                    str(limit), formattedDate,))
            self.getConnection(reset=True)
            self.cursor.execute(queryString)
        data = self.cursor.fetchall()
        if len(data) == 0:
            raise NotFoundError
        else:
            return DBResultSet(fieldnames, data)

    def closeConnection(self):
        self.connection.close()
        del(self.connection)

    def getConnection(self, reset=False):
        if reset is True:
            self.closeConnection()
            time.sleep(int(random.random()*10)+2)
        self.connection = DBConnection(self.connectionString)
        self.cursor = self.connection.cursor
        self.introspect()


class DBConnection(object):
    def __init__(self, connectionString):
        self.connectionString = connectionString
        self.conn = MySQLdb.connect(**connectionString)
        self.cursor = self.getCursor()

    def __str__(self):
        db = self.connectionString['db']
        user = self.connectionString['user']
        host = self.connectionString['host']
        return "Database: %s on %s\nLogged in as %s" % (db, host, user,)

    def close(self):
        self.conn.close()

    def getCursor(self):
        return self.conn.cursor()


class DBColumns(object):
    def __init__(self, tableName, dbconn):
        self.tablename = tableName
        # so we have a list of column names in the same order they're returned
        # from the db
        self.names = []
        self._columns = {}
        for column in self.introspectedColumns(dbconn):
            self.names.append(column[0])
            c = DBColumn(column)
            self._columns[c.name] = c

    def __str__(self):
        ret = ''
        for column in self._columns.values():
            ret += "Table name: %s\n\t%s\n\n" % (
                column.name, column.__str__(),)
        return ret

    def __getitem__(self, key):
        try:
            return self._columns[key]
        except (KeyError, AttributeError):
            return self._columns

    def __len__(self):
        return len(self._columns)

    def introspectedColumns(self, dbconn):
        dbconn.cursor.execute('''describe %s;''' % self.tablename)
        return dbconn.cursor.fetchall()


class DBColumn(object):
    def __init__(self, column):
        self.name = column[0]
        self.dataType = column[1]
        self.null = (column[2] if column[2] else 'unsp')
        self.key = (column[3] if column[3] else '<none>')
        self.default = column[4]
        self.extra = (column[5] if column[5] else '<none>')

    def __str__(self):
        ret = "Column Name: %s" % self.name
        ret += "\n\tType: %s" % self.dataType
        ret += "\n\tNull allowed: %s" % self.null
        ret += "\n\tIs key?: %s" % self.key
        ret += "\n\tDefault value: %s" % self.default
        return ret


class DBTables(object):
    def __init__(self, dbconn):
        dbconn.cursor.execute('''show tables;''')
        # so we have a list of tables in the same order they're returned by the
        # DB
        self.names = []
        self._tables = {}
        for table in dbconn.cursor.fetchall():
            tn = table[0]
            self.names.append(tn)
            t = DBTable(tn, dbconn)
            self._tables[t.name] = t

    def __getitem__(self, key):
        return self._tables[key]

    def __len__(self):
        return len(self._tables)


class DBTable(object):
    def __init__(self, tableName, dbconn):
        self.name = tableName
        self.columns = DBColumns(tableName, dbconn)

    def __getitem__(self, key):
        return self.columns[key]


class DBResultSet(object):
    def __init__(self, fieldnames, queryresults):
        self.fieldnames = fieldnames
        self.results = []
        for qr in queryresults:
            self.results.append(DBResultRow(fieldnames, qr))

    def __len__(self):
        return len(self.results)


class DBResultRow(object):
    ''' fieldnames should be a list containing the names of the attributes that
    should be defined on the DBResultRow object. This may or may not be the
    same as the column names from the database. In this manner, we can override
    a particular name here. They should be in the same order as the results to
    which they refer. '''
    def __init__(self, fieldnames, row):
        self._fieldnames = fieldnames
        self._data = {}
        for i, n in enumerate(fieldnames):
            self._data[n] = str(row[i])

    def __getattr__(self, attr):
        try:
            if self._data[attr] == 'None':
                self._data[attr] = ''
        except KeyError:
            print self._data
            raise AttributeError('instance has no attribute "%s"' % attr)
        return self._data[attr]

    def keys(self):
        return self._data.keys()

    @property
    def data(self):
        # Encapsulate the contents of _data in an lxml._ElementTree
        while True:
            try:
                return self._data_as_xml
            except AttributeError:
                self._data_as_xml = ET.Element('documentroot')
                for k, v in self._data.items():
                    if v:
                        elem = ET.SubElement(self._data_as_xml, k)
                        try:
                            elem.text = cleanAndEncode(v)
                        except ValueError:
                            print "Problematic encoding in %s: %s" % (
                                k, v)
                            raise

    # HACK! AbstractMapping needs to be fixed. This is a dependency leak, and I
    # don't like it.
    def _fields(self):
        return self._fieldnames
