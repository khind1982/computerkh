#pylint:disable=W0201,F0401,W0142,C0301
# put bit in threading to check file has xml ending!
# check file paths for threading data

# use ssdiff's superior chunking technique
# escape title strings properly
# put unique index on pageimages.pageimage (or make primary key?)

import sys
import os, os.path, re
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import codecs
from decimal import Decimal
import warnings

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import MySQLdb

from eima_pcmi_template import eima_pcmi_template
from eima_pagemap_template import eima_pagemap_template


from mappings.rules import general

from _mysql_exceptions import ProgrammingError

#
# >>> a = pagemapgenerator()
# >>> a.getresizefactors('resize.list')
# >>> a.gatherdata('/dc/popcult-images/sample')
# >>> a.createhandoverdirs('/dc/scratch/electra/eima_metadata')
# >>> a.createPCMIfiles()
# >>> a.createpagemapfiles()
# >>> a.populate_pagethreading()
# >>> a.populate_hithighlighting_threading()
#

# ppulate_hithightlingnthreadinf will mess up if table isn't truncated first
# delete all entries of required type first?

class pagemapgenerator:

    def __init__(self, product):

        self.product = product
        self.dbconnect()
        self.zonecoordres = {
                            'ulx': re.compile('<APS_ULX>(.*?)</APS_ULX>'),
                            'uly': re.compile('<APS_ULY>(.*?)</APS_ULY>'),
                            'lrx': re.compile('<APS_LRX>(.*?)</APS_LRX>'),
                            'lry': re.compile('<APS_LRY>(.*?)</APS_LRY>')
                            }
        self.pageimagere = re.compile('<APS_page_image.*?>(.*?)</APS_page_image>')
        self.pagenumre = re.compile('<APS_zone_pagenumber>(.*?)</APS_zone_pagenumber>')
        self.pageseqre = re.compile('<APS_page_sequence>(.*?)</APS_page_sequence>')
        #pylint:disable=W1401
        self.pcidissuedetailsre = re.compile('(.*?)_(\d{4})(\d{2})\d{2}')
        if self.product == 'wwd':
            self.docidre = re.compile('((WWD001_\d{8}_\d{2})_\d{3}.*).xml')
        else:
            self.docidre = re.compile('(?:APS_)?((.*?_.*?)_.*?).xml')

    def dbconnect(self):
        dbargs = {'user': 'eima',
                    'db': self.product,
                    'host': 'dsol',
                    'passwd': 'eima'
                    }

        self.dbconn = MySQLdb.connect(**dbargs)
        self.cu = self.dbconn.cursor()

    def threadingdbconnect(self):
        dbargs = {'user': 'root',
                    'db': self.product,
                    'host': 'mysql-server'
                    }

        self.threaddbconn = MySQLdb.connect(**dbargs)
        self.threadcu = self.threaddbconn.cursor()


    def gatherdata(self, directory):

        #self.cu.execute("""TRUNCATE TABLE zones;""")
        #self.cu.execute("""TRUNCATE TABLE pageimages;""")

        doctitlere = re.compile('<APS_title.*?>(.*?)</APS_title>')
        doctypere = re.compile('<APS_article.* type="(.*?)"')
        filesseen = 0


        with open("pagemap_bugs.log", "w") as self.outfile:
            #outfile.write("starting...\n")
            for direc in os.walk(directory):
                direc[1].sort()
                for infile in sorted(direc[2]):
                    if infile[-4:] == '.xml':
                        filesseen += 1
                        self.outfile.write("seen %s files; current file %s\n" % (str(filesseen), infile))

                        with open(os.path.join(direc[0], infile), 'r') as inp:
                            self.doctitle = ''
                            self.doctype = ''
                            inthezone = 0
                            currentzone = ''
                            self.recordid = self.docidre.search(infile).group(1)
                            self.recordid = self.recordid.replace('_final', '')
                            self.pcid = self.docidre.search(infile).group(2)
                            # I'm pretty sure ssdiff handles this better - abstract out at some point?
                            for line in inp:
                                #outfile.write("Found a line\n")
                                if doctitlere.search(line) != None:
                                    self.doctitle = doctitlere.search(line).group(1)
                                if doctypere.search(line) != None:
                                    self.doctype = doctypere.search(line).group(1)
                                if inthezone == 1:
                                    currentzone += line
                                if line.find('</APS_zone>') != -1:
                                    inthezone = 0
                                    #outfile.write("A zone:" + currentzone)
                                    self.storezonedata(currentzone)
                                    currentzone = ''
                                if line.find('<APS_zone ') != -1:
                                    inthezone = 1
                                    currentzone = line

    def getresizefactors(self, resizefile):
        #pylint:disable=W1401
        self.resizefactors = {}
        if self.product == 'eima':
            resizere = re.compile('.*(APS_.*?)\.jpg (\d+) (\d+)')
        else:
            resizere = re.compile('.*/(.*?)\.jpg (\d+) (\d+)')
        #151435/APS_151435_19520423/APS_151435_19520423-028.jpg 3087 700
        with open(resizefile, 'r') as inp:
            for line in inp:
                if resizere.search(line) != None:
                    pageimage = resizere.search(line).group(1)
                    originalsize = Decimal(resizere.search(line).group(2))
                    newsize = Decimal(resizere.search(line).group(3))
                    resizefactor = originalsize / newsize
                    self.resizefactors[pageimage] = resizefactor

    def storezonedata(self, zone):
        coords = {}
        #print "ZONE: %s" % zone
        #exit()
        pageimage = self.pageimagere.search(zone).group(1)[:-4]
        #print "PAGEIMAGE: %s" % pageimage
        #print self.resizefactors
        #exit()
        if pageimage in self.resizefactors:
            resizefactor = self.resizefactors[pageimage]
        else:
            print "No resize factor for " + pageimage
            resizefactor = Decimal(5)

        try:
            for coordtype in self.zonecoordres.keys():
                originalcoord = Decimal(self.zonecoordres[coordtype].search(zone).group(1))
                resizedcoord = originalcoord / resizefactor
                coords[coordtype] = str(int(resizedcoord))
        except AttributeError:
            print "Zone details: " + zone
            coords = {'ulx': '1', 'uly': '1', 'lrx': '1000', 'lry': '1000'}

        pagenum = self.pagenumre.search(zone).group(1)
        pageseq = self.pageseqre.search(zone).group(1)

        if self.doctitle.strip() == "":
            self.doctitle = normalise(self.doctype)

        try:
            self.doctitle = general.title(self.doctitle)
        except TypeError as e:
            print "doctitle is invalid: %s.  %s" % (self.doctitle, self.recordid)
            raise

        zonesql = ("""INSERT INTO zones (pageimage, docid, title, uly, ulx, lry, lrx)
                        VALUES("%s", "%s", "%s", "%s", "%s", "%s", "%s");"""
                                % (pageimage, self.recordid, self.doctitle.replace('"', '\\\"'), coords['uly'],
                                    coords['ulx'], coords['lry'], coords['lrx']))
        try:
            self.cu.execute(zonesql)
        except UnicodeEncodeError:
            print self.recordid, pageimage
            raise

        pageimagesql = ("""INSERT IGNORE INTO pageimages (pageimage, pcid, pagenum, pageseq)
                            VALUES("%s", "%s", "%s", "%s");"""
                                % (pageimage, self.pcid, pagenum, pageseq))

        try:
            self.cu.execute(pageimagesql)
        except ProgrammingError:
            print "Broken record: %s" % self.recordid
            print "%s: %s: %s: %s" % (pageimage, self.pcid, pagenum, pageseq)
            raise


    def createhandoverdirs(self, rootdir):
        self.cu.execute("""SELECT DISTINCT pcid FROM pageimages;""")
        pcids = self.cu.fetchall()
        journalids = {}  #pylint:disable=W0612
        self.outputroot = rootdir
        #issuedetailsre = re.compile('(.*?)_(\d{4})(\d{2})\d{2}')
        for pcidrow in pcids:
            pcid = pcidrow[0]
            pcidpath = self.getpathfrompcid(pcid)
            try:
                os.makedirs(os.path.join(self.outputroot, pcidpath, 'xml/pcmi'))
                os.makedirs(os.path.join(self.outputroot, pcidpath, 'xml/pagemap'))
                #os.makedirs(os.path.join(rootdir, journalid, year, month, coords))
            except OSError:
                pass

    def getpathfrompcid(self, pcid):
        journalid = self.pcidissuedetailsre.search(pcid).group(1)
        year = self.pcidissuedetailsre.search(pcid).group(2)
        month = self.pcidissuedetailsre.search(pcid).group(3)
        return os.path.join(journalid, year, month)

    def createPCMIfiles(self):

        self.cu.execute("""SELECT DISTINCT pcid FROM pageimages;""")
        pcids = self.cu.fetchall()
        for pcidrow in pcids:
            pcid = pcidrow[0]
            self.cu.execute("""SELECT * FROM pageimages WHERE pcid="%s" ORDER BY pageseq;""" % pcid)
            template = eima_pcmi_template()
            template.pages = []
            for page in self.cu.fetchall():
                pagedict = {
                    'product': self.product,
                    'pageid': page[0],
                    'pcid': pcid,
                    'pagenum': page[2],
                    'pageseq': page[3]
                    }
                template.pages.append(pagedict)
            pcidpath = self.getpathfrompcid(pcid)
            with open(os.path.join(self.outputroot, pcidpath, 'xml/pcmi', pcid + '.xml'), 'w') as outf:
                outf.write(template.respond())

    def createpagemapfiles(self):

        self.cu.execute("""SELECT pageimage, pcid, pageseq FROM pageimages;""")
        pages = self.cu.fetchall()
        for page in pages:
            template = eima_pagemap_template()
            pagedict = {
                        'pageid': page[0],
                        'pcid': page[1],
                        'pageseq': page[2],
                        'zones': []
                        }
            self.cu.execute("""SELECT * FROM zones WHERE pageimage="%s" ORDER BY uly;""" % page[0])
            for zone in self.cu.fetchall():
                zonedict = {}
                zonedict['docid'] = zone[2]
                zonedict['title'] = zone[3]
                zonedict['uly'] = zone[4]
                zonedict['ulx'] = zone[5]
                zonedict['lry'] = zone[6]
                zonedict['lrx'] = zone[7]
                pagedict['zones'].append(zonedict)
            template.page = pagedict
            pcid = page[1]  #pylint:disable=W0612
            pcidpath = self.getpathfrompcid(pagedict['pcid'])
            with codecs.open(os.path.join(self.outputroot, pcidpath, 'xml/pagemap', pagedict['pageid'] + '.xml'), 'w', 'utf8') as outf:
                t = template.respond()
                outf.write(t)

    def populate_pagethreading(self):


        self.threadingdbconnect()
        self.threadcu.execute("""TRUNCATE TABLE pagecollection_threading;""")

        pagere = re.compile('((?:APS_)?(.*?)_.*?)-(.*?)')

        self.cu.execute("""SELECT DISTINCT pcid FROM pageimages;""")
        pcids = self.cu.fetchall()
        for pcidrow in pcids:
            pcid = pcidrow[0]
            pcidpath = self.getpathfrompcid(pcid)
            self.threadcu.execute("""INSERT INTO pagecollection_threading (pcid, path, type)
                                    VALUES ("%s", "%s", "%s");"""
                                        % (pcid,
                                            os.path.join('/' + pcidpath, 'xml/pcmi', pcid + '.xml'),
                                            'PCMI'))

        self.cu.execute("""SELECT pageimage, pcid, pageseq FROM pageimages;""")
        pages = self.cu.fetchall()
        for page in pages:
            pageimage = page[0]
            pcid = page[1]
            pageseq = page[2]
            pcidpath = self.getpathfrompcid(pcid)
            self.threadcu.execute("""INSERT INTO pagecollection_threading (pcid, pageno, path, type)
                                    VALUES ("%s", "%s", "%s", "%s");"""
                                        % (pcid, pageseq,
                                                os.path.join('/' + pcidpath, 'xml/pagemap', pageimage + '.xml'),
                                                'PAGEMAP'))

            pubid = pagere.search(pageimage).group(2)
            issuestring = pagere.search(pageimage).group(1)
            #self.threadcu.execute("""INSERT INTO pagecollection_threading (pcid, pageno, path, type)
            #                        VALUES ("%s", "%s", "%s", "%s");"""
            #                            % (pcid, pageimage,
            #                                    os.path.join(pubid, issuestring, pageimage + '.jpg'),
            #                                    'IMG'))
            self.threadcu.execute("""INSERT INTO pagecollection_threading (pcid, pageno, path, type)
                                    VALUES ("%s", "%s", "%s", "%s");"""
                                        % (pcid, pageseq,
                                                os.path.join('/' + pubid, issuestring, 'scaled', pageimage + '.jpg'),
                                                'SCALED_IMG'))
        self.threadcu.close()
        self.threaddbconn.close()

    def populate_hithighlighting_threading(self):

        self.threadingdbconnect()
        self.threadcu.execute("""DELETE FROM threading WHERE type='co';""")
        self.threadcu.execute("""SELECT DISTINCT aid FROM threading;""")
        aids = self.threadcu.fetchall()
        for aidrow in aids:
            aid = aidrow[0]
            try:
                journalid = self.pcidissuedetailsre.search(aid).group(1)
            except AttributeError:
                print aidrow
                continue
            year = self.pcidissuedetailsre.search(aid).group(2)
            month = self.pcidissuedetailsre.search(aid).group(3)
            coordspath = os.path.join('/', journalid, year, month, "coords", aid)
            self.threadcu.execute("""INSERT INTO threading (aid, path, type)
                                    VALUES ("%s", "%s", "%s");"""
                                        % (aid, coordspath, "co"))
        self.threadcu.close()
        self.threaddbconn.close()

    def undoload(self, directory):
        """Remove all records from all SQL databases that relate to document and page
        collection IDs found in the data stored in specified directory.

        Use this when a load fails and you want to roll the SQL databases back to the state
        they were in before it.

        Currently excludes the data in pagecollection_threading as loads will usually
        fail before that table gets populated.

        """

        self.threadingdbconnect()

        for direc in os.walk(directory):
            for infile in direc[2]:
                if infile[-4:] == '.xml':
                    docidmatch = self.docidre.search(infile)
                    docid = docidmatch.group(1)
                    pcid = docidmatch.group(2)

                    self.cu.execute("""DELETE FROM pageimages WHERE pcid = "%s";""" % pcid)
                    self.cu.execute("""DELETE FROM zones WHERE docid = "%s";""" % docid)

                    self.threadcu.execute("""DELETE FROM threading WHERE aid = "%s";""" % docid)

        self.threadcu.close()
        self.threaddbconn.close()

