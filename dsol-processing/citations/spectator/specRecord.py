import re
import codecs
import sys
import thread
import gc
import os, sys
from time import gmtime, sleep

import MySQLdb
import roman
import amara

from citations.base.baseRecord import BaseRecord, BaseRecordSet
from citations.wellesley.wellesleyRecord import WellesleyRecordSet

from citations.pao.sptemplates import SPrecord_template
from citations.pao.sptemplates import DS_SPrecord_template
from citations.pao.sptemplates import SPsft_template
from citations.pao.sptemplates import SPtab_template
from time import localtime, strftime
def databaseConnection():
    """Connect to the British Periodicals MySQL database. Try three times."""
    for attempt in range(1,3):
        try:
            return MySQLdb.connect(host="localhost", user="spectator", passwd="spectator", db="spectator",
            use_unicode=True, charset="latin1")
        except:
            print 'Attempt number ' + str(attempt)
            print 'Problem connecting to the database. Will sleep for 60 seconds and then try again.'
            sleep(60)
            continue

"""TAG_EXP is a regular expression for any tag. We'll want to strip out tags from Wellesley data later on."""
TAG_EXP = re.compile('<.*?>')
"""PAGE_IMAGE_EXP is a regular expression to find page images. Useful for generating the .tab files which contain
page image information."""
PAGE_IMAGE_EXP = re.compile("<.*?_page_image>(.*?.tif)</.*?_page_image>")
"""ZONE_EXP is a regular expression used to identify individual zones within the source XML document."""
ZONE_EXP = re.compile('<BP_zone.*?</BP_zone>', re.DOTALL)
"""ILLUSTRATION_EXP is a regular expression used to identify a special sort of zone reserved for illustrations."""
ILLUSTRATION_EXP = re.compile('<BP_zone[ A-z"=0-9]*?type="image".*?</BP_zone>', re.DOTALL)
"""WORD_EXP is a regular expression used to pull out all the individual words from a text document."""
WORD_EXP = re.compile('<BP_word.*?</BP_word>', re.DOTALL)

"""This is the pathname to where the source xml documents are delivered."""
#FULLTEXTPATH = '/dc/bp/xml'
#temporary until files are unzipped
FULLTEXTPATH = '/dc/pao/xml'

"""A dictionary which maps number patterns that occur in the date field to months or seasons."""
MONTHMAP = {
    '01': 'Jan.',
    '02': 'Feb.',
    '03': 'Mar.',
    '04': 'Apr.',
    '05': 'May',
    '06': 'June',
    '07': 'July',
    '08': 'Aug.',
    '09': 'Sept.',
    '10': 'Oct.',
    '11': 'Nov.',
    '12': 'Dec.',
    '21': 'Spring',
    '22': 'Summer',
    '23': 'Autumn',
    '24': 'Winter'
}

"""Some articles in the source XML don't have titles. This dictionary is used to infer a title from the article type."""
TYPETITLEMAP = {
    'ad': 'Advertisement',
    'article': 'Untitled item',
    'back matter': 'Back matter',
    'back_matter': 'Back matter',
    'banner': 'Unindexed matter',
    'cover': 'Cover',
    'drama': 'Drama',
    'fiction': 'Fiction / Narrative',
    'front matter': 'Front matter',
    'front_matter': 'Front matter',
    'graphic': 'Illustration',
    'letter': 'Letter',
    'masthead': 'Unindexed matter',
    'obituary': 'Obituary',
    'other': 'Untitled item',
    'poem': 'Poem',
    'recipe': 'Recipe',
    'review': 'Book review',
    'statistics': 'Unindexed matter',
    'table of contents': 'Table of contents',
    'table_of_contents': 'Table of contents',
    'tbl_of_contents': 'Table of contents'
}

"""The source xml article types have variants. This table maps all known variants to a normalized form."""
NORMALIZEDTYPES = {
    'ad': 'Advertisement',
    'article': 'Article',
    'back matter': 'Back matter',
    'back_matter': 'Back matter',
    'cover': 'Cover',
    'drama': 'Drama',
    'fiction': 'Fiction',
    'front matter': 'Front matter',
    'front_matter': 'Front matter',
    'graphic': 'Graphic',
    'letter': 'Letter',
    'masthead': 'Masthead',
    'obituary': 'Obituary',
    'other': 'Other',
    'poem': 'Poem',
    'recipe': 'Recipe',
    'review': 'Review',
    'table of contents': 'Table of contents',
    'table_of_contents': 'Table of contents',
    'tbl_of_contents': 'Table of contents'
}


"""Two lookups are created here to map illustration codes to the illustration types found in the source xml."""
db = databaseConnection()
cu = db.cursor()
cu.execute("""SELECT * FROM illustrationtype;""")
ILLUSTYPES = dict([(row[1], row[2]) for row in cu.fetchall()])
cu.close()
db.close()

ILLUSCODES = dict([(y,x) for x, y in ILLUSTYPES.items()])

"""Here is a dictionary to map the pmid which is the journal identifier used by Apex to the journalid used
by us. Important thing is that often many pmids map to one journalid."""
db = databaseConnection()
cu = db.cursor()
cu.execute("""SELECT * FROM pmid_journal;""")
PMID_JOURNAL = dict([(str(row[0]), row[1]) for row in cu.fetchall()])
cu.close()
db.close()




class bpEntityConverter:
    """A simple class to filter the output from bp data at the time the templates are created."""
    
    def convert(self, instring):
        #print "converting characters..."
        outstring = instring.replace('&amp;', '&')
        outstring = outstring.replace('&quot;', '"')
        outstring = outstring.replace('&apos;', "'")
        outstring = outstring.replace('&amp;', '&')
        #outstring = outstring.encode('ascii', 'xmlcharrefreplace')
        return outstring
        #return outstring.encode('utf8')





