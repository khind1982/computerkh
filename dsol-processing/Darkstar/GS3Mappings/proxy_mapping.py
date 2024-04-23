''' ProxyMapping

Receives a record object that wants to be mapped to the GSv3 format, finds out
what type of mapping it requires, and returns an appropriate mapping object.

Most mappings should be straightforward, and require no further code in this
module. However, if ever we do come across another special case, then we can
handle it here (like the PRISMA case, where we emit two different types of 
record, depending on the input).

'''

import re

from GS3Mappings.pq_prisma_mapping import PQPrismaMapping
from GS3Mappings.hapi_prisma_mapping import HAPIPrismaMapping
from GS3Mappings.prisma_mapping import PrismaMapping
from GS3Mappings.iimpa_mapping import IIMPAMapping

class ProxyMapping:
    def __init__(self, record):
        self.mappingType = re.search(r'(.*)Record', str(record.__class__).split('.')[-1]).group(1) + "Mapping"
        self.record = record
        
    def getMappingType(self):
        ''' If this is a PRISMA record, we need to work out if we are making a
        ProQuest Prisma record, a HAPI Prisma record, or both.'''
        #if self.mappingType == 'PrismaMapping':
            
        #    ''' We have a PRISMA record. Do we emit a single PQ/HAPI record, 
        #    or one of each? '''
        #    if self.record.article_title and self.record.harticle_title:
        #        return [PQPrismaMapping(self.record), HAPIPrismaMapping(self.record)]
                
        #    elif self.record.pqid:
        #        return PQPrismaMapping(self.record)
        #    elif self.record.hapiid:
        #        return HAPIPrismaMapping(self.record)

        #else:
        return eval(self.mappingType+'(self.record)')
