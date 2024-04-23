#!/usr/local/bin/python2.5

import sys, amara
for lib_path in ['/home/dbye/svn/dsol/trunk/Darkstar', 
                 #'/home/dbye/lib', 
                 '/home/dbye/lib/python']:
    sys.path.append(lib_path)
from GS3Mappings.proxy_mapping import ProxyMapping
from DSDataParser.iimp_iipa_parser import IIMPARecord
from DateConverter import *
import DSDataParser
import EntityShield

if len(sys.argv) > 1:
    if re.match('^[0-9]+$', sys.argv[1]):
        count = int(sys.argv[1])
        infile = sys.argv[2]
    else:
        count = 0
        infile = sys.argv[1]
else:
    exit(1)
    
''' The exported data needs some cleaning before we can do anything useful with
it. Each element has redundant <value></value> pair around its content, which needs
to be stripped out, and the fulltext body is being ignored for the time being, so
is also discarded. '''

''' If there is a file with _cleaned before the .xml extension, use it instead of
cleaning the original. '''
if re.search(r'_cleaned.xml', infile):
    clean_data = infile
else:
    sys.stderr.write('Cleaning input data...\n')
    data = [line.rstrip() for line in open(infile)]
    clean_data = re.match(r'(.*)\..*', infile).group(1) + '_cleaned.xml'
    keep = []
    inside = 'NO'
    done_so_far = [0]
    for line in data:
        done_so_far[0] += 1
        ''' Strip out all the extraneous FiXML markup ''' 
        devalued = re.sub(r'</?value>', '', line)
        line = re.sub(r'(<!\[CDATA\[|\]\]>)', '', devalued)
        ''' This filthy hack is required to get round the existence of randomly placed
        '<' characters in the source data. I am preserving them as Unicode entrefs. '''
        bits = re.split(r'<', line)
        if len(bits) == 2:
            line = '<' + bits[1]
        elif len(bits) == 3:
            line = '<' + bits[1] + '<' + bits[-1]
        elif len(bits) >= 4:
            del(bits[0])
            bits[0] = '<' + bits[0]
            bits[-1] = '<' + bits[-1]
            line = ('&lt;').join(bits)
        if inside == 'NO':
            if re.search(r'name="body"', line):
                inside = 'YES'
            keep.append(line.rstrip())
        if inside == 'YES':
            if re.search(r'</element>', line):
                inside = 'NO'
        if done_so_far[0] % 1000 == 0:
            sys.stderr.write('.')

    del(data)

    sys.stderr.write('Done.\nFixing up XML...\n')
    outfile = open(clean_data, 'w')
    done_so_far = [0]
    for line in keep:
        done_so_far[0] += 1
        if re.search(r'"body">$', line):
            line += '</element>'
        outfile.write(line + '\n')
        if done_so_far[0] % 1000 == 0:
            sys.stderr.write('.')
        
    outfile.close()
    sys.stderr.write('Done.\nDoing mapping...\n')

    del(keep)

raw_field_names = '''author coauthor title journaltitle publishedstartdate
                     publishedenddate pubdisplaydate publisher pagedisplay
                     volissue volissuesort journalvolume journalissue
                     journalid abstract subject char cloc cnam corg csbj
                     csup workassubject issn documentlanguage language 
                     specialfeatures altjournalinfo altjournaltitles
                     documenttype royaltiesid articleid productid issntrim
                     autoftflag fulltextflag pdftxtflag issuenote Jstor
                     musecollection museurl naxosartist naxoschoir naxoscomposer
                     naxosconductor naxosensemble naxosorchestra onlineurl
                     paoarticleid peerreviewflag Pmurl pqarticleimageid 
                     pqpageimageid spub tngflag translatedtitle publishcountry'''.split()
                     
                     ## REMOVED body FROM LIST OF FIELDS - need to figure 
                     ## out how to parse it cleanly without blowing up.
                     
fields = ['.//element[@name="'+field+'"]' for field in raw_field_names]

print '<?xml version="1.0" encoding="UTF-8"?>\n<ROOT>'

done_so_far = [0]
for rec in amara.binderytools.pushbind(clean_data, u'/documents/document'):
    done_so_far[0] += 1
    record = ProxyMapping(IIMPARecord(rec, fields)).getMappingType()
    print (record.do_mapping()).xml(indent='y', omitXmlDeclaration='y')
    
    if done_so_far[0] % 100 == 0:
        sys.stderr.write(str(done_so_far[0]))
    elif done_so_far[0] % 10 == 0:
        sys.stderr.write('.')
    
    if count is not 0:
        if done_so_far[0] == count:
            break
sys.stderr.write('\n')

print '</ROOT>'