class BPRecordSet(BaseRecordSet):
    
    """This class represents a set of British Periodicals records.
    """
    
    def __init__(self):
        self.databaseConnection = databaseConnection
    
    def InferPageNumbers(self):
        """This method looks through all the records in the set and attempts to provide sensible values
        when the page number information in the source files is not sufficient.
        To run it in a meaningful way you should really have the records in the set to be ordered by page number.
        The best way of doing that would be to use an ORDER BY clause when you populate the set.
        """
        lastpagenumber = 0
        previous_page_sequence_end = 0
        previous_page_number_type = 0
        startpage_suggestions = (1, 1)
        LETTERPREFIX = re.compile('[A-Za-z]+([0-9]+)')
        for item in self:
            #print startpage_suggestions
            #print previous_page_sequence_end, previous_page_number_type
            #print '-' * 20
            #print item.startpage
            #print item.endpage
            #print item.nopages
            #print item.page_sequence_start
            #print item.page_sequence_end
            

            item.endpage_conv = None
            # test the endpage            
            try:
                item.endpage_conv = int(item.endpage)
                #print 'End page integer ok!'
            except:
                pass
 
            if item.endpage_conv is None:
                try:
                    item.endpage_conv = roman.fromRoman(item.endpage.upper())
                    #print 'End page Roman numeral ok!'
                except roman.InvalidRomanNumeralError:
                    pass
            
            if item.endpage_conv is None:
                try:
                    item.endpage_conv = int(LETTERPREFIX.search(item.endpage).group(1))
                except:
                    pass
                    
            if item.endpage_conv is None:
                badendpage = True
            else:
                badendpage = False
            # does this item have an acceptable start page number?
            # if so work out what page and page sequence it finished on
            try:
                item.numericpage = int(item.startpage)
                previous_page_sequence_end = item.page_sequence_end
                previous_page_number_type = 0
                if item.endpage_conv is None:
                    startpage_suggestions = (
                        int(item.startpage) + int(item.page_sequence_end) - int(item.page_sequence_start),
                        int(item.startpage) + int(item.page_sequence_end) - int(item.page_sequence_start) + 1
                    )
                    item.endpage_conv = startpage_suggestions[0]
                else:
                    startpage_suggestions = (
                        item.endpage_conv,
                        item.endpage_conv + 1
                    )
                    
                #print 'Integer ok!'
                item.updateDB("sourcefilename", **{
                                'sourcefilename': item.sourcefilename,
                                'startpage_conv': item.numericpage,
                                'endpage_conv': item.endpage_conv
                                }
                )
                continue
            except:
                pass

            try:
                item.numericpage = roman.fromRoman(item.startpage.upper())
                previous_page_sequence_end = item.page_sequence_end
                previous_page_number_type = 1
                if item.endpage_conv is None:
                    startpage_suggestions = (
                        roman.fromRoman(item.startpage.upper()) + int(item.page_sequence_end) - int(item.page_sequence_start),
                        roman.fromRoman(item.startpage.upper()) + int(item.page_sequence_end) - int(item.page_sequence_start) + 1
                    )
                    item.endpage_conv = startpage_suggestions[0]
                else:
                    startpage_suggestions = (
                        item.endpage_conv,
                        item.endpage_conv + 1
                    )

                #print 'Roman numeral ok!'
                item.updateDB("sourcefilename", **{
                                'sourcefilename': item.sourcefilename,
                                'startpage_conv': item.numericpage,
                                'endpage_conv': item.endpage_conv
                                }
                )
                continue
            except:
                pass

            
            try:
                item.numericpage = int(LETTERPREFIX.search(item.startpage).group(1))
                if item.endpage_conv is None:
                    startpage_suggestions = (
                        item.numericpage + int(item.page_sequence_end) - int(item.page_sequence_start),
                        item.numericpage + int(item.page_sequence_end) - int(item.page_sequence_start) + 1
                    )
                    item.endpage_conv = startpage_suggestions[0]
                else:
                    startpage_suggestions = (
                        item.endpage_conv,
                        item.endpage_conv + 1
                    )
                    
                #print 'Integer ok!'
                item.updateDB("sourcefilename", **{
                                'sourcefilename': item.sourcefilename,
                                'startpage_conv': item.numericpage,
                                'endpage_conv': item.endpage_conv
                                }
                )
                continue
            except:
                pass
            
            # if it doesn't:
            #   if the last page seqence is the same as our page sequence:
            #       infer that it starts on the same page as previous article finishes on            
            if item.page_sequence_start == previous_page_sequence_end:
                item.startpage_conv = startpage_suggestions[0]
                if item.endpage_conv is None:
                    item.endpage_conv = startpage_suggestions[0] + int(item.page_sequence_end) - int(item.page_sequence_start)
            #   else:
            #       infer that it starts on the page after the previous article finishes
            else:
                item.startpage_conv = startpage_suggestions[1]
                if item.endpage_conv is None:
                    item.endpage_conv = startpage_suggestions[1] + int(item.page_sequence_end) - int(item.page_sequence_start)
            #   infer that it finishes on the that page + number of pages - 1
            #   copy the format of the previous article as to whether to use roman numerals
            startpage_suggestions = (
                item.endpage_conv,
                item.endpage_conv + 1
            )

            if item.startpage_conv > item.endpage_conv:
                item.startpage_conv = 'n. pag.'

            if previous_page_number_type == 1:
                try:
                    item.startpage_conv = roman.toRoman(item.startpage_conv).lower()
                except:
                    pass
                try:
                    item.endpage_conv = roman.toRoman(item.endpage_conv).lower()
                except:
                    pass
            
            
            
            item.startpage_conv = '[' + str(item.startpage_conv) + ']'
            if badendpage == True:
                item.endpage_conv = '[' + str(item.endpage_conv) + ']'
            previous_page_sequence_end = item.page_sequence_end

            item.updateDB("sourcefilename", **{
                            'sourcefilename': item.sourcefilename,
                            'startpage_conv': item.startpage_conv,
                            'endpage_conv': item.endpage_conv
                            }
            )
 
 
 
 
 
 
 
 
 
