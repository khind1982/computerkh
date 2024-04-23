#!/usr/bin/env python2.7
# coding=utf-8

import os
import sys
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import lxml.etree as ET

from collections import defaultdict
from lxml.builder import E

from commonUtils.fileUtils import locate, buildLut

try:
    indir = sys.argv[1]
    outdir = sys.argv[2]
    # delbatch = sys.argv[3]
except:
    print "Usage: %s {indirectory} {outdirectory}" % __file__

newpersonlog = []


def cleanup(data):
    '''A function to clean up strings with unwanted whitespace'''
    strlst = []
    data = re.split(' |\n', data)
    for item in data:
        if item is not '':
            strlst.append(item)
    data = ' '.join(strlst)
    return data


class fiiPersonProcessing(object):
    def __init__(self):
        hello = 'Hello'

    def prodrelease(self):
        release = [year for year in record.findall('./Title_date/title_date_start') if year.find('../title_date.type/value[@lang="neutral"]').text == '03_R']
        return release

    def existing_productiondetails(self, person):
        production_details = ET.Element('production_details')
        title = ET.SubElement(production_details, 'production_title')
        try:
            title.text = [main for main in record.findall('./Title/title') if main.find('../title.type/value[@lang="neutral"]').text == '05_MAIN'][0].text
        except AttributeError:
            try:
                title.text = [main for main in record.findall('./Title/title')][0].text
            except IndexError:
                print 'No film title found'
        release = ET.SubElement(production_details, 'release_year')
        try:
            release.text = [year for year in record.findall('./Title_date/title_date_start') if year.find('../title_date.type/value[@lang="neutral"]').text == '03_R'][0].text
        except IndexError:
            release.text = [year for year in record.findall('./Title_date/title_date_start')][0].text
        castrole = ET.SubElement(production_details, 'person_castrole')
        castrole.text = person.find('.//cast.credit_on_screen').text
        # print ET.tostring(production_details, pretty_print=True)
        return production_details

    def existing_persondetails(self, person):
        persondets = []
        biography = ET.Element('note', type="Biography")
        if person.find('.//name.note') is not None and person.find('.//name.note').text is not None:
            biography.text = cleanup(person.find('.//name.note').text)
        if biography.text is not None:
            persondets.append(biography)
        deathdate = ET.Element('deathdate')
        if person.find('.//death.date.start') is not None and person.find('.//death.date.start').text is not None:
            deathdate.text = person.find('.//death.date.start').text
        if deathdate.text is not None:
            persondets.append(deathdate)

        return persondets

recs = 0

# perlist = []

# for f in locate('*.xml', '/dc/fii/data/master/fii0002'):
#     recs += 1
#     perlist.append('%s|%s\n' % (f.split('_')[-1].replace('.xml', ''), f))
#     sys.stdout.write('\033[92mNumber of records seen:\033[0m %s\r' % recs)
#     sys.stdout.flush()

# with open('/home/cmoore/svn/trunk/cstore/gs4/libdata/fiipers_existing.lut', 'w') as out:
#     for item in perlist:
#         out.write(item)

# recs = 0

master_pers = buildLut('fiipers_existing.lut')
perprods = defaultdict(list)
persubjs = defaultdict(list)


'''What do I need to gather from the incoming person records for existing people?
- Production details formatted like:
        <production_details>
          <production_title>Lesbian Vampire Killers</production_title>
          <release_year>2008</release_year>
          <person_castrole>the storyteller/vicar</person_castrole>
        </production_details>

- Production details formatted like:
        <production_details>
          <production_title>Lesbian Vampire Killers</production_title>
          <release_year>2008</release_year>
          <person_creditrole>the storyteller/vicar</person_castrole>
        </productions_details>


- Updated production_roles/activity
- Updated birth and death
- Updated nationality
- Updated notes
- Updated subjects (production title) (DONE)

'''

parser = ET.XMLParser(remove_blank_text=True)

for f in locate('*.xml', indir):
    tree = ET.iterparse(f, tag="record", huge_tree=True)

    for _, record in tree:
        recs += 1

        for person in record.findall('.//cast'):
            proddetails = fiiPersonProcessing().existing_productiondetails(person)
            persondetails = fiiPersonProcessing().existing_persondetails(person)
            # fiiPersonProcessing().existing_subjects(person)
            siftid = [sift.find('.//utb.content').text for sift in person.findall('.//utb') if sift.find('.//utb.fieldname').text == 'SIFT ID']
            if len(siftid) > 0:
                for sift in siftid[0], siftid[0].zfill(8):
                    if sift in master_pers.keys():
                        # try:
                        #     perprods[sift].append(filmtitle[0])
                        # except IndexError:
                        #     print 'No title found for %s' % master_pers[sift]
                        perprods[sift].append(proddetails)
                        subject = (ET.Element('subject', type="production"))
                        subject.text = proddetails.find('.//production_title').text
                        perprods[sift].append(subject)
                        if len(persondetails) > 0:
                            for item in persondetails:
                                perprods[sift].append(item)
                        # master_per_tree = ET.parse(master_pers[sift])
                        # print ET.tostring(master_per_tree.getroot(), pretty_print=True)

        sys.stdout.write('\033[92mNumber of records seen:\033[0m %s\r' % recs)
        sys.stdout.flush()

        # if recs == 10:
        #     exit()

    # master_per_tree = ET.parse(master_pers[[item for item in perprods]])
    # print master_per_tree
    print '\n'
    print perprods
    for item in perprods:
        outfname = '%s/fii0002%s' % (outdir, master_pers[item].split('fii0002')[1])
        if not os.path.exists(os.path.dirname(outfname)):
            os.makedirs(os.path.dirname(outfname))
        master_per_tree = ET.parse(master_pers[item], parser)
        master_per_root = master_per_tree.getroot()
        productions = master_per_root.find('.//productions')
        subjects = master_per_root.find('.//subjects')
        notes = master_per_root.find('.//notes')
        for i in perprods[item]:
            if i.tag == 'production_details':
                productions.insert(0, i)
            elif i.tag == 'subject':
                subjects.append(i)
            elif i.tag == 'note':
                if notes is not None and notes.find('.//note').text != i.text:
                    notes.append(i)

    #         productions.insert(0, i)
        # for i in persubjs[item]:
        #     subjects = master_per_root.find('.//subjects')
        #     subject = ET.Element('subject', type="production")
        #     subject.text = i
        #     subjects.append(subject)
        with open(outfname, 'w') as out:
            out.write(ET.tostring(master_per_root, pretty_print=True))
