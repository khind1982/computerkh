#!/usr/bin/env python2.7
# coding=utf-8

import os
import re
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import collections
import lxml.etree as ET

from datetime import datetime
from lxml.builder import E

from commonUtils.fileUtils import locate
from commonUtils.textUtils import fix_named_ents
from datetool.dateparser import parser as dateparser
from filmtransformfunc import levorder


roledcrew = {'Director': 'Director',
             'Directed by': 'Director',
             'Producer': 'Producer',
             'Produced by': 'Producer',
             'Production Company': 'ProductionCompany',
             '(Production Company)': 'ProductionCompany',
             '[Directed by]': 'Director'}

months = {'1': 'January',
          '2': 'February',
          '3': 'March',
          '4': 'April',
          '5': 'May',
          '6': 'June',
          '7': 'July',
          '8': 'August',
          '9': 'September',
          '10': 'October',
          '11': 'November',
          '12': 'December',
          '00': ''}

fiiids = [line.rstrip('\n') for line in open('/home/cmoore/svn/trunk/cstore/gs4/libdata/fii-ids.lut')]
errorslog = []
findlist = []

try:
    indir = sys.argv[1]
    outdir = sys.argv[2]
    delbatch = sys.argv[3]
except:
    print "Usage: %s {indirectory} {outdirectory}" % __file__


def testelem(root, elem):
    '''A function to test for an element's parent'''
    if root.find('.//%s' % elem) is None:
        retelem = ET.SubElement(root, elem)
    else:
        retelem = root.find('.//%s' % elem)
    return retelem


def cleanup(data):
    '''A function to clean up strings with unwanted whitespace'''
    strlst = []
    data = re.split(' |\n', data)
    for item in data:
        if item is not '':
            strlst.append(item)
    data = ' '.join(strlst)
    return data