class BPJournal(BPRecordSet):
 """This class is a special sort of records which holds all the records for a particular journal.
 It has a set of methods to do bits of work a journal at a time and has a lot of methods which
 correspond to methods in the individual record class.

 The idea is that one can save on queries to the database by fetching all the information we will
 need for a given journal upfront.
 """

 def journaltree(self):
     """Create a dictionary which describes the organization of records in the journal
     in a hierarchical fashion.
     year
         vol/iss
             article
     This isn't actually used don't worry about it.
     """
     treedict = {}
     orderedtree = []
     for item in self:
         item.CreateEnumeration()
         myenum = (item.numericvolume, item.numericissue, item.enumeration)
         if not treedict.has_key(str(item.date)[:4]):
             treedict[str(item.date)[:4]] = {}

         if not treedict[str(item.date)[:4]].has_key(myenum):
             treedict[str(item.date)[:4]][myenum] = []

         treedict[str(item.date)[:4]][myenum].append(item)

     return treedict


 def PopulateByJournalID(self, journalid):
     """This method actually gets all the records for our journal out of the database.
     Importantly it does it in the right order and excludes records that we don't do 
     anything with.

     Something to note here is that you pass the journalid as a parameter to this method.
     It would probably have been better for it to be an attribute of the BPJournal class.

     """
     self.tablename="indexrecord"
     self.recordclass=BPRecord
     self.getdbfields()
     self.freesearch(""" SELECT *
                         FROM indexrecord 
                         WHERE journalid='%s'
                         AND NOT type IN ('masthead', 'statistics', 'banner')
                         AND excluded != 'Y'
                         ORDER BY date, page_sequence_start, sourcefilename;""" % journalid)




 def PopulateByDecade(self, journalid,sentyear):
     """
     process the file on the decade basis (20000-30000 records at a time) instead of loading all the records...which  
      make the extraction very slow because of the  sheer size of the data 
     """
     self.tablename="indexrecord"
     self.recordclass=BPRecord
     self.getdbfields()
     self.freesearch(""" SELECT *
                         FROM indexrecord 
                         WHERE journalid='%s'
                         AND date REGEXP '%s'
                         AND NOT type IN ('masthead', 'statistics', 'banner')
                         AND excluded != 'Y'
                         ORDER BY date, page_sequence_start, sourcefilename;"""% (journalid,sentyear))

 def PopulateThreading(self, journalid):
     """This gets all the image threading information about a journal back."""
     threaddict = {}
     self.ThreadSet = BPRecordSet()
     self.ThreadSet.tablename = 'threading'
     self.ThreadSet.recordclass = BaseRecord
     self.ThreadSet.getdbfields()
     self.ThreadSet.freesearch("""SELECT threading.*
                                  FROM threading, indexrecord
                                  WHERE threading.paoid = indexrecord.paoid
                                  AND indexrecord.journalid = '%s'
                                  ORDER BY threading.paoid, threading.sequence;""" % journalid)

     for threadline in self.ThreadSet:
         if threaddict.has_key(threadline.paoid):
             threaddict[threadline.paoid].append(threadline)
         else:
             threaddict[threadline.paoid] = [threadline]

     for item in self:
         item.ThreadSet = BPRecordSet()
         if threaddict.has_key(item.paoid):
             item.ThreadSet.recordclass = BaseRecord
             item.ThreadSet.fieldnames = self.ThreadSet.fieldnames
             item.ThreadSet += threaddict[item.paoid]


 def PopulateIllustrations(self, journalid):
     """This populates the illustration information for every item in the record set.
     The idea is to do this as a one-off rather than hammering the database with a query
     for every record. So it's an optimization really.
     """
     illustrationdict = {}
     self.IllustrationSet = BPRecordSet()
     self.IllustrationSet.tablename = 'illustration'
     self.IllustrationSet.recordclass = BaseRecord
     self.IllustrationSet.getdbfields()
     self.IllustrationSet.freesearch(""" SELECT illustration.* 
                                         FROM illustration, indexrecord
                                         WHERE illustration.paoid = indexrecord.paoid
                                         AND journalid = '%s'
                                         """ % journalid)

     """Create a local dictionary which tells us for each paoid in our collection that has illustrations,
     which illustrations it has."""
     for illustration in self.IllustrationSet:
         illustration.illusname = ILLUSTYPES[illustration.illuscode]
         if illustrationdict.has_key(illustration.paoid):
             illustrationdict[illustration.paoid].append(illustration)
         else:
             illustrationdict[illustration.paoid] = [illustration]

     """Now do the illustration processing for each record."""
     for item in self:
         item.IllustrationSet = BPRecordSet()
         if illustrationdict.has_key(item.paoid):                
             item.IllustrationSet.recordclass = BaseRecord
             item.IllustrationSet.fieldnames = self.IllustrationSet.fieldnames
             item.IllustrationSet += illustrationdict[item.paoid]
             noillustrationsdict = {}
             """noillustrationdict is a dictionary to key page numbers to the numbers
             of different types of illustrations on that page."""
             for illustration in item.IllustrationSet:
                 if not noillustrationsdict.has_key(illustration.pagecount.__str__()):
                     noillustrationsdict[illustration.pagecount.__str__()] = {}

                 if not noillustrationsdict[illustration.pagecount.__str__()].has_key(illustration.illuscode):
                     noillustrationsdict[illustration.pagecount.__str__()][illustration.illuscode] = 0    
                 noillustrationsdict[illustration.pagecount.__str__()][illustration.illuscode] += 1

             """Some very specific processing goes on here to produce the eventual output that we need.
             For each page in the article we need to know what types of illustration code are present
             and how many of each type. e.g. page 24 has 2 photos and 3 cartoons.
             """
             try:
                 pagecounts = [(int(pgc), pgc) for pgc in noillustrationsdict.keys()]
             except ValueError:
                 pagecounts = [(pgc, pgc) for pgc in noillustrationsdict.keys()]
             pagecounts.sort()
             noillustrations = ''
             for pgc, pagecount in pagecounts:
                 noillustrations += pagecount
                 for illuscode in noillustrationsdict[pagecount]:
                     noillustrations += " " + illuscode + " " + str(noillustrationsdict[pagecount][illuscode])
                 noillustrations += '|'
             if noillustrations.endswith('|'):
                 noillustrations = noillustrations[:-1]
             item.IllustrationSet.noillustrations = noillustrations

 def PopulatePartJournals(self, journalid):
     """
     This populates the part-journal information for every item in the record set.
     The idea is to do this as a one-off rather than hammering the database with a query
     for every record.
     """
     self.PartJournalTitleSet = BPRecordSet()
     self.PartJournalTitleSet.tablename = 'ptjournaltitle'
     self.PartJournalTitleSet.recordclass = BaseRecord
     self.PartJournalTitleSet.getdbfields()
     self.PartJournalTitleSet.freesearch("""
         SELECT * FROM ptjournaltitle 
         WHERE `journalid` = '%s';""" % journalid)

     self.defaultJournalTitleSet = BPRecordSet()
     self.defaultJournalTitleSet.tablename = 'journaltitle'
     self.defaultJournalTitleSet.recordclass = BaseRecord
     self.defaultJournalTitleSet.getdbfields()
     self.defaultJournalTitleSet.freesearch("""
         SELECT * FROM journaltitle 
         WHERE `journalid` = '%s'""" % journalid)

     self.PartJournalEditorSet = BPRecordSet()
     self.PartJournalEditorSet.tablename = 'ptjournaleditor'
     self.PartJournalEditorSet.recordclass = BaseRecord
     self.PartJournalEditorSet.getdbfields()
     self.PartJournalEditorSet.freesearch("""
         SELECT * FROM ptjournaleditor 
         WHERE `journalid` = '%s';""" % journalid)

     for item in self:
         item.PartJournalTitleSet = BPRecordSet()
         item.PartJournalTitleSet.recordclass = BaseRecord
         item.PartJournalTitleSet.fieldnames = self.PartJournalTitleSet.fieldnames
         item.PartJournalEditorSet = BPRecordSet()
         item.PartJournalEditorSet.recordclass = BaseRecord
         item.PartJournalEditorSet.fieldnames = self.PartJournalEditorSet.fieldnames

         for pjt in self.PartJournalTitleSet:
             if item.date >= pjt.startdate and item.date <= pjt.enddate:
                 item.PartJournalTitleSet.append(pjt)

         if len(item.PartJournalTitleSet) == 0:
             item.PartJournalTitleSet = self.defaultJournalTitleSet

         for pje in self.PartJournalEditorSet:
             if item.date >= pje.startdate and item.date <= pje.enddate:
                 item.PartJournalEditorSet.append(pje)



 def processTAB(self, journalid):
     from TerminalController import TerminalController, ProgressBar
     self.PopulateByJournalID(journalid)
     self.PopulateThreading(journalid)
     recordnumber = len(self)
     term = TerminalController()
     print journalid
     bar = ProgressBar(term, str(recordnumber) + " rows in "+str(journalid)+".")

     count = 0
     pccount = 0
     try:
         #***outf = open('/dc/bp/processed_rel4/tab/' + journalid + '.tab', 'w')
         outf = open('/dc/pao/processed_rel1/tab/' + journalid + '.tab', 'w')
         outf.close()
     except:
         print 'Problem opening: ' + journalid+'.tab'
         return

     while len(self) > 0:
         count += 1
         if recordnumber > 99:
             if count % int(0.01 * recordnumber) == 0:
                 pccount += 0.01
                 if pccount > 1:
                     pccount = 1
                 bar.update(pccount, str(count) + " completed.")
         else:
             pccount += float(100) / float(recordnumber*100)
             bar.update(pccount, str(count) + " completed.")
         item = self.pop(0)
         #item.templateclass = BPtab_template.BPtab_template
         item.templateclass = SPtab_template.SPtab_template
         #***outf = codecs.open('/dc/bp/processed_rel4/tab/' + journalid + '.tab', 'a', encoding="latin-1")
         outf = codecs.open('/dc/pao/processed_rel1/tab/' + journalid + '.tab', 'a', encoding="latin-1")
         outf.write(item.FillTemplate())
         outf.close()
         del item

 def processGEN(self, journalid):
     from TerminalController import TerminalController, ProgressBar
     self.PopulateByJournalID(journalid)
     self.PopulatePartJournals(journalid)
     self.PopulateIllustrations(journalid)
     recordnumber = len(self)
     term = TerminalController()
     bar = ProgressBar(term, str(recordnumber) + " rows in "+str(journalid)+".")

     count = 0
     pccount = 0
     try:
         #***outf = open('/dc/bp/processed_rel4/gen/' + journalid + '.gen', 'w')
         outf = open('/dc/pao/processed_rel1/gen/' + journalid + '.gen', 'w')
         outf.close()
     except:
         print 'Problem opening: ' + journalid+'.gen'
         return
     while len(self) > 0:
         count += 1
         if recordnumber > 99:
             if count % int(0.01 * recordnumber) == 0:
                 pccount += 0.01
                 if pccount > 1:
                     pccount = 1
                 bar.update(pccount, str(count) + " completed.")
         else:
             pccount += float(100) / float(recordnumber*100)
             bar.update(pccount, str(count) + " completed.")
         item = self.pop(0)

         #item.PopulateWellesley()
         item.CoauthorSet = BPRecordSet()
         item.PopulateCoauthor()
         #item.PopulateIllustrations()
         item.CreateEnumeration()
         item.ChangeType()
         item.MapMonth()
         item.TodaysDate()
         item.ChangePageNumber()
         #***outf = codecs.open('/dc/bp/processed_rel4/gen/' + journalid + '.gen', 'a', encoding="utf8")
         outf = codecs.open('/dc/pao/processed_rel1/gen/' + journalid + '.gen', 'a', encoding="utf8")
         outf.write(item.FillTemplate())
         outf.close()
         del item        

 def processSFT(self, journalid, filterlist = None):
     """Process the searchable fulltext for the given journal."""

     from TerminalController import TerminalController, ProgressBar

     #***if not os.path.exists('/dc/bp/processed_rel4/sft/' + journalid):
     if not os.path.exists('/dc/pao/processed_rel1/sft/' + journalid):
         #***os.makedirs('/dc/bp/processed_rel4/sft/' + journalid)
         os.makedirs('/dc/pao/processed_rel1/sft/' + journalid)
     else:
         print "Folder already exists: " + journalid
         print "Skipping for now."
         return


     intyear= 1828
     #intyear= 182
     querycount=1
     thisyear=strftime('%Y', localtime())
     #self.PopulatePartJournals(journalid)
     #while intyear * 10 <= int(thisyear):
     recp=0
     while intyear  <= int(thisyear):
         #stary=intyear * 10
         #endy=stary+9
         #recyear=str(intyear)
         #print "\n\nProcessing issues from ",stary," To ",endy,"\n\n"
         self.PopulateByDecade(journalid,intyear)
         self.PopulatePartJournals(journalid)
         recordnumber = len(self)
         term = TerminalController()
         bar = ProgressBar(term, str(recordnumber) + " rows in "+str(journalid)+".")

         count = 0
         pccount = 0

         while len(self) > 0:
    #         try:
             count += 1
             if recordnumber > 99:
                 if count % int(0.01 * recordnumber) == 0:
                     pccount += 0.01
                     if pccount > 1:
                         pccount = 1
                     bar.update(pccount, str(count) + " completed.")
             else:
                 pccount += float(100) / float(recordnumber*100)
                 bar.update(pccount, str(count) + " completed.")

             item = self.pop(0)
             if filterlist is not None:
                 if item.sourcefilename not in filterlist:
                     del item
                     continue

             item.ChangeType()
             item.MapMonth()
             item.TodaysDate()
             item.PopulateZones()
             item.templateclass = SPsft_template.SPsft_template
             #***outf = codecs.open('/dc/bp/processed_rel4/sft/' + journalid + '/' + item.paoid + '.xml', 'w', encoding="latin-1")
             outf = codecs.open('/dc/pao/processed_rel1/sft/' + journalid + '/' + item.paoid + '.xml', 'w', encoding="latin-1")

             #try:
             outf.write(item.FillTemplate())
             #except UnicodeDecodeError:
             #    print item.paoid
             #    sys.exit()
             outf.close()
             del item
             gc.collect()
    #         except:
    #             print "An error occured"
    #             for part in sys.exc_info():
    #                 print part
    #             print item.paoid, item.sourcefilename
    #             outf = open('errors.log', 'a')
    #             outf.write(item.zones[-1].rawtext)
    #             sys.exit()
         intyear+=1
         querycount+1
         recp+=recordnumber
         print "\n\n Records processed so far = ", recp,"\n\n"
         
 def workflow(self, journalid, filterlist = None):
     """This method batches two processes that need to be run over the journals.
     It updates the page sequence information and then updates the threading
     information. 
     Once the page sequence information has been updated, then it can infer page numbers
     where that information is missing or dubious in the data.
     """
     from TerminalController import TerminalController, ProgressBar
     self.PopulateByJournalID(journalid)
     recordnumber = len(self)
     term = TerminalController()
     bar = ProgressBar(term, str(recordnumber) + " rows in "+str(journalid)+".")

     count = 0
     pccount = 0


     while len(self) > 0:
         count += 1
         if recordnumber > 99:
             if count % int(0.01 * recordnumber) == 0:
                 pccount += 0.01
                 if pccount > 1:
                     pccount = 1
                 bar.update(pccount, str(count) + " completed.")
         else:
             pccount += float(100) / float(recordnumber*100)
             bar.update(pccount, str(count) + " completed.")
         item = self.pop(0)
         if filterlist is not None:
             if item.sourcefilename not in filterlist:
                 del item
                 continue

         item.UpdatePageSequence()
         item.UpdateThreading()
         del item

     print "Repopulating in order and inferring pages."
     self.PopulateByJournalID(journalid)
     self.InferPageNumbers()

 def workflow2(self, journalid, filterlist = None):
     """This method batches together the processes to update illustration information
     and coauthor information. You'd want to run this after the workflow method because
     the illustration information uses page numbers which are improved by the methods called
     from workflow."""
     from TerminalController import TerminalController, ProgressBar
     self.PopulateByJournalID(journalid)
     recordnumber = len(self)
     term = TerminalController()
     bar = ProgressBar(term, str(recordnumber) + " rows in "+str(journalid)+".")

     count = 0
     pccount = 0


     while len(self) > 0:
         count += 1
         if recordnumber > 99:
             if count % int(0.01 * recordnumber) == 0:
                 pccount += 0.01
                 if pccount > 1:
                     pccount = 1
                 bar.update(pccount, str(count) + " completed.")
         else:
             pccount += float(100) / float(recordnumber*100)
             bar.update(pccount, str(count) + " completed.")
         item = self.pop(0)
         if filterlist is not None:
             if item.sourcefilename not in filterlist:
                 del item
                 continue

         item.UpdateIllustrations()
         item.UpdateCoauthors()
         del item        


