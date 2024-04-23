import re
import os
import optparse
import lxml.etree as etree
import site
site.addsitedir('/packages/dsol/lib/python2.6/site-packages')
import xlwt
import sys
sys.path.insert(0, "/packages/dsol/lib/python")
from lutbuilder import buildLut

idlookup = buildLut("add_ids.lut", delimiter="|")

countries = {'??': 'unknown', 'ar': 'Argentina', 'at': 'Austria', 'au': 'Austria', 'be': 'Belgium',
             'ch': 'Switzerland', 'cs': 'Czech Republic', 'cz': 'Czech Republic', 'da': 'Denmark',
             'db': 'Denmark', 'dd': 'Germany', 'de': 'Germany', 'dj': 'Denmark', 'dk': 'Denmark',
             'es': 'Spain', 'fi': 'Finland', 'fr': 'France', 'gb': 'United Kingdom', 'ic': 'Iceland',
             'id': 'Indonesia', 'is': 'Iceland', 'it': 'Italy', 'mx': 'Mexico', 'nl': 'Netherlands',
             'no': 'Norway', 'pl': 'Poland', 'pt': 'Portugal', 'se': 'Sweden', 'sw': 'Sweden', 'xx': 'unknown'}

class Record(object):
    def __init__(self, record):
        self.record = record
        self.alt_title = self._alt_title()
        self.boundwith = self._boundwith()
        self.languages = self._languages()
        self.pub_place = self._pub_place()
        self.pub_printer = self._pub_printer()
        self.imprint_pubdate = self._imprint_pubdate()
        self.general_note = self._general_note()
        self.subject = self._subject()
        self.contents_notes = self._contents_notes()

    @property   # not done sort the regex
    def localid(self):
        match = re.search('SYSID L[^0-9]*([0-9]*)\n', self.record)
        if match:
            localid = match.group(1).encode('utf-8')
            return localid

    @property   #not working
    def date(self):
        match = re.search('00800.L.(.*?)\n', self.record)
        if match:
            items = match.group(1).split('$$')
            for item in items:
                if item.startswith('a'):
                    return item[1:].encode('utf-8')

    @property
    def pub_country(self):
        match = re.search('00800.L.(.*?)\n', self.record)
        if match:
            items = match.group(1).split('$$')
            for item in items:
                if item.startswith('b'):
                    return item[1:].encode('utf-8')

    @property # multiple languages in this field?
    def language(self):
        match = re.search('00800.L.(.*?)\n', self.record)
        if match:
            items = match.group(1).split('$$')
            for item in items:
                if item.startswith('l'):
                    return item[1:].encode('utf-8')

    def _languages(self): # multiple languages in this field?
        match = re.search('04100.L.(.*?)\n', self.record)
        if match:
            language_list = []
            languages = match.group(1)
            langs = languages.split('$$')
            for lang in langs:
                language_list.append(lang[1:].encode('utf-8'))
            return language_list

    @property # this is rubbish
    def shelfmark(self):
        match = re.search('08800 L \$\$.(.*)', self.record)
        match1 = re.search('0960[05] L \$\$.(.*)\$\$u.*', self.record)
        match2 = re.search('0960[05] L \$\$.([^\$\n]*)[\$\n]', self.record)
        if match:
            return match.group(1).encode('utf-8')
        elif match1:
            return match1.group(1).encode('utf-8')
        elif match2:
            return match2.group(1).encode('utf-8')

    @property
    def author_main(self):
        match = re.search('10000.L.\$\$(.*)\n', self.record)
        if match:
            author = match.group(1).strip()
            author = re.sub(r'\$\$.', ' ', author[1:])
            return author.encode('utf-8')

    def _alt_title(self):
        alttitle = []
        match = re.findall('24100 L \$\$a(.*)[\$\$|\n]', self.record)
        match1 = re.findall('745[013]0 L \$\$a(.*)[\$\$|\n]', self.record)
        if match is not None or match1 is not None:
            if match:
                if len(match) > 1:
                    for i in match:
                        alttitle.append(i)
                else:
                    alttitle.append(match[0])
            if match1:
                if len(match1) > 1:
                    for i in match1:
                        alttitle.append(i)
                else:
                    alttitle.append(match1[0])
        else:
            alttitle = None
        return alttitle

    @property
    def main_title(self):
        match = re.search('24500 L \$\$.(.*)\n', self.record)
        if match:
            title = match.group(1).strip()
            title = re.sub(r'\$\$.', ' ', title[1:])
            return title.encode('utf-8')

    @property
    def edition_note(self):
        match = re.search('25000 L \$\$(.*)', self.record)
        if match:
            note = match.group(1).strip()
            note = re.sub(r'\$\$.', ' ', note[1:])
            return note.encode('utf-8')

    def _pub_place(self):
        match = re.search('26000.L.\$\$(.*?)\n', self.record)
        if match:
            place_list = []
            places = match.group(1)
            plce = places.split('$$')
            for item in plce:
                if item.startswith('a'):
                    place_list.append(item[1:].encode('utf-8'))
            return place_list

    def _pub_printer(self):
        match = re.search('26000.L.\$\$.(.*?)\n', self.record)
        if match:
            item_list = []
            item = match.group(1)
            items = item.split('$$')
            for i in items:
                if i.startswith(('b', 'k', 'r')):
                    item_list.append(i[1:].encode('utf-8'))
            return item_list

    def _imprint_pubdate(self):
        match = re.search('26000.L.\$\$.(.*?)\n', self.record)
        if match:
            item_list = []
            item = match.group(1)
            items = item.split('$$')
            for i in items:
                if i.startswith('c'):
                    item_list.append(i[1:].encode('utf-8'))
            return item_list

    @property
    def pagination(self):
        match = re.search('30000.L.\$\$(.*)', self.record)
        if match:
            items = match.group(1).split('$$')
            for item in items:
                if item.startswith('a'):
                    return item[1:].encode('utf-8')

    @property
    def size(self): ### $$b???
        match = re.search('30000.L.\$\$(.*)', self.record)
        if match:
            items = match.group(1).split('$$')
            for item in items:
                if item.startswith('c'):
                    return item[1:].encode('utf-8')

    def _contents_notes(self):
        subject = []
        match = re.findall('(50400|51200|53000)...\$\$(.*)', self.record)
        if match is not None:
            if len(match) == 0:
                subject = None
            else:
                if match:
                    if len(match) > 1:
                        for i in match:
                            sub = i[1].strip().encode('utf-8')
                            sub = re.sub(r'\$\$.', ' ', sub)
                            subject.append(sub[1:])
                    else:
                        sub = match[0][1].strip().encode('utf-8')
                        sub = re.sub(r'\$\$.', ' ', sub)
                        subject.append(sub[1:])
        else:
            subject = None
        return subject

    def _boundwith(self):
        boundwith = []
        bound_title = {}
        match = re.findall('53000.L.(.*?)\n', self.record)
        if match:
            for item in match:
                bounds = item.split('$$')
                bounds.pop(0)
                for item in bounds:
                   # print item
                    if item.startswith('i'):
                        bound_title['i'] = item[1:]
                    if item.startswith('t'):
                        bound_title['t'] = item[1:]
                    if item.startswith('e'):
                        bound_title['e'] = item[1:]
                    if item.startswith('b'):
                        bound_title['b'] = item[1:]
                boundwith.append(bound_title)
        return boundwith

    def _general_note(self):
        gen_note = []
        match = re.findall('55900...\$\$(.*)\n', self.record)
        if match:
            if len(match) > 1:
                for i in match:
                    item = re.sub(r'\$\$.', ' ', i[1:])
                    gen_note.append(item)
            else:
                item = re.sub(r'\$\$.', ' ', match[0][1:])
                gen_note.append(item)
        else:
            gen_note = None
        return gen_note

    def _subject(self):
        subject = []
        match = re.findall('(60000|63100)...\$\$(.*)', self.record)
        if match is not None:
            if len(match) == 0:
                subject = None
            else:
                if match:
                    if len(match) > 1:
                        for i in match:
                            sub = i[1].strip().encode('utf-8')
                            sub = re.sub(r'\$\$.', ' ', sub)
                            subject.append(sub[1:])
                    else:
                        sub = match[0][1].strip().encode('utf-8')
                        sub = re.sub(r'\$\$.', ' ', sub)
                        subject.append(sub[1:])
        else:
            subject = None
        return subject

    @property
    def author_other(self):
        other_list = []
        match = re.findall('70000.L.\$\$(.*)\n', self.record)
        if match is not None:
            if len(match) == 0:
                other_list = None
            else:
                if match:
                    for au in match:
                        author = au.strip()
                        author = re.sub(r'\$\$.', ' ', author[1:])
                        other_list.append(author.encode('utf-8'))
        else:
            other_list = None
        return other_list

    @property
    def bibliographic_reference(self):
        match = re.search('LN....L.(.*)$', self.record)
        if match:
            bibliographic_reference = match.group(1).encode('utf-8')
            return bibliographic_reference

    @property
    def uid(self):
        match = re.search('UID   L \$\$ax(.*?)kbd', self.record)
        if match:
            return match.group(1)


