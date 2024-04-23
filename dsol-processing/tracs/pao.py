import re
import csv
import sys
#sys.path.append('/home/amedafe/SVN/dsol/lib/python')
import MySQLdb

# do repeat fields
# stop mixing types in field table

def fields_names():
    field_list=[]
    element_name_rgx=re.compile('<element name="(.*?)">')
    op_file=open('sample_pio_pao.xml','rU')
    read_file=op_file.read().decode('cp1252')
    op_file.close
    allfield=element_name_rgx.findall(read_file)
    for field in allfield:
        if field not in field_list:
            field_list.append(field)
    for x in field_list:
        print x
    print field_list
    
    

def outputfields():
    fieldnames = {
                'Journal ID': [Mapper.journalid, ()],
                'Full Text Flag': 'fulltextflag',
                'PIO Segment': 'piosegment',
                'ISSN': 'issn',
                'Journal Title': 'journaltitle',
                'Sort Journal Title': 'sortjournaltitle',
                'Publ Statement': 'publstatement', 
		'Country': 'country',
		'Physical Description': 'physicaldescription',
		'Frequency': 'frequency',
		'Index Coverage': 'indexcoverage',
		'Full Coverage': 'fullcoverage',
		'Extension Coverage': 'extensioncoverage',
		'Start End Date': 'startenddate',
		'Subject': 'subjecteng',
		'Document Language': 'documentlanguage',
		'LCCN': 'lccn',
		'Publication Notes': 'publicationnotes',
		'LCCall': 'lccall',
		'Summary': 'summary',
		'Previous Journal Title': 'previousjournaltitle',
		'Frequency Former': 'frequencyformer', 
		'Dewey': 'dewey', 
		'PIO Espanol': 'pioespanol',
		'PAO General Collection Number': 'paogeneralcollectionnumber',
		'PAO General Collection Name': 'paogeneralcollectionname',
		'Full Text Coverage': 'fulltextcoverage',
		'Publisher': [Mapper.publisher, ()],
                'PAO Collection': 'paocollection',
                'General Notes': 'generalnotes',
                'JSTOR Collection': 'jstorcollection',
                'Extension Full Text Coverage': 'extensionfulltextcoverage',
                'Alternative Journal Title': 'alternativejournaltitle',
                'Muse URL': 'museurl',
                'FT Dig Notes': 'ftdignotes',
                'Primary Source Type': [Mapper.sourcetype, ()],
                'Block From Publication Search': [Mapper.default, ("N")],
                'Article Translation': [Mapper.default, ("Y")],
                'Pub Search Alert Flag': [Mapper.default, ("N")],
                'Doc Usage Royalties': [Mapper.default, ("Y")],
                'Pub Rights': [Mapper.pubrights, ()],
		'Other Publisher': 'publisher',
		'City': [Mapper.donothing, ()]
                }
    # otherpublisher? city?
    # drop foreign subjects
    fieldorder = [
                'Journal Title',
                'Sort Journal Title',
                'Alternative Journal Title',
                'Primary Source Type',
                'Block From Publication Search',
                'Article Translation',
                'Pub Search Alert Flag',
                'Doc Usage Royalties',
                'Pub Rights',
		'Previous Journal Title',
		'Frequency Former', 
                'Full Text Flag',
		'Index Coverage',
		'Full Text Coverage',
		'Full Coverage',
		'Start End Date',
                'Extension Full Text Coverage',
		'Subject',
		'Physical Description',
                'Publ Statement', 
		'Publisher',
		'Other Publisher',
		'City',
		'Country',
		'Publication Notes',
		'Summary',
                'General Notes',
                'ISSN',
                'Journal ID',
		'Document Language',
                'PIO Segment',
		'Frequency',
		'LCCN',
		'LCCall',
		'Dewey', 
		'PIO Espanol',
		'PAO General Collection Number',
		'PAO General Collection Name',
                'PAO Collection',
                'JSTOR Collection',
                'Muse URL',
		'Extension Coverage',
                'FT Dig Notes'                
                ]
                
    return fieldnames, fieldorder


