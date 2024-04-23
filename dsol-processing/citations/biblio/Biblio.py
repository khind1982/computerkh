"""Store in and retrieve bibliographic information from MySQL DB

    Sources are command line inputs and MARC records
    >>> from Biblio import*
    >>> a=Book()
    >>> a.Marcrecord("file to import")
    
                Or
    >>> from Biblio import* 
    >>> a=Bibjournal() 
    >>> a.Marcrecord("file to import")

    
    
    
    
    
    
    """
import MySQLdb
import re
import pprint
import string
from citations.base.baseRecord import* 
from citations.base import dbconnector 
from time import localtime, strftime
from citations.Biblio.templates import wholebook
from citations.Biblio.templates import wholejrnl
import codecs
#import Cheetah.Filters
import warnings

DIGIT_EXP = re.compile('[0-9]+')


TRANSLATIONLOOKUP = {}
inf = codecs.open('/dc/misc/python/citations/iimpiipa/totranslate.lup', 'r', encoding="utf8")
for line in inf:
    if len(line.split('|')) > 1:
        TRANSLATIONLOOKUP[line.split('|')[0]] = line.split('|')[1]
inf.close()



def translatecoverage(foreigncoverage):
    
    foreigncoverage=unicode(foreigncoverage)
    for foreign, english in TRANSLATIONLOOKUP.items():
        foreigncoverage = foreigncoverage.replace(foreign, english)
        
    foreigncoverage = foreigncoverage.replace('<![CDATA[', '').replace(']]>', '')
    foreigncoverage = foreigncoverage.replace('\n', '')
    foreigncoverage = foreigncoverage.replace('\r', '')
    
    return foreigncoverage



DIGIT_EXP = re.compile('[0-9]+')


def databaseConnection():
        databaseConnection = dbconnector.dbconnector(host="localhost", user="bibliodb", passwd="bibliodb", db="bibliodb",use_unicode=True, charset="latin1").MakeConnection

        
def Checkcoverage(JL):
        a=Bibjournal(JID=JL)
        #a=Bibjournal(JID="JID01411896")
        a.PopulateListOfIssues()
        a.GenerateCoverageStatement()
        #FALSEGAPS=JID09511326



def Checkallcoverage():
    databaseConnection3 = dbconnector.dbconnector(host="localhost", user="iimpiipa", passwd="iimpiipa", db="iimpiipa",use_unicode=True, charset="latin1").MakeConnection
    db3 = databaseConnection3()
    cu3 = db3.cursor()
    #loadall =['JID10426736','JID10499261','JID0002869X','JID08986185','JID01901559','JID09627472','JID09511326','JID0017310X','JID00303607','JID07162790','JID00175463','JID0035791X','JID10552685','JID10583572','JID07344392','JID00030716','JID1050785X','JID02763605','JID10898514','JID03624331','JID10756647','JID07089635','JID01923749','JID00095028','JID01904922','JID10461744','JID10708251','JID00904007','JID12110264','JID03060373']
    #loadall =['JID0035791X','JID09627472']
    #cu3.execute("""SELECT DISTINCT journalid FROM `newrecords`;""")
    #Not a relational database integrity constrainte not enforced (1535 records withhout journalid...no coverage check for them)may be source of troubles later
    cu3.execute("""SELECT journalid  FROM journals;""")
    loadall =cu3.fetchall()
    count=0
    #check=[]
    for row in loadall:
        print "loadall"
        if row[0]==None or row[0]=="":
            continue
        Checkcoverage(row[0])
        #Checkcoverage(row)
        count=count+1
        print count
    cu3.close()
    db3.close()
    #print "check"
    #print self.check
    
    
    
    

         
