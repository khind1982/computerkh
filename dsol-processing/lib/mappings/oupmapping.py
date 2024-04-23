#!/usr/local/bin/python2.6
# -*- mode: python -*-
"""format oup data for new platform"""
import sys
import os
#import re
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))
#??import amara
from commonUtils import *
from abstractmapping import AbstractMapping
#import codecs
#import time
#from datetime import datetime, date, time

 
class OupMapping(AbstractMapping):
    """map input fields to output field"""
    def __init__(self, rawrecord):
        AbstractMapping.__init__(self, rawrecord)
        self._fields = ['eid', 'hg', 'contributors', 'fulltext', 'bibliography']
        #print self._record
        #print self.__dict__
        self.productId = u'IIPAREF'
        #self.gs4.productId =self.productId+'-'
        self.gs4.uptime = (datetime.now()).strftime("%Y%m%d%H%M%S")
        self._dtable =  {"eid":OupMapping.recordId,
                        "hg":OupMapping.recordTitle,
                        "contributors":OupMapping.recordAuthor,
                        "bibliography":OupMapping.recordBibliography,
                        "fulltext":OupMapping.recordFullText
                        }
    
    def recordId(self, data):
        """id & legacy id"""
        self.record.eid = unicode(data.xml_xpath('//@eid')[0])
        self.gs4.eid = textUtils.cleanAndEncode(self.record.eid)
        self.gs4.legacyId = self._prefixedLegacyId(self.record.eid)
             
    def recordTitle(self, data):
        """title"""
        self.record.hg = unicode(data.xml_xpath('//hg')[0])  
        self.gs4.entry = textUtils.cleanAndEncode(self.record.hg)
        
    def recordAuthor(self, data):
        """contributors: author, co-author ,translator"""
        self.gs4.author = []
        allauth = data.xml_xpath('//contributors')
        if allauth:
            firstAuth = 'yes'
            counter = 0
            for auth in allauth:
                authlist = auth.xml_xpath('auth')
                for one in authlist:
                    one1 = textUtils.cleanAndEncode(unicode(one))
                    if one1 != '':
                        counter += 1
                        order = counter
                        if one1.find('trans.') != -1:
                            role = 'Translator'
                        else:
                            #the first encountered author=author ..followings =coauth
                            if firstAuth == 'yes':
                                role = 'Author'
                                firstAuth = 'no'
                            else:
                                role = 'CoAut'
                        one1 = one1.replace('trans.', '')
                        self.gs4.author.append(str(order) + '|' + role + '|' + textUtils.cleanAndEncode(one1.strip()))
                    else:
                        continue
                                
    def recordFullText(self, data):
        """full text"""
        ftdata = data.xml_xpath('//fulltext')
        #print ftdata
        if ftdata:
            self.record.fulltext = unicode(data.xml_xpath('//fulltext')[0])
            self.gs4.fulltext = textUtils.cleanAndEncode(self.record.fulltext, escape = False)       
    
    def recordBibliography(self, data):
        """bibliography"""
        #exeption when bibliography is within fulltext 1 in t74 e2706
        bib = data.xml_xpath('//Bibliography')
        if bib:
            self.record.bibliography = unicode(data.xml_xpath('//Bibliography')[0])
            combineddata = self.gs4.fulltext + '\nBibliography:\n' + self.record.bibliography.strip()
            self.gs4.fulltext = textUtils.cleanAndEncode(combineddata, escape = False )
            
    def computedValues(self):
        """fulltext=component"""
        pass
   
    def do_mapping(self):
        """main"""
        data = self._rawrecord
        for field in self._fields:
            self._dtable[field](self, data)
                

'''   
./transform -o directory=/dc/perfarts/oup/oup_cleaned_files/t74_outputs,io=t74 -f oupfil oup  /dc/perfarts/oup/oup_cleaned_files/t74impout.xml

./transform -o directory=/dc/perfarts/oup/oup_cleaned_files/t177_outputs,io=t177 -f oupfil oup  /dc/perfarts/oup/oup_cleaned_files/t177impout.xml

'''