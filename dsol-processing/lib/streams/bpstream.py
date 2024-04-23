#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os, re
#sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../../../../lib/python'))
#sys.path.append('/packages/dsol/lib/python')

import warnings
from cstoreerrors import *
from citations.bp.bpRecord import BPJournal, streamrecordsforPQIS

from abstractstream import AbstractStream

class BPStream(AbstractStream):
    def __init__(self, cfg):          # product, stream, streamopts
        AbstractStream.__init__(self, cfg)
        self._stream = cfg['stream']
        extractionargs = cfg['streamOpts'].split(',')
        for a in extractionargs:
            print a
        self._journalid = extractionargs[0]
        self._journalfile = cfg['journalsfile']
        #self._imagesizefile = cfg['imagesizefile']
        if len(extractionargs) > 1:
            self._partsize = int(extractionargs[1])
            if len(extractionargs) > 2:
                self._startpart = int(extractionargs[2])
            else:
                self._startpart = 0
            if len(extractionargs) > 3:
                self._endpart = int(extractionargs[3])
            else:
                self._endpart = None
        else:
            self._partsize = 5000
            self._startpart = 0
            self._endpart = None
        self.getjournaldetails()
        #self.getimagesizes()

    def getjournaldetails(self):

        inf = open(self._journalfile, 'r')
        jdata = inf.read()
        inf.close()
    
        jdocs = jdata.split('</document>')
        #jidre = re.compile('<element name="journalid">' + self._journalid + '</element>')
        jidre = re.compile('<element name="journalid">(.*?)</element>')
        publre = re.compile('<element name="publisher">(.*?)</element>')
        subjre = re.compile('<element name="subject">(.*?)</element>')
        collre = re.compile('<element name="subscription">(.*?)</element>')
        issnre = re.compile('<element name="issn">(.*?)</element>')
    
        self._journaldetails = {}
    
        for doc in jdocs:
            if jidre.search(doc) != None:
                currentdocjid = jidre.search(doc).group(1)
                self._journaldetails[currentdocjid] = {}
                if publre.search(doc) != None:
                    self._journaldetails[currentdocjid]['publisher'] = publre.search(doc).group(1)
                if subjre.search(doc) != None:
                    self._journaldetails[currentdocjid]['subjects'] = subjre.search(doc).group(1).split('|')
                if collre.search(doc) != None:
                    self._journaldetails[currentdocjid]['collection'] = collre.search(doc).group(1)
                if issnre.search(doc) != None:
                    self._journaldetails[currentdocjid]['issn'] = issnre.search(doc).group(1)
                
        del jdata
        del jdocs
        return self._journaldetails

    def getimagesizes(self):
        inf = open(self._imagesizefile, 'r')
        self._imagesizes = {}
        imgandsizere = re.compile('(EBP[0-9_]*)\t([0-9]*)')
        journalflag = 0
        print self._journalid
        for line in inf:
            if journalflag == 0:
                if line.find('images\\bp\\' + self._journalid) != -1:
                    #print "got here 3"
                    journalflag = 1
            elif line.find('\\images\\bp\\') != -1:
                journalflag = 0
            else:
                #print "got here 1"
                imgmatch = imgandsizere.search(line)
                if imgmatch != None:
                    #print "got here 2"
                    self._imagesizes[imgmatch.group(1)] = imgmatch.group(2)
        inf.close()

    
    def streamdata(self):
        if 'recordids' in self._cfg.keys():
            for record in streamrecordsforPQIS(self._cfg['recordids']):
                self._count += 1
                self._cfg['index'] = self._count
                record.__dict__['_cfg'] = self._cfg
                record._journaldetails = self._journaldetails[record.journalid]
                yield record
                
        else:
            j = BPJournal()
            for record in j.helios(self._journalid, self._partsize, self._startpart, self._endpart):
                self._count += 1
                self._cfg['index'] = self._count
                record.__dict__['_cfg'] = self._cfg
                record._journaldetails = self._journaldetails[self._journalid]
                #record._imagesizes = self._imagesizes
                #print record.PartJournalTitleSet[0].journaltitle
                yield record
        