class BPRecord(BaseRecord):
     def __init__(self, rawtext=None):
         self.rawtext = rawtext
         self.tablename="indexrecord"
         #self.templateclass = BPrecord_template.BPrecord_template
         self.templateclass = SPrecord_template.SPrecord_template
         self.entityconverter = bpEntityConverter()
         self.requiredFields=[   'paoid',
                                 'sourcefilename',
                                 'journalid',
                                 'pmid',
                                 'author',
                                 'title',
                                 'type',
                                 'volume', 
                                 'issue',
                                 'date',
                                 'month',
                                 'nopages',
                                 'startpage',
                                 'endpage',
                                 'todaydate',
                                 'categoryid',
                                 'numericpage',
                                 'numericendpage',
                                 'pagetype',
                                 'enumeration',
                                 'numericvolume',
                                 'numericissue',
                                 'page_sequence_start',
                                 'page_sequence_end',
                                 'startpage_conv',
                                 'endpage_conv']
         self.optionalFields=[   'PartJournalTitleSet',
                                 'PartJournalEditorSet',
                                 'abstract',
                                 'WellesleySet',
                                 'CoauthorSet',
                                 'IllustrationSet',
                                 'ContributorSet',
                                 'CurranSet',
                                 'ThreadSet',
                                 'zones',
                                 'wordcount',
                                 'illustrated',
                                 'blocked',
                                 'excluded']
         self.databaseConnection = databaseConnection
         
         self.regexmap = {
             'PAGE_SEQUENCE': re.compile('<BP_page_sequence>(.*?)</BP_page_sequence>'),
             'PAGE_NUMBER_EXP': re.compile('<BP_zone_pagenumber>(.*?)</BP_zone_pagenumber>'),
             'date': re.compile('<BP_date_8601>(.*?)</BP_date_8601>'),
             'author': re.compile('<BP_author>(.*?)</BP_author>'),
             'title': re.compile('<BP_title>(.*?)</BP_title>'),
             'volume': re.compile('<BP_volume>(.*?)</BP_volume>'),
             'issue': re.compile('<BP_issue>(.*?)</BP_issue>'),
             'type': re.compile('<BP_article.*?type="(.*?)"'),
             'abstract': re.compile('<BP_abstract>(.*?)</BP_abstract>')
 
         }
         
         self.zones = bpZoneSet()
     
     #def PopulateFromRawXml(self):
         #if self.rawtext is None:
             #self.PopulateRawXml()
         #for regex in self.regexmap.keys():
             #if self.regexmap[regex].search(self.rawtext) is not None:
                 #setattr(self, regex, self.regexmap[regex].search(self.rawtext).group(1))
     
     
     
     def PopulateFromRawXml(self):
         adtitleregex= re.compile('<BP_title added="yes">(.*?)</BP_title>')
         if self.rawtext is None:
            self.PopulateRawXml()
         for regex in self.regexmap.keys():
             if regex=='title':
                 #normal title
                 if self.regexmap[regex].search(self.rawtext) is not None:
                     setattr(self, regex, self.regexmap[regex].search(self.rawtext).group(1)) 
                 else:
                     #title added="yes"
                     if adtitleregex.search(self.rawtext) is not None:
                         preadtiltle=adtitleregex.search(self.rawtext).group(1)
                         postadtitle="["+ preadtiltle + "]"
                         setattr(self, regex,postadtitle)    
             #elif regex=='abstract':
                 #if self.regexmap[regex].search(self.rawtext) is not None:
                     #if adtitleregex.search(self.rawtext) is not None:
                         #firsline=adtitleregex.search(self.rawtext).group(1)
                         #otherlines=self.regexmap[regex].search(self.rawtext).group(1)
                     
                         #wholeabstract= firsline + otherlines
                         #print "SUCCES"
                         #print wholeabstract
                         #setattr(self, regex, wholeabstract)
                     #else:
                         #setattr(self, regex, self.regexmap[regex].search(self.rawtext).group(1)) 
             else:      
                 if self.regexmap[regex].search(self.rawtext) is not None:
                     setattr(self, regex, self.regexmap[regex].search(self.rawtext).group(1))

                 
                 
     def GenerateBpid(self, idstub):
         """This method is the formula for creating a conventional paoid from the various attributes
         of the record. You need to pass the 'auto-incrementing' idstub as a parameter. There is a
         separate method GetNewIdstub to create a new one."""
         try:
             volume = self.volume
         except:
             volume = '0'
         try:
             issue = self.issue
         except:
             issue = '0'
         self.paoid = self.journalid + '-' + str(self.date)[:4] + '-' + str(volume)[-3:].zfill(3) + '-' + str(issue)[-2:].zfill(2) + '-' + idstub
 
     def GetNewIdstub(self, counter=None):
         """When inserting a batch of records for the first time, each one will require a new idstub
         which kind of autoincrements as you go. If you keep count as you go then you will have a counter
         that you can pass in as a parameter but where that's none it will count the number of records already assigned
         to a journal-year and start from there."""
         if counter is None:
             counter = self.doSQL("""SELECT count(*) FROM indexrecord WHERE `date` LIKE '%s%%' AND `journalid`='%s';
                         """ % (self.date[:4], self.journalid))
             #print counter
             counter = int(counter[0][0]) + 1
         else:
             counter += 1
 
         """A curious rule: if the type of the record is in the list below, then the id is altered so that
         a B is added to the end. This nonsense means that you need to know the type of the record before you
         can create the stub."""
         if self.type in ['Other', 'Cover', 'Front matter', 'Table of contents', 'Back matter', 'Advertisement']:
             filledcounter = str(counter).zfill(5) + 'B'
         else:
             filledcounter = str(counter).zfill(6)
         return filledcounter, counter
     
     def NormalizeType(self):
         """The data has variants on the different types. The mapping to the normalized form
         is defined as a constant near the top of the module. This just updates it."""
         if NORMALIZEDTYPES.has_key(self.type):
             self.type = NORMALIZEDTYPES[self.type]
         
     def MapTypeTitle(self):
         """If a record doesn't have a title but does have a type, then we can create a decent title
         for it by looking up one appropriate for that type. The mapping is defined as a constant.
         Note that the mapping maps the denormalized type forms rather than the normalized ones.
         So you probably need to call this before NormalizeType."""
         if not hasattr(self, "title"):
             if hasattr(self, "type"):
                 if TYPETITLEMAP.has_key(self.type):
                     self.title = TYPETITLEMAP[self.type]
                 else:
                     self.title = "Unindexed matter"
             else:
                 print "No type for " + self.sourcefilename
                 sys.exit()
     
     def MapMonth(self):
         """This method takes the two digits in the numeric data field and maps them to the name of the
         month in string form. In fact, it doesn't deal only with months but there are also mappings to
         seasons where appropriate.
         The mapping dictionary is defined as a constant at the top of the module.
         """
         try:
             self.month = MONTHMAP[self.date.__str__()[4:6]]
         except KeyError:
             self.month = ''
 
     def TodaysDate(self):
         """This populates the todaydate attribute with a six-digit numeric representation of today's date
         in the format YYMMDD."""
         year, month, day = gmtime()[:3]
         self.todaydate = str(year)[-2:] + str(month).zfill(2) + str(day).zfill(2)
     
     def CreateEnumeration(self):
         """This creates the enumeration string which contains volume and issue information. The desired
         format is something like (vol:iss) but either of volume and issue could be missing."""
         self.numericvolume = 0
         self.numericissue = 0
         self.enumeration = ""
         
         if self.volume is not None:
             self.enumeration += str(self.volume)
             try:
                 self.numericvolume = int(self.volume)
             except:
                 self.numericvolume = 0
             if self.issue is not None:
                 self.enumeration += ":"
             
         if self.issue is not None:
             self.enumeration += str(self.issue)
             try:
                 self.numericissue = int(self.issue)
             except ValueError:
                 self.numericissue = 0
     
     def ChangeType(self):
         """This is a special rule to handle the types of articles which are Fiction or Drama.
         The categorizer indicates articles which it thinks are fiction but it is frequently out on short
         articles so we ignore them here by checking whether the wordcount exceeds 500."""
         if self.type == 'Article':
             if int(self.categoryid) == 1 and int(self.wordcount) > 500:
                 self.type = 'Fiction'
         elif self.type == 'Drama':
             if int(self.categoryid) != 2:
                 self.type = 'Article'
     
     def ChangePageNumber(self):
         """This checks whether the page number is a valid arabic or roman numeral. It should be
         unnecessary to use this if one has run the infer pages method of the record set first."""
         
         startpage = self.startpage_conv.replace('[', '').replace(']', '')
         try:
             self.numericpage = int(startpage)
             self.pagetype = '1'
             self.numericendpage = self.numericpage + int(self.nopages) - 1
             return
         except ValueError:
             pass
         
         try:
             self.numericpage = roman.fromRoman(startpage)
             self.pagetype = '0'
             self.numericendpage = self.numericpage + int(self.nopages) - 1
             return
         except roman.InvalidRomanNumeralError:
             pass
         
         self.numericpage = 0
         self.numericendpage = 0
         self.startpage = "[n. pag.]"
         self.pagetype = '1'
             
     
     def PopulatePartJournals(self):
         """A partjournal defines a few fields such as title, editor that might be true for
         a portion of a journal run. Note that it's not just title and editor but there are 
         other field as well."""
         self.PartJournalTitleSet = BPRecordSet()
         self.PartJournalTitleSet.tablename = 'ptjournaltitle'
         self.PartJournalTitleSet.recordclass = BaseRecord
         self.PartJournalTitleSet.getdbfields()
         self.PartJournalTitleSet.freesearch("""
             SELECT * FROM ptjournaltitle 
             WHERE `journalid` = '%s'
             AND `startdate` <= '%s'
             AND enddate >= '%s';""" % (self.journalid, self.date, self.date))
         
         if len(self.PartJournalTitleSet) == 0:
             self.PartJournalTitleSet.tablename = 'journaltitle'
             self.PartJournalTitleSet.getdbfields()
             self.PartJournalTitleSet.freesearch("""
                 SELECT * FROM journaltitle 
                 WHERE `journalid` = '%s'""" % self.journalid)
         
         self.PartJournalEditorSet = BPRecordSet()
         self.PartJournalEditorSet.tablename = 'ptjournaleditor'
         self.PartJournalEditorSet.recordclass = BaseRecord
         self.PartJournalEditorSet.getdbfields()
         self.PartJournalEditorSet.freesearch("""
             SELECT * FROM ptjournaleditor 
             WHERE `journalid` = '%s'
             AND `startdate` <= '%s'
             AND enddate >= '%s';""" % (self.journalid, self.date, self.date))
             
     
         
     def PopulateCoauthor(self):
         """Some bp records have coauthors. This is fairly straightforward at the moment.
         Go fish them out from the coauthor table, keyed by paoid."""
         self.CoauthorSet = BPRecordSet()
         self.CoauthorSet.tablename = 'coauthor'
         self.CoauthorSet.recordclass = BaseRecord
         self.CoauthorSet.getdbfields()
         self.CoauthorSet.populatefromdb(paoid=self.paoid)
         
     def PopulateIllustrations(self):
         """This method fetches back illustrations in the database that have been related to the
         record in question.
         
         Note the mapping ILLUSTYPES defined as a constant at the start of the module. It's not so
         much defined as read out of a table in the database.
         
         noillustrations refers to the number of a type of illustration on a particular page.
         """
         self.IllustrationSet = BPRecordSet()
         self.IllustrationSet.tablename = 'illustration'
         self.IllustrationSet.recordclass = BaseRecord
         self.IllustrationSet.getdbfields()
         self.IllustrationSet.populatefromdb(paoid=self.paoid)
         self.IllustrationSet.noillustrations = {}
         for illustration in self.IllustrationSet:
             illustration.illusname = ILLUSTYPES[illustration.illuscode]
             if self.IllustrationSet.noillustrations.has_key(illustration.pagecount.__str__()):
                 self.IllustrationSet.noillustrations[illustration.pagecount.__str__()] += 1
             else:
                 self.IllustrationSet.noillustrations[illustration.pagecount.__str__()] = 1
  
     def PopulateRawXml(self):
         """Read in the source datafile for the record.
         FULLTEXTPATH is defined as a constant.
         Note that there's some fancy regex here to correct an infelicity in the data.
         """
         import os
         inf = codecs.open(os.path.join(FULLTEXTPATH, self.sourcefilename), 'r')
         self.rawtext = inf.read()
         inf.close()
         fixpgnolinebreaks = re.compile('(<BP_zone_pagenumber>[^<\n]*)\n+(\|.*<\/BP_zone_pagenumber>)')
         self.rawtext = fixpgnolinebreaks.sub('\\1\\2', self.rawtext)
         
     def PopulateThreading(self):
         """Go get the threading information as stored in the database.
         Threading is basically the association between a record and a sequence of page images."""
         self.ThreadSet = BPRecordSet()
         self.ThreadSet.tablename = 'threading'
         self.ThreadSet.recordclass = BaseRecord
         self.ThreadSet.getdbfields()
         self.ThreadSet.indexsearch(paoid=self.paoid, orderby='sequence')
     
     def UpdateThreading(self):
         """Update or populate the threading information in the database on the basis of the raw XML file.
         """
         if self.rawtext is None:
             self.PopulateRawXml()
         sequencecounter = 0
         self.doSQL("""DELETE FROM threading WHERE `paoid`='%s';""" % self.paoid)
         
         """We use a regular expression, defined as a constant to pull out a sequence of all page images
         from the source file."""
         pageimages = PAGE_IMAGE_EXP.findall(self.rawtext)
         """But we then need to remove duplicates from that list."""
         for pageimage in pageimages:
             while pageimages.count(pageimage) > 1:
                 pageimages.remove(pageimage)
         
         for pageimage in pageimages:
             sequencecounter += 1
             #print self.paoid, self.journalid + '/' + pageimage, sequencecounter
             self.doSQL("""INSERT INTO threading
                           SET `paoid`='%s', `imageid`='%s', `sequence`='%s'
                           """ % (self.paoid, self.journalid + '/' + pageimage, sequencecounter))
          
     def UpdateCoauthors(self):
         """This pulls out the so-called coauthors from the raw XML data.
         In practice, a co-author is defined as all authors after the first one. So the process is actually
         to pull out all the authors. The first author in the list gets into the indexrecord table
         and the rest are inserted into the coauthor table."""
         if self.rawtext is None:
             self.PopulateRawXml()
         authors = self.regexmap['author'].findall(self.rawtext)
         if len(authors) > 1:
 
             self.doSQL("""DELETE FROM coauthor WHERE `paoid`='%s';""" % self.paoid)
             for coauthor in authors[1:]:
                 self.doSQL("""INSERT INTO coauthor
                               SET `paoid`='%s', `coauthor`='%s'
                               """ % (self.paoid, coauthor))
 
     def UpdateIllustrations(self):
         """This method updates the illustration information in the database on the basis of what's in the
         raw XML file. Illustrations are quite complicated as objects so the process here is to pull out all
         the illustrations with a regular expression. Then for each one we create a bpIllustration object
         where we pass whatever we pulled out with the regex as the rawtext parameter.
         """
         illustrations = []
         if self.rawtext is None:
             self.PopulateRawXml()
     
         for illus in ILLUSTRATION_EXP.finditer(self.rawtext):
             illustrations.append( bpIllustration(rawtext=illus.group()) )
             #outf = open('/home/richardm/illus.log', 'a')
             #outf.write(illustrations[-1].rawtext)
             #outf.close()
             test = illustrations[-1].process(self)
             if test == -1:
                 illustrations.pop()
             
         if len(illustrations) > 0:
             self.doSQL("""DELETE FROM illustration WHERE `paoid`='%s';""" % self.paoid)
         
             for illus in illustrations:
                 self.doSQL("""INSERT INTO illustration
                                   SET `paoid`='%s', `illuscode`='%s', `pageno`='%s', `pagecount`='%s';
                                   """ % (self.paoid, illus.illuscode, illus.pageno, illus.pagecount))
 
     def UpdatePageSequence(self):
         """This method updates the pagination information from a record on the basis of whatever is
         in the raw XML file.
         The pagination in the raw XML is not stored as bibliographic information at the top of the file.
         Rather, there is a series of pages. So the process is to pull out all the pages and then take the
         first and last in the list to get the appropriate information.
         
         There are two sorts of pagination at work here. The PAGE_NUMBER corresponds, roughly, to whatever
         was on the printed page and therefore could be any old nonsense (e.g. roman numerals, combinations of
         letters and numbers). The PAGE_SEQUENCE is an integer (or something you can effectively turn into an
         integer) and actually shows the ordering of the pages. Because these are integers it also means you can
         subtract the small one from the big one to get the number of pages.
         
         Various attempts have been made to improve the page numbering situation, the sad legacy of one of which
         can be found below. Page numbers can come in the format xxx|yyy where, as far I can work out, if there's
         something worthwhile on the right-hand side of the pipe you should use it instead.
         """
         if self.rawtext is None:
             self.PopulateRawXml()
         pagenumbers = self.regexmap['PAGE_NUMBER_EXP'].findall(self.rawtext)
         pagesequences = self.regexmap['PAGE_SEQUENCE'].findall(self.rawtext)
         if len(pagesequences) and len(pagenumbers) > 0:
             self.startpage = pagenumbers[0]
             self.endpage = pagenumbers[-1]
             self.page_sequence_start = pagesequences[0]
             self.page_sequence_end = pagesequences[-1]
             # nopages = number of pages.
             self.nopages = int(self.page_sequence_end) - int(self.page_sequence_start) + 1
             
             if self.startpage.find('|') > -1:
                 pipeleft, piperight = self.startpage.split('|')
                 if len(piperight) > 0:
                     self.startpage = piperight
                 else:
                     self.startpage = pipeleft
 
             if self.endpage.find('|') > -1:
                 pipeleft, piperight = self.endpage.split('|')
                 if len(piperight) > 0:
                     self.endpage = piperight
                 else:
                     self.endpage = pipeleft
                     
             
             self.updateDB("sourcefilename", **{
                             'sourcefilename': self.sourcefilename,
                             'startpage': self.startpage,
                             'endpage': self.endpage,
                             'page_sequence_start': self.page_sequence_start,
                             'page_sequence_end': self.page_sequence_end,
                             'nopages': self.nopages
                             }
             )
         else:
             print self.sourcefilename
             print pagesequences
             print pagenumbers
 
     def PopulateZones(self):
         """In the raw XML the fulltext data for an article is split into Zones which can be
         roughly defined as rectangles of text or, at any rate, content.
         Zones are quite complicated so the process here is to pull out all the zones with a regex
         and then create a series of bpZone objects.
         """
         if self.rawtext is None:
             self.PopulateRawXml()
     
         for zone in ZONE_EXP.finditer(self.rawtext):
             self.zones.append( bpZone(rawtext=zone.group()) )
             self.zones[-1].process() 
 

