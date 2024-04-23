import re
import os
import optparse
import site
import copy
site.addsitedir('/packages/dsol/lib/python2.6/site-packages')
import xlwt
import subprocess
import lxml.etree as etree
import sys
sys.path.insert(0, "/packages/dsol/lib/python")
from lutbuilder import buildLut
entities = buildLut('/dc/eurobo/scanlists/Scanlist_essentials/lookup_marc_curlybracketed_enrefs.txt', '|')

def translit(text, f_r_dict):
    f_r_dict = dict((re.escape(k), v) for k, v in f_r_dict.iteritems())
    pattern = re.compile("|".join(f_r_dict.keys()))
    returned = pattern.sub(lambda m: f_r_dict[re.escape(m.group(0))], text)
    return returned

def lookUp(filename, delimiter, comment='#'):
    luTable = {}
    with open(filename, 'r') as lutfile:
        for line in lutfile:
            value_list = {}
            if line.startswith(comment):
                continue
            else:
                split_line = line.split(delimiter, 1)
                v_list = split_line[1].rstrip().split('~')
                value_list[v_list[0]] = v_list[1]
                luTable[split_line[0]] = value_list
    return luTable

class Record(object):
    def __init__(self, record):
        self.record = record
        self.uniform_title = self._uniform_title()
        self.alt_title = self._alt_title()
        self.related_title = self._related_title()
        self.other_authors = self._other_authors()
        self.fingerprints = self._fingerprints()
        self.languages = self._languages()
        self.bibrefs = self._bibrefs()
        self.generalnote = self._generalnote()
        self.fingerprints = self._fingerprints()
        self.relatedtitlenote = self._relatedtitlenote()
        self.subject = self._subject()

    @property
    def main_title(self):
        match = re.search('=245....\$(.*)\n', self.record)
        if match:
            main_title = match.group(1).strip()
            main_title = re.sub(r'\$.', ' ', main_title)
            return main_title[1:]

    def _uniform_title(self):
        uni_title = []
        match = re.findall('=(130|730|240|243)....\$(.*)\n', self.record)
        if match is not None:
            if len(match) == 0:
                uni_title = None
            else:
                if match:
                    if len(match) > 1:
                        for i in match:
                            item = i[1].split('$')
                            for a in item:
                                if a.startswith('a'):
                                    uni_title.append(a[1:].strip().encode('utf-8'))
                    else:
                        item = match[0][1].split('$')
                        for a in item:
                            if a.startswith('a'):
                                uni_title.append(a[1:].strip().encode('utf-8'))
        else:
            uni_title = None
        return uni_title

    def _alt_title(self):
        alt_title = []
        match = re.findall('=(524|740|749)....\$a(.*)\n', self.record)
        if match is not None:
            if len(match) == 0:
                alt_title = None
            else:
                if match:
                    if len(match) > 1:
                        for i in match:
                            alt_title.append(i[1].strip().encode('utf-8'))
                    else:
                        alt_title.append(match[0][1].strip().encode('utf-8'))
        else:
            alt_title = None
        return alt_title

    def _related_title(self):
        rel_title = []
        match = re.findall('=787....\$t(.*)\n', self.record)
        if match is not None:
            if len(match) > 1:
                for i in match:
                    rel_title.append(i.strip().encode('utf-8'))
            elif len(match) == 0:
                rel_title = None
            else:
                rel_title.append(match[0].strip().encode('utf-8'))
        else:
            rel_title = None
        return rel_title

    @property
    def pubdate(self):
        match = re.search('008  [0-9]*s([0-9][0-9X][0-9X][0-9X])', self.record)
        if match:
            pubdate = match.group(1).strip()
            return pubdate

    @property
    def localid(self):
        match = re.search('=001.*?\n', self.record)
        if match:
            localid = match.group(0)[9:].strip()
            return localid

    @property
    def imprint(self):
        match = re.search('=260....\$(.*)\n', self.record)
        if match:
            imprint = match.group(1).strip()
            imprint = re.sub(r'\$.', ' ', imprint)
            return imprint[1:]

    @property
    def printer_publisher(self):
        match = re.search('=260(.*)\n', self.record)
        if match:
            imprint = match.group(1).split('$')
            for i in imprint:
                if i.startswith('b'):
                    return i[1:].strip().encode('utf-8')

    @property
    def pub_place(self):
        match = re.search('=260(.*)\n', self.record)
        if match:
            imprint = match.group(1).split('$')
            for i in imprint:
                if i.startswith('a'):
                    if i.endswith(':'):
                        return i[1:-1].strip().encode('utf-8')

    @property
    def author(self):
        match = re.search('=1[01]0....\$(.*)', self.record)
        if match:
            author = match.group(1).strip()
            author = re.sub(r'\$.', ' ', author[1:])
            return author.encode('utf-8')

    def _other_authors(self):
        oth_author = []
        match = re.findall('=7[10]0....\$(.*)', self.record)
        if match is not None:
            if len(match) > 1:
                for i in match:
                    auth = i.strip().encode('utf-8')
                    auth = re.sub(r'\$.', ' ', auth[1:])
                    oth_author.append(auth)
            elif len(match) == 0:
                oth_author = None
            else:
                auth = match[0].strip().encode('utf-8')
                auth = re.sub(r'\$.', ' ', auth[1:])
                oth_author.append(auth)
        else:
            oth_author = None
        return oth_author

    def _translator_editor(self):
        transl_editor = []
        match = re.findall('=702.*\$a(.*)', self.record)
        if match is not None:
            if len(match) > 1:
                for i in match:
                    transl_editor.append(i.strip().encode('utf-8'))
            elif len(match) == 0:
                transl_editor = None
            else:
                transl_editor.append(match[0].strip().encode('utf-8'))
        else:
            transl_editor = None
        return transl_editor

    @property
    def size(self):
        match = re.search('=300.*;\$c(.*)', self.record)
        if match:
            size = match.group(1).encode('utf-8')
            return size.strip()

    @property
    def pagination(self):
        match = re.search('=300....\$a(.*?)[;\n]', self.record)
        if match:
            page = match.group(1).strip().encode('utf-8')
            page = re.sub(r'\$.', ' ', page)
            return page

    @property
    def shelfmark(self):
        match = re.search('=945(.*)', self.record)
        if match is not None:
            sm = match.group(1).split('$')
            for i in sm:
                if i.startswith('a'):
                    shm = i[1:].strip().encode('utf-8')
                    return shm

    @property
    def volume(self):
        match = re.search('=945(.*)', self.record)
        if match is not None:
            sm = match.group(1).split('$')
            for i in sm:
                if i.startswith('c'):
                    vol = i[1:]
                    vol = vol.replace(" ", "")
                    return vol

    @property
    def item(self):
        match = re.search('=945(.*)', self.record)
        if match is not None:
            sm = match.group(1).split('$')
            for i in sm:
                if i.startswith('y'):
                    i_num = i.split('i')[1]
                    i_num = 'i%s' % i_num
                    return i_num

    def _languages(self):
        language = []
        match = re.findall('=008.....................................(...)', self.record)
        match1 = re.findall('=101.*\$b(...)', self.record)
        match2 = re.findall('=101.*\$c(...)', self.record)
        if match is not None or match1 is not None or match2 is not None:
            if match:
                if len(match) > 1:
                    for i in match:
                        language.append(i)
                else:
                    language.append(match[0])
            if match1:
                if len(match1) > 1:
                    for i in match1:
                        language.append(i)
                else:
                    language.append(match1[0])
            if match2:
                if len(match2) > 1:
                    for i in match2:
                        language.append(i)
                else:
                    language.append(match2[0])
        else:
            language = None
        return language

    @property
    def countryofpublication(self):
        match = re.search('=008.................(..)', self.record)
        if match:
            countryofpublication = match.group(1).encode('utf-8')
            return countryofpublication

    def _bibrefs(self):
        bibrefs = []
        match = re.findall('=510....\$(.*)', self.record)
        if match is not None:
            if len(match) > 1:
                for i in match:
                    bib = i.strip().encode('utf-8')
                    bib = re.sub(r'\$.', ' ', bib)
                    bibrefs.append(bib[1:])
            elif len(match) == 0:
                bibrefs = None
            else:
                bib = match[0].strip().encode('utf-8')
                bib = re.sub(r'\$.', ' ', bib)
                bibrefs.append(bib[1:])
        else:
            bibrefs = None
        return bibrefs

    @property
    def editionnote(self):
        match = re.search('=250....\$a(.*)', self.record)
        if match:
            editionnote = match.group(1).strip().encode('utf-8')
            editionnote = re.sub(r'\$.', ' ', editionnote)
            return editionnote

    def _fingerprints(self):
        fingerprints = []
        match = re.findall('=012...\$a([^\$]*)\$', self.record)
        if match is not None:
            if len(match) > 1:
                for i in match:
                    fingerprints.append(i.strip().encode('utf-8'))
            elif len(match) == 0:
                fingerprints = None
            else:
                fingerprints.append(match[0].strip().encode('utf-8'))
        else:
            fingerprints = None
        return fingerprints

    def _generalnote(self):
        generalnote = []
        match = re.findall('=(500|501|546|327)....\$a(.*)', self.record)
        if match is not None:
            if len(match) == 0:
                generalnote = None
            else:
                if match:
                    if len(match) > 1:
                        for i in match:
                            generalnote.append(i[1].strip().encode('utf-8'))
                    else:
                        generalnote.append(match[0][1].strip().encode('utf-8'))
        else:
            generalnote = None
        return generalnote

    def _relatedtitlenote(self):
        relatedtitlenote = []
        match = re.findall('=311...\$a(.*?)\$', self.record)
        if match is not None:
            if len(match) > 1:
                for i in match:
                    relatedtitlenote.append(i.strip().encode('utf-8'))
            elif len(match) == 0:
                relatedtitlenote = None
            else:
                relatedtitlenote.append(match[0].strip().encode('utf-8'))
        else:
            relatedtitlenote = None
        return relatedtitlenote

    @property
    def copyspecificnote_single(self):
        match = re.search('=780....\$a(.*)', self.record)
        if match is not None:
            return match.group(1).strip().encode('utf-8')

    @property
    def copyspecificnote_double(self):
        match = re.search('=591  00z(Copy [0-9]*)eNote:(.*)', self.record)
        if match is not None:
            return (match.group(1).strip().encode('utf-8'), match.group(2).strip().encode('utf-8'))

    @property
    def boundwithnote(self):
        match = re.search('=423  .*?\$a(.*)', self.record)
        if match:
            boundwithnote = match.group(1).strip().encode('utf-8')
            return boundwithnote

    @property
    def contentsnotes(self):
        match = re.search('=520....\$a(.*)', self.record)
        if match:
            contentsnotes = match.group(1).strip().encode('utf-8')
            return contentsnotes

    @property
    def translator_editor(self):
        match = re.search('=702.*\$a(.*)', self.record)
        if match:
            translator_editor = match.group(1).strip().encode('utf-8')
            return translator_editor

    def _subject(self):
        subject = []
        match1 = re.findall('=(600|650|659|610|630|648)....\$(.*)', self.record)
        if match1 is not None:
            if len(match1) == 0:
                subject = None
            else:
                if match1:
                    if len(match1) > 1:
                        for i in match1:
                            sub = i[1].strip().encode('utf-8')
                            sub = re.sub(r'\$.', ' ', sub)
                            subject.append(sub[1:])
                    else:
                        sub = match1[0][1].strip().encode('utf-8')
                        sub = re.sub(r'\$.', ' ', sub)
                        subject.append(sub[1:])
        else:
            subject = None
        return subject

    @property
    def bnumber(self):
        match = re.search('=907.*?\n', self.record)
        if match:
            bnumber = match.group(0).strip().split('$')
            bnumber = bnumber[1][2:]
            return bnumber

