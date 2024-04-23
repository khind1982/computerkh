#!/usr/local/bin/python2.5

''' Run through a Prisma data set, converting to the GSv3 format. '''

import os, sys, amara
from time import gmtime
#sys.path.append('/packages/dsol/lib/python')

for lib_path in ['/home/dbye/svn/dsol/trunk/Darkstar',
                 #'/home/dbye/lib',
                 '/home/dbye/lib/python']:
    sys.path.append(lib_path)
from GS3Mappings.proxy_mapping import ProxyMapping
from DSDataParser.prisma_parser import PrismaRecord
from DateConverter import *
import DSDataParser, EntityShield


if len(sys.argv) > 1:
    if re.match('^[0-9]+$', sys.argv[1]):
        count = int(sys.argv[1])
        infile = sys.argv[2]
    else:
        count = 0
        infile = sys.argv[1]
else:
    exit(1)
    
raw_field_names = ['article_title', 'harticle_title', 'abstract', 
                   'language', 'hlanguage', 'page', 'hpage', 
                   'pagecount', 'hpagecount', 'author', 'authors', 
                   'hapiid', 'pqid', 'notes', 'subjects', 'descriptors', 
                   'bkr', 'other_authors', 'copyright', 'sdt', 'udt',
                   'publication', 'pq_publication', 'isu', 'vol', 'peer',
                   'issn', 'jid', 'iid', 'ft', 'jtitle', 'ftsource',
                   'pageimage', 'hsp']

fields = ['.//*[@name="'+field+'"]' for field in raw_field_names]

print '<?xml version="1.0" encoding="UTF-8"?>\n<ROOT>'

# Because we don't get as many output records as we have input records,
# keep track of both separately:

exportDate = gmtime()[0:3]
y = str(exportDate[0])
m = str(exportDate[1]).zfill(2)
d = str(exportDate[2]).zfill(2)


basepath = '/dc/scratch/prisma/darkstar/pre'
darkStar = open(os.path.join(basepath, os.path.splitext(os.path.basename(infile))[0] + '_' + y + m + d + '.xml'), 'w')

darkStar.write('<?xml version="1.0" encoding="UTF-8"?>\n<ROOT>\n')

prismaLogFile = open(os.path.join('/home/dbye', os.path.basename(infile) + '.txt'), 'w')

done_so_far = [0, 0]
for rec in amara.binderytools.pushbind(infile, '/ROOT/row'):
    done_so_far[0] +=1
    
    if done_so_far[0] % 100 == 0:
        sys.stderr.write(str(done_so_far[0]))
        sys.stderr.write('(' + str(done_so_far[1]) + ')' )
    elif done_so_far[0] % 10 == 0:
        sys.stderr.write('.')

    record = ProxyMapping(PrismaRecord(rec, fields)).getMappingType()
    if record.record.hapiid == '':
        prismaLogFile.write(record.record.pqid + '\n')
        continue
    #else: continue # Short circuit the full transform - just want to capture
                   # the pqids of records with no hapiid.
    if type(record) is list:
        for r in record:
            print (r.do_mapping()).xml(indent='y', omitXmlDeclaration='y')
    else:
        ''' If the record has DocInternalGrouping set, it's a DarkStar record
        and needs to be written to a differnt file '''
        #mapped = record.do_mapping()
        #if mapped.xml_xpath('//DocInternalGrouping'):
        #    darkStar.write(mapped.xml(indent='y', omitXmlDeclaration='y'))
        #    darkStar.write('\n')
        #else:
        print (record.do_mapping()).xml(indent='y', omitXmlDeclaration='y')
    done_so_far[1] += 1
        
    if count is not 0:
        if done_so_far[1] >= count:
            break
sys.stderr.write('\n')
print '</ROOT>'

darkStar.write('</ROOT>\n')
darkStar.close()
prismaLogFile.close()