class Publication(BaseRecord):

    def __init__(self):
    
        self.databaseConnection = dbconnector.dbconnector(host="localhost", user="bibliodb", passwd="bibliodb", db="bibliodb",use_unicode=True, charset="latin1").MakeConnection
        self.db = self.databaseConnection()
        self.recordclass = BaseRecord
        self.recordset=BaseRecordSet()
        self.cu = self.db.cursor()
    
    
            
   
    def Insertdictionary(self,recordict,table):
        ###SOLUTION TO DOT PB TO ADD AND TEST
        #'DateOfPublication' use to contain a dot that should not be there
        if recordict.has_key('DateOfPublication'):
            recordict['DateOfPublication']=recordict['DateOfPublication'].strip('.')
        ###END SOLUTION
        fld=[] 
        self.vl=[]
        
        for k,v in recordict.items():
            fld.append(k)
            #print v
            
            #MySQL 5.0 supports two character sets for storing Unicode data(ucs2 & utf8)
            v.encode('utf-8')
            #v.replace("\\", "\\\\").replace("'", "\\'")
            self.vl.append(v)
            #print self.vl
        field=str(tuple(fld))
        field=str(tuple(fld))
        fields= field.replace("'","")
        value=""
        for v in self.vl:
            value=value+'"%s",'% unicode(v.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"'))
        value=value[:-1]
        value="( %s )"%value
        #print "value"
        #print value    
        
        self.querystring="""INSERT INTO %s %s VALUES %s;""" % (table,fields, value)
        #print self.querystring
        self.cu.execute(self.querystring)
        warnings.filterwarnings("ignore")
        self.countrec= self.countrec + 1
        
    
    def Showtemplate(self,*pubid):
        #create templates
        for tid in pubid:
            self.tablename=self.mandatorytable
            self.db = self.databaseConnection()
            self.cu = self.db.cursor()
            self.cu.execute("""SELECT  * FROM `%s` WHERE %s = '%s';""" % (self.tablename,self.pkfield,tid))
            self.result=self.cu.fetchone()
            if self.publicationtype=="Book":
                #print mandatotry table
                self.requiredFields =['Bid','RecordStatus','RecordType','BibLevel','ControlNumber','RecordTimeStamp','PublicationStatus','PublicationCountry','Language','StartDate','EndDate','Title','PlaceOfPublication','Publisher','RecordCreationDate','DateOfPublication']
                self.optionalFields =[]
                self.templateval(self.requiredFields,self.result)
                #print non mandatotry table
                self.tablename=self.nonmandatorytable
                self.cu.execute("""SELECT * FROM `%s` WHERE fkbid = '%s';""" % (self.tablename,tid))
                self.result=self.cu.fetchone()
                self.requiredFields=['Id','AuthorName','AuthorNumber','AuthorTitle','AuthorDates','AuthorRole','AuthorMiscellaneous','AuthorAttribution','AuthorFullName',\
                'AuthorAffiliation','CorporateAuthor','SubCorporateAuthor','Subtitle','PartTitle','SeriesStatement','GeneralNote','DissertationNote','FormattedContentNote',\
                'SummaryNote','OriginalIntro','OriginalMainEntry','OriginalEditionStatement','OriginalTitle','OriginalDate','OriginalPublisher','PublicationPlace','OriginalDescription','OriginalISSN','OriginalISBN','CopyrightStatement',\
                'LinkNote','SAEAuthorName','SAEAuthorNumber','SAEAuthorTitle','SAEAuthorDates','SAEAuthorRole','SAEAuthorMiscellaneous','SAEAuthorAttribution','SAEAuthorFullName',\
                'SAEAuthorAffiliation','SAETitle','SAESubject','IndexTerm','AEAuthorName','AEAuthorNumber','AEAuthorTitle','AEAuthorDates','AEAuthorRole','AEAuthorMiscellaneous',\
                'AEAuthorAttribution','AEAuthorFullName','AEAuthorAffiliation','AECorporateAuthor','SeriesEntryRelationship','SeriesEntryTitle','FileSize','URI','fkbid']
                self.fieldnames=self.requiredFields
                self.templateval(self.requiredFields,self.result)
                self.optionalFields.append("tmp")
                print self.FillTemplate()
            else:
            #Jounals
                self.requiredFields =['Id','RecordStatus','RecordType','BibLevel','ControlNumber','RecordTimeStamp','RecordCreationDate','PublicationStatus','PublicationCountry',\
                'Language','StartDate','EndDate','Title','PlaceOfPublication','Publisher','DateOfPublication','CoverageStatement']
                self.optionalFields =[]
                self.templateval(self.requiredFields,self.result)
                #print non mandatotry table
                self.tablename=self.nonmandatorytable
                self.templateval(self.requiredFields,self.result)
                #print non mandatotry table
                self.tablename=self.nonmandatorytable
                self.tablename=self.nonmandatorytable
                self.cu.execute("""SELECT * FROM `%s` WHERE fkmarcjid = '%s';""" % (self.tablename,tid))
                self.result=self.cu.fetchone()
                self.requiredFields=['Njid','Subtitle', 'FormerTitle', 'FormerSubtitle','FormerTitleDates','FormerMedium','FormerISSN','CurrentFrequency','CurrentFrequencyDate',\
                'FormerFrequency','FormerFrequencyDate','GeneralNote','TermsOfAccess','NumberingNote','SummaryNote','ReproductionType','ReproductionPublisher','ReproductionNotes','OriginalDate',\
                'OriginalPublisher','PublicationPlace','Introduction','OriginalEdStatement','OriginalTitleStatement','OriginalDescription','OriginalISSN','SAESubject','IndexTerm','AEAuthorName','AEAuthorNumber','AEAuthorTitle',\
                'SeriesEntryRelationship','URI','CopyrightStatement','fkmarcjid']
                self.fieldnames=self.requiredFields
                self.templateval(self.requiredFields,self.result)
                self.optionalFields.append("tmp")
                print self.FillTemplate()
        self.cu.close()
        self.db.close()



   
   
 
    def templateval(self,tfield,tval):
        
        for val in tfield:
            dx=tfield.index(val)
            self.tval=tval
            d=unicode(self.tval[dx])
            
            self.tmp[val]=d
               
   
            
   
    def XLdata(self):
        excel_file = 'values.xls'
        connection = sql.DriverManager.getConnection(
        'jdbc:odbc:Driver={Microsoft Excel Driver (*.xls)};DBQ=%s;READONLY=true}' % excel_file, '', '')
        # Sheet1 is the name of the Excel workbook we want.  The field names for the
        # query are implicitly set by the values for each column in the first row.
        record_set = connection.createStatement( ).executeQuery('SELECT * FROM [Sheet1$]')
        # print the first-column field of every record (==row)
        while record_set.next( ):
            print record_set.getString(1)
            # we're done, close the connection and recordset
        record_set.close( )
        connection.close( )

        
    
     
    
    def Marcrecord(self,source):
        pp = pprint.PrettyPrinter(indent=4)
        sourcefile=open(source,'rU')
        repeat=[]
        nomandictio={}
        mandictio={}
        dictio= {}
        self.databaseConnection = dbconnector.dbconnector(host="localhost", user="bibliodb", passwd="bibliodb", db="bibliodb",use_unicode=True, charset="latin1").MakeConnection
        self.db = self.databaseConnection()
        self.cu = self.db.cursor()
        print "Inserting records from  %s  into the database . Please wait...\n\n\n\n" % (source)
        
        for lin in sourcefile.xreadlines():
            l=lin.decode(self.codec)
            allsubfields=l[6:]
            if l =='\n':
                continue
            else:
                a = l.find('=LDR')
                if a!=-1 and len(mandictio)>0:
                    #print  "MANDICTIO"
                    #***pp.pprint(mandictio)
                    #print  "NOMANDICTIO"
                    #***pp.pprint(nomandictio)
                    if self.publicationtype=='Journal':   
                        self.Insertdictionary(mandictio,self.mandatorytable)
                        nomandictio['fkmarcjid']=str(self.db.insert_id())
                    else :
                        self.Insertdictionary(mandictio,self.mandatorytable)
                        nomandictio['fkbid']=unicode(self.db.insert_id())  
                    #print  "NOMANDICTIO"
                    #print nomandictio
                    self.Insertdictionary(nomandictio,self.nonmandatorytable)
                    mandictio={}
                    repeat=[]
                    dictio={}
                    nomandictio={}
                    self.fieldsindex(l,'LDR',mandictio)

                elif a!=-1 and len(mandictio)==0:
                    self.fieldsindex(l,'LDR',mandictio)
                    continue
                else :                
                    attribute = l[:6]
                    for key in self.allfields.keys():                        
                        strf = key
                        f = attribute.find(strf)
                        if f !=-1:
                            if strf=='534':
                                self.case534(dictio,repeat,strf,l,allsubfields,mandictio,nomandictio)
                            if strf in self.reffield:
                                self.fieldsindex(l,strf,mandictio)
                            else:
                                for key in self.allfields[strf].keys():
                                    if strf in self.mandatoryfieds:
                                        dictio=mandictio
                                    else:
                                        dictio=nomandictio
                                    if strf==245:
                                        self.splitfields(strf)
                                        continue
                                    else:                                      
                                        start=allsubfields.find(key)
                                        if start !=-1:
                                            dictkey=self.allfields[strf][key]
                                            start2= start+2
                                            subfieldstart=allsubfields[start2:]
                                            end=string.find(subfieldstart,'$')
                                            if end !=-1:
                                                dictval=subfieldstart[:end]
                                                #print "LOOK"
                                                #print dictval
                                                #print dictio
                                                self.duplicatefield(dictkey,dictval,dictio,repeat,strf,mandictio,nomandictio)
                                                continue
                                            else:
                                                #dictval=unicode(subfieldstart[:],'latin1')
                                                dictval=subfieldstart[:]
                                                dictval=dictval.replace('\n','')
                                                #print "LOOK2"
                                                #print dictval
                                                #print dictio
                                                self.duplicatefield(dictkey,dictval,dictio,repeat,strf,mandictio,nomandictio)
                                                continue



        #insert last record 
        if len(dictio)>0:
            for k in dictio.keys():
                if k==dictkey:
                    repeat.append(dictio[k])
                    dictio[dictkey]=dictval
                    #dictio[dictkey]=dictval.encode('latin1')
                    #print "MANDICTIO" + "%s"% mandictio
                    #print  "NOMANDICTIO"+"%s"%  nomandictio
        else:
            dictio[dictkey]=dictval
            #dictio[dictkey]=dictval.encode('latin1')
            #print "MANDICTIO" + "%s"% mandictio
            #print  "NOMANDICTIO"+"%s"%  nomandictio
        if self.publicationtype=='Journal':
            self.Insertdictionary(mandictio,self.mandatorytable)
            #if self.publicationtype=='Journal':
            nomandictio['fkmarcjid']=str(self.db.insert_id())
        else :
            self.Insertdictionary(mandictio,self.mandatorytable)
            nomandictio['fkbid']=str(self.db.insert_id())
        #print  "MANDICTIO"
        #print mandictio  
        #print  "NOMANDICTIO"
        #print nomandictio
        self.Insertdictionary(nomandictio,self.nonmandatorytable)           
        self.cu.close()
        self.db.close()
        print "Done \n"
        print str(self.countrec/2) + " records inserted"
        self.countrec=0
    
    
    
    def fieldsindex(self,l,marcfield,mandictio):
        allsubfields=l[6:]
        if marcfield=='LDR':
            mandictio['RecordStatus']=allsubfields[5]
            mandictio['RecordType']=allsubfields[6]
            mandictio['BibLevel']=allsubfields[7]
        elif marcfield=='001':
            mandictio['ControlNumber']=allsubfields.replace('\n','')
        #elif marcfield==005
            #do nothing here timestamp/trigger base /time of last transaction) will set this value in db    
        elif marcfield=='008':
            mandictio['RecordCreationDate']=unicode(strftime("%y%m%d", localtime()))
            #mandictio['RecordCreationDate']=strftime("%y%m%d", localtime())
            #timestamp in field created=now:first insert
            mandictio['PublicationStatus']=allsubfields[6]
            mandictio['PublicationCountry']=allsubfields[15:18]
            mandictio['Language']=allsubfields[35:38]
            mandictio['StartDate']=allsubfields[7:11]
            mandictio['EndDate']=allsubfields[11:15]
            

            
            
            
    

    def duplicatefield(self,dictkey,dictval,dictio,repeat,strf,mandictio,nomandictio):
        #split necessary because unlike "title" 245:subtitle'and'partnbr' are non mandatory
        if strf=='245':
            if dictkey=='Title':
                dictio=mandictio
            else:
                dictio=nomandictio
        
        if len(dictio)>0:
            #HOW DOES IT PROCESS FIELD 700
            if dictkey in dictio:
                repeat=[]
                dictio[dictkey]=dictio[dictkey].rstrip(",")+ "--"
                repeat.append(dictio[dictkey])
                dictval=repeat[0]+dictval.rstrip(",")
                #print "repeat"
                #print repeat
                dictio[dictkey]=dictval            

            else:
                dictio[dictkey]=dictval

        else:
            dictio[dictkey]=dictval
            
    
    


    def case534(self,dictio,repeat,strf,l,allsubfields,mandictio,nomandictio):
        #this method deals only with 3 subfields of field 534 the remaining fields are dealt with in the normal way (part of allfields)
        dictio=nomandictio
        start=allsubfields.find('$c')
        if start !=-1:
            start2= start + 2
            subfieldstart=allsubfields[start2:]
            end=string.find(subfieldstart,':')
            if end !=-1:
                pub='PublicationPlace'
                pubval=subfieldstart[:end]
                self.duplicatefield(pub,pubval,dictio,repeat,strf,mandictio,nomandictio)
                start3 =  end + 2
                subfieldstart2=subfieldstart[start3:]
                end2=string.find(subfieldstart2,',')
                if end2 !=-1:
                    opub= 'OriginalPublisher'
                    opubval=subfieldstart2[:end2]
                    self.duplicatefield(opub,opubval,dictio,repeat,strf,mandictio,nomandictio)
                    start4=end2+2 
                    subfieldstart3=subfieldstart2[start4:]
                    end3=string.find(subfieldstart3,'.')
                    if end3 !=-1:
                        newend=end3 -1
                        dat='OriginalDate'
                        datval= subfieldstart3[:end3]
                        self.duplicatefield(dat,datval,dictio,repeat,strf,mandictio,nomandictio)
                else:
                    opubval=subfieldstart[end:].replace('\n','')
                    opub='OriginalPublisher'
                    self.duplicatefield(opub,opubval,dictio,repeat,strf,mandictio,nomandictio)
                    dictio['OriginalDate']=''







class PublicationRecordset(BaseRecordSet):
    
   

    def __init__(self):
    
        #self.tablename='Journal'
        self.databaseConnection = dbconnector.dbconnector(host="localhost", user="bibliodb", passwd="bibliodb", db="bibliodb",use_unicode=True, charset="latin1").MakeConnection
        self.db = self.databaseConnection()
        self.recordclass = BaseRecord
        self.recordset=BaseRecordSet()

    
        #TO SET VALUES FROM DB USE self.populatefromdb(**conditions)
        
       


    def UserInput(self,tablename):
        # Create a record 'shell':a dictionary with fieldnames as keys and  values set to None(just waiting for values to be set by user input)
        self.tablename=tablename
        self.getdbfields()
        self.Pubrec = {}.fromkeys(self.fieldnames)
        print 'Enter values:\n'
        for key in self.Pubrec.keys():
        #print 'Enter values',
            print '%s:' % key,
            self.Pubrec[key]= raw_input()
            

    #TO INSERT THE VALUES COLLECTED CALL InsertIntoDB (self,**entries):



class JournalRecordset(PublicationRecordset):

    def __init__(self):
        self.recordset=PublicationRecordset()
        
    
    
    
    
    #def PopulateListOfIssues(self,querymethod=None):
    def PopulateListOfIssues(self):
        self.ListOfAllIssuesQuery()
        #querymethod()
        self.ListOfIssues=[]
        self.all=self.cu.fetchall()

        if self.cu.rowcount==0:
            return -1
        # Weed out rogue duplicates
        self.rogues = []
        self.numberingpattern=[]
        self.year=[]
        self.month=[]
        self.mdiff=[]
        for issue in self.all:
            issue= list (issue)
            #issue.append(self.issattributes)
            self.ListOfIssues.append(issue)
            #Ilenght= len(self.ListOfIssues)
            previousissue=self.ListOfIssues[0]

        for issue in self.ListOfIssues[1:]:
            if issue[2] == previousissue[2]:
                self.db = self.databaseConnection()
                cu3 = self.db.cursor()
                issuecount = cu3.execute("""SELECT * FROM `%s`  WHERE %s='%s' AND '%s'='%s' AND '%s'='%s' AND '%s'='%s' AND '%s'='%s';""" % \
                (self.issuetablename,self.foreignk,self.requiredFields,self.fieldnames[2],issue[2],self.fieldnames[3],issue[3],self.fieldnames[4],issue[4],self.fieldnames[5],issue[5]))
                cu3.close()
                #check=cu3.fetchall()
                cu3 = self.db.cursor()
                prevcount = cu3.execute("""SELECT * FROM `%s`  WHERE %s='%s' AND %s='%s' AND %s='%s' AND %s='%s' AND %s='%s';""" % \
                    (self.issuetablename,self.foreignk,self.requiredFields,self.fieldnames[2], previousissue[2],self.fieldnames[3] ,previousissue[3],self.fieldnames[4] ,previousissue[4], self.fieldnames[5],previousissue[5]))
                cu3.close()
                self.db.close()
                if issuecount > prevcount:
                    self.rogues.append(previousissue)
                else:
                    self.rogues.append(issue)
            previousissue = issue

        for rogue in self.rogues:
            if rogue in self.ListOfIssues:
                self.ListOfIssues.remove(rogue)
        self.lenrogues= len(self.rogues)
        del self.rogues

        # Generate Numbering patterns

        for issue in self.ListOfIssues:
            nbringpatrn =0
            if issue[3] != '':
                nbringpatrn += 4
            if issue[4] != '':
                nbringpatrn += 2
            if issue[5] != '':
                nbringpatrn += 1
            self.numberingpattern.append(nbringpatrn)

        # Generate frequency analysis

        for issue in self.ListOfIssues:
            Iyear = 3000
            Imonth= 13
            try:
                Iyear = int(issue[2][:4])
                Imonth = int(issue[2][4:6])
            except ValueError:
                Iyear = 3000
                Imonth= 13
            self.year.append(Iyear)
            self.month.append(Imonth)
        
        previousissue = self.ListOfIssues[0]
        self.frequencies = {}
        for issue in self.ListOfIssues[1:]:
            idx=self.ListOfIssues.index(issue)
            self.monthdiff = self.month[idx] - self.month[idx-1] 
            self.monthdiff += (self.year[idx] - self.year[idx-1]) * 12
            self.mdiff.append(self.monthdiff)
            if self.frequencies.has_key(self.monthdiff):
                self.frequencies[self.monthdiff] += 1
            else:
                self.frequencies[self.monthdiff] = 1
            previousissue = issue
        if len(self.ListOfIssues) > 1:
            self.mdiff2 = []
            self.mdiff2.append(self.mdiff[0])
            for md in self.mdiff:
                self.mdiff2.append(md)
                self.mdiff=self.mdiff2
        else:  
            #self.mdiff[0]=1
            self.mdiff.insert(0,"1")
            self.frequencies[1] = 3
            #added quotes
        orderedfrequencies = [(freqcount, freq) for (freq,freqcount) in self.frequencies.items()]
        orderedfrequencies.sort()
        self.unusualfreq = orderedfrequencies[len(orderedfrequencies)/2]
        print "frequencies"
        print self.frequencies
        print self.unusualfreq









    #def GenerateCoverageStatement(self, updatemethod=None):
    def GenerateCoverageStatement(self): 
        #print "step1"
        self.cu.execute("""SELECT %s FROM `%s` WHERE %s= '%s';""" % (self.frequency,self.tablename,self.foreignk,self.JID))
        freq=self.cu.fetchall() 
        self.cu.close()
        self.frequency=freq[0][0]
        print "self frequency"
        print self.frequency
        if len(self.ListOfIssues) == 0:
            self.statement=''
            self.Recordgaps()
            return
        if self.frequency == '0':
            self.basefrequency = 12        
        else:
            try:
                self.basefrequency = int((12 / int(self.frequency)) * 1.5)
            except ValueError:
                self.basefrequency = 12
        print"gen stat"
        print self.frequency
        print self.basefrequency

    
    
    

        def easycoverage(obj):
            #print "step2"
            ret = ''
            indx=self.ListOfIssues.index(obj)
            for x in self.fieldnames[1:]:
                z=self.fieldnames.index(x)
                ret += x + '=' + unicode(self.ListOfIssues[indx][z]) + '\n'
            ret += 'numberingpatern' + '=' + unicode(self.numberingpattern[indx]) + '\n'
            ret += 'monthdiff' + '=' + unicode(self.mdiff[indx]) + '\n'
            ret += 'frequency of this monthdiff =' + str(self.frequencies[int(self.mdiff[indx])])+ '\n'
            return ret


        def coverageEnumeration(obj):
            #print "step3"
            ret = ''
            odx=self.ListOfIssues.index(obj)
            if self.numberingpattern[odx] == 1: # just NUM
                ret += 'no. ' + self.ListOfIssues[odx][5]
            elif self.numberingpattern[odx] == 7: # VOL, ISS AND NUM
                ret += 'vol. ' + self.ListOfIssues[odx][3] + ', no. ' + self.ListOfIssues[odx][4] + ' = no. ' + self.ListOfIssues[odx][5]
            else:
                if self.ListOfIssues[odx][3]!= '': # VOL present
                    ret += 'vol. ' + self.ListOfIssues[odx][3]
                    if self.ListOfIssues[odx][4] != '' or self.ListOfIssues[odx][5] != '':
                        ret += ', '
                if self.ListOfIssues[odx][4] != '': # ISS present
                    ret += 'no. ' + self.ListOfIssues[odx][4]
                if self.ListOfIssues[odx][5] != '': # NUM present
                    ret += 'no. ' + self.ListOfIssues[odx][5]
            if self.ListOfIssues[odx][3] != '' or self.ListOfIssues[odx][4] != '' or self.ListOfIssues[odx][5] != '':
                ret += ' (' + self.ListOfIssues[odx][1] + ')'
            else:
                ret += self.ListOfIssues[odx][1]
            ret = translatecoverage(ret)  
            return ret






        
        def gaplogic(issue, previousissue):
            #print "step4"
            gdx=self.ListOfIssues.index(issue)
            ret = False
            if (self.frequencies[self.mdiff[gdx]] < self.unusualfreq and self.mdiff[gdx] > self.basefrequency):
                ret = True
                if self.ListOfIssues[gdx][2].endswith('0000'):
                    ret = False
                if self.ListOfIssues[gdx]!='' and self.ListOfIssues[gdx-1][4]!='':
                    issue_numericiss = [int(x) for x in DIGIT_EXP.findall(self.ListOfIssues[gdx][4])]
                    #print "issue_numericiss" 
                    #print issue_numericiss 
                    issue_numericiss.sort()
                    previousissue_numericiss = [int(x) for x in DIGIT_EXP.findall(self.ListOfIssues[gdx-1][4])]
                    #print previousissue_numericiss
                    previousissue_numericiss.sort()
                    if len(issue_numericiss) > 0 and len(previousissue_numericiss) > 0:
                        if issue_numericiss[0] - previousissue_numericiss[-1] == 1:
                            ret = False
            return ret
        #print "step5"
        self.coverages = []
        self.formattedcoverages = []
        #first issue
        currentissue = self.ListOfIssues[0]
        #append returned value
        self.coverages.append([easycoverage(currentissue),'', ''])
        self.formattedcoverages.append([coverageEnumeration(currentissue)[0].upper()+ coverageEnumeration(currentissue)[1:],'']) 
        #cycle through intermediate issues, checking for triggers
        previousissue = currentissue
        self.db = self.databaseConnection()
        self.cu = self.db.cursor()
        #***self.cu.execute("""SELECT statustype FROM journals WHERE %s= '%s';""" % (self.foreignk,self.JID))
        self.cu.execute("""SELECT %s FROM `%s` WHERE %s= '%s';""" % (self.statustype,self.tablename,self.foreignk,self.JID))
        status=self.cu.fetchall() 
        self.cu.close()
        self.statustype=status[0][0]
        for issue in self.ListOfIssues[1:-1]:
            gdx=self.ListOfIssues.index(issue)
            if issue[0] != previousissue[0] \
            or (self.numberingpattern[gdx] != self.numberingpattern[gdx-1]
                and self.numberingpattern[gdx] != 0 
                and self.numberingpattern[gdx-1] != 0
                and (self.numberingpattern[gdx] == 1 or self.numberingpattern[gdx-1] == 1)
                )\
            or gaplogic(issue, previousissue):
                if issue[0] != previousissue[0]: reason = 'Change of title'
                if (self.numberingpattern[gdx] != self.numberingpattern[gdx-1] 
                and self.numberingpattern[gdx] != 0 
                and self.numberingpattern[gdx-1] != 0 
                and (self.numberingpattern[gdx] == 1 or self.numberingpattern[gdx-1] == 1)
                ): reason = 'Change of numbering pattern'
                if (self.frequencies[self.mdiff[gdx]] < self.unusualfreq 
                and self.mdiff[gdx] > self.basefrequency):reason = 'Unusual number of months (>9) since last issue'
                #print"WRONG"
                #print self.frequencies[self.mdiff[gdx]]
                #print self.unusualfreq
                #print self.mdiff[gdx]
                #print self.basefrequency
                self.coverages[-1][1] = easycoverage(previousissue)
                self.formattedcoverages[-1][1] = coverageEnumeration(previousissue)
                self.coverages.append([easycoverage(issue),'', 'Reason: ' + reason])
                self.formattedcoverages.append([coverageEnumeration(issue),''])
                    #print "GDX"
                    #print gdx
            previousissue = issue
            #last issue       
        if self.statustype != 'Current':
            currentissue = self.ListOfIssues[-1]
            self.coverages[-1][1] = easycoverage(currentissue)
            self.formattedcoverages[-1][1] = coverageEnumeration(currentissue)

        if self.statustype == 'Selective Coverage':
            self.formattedcoverages = [[self.formattedcoverages[0][0], self.formattedcoverages[-1][1]]]
        self.statement = unicode('; '.join([start+'-'+end for start,end in self.formattedcoverages]))

        if self.statustype != 'Current':
            self.statement += '.'
        print"old format"
        print self.formattedcoverages 
        
        
        print"new format"
        print self.formattedcoverages
        self.statement = '; '.join([start+'-'+end for start,end in self.formattedcoverages]) + '.\n'
        #self.statement = self.statement.replace("-dummy value.","")
        print"statement"
        print self.statement
        self.db = self.databaseConnection2()
        self.cu = self.db.cursor()
        self.cu.execute("""SELECT * FROM Coverage WHERE gapjrnlid= '%s';""" % (self.JID))
        #
        if self.cu.rowcount==0:
            #first time are seached for this journal
            self.Recordgaps()
            #CALL TO self.Checkdblissues(self.statement)
            if self.statement.find("=")!=-1 or self.statement.find("vol.")==-1 or self.statement.find("no.")==-1 :
                self.Checkdblissues(self.statement)
        else:
            #gaps seached at least once
            self.foundgap=self.cu.fetchall()
            print "foundgap"
            print self.foundgap
            #recordedgaps=[]
            oldgaps=[]
            falsegaps=[]
            #falsegaps field is not empty
            if self.foundgap[0][3]!=None and self.foundgap[0][3]!="":
                recordedgaps= str(self.foundgap[0][3])
                print "recordedgaps"
                print recordedgaps
                # test withouth ... recordedgaps=oldrecordedgaps.replace(';',';$')
                recordedgaps=recordedgaps.replace(';',';$')
                print recordedgaps
                if recordedgaps.startswith('$'):
                   recordedgaps=recordedgaps.lstrip('$')
                print recordedgaps
                #falsegap from db
                for end in recordedgaps:
                    end=recordedgaps.find('$')
                    if end !=-1:
                        start=0
                        gap=recordedgaps[start:end]
                        falsegaps.append(gap.strip())
                        start=end+1
                        recordedgaps=recordedgaps[start:]
                     #check for best results
                    else:
                        falsegaps.append(recordedgaps.strip())
                        break
                print 'falsegaps'
                print falsegaps
                #seems not to be necessary
                #gaps in self statemen include good and false gaps
                self.newstatement=str(self.statement)
                print "statement***"
                print self.newstatement
                for end in self.newstatement:
                    end=self.newstatement.find(';')
                    if end !=-1:
                        start=0
                        gap=self.newstatement[start:end+1]
                        oldgaps.append(gap.strip())
                        start=end+1
                        self.newstatement=self.newstatement[start:]
                    else:
                        end=self.newstatement.find('\n')
                        if end !=-1:
                            oldgaps.append(self.newstatement.strip())
                            break
                print 'oldgaps'
                print oldgaps
                
                
                for gp in falsegaps:
                    gp2=gp +';' 
                    if gp in oldgaps :
                        oldgaps.remove(gp)
                    if gp2 in oldgaps :
                        oldgaps.remove(gp2)
                truegaps=""
                for tg in oldgaps:
                    truegaps += tg
                if truegaps.endswith(';'):
                    truegaps=truegaps.rstrip(';')
                print "truegaps"
                print oldgaps
                print truegaps
                self.Updategaps(truegaps)
            else:
                #gap field is empty (no gap found the previous time
                self.Updategaps(self.statement)
                
        self.cu.close()
        self.db.close() 
               


    def Updategaps(self,formattedgaps):
        #remove falsgaps:delete all false gap or only thosefound in formatted coverages
        self.db1 = self.databaseConnection2()
        self.cu1 = self.db1.cursor()
        self.cu1.execute
        self.cu1.execute("""UPDATE Coverage SET gaps= \"%s\" WHERE gapjrnlid= \"%s\";""" % (formattedgaps,self.JID)) 
        self.cu1.close()
        self.db1.close()    
        
    
    def Recordgaps(self):
        self.qstring="""INSERT INTO Coverage (product,gaps,gapjrnlid) VALUES (\"%s\",\"%s\",\"%s\");""" % (self.product,self.statement,self.JID)
        print self.qstring
        self.db1 = self.databaseConnection2()
        self.cu1 = self.db1.cursor()
        self.cu1.execute(self.qstring)
        self.cu1.close()
        self.db1.close() 
        print "inserted"




    
    def ParseRawText(self):
        for field, value in self.reg_exp.findall(self.rawtext):
            if hasattr(self, field):
                value = getattr(self, field) + "--" + value
            setattr(self, field, value)



    
    
    
    
    
    def Checkdblissues(self,recordedgaps):
    #WORK WELL ONLY IF  GAP CONTAINS "\s*\d+\,\s+no.\s+\d not followed by =" or simply do not containd "="
        #recordedgaps="Vol. 17, no. 7-8 = no. 151-152 (Jan.-Feb. 1996)-vol. 19, no. 6 = no. 174 (Dec. 1997); vol. 19, no. 9 = no. 177 (Mar. 1998)-vol. 26, no. 6 = no. 258 (Dec. 2004); no. 259-260 (Jan.-Feb. 2005)-no. 259-260 (Jan.-Feb. 2005); vol. 26, no. 9 = no. 261 (Mar. 2005)-vol. 26, no. 12 = no. 264 (June 2005); no. 265 (July 2005)-no. 265 (July 2005); vol. 27, no. 2-3 = no. 266-267 (Aug.-Sept. 2005)-vol. 27, no. 2-3 = no. 266-267 (Aug.-Sept. 2005); no. 268 (Oct. 2005)-no. 269 (Nov. 2005); vol. 27, no. 6 = no. 270 (Dec. 2005)-vol. 27, no. 7-8 = no. 271-272 (Jan.-Feb. 2006); no. 273 (Mar. 2006)-no. 274 (Apr. 2006); vol. 27, no. 11 = no. 275 (May 2006)-vol. 27, no. 12 = no. 276 (June 2006); no. 277 (July 2006)-no. 278-279 (Aug.-Sept. 2006); no. 280 (Oct. 2006)-no. 281 (Nov. 2006); vol. 28, no. 6 = no. 282 (Dec. 2006)-vol. 28, no. 12 = no. 288 (June 2007)\
        # "
        
        if recordedgaps=="":
            return
        if recordedgaps.find(";")==-1:
            newsttmnt="No gap"
            self.recordfiltered(newsttmnt)
            return
            #empty statement --->nothing to filter ****source of pb???
        falsegaps=[]
        cleangap=[]
        cleancopy=[]
        #print "recordedgaps"
        #print recordedgaps
        #***copy of gaps in db
        # test withouth ... recordedgaps=oldrecordedgaps.replace(';',';$')
        recordedgaps=recordedgaps.replace(';',';$')
        #print recordedgaps
        #for end in recordedgaps:
        if recordedgaps.startswith('$'):
           recordedgaps=recordedgaps.lstrip('$')
        #print recordedgaps
        #falsegap from db
        for end in recordedgaps:
            end=recordedgaps.find('$')
            if end !=-1:
                start=0
                gap=recordedgaps[start:end]
                falsegaps.append(gap.strip())
                start=end+1
                recordedgaps=recordedgaps[start:]
            else:
                falsegaps.append(recordedgaps.strip())
                break
        #print 'falsegaps'
        #print falsegaps
    
        for tg in falsegaps:
            if tg.endswith(';'):
                tg=tg.rstrip(';')
                cleangap.append(tg)
                cleancopy.append(tg)
            else:
                cleangap.append(tg)
                cleancopy.append(tg)
        print cleancopy
        flag="red"
        for cg in cleangap:
            rank = cleangap.index(cg)
            if cg==cleangap[-1]:

                continue
                
            print 'cg'
            print cg
            first="o*\.*\s*\d*-*\d*\s*\(\d*\s*[A-Z]*[a-z]*\s*\.*\s*-*\d*-*\d*\s*[A-Z]*[a-z]*\.*\s*\d+\)$"
            if rank % 2 ==0:
                print rank
                isin = re.findall(first,str(cg))
                if isin != []:
                    lisin=isin[-1]
                    print lisin
                    #Make sure that is the one at he end of the line
                    isnbr="-*\d+\s*\("
                    date="\(\d*\s*[A-Z]*[a-z]*\s*\.*\/*\s*-*\d*-*\d*\s*[A-Z]*[a-z]*\.*\s*\d+\)"
                    findate=re.findall(date,lisin)
                    print "findate"
                    print findate
                    #***if findate=[]
                        #***move on
                    if findate !=[]:
                        findate2=findate[-1]
                        findyear="\d\d\d\d\)"
                        year=re.findall(findyear,findate2)
                        year0=year[-1]
                        year1=int(year[-1].replace(')',""))
                    else:
                         year1=0
                    print "year1"
                    print year1
                    #fmonth="De*\.*"
                    last=re.findall(isnbr,lisin)
                    lastis=last[-1]
                    print "lastis"
                    print lastis
                    lastis2=lastis.replace('-',"")
                    #TRYING WITH THAT TO INCLUDE VOL
                    nextisnbr= str(int(lastis2.replace('(',"")))
                    nextisnbr2=str(int(lastis2.replace('(',""))+1)
                    #added "" to make sure tahat the number we are looking for is followed by a least one space (avoid :if nextisnbr =2 find it in "2007"
                    print "nextisnbrs"
                    print nextisnbr
                    print nextisnbr2
                    nextcg=str(cleangap[rank+1])
                    print "nextcg"
                    print nextcg
                    #part2isnbr="o*\.*\s*\d*-*\d*\s*\("
                    #VOL
                    part2isnbr="o*\l*\.*\s*\d*-*\d*\s*\("
                    foundnext=re.findall(part2isnbr,nextcg)
                   
                    print "foundnext*********"
                    print foundnext
                    if foundnext==[]:
                        continue     
                    foundnext2=foundnext[0].replace('(',"")
                    print "foundnextis********* need cleaning??"
                    print foundnext2
                    print "findate year 2"
                    findate=re.findall(date,nextcg)
                    print findate
                    #findate2=findate[-1]
                    #changed from -1 t0 0
                    #ADDED
                    if findate !=[]:
                        findate2=findate[0]
                        findyear="\d\d\d\d\)"
                        year=re.findall(findyear,findate2)
                        print "findall year 2"
                    #print year
                        year2=int(year[0].replace(')',""))
                    else:
                        year2=0
                    print "year2"
                    print year2
                    
                  
                    foundnextis=foundnext2.find(nextisnbr)
                    print "foundnextis*********"
                    print foundnextis
                    if foundnextis == -1:
                        print "foundnextis...2"
                        foundnextis=foundnext2.find(nextisnbr2)
                        print "identified"
                        print foundnextis
                    if foundnextis != -1 and year1 ==year2 or foundnextis != -1 and year2==year1 +1 :
                        print "foundnextis before remove"
                        print foundnextis
                        #or year2=year1+1 and lstmonth!=[]
                        cleancopy.remove(cg)
                        cleancopy.remove(nextcg)
                        flag="green"
                        #based on the first item :if the first and the second item have been removed we will be examing now the second item ????
                        #continue...to nextcg
                        #continue to item after next cg
                    
                    #check here if the next does not contain the next issue???
                    #cleancopy.remove(nextcg) last???
                else:
                    print "none"
                    continue
            else:
                #we are on the nextcg and therefore checked previously(odd index)
                continue
        if len(cleancopy)% 2 !=0:
            clean=cleancopy
            cleancopy.remove(clean[-1])
        print cleancopy 
        #from list to string
        if cleancopy==[]:
            newsttmnt="No gap"
            self.recordfiltered(newsttmnt)
            #All these are not true gaps.with the new solution,the gaps field will be empty in this case
        elif flag=="red":
            newsttmnt=""
            #*****????all were false gaps pbs here?
            #is this the best way of exiting the function? is there anytying to return to?
            #return
            #print "lenght"
            #print len(cleancopy)
            if len(cleangap)% 2 ==0:
                newsttmnt="OK"
                self.recordfiltered(newsttmnt)
                return
            else:    #print "cleancopy after rempoval"
                #print cleancopy
                for filtered in cleancopy:
                    newsttmnt+=filtered+";"
                newsttmnt=newsttmnt.rstrip(";")
                self.recordfiltered(newsttmnt)
                return
      
        else:
            newsttmnt=""
            if len(cleancopy)==1:
                newsttmnt="No gap"
                self.recordfiltered(newsttmnt)
                return
            for filtered in cleancopy:
                newsttmnt+=filtered+";"
            newsttmnt=newsttmnt.rstrip(";")
            self.recordfiltered(newsttmnt)
            return
            
    def recordfiltered (self,newsttmnt):
        self.qstring="""UPDATE Coverage SET filteredgaps =\"%s\" WHERE gapjrnlid =\"%s\";""" % (newsttmnt,self.JID)
        #self.qstring="""INSERT INTO Coverage (product,gaps,gapjrnlid) VALUES (\"%s\",\"%s\",\"%s\");""" % (self.product,self.statement,self.JID)
        print self.qstring
        self.db2 = self.databaseConnection3()
        self.cu2 = self.db2.cursor()
        self.cu2.execute(self.qstring)
        #self.cu.execute(self.qstring)
        self.cu2.close()
        self.db2.close()   

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    



    
    
   


class Bibjournal(JournalRecordset,Publication):
#the coverage methods(PopulateListOfIssues,GenerateCoverageStatement,easycoverage,coverageEnumeration,gaplogic...
#in class JournalRecordset) are based on Lists and 'fetch' function; the order of the attributes in the list, 
#and fields in queries(when overloadind variables)is therefore important,
#when inheriting JournalRecordset for the purpose of checking the coverage of a journal, to set the following variables and query approrpriatetly
#Such inheritance is based on the assumptions that the table containing the issues of the particular journal has a direct relationship 
#with table Journals (has a foreign key:value of self.foreignk, corresponding to primary key 'journalid' in the journals table of iimpiipa database)  
    
#Variables
##see COVERAGE below
    
#function 
#ListOfAllIssuesQuery-ListOfAllIssuesUpdate 

    def __init__(self, rawtext=None,JID=None):
    
        self.codec = 'latin1'
        self.mandatoryfieds= ['LDR','001','005','008','260','362']
        self.reffield=['001','008']
        self.allfields={'245':{'$a':'Title','$b':'Subtitle'},'247':{'$a':'FormerTitle','$b':'FormerSubtitle','$f':'FormerTitleDates','$h':'FormerMedium','$x':'FormerISSN'},\
               '310':{'$a':'CurrentFrequency','$b':'CurrentFrequencyDate'},'321':{'$a':'FormerFrequency','$b':'FormerFrequencyDate'},'362':{'$a':'CoverageStatement'},\
               '500':{'$a':'GeneralNote'},'506':{'$a':'TermsOfAccess'},'515':{'$a':'NumberingNote'},'520':{'$a':'SummaryNote'},\
               '533':{'$a':'ReproductionType','$c':'ReproductionPublisher','$n':'ReproductionNotes'},\
               '534':{'$p':'Introduction','$b':'OriginalEdStatement','$t':'OriginalTitleStatement','$e':'OriginalDescription','$x':'OriginalISSN',},\
               '540':{'$a':'CopyrightStatement'},'650':{'$a':'SAESubject'},'653':{'$a':'IndexTerm'},'700':{'$a':'AEAuthorName','$c':'AEAuthorNumber','$d':'AEAuthorTitle'},\
               '773':{'$t':'SeriesEntryRelationship'},'856':{'$u':'URI'},'260':{'$a':'PlaceOfPublication','$b':'Publisher','$c':'DateOfPublication'},'001':{},'008':{}}
    
        self.publicationtype='Journal'
        self.mandatorytable='Marcjournalman'
        self.nonmandatorytable='Marcjournalnonman'
        self.countrec=0
        self.databaseConnection = dbconnector.dbconnector(host="localhost", user="bibliodb", passwd="bibliodb", db="bibliodb",use_unicode=True, charset="latin1").MakeConnection
        #self.databaseConnection = dbconnector.dbconnector(host="localhost", user="iimpiipa", passwd="iimpiipa", db="iimpiipa",use_unicode=True, charset="latin1").MakeConnection
        self.db = self.databaseConnection()
        self.cu = self.db.cursor()
        self.templateclass =wholejrnl.wholejrnl
        self.recordset=PublicationRecordset()
        self.tmp={}
        self.vl=[]
        self.pkfield="Id"
        self.tval=[]
        
        
        
        #COVERAGE (all the following variables and function are required and should be added or 'overloaded' in the inheriting class if necessary)
        self.issuetablename='newrecords'
        self.tablename='journals'
        self.requiredFields = JID
        self.cu2 = self.db.cursor()
        self.recordclass=Publication
        self.recordset=PublicationRecordset()
        self.JID=JID
        #will be the "Njid" passed to tables contening the issues
        self.lenrogues=0
        #foreignk in the issues tables-- has same value as JID
        self.foreignk='journalid'
        self.foreignk=self.foreignk.replace("'", "")
        self.statement=''
        self.product='iimpiipa'
        #field corresponding to frequency field in self.tablename
        self.frequency='frequency'
        #field corresponding to statustype field in self.tablename
        self.statustype='statustype'
        self.databaseConnection2 = dbconnector.dbconnector(host="localhost", user="jcover", passwd="jcover", db="jcover").MakeConnection
        self.databaseConnection3 = dbconnector.dbconnector(host="localhost", user="jcover", passwd="jcover", db="jcover").MakeConnection
        PublicationRecordset.__init__(self)
        self.ListOfIssues = PublicationRecordset()
        
        
        
        self.ListOfIssues.fieldnames = ['journaltitle', 'pubdisplaydate', 'publishedstartdate', 'journalvolume', 'journalissue', 'sequencenum'] 
        #self.ListOfIssues.fieldnames = ['journalname', 'displaydate', 'startdate', 'journalvolume', 'journalissue', 'sequencenum']  
        #inheritance : elements in the list should be replaced by corresponding field names in that precised order
        #same rule applies to the field names in the functions below.
        self.fieldnames=self.ListOfIssues.fieldnames



    def ListOfAllIssuesQuery(self):
        self.cu.execute("""SELECT DISTINCT journaltitle, pubdisplaydate, publishedstartdate, journalvolume, journalissue, sequencenum FROM `newrecords` WHERE %s='%s' ORDER BY publishedstartdate;""" % (self.foreignk,self.JID))
        self.cu2.execute("""SELECT DISTINCT journaltitle, pubdisplaydate, publishedstartdate, journalvolume, journalissue, sequencenum FROM `newrecords` WHERE %s='%s' ORDER BY publishedstartdate;""" % (self.foreignk,self.JID))
          
    
    
    
    
    
    

    
class Book(Publication,PublicationRecordset):
 
    
    def __init__(self):
        
        self.codec = 'latin1'
        self.mandatoryfieds= ['LDR','001','005','008','260']
        self.reffield=['001','008']
        self.allfields={'100':{'$a':'AuthorName','$b':'AuthorNumber','$c':'AuthorTitle','$d':'AuthorDates','$e':'AuthorRole','$g':'AuthorMiscellaneous','$j':'AuthorAttribution','$q':'AuthorFullName','$u':'AuthorAffiliation'},\
        '110':{'$a':'CorporateAuthor','$b':'SubCorporateAuthor'},'245':{'$a':'Title','$b':'Subtitle','$p':'PartTitle'},'490':{'$a':'SeriesStatement'},'500':{'$a':'GeneralNote'},'502':{'$a':'DissertationNote'},'505':{'$a':'FormattedContentNote'},\
        '520':{'$a':'SummaryNote'},'534':{'$p':'OriginalIntro','$a':'OriginalMainEntry','$b':'OriginalEditionStatement','$t':'OriginalTitle','$e':'OriginalDescription','$x':'OriginalISSN','$z':'OriginalISBN'},\
        '540':{'$a':'CopyrightStatement'},'580':{'$a':'LinkNote'},'600':{'$a':'SAEAuthorName','$b':'SAEAuthorNumber','$c':'SAEAuthorTitle','$d':'SAEAuthorDates','$e':'SAEAuthorRole','$g':'SAEAuthorMiscellaneous','$j':'SAEAuthorAttribution','$q':'SAEAuthorFullName','$u':'SAEAuthorAffiliation','$t':'SAETitle'},\
        '650':{'$a':'SAESubject'},'653':{'$a':'IndexTerm'},\
        '700':{'$a':'AEAuthorName','$b':'AEAuthorNumber','$c':'AEAuthorTitle','$d':'AEAuthorDates','$e':'AEAuthorRole','$g':'AEAuthorMiscellaneous','$j':'AEAuthorAttribution','$q':'AEAuthorFullName','$u':'AEAuthorAffiliation'},\
        '710':{'$a':'AECorporateAuthor'},'773':{'$g':'SeriesEntryRelationship','$t':'SeriesEntryTitle'},'856':{'$s':'FileSize','$u':'URI'},'260':{'$a':'PlaceOfPublication','$b':'Publisher','$c':'DateOfPublication'},'001':{},'008':{}}
        self.publicationtype='Book'
        self.mandatorytable='Marcbookman'
        self.nonmandatorytable='Marcbooknonman'
        self.countrec=0
        self.databaseConnection = dbconnector.dbconnector(host="localhost", user="bibliodb", passwd="bibliodb", db="bibliodb",use_unicode=True, charset="latin1").MakeConnection
        self.db = self.databaseConnection()
        self.cu = self.db.cursor()
        self.templateclass =wholebook.wholebook
        self.recordset=PublicationRecordset()
        self.tmp={}
        #try limiting it to vl and tval
        self.vl=[]
        self.pkfield="Bid"
        self.tval=[]
        self.entityconverter = ""
        
        
        
        
        
        
        
        """
        CREATE TABLE `Marcbookman` (\n  `Bid` int(11) NOT NULL auto_increment,\n  `RecordStatus` varchar(1) NOT NULL default 'n',\n  `RecordType` varchar(1) NOT NULL default 'a',\n  `BibLevel` varchar(1) NOT NULL default 's',\n  `ControlNumber` varchar(15) NOT NULL,\n  `RecordTimeStamp` varchar(20) NOT NULL,\n  `PublicationStatus` varchar(1) NOT NULL default 'c',\n  `PublicationCountry` varchar(3) NOT NULL,\n  `Language` varchar(3) NOT NULL,\n  `StartDate` varchar(4) NOT NULL,\n  `EndDate` varchar(4) NOT NULL,\n  `Title` text NOT NULL,\n  `PlaceOfPublication` varchar(50) NOT NULL,\n  `Publisher` varchar(250) NOT NULL,\n  `RecordCreationDate` varchar(6) NOT NULL,\n  `DateOfPublication` varchar(16) NOT NULL,\n  PRIMARY KEY  (`Bid`)\n) ENGINE=MyISAM AUTO_INCREMENT=77 DEFAULT CHARSET=latin1
        
        CREATE TABLE `Marcbooknonman` (\n  `Id` int(11) NOT NULL auto_increment,\n  `AuthorName` varchar(250) default NULL,\n  `AuthorNumber` varchar(30) default NULL,\n  `AuthorTitle` varchar(250) default NULL,\n  `AuthorDates` varchar(250) default NULL,\n  `AuthorRole` varchar(250) default NULL,\n  `AuthorMiscellaneous` varchar(250) default NULL,\n  `AuthorAttribution` varchar(250) default NULL,\n  `AuthorFullName` varchar(250) default NULL,\n  `AuthorAffiliation` text,\n  `CorporateAuthor` varchar(250) default NULL,\n  `SubCorporateAuthor` varchar(250) default NULL,\n  `Subtitle` text,\n  `PartTitle` varchar(5) default NULL,\n  `SeriesStatement` varchar(30) default NULL,\n  `GeneralNote` text,\n  `DissertationNote` text,\n  `FormattedContentNote` text,\n  `SummaryNote` text,\n  `OriginalIntro` text,\n  `OriginalMainEntry` varchar(250) default NULL,\n  `OriginalEditionStatement` text,\n  `OriginalTitle` text,\n  `OriginalDate` varchar(4) default NULL,\n  `OriginalPublisher` varchar(250) default NULL,\n  `PublicationPlace` varchar(250) default NULL,\n  `OriginalDescription` text,\n  `OriginalISSN` varchar(20) default NULL,\n  `OriginalISBN` varchar(20) default NULL,\n  `CopyrightStatement` text,\n  `LinkNote` text,\n  `SAEAuthorName` varchar(250) default NULL,\n  `SAEAuthorNumber` varchar(30) default NULL,\n  `SAEAuthorTitle` varchar(250) default NULL,\n  `SAEAuthorDates` varchar(250) default NULL,\n  `SAEAuthorRole` varchar(250) default NULL,\n  `SAEAuthorMiscellaneous` varchar(250) default NULL,\n  `SAEAuthorAttribution` varchar(250) default NULL,\n  `SAEAuthorFullName` varchar(250) default NULL,\n  `SAEAuthorAffiliation` text,\n  `SAETitle` varchar(30) default NULL,\n  `SAESubject` text,\n  `IndexTerm` text,\n  `AEAuthorName` varchar(250) default NULL,\n  `AEAuthorNumber` varchar(30) default NULL,\n  `AEAuthorTitle` varchar(250) default NULL,\n  `AEAuthorDates` varchar(250) default NULL,\n  `AEAuthorRole` varchar(250) default NULL,\n  `AEAuthorMiscellaneous` varchar(30) default NULL,\n  `AEAuthorAttribution` varchar(250) default NULL,\n  `AEAuthorFullName` varchar(250) default NULL,\n  `AEAuthorAffiliation` text,\n  `AECorporateAuthor` varchar(50) default NULL,\n  `SeriesEntryRelationship` varchar(250) default NULL,\n  `SeriesEntryTitle` varchar(250) default NULL,\n  `FileSize` varchar(10) default NULL,\n  `URI` text,\n  `fkbid` int(11) NOT NULL,\n  PRIMARY KEY  (`Id`),\n  KEY `fkbid` (`fkbid`)\n) ENGINE=MyISAM AUTO_INCREMENT=77 DEFAULT CHARSET=latin1
        
        """