def normalise(string):
    string = string.replace('_', ' ')
    words = string.split()
    if len(words) > 0:
        words[0] = words[0].capitalize()
        words[-1] = words[-1].capitalize()
        return (' ').join(words)
    else:
        return


# """

# <PageMap>
#   <PcId>xxx_xxxx from docname</PcId>
#   <PageNum>actual page number or sequential position?</PageNum>
#   <Zone>
#     <DocId>file name, replace APS_ with eima-</DocId>
#     <Title>Advertisement: Dolce &amp; Gabbana (Dolce &amp; Gabbana)</Title>
#     <Blocked>false</Blocked>
#     <Top>1</Top>
#     <Left>1</Left>
#     <Bottom>960</Bottom>
#     <Right>698</Right>
#   </Zone>
#   <Zone>
#     <DocId>200708010010</DocId>
#     <Title>Advertisement: Dolce &amp; Gabbana (Dolce &amp; Gabbana)</Title>
#     <Blocked>false</Blocked>
#     <Top>29</Top>
#     <Left>33</Left>
#     <Bottom>130</Bottom>
#     <Right>56</Right>
#   </Zone>
#   <Zone>
#     <DocId>200708010010</DocId>
#     <Title>Advertisement: Dolce &amp; Gabbana (Dolce &amp; Gabbana)</Title>
#     <Blocked>false</Blocked>
#     <Top>795</Top>
#     <Left>15</Left>
#     <Bottom>957</Bottom>
#     <Right>696</Right>
#   </Zone>
# </PageMap>

# """
