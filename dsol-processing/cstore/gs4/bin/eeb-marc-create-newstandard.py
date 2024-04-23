#!/usr/local/bin/python2.7

import lxml.etree as et
import sys
import os
import io
import re
import codecs
import datetime
import difflib
from collections import OrderedDict

parser = et.XMLParser(remove_blank_text=True)


marc_dict = OrderedDict([
    ("LDR", ""),
    ("001", "  50000000"),
    ("003", "  Uk-CbPIL"),
    ("005", ""),
    ("006", ""),
    ("007", ""),
    ("008", ""),
    ("040", "  \\\\$aUk-CbPIL$cUk-CbPIL"),
    ("author", ""), 
    ("245", ""), 
    ("260", ""), 
    ("300", ""), 
    ("500", ""), 
    ("533", "  \\\\$aElectronic reproduction.$bCambridge, UK :$cProQuest,$d2014."), 
    ("752", ""), 
    ("830", "  \\0$aEarly European Books : Printed sources to 1700."), 
    ("856", "")
    ])

nonfiling_chars = []
with open("/dc/eurobo/utils/marc_utils/eeb-nonfiling-chars.txt") as infile:
    for line in infile.readlines():
        nonfiling_chars.append(line.strip('\r\n'))
nonfiling_chars.sort(lambda x,y: cmp(len(y), len(x)))

corp_auths = []
with codecs.open("/dc/eurobo/utils/marc_utils/eeb-corporate-auth-names.txt", "r", encoding='utf8') as infile:
    for line in infile.readlines():
        corp_auths.append(line.strip('\r\n'))
corp_auths.sort(lambda x,y: cmp(len(y), len(x)))

eeb_relators = []
with codecs.open("/dc/eurobo/utils/marc_utils/eeb-auth-relator-terms.txt", "r", encoding='utf8') as infile:
    for line in infile.readlines():
        eeb_relators.append(line.strip('\r\n'))
eeb_relators.sort(lambda x,y: cmp(len(y), len(x)))

eeb_titles = []
with codecs.open("/dc/eurobo/utils/marc_utils/eeb-auth-titles.txt", "r", encoding='utf8') as infile:
    for line in infile.readlines():
        eeb_titles.append(line.strip('\r\n'))
eeb_titles.sort(lambda x,y: cmp(len(y), len(x)))

eeb_numerals = []
with codecs.open("/dc/eurobo/utils/marc_utils/eeb-auth-numerators.txt", "r", encoding='utf8') as infile:
    for line in infile.readlines():
        eeb_numerals.append(line.strip('\r\n'))
eeb_numerals.sort(lambda x,y: cmp(len(y), len(x)))

marc_pays = {}
with open("/dc/eurobo/utils/marc_utils/eeb-marc-countries.lut") as infile:
    for line in infile.readlines():
        line = line.strip('\n')
        pays_key = line.split('|')[0]
        pays_value = line.split('|')[1]
        marc_pays[pays_key] = pays_value

marc_langs = {}
with open("/dc/eurobo/utils/marc_utils/eeb-marc-languages.lut") as infile:
    for line in infile.readlines():
        line = line.strip('\n')
        langs_key = line.split('|')[0]
        langs_value = line.split('|')[1]
        marc_langs[langs_key] = langs_value

eeb_countries_places = []
with codecs.open("/dc/eurobo/utils/marc_utils/eeb-countries-places.lut", "r") as infile:
    for line in infile.readlines():
        eeb_countries_places_dict = {}
        line = line.strip('\n')
        countries_key = line.split('|')[0]
        places_value = line.split('|')[1]
        eeb_countries_places_dict[countries_key] = places_value
        eeb_countries_places.append(eeb_countries_places_dict)

eeb_city_check = []
with codecs.open("/dc/eurobo/utils/marc_utils/eeb-places-countries-places.lut", "r") as infile:
    for line in infile.readlines():
        line = line.strip('\n')
        citykey = line.split('|')[0]
        eeb_places_countries_places = {}
        pays_ville_dict = {line.split('|')[1] : line.split('|')[2]}
        eeb_places_countries_places[citykey] = pays_ville_dict
        eeb_city_check.append(eeb_places_countries_places)