class bpZoneSet(list):

    def entityconvert(self):
        for zone in self:
            for word in zone.words:
                #print word.text
                latin1text = word.text.decode('latin1')
                word.text = latin1text.encode('ascii', 'xmlcharrefreplace')
                
                #print word.text
        
 
class bpZone:
 
     """This class corresponds to a zone in the BP fulltext data. A BP article with any fulltext
     is made up of a series of zones. A zone is basically a rectangle that someone has drawn round
     a portion of the text. It doesn't necessarily correspond to a full page. But it never
     straddles multiple pages.
     
     In the raw data, the zone coordinates indicate where the zone is on the page. One of the things
     that zones contain is a list of individual words.
     """
     
     def __init__(self, rawtext=None):
         self.rawtext=rawtext
         self.words = []
         
         # This regex is going to be used to pull out the coordinates for a zone.
         # Note the (?P ... ) notation which allows up to access the groups by
         # name later on.
         self.COORD_EXP=re.compile(""" <BP_zone_coord>
                                             <BP_ULX>(?P<ulx>.*?)</BP_ULX>
                                             <BP_ULY>(?P<uly>.*?)</BP_ULY>
                                             <BP_LRX>(?P<lrx>.*?)</BP_LRX>
                                             <BP_LRY>(?P<lry>.*?)</BP_LRY>
                                         </BP_zone_coord>""", re.VERBOSE)
         
         self.regexmap = {
             'ZONE_TYPE':    re.compile("<BP_zone.*?type=\"(.*?)\""),
             'ZONE_DESCRIP': re.compile("<BP_zone.*?descrip=\"(.*?)\""),
             'ZONE_NUMBER':  re.compile("<BP_zone.*?zone_number=\"(.*?)\""),
             'ZONE_IMAGE':   re.compile("<BP_zone_image>(.*?)</BP_zone_image>"),
             'PAGE_IMAGE':   re.compile("<BP_page_image>(.*?)</BP_page_image>"),
             'ZONE_PAGENUMBER':      re.compile("<BP_zone_pagenumber>(.*?)</BP_zone_pagenumber>"),
             'ZONE_PAGESEQUENCE':    re.compile("<BP_page_sequence>(.*?)</BP_page_sequence>")
         }
         
     def process(self):
         """Process the coordinates."""
         coords = self.COORD_EXP.search(self.rawtext)
         self.ulx = int(coords.group('ulx'))
         self.uly = int(coords.group('uly'))
         self.lrx = int(coords.group('lrx'))
         self.lry = int(coords.group('lry'))
 
         for regex in self.regexmap:
             if self.regexmap[regex].search(self.rawtext) is not None:
                 setattr(self, regex, self.regexmap[regex].search(self.rawtext).group(1))
                 # print regex, self.regexmap[regex].search(self.rawtext).group(1)
             else:
                 outf = open('errors.log', 'a')
                 outf.write('No match for ' + regex)
                 outf.close()
         
         for word in WORD_EXP.finditer(self.rawtext):
             self.words.append(bpWord(rawtext=word.group(), zone=self))
             self.words[-1].process()
             self.dezoned = self.words[-1].dezoneCoords()
 
