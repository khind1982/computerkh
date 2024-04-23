#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib'))
sys.path.append('/packages/dsol/lib/python')

from dbtools import * #pylint:disable=W0401,W0614
from streams.abstractstream import * #pylint:disable=W0401

from cstoreerrors import PrismaSQLStreamUnknownVariantError

FIELDNAMES = '''aid article_title harticle_title abstract language hlanguage page hpage pagecount hpagecount ft ftsource pageimage haid author authors
hapiid pqid notes subjects descriptors hsp bkr iid publication other_authors displaypage copyright doctype updated newdata pq_publication
iid jid isu sdt udt ref vol allissues jtitle publisher issn country peer pqjid'''.split()

CONNECTION_STRING = {"user": "root", "db": "prisma_data", "host": "mysql-server"}

class PrismaSQLStream(AbstractStream):
    def __init__(self, cfg):
        AbstractStream.__init__(self, cfg)
        self.dbconn = DBBase(CONNECTION_STRING)
        self.dbconn.introspect()
        self.offset = 10000

        self.sqlFields = ['a.*', 'i.*', 'j.title as jtitle', 'j.publisher', 'j.issn', 'j.country', 'j.peer', 'j.pqjid']
        self.sqlTables = ['article_records a', 'issues i', 'journals j']
        self.sqlConditions = ['a.iid = i.iid AND i.jid = j.jid']

        self.start = 0

        self._data_types = ['pqonly', 'hapi', 'pqhapi', 'pqnohapi']

    def streamdata(self, dataTypes=None):  # pylint: disable = W0221
        if dataTypes is None:
            dataTypes = self._data_types
        elif isinstance(dataTypes, basestring) and dataTypes in self._data_types:
            dataTypes = [dataTypes]
        else:
            raise PrismaSQLStreamUnknownVariantError('%s is not a valid Prisma data variant identifier' % dataTypes)
    
        for dataType in dataTypes:
            self._cfg['prismaType'] = dataType
            self.start = 0
            eod = False
            while eod == False:
                try:
                    data = self.fetchData(dataType, self.start, self.offset)
                    for record in data.results:
                        self._count += 1
                        self._cfg['index'] = self._count
                        record.__dict__['_cfg'] = self._cfg
                        yield record
                    self.start += self.offset
                except NotFoundError:
                    eod = True

    def fetchData(self, data, start, offset):
        if data == 'hapi':
            sqlConditions = self.buildConditions('AND a.hapiid IS NOT NULL AND a.pqid IS NULL')
        elif data == 'pqonly':
            sqlConditions = self.buildConditions('AND a.hapiid IS NULL AND a.pqid IS NOT NULL')
        elif data == 'pqhapi' or data == 'pqnohapi':
            sqlConditions = self.buildConditions('AND a.hapiid IS NOT NULL AND a.pqid IS NOT NULL')
        return self.dbconn.find(self.sqlFields, self.sqlTables, sqlConditions,
                                limit = [str(start), str(offset)],
                                fieldnames = FIELDNAMES)

    def buildConditions(self, condition):
        return [self.sqlConditions[0] + ' ' + condition]