class PQID(object):
    def __init__(self, idstring):
        self.idstring = idstring

    def incr_vol(self):
        return self.increment('vol')

    def incr_seq(self):
        return self.increment('seq')

    def increment(self, what):
        if what is 'vol':
            part_number = 3
            padding = '%08d'
        else:
            part_number = 4
            padding = '%03d'
        id_parts = self.idstring.split('-')
        id_parts[part_number] = padding % (int(id_parts[part_number]) + 1)
        return '-'.join(id_parts)

class PQIDOrganiser(object):
    _pqids = lookUp('/dc/eurobo/scanlists/Scanlist_essentials/lookup_pqid.txt', '|')
    _sm_pid = {}
    for k, v in _pqids.iteritems():
        for x, y in v.iteritems():
            _sm_pid[x] = y
    _max_id = 'hin-wel-all-%08d-001' % max([[int(d.split('-')[3]) for c,d in v.iteritems()] for k,v in _pqids.iteritems()])[0]
    #print _max_id
    __dict = { 'pqids': _pqids, 'sm_pid': _sm_pid, 'max_id': _max_id  }
    #print __dict

    def __init__(self, record):
        self.__dict__ = self.__class__.__dict
        self.record = record


    def __getitem__(self, item):
        while True:
            try:
                return self.pqids[item]
            except KeyError:
                if self.record.shelfmark:
                    sm = re.sub('/', '', self.record.shelfmark)
                else:
                    sm = 'None'
                if self.record.volume:
                    vol = re.sub(' ', '', self.record.volume)
                    sm = '%s%s' % (sm, vol)
                if sm in self.sm_pid:
                    new_pqid = PQID(self.sm_pid[sm]).incr_seq()
                    self.sm_pid[sm] = new_pqid
                else:
                    try:
                        n_pqid = PQID(self.sm_pid[sm]).incr_vol()
                    except KeyError:
                        self.max_id = new_pqid = PQID(self.max_id).incr_vol()
                    self.sm_pid[sm] = new_pqid
                self.pqids[item] = {sm: new_pqid}

    @classmethod
    def pqid_dup_check(cls):
        return cls._pqids

    @classmethod
    def save(cls):
        out = open('pqid.lup', 'w')
        for k, v in cls._pqids.iteritems():
            for x, y in v.iteritems():
                out.write('%s|%s~%s\n' % (k, x, y))
        out.close()