class bpIllustration(bpZone):
     
     """A bp illustration is a special sort of zone. It doesn't contain any text but 
     instead there is a need to pull out information which is specific to the illustration.
     
     Note that the pipe-delimted page number logic is repeated here which should be done better."""
     
     def process(self, parent):
         for regex in self.regexmap:
             if self.regexmap[regex].search(self.rawtext) is not None:
                 setattr(self, regex, self.regexmap[regex].search(self.rawtext).group(1))
 
         if self.ZONE_DESCRIP == 'text':
             self.ZONE_DESCRIP = 'illustrative text'
         
         if not ILLUSCODES.has_key(self.ZONE_DESCRIP):
             return -1
         self.illuscode = ILLUSCODES[self.ZONE_DESCRIP]
 
         self.pageno = str(self.ZONE_PAGESEQUENCE)
 
         if self.pageno.find('|') > -1:
             pipeleft, piperight = self.pageno.split('|')
             if len(piperight) > 0:
                 self.pageno = piperight
             else:
                 self.pageno = pipeleft
 
         self.pagecount =   str(
                                 int(str(self.pageno))
                                 - int(parent.page_sequence_start) + 1
                                 )
     
class bpWord:
        
     """ <BP_word>
             <BP_text>BRITISH</BP_text>
             <BP_wc ulx="83" uly="388" lrx="652" lry="480" />
         </BP_word>
     """
     
     def __init__(self, rawtext=None, zone=None):
         self.rawtext = rawtext
         self.coords = []
         self.zone = zone
         
         self.TEXT_EXP = re.compile('<BP_text>(.*?)</BP_text>')
         self.COORD_EXP = re.compile('<BP_wc ulx="(?P<ulx>.*?)" uly="(?P<uly>.*?)" lrx="(?P<lrx>.*?)" lry="(?P<lry>.*?)" />')
         
     def process(self):
         self.text = self.TEXT_EXP.search(self.rawtext).group(1)
         for coordset in self.COORD_EXP.finditer(self.rawtext):
             self.coords.append(
             [
             coordset.group('ulx'),
             coordset.group('uly'),
             coordset.group('lrx'),
             coordset.group('lry')
             ]
             )
 
     def dezoneCoords(self):
         """This method returns a string for the word coordinates. 
         We calculate absolute coordinates for the word by adding the relative woord coordinates
         to the zone coordinates.
         Where there are two sets of coordinates (say because a word is hyphenated across two lines,
         then those two coordinates are separated by -.
         Then the actual coordinates or coordinate groups are returned separated by commas.
         
         e.g.
         x1,y1,x2,y2
         x1a-x1b,y1a-y1b,x2a-x2b,y2a-y2b
         """
         x1set = "-".join([str(self.zone.ulx + int(coordset[0])) for coordset in self.coords])
         y1set = "-".join([str(self.zone.uly + int(coordset[1])) for coordset in self.coords])
         x2set = "-".join([str(self.zone.ulx + int(coordset[2])) for coordset in self.coords])
         y2set = "-".join([str(self.zone.uly + int(coordset[3])) for coordset in self.coords])
         
         return ",".join([x1set, y1set, x2set, y2set])
 