class Mapper:

    def __init__(self):
        self.fieldnames, self.fieldorder = outputfields()
        self.getsourcetypes()
        
    def mapdataset(self):

        record_rgx=re.compile('<document>(.*?)</document>',re.DOTALL)
        journalid_rgx = re.compile('<element name="journalid">(.*?)</element>')
        #element_name_rgx=re.compile('<element name="(.*?)">')
        op_file=open('pio_pubs_with_subjects.xml','rU')
        read_file=op_file.read().decode('cp1252')
        read_file=read_file.replace('&amp;','&')
        op_file.close()
        allrecord=record_rgx.findall(read_file)
        for record in allrecord:
            self.piorec = record
            self.tracsrec = TRACSRecord(self.fieldorder)
            self.currentjournalid = journalid_rgx.search(record).group(1)
        
            for field in self.fieldorder:
                if type(self.fieldnames[field]) == str:
                    element_name_rgx=re.compile('<element name="'+self.fieldnames[field]+'">(.*?)</element>')
                    field_value=element_name_rgx.findall(record)
                    if field_value and len(field_value)>1:
                        field_value=['\n-----\n'.join(field_value)]
                    if field_value:
                        self.tracsrec.setfield(field, field_value[0])
                else:
                    self.tracsrec.setfield(field, self.fieldnames[field][0](self, *self.fieldnames[field][1]))

            yield self.tracsrec
            
    def getsourcetypes(self, sourcetypefile="piosourcetypes.txt"):
        self.sourcetypes = {}
        srcre = re.compile("^(.*?)\t(.*?)$", re.M)
        with open(sourcetypefile, "r") as srcfile:
            for line in srcfile:
                match = srcre.search(line)
                if match != None:
                    self.sourcetypes[match.group(1)] = match.group(2)
                    
    
    def donothing(self):
        return ''
        
    def default(self, value):
        return value
        
    def publisher(self):
        return ''
    
    def sourcetype(self):
        if self.currentjournalid in self.sourcetypes:
            return self.sourcetypes[self.currentjournalid]
        else:
            print "No entry in source type lookup for jid " + self.currentjournalid
            return ''
        
    def journalid(self):
        return ''.join(['PIO', self.currentjournalid])
    
    def pubrights(self):
        ftflag = re.search('<element name="fulltextflag">(.*?)</element>', self.piorec).group(1)
        if ftflag == "Y":
            return "Abstract|Text|Image|ThumbInlineImage|FullInlineImage|PinkyInlineImage"
        else:
            return "Abstract"

def piototracs():
    
    fieldnames, fieldorder = outputfields()
    
    execfil=open('pao2.csv','w')
    dialect=csv.excel
    writer = csv.writer(execfil,dialect)
    writer.writerow ([field for field in fieldorder])

    mapper = Mapper()
    for tracsrec in mapper.mapdataset():
        writer.writerow([tracsrec[field].encode('cp1252') for field in fieldorder])
    
    execfil.close()
            