class InputReader(object):
    def __init__(self, input_file):
        self.input_file = input_file
        with open(self.input_file, 'r') as inf:
            self.contents = translit(inf.read(), entities)

    def __iter__(self):
        for raw_record in self.contents.split('\n=LDR'):
            yield raw_record

class SpreadsheetWriter(object):
    def __init__(self, ws_name=None, col_lables=None):
        self.workbook = xlwt.Workbook(encoding = 'ascii')
        if ws_name is None:
            ws_name = 'My_Worksheet'
        self.worksheet = self.workbook.add_sheet(ws_name)
        if col_lables is not None:
            for i, col_label in enumerate(col_lables):
                self.worksheet.write(0, i, label = col_label)

    def create_row(self, row_num, record):
        self.worksheet.write(row_num + 1, 0, label = PQIDOrganiser(r)[r.item][PQIDOrganiser(r)[r.item].keys()[0]])
        self.worksheet.write(row_num + 1, 1, label = record.shelfmark)
        self.worksheet.write(row_num + 1, 2, label = record.item)
        self.worksheet.write(row_num + 1, 3, label = record.main_title[:80])
        self.worksheet.write(row_num + 1, 4, label = '')
        if record.pagination:
            self.worksheet.write(row_num + 1, 5, label = record.pagination[:80])
        else:
            self.worksheet.write(row_num + 1, 5, label = '')
        self.worksheet.write(row_num + 1, 6, label = record.size)

    def save(self, wb_name):
        self.workbook.save(wb_name)

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
        mods_recordIdentifier.text = PQIDOrganiser(r)[r.item][PQIDOrganiser(r)[r.item].keys()[0]]
        mods_recordContentSourcer = etree.SubElement(mod_recordInfo, "{http://www.loc.gov/mods/v3}recordContentSource")
        mods_recordContentSourcer.text = '%s|%s|%s' % (record.item, record.localid, record.bnumber)
        mod_titleInfo = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}titleInfo")
        mods_title = etree.SubElement(mod_titleInfo, "{http://www.loc.gov/mods/v3}title")
        mods_title.text = record.main_title
        if record.alt_title:
            for at in record.alt_title:
                mods_alter = etree.SubElement(mod_titleInfo, "{http://www.loc.gov/mods/v3}title", type="alternative")
                mods_alter.text = at
        mod_name = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}name", type="personal")
        mods_namepart = etree.SubElement(mod_name, "{http://www.loc.gov/mods/v3}namePart")
        mods_namepart.text = record.author
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
            mod_note_type = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}note")
            mod_note_type.text = 'NOTE: %s' % record.editionnote
        if record.relatedtitlenote:
            for no in record.relatedtitlenote:
                mod_note_type = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}note")
                mod_note_type.text = 'NOTE: %s' % no
        if record.generalnote:
            for no in record.generalnote:
                mod_note_type = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}note")
                mod_note_type.text = 'NOTE: %s' % no
        if record.boundwithnote:
            for no in record.boundwithnote:
                mod_note_type = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}note")
                mod_note_type.text = 'NOTE: %s' % no
        if record.copyspecificnote_single:
            for no in record.copyspecificnote_single:
                mod_note_type = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}note")
                mod_note_type.text = 'NOTE: %s' % no
        if record.copyspecificnote_double:
            for no in record.copyspecificnote_double:
                mod_note_type = etree.SubElement(self.root_node, "{http://www.loc.gov/mods/v3}note")
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
        savename = 'mods/%s.xml' % PQIDOrganiser(r)[r.item][PQIDOrganiser(r)[r.item].keys()[0]]
        output = open(savename, 'w')
        out_xml = etree.tostring(self.root_node, xml_declaration=True, encoding='utf-8', pretty_print=True)
        out_xml = re.sub(r'&amp;#', '&#', out_xml)
        output.write(out_xml)
        output.close()