eeb_legid_goid = {}
with codecs.open("/dc/eurobo/utils/marc_utils/eeb-legid-goid.lut", "r") as infile:
    for line in infile.readlines():
        line = line.strip('\n')
        legid = line.split('|')[0].split('eeb-')[1]
        goid = line.split('|')[1]
        eeb_legid_goid[legid] = goid


def marc_leader_create():
    char_pos_00_04_leader = '  00000'
    char_pos_05_leader = 'n'
    char_pos_06_leader = 'a'
    char_pos_07_leader = 'm'
    char_pos_08_09_leader = '  '
    char_pos_10_leader = '2'
    char_pos_11_leader = '2'
    char_pos_12_16_leader = '00000'
    char_pos_17_leader = '1'
    char_pos_18_leader = 'a'
    char_pos_19_leader = ' '
    char_pos_20_leader = '4'
    char_pos_21_leader = '5'
    char_pos_22_leader = '0'
    char_pos_23_leader = '0'
    marc_dict['LDR'] = '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (char_pos_00_04_leader, char_pos_05_leader, char_pos_06_leader, 
    char_pos_07_leader, char_pos_08_09_leader, char_pos_10_leader, char_pos_11_leader, char_pos_12_16_leader, 
    char_pos_17_leader, char_pos_18_leader, char_pos_19_leader, char_pos_20_leader, char_pos_21_leader, char_pos_22_leader, 
    char_pos_23_leader)

def marc_005_create():
    marc_dict['005'] = '%s%s' % ('  ', datetime.datetime.today().strftime('%Y%m%d%H%M%S.0'))

def marc_006_create():
    char_pos_00_006 = '  m'
    char_pos_01_04_006 = '\\\\\\\\'
    char_pos_05_006 = 'g'
    char_pos_06_006 = '\\'
    char_pos_07_08_006 = '\\\\'
    char_pos_09_006 = 'd'
    char_pos_10_006 = '\\'
    char_pos_11_006 = '\\'
    char_pos_12_17_006 = '\\\\\\\\\\\\'
    marc_dict['006'] = '%s%s%s%s%s%s%s%s%s' % (char_pos_00_006, char_pos_01_04_006, char_pos_05_006,  char_pos_06_006, 
    char_pos_07_08_006, char_pos_09_006, char_pos_10_006, char_pos_11_006, char_pos_12_17_006)

def marc_007_create():
    char_pos_00_007 = '  c'
    char_pos_01_007 = 'r'
    char_pos_02_007 = '\\'
    char_pos_03_007 = 'c'
    char_pos_04_007 = 'n'
    char_pos_05_007 = '\\'
    char_pos_06_08_007 = '|||'
    char_pos_09_007 = 'a'
    char_pos_10_007 = '|'
    char_pos_11_007 = 'b'
    char_pos_12_007 = 'b'
    char_pos_13_007 = '|'
    marc_dict['007'] = '%s%s%s%s%s%s%s%s%s%s%s%s' % (char_pos_00_007, char_pos_01_007, char_pos_02_007, char_pos_03_007, char_pos_04_007, 
    char_pos_05_007, char_pos_06_08_007, char_pos_09_007, char_pos_10_007, char_pos_11_007, char_pos_12_007, char_pos_13_007)