class ModsWriter(object):
    def __init__(self):
        xml_ns = "http://www.loc.gov/mods/v3"
        xsi = "http://www.w3.org/2001/XMLSchema-instance"
        schemaLocation = "http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-3-3.xsd"
        xml = "{%s}" % xml_ns
        NSMAP = {'mods' : xml_ns}
        self.root_node = etree.Element(xml + 'mods', attrib = {"{" + xsi + "}schemaLocation" : schemaLocation}, nsmap=NSMAP)

    def create_mod_record(self, record):
        mod_recordInfo = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}recordInfo")
        mods_recordIdentifier = etree.SubElement(mod_recordInfo, "{http://www.loc.gov/mods/v3}recordIdentifier")
        mods_recordIdentifier.text = '{{pqid}}'
        mods_recordContentSource = etree.SubElement(mod_recordInfo, "{http://www.loc.gov/mods/v3}recordContentSource")
        mods_recordContentSource.text = '%s|%s' % (record.sysid, record.uid)
        mod_titleInfo = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}titleInfo")
        mods_title = etree.SubElement(mod_titleInfo, "{http://www.loc.gov/mods/v3}title")
        mods_title.text = record.main_title
        if record.alt_title:
            for at in record.alt_title:
                mods_alter = etree.SubElement(mod_titleInfo, "{http://www.loc.gov/mods/v3}title", type="alternative")
                mods_alter.text = at
        if record.related_title:
            for at in record.related_title:
                mods_alter = etree.SubElement(mod_titleInfo, "{http://www.loc.gov/mods/v3}title", type="related")
                mods_alter.text = at
        if record.uniform_title:
            for at in record.uniform_title:
                mods_alter = etree.SubElement(mod_titleInfo, "{http://www.loc.gov/mods/v3}title", type="uniform")
                mods_alter.text = at
        mod_name = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}name", type="personal")
        mods_namepart = etree.SubElement(mod_name, "{http://www.loc.gov/mods/v3}namePart")
        mods_namepart.text = record.author_main
        mods_role = etree.SubElement(mod_name, "{http://www.loc.gov/mods/v3}role")
        mods_roleterm = etree.SubElement(mods_role, "{http://www.loc.gov/mods/v3}roleTerm", type="text")
        mods_roleterm.text = 'mainauthor'
        if record.other_authors:
            for oa in record.other_authors:
                mod_name = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}name", type="personal")
                mods_namepart = etree.SubElement(mod_name, "{http://www.loc.gov/mods/v3}namePart")
                mods_namepart.text = oa
                mods_role = etree.SubElement(mod_name, "{http://www.loc.gov/mods/v3}role")
                mods_roleterm = etree.SubElement(mods_role, "{http://www.loc.gov/mods/v3}roleTerm", type="text")
                mods_roleterm.text = 'otherauthor'
        mod_originInfo = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}originInfo")
        mod_place = etree.SubElement(mod_originInfo, "{http://www.loc.gov/mods/v3}place")
        mod_placeterm = etree.SubElement(mod_place, "{http://www.loc.gov/mods/v3}placeTerm", type="text")
        mod_placeterm.text = record.pub_place
        mod_place = etree.SubElement(mod_originInfo, "{http://www.loc.gov/mods/v3}place")
        mod_placeterm = etree.SubElement(mod_place, "{http://www.loc.gov/mods/v3}placeTerm", type="text")
        mod_placeterm.text = 'COUNTRY:%s' % record.countryofpublication
        mod_dateissued = etree.SubElement(mod_originInfo, "{http://www.loc.gov/mods/v3}dateIssued")
        mod_dateissued.text = record.pubdate
        mod_publisher = etree.SubElement(mod_originInfo, "{http://www.loc.gov/mods/v3}publisher")
        mod_publisher.text = record.printer_publisher
        mod_physicalDescription = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}physicalDescription")
        mod_form = etree.SubElement(mod_physicalDescription, "{http://www.loc.gov/mods/v3}form")
        mod_form.text = record.size
        if record.pagination:
            mod_extent = etree.SubElement(mod_physicalDescription, "{http://www.loc.gov/mods/v3}extent")
            mod_extent.text = record.pagination[:169]
        mod_note = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}note")
        mod_note.text = 'IMPRINT: %s' % record.imprint
        if record.editionnote:
            mod_note_type = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}note_type")
            mod_note_type.text = 'NOTE: %s' % record.editionnote
        if record.relatedtitlenote:
            for no in record.relatedtitlenote:
                mod_note_type = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}note_type")
                mod_note_type.text = 'NOTE: %s' % no
        if record.generalnote:
            for no in record.generalnote:
                mod_note_type = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}note_type")
                mod_note_type.text = 'NOTE: %s' % no
        if record.boundwithnote:
            for no in record.boundwithnote:
                mod_note_type = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}note_type")
                mod_note_type.text = 'NOTE: %s' % no
        if record.copyspecificnote_single:
            for no in record.copyspecificnote_single:
                mod_note_type = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}note_type")
                mod_note_type.text = 'NOTE: %s' % no
        if record.copyspecificnote_double:
            for no in record.copyspecificnote_double:
                mod_note_type = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}note_type")
                mod_note_type.text = 'NOTE: Note on %s: %s' % (no[0], no[1])
        location = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}location")
        mod_physicalLocation = etree.SubElement(location, "{http://www.loc.gov/mods/v3}physicalLocation")
        mod_physicalLocation.text = 'SHELFMARK: %s' % record.shelfmark
        mod_physicalLocation = etree.SubElement(location, "{http://www.loc.gov/mods/v3}physicalLocation")
        mod_physicalLocation.text = 'SOURCE: The Wellcome Collection'
        mod_physicalLocation = etree.SubElement(location, "{http://www.loc.gov/mods/v3}physicalLocation")
        mod_physicalLocation.text = 'LIBRARY: The Wellcome Library, London'
        language = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}language")
        for i in record.languages:
            mod_languageTerm = etree.SubElement(language, "{http://www.loc.gov/mods/v3}languageTerm",  type="text")
            mod_languageTerm.text = i

    def save(self, record):
        if not os.path.isdir('mods'):
            subprocess.call(["mkdir", "mods"])
        savename = 'mods/%s.xml' % pqid
        output = open(savename, 'w')
        out_xml = etree.tostring(self.root_node, xml_declaration=True, encoding='utf-8', pretty_print=True)
        out_xml = re.sub(r'&amp;#', '&#', out_xml)
        output.write(out_xml)
        output.close()



