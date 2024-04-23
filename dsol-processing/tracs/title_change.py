import sys

#use/package/dsol/lib/python/citations')
sys.path.append('/home/amedafe/SVN/dsol/lib/python')
import re
import glob
import codecs
import MySQLdb
import xlrd
import csv
#from citations.base.baseRecord import* 
#from citations.base import dbconnector
from datetime import datetime

"""
Gather title change history information for TRACS.

populate_titles: gather info for every unique issue from article data, populate title_and_date_sets
compare: use title_and_date sets to create table of all journal runs with start and end dates (title_change)
add_spreadsheet_fields
writehistoryspreadsheet

##makemap: adds previous titles from pub-level data to the title_change table

NB Need to add to or alter record_directories list for new directories? Handle this better?

"""


def dbconnect():
    dbargs = {'user': 'tempio',
                'db': 'tempio',
                'host': 'dsol',
                'passwd': 'tempio'
                }

    dbconn = MySQLdb.connect(**dbargs)
    return dbconn

def populate_titles():
    #databaseConnection = dbconnector.dbconnector(host="localhost", user="tempio", passwd="tempio", db="tempio").MakeConnection    
    db = dbconnect()
    cu = db.cursor() 
    cu.execute("""truncate title_and_date_sets;""")
    #record_directories=['1#0','1#1','1#3','1#4','1#5','1#6','1#7','1#8','1#9','2#1','2#2','2#3','2#4','2#5','2#6','2#7',
    #                    '2#8','2#10','2#11','2#13','2#14','2#16','2#17','2#18','2#19','2#20','2#21','2#22','2#23','2#24',
    #                    '2#25','2#26','2#27','2#28','2#29','2#30','2#31','2#32','2#33','2#34','2#35','2#36','2#37','2#38',
    #                    '2#39','2#40', '2#41','Coll1','Coll2','Coll3','Coll4','Coll5']
    #record_directories = ['Coll5']
    err=open('error.log','w')                    
    

    record_directories = ['02_13-04']
    for directory in record_directories:
        
        directory_files=[]
        gen_files=glob.glob('/handover/piopao/'+directory+'/*.gen')
        top_files=glob.glob('/handover/piopao/'+directory+'/*.top')
        directory_files.extend(gen_files)
        directory_files.extend(top_files)

        for record_file in directory_files:
            
            titledates = TitleAndDateSet(record_file)
            with open(record_file,'rU') as op_file:
            #read_file=op_file.read().decode('cp1252')
                currentrec = ''
                for line in op_file:
                    if line[:3] == '001':
                        if currentrec.strip() != '':
                            titledates.checkrecord(currentrec)
                            currentrec = line
                    else:
                        currentrec += line
                for titledate, data in titledates.items():
                    
                    cu.execute("""INSERT INTO title_and_date_sets (journal_id, journal_title, issn, date, display_date, file) 
                            VALUES (%s, %s, %s, %s, %s, %s)""", (data[0], titledate[0].replace('"', '\"'), data[2], titledate[1], data[1], record_file)) 
    cu.close()
    db.close()

class TitleAndDateSet(dict):

    def __init__(self, record_file):
        self.journalidre = re.compile('\n035\s+\$a(.*?)-')
        self.titlere = re.compile('\n773.*?\$t(.*?)(\$|$)')
        self.issnre = re.compile('\n022\s+(.*?)\n')
        self.displaydatere = re.compile('\n773.*\$g.*\((.*?)\)')
        self.datere = re.compile('\n947.*?\$a\d(\d{8})')
        self.record_file = record_file
    
    def checkrecord(self, recordstring):
        try:
            jid = self.journalidre.search(recordstring, re.M).group(1)
        except:
            print 'journal id not found from:\n', self.record_file,'\n',recordstring
            jid = 'xxxx'
        try:
            jtitle = self.titlere.search(recordstring, re.M).group(1)
        except:
            print 'title not found from:\n', self.record_file,'\n',recordstring
            jtitle = ''
        try:
            issn = self.issnre.search(recordstring, re.M).group(1).strip()
            issn = issn.replace('$a', '')
            if len(issn) > 9:
                print 'dubious issn found in', self.record_file, ':', issn
        except:
            #print 'issn not found from:\n', self.record_file,'\n',recordstring
            issn = ''
        try:
            displaydate = self.displaydatere.search(recordstring, re.M).group(1)
        except:
            print 'display date not found from:\n', self.record_file,'\n',recordstring
            displaydate = ''
        try:
            date = format_date(self.datere.search(recordstring, re.M).group(1))
        except:
            print 'date not found from:\n', self.record_file,'\n',recordstring
            date = '11110101'
        #print " ".join([jid, jtitle, date])
        # note that the last combination of a particular title and date in a file is the one that
        # will be registered in the database
        # displaydate and issn are not used to identify a unique new entry
        self[(jtitle, date)] = (jid, displaydate, issn)