def marc_008_create():
    char_pos_00_05_008 = datetime.datetime.today().strftime('%y%m%d')
    if len(eebxml.xpath('//startdate')) == 0:
        char_pos_07_10_008 = "uuuu"
        char_pos_11_14_008 = "uuuu"
        char_pos_06_008 = 'n'
    else:
        char_pos_07_10_008 = eebxml.xpath('//startdate')[0].text[0:4]
        if len(eebxml.xpath('//enddate')) == 0:
            char_pos_11_14_008 = "\\\\\\\\"
            char_pos_06_008 = 's'
        else:
            if eebxml.xpath('//enddate')[0].text[0:4] == char_pos_07_10_008:
                char_pos_11_14_008 = "\\\\\\\\"
                char_pos_06_008 = 's'
            else:
                char_pos_11_14_008 = eebxml.xpath('//enddate')[0].text[0:4]
                char_pos_06_008 = 'm'
    if len(eebxml.findall('//country_of_publication')) == 0:
        char_pos_15_17_008 = "xx\\"
    elif len(eebxml.findall('//country_of_publication')) > 1:
        error_file.write('%s/%s: marc_008 error - Too many <country_of_publication> elements. Only one country permitted in field 008.\n' % (dirname, filename))
        char_pos_15_17_008 = "xx\\"
    else:
        eeb_pays = eebxml.xpath('//rec/rec_search/country_of_publication')[0].text
        for key in marc_pays.keys():
            if key == eeb_pays and len(marc_pays[key]) == 3:
                char_pos_15_17_008 = '%s' % (marc_pays[key])
                break
            elif key == eeb_pays and len(marc_pays[key]) == 2:
                char_pos_15_17_008 = '%s\\' % (marc_pays[key])
                break
            else:
                char_pos_15_17_008 = ''
                continue
    char_pos_18_21_008 = '\\\\\\\\'
    char_pos_22_008 = 'g'
    char_pos_23_008 = '\\'
    char_pos_24_25_008 = '\\\\'
    char_pos_26_008 = '\\'
    char_pos_27_008 = '\\'
    char_pos_28_008 = '\\'
    char_pos_29_34_008 = '|||\|\\'
    if len(eebxml.findall('//language')) == 0:
        char_pos_35_37_008 = 'und'
    elif len(eebxml.findall('//language')) > 1:
        char_pos_35_37_008 = 'mul'
    else:
        eeb_lang = eebxml.xpath('//rec/rec_search/language')[0].text
        for key in marc_langs.keys():
            if key == eeb_lang:
                char_pos_35_37_008 = marc_langs[key]
                break
            else:
                char_pos_35_37_008 = ''
                continue
    char_pos_38_008 = '\\'
    char_pos_39_008 = 'd'
    if char_pos_35_37_008 == '':
        char_pos_35_37_008 = 'und'
        error_file.write('%s/%s: marc_008 error - Unrecognised language "%s" - using default language code "mul" in character positions 35-37.\n' % (dirname, filename, eeb_lang))
    elif char_pos_15_17_008 == '':
        char_pos_15_17_008 = "xx\\"
        error_file.write('%s/%s: marc_008 error - Unrecognised country "%s" - using default country code "xx\" in character positions 15-17.\n' % (dirname, filename, eeb_pays))
    marc_dict['008'] = '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % ('  ', char_pos_00_05_008, char_pos_06_008, char_pos_07_10_008, char_pos_11_14_008, char_pos_15_17_008, char_pos_18_21_008, 
    char_pos_22_008, char_pos_23_008, char_pos_24_25_008, char_pos_26_008, char_pos_27_008, char_pos_28_008, char_pos_29_34_008, char_pos_35_37_008, char_pos_38_008, char_pos_39_008)

def marc_author_create():
    if len(eebxml.xpath('//rec/rec_search/author_main/author_corrected')) == 0:
        error_file.write('%s/%s: The main author name is missing from the <author_corrected> element.\n' % (dirname, filename))
    elif eebxml.xpath('//rec/rec_search/author_main/author_corrected') == None:
        error_file.write('%s/%s: Element <author_corrected> is empty. Must contain text.\n' % (dirname, filename))
    else:
        auth_name = eebxml.xpath('//rec/rec_search/author_main/author_corrected')[0].text
        if auth_name in corp_auths:
            fieldname = '=110'
            name = auth_name
            marc_dict['author'] = '%s%s%s%s' % (fieldname, '  ', '2\$a', name)
        else:
            fieldname = '=100'
            authdict = {}
            authdict_a_string = ''
            try:
                for authchunk in auth_name.split(', '):
                    match = re.search(r'\d{2,4}', authchunk)
                    if match:
                        authdict['$d'] = match.string
                    elif authchunk in eeb_relators:
                        authdict['$e'] = authchunk
                    elif authchunk in eeb_titles:
                        authdict['$c'] = authchunk
                    else:
                        authdict_a_string = authdict_a_string + authchunk + ', '
                        authdict_a_string_new = ''
                        for i in authdict_a_string.split(' '):
                            if i.strip(', ') in eeb_numerals:
                                authdict['$b'] = i.strip(', ')
                            else:
                                authdict_a_string_new = authdict_a_string_new + i + ' '
                                authdict['$a'] = authdict_a_string_new.strip(', ')
                                if len(authdict['$a'].split(',')) == 1 or len(authdict['$a'].split(',')) == 0:
                                    char_pos_01_auth = 0
                                else:
                                    char_pos_01_auth = 1
                authdictstring = ''
                for k in sorted(authdict.keys()):
                    authdictstring = authdictstring + k + authdict[k]
                    try:
                        marc_dict['author'] = '%s%s%s%s%s' % (fieldname, '  ', char_pos_01_auth, '\\', authdictstring) 
                    except:
                        error_file.write('%s/%s(%s): The author name in <author_main> is not properly standardised.\n' % (dirname, filename, auth_name))
            except:
                error_file.write('%s/%s(%s): The author name in <author_main> is not properly standardised.\n' % (dirname, filename, auth_name))