def getrec():

    repeat=0
    #headear=['JOURNALID', 'FULLTEXTFLAG', 'PIOSEGMENT', 'ISSN', 'JOURNALTITLE', 'SORTJOURNALTITLE', 'PUBLSTATEMENT', 'COUNTRY', 
    #    'PHYSICALDESCRIPTION', 'FREQUENCY', 'INDEXCOVERAGE', 'FULLCOVERAGE', 'EXTENSIONCOVERAGE', 'STARTENDDATE', 'SUBJECT', 
    #    'DOCUMENTLANGUAGE', 'LCCN', 'PUBLICATIONNOTES', 'LCCALL', 'SUMMARY', 'PREVIOUSJOURNALTITLE', 'FREQUENCYFORMER', 'DEWEY', 
    #    'PIOESPANOL', 'PAOGENERALCOLLECTIONNUMBER', 'PAOGENERALCOLLECTIONNAME', 'FULLTEXTCOVERAGE', 'PUBLISHER', 'PAOCOLLECTION',
    #    'GENERALNOTES', 'JSTORCOLLECTION', 'EXTENSIONFULLTEXTCOVERAGE', 'ALTERNATIVEJOURNALTITLE', 'MUSEURL']

    fieldnames, fieldorder = outputfields()

    execfil=open('pao.csv','w')
    dialect=csv.excel
    writer = csv.writer(execfil,dialect)
    #writer.writerow ([x for x in headear])
    writer.writerow ([fieldnames[field] for field in fieldorder])
    #print b




    record_rgx=re.compile('<document>(.*?)</document>',re.DOTALL)
    #element_name_rgx=re.compile('<element name="(.*?)">')
    op_file=open('pio_pubs_with_subjects.xml','rU')
    read_file=op_file.read().decode('cp1252')
    read_file=read_file.replace('&amp;','&')
    op_file.close
    allrecord=record_rgx.findall(read_file)
    for record in allrecord:
        #rcd={'journaltitle':'', 'sortjournaltitle':'','journalid':'', 'fulltextflag':'', 'piosegment':'', 'issn':'',  'publstatement':'', 
        #    'country':'', 'physicaldescription':'', 'frequency':'', 'indexcoverage':'', 'fullcoverage':'', 'extensioncoverage':'', 'startenddate':'',
        #    'subject':'', 'documentlanguage':'', 'lccn':'', 'publicationnotes':'', 'lccall':'', 'summary':'', 'previousjournaltitle':'', 'frequencyformer':'', 
        #    'dewey':'', 'pioespanol':'', 'paogeneralcollectionnumber':'', 'paogeneralcollectionname':'', 'fulltextcoverage':'', 'publisher':'',
        #    'paocollection':'', 'generalnotes':'', 'jstorcollection':'', 'extensionfulltextcoverage':'', 'alternativejournaltitle':'', 'museurl':'',
        #    'ftdignotes': ''}

        tracsrec = TRACSRecord()
        
        for field in fieldorder:
            if type(fieldnames[field]) == StringType:
                element_name_rgx=re.compile('<element name="'+field+'">(.*?)</element>')
                field_value=element_name_rgx.findall(record)
                #if field_value and len(field_value)==1:
                #    rcd[field]=field_value[0]
                if field_value and len(field_value)>1:

                    field_value=['\n-----\n'.join(field_value)]
                if field_value:
                    tracsrec.setfield(field, field_value[0])
            else:
                getattr(tracsrec, field)()
        #for field in rcd.keys():
        #    element_name_rgx=re.compile('<element name="'+field+'">(.*?)</element>')
        #    field_value=element_name_rgx.findall(record)
        #    if field_value and len(field_value)==1:
        #        rcd[field]=field_value[0]
        #    elif field_value and len(field_value)>1:

        #        rcd[field]='\n-----\n'.join(field_value)
        #        ###
        #        if len(field_value)>=repeat:
        #            print field,':',repeat
        #            repeat=len(field_value)

        writer.writerow([rcd[field].encode('cp1252') for field in fieldorder])
        
        #writer.writerow ([(rcd['journalid']).encode('cp1252'), (rcd['fulltextflag']).encode('cp1252'), (rcd['piosegment']).encode('cp1252'), 
        #(rcd['issn']).encode('cp1252'), (rcd['journaltitle']).encode('cp1252'), (rcd['sortjournaltitle']).encode('cp1252'), (rcd['publstatement']).encode('cp1252'),
        #(rcd['country']).encode('cp1252'), (rcd['physicaldescription']).encode('cp1252'), (rcd['frequency']).encode('cp1252'), 
        #(rcd['indexcoverage']).encode('cp1252'), (rcd['fullcoverage']).encode('cp1252'), (rcd['extensioncoverage']).encode('cp1252'), 
        #(rcd['startenddate']).encode('cp1252'), (rcd['subject']).encode('cp1252'), (rcd['documentlanguage']).encode('cp1252'), 
        #(rcd['lccn']).encode('cp1252'), (rcd['publicationnotes']).encode('cp1252'), (rcd['lccall']).encode('cp1252'), (rcd['summary']).encode('cp1252'), 
        #(rcd['previousjournaltitle']).encode('cp1252'), (rcd['frequencyformer']).encode('cp1252'), (rcd['dewey']).encode('cp1252'), 
        #(rcd['pioespanol']).encode('cp1252'), (rcd['paogeneralcollectionnumber']).encode('cp1252'), (rcd['paogeneralcollectionname']).encode('cp1252'), 
        #(rcd['fulltextcoverage']).encode('cp1252'), (rcd['publisher']).encode('cp1252'), (rcd['paocollection']).encode('cp1252'),
        #(rcd['generalnotes']).encode('cp1252'), (rcd['jstorcollection']).encode('cp1252'), (rcd['extensionfulltextcoverage']).encode('cp1252'), 
        #(rcd['alternativejournaltitle']).encode('cp1252'), (rcd['museurl']).encode('cp1252')])   
        
        
class TRACSRecord(dict):

    def __init__(self, fieldnames):
        for fieldname in fieldnames:
            self[fieldname] = ''
        
    def setfield(self, fieldname, value):
        if fieldname not in self:
            print fieldname + " not in master field list"
        self[fieldname] = value
  
"""  
  
def populate():
    scdbconnector = dbconnector(user='tempio', passwd='tempio', db='tempio')
    databaseConnection = scdbconnector.MakeConnection
    db1 = databaseConnection()
    cu = db1.cursor() 
    
    
    record_rgx=re.compile('<document>(.*?)</document>',re.DOTALL)
    #element_name_rgx=re.compile('<element name="(.*?)">')
    op_file=open('sample_pio_pao.xml','rU')
    read_file=op_file.read().decode('cp1252')
    op_file.close
    allrecord=record_rgx.findall(read_file)
    for record in allrecord:

"""    