class XMLWriter(object):
    def __init__(self):
        self.output = open('wellcome.xml', 'w')

    def create_xml_record(self, record):
        xml_record = etree.Element("rec")
        xml_pqid = etree.SubElement(xml_record, "pqid")
        xml_pqid.text = PQIDOrganiser(r)[r.item][PQIDOrganiser(r)[r.item].keys()[0]]
        xml_shelfmark = etree.SubElement(xml_record, "shelfmark")
        xml_shelfmark.text = record.shelfmark
        xml_sysid = etree.SubElement(xml_record, "sysid")
        xml_sysid.text = '%s|%s|%s' % (record.item, record.localid, record.bnumber)
        xml_country_of_publication = etree.SubElement(xml_record, "country_of_publication")
        xml_country_of_publication.text = record.countryofpublication
        if record.languages:
            for i in record.languages:
                xml_language = etree.SubElement(xml_record, "language")
                xml_language.text = i
        xml_title = etree.SubElement(xml_record, "title")
        xml_title.text = record.main_title
        if record.uniform_title:
            for i in record.uniform_title:
                xml_uniform_title = etree.SubElement(xml_record, "uniform_title")
                xml_uniform_title.text = i
        if record.alt_title:
            for i in record.alt_title:
                xml_alt_title = etree.SubElement(xml_record, "alt_title")
                xml_alt_title.text = i
        if record.related_title:
            for i in record.related_title:
                xml_related_title = etree.SubElement(xml_record, "related_title")
                xml_related_title.text = i
        if record.author:
            xml_author_main = etree.SubElement(xml_record, "author_main")
            xml_author_main.text = record.author
        if record.other_authors:
            for i in record.other_authors:
                xml_author_other = etree.SubElement(xml_record, "author_other")
                xml_author_other.text = i
        if record.imprint:
            xml_imprint = etree.SubElement(xml_record, "imprint")
            xml_imprint.text = record.imprint
        xml_publisher_printer = etree.SubElement(xml_record, "publisher_printer")
        xml_publisher_printer.text = record.printer_publisher
        xml_place_of_publication = etree.SubElement(xml_record, "place_of_publication")
        xml_place_of_publication.text = record.pub_place
        xml_date = etree.SubElement(xml_record, "date")
        xml_date.text = record.pubdate
        if record.pagination:
            xml_pagination = etree.SubElement(xml_record, "pagination")
            xml_pagination.text = record.pagination
        xml_size = etree.SubElement(xml_record, "size")
        xml_size.text = record.size
        if record.bibrefs:
            for i in record.bibrefs:
                xml_bibliographic_reference = etree.SubElement(xml_record, "bibliographic_reference")
                xml_bibliographic_reference.text = i
        if record.generalnote:
            for i in record.generalnote:
                xml_note = etree.SubElement(xml_record, "note")
                xml_note.text = i
        if record.fingerprints:
            for i in record.fingerprints:
                xml_f_note = etree.SubElement(xml_record, "note")
                xml_f_note.text = 'FINGERPRINT: %s' % i
        if record.contentsnotes:
            for i in record.contentsnotes:
                xml_contentsnotes = etree.SubElement(xml_record, "note")
                xml_contentsnotes.text = 'CONTENTS NOTE: %s' % i
        if record.editionnote:
            xml_editionnote = etree.SubElement(xml_record, "edition_note")
            xml_editionnote.text = record.editionnote
        if record.relatedtitlenote:
            for i in record.relatedtitlenote:
                xml_relatedtitlenote = etree.SubElement(xml_record, "note")
                xml_relatedtitlenote.text = 'RELATED TITLE: %s' % i
        if record.copyspecificnote_single:
            if record.copyspecificnote_single is not None:
                xml_copyspecificnote_single = etree.SubElement(xml_record, "note")
                xml_copyspecificnote_single.text = 'Note on %s' % record.copyspecificnote_single
            if record.copyspecificnote_double is not None:
                xml_copyspecificnote_double = etree.SubElement(xml_record, "note")
                xml_copyspecificnote_double.text = 'Note on %s: %s' % (record.copyspecificnote_double[0], record.copyspecificnote_double[1])

        if record.boundwithnote:
            xml_boundwithnote = etree.SubElement(xml_record, "note")
            xml_boundwithnote.text = 'Includes: %s' % record.boundwithnote
        if record.subject:
            for i in record.subject:
                xml_subject = etree.SubElement(xml_record, "subject")
                xml_subject.text = i

        out_xml = etree.tostring(xml_record, pretty_print=True)
        out_xml = re.sub(r'&amp;#', '&#', out_xml)
        self.output.write(out_xml)
        #self.output.write(etree.tostring(xml_record, pretty_print=True))
        #print etree.tostring(self.xml_record, pretty_print=True)

    def save(self):
        self.output.close()