def format_date(raw_date):
    monthmap = {
                '00': '01',
                '21': '04',
                '22': '07',
                '23': '10',
                '24': '12'
                }
    if raw_date[4:6] in monthmap:
        raw_date = ''.join([raw_date[:4], monthmap[raw_date[4:6]], raw_date[6:]])
    if raw_date[6:] == '00':
        raw_date = ''.join([raw_date[:6], '01'])

    return raw_date    
    
def compare():
    #databaseConnection = dbconnector.dbconnector(host="localhost", user="tempio", passwd="tempio", db="tempio").MakeConnection    
    db = dbconnect()
    cu = db.cursor() 
    
    cu.execute("""TRUNCATE title_change""")
    cu.execute("""SELECT DISTINCT journal_id FROM title_and_date_sets;""")
    all_journal_id =cu.fetchall()
    
    for row in all_journal_id:
        #cu.execute("""SELECT rec_ID,rec_JOURNALTITLE ,rec_DATE ,FILE FROM publication_records WHERE `rec_JOURNALID`= `%s` ORDER BY `rec_DATE`  ASC ; """)%(row[0])
        cu.execute("""SELECT journal_id, journal_title, issn, date, display_date, file FROM title_and_date_sets WHERE journal_id = %s ORDER BY date ASC ; """, (row[0]))
        title_dates = cu.fetchall()
        try:
            currenttitle = title_dates[0][1]
        except:
            print row[0]
        lastdateseen = ['', '']
        titlestartend = [[title_dates[0][1], title_dates[0][2], title_dates[0][3], '', title_dates[0][4], '']]
        
        for title_date in title_dates:
            if title_date[1] != currenttitle:
                titlestartend[-1][3] = lastdateseen[0]
                titlestartend[-1][5] = lastdateseen[1]
                titlestartend.append([title_date[1], title_date[2], title_date[3], '', title_date[4], '']) 
                currenttitle = title_date[1]
            lastdateseen = [title_date[3], title_date[4]]
            
        for title_run in titlestartend:
            cu.execute("""INSERT INTO title_change (JID, JTITLE, ISSN, START_Date, END_Date, START_Date_displayable, END_Date_displayable)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)""", (row[0], title_run[0], title_run[1], title_run[2], title_run[3], title_run[4], title_run[5]))
    cu.close()
    db.close()
    
    
   
def makemap(pubfile="CHEDDAR.XML"):

    jtitlere = re.compile('<element name="journaltitle">(.*?)</element>')
    jidre = re.compile('<element name="journalid">(.*?)</element>')
    prevtitlere = re.compile('<element name="previousjournaltitle">(.*?)</element>')
    
    databaseConnection = dbconnector.dbconnector(host="localhost", user="tempio", passwd="tempio", db="tempio").MakeConnection    
    db = databaseConnection()
    cu = db.cursor() 
        
    #with codecs.open("pio_enddates.txt", "w", "utf-8") as outfile:
    with open(pubfile, "rU") as pubdata: 
        recs = pubdata.read().split('</document>')
        for rec in recs:
            if rec.strip() == "":
                continue
            rec = rec.decode("cp1252")
            prevtitles = prevtitlere.findall(rec)
            if prevtitles != []:
                jid = jidre.search(rec).group(1)
                jtitle = jtitlere.search(rec).group(1)
                prevtitles.append(jtitle)
               
                cu.execute("""SELECT JTITLE, START_Date, END_Date, START_Date_displayable, END_Date_displayable, shortid FROM title_change WHERE JID = %s""", (jid))
                dbdata = cu.fetchall()
                    
                for mapping in map(maptitles, prevtitles, dbdata):
                    #mapstring = u"\t".join([jid, mapping[0], mapping[1][0], mapping[1][1], mapping[1][2], mapping[1][3], mapping[1][4]])
                    #outfile.write(mapstring + "\n")
                        
                    cu.execute("""UPDATE title_change SET pubdata_version = %s WHERE shortid= %s""", (mapping[0].encode("latin-1", "xmlcharrefreplace"), mapping[1][5]))
                                   