class bpFeed:
 
     """The bpFeed is a class which corresponds to a new set of BP journal data which need to be
     inserted into the database for the first time. 
     """
     
     def __init__(self, pmid):
         self.foldername = pmid
         self.counter=None
         self.previous=None
     
     def GetCurrentRecords(self):
         db = databaseConnection()
         cu = db.cursor()
         cu.execute("""SELECT sourcefilename FROM indexrecord WHERE `journalid`='%s';""" % self.journalid)
         self.donefiles = [row[0] for row in cu.fetchall()]
         cu.close()
         db.close()
         
     
     def GenerateRecords(self):
         """This is the key method of the bpFeed."""
         from TerminalController import TerminalController, ProgressBar
         filenames = os.listdir(os.path.join(FULLTEXTPATH, self.foldername))
         
         """This could be an extension to an existing journal so the first step is to split files
         in a folder into those that are new and those that are already in the database."""
         self.journalid = PMID_JOURNAL[self.foldername]
         self.GetCurrentRecords()
         
         self.recordSet=BPRecordSet()
         self.recordSet.tablename="indexrecord"
         self.recordSet.getdbfields()
 
         sourcefilenames = [os.path.join(self.foldername, filename) for filename in filenames]
         actualfilenames = set(sourcefilenames).difference(set(self.donefiles))
         # actualfilenames.sort()
         # print sourcefilenames, actualfilenames, self.donefiles
         print str(len(self.donefiles)) + " done already. "
         print str(len(actualfilenames)) + " to process. "
         print str(len(filenames)) + " in total. "
         recordnumber = len(actualfilenames)
         term = TerminalController()
         bar = ProgressBar(term, str(recordnumber) + " files in "+self.foldername+".")
         count = 0
         pccount = 0
 
         for sourcefilename in actualfilenames:
             count += 1
             if recordnumber > 99:
                 if count % int(0.01 * recordnumber) == 0:
                     pccount += 0.01
                     if pccount > 1:
                         pccount = 1
                     bar.update(pccount, str(count) + " completed.")
             else:
                 pccount += float(100) / float(recordnumber*100)
                 bar.update(pccount, str(count) + " completed.")
 
             #print filename
             inf = codecs.open(os.path.join(FULLTEXTPATH, sourcefilename), 'r', encoding='latin-1')
             #data = inf.read().decode('latin-1')
             data = inf.read()
             self.recordSet.append(BPRecord(rawtext=data))
             self.FeedWorkflow(self.recordSet[-1], sourcefilename)
             inf.close()
             self.previous=self.recordSet[-1]
             del self.recordSet[-1]
             
             
     def FeedWorkflow(self, record, sourcefilename):
         """This method pulls together the methods that need to be run on a new BPRecord as it
         goes into the database.
         It could just as well sit as a method in the BPRecord class.
         """
         record.sourcefilename = os.path.join(sourcefilename)
         record.PopulateFromRawXml()
         record.MapTypeTitle()
         record.NormalizeType()
         record.journalid = PMID_JOURNAL[self.foldername]
         
         if self.previous is not None:
             if self.previous.date[:4] != record.date[:4]:
                 counter = None
             
         newidstub, self.counter = record.GetNewIdstub(counter=self.counter)
         
         record.GenerateBpid(idstub = newidstub)
         
         #print record.xml()
         record.InsertIntoDB_new(fieldnames = self.recordSet.fieldnames)
             
     def FixAbstracts(self):
         """Circa Nov 2007 processes were altered and abstracts ceased to be picked up.
         This method finds any abstracts belonging to records in the feed and replaces
         them into the database
         """
         
         filenames = os.listdir(os.path.join(FULLTEXTPATH, self.foldername))
             
         self.recordSet=BPRecordSet()
         self.recordSet.tablename="indexrecord"
         self.recordSet.getdbfields()
 
         sourcefilenames = [os.path.join(self.foldername, filename) for filename in filenames]
 
         db = databaseConnection()
         cu = db.cursor()
         
         abstractre = re.compile('<BP_abstract>(.*?)</BP_abstract>', re.S)
         anytagre = re.compile('<.*?>')
 
         for sourcefilename in sourcefilenames:
 
             inf = codecs.open(os.path.join(FULLTEXTPATH, sourcefilename), 'r', encoding='latin-1')
             data = inf.read()
             #self.recordSet.append(BPRecord(rawtext=data))
             adtitleregex= re.compile('<BP_title added="yes">(.*?)</BP_title>')
             
             #self.FeedWorkflow(self.recordSet[-1], sourcefilename)
             if abstractre.search(data) is not None:
                 abstract = abstractre.search(data).group(1)
                 abstract = anytagre.sub('', abstract).strip()
                 if adtitleregex.search(data) is not None:
                    preadtiltle=adtitleregex.search(data).group(1)
                    wholeabstract=preadtiltle + abstract
                    cu.execute("""UPDATE indexrecord SET `abstract` ='%s' WHERE `sourcefilename`='%s';""" % (wholeabstract, sourcefilename))
                 else:
                     cu.execute("""UPDATE indexrecord SET `abstract` ='%s' WHERE `sourcefilename`='%s';"""
                             % (abstract, sourcefilename))
            
 
             inf.close()
 
         cu.close()
         db.close()