class fiiTransform(object):

    def __init__(self):
        # created = 0
        document = E.document(
            E.record(
                E.film(
                    E.doctypes(
                        E.doctype1('Film')
                        )
                    )
                ),
            delbatch="%s" % delbatch)

        film = document.xpath('.//film')[0]

        film.append(self.docid())

        for title in self.titles():
            film.append(title)

        contributors = ET.SubElement(film, 'contributors')
        contribseq = 0
        for contrib in self.cast():
            contribseq += 1
            contrib.attrib['order'] = str(contribseq)
            contributors.append(contrib)
        for contrib in self.credits():
            contribseq += 1
            contrib.attrib['order'] = str(contribseq)
            contributors.append(contrib)

        if self.synopsis() is not None:
            film.append(self.synopsis())

        objseq = 0
        for object_citation in self.object_citations():
            objseq += 1
            object_citation[1].attrib['citorder'] = str(objseq)
            ob_cits = testelem(film, 'object_citations')
            ob_cits.append(object_citation[1])

        film.append(self.pubdates())
        film.append(self.production_details())

        film.append(self.language())

        for prod_ctry in self.production_country():
            film.append(prod_ctry)

        film.append(self.subjects())

        '''Assigning vendor field, source institution, projectcode'''
        ET.SubElement(film, 'vendor').text = 'BFI'
        ET.SubElement(film, 'sourceinstitution').text = 'BFI'
        ET.SubElement(film, 'projectcode').text = 'fiifilm'

        # print ET.tostring(document, pretty_print=True)

        if self.physdesc() is not None:
            film.append(self.physdesc())

        finaldoc = levorder(document, 'film')
        self.recout(finaldoc)

    def docid(self):
        # Check IDs for discrepancies
        docids = record.findall('.//utb/utb.content')
        sifts = [sift.text for sift in record.findall('utb/utb.fieldname')]
        if 'SIFT ID' not in sifts:
            elem = ET.Element('docid')
            elem.text = record.get('priref')
        else:
            for docid in docids:
                if docid.find('./../utb.fieldname').text == 'SIFT ID':
                    if docid.text.zfill(8) in fiiids:
                        elem = ET.Element('docid')
                        elem.text = docid.text.zfill(8)
                    elif docid.text in fiiids:
                        elem = ET.Element('docid')
                        elem.text = docid.text
                    else:
                        elem = ET.Element('docid')
                        elem.text = record.get('priref')
        if elem.text is None:
            print ET.tostring(record, pretty_print=True)
            exit()
        return elem

    def titles(self):
        # Work in progress - check alt title
        titles = record.findall('./Title/title')
        titlelist = []
        if len(record.findall('./Title/title.type[@value="05_MAIN"]')) == 0:
            elem = ET.Element('title')
            if titles[0].find('./../title.article') is not None and titles[0].find('./../title.article').text is not None:
                titles[0].text = '%s %s' % (titles[0].find('./../title.article').text, titles[0].text)
            elem.text = titles[0].text
            titlelist.append(elem)
            for title in titles[1:]:
                if title.find('./../title.article') is not None and title.find('./../title.article').text is not None:
                    title.text = '%s %s' % (title.find('./../title.article').text, title.text)
                altitle = ET.Element('alternate_title')
                altitle.text = title.text
                titlelist.append(altitle)
        else:
            for title in titles:
                if titles[0].find('./../title.article') is not None and titles[0].find('./../title.article').text is not None:
                    title.text = '%s %s' % (title.find('./../title.article').text, title.text)
                if title.find('../title.type[@value="05_MAIN"]') is not None:
                    titlelist.append(title)
                else:
                    altitle = ET.Element('alternate_title')
                    altitle.text = title.text
                    titlelist.append(altitle)
        return titlelist

    def cast(self):
        # DONE
        castlist = []
        for castmemb in record.findall('.//cast'):
            contributor = ET.Element('contributor', role="Cast")
            if castmemb.find('.//cast.name/name') is not None and castmemb.find('.//cast.name/name').text is not None:
                ET.SubElement(contributor, 'originalform').text = castmemb.find('.//cast.name/name').text
            if castmemb.find('.//cast.credit_credited_name') is not None and castmemb.find('.//cast.credit_credited_name').text is not None:
                ET.SubElement(contributor, 'altoriginalform').text = castmemb.find('.//cast.credit_credited_name').text
            if castmemb.find('.//cast.credit_on_screen') is not None and castmemb.find('.//cast.credit_on_screen').text is not None:
                contributor_notes = testelem(contributor, 'contributor_notes')
                ET.SubElement(contributor_notes, 'character_played').text = castmemb.find('.//cast.credit_on_screen').text
            castlist.append(contributor)
        return castlist

    def credits(self):
        # DONE
        credlist = []
        for credit in record.findall('.//credits'):
            contributor = ET.Element('contributor', role="Crew")
            if credit.find('.//credit.name/name') is not None and credit.find('.//credit.name/name').text is not None:
                ET.SubElement(contributor, 'originalform').text = credit.find('.//credit.name/name').text
            if credit.find('.//credit.credited_name') is not None and credit.find('.//credit.credited_name').text is not None:
                ET.SubElement(contributor, 'altoriginalform').text = credit.find('.//credit.credited_name').text
            if credit.find('.//credit.type/value') is not None and credit.find('.//credit.type/value').text is not None:
                if credit.find('.//credit.type/value').text in roledcrew.keys():
                    if roledcrew[credit.find('.//credit.type/value').text] == 'Director' or roledcrew[credit.find('.//credit.type/value').text] == 'Producer':
                        dupecontrib = ET.fromstring(ET.tostring(contributor))
                        if credit.find('.//credit.on_screen') is not None and credit.find('.//credit.on_screen').text is not None:
                            dupecontributor_notes = testelem(dupecontrib, 'contributor_notes')
                            ET.SubElement(dupecontributor_notes, 'production_role').text = credit.find('.//credit.on_screen').text
                        else:
                            dupecontributor_notes = testelem(dupecontrib, 'contributor_notes')
                            ET.SubElement(dupecontributor_notes, 'production_role').text = credit.find('.//credit.type/value').text
                        contributor.attrib['role'] = roledcrew[credit.find('.//credit.type/value').text]
                        credlist.append(contributor)
                        credlist.append(dupecontrib)
                    else:
                        contributor.attrib['role'] = roledcrew[credit.find('.//credit.type/value').text]
                        credlist.append(contributor)
                else:
                    if credit.find('.//credit.on_screen') is not None and credit.find('.//credit.on_screen').text is not None:
                        contributor_notes = testelem(contributor, 'contributor_notes')
                        ET.SubElement(contributor_notes, 'production_role').text = credit.find('.//credit.on_screen').text
                    else:
                        contributor_notes = testelem(contributor, 'contributor_notes')
                        ET.SubElement(contributor_notes, 'production_role').text = credit.find('.//credit.type/value').text
                    credlist.append(contributor)
        return credlist

    def synopsis(self):
        # DONE
        syndict = {}
        for synopsis in record.findall('./Description'):
            try:
                syndict[synopsis.find('./description.type/value').text] = cleanup(synopsis.find('.//description').text)
            except AttributeError:
                pass
            except TypeError:
                errorslog.append('Broken Synopsis field found in incoming data. Check:\n%s' % (ET.tostring(record, pretty_print=True)))
                pass
        if not syndict:
            elem = None

        if 'Synopsis' in syndict.keys():
            elem = ET.Element('synopsis')
            elem.text = syndict['Synopsis']
        elif 'Shotlist' in syndict.keys():
            elem = ET.Element('synopsis')
            elem.text = syndict['Shotlist']
        elif 'NFA Catalogue (obsolete - to be replaced)' in syndict.keys():
            elem = ET.Element('synopsis')
            elem.text = syndict['NFA Catalogue (obsolete - to be replaced)']
        elif 'Work History (obsolete - to be replaced)' in syndict.keys():
            elem = ET.Element('synopsis')
            elem.text = syndict['Work History (obsolete - to be replaced)']
        else:
            elem = None

        try:
            return elem
        except UnboundLocalError:
            print ET.tostring(synopsis, pretty_print=True)
            raise
            # return None

    def object_citations(self):
        # DONE
        fielddict = collections.OrderedDict([('documentation.title/title', 'citation_title'),
                                             ('description', 'citation_notes'),
                                             ('source.issue', 'citation_issue'),
                                             ('documentation.title/source.volume', 'citation_volume'),
                                             ('souce.title/issn', 'citsource_issn'),
                                             ('source.pagination', 'citsource_pagination'),
                                             ('source.title/title', 'citation_source'),
                                             ('language', 'citsource_lang')])

        object_citations = []
        objtest = []
        for article in record.findall('.//Documentation'):
            if 'Articles' in article.find('.//bibliographic_level/value[@lang="0"]').text:
                object_citation = ET.Element('object_citation')
                for author in article.findall('.//author.name/name/value'):
                    ET.SubElement(object_citation, 'citation_author').text = author.text
                for key in fielddict.keys():
                    if article.find('.//%s' % key) is not None and article.find('.//%s' % key).text is not None:
                        ET.SubElement(object_citation, '%s' % fielddict[key]).text = article.find('.//%s' % key).text
                if article.find('.//illustrations/value') is not None and article.find('.//illustrations/value').text == 'yes':
                    ET.SubElement(object_citation, 'citation_illus').text = 'illus'
                if article.find('.//source.month') is not None and article.find('.//source.month').text is not None:
                    artmon = article.find('.//source.month').text.zfill(2)
                    try:
                        month = months[article.find('.//source.month').text]
                    except KeyError:
                        month = article.find('.//source.month').text
                else:
                    month = ''
                    artmon = '01'
                if article.find('.//source.publication_years') is not None and article.find('.//source.publication_years').text is not None:
                    year = article.find('.//source.publication_years').text
                else:
                    year = ''
                ET.SubElement(object_citation, 'citsource_date').text = '%s %s' % (month, year)

                articledate = '%s%s01' % (year.zfill(4), artmon)
                arttupe = (articledate, object_citation)
                objtest.append(arttupe)

                object_citations.append(arttupe)

        object_citations.sort(reverse=True)
        return object_citations

    def language(self):
        langs = list(set(['%s' % lang.text for lang in record.findall('.//Parts/parts_reference/language/term/value') if lang.find('../../language.type/value') is not None and lang.find('../../language.type/value').text == 'DIALORIGDialogue (original)']))
        languages = ET.Element('languages')
        if not langs:
            langs.append('English')
            errorslog.append('No language detected. Check:\n%s' % (ET.tostring(record, pretty_print=True)))
        for lang in langs:
            ET.SubElement(languages, 'language').text = lang
        return languages

    def production_country(self):
        prod_ctry = [ET.fromstring('<country_of_production>%s</country_of_production>' % country.text) for country in record.findall('.//production_country/term')]
        return prod_ctry

    def subjects(self):
        subjects = ET.Element('subjects')
        subs = [ET.fromstring('<subject type="location">%s</subject>' % country.text) for country in record.findall('.//production_country/term')] + [ET.fromstring('<subject type="production">%s</subject>' % fix_named_ents(title.text)) for title in self.titles()]
        for sub in subs:
            subjects.append(sub)
        return subjects

    def _formatteddate(self, date):
        try:
            formatdate = datetime.strptime(date, '%Y-%m-%d').strftime('%d %b, %Y')
            parsed_date = dateparser.parse(formatdate).start_date
        except ValueError:
            try:
                formatdate = datetime.strptime(date, '%Y-%m').strftime('%b, %Y')
            except ValueError:
                formatdate = date
            try:
                parsed_date = dateparser.parse(formatdate).start_date
            except AttributeError:
                print ET.tostring(record, pretty_print=True)
                raise
        except UnboundLocalError:
            print ET.tostring(record, pretty_print=True)
            raise

        numdate = '%s-%s-%s' % (parsed_date.normalised_numeric_date[0:4], parsed_date.normalised_numeric_date[4:6], parsed_date.normalised_numeric_date[6:8])
        retdates = (formatdate, numdate)

        return retdates

    def pubdates(self):
        # DONE
        dates = collections.OrderedDict([('Release', None), ('Television', None), ('Copyright', None), ('Production', None)])
        pubs = ET.Element('pubdates')
        if len(record.findall('Title_date')) < 1:
            ET.SubElement(pubs, 'originaldate', undated="true").text = '0001'
            ET.SubElement(pubs, 'numdate', undated="true").text = '0001-01-01'
        for date in record.findall('Title_date'):
            formatdate = self._formatteddate(date.find('.//title_date_start').text)[0]
            parsed_date = self._formatteddate(date.find('.//title_date_start').text)[1]

            if date.find('.//title_date.type/value[@lang="0"]') is not None and date.find('.//title_date.type/value[@lang="0"]').text in dates:
                dates[date.find('.//title_date.type/value[@lang="0"]').text] = formatdate, parsed_date

        ET.SubElement(pubs, 'originaldate').text = next(date[0] for date in dates.values() if date is not None)
        ET.SubElement(pubs, 'numdate').text = next(date[1] for date in dates.values() if date is not None)

        if len(pubs) < 1:
            ET.SubElement(pubs, 'originaldate', undated="true").text = '0001'
            ET.SubElement(pubs, 'numdate', undated="true").text = '0001-01-01'
            errorslog.append('No release date or titledate.type found. Added as undated. Check:\n%s' % (ET.tostring(record, pretty_print=True)))

        return pubs

    def production_details(self):
        # DONE
        prods = ET.Element('productions')
        production_details = ET.SubElement(prods, 'production_details')
        '''Different Dates'''
        dates = {}
        fields = {'Copyright': 'production_crdate', 'Television': 'production_transdate', 'Production': 'production_dates'}
        for date in record.findall('Title_date'):
            if date.find('.//title_date.type/value[@lang="0"]') is not None and date.find('.//title_date.type/value[@lang="0"]').text is not None:
                dates[date.find('.//title_date.type/value[@lang="0"]').text] = self._formatteddate(date.find('.//title_date_start').text)[0]
        for datetype in dates.keys():
            try:
                ET.SubElement(production_details, fields[datetype]).text = dates[datetype]
            except KeyError:
                pass
        '''Runtime'''
        ET.SubElement(production_details, 'duration').text = record.find('.//runtime').text
        '''colcode, coloursys and soundsys'''
        try:
            allcolcode = record.findall('.//colour_manifestation/value[@lang="0"]')
            ET.SubElement(production_details, 'colcode').text = allcolcode[0].text
        except IndexError:
            errorslog.append('Missing colour information for record:%s\n' % record.get('priref'))
        try:
            allcolsys = record.findall('.//colour_code_manifestation')
            ET.SubElement(production_details, 'colsys').text = allcolsys[0].text
        except IndexError:
            errorslog.append('Missing colour systems information for record:%s\n' % record.get('priref'))
        try:
            allsoundsys = record.findall('.//sound_manifestation/value[@lang="0"]')
            ET.SubElement(production_details, 'soundsys').text = allsoundsys[0].text
        except IndexError:
            errorslog.append('Missing sound information for record:%s\n' % record.get('priref'))

        return prods

    def physdesc(self):
        dimvars = []
        for dimension in record.findall('.//Dimension'):
            if dimension.find('.//dimension.value') is not None and dimension.find('.//dimension.value').text is not None:
                dimvars.append('%s %s' % (dimension.find('.//dimension.value').text, dimension.find('.//dimension.unit').text))
        if len(dimvars) > 0:
            notes = ET.Element('notes')
            for note in list(set(dimvars)):
                ET.SubElement(notes, 'note', type="PhysDesc").text = note
        else:
            notes = None

        return notes

    def recout(self, document):
        try:
            path = '%s/%s' % (outdir, document.find('.//numdate').text[0:4])
        except AttributeError:
            print ET.tostring(document, pretty_print=True)
            raise
        if not os.path.exists(path):
            os.makedirs(path)
        outfname = '%s/FII_%s_%s.xml' % (path, document.find('.//numdate').text[0:4], document.find('.//docid').text)
        with open(outfname, 'w') as out:
            out.write(ET.tostring(document, pretty_print=True, xml_declaration=True))

recs = 0

for f in locate('*.xml', indir):
    tree = ET.iterparse(f, tag="record", huge_tree=True)

    for _, record in tree:
        recs += 1
        fiiTransform()

        sys.stdout.write('\033[92mNumber of records created:\033[0m %s\r' % recs)
        sys.stdout.flush()

    # Have to remove the record from the tree in order to keep processing the file.
        record.getparent().remove(record)
        # if recs == 10:
        #     exit()
    print '\n'

errorsout = '/dc/fii/data/validation/log%s%s%s.txt' % (datetime.now().year, datetime.now().month, datetime.now().day)

with open(errorsout, 'w') as out:
    for i in errorslog:
        out.write(i)