def add_spreadsheet_fields(spreadsheet):
    
    #set up db connection
    #databaseConnection = dbconnector.dbconnector(host="localhost", user="tempio", passwd="tempio", db="tempio").MakeConnection    
    db = dbconnect()
    cu = db.cursor() 
    
    #open spreadsheet
    book = xlrd.open_workbook(spreadsheet)
    
    #locate worksheet, testing for "pio_new" at start
    sheetnames = book.sheet_names()
    newrecordssheetname = None
    for sheetname in sheetnames:
        if sheetname[:7].lower() == "pio_new":
            if not newrecordssheetname:
                newrecordssheetname = sheetname
            else:
                print "".join(["Too many worksheets named \"pio_new...\" in ", spreadsheet, "; using first: ", newrecordssheetname])
    newrecordssheet = book.sheet_by_name(newrecordssheetname)
    
    #get top row
    toprow = newrecordssheet.row_values(0)
    
    #cycle through cells in top row looking for "issn" and "journal id"; record column indexes
    columnindexes = {
                        'city': '',
                        'original id': ''
                        }
    for value in toprow:
        for fieldname in columnindexes.keys():
            if fieldname == value.lower():
                columnindexes[fieldname] = toprow.index(value)
    for fieldname, columnindex in columnindexes.items():
        if columnindex == '':
            print "".join(["No column heading ", fieldname, " found in first row of ", spreadsheet, ", worksheet: ", newrecordssheetname,
                                                                                                                "\nGiving up."])
            sys.exit()    
    
    #for each row get journalid and issn and update mysql database
    #journalidtestre = re.compile('PIO(....)', re.I)
    
    for rownumber in xrange(1, newrecordssheet.nrows):
        rowvalues = newrecordssheet.row_values(rownumber)
        #for x in rowvalues:
        #    print x
        city = rowvalues[columnindexes['city']]
        #print city
        journalidfromspreadsheet = rowvalues[columnindexes['original id']]
#        if journalidtestre.match(journalidfromspreadsheet) != None:
#        journalid = journalidtestre.match(journalidfromspreadsheet).group(1)
        journalid = journalidfromspreadsheet
        cu.execute("""UPDATE title_change SET city = %s WHERE JID= %s""", (city, journalid))
#        else:
#            print "".join(["Ignoring row ", unicode(rownumber), " in ", spreadsheet, ",worksheet: ", newrecordssheetname,
#                                                    " because journal id given is: ", journalidfromspreadsheet])
    
def writehistoryspreadsheet():
    date = datetime.now().strftime("%y%m%d")

    dialect=csv.excel

    prevtitlefile = open(''.join(['paoprevtitles_update', date,'.txt']), 'w')
    prevtitlewriter = csv.writer(prevtitlefile, dialect)
    prevtitlewriter.writerow([
                            'Journal ID',
                            'Title',
                            'ISSN',
                            'Qualifier',
                            'Start Date',
                            'End Date',
                            'Start Date - Displayable',
                            'End Date - Displayable',
                            ])
    
    dbconn = dbconnect()
    cu = dbconn.cursor()
    cu.execute("""SELECT * FROM title_change;""")
    
    for row in cu.fetchall():
        print type(row[6]), str(len(row[6]))
        if row[6] != '':
            prevtitlewriter.writerow([value for value in row[1:]])
    
    prevtitlefile.close()





def maptitles(pubversion, articleversion):
     #mappedtitles = []
     #for ttl in titleversions:
     #    if ttl == None:
     #        ttl = ''
     #    mappedtitles.append(ttl)
     if pubversion == None:
         pubversion = ''
     if articleversion == None:
         articleversion = ['', '', '', '', '', '']
     return (pubversion, articleversion)

def getjidstocorrect():

    #databaseConnection = dbconnector.dbconnector(host="localhost", user="tempio", passwd="tempio", db="tempio").MakeConnection    
    db = dbconnect()
    cu = db.cursor() 
    cu.execute("""SELECT DISTINCT JID FROM title_change WHERE pubdata_version = ''""")
    with open("jidstocorrect_toomanypublevel.txt", 'w') as outf:
        for row in cu.fetchall():
            outf.write("%s\n" % row[0])
            
def preparecorrectionstable():

    #databaseConnection = dbconnector.dbconnector(host="localhost", user="tempio", passwd="tempio", db="tempio").MakeConnection    
    db = dbconnect()
    cu = db.cursor() 
    cu.execute("""truncate title_change_corrections;""")

    with open("jidstocorrect3.txt", "r") as inf:
        for line in inf:
            jid = line.strip()
            if jid != "":
                cu.execute("""INSERT INTO title_change_corrections SELECT * FROM title_change WHERE JID = %s""", jid)
                
    cu.close()
    db.close()