class WorksheetWriter(object):
    def __init__(self, ws_name=None):
        self.workbook = xlwt.Workbook(encoding = 'ascii')
        if ws_name is None:
            ws_name = 'My_Worksheet'
        self.worksheet = self.workbook.add_sheet(ws_name)

    def create_row(self, row_num, record):
        self.worksheet.write(row_num, 0, label = record.shelfmark)
        self.worksheet.write(row_num, 1, label = record.size)
        pqid = idlookup[record.localid]
        self.worksheet.write(row_num, 2, label = pqid)
        self.worksheet.write(row_num, 3, label = record.localid)
        self.worksheet.write(row_num, 4, label = record.main_title[:50])
        self.worksheet.write(row_num, 5, label = record.pub_place)

    def save(self, wb_name):
        self.workbook.save(wb_name)


class InputReader(object):
        def __init__(self, input_file):
            self.input_file = input_file
            with open(self.input_file, 'r') as inf:
                self.contents = inf.read()

        def __iter__(self):
            for raw_record in self.contents.split('record_split_key\n'):
                yield raw_record
                  

if __name__ == '__main__':

    parser = optparse.OptionParser()
    parser.add_option('-i', '--input', dest="input", help='Name of the input file. E.g. "-i data.txt"')
    (options, args) = parser.parse_args()
    if options.input is None:
        parser.print_help()
        exit(1)

    print options.input

    workbook = WorksheetWriter('test sheet')

    for i, marc in enumerate(InputReader(options.input)):
        r = Record(marc)
        workbook.create_row(i, r)
        print 'localid:         %s' % r.localid
        print 'date:            %s' % r.date
        print 'language:        %s' % r.pub_country
        print 'language:        %s' % r.language
        print 'languages:        %s' % r.languages
        print 'shelfmark:       %s' % r.shelfmark
        print 'author_main:       %s' % r.author_main
        print 'alt_title:       %s' % r.alt_title
        print 'maintitle:       %s' % r.main_title
        print 'edition_note:     %s' % r.edition_note
        print 'pub_place:     %s' % r.pub_place
        print 'pub_printer:     %s' % r.pub_printer
        print 'imprint_pubdate: %s' % r.imprint_pubdate
        print 'pagination:      %s' % r.pagination
        print 'size:            %s' % r.size
        print 'contents_notes:     %s' % r.contents_notes
        #print 'boundwith_title:     %s' % r.boundwith_title
        #print 'boundwith_titlesec:     %s' % r.boundwith_titlesec
        #print 'boundwith_imprint:     %s' % r.boundwith_imprint
        print 'general_note      %s' % r.general_note
        print 'subject      %s' % r.subject
        print 'author_other:       %s' % r.author_other
        print 'bibliographic_reference:       %s' % r.bibliographic_reference
        print 'uid:             %s' % r.uid
        print 'pqid'        %   idlookup[r.uid]
        #m = Mods(r, i)
        #print m.language
        if r.boundwith:
            print r.boundwith

    workbook.save('Excel_Workbook_test.xls')
    """
    print 'pub_place:       %s' % r.pub_place
    print 'localid:         %s' % r.localid
    print 'imprint_pubdate: %s' % r.imprint_pubdate
    print 'maintitle:       %s' % r.main_title
    print 'alt_title:       %s' % r.alt_title
    print 'pub_printer:     %s' % r.pub_printer
    print 'date:            %s' % r.date
    print 'language:        %s' % r.pub_country
    print 'size:            %s' % r.size
    print 'pagination:      %s' % r.pagination
    print 'shelfmark:       %s' % r.shelfmark
    print 'bib_num:         %s' % r.bib_num
    print 'uid:             %s' % r.uid
    print 'editionnote:     %s' % r.editionnote
    print 'generalnote      %s' % r.generalnote

    """
    print '\n'


































"""
??|unknown
ar|Argentina
at|Austria
au|Austria
be|Belgium
ch|Switzerland
cs|Czech Republic
cz|Czech Republic
da|Denmark
db|Denmark
dd|Germany
de|Germany
dj|Denmark
dk|Denmark
es|Spain
fi|Finland
fr|France
gb|United Kingdom
ic|Iceland
id|Indonesia
is|Iceland
it|Italy
mx|Mexico
nl|Netherlands
no|Norway
pl|Poland
pt|Portugal
se|Sweden
sw|Sweden
xx|unknown
"""



