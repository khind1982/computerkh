#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

from lutbuilder import buildLut

# I am trying to speed up the transformation by pulling out these definitions
# into a module that gets imported only once, when the IMPAMapping class is
# defined, and attached to each instance as it is created, rather than 
# defining the whole lot for each instance. We'll see how that goes...

documentTypes = {
    'Biographical Profile':       u'Biography',
    'Book Excerpt':               u'Book Chapter',
    'Book Illustrations':         u'Illustration',
    'Correspondence (Text)':      u'Letter',
    'Discography':                u'Discography/Filmography',
    'Essay (Text)':               u'Essay',
    'Eulogy':                     u'Obituary',
    'Exhibit Review':             u'Exhibition Review',
    'Filmography':                u'Discography/Filmography',
    'General Review':             u'Review',
    'Instruction/Guidelines':     u'Instruction/Guidelines',
    'Lecture':                    u'Speech/Lecture',
    'Letter to the Editor':       u'Letter',
    'Listening Guide':            u'Instruction/Guidelines',
    'Literary Criticism':         u'Essay',
    'Memoirs':                    u'Memoir/Personal Document',
    'Multimedia/Software Review': u'Software Review',
    'Music Review':               u'Audio Review',
    'Musical Catalog':            u'Catalog',
    'Organizational Profile':     u'Company Profile',
    'Photoessay':                 u'Essay',
    'Play (Text)':                u'Fiction',
    'Poem (Text)':                u'Poem',
    'Profile':                    u'Biography',
    'Radio Review':               u'Audio Review',
    'Recording Review':           u'Audio Review',
    'Roundtable Discussion':      u'Transcript',
    'Screenplay':                 u'Fiction',
    'Speech':                     u'Speech/Lecture',
    'Statistics':                 u'Statistics/Data Report',
    'Story (Text)':               u'Fiction',
    'Tbl of Contents':            u'Table of Contents',
    'Text Excerpt':               u'Fiction',
    }

productElementNames = {
    'char':           u'Char',
    'fulltextflag':   u'FulltextFlag',
    'autoftflag':     u'AutoftFlag',
    'jstor':          u'Jstor',
    'musecollection': u'MuseCollection',
    'naxoscomposer':  u'NaxosComposer',
    'royaltiesid':    u'RoyaltiesID',
    'tngflag':        u'TngFlag',
    }

# This seems to yield the biggest time saving:
#iimprids = buildLut(os.path.join('../libdata', 'iimprids'), delimiter=':')
#iiparids = buildLut(os.path.join('../libdata', 'iiparids'), delimiter=':')
paopdfPageCounts = buildLut('/dc/dsol/steadystate/misc/impa_shortened.lut', delimiter='\t')
iimpInno = [line.strip() for line in open(os.path.join(os.path.dirname(__file__), '../../libdata', 'iimpinnodata.txt'))]
iipaInno = [line.strip() for line in open(os.path.join(os.path.dirname(__file__), '../../libdata', 'iipainnodata.txt'))]

# A temporary hack (!) to include DIDs that are not yet in the STAR data.
futzIDs = buildLut('/dc/dsol/steadystate/misc/impa_articleid_to_docid.list', delimiter='\t')