def marc_author_other_create():
    if eebxml.xpath('//rec/rec_search/author_other/author_corrected') == None:
        error_file.write('%s/%s: Element <author_corrected> is empty. Must contain text.\n' % (dirname, filename))
    elif len(eebxml.xpath('//rec/rec_search/author_other/author_corrected')) == 1:
        auth_other = eebxml.xpath('//rec/rec_search/author_other/author_corrected')[0].text
        if auth_other == None:
            error_file.write('%s/%s: Element <author_corrected> is empty. Must contain text.\n' % (dirname, filename))
        if auth_other in corp_auths:
            fieldname = '=710'
            name = auth_other
            author_other = '%s%s%s%s' % (fieldname, '  ', '2\$a', name)
            outf.write('%s\n' % (author_other))
        else:
            fieldname = '=700'
            authdict = {}
            authdict_a_string = ''
            try:
                for authchunk in auth_other.split(', '):
                    match = re.search(r'\d{2,4}', authchunk)
                    if match:
                        authdict['$d'] = match.string
                    elif authchunk in eeb_relators:
                        authdict['$e'] = authchunk
                    elif authchunk in eeb_titles:
                        authdict['$c'] = authchunk
                    else:
                        authdict_a_string = authdict_a_string + authchunk + ', '
                        authdict_a_string_new = ''
                        for i in authdict_a_string.split(' '):
                            if i.strip(', ') in eeb_numerals:
                                authdict['$b'] = i.strip(', ')
                            else:
                                authdict_a_string_new = authdict_a_string_new + i + ' '
                                authdict['$a'] = authdict_a_string_new.strip(', ')
                                if len(authdict['$a'].split(',')) == 1:
                                    char_pos_01_auth = 0
                                else:
                                    char_pos_01_auth = 1
                authdictstring = ''
                for k in sorted(authdict.keys()):
                    authdictstring = authdictstring + k + authdict[k]
                    author_other = '%s%s%s%s%s' % (fieldname, '  ', char_pos_01_auth, '\\', authdictstring)
                try:
                    outf.write('%s\n' % (author_other))
                except:
                    error_file.write('%s/%s(%s): The author name in <author_other> is not properly standardised.\n' % (dirname, filename, auth_other))
            except:
                error_file.write('%s/%s(%s): The author name in <author_other> is not properly standardised.\n' % (dirname, filename, auth_other))
    else:
        for i in eebxml.xpath('//rec/rec_search/author_other/author_corrected'):
            auth_other = i.text
            if auth_other == None:
                error_file.write('%s/%s: Element <author_corrected> is empty. Must contain text.\n' % (dirname, filename))
                break
            elif auth_other in corp_auths:
                fieldname = '710'
                name = auth_other
                author_other = '%s%s%s%s' % (fieldname, '  ', '2\$a', name)
                outf.write('%s\n' % (author_other))
            else:
                fieldname = '=700'
                authdict = {}
                authdict_a_string = ''
                try:
                    for authchunk in auth_other.split(', '):
                        match = re.search(r'\d{2,4}', authchunk)
                        if match:
                            authdict['$d'] = match.string
                        elif authchunk in eeb_relators:
                            authdict['$e'] = authchunk
                        elif authchunk in eeb_titles:
                            authdict['$c'] = authchunk
                        else:
                            authdict_a_string = authdict_a_string + authchunk + ', '
                            authdict_a_string_new = ''
                            for i in authdict_a_string.split(' '):
                                if i.strip(', ') in eeb_numerals:
                                    authdict['$b'] = i.strip(', ')
                                else:
                                    authdict_a_string_new = authdict_a_string_new + i + ' '
                                    authdict['$a'] = authdict_a_string_new.strip(', ')
                                    if len(authdict['$a'].split(',')) == 1:
                                        char_pos_01_auth = 0
                                    else:
                                        char_pos_01_auth = 1
                    authdictstring = ''
                    for k in sorted(authdict.keys()):
                        authdictstring = authdictstring + k + authdict[k]
                        author_other = '%s%s%s%s%s' % (fieldname, '  ', char_pos_01_auth, '\\', authdictstring)
                    try:       
                        outf.write('%s\n' % (author_other))                
                    except:
                        error_file.write('%s/%s(%s): The author name in <author_other> is not properly standardised.\n' % (dirname, filename, auth_other))
                except:
                    error_file.write('%s/%s(%s): The author name in <author_other> is not properly standardised.\n' % (dirname, filename, auth_other))