#['\nScanlist Subject group 15. Digitisation 17.th century KBDK.\n\nSYSID L 2174355\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax482003234$$fa\n00400 L $$rn$$ae\n00800 L $$a1607$$bdk$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-39\n09600 L $$aHielmst. 1407 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aJersin$$hJens Dinesen\n24500 L $$aBrevis Tractatus continens officia, discipulis ad doctrinamconsequendam, necessaria ...$$ea Jano Dionysio Jersino\n26000 L $$aHafni\xe6$$btypis Waldkirchianis$$c[1607]\n30000 L $$a[14] bl.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/supplab0091.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20040106\n63100 L $$aP\xe6dagogik\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax482003234kbd\n\nSYSID L 2084992\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax48156240x$$fa\n00400 L $$rn$$ae\n00800 L $$a1625$$bdk$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-39\n09600 L $$a15,-39 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aMatthias$$hDaniel\n24500 L $$aOratio de gymnastica et sciamachia earundemque usu ac fructuveroque fine$$econscripta & dedicata ... \xe2 Daniele Matthiade R\xf6eschildano\n26000 L $$aRostochii$$bexcudebat Augustinus Ferberus$$c1625\n30000 L $$a46 s.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010509.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20010123\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax48156240xkbd\n\nSYSID L 2084993\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481562418$$fa\n00400 L $$rn$$ae\n00800 L $$a1668$$bdk$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-39\n09600 L $$a15,-39 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aBenzon$$hPeder$$c1652\n24500 L $$a... De scholis judicium breve$$ead publicam disquisitionem ... \xe0Petro Benzonio Nicolai, respondente Petro Ramlosio ...\n26000 L $$aHafni\xe6$$bliteris Henrici G\xf6diani$$c1668\n30000 L $$a[8] bl.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010509.jpg\n56500 L $$aDefekt, sidste blad(e) mangler\n59900 L $$bEEBKBDK16002010$$cSCK20070312\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n70000 L $$aRaml\xf8se$$hPeder\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481562418kbd\n\nSYSID L 2191104\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax482119135$$fa\n00400 L $$rn$$ae\n00800 L $$a1671$$bde$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-39\n09600 L $$a15,-39 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aEinsperg$$hMichael\n24500 L $$aOratio de scholarum publicarum utilitate et discentium in iisdeminformatione maxime necessaria ...$$cadditis quibusdam de Academiarum perorbem mitiorem constitutione$$econscripta a Michaele Einspergio\n26000 L $$aGustrovii$$bliteris Scheippelianis$$c[1671]\n30000 L $$a[8] bl.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/supplcd0307.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20030228\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax482119135kbd\n\nSYSID L 2321873\nFMT   L BK\nLDR   L -----nam----------a-----\n00100 L $$ax481227864$$fa\n00400 L $$rn$$ae\n00800 L $$a1614$$bde$$lger$$tm\n00900 L $$aa\n08800 L $$o15,-71\n09600 L $$a15,-71 8\xb0$$uKan ikke hjeml\xe5nes\n24500 L $$aBericht von der Didactica, oder, Lehrkunst WolfgangiRatichii$$cdarinnen es Anleitung gibt, wie die Sprachen gar leicht undgeschwinde k\xf6nnen ohne sonderlichen Zwang und Verdruss des Jugendfortgepflantzet werden$$cauff begeren gestallet und beschrieben, durchetliche Professoren der Universit\xe4t Jehna ...$$cmit angehencktem kurtzenBericht etlicher Herrn Professorn der l\xf6blichen Universit\xe4t Giessen vonderselben Materia\n26000 L $$aJehna$$bgedruckt ... durch Heinrich Rauchmaul$$c1614\n30000 L $$a96, 59 s.\n55900 L $$aDet tilf\xf8jede v\xe6rk har selvst\xe6ndigt titelblad og paginering\n59900 L $$bEEBKBDK16002010$$cSCK20020521\n70000 L $$aRatke$$hWolfgang\n70000 L $$aHelwig$$hChristoph\n70000 L $$aJungius$$hJoachim\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481227864kbd\n\nSYSID L 4549102\nFMT   L BK\nLDR   L -----nam--22--------45--\n00100 L $$ax232720028$$fa\n00400 L $$rn$$ae\n00800 L $$tm$$a1615$$bde$$llat\n00900 L $$aa\n08800 L $$o15,-71\n09600 L $$a15,-71 8\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aRatke$$hWolfgang\n24500 L $$aDesiderata methodus nova Ratichiana lingvas compendiose &artificiose discendi$$cab autore ipso amicis communicata, nunc vero ingratiam studiosa juventutis juris publici facta$$e[Wolfgang Ratich]\n26000 L $$aHal\xe6 Saxonum$$bPetrus Faber typis exscribebat, impensis JoachimiKrusicken$$c1615\n30000 L $$a61 s.\n59900 L $$bEEBKBDK16002010$$cRETRO200501\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax232720028kbd\n\nSYSID L 5324680\nFMT   L BK\nLDR   L -----nam----------a-----\n00100 L $$ax483670358$$fa\n00400 L $$rn$$ae\n00800 L $$tm$$a1619$$bde$$llat$$v1\n00900 L $$aa\n08800 L $$o15,-71\n09600 L $$a15,-71 8\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aStrachindis$$hMarius de\n24500 L $$aRatichius non radicans seu explicatio et probatio quoddidactica, seu methodus docendi a Wolffgango Ratichio proposita nonsufficiens, sed imperfecta sit$$eauthore Mario de Strachindis ...\n26000 L $$aFrancofurti$$bprostat ... in officina Jonae Rosae$$c1619\n30000 L $$a31 s.\n59900 L $$bEEBKBDK16002010$$cRETRO200506\n60000 L $$aRatke$$hWolgang\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax483670358kbd\n\nSYSID L 4085453\nFMT   L BK\nLDR   L -----nam--a--------\n00100 L $$ax232176964$$fa\n00400 L $$rn$$ae\n00800 L $$tm$$a1619$$bde$$llat$$v1\n00900 L $$aa\n08800 L $$o15,-71\n09600 L $$a15,-71 8\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aMeier$$hGeorg\n24500 L $$aMarius de Strachindis nihil probans, seu oratione inauguralispro solenni introductione habita$$cMagd\xe6burgi, prid. Calend. Jun. anni CI?I?C XIX, in qu\xe1 Marii de Strachindis ICti. Ratichius non radicansexaminatur atque refutatur ...$$eautore Georgio Meiero ...\n26000 L $$aMagd\xe6b.$$btypis Andre\xe6 Bezelii, sumtibus AmbrosiiKirchnerii$$c[1619]\n30000 L $$a[36] bl.\n59900 L $$bEEBKBDK16002010$$cRETRO200408\n60000 L $$aStrachindis$$hMarius de\n60000 L $$aRatke$$hWolfgang\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax232176964kbd\n\nSYSID L 2085063\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481563112$$fa\n00400 L $$rn$$ae\n00800 L $$a1628$$bdk$$lger$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-72\n09600 L $$a15,-72 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aEngelbrecht$$hJacob\n24500 L $$aOrth? dias prom?n, das ist, Vortrab eines rechten Wegezeigersdamit... die Lehr-Jugendt zum rechten Wege nicht allein die beydenf\xfcrnembsten und n\xf6thigsten Hauptsprachen, als die grichische undlateinische ... zu studiren ..., besondern auch auff die rechte, uhraltephilosophische Bahne ... zu tretten beruffen wirdt ...$$evon JacoboEngelbrecht ...\n26000 L $$aKoppenhagen$$bgedruckt ... durch Georgium Hantzsch$$c1628\n30000 L $$a[28] bl.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010511.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20030318\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481563112kbd\n\nSYSID L 5001176\nFMT   L BK\nLDR   L -----nam--22--------45--\n00100 L $$ax233047912$$fa\n00400 L $$rn$$ae\n00800 L $$tm$$a1682$$bdk$$ldan\n00900 L $$aa\n08800 L $$o15,-72\n09600 L $$a15,-72 8\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aSiwers$$hBerent\n24500 L $$aTvende Skole-Methoder, den gamle oc dend Ny, kortligen oceenfoldigen forestillet Episcopis oc Rectoribus Scholarum til Guds \xe6ris ocdend studerende Ungdoms forfremmelse$$e[Bernhard Siwers]\n26000 L $$a[Hafni\xe6]$$c[1682]\n30000 L $$a[9] bl.\n59900 L $$bEEBKBDK16002010$$cRETRO200504\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax233047912kbd\n\nSYSID L 2960809\nFMT   L BK\nLDR   L -----nam----------a-----\n00100 L $$ax231321073$$fa\n00400 L $$rn$$ae\n00800 L $$tm$$a1653$$bdk$$llat$$v1\n00900 L $$aa\n08800 L $$o15,-88\n09600 L $$a15,-88 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aHolm$$hJacob Nielsen\n24500 L $$aJacobi Holmii Exercitatio oratoria de pr\xe6ceptorum institutionefrigida$$cqua justis censoribus ad examinandum proponitur, an salva &illibata conscientia suo fungantur officio rectores, qui e scholis, utvocant, trivialibus, oratores, poetas, gr\xe6cos et latinos excludunt &nobilia ac pr\xe6clara ingenia ab illis dum arcent, nonne perdant, su\xe6que fam\xe6turpem maculam aspergant? ...\n26000 L $$aSor\xe6$$btypis Petri Jansonii$$c[1653]\n30000 L $$a[8] bl.\n59900 L $$bEEBKBDK16002010$$cRETRO200311\n74500 L $$aExercitatio oratoria de pr\xe6ceptorum institutione frigida\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax231321073kbd\n\nSYSID L 2085105\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481563538$$fa\n00400 L $$rn$$ae\n00800 L $$a1603$$bdk$$llat$$tm$$v9$$dm\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$a15,-132 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aTheophilus$$hNicolaus\n24500 L $$aDe privilegiis studiosorum theses ...$$epr\xe6side Nic. Theophilo,respondente Johanne Sylvio ...\n26000 L $$aHafni\xe6$$btypis Henrici Waldkirchii$$c1603\n30000 L $$a[6] bl.\n50600 L $$aDisputats\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20010123\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n70000 L $$aSkov$$hHans\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481563538kbd\n\nSYSID L 2085106\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481563546$$fa\n00400 L $$rn$$ae\n00800 L $$a1622$$bdk$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$a15,-132 8\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aWorm$$hOle\n24500 L $$aOlai Wormii ... Baccalaureus philosophi\xe6, seu, De nomine causis,requisitis & privilegiis Baccalaureorum philosophi\xe6 discursus academicus...\n26000 L $$aHafni\xe6$$bliteris Sartorianis$$c[1622]\n30000 L $$a60 s.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n56500 L $$aDesuden 1 eks.: Hielmst. 2320 8\xb0\n59900 L $$bEEBKBDK16002010$$cSCK20051206\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n74500 L $$aBaccalaureus philosophi\xe6\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481563546kbd\n\nSYSID L 8032383\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax236530886$$fa\n00400 L $$rn$$ae\n00800 L $$a1622$$bdk$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$aHielmst. 2320 8\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aWorm$$hOle\n24500 L $$aOlai Wormii ... Baccalaureus philosophi\xe6, seu, De nomine causis,requisitis & privilegiis Baccalaureorum philosophi\xe6 discursus academicus...\n26000 L $$aHafni\xe6$$bliteris Sartorianis$$c[1622]\n30000 L $$a60 s.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20051206\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n74500 L $$aBaccalaureus philosophi\xe6\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax236530886kbd\n\nSYSID L 2085107\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481563554$$fa\n00400 L $$rn$$ae\n00800 L $$a1650$$bdk$$llat$$tm$$v9$$dm\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$a15,-132 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aBang$$hThomas\n24500 L $$aExercitatio acroamatica de curis boni auditoris$$equam ...pr\xe6side Thoma Bangio ...\n26000 L $$aHauni\xe6$$btypis Melchioris Martzan$$c1650\n30000 L $$a[20] bl.\n50600 L $$aDisputats\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20020123\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481563554kbd\n\nSYSID L 2191170\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax482119798$$fa\n00400 L $$rn$$ae\n00800 L $$a1659$$bde$$lger$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$a15,-132 8\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aSchupp$$hJohann Balthasar\n24500 L $$aJ B. Schuppii Erste und eylfertige Antwort auff M. BernhardSchmitts Discurs de Reputatione Academica\n26000 L $$aAltena$$bgedruckt bey Victor de Leeu$$c1659\n30000 L $$a70 s.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/supplcd0309.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20010330\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n74500 L $$aErste und eylfertige Antwort auff M. Bernhard Schmitts Discursde Reputatione Academica\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax482119798kbd\n\nSYSID L 2085108\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481563562$$fa\n00400 L $$rn$$ae\n00800 L $$a1666$$bde$$llat$$tm$$v9$$dm\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$a15,-132 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aSchwenck$$hJohannes\n24500 L $$aDisputatio juridica De jure Academiarum$$equam ... pr\xe6sideJohanne Schwenck ..., eruditorum examini publice submittit Dedl. Diedr.Dankwert\n26000 L $$aKilonii$$btypis Joachimi Reumanni$$c[1666]\n30000 L $$a[42] s.\n50600 L $$aDisputats\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20010123\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n70000 L $$aDankwert$$hDedl. Dietrich\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481563562kbd\n\nSYSID L 2085109\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481563570$$fa\n00400 L $$rn$$ae\n00800 L $$a1667$$bdk$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$a15,-132 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aResen$$hPeder Hansen$$c1625-1688\n24500 L $$a[De gradibus academicis]$$ePetrus Johannis Resenius\n26000 L $$a[Haffni\xe6]$$c[1667]\n30000 L $$a4 s.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n55900 L $$aUniversitetsprogram\n56500 L $$aUden titelblad\n59900 L $$bEEBKBDK16002010$$cSCK20010123\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481563570kbd\n\nSYSID L 2191171\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax482119801$$fa\n00400 L $$rn$$ae\n00800 L $$a1681$$bde$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$a15,-132 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aMajor$$hJohann Daniel\n24500 L $$aProgramma quo ... Johann Daniel Major disputationem ... Depetechiis a Joh. Philippo Foertschio ... habendam intimat, & ad hanc ...invitat\n26000 L $$a[Kili\xe6]$$bibidem imprimebat Joach. Reumannus$$c[1681]\n30000 L $$a15 s.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/supplcd0309.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20010330\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n70000 L $$aF\xf6rtsch$$hJohann Philipp\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax482119801kbd\n\nSYSID L 2085110\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481563589$$fa\n00400 L $$rn$$ae\n00800 L $$a1695$$bdk$$llat$$tm$$v9$$dm\n00900 L $$aa\n08800 L $$o15,-133\n09600 L $$a15,-133 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aGlud$$hS\xf8ren Pedersen$$c1662\n24500 L $$aDissertatio De gradu Magisterii philosophici ex variis membranis& antiquitatibus eruta ...$$epublice circumcidenda proponitur \xe0 SeverinoPetri Glud, respondente Johanne Alberto Syling ...\n26000 L $$aHafni\xe6$$bliteris ... Johannis Philippi Bockenhoffer$$c[1695]\n30000 L $$a[47] s.\n50600 L $$aDisputats\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n56500 L $$aDesuden 1 eks.: Hielmst. 1382 4\xb0\n59900 L $$bEEBKBDK16002010$$cSCK20030624\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n70000 L $$aSyling$$hHans Albert\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481563589kbd\n\nSYSID L 8032415\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax236531157$$fa\n00400 L $$rn$$ae\n00800 L $$a1695$$bdk$$llat$$tm$$v9$$dm\n00900 L $$aa\n08800 L $$o15,-133\n09600 L $$aHielmst. 1382 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aGlud$$hS\xf8ren Pedersen$$c1662\n24500 L $$aDissertatio De gradu Magisterii philosophici ex variis membranis& antiquitatibus eruta ...$$epublice circumcidenda proponitur \xe0 SeverinoPetri Glud, respondente Johanne Alberto Syling ...\n26000 L $$aHafni\xe6$$bliteris ... Johannis Philippi Bockenhoffer$$c[1695]\n30000 L $$a[47] s.\n50600 L $$aDisputats\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20030624\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n70000 L $$aSyling$$hHans Albert\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax236531157kbd\n\nSYSID L 2085218\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481564666$$fa\n00400 L $$rn$$ae\n00800 L $$a1661$$bde$$lger$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-210\n09600 L $$a15,-201 8\xb0$$uKan ikke hjeml\xe5nes\n24500 L $$a[ABC]\n26000 L $$aSchlesswig$$c1661\n30000 L $$a[4] bl.$$bill.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010517.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20010123\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n74500 L $$a[A.B.C.]\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481564666kbd\n\nSYSID L 2266906\nFMT   L BK\nLDR   L -----nam----------a-----\n00100 L $$ax482636598$$fa\n00400 L $$rn$$ae\n00800 L $$tm$$a1684$$bis$$lger$$v9\n00900 L $$aa\n08800 L $$o15,-201\n09600 L $$a15,-201 8\xb0$$uKan ikke hjeml\xe5nes\n24500 L $$a<<[En >>tydsk ABC]\n26000 L $$aHoolum$$c1684\n30000 L $$a7, [1] bl.\n59900 L $$bEEBKBDK16002010$$cSCK20010824\n74500 L $$a<<[En >>tydsk A.B.C.]\nB0100 L $$aKBD\nBAS   L kbd\n']
#['\nScanlist Subject group 15. Digitisation 17.th century KBDK.\n\nSYSID L 2174355\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax482003234$$fa\n00400 L $$rn$$ae\n00800 L $$a1607$$bdk$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-39\n09600 L $$aHielmst. 1407 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aJersin$$hJens Dinesen\n24500 L $$aBrevis Tractatus continens officia, discipulis ad doctrinamconsequendam, necessaria ...$$ea Jano Dionysio Jersino\n26000 L $$aHafni\xe6$$btypis Waldkirchianis$$c[1607]\n30000 L $$a[14] bl.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/supplab0091.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20040106\n63100 L $$aP\xe6dagogik\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax482003234kbd\n\nSYSID L 2084992\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax48156240x$$fa\n00400 L $$rn$$ae\n00800 L $$a1625$$bdk$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-39\n09600 L $$a15,-39 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aMatthias$$hDaniel\n24500 L $$aOratio de gymnastica et sciamachia earundemque usu ac fructuveroque fine$$econscripta & dedicata ... \xe2 Daniele Matthiade R\xf6eschildano\n26000 L $$aRostochii$$bexcudebat Augustinus Ferberus$$c1625\n30000 L $$a46 s.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010509.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20010123\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax48156240xkbd\n\nSYSID L 2084993\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481562418$$fa\n00400 L $$rn$$ae\n00800 L $$a1668$$bdk$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-39\n09600 L $$a15,-39 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aBenzon$$hPeder$$c1652\n24500 L $$a... De scholis judicium breve$$ead publicam disquisitionem ... \xe0Petro Benzonio Nicolai, respondente Petro Ramlosio ...\n26000 L $$aHafni\xe6$$bliteris Henrici G\xf6diani$$c1668\n30000 L $$a[8] bl.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010509.jpg\n56500 L $$aDefekt, sidste blad(e) mangler\n59900 L $$bEEBKBDK16002010$$cSCK20070312\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n70000 L $$aRaml\xf8se$$hPeder\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481562418kbd\n\nSYSID L 2191104\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax482119135$$fa\n00400 L $$rn$$ae\n00800 L $$a1671$$bde$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-39\n09600 L $$a15,-39 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aEinsperg$$hMichael\n24500 L $$aOratio de scholarum publicarum utilitate et discentium in iisdeminformatione maxime necessaria ...$$cadditis quibusdam de Academiarum perorbem mitiorem constitutione$$econscripta a Michaele Einspergio\n26000 L $$aGustrovii$$bliteris Scheippelianis$$c[1671]\n30000 L $$a[8] bl.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/supplcd0307.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20030228\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax482119135kbd\n\nSYSID L 2321873\nFMT   L BK\nLDR   L -----nam----------a-----\n00100 L $$ax481227864$$fa\n00400 L $$rn$$ae\n00800 L $$a1614$$bde$$lger$$tm\n00900 L $$aa\n08800 L $$o15,-71\n09600 L $$a15,-71 8\xb0$$uKan ikke hjeml\xe5nes\n24500 L $$aBericht von der Didactica, oder, Lehrkunst WolfgangiRatichii$$cdarinnen es Anleitung gibt, wie die Sprachen gar leicht undgeschwinde k\xf6nnen ohne sonderlichen Zwang und Verdruss des Jugendfortgepflantzet werden$$cauff begeren gestallet und beschrieben, durchetliche Professoren der Universit\xe4t Jehna ...$$cmit angehencktem kurtzenBericht etlicher Herrn Professorn der l\xf6blichen Universit\xe4t Giessen vonderselben Materia\n26000 L $$aJehna$$bgedruckt ... durch Heinrich Rauchmaul$$c1614\n30000 L $$a96, 59 s.\n55900 L $$aDet tilf\xf8jede v\xe6rk har selvst\xe6ndigt titelblad og paginering\n59900 L $$bEEBKBDK16002010$$cSCK20020521\n70000 L $$aRatke$$hWolfgang\n70000 L $$aHelwig$$hChristoph\n70000 L $$aJungius$$hJoachim\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481227864kbd\n\nSYSID L 4549102\nFMT   L BK\nLDR   L -----nam--22--------45--\n00100 L $$ax232720028$$fa\n00400 L $$rn$$ae\n00800 L $$tm$$a1615$$bde$$llat\n00900 L $$aa\n08800 L $$o15,-71\n09600 L $$a15,-71 8\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aRatke$$hWolfgang\n24500 L $$aDesiderata methodus nova Ratichiana lingvas compendiose &artificiose discendi$$cab autore ipso amicis communicata, nunc vero ingratiam studiosa juventutis juris publici facta$$e[Wolfgang Ratich]\n26000 L $$aHal\xe6 Saxonum$$bPetrus Faber typis exscribebat, impensis JoachimiKrusicken$$c1615\n30000 L $$a61 s.\n59900 L $$bEEBKBDK16002010$$cRETRO200501\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax232720028kbd\n\nSYSID L 5324680\nFMT   L BK\nLDR   L -----nam----------a-----\n00100 L $$ax483670358$$fa\n00400 L $$rn$$ae\n00800 L $$tm$$a1619$$bde$$llat$$v1\n00900 L $$aa\n08800 L $$o15,-71\n09600 L $$a15,-71 8\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aStrachindis$$hMarius de\n24500 L $$aRatichius non radicans seu explicatio et probatio quoddidactica, seu methodus docendi a Wolffgango Ratichio proposita nonsufficiens, sed imperfecta sit$$eauthore Mario de Strachindis ...\n26000 L $$aFrancofurti$$bprostat ... in officina Jonae Rosae$$c1619\n30000 L $$a31 s.\n59900 L $$bEEBKBDK16002010$$cRETRO200506\n60000 L $$aRatke$$hWolgang\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax483670358kbd\n\nSYSID L 4085453\nFMT   L BK\nLDR   L -----nam--a--------\n00100 L $$ax232176964$$fa\n00400 L $$rn$$ae\n00800 L $$tm$$a1619$$bde$$llat$$v1\n00900 L $$aa\n08800 L $$o15,-71\n09600 L $$a15,-71 8\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aMeier$$hGeorg\n24500 L $$aMarius de Strachindis nihil probans, seu oratione inauguralispro solenni introductione habita$$cMagd\xe6burgi, prid. Calend. Jun. anni CI?I?C XIX, in qu\xe1 Marii de Strachindis ICti. Ratichius non radicansexaminatur atque refutatur ...$$eautore Georgio Meiero ...\n26000 L $$aMagd\xe6b.$$btypis Andre\xe6 Bezelii, sumtibus AmbrosiiKirchnerii$$c[1619]\n30000 L $$a[36] bl.\n59900 L $$bEEBKBDK16002010$$cRETRO200408\n60000 L $$aStrachindis$$hMarius de\n60000 L $$aRatke$$hWolfgang\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax232176964kbd\n\nSYSID L 2085063\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481563112$$fa\n00400 L $$rn$$ae\n00800 L $$a1628$$bdk$$lger$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-72\n09600 L $$a15,-72 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aEngelbrecht$$hJacob\n24500 L $$aOrth? dias prom?n, das ist, Vortrab eines rechten Wegezeigersdamit... die Lehr-Jugendt zum rechten Wege nicht allein die beydenf\xfcrnembsten und n\xf6thigsten Hauptsprachen, als die grichische undlateinische ... zu studiren ..., besondern auch auff die rechte, uhraltephilosophische Bahne ... zu tretten beruffen wirdt ...$$evon JacoboEngelbrecht ...\n26000 L $$aKoppenhagen$$bgedruckt ... durch Georgium Hantzsch$$c1628\n30000 L $$a[28] bl.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010511.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20030318\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481563112kbd\n\nSYSID L 5001176\nFMT   L BK\nLDR   L -----nam--22--------45--\n00100 L $$ax233047912$$fa\n00400 L $$rn$$ae\n00800 L $$tm$$a1682$$bdk$$ldan\n00900 L $$aa\n08800 L $$o15,-72\n09600 L $$a15,-72 8\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aSiwers$$hBerent\n24500 L $$aTvende Skole-Methoder, den gamle oc dend Ny, kortligen oceenfoldigen forestillet Episcopis oc Rectoribus Scholarum til Guds \xe6ris ocdend studerende Ungdoms forfremmelse$$e[Bernhard Siwers]\n26000 L $$a[Hafni\xe6]$$c[1682]\n30000 L $$a[9] bl.\n59900 L $$bEEBKBDK16002010$$cRETRO200504\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax233047912kbd\n\nSYSID L 2960809\nFMT   L BK\nLDR   L -----nam----------a-----\n00100 L $$ax231321073$$fa\n00400 L $$rn$$ae\n00800 L $$tm$$a1653$$bdk$$llat$$v1\n00900 L $$aa\n08800 L $$o15,-88\n09600 L $$a15,-88 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aHolm$$hJacob Nielsen\n24500 L $$aJacobi Holmii Exercitatio oratoria de pr\xe6ceptorum institutionefrigida$$cqua justis censoribus ad examinandum proponitur, an salva &illibata conscientia suo fungantur officio rectores, qui e scholis, utvocant, trivialibus, oratores, poetas, gr\xe6cos et latinos excludunt &nobilia ac pr\xe6clara ingenia ab illis dum arcent, nonne perdant, su\xe6que fam\xe6turpem maculam aspergant? ...\n26000 L $$aSor\xe6$$btypis Petri Jansonii$$c[1653]\n30000 L $$a[8] bl.\n59900 L $$bEEBKBDK16002010$$cRETRO200311\n74500 L $$aExercitatio oratoria de pr\xe6ceptorum institutione frigida\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax231321073kbd\n\nSYSID L 2085105\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481563538$$fa\n00400 L $$rn$$ae\n00800 L $$a1603$$bdk$$llat$$tm$$v9$$dm\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$a15,-132 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aTheophilus$$hNicolaus\n24500 L $$aDe privilegiis studiosorum theses ...$$epr\xe6side Nic. Theophilo,respondente Johanne Sylvio ...\n26000 L $$aHafni\xe6$$btypis Henrici Waldkirchii$$c1603\n30000 L $$a[6] bl.\n50600 L $$aDisputats\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20010123\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n70000 L $$aSkov$$hHans\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481563538kbd\n\nSYSID L 2085106\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481563546$$fa\n00400 L $$rn$$ae\n00800 L $$a1622$$bdk$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$a15,-132 8\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aWorm$$hOle\n24500 L $$aOlai Wormii ... Baccalaureus philosophi\xe6, seu, De nomine causis,requisitis & privilegiis Baccalaureorum philosophi\xe6 discursus academicus...\n26000 L $$aHafni\xe6$$bliteris Sartorianis$$c[1622]\n30000 L $$a60 s.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n56500 L $$aDesuden 1 eks.: Hielmst. 2320 8\xb0\n59900 L $$bEEBKBDK16002010$$cSCK20051206\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n74500 L $$aBaccalaureus philosophi\xe6\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481563546kbd\n\nSYSID L 8032383\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax236530886$$fa\n00400 L $$rn$$ae\n00800 L $$a1622$$bdk$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$aHielmst. 2320 8\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aWorm$$hOle\n24500 L $$aOlai Wormii ... Baccalaureus philosophi\xe6, seu, De nomine causis,requisitis & privilegiis Baccalaureorum philosophi\xe6 discursus academicus...\n26000 L $$aHafni\xe6$$bliteris Sartorianis$$c[1622]\n30000 L $$a60 s.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20051206\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n74500 L $$aBaccalaureus philosophi\xe6\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax236530886kbd\n\nSYSID L 2085107\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481563554$$fa\n00400 L $$rn$$ae\n00800 L $$a1650$$bdk$$llat$$tm$$v9$$dm\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$a15,-132 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aBang$$hThomas\n24500 L $$aExercitatio acroamatica de curis boni auditoris$$equam ...pr\xe6side Thoma Bangio ...\n26000 L $$aHauni\xe6$$btypis Melchioris Martzan$$c1650\n30000 L $$a[20] bl.\n50600 L $$aDisputats\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20020123\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481563554kbd\n\nSYSID L 2191170\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax482119798$$fa\n00400 L $$rn$$ae\n00800 L $$a1659$$bde$$lger$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$a15,-132 8\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aSchupp$$hJohann Balthasar\n24500 L $$aJ B. Schuppii Erste und eylfertige Antwort auff M. BernhardSchmitts Discurs de Reputatione Academica\n26000 L $$aAltena$$bgedruckt bey Victor de Leeu$$c1659\n30000 L $$a70 s.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/supplcd0309.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20010330\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n74500 L $$aErste und eylfertige Antwort auff M. Bernhard Schmitts Discursde Reputatione Academica\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax482119798kbd\n\nSYSID L 2085108\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481563562$$fa\n00400 L $$rn$$ae\n00800 L $$a1666$$bde$$llat$$tm$$v9$$dm\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$a15,-132 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aSchwenck$$hJohannes\n24500 L $$aDisputatio juridica De jure Academiarum$$equam ... pr\xe6sideJohanne Schwenck ..., eruditorum examini publice submittit Dedl. Diedr.Dankwert\n26000 L $$aKilonii$$btypis Joachimi Reumanni$$c[1666]\n30000 L $$a[42] s.\n50600 L $$aDisputats\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20010123\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n70000 L $$aDankwert$$hDedl. Dietrich\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481563562kbd\n\nSYSID L 2085109\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481563570$$fa\n00400 L $$rn$$ae\n00800 L $$a1667$$bdk$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$a15,-132 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aResen$$hPeder Hansen$$c1625-1688\n24500 L $$a[De gradibus academicis]$$ePetrus Johannis Resenius\n26000 L $$a[Haffni\xe6]$$c[1667]\n30000 L $$a4 s.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n55900 L $$aUniversitetsprogram\n56500 L $$aUden titelblad\n59900 L $$bEEBKBDK16002010$$cSCK20010123\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481563570kbd\n\nSYSID L 2191171\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax482119801$$fa\n00400 L $$rn$$ae\n00800 L $$a1681$$bde$$llat$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-132\n09600 L $$a15,-132 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aMajor$$hJohann Daniel\n24500 L $$aProgramma quo ... Johann Daniel Major disputationem ... Depetechiis a Joh. Philippo Foertschio ... habendam intimat, & ad hanc ...invitat\n26000 L $$a[Kili\xe6]$$bibidem imprimebat Joach. Reumannus$$c[1681]\n30000 L $$a15 s.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/supplcd0309.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20010330\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n70000 L $$aF\xf6rtsch$$hJohann Philipp\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax482119801kbd\n\nSYSID L 2085110\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481563589$$fa\n00400 L $$rn$$ae\n00800 L $$a1695$$bdk$$llat$$tm$$v9$$dm\n00900 L $$aa\n08800 L $$o15,-133\n09600 L $$a15,-133 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aGlud$$hS\xf8ren Pedersen$$c1662\n24500 L $$aDissertatio De gradu Magisterii philosophici ex variis membranis& antiquitatibus eruta ...$$epublice circumcidenda proponitur \xe0 SeverinoPetri Glud, respondente Johanne Alberto Syling ...\n26000 L $$aHafni\xe6$$bliteris ... Johannis Philippi Bockenhoffer$$c[1695]\n30000 L $$a[47] s.\n50600 L $$aDisputats\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n56500 L $$aDesuden 1 eks.: Hielmst. 1382 4\xb0\n59900 L $$bEEBKBDK16002010$$cSCK20030624\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n70000 L $$aSyling$$hHans Albert\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481563589kbd\n\nSYSID L 8032415\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax236531157$$fa\n00400 L $$rn$$ae\n00800 L $$a1695$$bdk$$llat$$tm$$v9$$dm\n00900 L $$aa\n08800 L $$o15,-133\n09600 L $$aHielmst. 1382 4\xb0$$uKan ikke hjeml\xe5nes\n10000 L $$aGlud$$hS\xf8ren Pedersen$$c1662\n24500 L $$aDissertatio De gradu Magisterii philosophici ex variis membranis& antiquitatibus eruta ...$$epublice circumcidenda proponitur \xe0 SeverinoPetri Glud, respondente Johanne Alberto Syling ...\n26000 L $$aHafni\xe6$$bliteris ... Johannis Philippi Bockenhoffer$$c[1695]\n30000 L $$a[47] s.\n50600 L $$aDisputats\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010513.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20030624\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n70000 L $$aSyling$$hHans Albert\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax236531157kbd\n\nSYSID L 2085218\nFMT   L BK\nLDR   L -----nam--22------a-4500\n00100 L $$ax481564666$$fa\n00400 L $$rn$$ae\n00800 L $$a1661$$bde$$lger$$tm$$v9\n00900 L $$aa\n08800 L $$o15,-210\n09600 L $$a15,-201 8\xb0$$uKan ikke hjeml\xe5nes\n24500 L $$a[ABC]\n26000 L $$aSchlesswig$$c1661\n30000 L $$a[4] bl.$$bill.\n52900 L $$bBibliothecaDanica$$uhttp://images.kb.dk/bibliotheca_danica/bind%2010517.jpg\n59900 L $$bEEBKBDK16002010$$cSCK20010123\n63100 L $$aP\xe6dagogik$$aP\xe6dagogik\n74500 L $$a[A.B.C.]\nB0100 L $$aKBD\nBAS   L kbd\nUID   L $$ax481564666kbd\n\nSYSID L 2266906\nFMT   L BK\nLDR   L -----nam----------a-----\n00100 L $$ax482636598$$fa\n00400 L $$rn$$ae\n00800 L $$tm$$a1684$$bis$$lger$$v9\n00900 L $$aa\n08800 L $$o15,-201\n09600 L $$a15,-201 8\xb0$$uKan ikke hjeml\xe5nes\n24500 L $$a<<[En >>tydsk ABC]\n26000 L $$aHoolum$$c1684\n30000 L $$a7, [1] bl.\n59900 L $$bEEBKBDK16002010$$cSCK20010824\n74500 L $$a<<[En >>tydsk A.B.C.]\nB0100 L $$aKBD\nBAS   L kbd\n']
