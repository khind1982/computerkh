import re
import csv
import sys
#use package/dsol/lib/python/citations
sys.path.append('/home/amedafe/SVN/dsol/lib/python')
import MySQLdb
from citations.base.baseRecord import* 
from citations.base import dbconnector 

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
    

    
def getrec():
    #scdbconnector = dbconnector(user='tempio', passwd='tempio', db='tempio')
    #databaseConnection = scdbconnector.MakeConnection
    databaseConnection = dbconnector.dbconnector(host="localhost", user="tempio", passwd="tempio", db="tempio").MakeConnection    
    db1 = databaseConnection()
    cu = db1.cursor() 
    cu.execute("""truncate publication """)

    repeat=0
    headear=['JOURNALID', 'FULLTEXTFLAG', 'PIOSEGMENT', 'ISSN', 'JOURNALTITLE', 'SORTJOURNALTITLE', 'PUBLSTATEMENT', 'COUNTRY', 
        'PHYSICALDESCRIPTION', 'FREQUENCY', 'INDEXCOVERAGE', 'FULLCOVERAGE', 'EXTENSIONCOVERAGE', 'STARTENDDATE', 'SUBJECT', 
        'DOCUMENTLANGUAGE', 'LCCN', 'PUBLICATIONNOTES', 'LCCALL', 'SUMMARY', 'PREVIOUSJOURNALTITLE', 'FREQUENCYFORMER', 'DEWEY', 
        'PIOESPANOL', 'PAOGENERALCOLLECTIONNUMBER', 'PAOGENERALCOLLECTIONNAME', 'FULLTEXTCOVERAGE', 'PUBLISHER', 'PAOCOLLECTION',
        'GENERALNOTES', 'JSTORCOLLECTION', 'EXTENSIONFULLTEXTCOVERAGE', 'ALTERNATIVEJOURNALTITLE', 'MUSEURL']


    execfil=open('pao.csv','w')
    dialect=csv.excel
    writer = csv.writer(execfil,dialect)
    writer.writerow ([x for x in headear])
    #print b





    record_rgx=re.compile('<document>(.*?)</document>',re.DOTALL)
    #element_name_rgx=re.compile('<element name="(.*?)">')
    op_file=open('sample_pio_pao.xml','rU')
    #read_file=op_file.read().decode('cp1252')
    
    read_file=op_file.read().decode('latin-1','xmlcharrefreplace')
    read_file=read_file.replace('&amp;','&')
    op_file.close
    allrecord=record_rgx.findall(read_file)
    for record in allrecord:
        rcd={'journalid':'', 'fulltextflag':'', 'piosegment':'', 'issn':'', 'journaltitle':'', 'sortjournaltitle':'', 'publstatement':'', 
            'country':'', 'physicaldescription':'', 'frequency':'', 'indexcoverage':'', 'fullcoverage':'', 'extensioncoverage':'', 'startenddate':'',
            'subject':'', 'documentlanguage':'', 'lccn':'', 'publicationnotes':'', 'lccall':'', 'summary':'', 'previousjournaltitle':'', 'frequencyformer':'', 
            'dewey':'', 'pioespanol':'', 'paogeneralcollectionnumber':'', 'paogeneralcollectionname':'', 'fulltextcoverage':'', 'publisher':'',
            'paocollection':'', 'generalnotes':'', 'jstorcollection':'', 'extensionfulltextcoverage':'', 'alternativejournaltitle':'', 'museurl':''}

        for field in rcd.keys():
            element_name_rgx=re.compile('<element name="'+field+'">(.*?)</element>')
            field_value=element_name_rgx.findall(record)
            if field_value and len(field_value)==1:
                rcd[field]=field_value[0]
            elif field_value and len(field_value)>1:

                rcd[field]='\n-----\n'.join(field_value)
                ###
                if len(field_value)>=repeat:
                    print field,':',repeat
                    repeat=len(field_value)
        ###import
        if rcd['previousjournaltitle']!='':
            
            qstring="""INSERT INTO publication (JOURNALID,ISSN,JOURNALTITLE,PREVIOUS_TITLES) VALUES (\"%s\",\"%s\",\"%s\",\"%s\");""" % (rcd['journalid'],rcd['issn'],rcd['journaltitle'],rcd['previousjournaltitle'])  
            cu.execute(qstring)
            
            
       