def marc_245_create():
    eeb_title = eebxml.xpath('//rec/rec_search/title')[0].text
    for i in nonfiling_chars:
        if eeb_title.startswith("De ") and marc_dict['008'][37:40] == 'dan':
            char_pos_01 = 3
            break
        elif eeb_title.startswith("De ") and marc_dict['008'][37:40] == 'dut':
            char_pos_01 = 3
            break
        elif eeb_title.startswith(i):
            char_pos_01 = len(i)
            break
        else:
            char_pos_01 = 0
    marc_dict['245'] = '%s%s%s$a%s' % ('  ', '1', char_pos_01, eeb_title)

def marc_260_create():
    if len(eebxml.findall('//place_of_publication')) == 0:
        eeb_260_a = '[s.l.]'
    elif len(eebxml.findall('//place_of_publication')) == 1:
        eeb_260_a = eebxml.xpath('//place_of_publication')[0].text
    else:
        placelist = []
        for i in eebxml.findall('//place_of_publication'):
            placelist.append(i.text)
        eeb_260_a = ', '.join(placelist)
    try:
        eeb_260_b = eebxml.xpath('//rec/rec_search/publisher_printer')[0].text
    except IndexError:
        eeb_260_b = '[ s.n.]'
    try:
        eeb_260_c = '%s.' % (eebxml.xpath('//displaydate')[0].text)
        marc_dict['260'] = '%s%s$a%s:$b%s,$c%s' % ('  ', '\\\\', eeb_260_a, eeb_260_b, eeb_260_c)
    except:
        eeb_260_c = '[s.d.]'
        marc_dict['260'] = '%s%s$a%s:$b%s,$c%s' % ('  ', '\\\\', eeb_260_a, eeb_260_b, eeb_260_c)

def marc_300_create():
    try:
        eeb_300_a = eebxml.xpath('//rec/rec_search/pagination')[0].text
        if eebxml.xpath('//rec/rec_search/pagination')[0].text == None:
            eeb_300_a = 'v.'
    except:
        eeb_300_a = 'v.'
    try:
        eeb_300_b = eebxml.xpath('//rec/rec_search/size')[0].text
        if eebxml.xpath('//rec/rec_search/size')[0].text == None:
            eeb_300_b = 'ill.'    
    except:
        eeb_300_b = 'ill.'
    eeb_300 = []
    eeb_300.append(eeb_300_a)
    eeb_300.append(eeb_300_b)
    neweeb_300 = ', '.join(eeb_300)
    marc_dict['300'] = '%s%s$aOnline resource (%s).' % ('  ', '\\\\', neweeb_300)

def marc_500_create():
    try:
        eeb_500 = eebxml.xpath('//source_library')[0].text
        marc_dict['500'] = '%s%s$a%s%s.' % ('  ', '\\\\', 'Reproduction of original in ', eeb_500)
    except:
        eeb_500 = 'Reproduction of an original.'
        marc_dict['500'] = '%s' % (eeb_500)