if __name__ == '__main__':

    parser = optparse.OptionParser()
    parser.add_option('-i', '--input', dest="input", help='Name of the input file. E.g. "-i data.txt"')
    (options, args) = parser.parse_args()
    if options.input is None:
        parser.print_help()
        exit(1)

    col_lables = ['PQID', 'Shelfmark', 'Copy ID', 'Title', 'Imprint', 'Pagination', 'Size']
    workbook = SpreadsheetWriter('Sheet 1', col_lables)
    xml = XMLWriter()
    print 'Working...'

    for i, marc in enumerate(InputReader(options.input)):
        r = Record(marc)
        if r.item in PQIDOrganiser.pqid_dup_check():
            print 'Possible duplicate item: %s, shelfmark: %s' % (r.item, r.shelfmark)
        elif PQIDOrganiser(r)[r.item].keys()[0] is 'None':
            print '%s failed: No shelf mark' % r.item # /VIT
        elif r.item is None:
            print 'No item number for shelfmark: %s, b-number: %s' % (r.shelfmark, r.bnumber)

            #elif PQIDOrganiser(r)[r.item].keys()[0][0] is not
        else:
            try:
                int(PQIDOrganiser(r)[r.item].keys()[0][0])
                mods_xml = ModsWriter()
                mods_xml.create_mod_record(r)
                xml.create_xml_record(r)
                workbook.create_row(i, r)
                mods_xml.save(r)
            except ValueError:
                print 'Invalid Shelfmark %s' % PQIDOrganiser(r)[r.item].keys()[0]

    PQIDOrganiser.save()
    xml.save()
    workbook.save('wellcome.xls')


#print PQIDOrganiser(r)[r.item]
#print PQIDOrganiser(r)[r.item].values()[0]
#print PQIDOrganiser(r)[r.item][PQIDOrganiser(r)[r.item].keys()[0]]