def marc_752_create():
    if len(eebxml.xpath('//rec/rec_search/place_of_publication')) == 0:
        marc_752_placepub = '[s.l.]'
    else:
        marc_752_placepub = et.tostring(eebxml.xpath('//rec/rec_search/place_of_publication')[0]).replace('<place_of_publication>', '').replace('</place_of_publication>', '')

    if len(eebxml.xpath('//rec/rec_search/country_of_publication')) == 0:
        marc_752_countrypub = '[s.l.]'
    else:
        marc_752_countrypub = et.tostring(eebxml.xpath('//rec/rec_search/country_of_publication')[0]).replace('<country_of_publication>', '').replace('</country_of_publication>', '')

    for i in eeb_city_check:
        if marc_752_placepub == i.keys()[0]:
            marc_752_d = i.values()[0].values()[0]
            marc_752_a = i.values()[0].keys()[0]
            break
        else:
            continue
    try:      
        marc_dict['752'] = '%s%s$a%s$d%s' % ('  ', '\\\\', marc_752_a, marc_752_d)
    except:
        marc_dict['752'] = '  \\\\$a[s.l.]$d[s.l.]'
        error_file.write("%s/%s(%s, %s): marc_752 field error.  Using default values in 752 field.  Check combination of country and place of publication against standard list.\n" % (dirname, filename, marc_752_countrypub, marc_752_placepub))

def marc_856_create(eeb_legid_goid, docid):
    for eebid,goid in eeb_legid_goid.items():
        if eebid == docid:
            marc_dict['856'] = '%s$u%s%s' % ('  4\$zConnect to this resource online:', 
            'https://search.proquest.com/docview/', goid)
            break

recordstr = []
def marc_001_create():
    for val in numstr:
        if val in recordstr:
            continue
        else:
            marc_dict['001'] = '%s%s' % ('  ', str(val).zfill(10))
            recordstr.append(val)
            break
try:
    indir = sys.argv[1]
    outdir = sys.argv[2]
except:
    print "usage: LD_LIBRARY_PATH=/usr/local/lib eeb-marc-create.py [input directory] [output directory].  Please specify an input directory for the files you wish to convert to MARC records and an output directory for the output files."
    exit (1)

outf = codecs.open("%s/marc-recs.mrk" % (outdir), 'w', encoding='utf8')

error_file = codecs.open("%s/errors.txt" % (outdir), "w", encoding='utf8')

for dirname, dirpaths, filenames in os.walk(indir):
    filenum = len(filenames) + 1
    numstr = [num for num in range(1,filenum)]
    for filename in filenames:
        if filename.endswith('xml'):
            with codecs.open(os.path.join(dirname, filename), "r", encoding='utf8') as infile:
                print "creating MARC Record for %s..." % (filename)
                eebxml = et.parse(infile, parser)
                docid = eebxml.xpath('//pqid')[0].text
                auth_name = eebxml.xpath('//rec/rec_search/author_main/author_corrected')[0].text
                marc_leader_create()
                outf.write('=%s%s\n' % (marc_dict.keys()[0], marc_dict['LDR']))
                marc_001_create()
                outf.write('=%s%s\n' % (marc_dict.keys()[1], marc_dict['001']))
                outf.write('=%s%s\n' % (marc_dict.keys()[2], marc_dict['003']))
                marc_005_create()
                outf.write('=%s%s\n' % (marc_dict.keys()[3], marc_dict['005']))
                marc_006_create()
                outf.write('=%s%s\n' % (marc_dict.keys()[4], marc_dict['006']))
                marc_007_create()
                outf.write('=%s%s\n' % (marc_dict.keys()[5], marc_dict['007']))
                marc_008_create()
                outf.write('=%s%s\n' % (marc_dict.keys()[6], marc_dict['008']))
                outf.write('=%s%s\n' % (marc_dict.keys()[7], marc_dict['040']))
                marc_author_create()
                outf.write('%s\n' % (marc_dict['author']))
                marc_245_create()
                outf.write('=%s%s\n' % (marc_dict.keys()[9], marc_dict['245']))
                marc_260_create()
                outf.write('=%s%s\n' % (marc_dict.keys()[10], marc_dict['260']))
                marc_300_create()
                outf.write('=%s%s\n' % (marc_dict.keys()[11], marc_dict['300']))
                marc_500_create()
                outf.write('=%s%s\n' % (marc_dict.keys()[12], marc_dict['500']))
                outf.write('=%s%s\n' % (marc_dict.keys()[13], marc_dict['533']))
                marc_author_other_create()
                marc_752_create()
                outf.write('=%s%s\n' % (marc_dict.keys()[14], marc_dict['752']))
                outf.write('=%s%s\n' % (marc_dict.keys()[15], marc_dict['830']))
                marc_856_create(eeb_legid_goid, docid)
                outf.write('=%s%s\n\n' % (marc_dict.keys()[16], marc_dict['856']))
                print "MARC Record for %s created." % (filename)