import sys
import codecs
import re
import glob
from time import localtime, strftime
from citations.base.baseRecord import BaseRecord
from marctemp import Marc_template
import os


#will loop to process all the files in poetry,drama and  prose directories 
#in each file after isolating the header will create a dictionnary of the fields needed to create the MARC RECORD
#will create a log files for new author
#NOTE: this is limited to books 
#After creation of MARC record Anke will manually replace the entities not present in the lookup 

#Following a late change in specification(processing was based on the full content of folders,precision is now given that some outputs (all?)will need to be limited to some specific records:
#Twentieth-Century American Poetry in poetry folder and Twentieth-Century Drama Full-Text Database) and other should not contain,the last function (subrec())  has been added to produce these outputs by  filtering  the previous .    

#these steps were therefore necessary to create the final 14 outputs
#CREATE
#base datasets:uk and us version of drama, prose and poetry files (6 files)= ALL FILES IN THE DIRECTORIES
#combined datasetS uk and us version of combined drama, prose and poertry files (2 files)
#transition datasets=those selected in var_file: ilcs-aws_po-pr-dr, lion-aws_po-pr-dr, lion_po-pr-dr (uk and us)

#the transition datasets are then filtered to produce the final outputs

#*from marc import *
#a=marcout()
#a.marcfor()




class marcout(BaseRecord):
    #inherit baserecord (will allow us to create the template)


    def __init__(self):
    
        self.requiredFields=[] 
        self.optionalFields=['s_serial','accno','attbytes','auth_100','auths_700','copyrite','country','ctrl','desc','f_city','f_pubdate','f_publ','f_pubnote','f_series','f_subjects','f_ttl','isbn','orig_auth','recdate','s_city','s_pubdate','s_publ','s_pubnote','s_ttl','sysdate']

        
        
  
    
    def brackets(self,ttltxt):
        #replace [...] with ...
        titletext=re.sub('\[\.\.\.\]','...',ttltxt.strip())       
        inout=re.search ('^\[.+\]\s*?\[in',titletext)
        enclosin= re.search ('^\[.+\s*?\[in\]',titletext)       
        semicolumnin=re.search ('^\[.+:]',titletext)
        semicolumnout=re.search ('^\[.+]:',titletext)
        #title start and end with a brackets and contain no embeded brackets
        if titletext[0]=='[' and  titletext[-1]==']' and titletext[1:-1].find('[')==-1:
            newtitle=titletext.lstrip('[').rstrip(']')
        #closing bracket followed by '[in... OR preceded by '[in'
        elif inout!=None  or semicolumnin!=None or semicolumnout!=None or enclosin!=None:
            newtitle=titletext.lstrip('[').replace(']','',1)
        else:
            newtitle=titletext
        
        return newtitle
        
    ########################################################################
    # mangle_pubnote($)
    # deals with tagging in <pubnote>s as specced in /dc/elp/share/marc/marctags.xls .
    
    def mangle_pubnote(self, initext): 
    
        #made the change to covert situation where <exclude>.+?</exclude> is contain within another with old wil stop at first </exclude> 
        exlregex=re.compile('<exclude>(<exclude>.+?</exclude>)*.+?</exclude>',re.DOTALL)
        pubnote=re.sub(exlregex,'',initext)
        # remove EAF boilerplate text:
        pubnote1 =re.sub('<p>Page images have been included from the print version.</p>','',pubnote)
        pubnote2 =re.sub('<p>URL: http://etext\.lib\.virginia\.edu/eaf/</p>','',pubnote1)
        # remove irrelevant tags and their contents:
        pubnote3 =re.sub('<p><idno.*?>.*?</idno></p>','',pubnote2)
        pnotregex=re.compile('<notestmt>.*?</notestmt>',re.DOTALL)
        pubnote4 =re.sub(pnotregex,'',pubnote3)
        pserieregex=re.compile('<seriesst>.*?</seriesst>',re.DOTALL)
        pubnote5 =re.sub(pserieregex,'',pubnote4)   
        # remove style tags but *not* their contents:
        pubnote6=re.sub('</?hi.*?>','',pubnote5)
        pubnote7 =re.sub('</?it>','',pubnote6 )
        pubnote8 =re.sub('</?sup>','',pubnote7)
        # add space between paragraphs if they don't already have one:
        pubparegex=re.compile('</p>[\r\n]*<p>',re.DOTALL)
        paraspace= re.search(pubparegex,pubnote8)
        if paraspace !=None:
            pubnote9=re.sub(pubparegex,' ',pubnote8)  
        else:
            pubnote9=pubnote8
        # remove any remaining <p> tagging (may have r= attribs):
        rparegex=re.compile('</?p.*?>',re.DOTALL)
        pubnote10 =re.sub(rparegex,'',pubnote9)
        # remove any lurking carriage returns:
        pubnote11 =re.sub('[\r\n]','',pubnote10)
        pubnote12 =re.sub('^ +| +$','',pubnote11)
        if pubnote12 !='':
            if pubnote12[-1]!=".": 
                pubnote12=pubnote12+"."
            if len(pubnote12)>=2 and pubnote12[-2]=='.':
                pubnote12=pubnote12[:-1]
        #ADDED 
        #to add?? will remove all remaining tags and not only <list></list> and <item></item>
        #alltags=re.compile('<.*?>')
        #pubnote13=re.sub(alltags,'',pubnote12)
        pubnote13=pubnote12.replace('<list>','').replace('</list>','').replace('<item>','').replace('</item>','')
        #
        return (pubnote13)
    
    
    ########################################################################
    # strip_tagging($)
    # removes all the style tagging from a given field. For the purposes of
    # this subroutine style tagging comprises <hi>, <it>, <sup>, <p>.
    
    def strip_tagging(self,tagged): 
    
        paraph=re.compile('</?p>',re.DOTALL)   
        stripped =re.sub('</?hi.*?>','',tagged)
        stripped1 =re.sub('</?it>','',stripped)
        stripped2 =re.sub('</?sup>','',stripped1)
        stripped3 =re.sub(paraph,'',stripped2)
        return (stripped3);
    

    def marcfor(self):
        
        print "\n\nlooking for new entities in input files...please wait"
        
        headeregex=re.compile('<div0.*?<div1 type=.*?>.*?<header>.*?</header>.*?</div1>',re.DOTALL)
        idregex=re.compile('<idref>(.*?)</idref>',re.DOTALL)
        sizeregex=re.compile('<attbytes>(.*?)<\/attbytes>',re.DOTALL)
        exlregex=re.compile('<p>(The following plays.*?</list>)',re.DOTALL)
        accregex=re.compile('<acc.no>(.+?)</acc.no>',re.DOTALL)
        divregex=re.compile('<div0id>(.+?)</div0id>')
        pupbateregex=re.compile('<file>.+?<pubdate>(.+?)</pubdate>',re.DOTALL)
        sourcepubregex=re.compile('<source>.+?<pubdate>(.+?)</pubdate>',re.DOTALL)
        elecfregex=re.compile('<file>.*?<aacr2ttl>((?:(?!aacr2ttl>).)+)</aacr2ttl>',re.DOTALL)
        elecfpubregex=re.compile('<file>.*?<city>(.+?)</city>',re.DOTALL)
        subjregex=re.compile('<source>.*?<subject>(.+?)</subject>',re.DOTALL)
        srcityregex=re.compile('<source>.*?<city>(.+?)</city>',re.DOTALL)
        descregex=re.compile('<source>.*?<desc>(.+?)</desc>',re.DOTALL)
        isbnregex=re.compile('<source>.*?<isbn>(.+?)</isbn>',re.DOTALL)
        divesizeregex=re.compile('<div0size>(.+?)</div0size>')
        publecleregex=re.compile('<publ>(.+?)</publ>',re.DOTALL)
        srcpnoteregex=re.compile('<source>.*?<pubnote>(.+?)</pubnote>',re.DOTALL)
        serialregex=re.compile('<serial>(.+?)</serial>',re.DOTALL)
        srcpublregex=re.compile('<source>.*?<publ>(.+?)</publ>',re.DOTALL)
        srcserieregex=re.compile('<source>.*?<series>(.+?)</series>',re.DOTALL)
        srcserialregex=re.compile('<source>.*?<serial>(.+?)</serial>',re.DOTALL)
        filepnoteregex=re.compile('<file>.*?<pubnote>(.+?)</pubnote>.*?</file>',re.DOTALL)
        copyregex=re.compile('<copyrite>(.+?)</copyrite>')
        hostregex=re.compile('<file>.*?<series>(.+?)</series>',re.DOTALL)
        filetitlregex=re.compile('<file>.*?<aacr2ttl>((?:(?!aacr2ttl>).)+)</aacr2ttl>',re.DOTALL)
        origintitlregex=re.compile('<source>.*?<aacr2ttl>((?:(?!aacr2ttl>).)+)</aacr2ttl>',re.DOTALL)
        namevinregex=re.compile('<author>.*?<nameinv>(.+?)</nameinv>.*?</author>',re.DOTALL)
        addautregex=re.compile('<addauth>(.*?)</addauth>',re.DOTALL)
        fullautregex=re.compile('<nameinv>(.+?)</nameinv>.*?<authrole>(.+?)</authrole>',re.DOTALL)
        namregex=re.compile('<nameinv>(.+?)</nameinv>',re.DOTALL)
        
        #####################################
        #lIST OF AUTHOR TO REMOVE FROM THE US VERSION
        
        notuk=['1\$aJohnson, James Weldon,$d1871-1938.',
                '1\$aSarton, May,$d1912-1995.',
                '1\$aFrost, Robert,$d1874-1963.',
                '1\$aGinsberg, Allen,$d1926-1997.',
                '1\$aJohnson, Fenton,$d1888-1958.',
                '1\$aJohnson, Georgia Douglas Camp,$d1886-1966.',
                '1\$aLorde, Audre.',
                '1\$aMcKay, Claude,$d1890-1948.',
                '1\$aSandburg, Carl,$d1878-1967.',
                ]
        
       
      
        merr=open('newauthor.log','w')
        
        #test ouput file
        ##################################
        #.LUT
        #for test will be working with copy of the lut files
        ####################################
        marcupd={}
        #####################################
        #will be use to update marc_lut at the end of the process
        marc_lut = '/dc/lion3/data/marc/Processing/nameinv_marcauth.lut'
        marcdict={}
        marcdlkup=open(marc_lut,'rU')
        
        ##############################
        #Creating MARC authors dictinnary
        #############################
        for line in marcdlkup.xreadlines():
            mline=line.strip()
            marckv=mline.split('|')
            mardictkey=marckv[0]
            marcdict[mardictkey]='|'.join(val for val in marckv[1:])
            #if there are more than two fields(happen sometime with lc_marc), the
            # first field will become the key and subsequent fields will become an
            # anonymous array to which the value is a reference.
            # Lookup table for MARC forms of author names. This should be extracted from the <MARCform> field
            # in the DMS (may need to ask SD to do extraction as the output needs to be plain text). The lookup 
            # table should be in the form LCname|MARCform.

        dateupd={}
        #will be use to update date_lut at the end of the process
        datedict={}
        date_lut = '/dc/lion3/data/marc/utils/marcdates.lut'
        datedlup=open(date_lut,'rU')
        ##############################
        #Creating MARC dates dictinnary
        #############################
        for line in datedlup.xreadlines():
            dline=line.strip()
            datekv=dline.split('|')
            datekey=datekv[0]
            datedict[datekey]=datekv[1]
        # Lookup table for first date of MARC record creation. This will be in 
        # the form <acc.no>|YYMMDD. If a MARC record has already been created 
        # for a given LION header, the date of creation of the original MARC 
        # record should appear in this lookup table. If no match is found for 
        # the specified <acc.no>, it will be assumed that this is a new MARC
        # record; the current date will be used and will be added to the lookup
        # table, i.e. THIS FILE WILL BE RE-WRITTEN WHEN THE SCRIPT IS RUN.

        
        ####a dictionnary based on the values on thes files need to be created
        ###need to get it right :read comment aon read2hash
        # reads a delimited lookup table into a hash. If there are only
        # two fields in the lookup table, the LHS will become the key and the
        # RHS will become the value. If there are more than two fields(happen sometime with lc_marc), the
        # first field will become the key and subsequent fields will become an
        # anonymous array to which the value is a reference.
        
        #####################################################
        #list of all existing entities stored in mrcentity
        mrcentity={}
        entlist=open('/dc/lion3/data/marc/Processing/marc_entities.lut','rU')
        for line in entlist.xreadlines():
            l=line.decode('latin-1')
            entnv=l.strip('\n').split('|')
            if len(entnv)>1:
                wordent=entnv[0]
                mrcentity[wordent]=unichr(int(entnv[1]))
        
        #####################################################
        #PRE-PROCESSING:LOOKING FOR ENTITIES NOT IN LOOKUP
                
        sets=["drama","poetry","prose"]
        for unit in sets:            
            #loadpath='/dc/lion3/data/'+unit+'/master/amarctest/*.new'
            loadpath='/dc/lion3/data/'+unit+'/master/*.new'
            allhead=open(unit+".hd",'w')
            sourcepath=glob.glob(loadpath)
            #ADDED TO REMV....provide file with field: value
            #mout=open('/dc/lion3/data/'+unit+'/master/amarctest/marectest.log','a')
            #mout=open(unit+'marectest.log','a')
            #END ADDED TO REMV
            for sourcefile in sourcepath:
                #print sourcefile
                marcfile = codecs.open(sourcefile, 'r')
                marctext = marcfile.read()
                marcfile.close()
                header=headeregex.findall(marctext)
                # writting all header found in 3 temporary files: drama.hd,prose.hd,poetry.hd
                if header !=[]:
                    for hd in  header:
                        allhead.write(hd)
            allhead.close 


        #Go through the 3 header files searching for neww entities (that are not in tle entity .lut file)
        entlist=[]        
        entregex=re.compile('&.*?;')
        headpath=glob.glob('*.hd')
        #print "\n\nlooking for new entities in input files...please wait"
        for hp in headpath:
            headfile = codecs.open(hp, 'r')
            headtext = headfile.read()
            headfile.close()
            headerentities=entregex.findall(headtext)
            if headerentities !=[]:
                for ent in headerentities:
                    if  not mrcentity.has_key(ent) and ent not in entlist:
                        entlist.append(ent)
                        print ent
        if len(entlist)>0:
            entlog=open('missing_entities.log','w') 
            for ent in entlist:
                entlog.write(ent+'\n')
            print("ABOVE NEW ENTITIES FOUND PLEASE CHECK missing_entities.log AT THE END OF THE PROCESS\n") 
        #remove .hd files
        for hp in headpath:
               
            os.remove(hp)
        
        
        #we need to delete the existing log file
        #if os.path.isfile('missing_entities.log'):
            #os.remove('missing_entities.log')
        sets=["drama","poetry","prose"]
        print "Creating Marc records"
        for unit in sets:            
            loadpath='/dc/lion3/data/'+unit+'/master/*.new'
            sourcepath=glob.glob(loadpath)
            output=codecs.open('/dc/lion3/data/'+unit+'/master/Marc_with_entities.txt','a',encoding="latin-1")
            uk_output=codecs.open('/dc/lion3/data/'+unit+'/master/Ukmarcrecords.txt','a',encoding="latin-1")
            
            for sourcefile in sourcepath:
                marcfile = codecs.open(sourcefile, 'r')
                #####????????
                marctext = marcfile.read()
                #marctext = marcfile.read().decode('latin-1')
                marcfile.close()
                header=headeregex.findall(marctext)
                if header !=[]:
                    #####################
                    #Processing file header by header(each header containing the data to be use to create a MARC record)
                    #MARC records (fields/values will be stored in recdetails dictionnary
                    #####################
                   
                    for head in header:

                        recdetails={'s_serial':'','accno':'','attbytes':'','auth_100':'','auths_700':'','copyrite':'','country':'','ctrl':'',
                        'desc':'','f_city':'','f_pubdate':'','f_publ':'','f_pubnote':'','f_series':'','f_subjects':'','f_ttl':'',
                        'isbn':'','orig_auth':'','recdate':'','s_city':'','s_pubdate':'','s_publ':'','s_pubnote':'','s_ttl':'','sysdate':''}

                        #make change that span ove multiple lines
                        #save the changes in newhead
                        findexlregex=re.search(exlregex,head)
                        if findexlregex!=None:
                            exclpart=findexlregex=re.search(exlregex,head).group(1)
                            replacement='<exclude>'+ exclpart+'</exclude>'
                            newhead=re.sub(exlregex,replacement,head)
                        else:
                            newhead=head
                        # system date/time for use in the 005 field: yyyymmddhhmmss.f
                        now=strftime('%Y%m%d%H%M%S', localtime())
                        # fractions of seconds not required -- just stick a .0 on the end:
                        recdetails['sysdate'] = now +'.0'
                        #format='20090402153204'
                        findacc=re.search(accregex,newhead)
                        # accession number:
                        if findacc!=None:
                            recdetails['accno']=re.search(accregex,newhead).group(1)
                            if datedict.has_key(recdetails['accno']):
                                recdetails['recdate']=datedict[recdetails['accno']]
                            else:
                                recdetails['recdate'] = strftime('%y%m%d', localtime())
                                #the acc nbr was not in the dict it value will be the current short date
                                #acc nbr a current short date are added to dateupd dict which will used to update date lut at the end of the process
                                #(in old system not necessay in fact so update ommited)
                                dateupd[recdetails['recdate']]=recdetails['recdate']
                        else:
                            #if there is no  accession number we should exit this a required field
                            print 'No acc.no in ', newhead,"\n\n",'record to be found in',sourcefile
                            sys.exit()                         
                        findpubdate=re.search(pupbateregex,newhead)
                        if findpubdate !=None:
                           padchar ='u'
                           N = 4
                           pref_pubdate=re.search(pupbateregex,newhead).group(1)
                           for x in pref_pubdate:
                               if not x.isdigit():
                                   digitf_pubdate=pref_pubdate.replace(x,'')
                                   pref_pubdate=digitf_pubdate
                           f_pubdate=(pref_pubdate+padchar*N)[:N]
                           recdetails['f_pubdate']= f_pubdate
                        else:
                            f_pubdate = "FILE_PUBDATE_MISSING"
                            recdetails['f_pubdate']="uuuu"

                        # date of the original publication (<source><pubdate>):                    
                        findsourcepub=re.search(sourcepubregex,newhead)
                        if findsourcepub !=None:
                           padchar ='u'
                           N = 4
                           pres_pubdate= re.search(sourcepubregex,newhead).group(1)
                           #remove any non digit
                           for x in pres_pubdate:
                                if not x.isdigit():
                                    digit_pubdate=pres_pubdate.replace(x,'')
                                    pres_pubdate=digit_pubdate
                           #s_pubdate=pres_pubdate.strip('[').strip(']')
                           #if len (digit_pubdate)< 4 padd it with 'u' to the lenght of 4
                           #s_pubdate=(digit_pubdate+padchar*N)[:N]
                           s_pubdate=(pres_pubdate+padchar*N)[:N]
                           #recdetails['s_pubdate']= s_pubdate[:4]
                           recdetails['s_pubdate']= s_pubdate
                        else:
                            s_pubdate= "SOURCE_PUBDATE_MISSING" 
                            recdetails['s_pubdate'] ="uuuu"

                         # country of publication code:
                        #maybe would have been better to USE REGEX TO AVOID PB WITH SPACES WHICH WILL PREVENT DETECTION
                        if newhead.find('<country>UK</country>')!=-1:
                            country = "xxk"
                        else:
                            country = "xxu"
                        #elif newhead.find('<country>US</country>')!=-1:
                            #country = "xxu"
                        #else:
                            #country = "COUNTRY_MISSING"
                            #COUNTRY_MISSING is invalid.  If the country is not known then it should be coded as 'xxu'
                            #country = "COUNTRY_MISSING"
                        recdetails['country'] = country

                        # Title of electronic file (AACR2-compliant):
                        findfiletitle=re.search(filetitlregex,newhead)
                        if findfiletitle !=None:
                            filetitle=re.search(filetitlregex,newhead).group(1)
                            pre_f_ttl = self.strip_tagging(filetitle)
                            #= 245 No spaces or punctuation before $h...
                            punct=['.',',',';']
                            while pre_f_ttl[-1] in punct:
                                pre_f_ttl=pre_f_ttl[:-1]
                            f_ttlbase=pre_f_ttl.strip()
                            #space before  3 consecutive dots
                            f_ttlbrack=re.sub(r'([a-zA-Z0-9])(\.\.\.)',r"\1 \2",f_ttlbase)
                            #need now to remove brackets if there is 
                            f_ttl=self.brackets(f_ttlbrack)
                        else:
                            f_ttl = "FILE_TITLE_MISSING"

                        recdetails['f_ttl'] = f_ttl

                        # Place of publication of electronic file:                    
                        findelecfpub=re.search(elecfpubregex,newhead)
                        if findelecfpub !=None:
                           f_city= re.search(elecfpubregex,newhead).group(1)
                        else:
                            f_city = "FILE_CITY_MISSING"

                        recdetails['f_city'] = f_city

                        # Publisher of electronic file:
                        findelecpublisher=re.search(publecleregex,newhead)
                        if findelecpublisher !=None:
                            epublisher=re.search(publecleregex,newhead).group(1)  
                            f_publ=self.strip_tagging(epublisher) 
                        else:
                            f_publ = "FILE_PUBL_MISSING"

                        recdetails['f_publ'] = f_publ

                        # Subjects, for 20th century drama only at this point:
                        findsubj=re.search(subjregex,newhead)
                        if findsubj !=None:
                            #never end in punctuation
                            punctuation=['.',',',';','!']
                            pref_subjects=re.search(subjregex,newhead).group(1)
                            if pref_subjects[-1] in punctuation:
                                f_subjects=pref_subjects[:-1]    
                            else:
                                f_subjects=pref_subjects
                        else:
                            #f_subjects = "SUBJECTS_MISSING"
                            f_subjects =""

                        recdetails['f_subjects']=f_subjects

                        # <source> pubnote:
                        # if there's actually anything left after the mangling process, put it in the hash:
                        findsrcpnote=re.search(srcpnoteregex,newhead)
                        if findsrcpnote !=None:
                            pnote=re.search(srcpnoteregex,newhead).group(1)
                            s_pubnote=self.mangle_pubnote(pnote)
                            if  s_pubnote!="":
                                recdetails['s_pubnote']=s_pubnote


                        # serial - goes in another 500 field    check results ?????
                        findserial=re.search(serialregex,newhead)
                        if findserial !=None:
                            serial1=re.search(serialregex,newhead).group(1)
                            serial=re.sub('.*?<serial>(.+?)<\serial>.*','\1',serial1)
                            if serial[-1]!=".": 
                                serial=serial+"."
                            if serial[-2]=='.':
                                serial=serial[:-1]
                            recdetails['serial'] = serial    

                         # Title of original (AACR2-compliant):
                        findorgtitle=re.search(origintitlregex,newhead)
                        if findorgtitle !=None:
                            orgtitle=re.search(origintitlregex,newhead).group(1)
                            pre_s_ttl = self.strip_tagging(orgtitle)
                            #space before 3 consecutive dots
                            s_ttlbrack=re.sub(r'([a-zA-Z0-9])(\.\.\.)',r"\1 \2",pre_s_ttl)
                            s_ttl=self.brackets(s_ttlbrack)                            
                        else:
                            s_ttl = "SOURCE_TITLE_MISSING"

                        recdetails['s_ttl'] = s_ttl    

                        # Place of publication of original (take first <city> tag in <source>):
                        findsrcity=re.search(srcityregex,newhead)
                        if findsrcity !=None:
                            s_city=re.search(srcityregex,newhead).group(1)
                        else:
                            s_city="[S. l.]"

                        recdetails['s_city'] = s_city

                        # Publisher of original (take first <publ> tag in <source>):
                        findsrcpublish=re.search(srcpublregex,newhead)
                        if findsrcpublish !=None:
                            srcpubl=re.search(srcpublregex,newhead).group(1)
                            pre_s_publ=self.strip_tagging(srcpubl)
                            s_publ=re.sub(r'([a-zA-Z0-9])(\.\.\.)',r"\1 \2",pre_s_publ)
                        else:
                            s_publ = "[s. n.]"

                        recdetails['s_publ'] = s_publ

                        # Note field -- <series> from <source>:
                        findsrcseries=re.search(srcserieregex,newhead)
                        if findsrcseries !=None:
                            s_series=re.search(srcserieregex,newhead).group(1)
                            if s_series[-1]!=".": 
                                s_series=s_series+"."
                            if s_series[-2]=='.':
                                s_series=s_series[:-1]
                            recdetails['s_series'] = s_series     

                        # Note field -- <serial> from <source>:
                        findsrcserial=re.search(srcserialregex,newhead)
                        if findsrcserial !=None:
                            s_serial=re.search(srcserialregex,newhead).group(1)
                            if serial[-1]!=".": 
                                s_serial=s_serial+"."
                            if s_serial[-2]=='.':
                                s_serial=s_serial[:-1]
                            #recdetails['s_serial'] =s_serial
                            #ADDED 
                            recdetails['s_serial'] = self.mangle_pubnote(s_serial) 

                        # Physical description of original:
                        #we are only looking for the part containing the pagination info and has generall the format n* p.: 123 p.
                        finddesc=re.search(descregex,newhead)
                        if finddesc!=None:
                            pagination=[]
                            pre_desc=re.search(descregex,newhead).group(1)
                            new_desc=pre_desc.split(',')
                            for pg in new_desc:
                                if pg.find('p')!=-1:
                                    pagination.append(pg)
                            if pagination!=[]:
                                page=pagination[0].strip().replace('[','').replace(']','')
                                #should have a dot after p
                                if page[-1]=='.':
                                    desc=page
                                else:
                                    desc=page+'.'
                                
                            else:
                                desc=''
                            recdetails['desc'] = desc.strip()

                        # ISBN of original:
                        findisbn=re.search(isbnregex,newhead)
                        if findisbn !=None:
                            isbn = re.search(isbnregex,newhead).group(1)
                            recdetails['isbn'] = isbn    

                        # File pubnote:
                        findfilnote=re.search(filepnoteregex,newhead)
                        if findfilnote !=None:
                            filnote=re.search(filepnoteregex,newhead).group(1)
                            f_pubnote = self.mangle_pubnote(filnote)
                            recdetails['f_pubnote'] = f_pubnote

                        # Third-party copyright statement:
                        findcopyr=re.search(copyregex,newhead)
                        if findcopyr !=None:
                            copyr=re.search(copyregex,newhead).group(1)
                            copyrite = self.mangle_pubnote(copyr)
                            recdetails['copyrite'] = copyrite

                        # Host item entry (ie ILC name) -- <series> from <file>:

                        findfilserie=re.search(hostregex,newhead)
                        if findfilserie !=None:
                            f_series =re.search(hostregex,newhead).group(1)
                            recdetails['f_series'] = f_series



                        ##############################################
                        ##############################################
                        ########
                        ### Now for the author-related stuff (the tricky bit):
                        # find main author nameinvs

                        findnameinv=re.findall(namevinregex,newhead)
                        if findnameinv !=[]:
                           nameinv=findnameinv[0]
                        else:
                            nameinv = "NAMEINV_MISSING"

                        full_aauths=[]

                        if re.search('<addauth>',newhead) !=None:
                            aahd=newhead    
                            allfull_add=re.findall(addautregex,aahd)
                            if allfull_add != []:
                                full_aauths.append(allfull_add[0])
                                #print "CHECKED"
                                #print 'full_aauths\n',allfull_add[0] 
                            aahd1=re.sub(addautregex,'',aahd)

                        # if there's more than one author in <nameinv> (separated by
                        # forward-slashes) split these into an array:
                        nameinvs=[]
                        manyname= nameinv.split('/')
                        if len(manyname) >1:
                           for aname in manyname:
                               nameinvs.append(aname) 
                        else:
                            nameinvs.append(manyname[0])



                        # if there's a <marcauth primary=y>, this goes in the 100 field. We
                        # need to keep the non-MARC form of the name for the 534 field
                        # (author of original work).
                        # otherwise, the MARC form of the first <nameinv> from <author>
                        # goes in the 100 field, and the non-MARC form goes in the 534
                        # field (author of original work).
                        #marcdict=lc_marc
                        nomarc=[]
                        if nameinvs!=[]:
                            namea=nameinvs[0].strip()
                            orig_auth=namea
                            if marcdict.has_key(namea):
                                #####????????
                                auth_100=marcdict[namea].decode('latin-1')
                            else:
                                auth_100=namea
                                nomarc.append('1-No MARCform found for author ' +namea+'\n')
                                #store it here until we are able to link it to the idref of the record containing it
                                #once we will have the idref we will write it  in the log file and link idref and author name to make 
                                #it easier to make the correction 
                                #divregex=re.compile('<div0id>(.+?)</div0id>')
                                #when we will find it we will write it to the error file
                                #merr.write("No MARCform found for author"+ namea+"\n)"


                        # anything left from the <nameinv> or from <addauth>s will go
                        # into the 700 field. (Get the MARC form of each <nameinv>).
                        #this is <nameinv>not namevisns
                        auths_700=[]
                        if len(findnameinv)>1:
                            for authname in findnameinv[1:]:
                                if marcdict.has_key(authname):
                                    auths_700.append(marcdict[authname])
                                else:    
                                    auths_700.append(authname)
                                    nomarc.append("2-No MARCform found for add author "+ authname+"\n")

                        marcauths=[]
                        for f in full_aauths:
                            namrol=re.findall(fullautregex,f)
                            namonly=re.search(namregex,f)
                            if namrol !=[]:
                                #print namrol
                                ninv=namrol[0][0]
                                orol=namrol[0][1]
                                if marcdict.has_key(ninv):
                                    maut=marcdict[ninv]+'$e'+orol
                                    marcauths.append(maut)
                                else:
                                    maut= ninv +'$e'+ orol
                                    marcauths.append(maut)
                                    nomarc.append("3-No MARCform found for add author "+ninv +"\n")

                            elif namonly !=None:
                                ninv=re.search(namregex,f).group(1)
                                if marcdict.has_key(ninv):
                                    maut=marcdict[ninv]
                                    marcauths.append(maut)
                                else:
                                    maut= ninv
                                    marcauths.append(maut)
                                    nomarc.append("4-No MARCform found for add author "+ninv +"\n")
                            else:
                                print f,'is not valid'

                        if len (marcauths) > 0:
                            for mcau in marcauths:
                                #####?????????
                                auths_700.append(mcau.decode('latin-1'))


                        # need a full stop at the end of original author (before $t in 534 field):
                        if orig_auth[-1]!='.':
                           orig_auth= orig_auth+'.'
                        recdetails['orig_auth'] = orig_auth
                        recdetails['auth_100']  = auth_100
                        if len(auths_700) > 0:
                            recdetails['auths_700'] = "|".join(at7 for at7 in  auths_700)
                            

                        finddiv0id=re.search(idregex,newhead)
                        finddiv0size=re.search(sizeregex,newhead)


                        if finddiv0id !=None:
                            div0id=re.search(idregex,newhead).group(1)
                        if finddiv0size !=None :
                            #we want only the first attbyte encountered
                            div0size=re.search(sizeregex,newhead).group(1)

                        sizefound='no'
                        marcbase=[]
                        lines=newhead.split('\n')
                        #make change to lines
                        #save the changes in marcbase
                        for line in lines:
                            if line.find('</header>')!=-1:
                                idsize='\n<div0id>'+div0id+'</div0id>\n<div0size>'+div0size+'</div0size>\n</header>'
                                newline=line.replace('</header>', idsize)
                                marcbase.append(newline)
                            else:
                                marcbase.append(line)
                        
                        #in marcbase we have a single <header></header> ready to be split into field and value and be stored  in a dict 
                        # if we need some processing before extraction do it above and put the changed line in marc base
                        for newline in marcbase:
                            ##POPULATE DICTIONNARY final entries  
                            finddiv=re.search(divregex,newline)
                            if finddiv!=None:
                                recdetails['ctrl']=re.search(divregex,newline).group(1)

                            findivsize=re.search(divesizeregex,newline)
                            if findivsize!=None:
                                recdetails['attbytes']=re.search(divesizeregex,newline).group(1).strip('\r').strip('\n')
                                attbytes=recdetails['attbytes']
                               
                        if nomarc!=[]:
                            #if we have any new author write to log
                            #first write the id of the record... and then the error message
                            merr.write('Record'+recdetails['ctrl']+'\n')
                            for missing in nomarc:
                                merr.write(missing)
                            merr.write('\n\n')
                        
                        #ADDED TO REMV ....provide file with field: value
                        #for key in recdetails.keys():                        
                            #mout.write(key+': '+recdetails[key].encode('latin-1')+'\n')
                        #mout.write('\n\n')
                        #END ADDED
                        self.accno=recdetails['accno']
                        self.ctrl=recdetails['ctrl']
                        print self.accno
                        self.attbytes=recdetails['attbytes']
                        self.auth_100=recdetails['auth_100']
                        self.auths_700=recdetails['auths_700']
                        self.copyrite=recdetails['copyrite']
                        self.country=recdetails['country']                       
                        self.desc=recdetails['desc']
                        self.f_city=recdetails['f_city']
                        self.f_pubdate=recdetails['f_pubdate']
                        self.f_publ=recdetails['f_publ']
                        self.f_pubnote=recdetails['f_pubnote']
                        self.f_series=recdetails['f_series']
                        self.f_subjects=recdetails['f_subjects']
                        self.f_ttl=recdetails['f_ttl']
                        self.isbn=recdetails['isbn']
                        self.orig_auth=recdetails['orig_auth']
                        self.recdate=recdetails['recdate']
                        self.s_city=recdetails['s_city']
                        self.s_pubdate=recdetails['s_pubdate']
                        self.s_publ=recdetails['s_publ']
                        self.s_pubnote=recdetails['s_pubnote']
                        self.s_ttl=recdetails['s_ttl']
                        self.sysdate=recdetails['sysdate']
                        self.s_serial=recdetails['s_serial']
                        self.templateclass = Marc_template.Marc_template
                        #print self 
                        output.write(self.FillTemplate()+'\n\n')

                        #UK VERSION
                        #################
                        #CREATING UK VERSION(REMOVING  SOME AUTHOR)
                        for usaut in notuk:

                            self.auth_100=recdetails['auth_100'].replace(usaut,'')
                            recdetails['auth_100']=self.auth_100
                            self.auths_700=recdetails['auths_700'].replace(usaut,'')
                            recdetails['auths_700']=self.auths_700
                        uk_output.write(self.FillTemplate()+'\n\n')

                

        fnames={"drama":"dr","poetry":"po","prose":"pr"}
        baseurl="http://gateway.proquest.com/openurl?ctx_ver=Z39.88-2003&xri:pqil:res_ver=0.2&res_id=xri:$collection&rft_id=xri:lion:"
        print "\n\nCreating datasets:\n"
        for unit in sets:
            otfile = codecs.open('/dc/lion3/data/'+unit+'/master/Ukmarcrecords.txt', 'r')
            stringforrepl=otfile.read()
            ##############################################
            #this the string (whole file) before replacing the entities
            lkt=stringforrepl.decode('latin-1')
            luset=open('/dc/lion3/data/marc/Processing/marc_entities.lut','rU')
            lutest=open('/dc/lion3/data/'+unit+'/master/'+fnames[unit]+'_uk.txt','w')
            #replacing the entities
            for line in luset.xreadlines():
                lkline=line.decode('latin-1').strip('\n')
                entekv=lkline.split('|')
                if len(entekv)>1:
                    myent=entekv[0]
                    myentval=entekv[1]
                    ctext=lkt.replace(myent,unichr(int(myentval)))
                    lkt=ctext
               
            #inserting a basic/standard url line(=856)
            recordid=''
            lineforurl=ctext.split('\n')
            for uline in lineforurl:
                recurl=uline.find('=856')
                idline=uline.find('=001')
                if idline !=-1:
                    recordid=uline[6:].strip()
                    lutest.write(uline.encode('latin-1')+'\n')
                elif recurl !=-1:
                    replurl=baseurl+fnames[unit]+':'+recordid+'\n'
                    newurline=uline.replace('http://lion.chadwyck.co.uk/',replurl)
                    lutest.write(newurline.encode('latin-1'))
                else:
                    lutest.write(uline.encode('latin-1')+'\n')

            print lutest 
            lutest.close()
            otfile.close()
            luset.close()
            

            #REPLACING ENTITIES IN US VERSION (FULL VERSION)
            
            USotfile = codecs.open('/dc/lion3/data/'+unit+'/master/Marc_with_entities.txt', 'r')
            USstringforrepl=USotfile.read()
            USlkt=USstringforrepl.decode('latin-1')
            #lookup file
            USluset=open('/dc/lion3/data/marc/Processing/marc_entities.lut','rU')
            USlutest=open('/dc/lion3/data/'+unit+'/master/'+fnames[unit]+'_us.txt','w')
            
            for line in USluset.xreadlines():
                lkline=line.decode('latin-1').strip('\n')
                entekv=lkline.split('|')
                if len(entekv)>1:
                    myent=entekv[0]
                    myentval=entekv[1]
                    ctext=USlkt.replace(myent,unichr(int(myentval)))
                    USlkt=ctext
                    
            
            
            
            recordid=''
            lineforurl=ctext.split('\n')
            for uline in lineforurl:
                recurl=uline.find('=856')
                idline=uline.find('=001')
                if idline !=-1:
                    recordid=uline[6:].strip()
                    USlutest.write(uline.encode('latin-1')+'\n')
                elif recurl !=-1:
                    replurl=baseurl+fnames[unit]+':'+recordid+'\n'
                    newurline=uline.replace('http://lion.chadwyck.co.uk/',replurl)
                    USlutest.write(newurline.encode('latin-1'))
                else:
                    USlutest.write(uline.encode('latin-1')+'\n')
            
            #the values lion lion_us on line =856 must be replaced  later with the appropriate product name
            
            
            print USlutest 
            USlutest.close()
            #US VERSION
            USotfile.close()
            os.remove('/dc/lion3/data/'+unit+'/master/Marc_with_entities.txt')
            #removing the file where entities were not yet replaced
            os.remove('/dc/lion3/data/'+unit+'/master/Ukmarcrecords.txt')
            
        
        self.create_outputs()

            
            
            
            
            
                   
    def create_outputs(self):


        #As dataset type we will therefore have the following variants:
        #the uk an us version of the following will be in the same directory as the script
        #Poetry-prose-drama
        #Poetry-prose
        #Poetry- drama
        #prose-drama
        # the uk an us version   of the following will be in the respective product directory
        #Poetry.....\\mclaren\lion3\data\poetry\master\amarctest
        #Prose......\\mclaren\lion3\data\prose\master\amarctest
        #drama......\\mclaren\lion3\data\drama\master\amarctest
        ######

        ##########################################
        #CREATING MULTI SETS FILES

        ##########################################
        print "\n\nCreating combined Datasets\n\n"
        ppduk=codecs.open('po-pr-dr_uk.txt','w')
        ppdus=codecs.open('po-pr-dr_us.txt','w')
        #NOT USEFUL FOR THE TIME BEING
        """
        #will contain #Poetry-prose uk and us versions
        ppuk=codecs.open('po-pr_uk.txt','a')
        ppus=codecs.open('po-pr_us.txt','a')
        #will contain #Poetry-drama uk and us versions
        podruk=codecs.open('po-dr_uk.txt','a')
        podrus=codecs.open('po-dr_us.txt','a')
        #will contain Prose-drama uk and us versions
        prdruk=codecs.open('pr-dr_uk.txt','a')
        prdrus=codecs.open('pr-dr_us.txt','a')
        """

        #opening and reading from various USMarcVersion UKMarcVersion(Poetry-prose-drama)
        #drama
        ukdramafile = codecs.open('/dc/lion3/data/drama/master/dr_uk.txt', 'r')
        ukdramatext = ukdramafile.read().decode('latin-1')
        usdramafile = codecs.open('/dc/lion3/data/drama/master/dr_us.txt', 'r')
        usdramatext = usdramafile.read().decode('latin-1')
        #poetry
        ukpoetryfile = codecs.open('/dc/lion3/data/poetry/master/po_uk.txt', 'r')
        ukpoetrytext = ukpoetryfile.read().decode('latin-1')
        uspoetryfile = codecs.open('/dc/lion3/data/poetry/master/po_us.txt', 'r')
        uspoetrytext = uspoetryfile.read().decode('latin-1')
        #prose
        ukprosefile = codecs.open('/dc/lion3/data/prose/master/pr_uk.txt', 'r')
        ukprosetext = ukprosefile.read().decode('latin-1')
        usprosefile = codecs.open('/dc/lion3/data/prose/master/pr_us.txt', 'r')
        usprosetext = usprosefile.read().decode('latin-1')


        #writing different sources files for the output
        #Poetry-prose-drama
        ppduk.write(ukpoetrytext.encode('latin-1'))
        ppduk.write(ukprosetext.encode('latin-1'))
        ppduk.write(ukdramatext.encode('latin-1'))
        print ppduk
        ppduk.close()
         
        ppdus.write(uspoetrytext.encode('latin-1'))
        ppdus.write(usprosetext.encode('latin-1'))
        ppdus.write(usdramatext.encode('latin-1'))
        print ppdus
        ppdus.close()
        
        #NOT USEFUL FOR THE TIME BEING
        """
        #Poetry-prose
        ppuk.write(ukpoetrytext.encode('latin-1'))
        ppuk.write(ukprosetext.encode('latin-1'))
        ppuk.close()
        ppus.write(uspoetrytext.encode('latin-1'))
        ppus.write(usprosetext.encode('latin-1'))
        ppus.close()

        #Poetry- drama
        podruk.write(ukpoetrytext.encode('latin-1'))
        podruk.write(ukdramatext.encode('latin-1'))
        podruk.close()
        podrus.write(uspoetrytext.encode('latin-1'))
        podrus.write(usdramatext.encode('latin-1'))
        podrus.close

        #prose-drama
        prdruk.write(ukprosetext.encode('latin-1'))
        prdruk.write(ukdramatext.encode('latin-1'))
        prdruk.close()
        prdrus.write(usprosetext.encode('latin-1'))
        prdrus.write(usdramatext.encode('latin-1'))
        prdrus.close()
        """




        #######sys.exit()

        #file created at this stage in the local directory
        #po-pr-dr_us.txt
        #po-pr-dr_uk.txt
        #po-pr_us.txt
        #po-pr_uk.txt
        #po-dr_us.txt
        #po-dr_uk.txt
        #pr-dr_us.txt
        #pr-dr_uk.txt

        #Now having all our base source text we can take in account the values from the variable file 

        #[selection]|product| dataset type| Version type


        print "\n\nCreating outputs:\n"
        varlist=open('var_file.lut','rU')

        for line in varlist:
            if line.startswith('[*]'):
                #USandUK=[]
                #[*]|faber | Po-pr-dr | lion-ilcs
                outputvar=line.strip('[*]\n').split('|')
                product=outputvar[0]
                #faber
                dataset=outputvar[1]
                #Po-pr-dr
                #with this we should just need to add .txt to open the source file created above (may be add the path if lennot >1
                linktype=outputvar[2]
                linkval=linktype.split('-')
                #lion-ilcs....>[lion,ilcs]
                #lion...>[lion]
                #is there a function to copy a file
                diffdata=dataset.split('-')
                datlocindic=len(diffdata)
                productype=product.split('-')

                #datlocindic will allow us to detemine where the source files are located :if len()>1..location is current directory
                #else location = original directory ....the output will contain only one dataset
                #print '\n\n\n'
                #print datlocindic
                if datlocindic >1:

                    sourcedatasetUK=codecs.open(dataset+'_uk.txt','rU')
                    sourcedatasetUS=codecs.open(dataset+'_us.txt','rU')
                else:
                    if diffdata[0]=='dr':
                        sourcedatasetUK=open('/dc/lion3/data/drama/master/dr_uk.txt', 'r')
                        sourcedatasetUS=open('/dc/lion3/data/drama/master/dr_us.txt', 'r')
                        #datasetname='drama'
                    if diffdata[0]=='po':
                        #datasetname='poetry'
                        sourcedatasetUK=open('/dc/lion3/data/poetry/master/po_uk.txt', 'r')
                        sourcedatasetUS=open('/dc/lion3/data/poetry/master/po_us.txt', 'r')
                    if diffdata[0]=='pr':
                        #datasetname='prose'            
                        sourcedatasetUK=open('/dc/lion3/data/prose/master/pr_uk.txt', 'r')
                        sourcedatasetUS=open('/dc/lion3/data/prose/master/pr_us.txt', 'r')
                    
                

                if productype[0].strip()=='ilcs':
                    endusfile=open('outputs/'+product+'_'+dataset+'_US.txt','w')
                    #print endusfile
                    for line in sourcedatasetUS.xreadlines():
                        #print line
                        uline=line.decode('latin-1')
                        usurl=uline.find('=856')                    
                        if usurl ==-1:
                            endusfile.write(uline.encode('latin-1'))
                        else:

                            ilcsline=uline.replace('xri:$collection','xri:ilcs-us').replace('lion','ilcs')
                            for x in diffdata:
                                y=diffdata.index(x)
                                if uline.find(x+':')!=-1:
                                    newiclsurl=ilcsline.replace(x+':',linkval[y]+':')
                                    endusfile.write(newiclsurl.encode('latin-1'))
                    #print endusfile
                    endusfile.close()
                    
                    #sourcedatasetUS.close()

                    endukfile=open('outputs/'+product+'_'+dataset+'_UK.txt','w')
                    #print endukfile
                    for line in sourcedatasetUK.xreadlines():
                        uline=line.decode('latin-1')
                        ukurl=uline.find('=856')                    
                        if ukurl ==-1:
                            endukfile.write(uline.encode('latin-1'))
                        else:
                            ilcsline=uline.replace('xri:$collection','xri:ilcs').replace('lion','ilcs')
                            for x in diffdata:
                                y=diffdata.index(x)
                                if uline.find(x+':')!=-1:
                                    newiclsurl=ilcsline.replace(x+':',linkval[y]+':')
                                    endukfile.write(newiclsurl.encode('latin-1'))
                    #print endukfile
                    endukfile.close()
                    #sourcedatasetUK.close()



                else:

                    endusfile=open('outputs/'+product+'_'+dataset+'_US.txt','w')
                    for line in sourcedatasetUS.xreadlines():
                        uline=line.decode('latin-1')
                        usurl=uline.find('=856')                    
                        if usurl ==-1:
                            endusfile.write(uline.encode('latin-1'))
                        else:
                            newusurl=uline.replace('xri:$collection','xri:lion-us')
                            #print newusurl
                            endusfile.write(newusurl.encode('latin-1'))
                    #print endusfile
                    endusfile.close()
                    #sourcedatasetUS.close()

                    endukfile=open('outputs/'+product+'_'+dataset+'_UK.txt','w')
                    for line in sourcedatasetUK.xreadlines():
                        uline=line.decode('latin-1')
                        ukurl=uline.find('=856')                    
                        if ukurl ==-1:
                            endukfile.write(uline.encode('latin-1'))
                        else:
                            newukurl=uline.replace('xri:$collection','xri:lion')
                            #print newukurl
                            endukfile.write(newukurl.encode('latin-1'))
                    #print endukfile
                    endukfile.close()
                    #sourcedatasetUK.close()
        
        #removing source dataset files
        os.remove('po-pr-dr_uk.txt')
        os.remove('po-pr-dr_us.txt')
        os.remove('/dc/lion3/data/drama/master/dr_uk.txt')
        os.remove('/dc/lion3/data/drama/master/dr_us.txt')
        os.remove('/dc/lion3/data/poetry/master/po_uk.txt')
        os.remove('/dc/lion3/data/poetry/master/po_us.txt')
        os.remove('/dc/lion3/data/prose/master/pr_uk.txt')
        os.remove('/dc/lion3/data/prose/master/pr_us.txt')
        self.subrec()
        
        
        
        
        #Following a late change in specification(processing was based on full content of folders,precision is now given that some outputs will need to be limited to some specific records:
        #Twentieth-Century American Poetry in poetry folder and Twentieth-Century Drama Full-Text Database) and other should not contain them this function has been added to produce these outputs by  filtering  the previous .    
    def subrec(self):
        basefiles=['outputs/lion-aws_po-pr-dr_UK.txt','outputs/lion-aws_po-pr-dr_US.txt','outputs/ilcs-aws_po-pr-dr_UK.txt','outputs/ilcs-aws_po-pr-dr_US.txt']
        lpdr=['outputs/lion_po-pr-dr_US.txt','outputs/lion_po-pr-dr_UK.txt']
    
        for filnam in basefiles:
            handle=open(filnam,'r')
            marctext = handle.read()
            handle.close()
            marcrecords=marctext.split('\n\n')
            cat=filnam.replace('outputs/','').replace('-aws_po-pr-dr','').replace('.txt','')
            file1=open('outputs/'+cat+'aws.txt','w')
            file2=open('outputs/'+cat+'amp.txt','w')
            file3=open('outputs/'+cat+'tcd.txt','w')
            for rec in marcrecords:
                if rec.find('=773  0\$tAfrican Writers Series')!=-1:
                    file1.write(rec+'\n')

                if rec.find('=773  0\$tTwentieth-Century American Poetry, Second Edition')!=-1:
                    # in the link aws_poetry must become 20ampo2
                    if cat.startswith('ilcs'):
                        rec2=re.sub('aws_poetry','20ampo2',rec)
                        file2.write(rec2+'\n')
                    else:
                        file2.write(rec+'\n')          
                if rec.find('=773  0\$tTwentieth-Century Drama Full-Text Database')!=-1:
                    #in the link aws_drama should be 20drama
                    if cat.startswith('ilcs'):
                        rec2=re.sub('aws_drama','20drama',rec)
                        file3.write(rec2+'\n')
                    else:
                        file3.write(rec+'\n')
            print file1
            print file2
            print file3
        #removing transitional datasets
        os.remove('outputs/lion-aws_po-pr-dr_UK.txt')
        os.remove('outputs/lion-aws_po-pr-dr_US.txt')
        os.remove('outputs/ilcs-aws_po-pr-dr_UK.txt')
        os.remove('outputs/ilcs-aws_po-pr-dr_US.txt')
        
        
        """
        You can keep all of the files in newout2 and the following 2 files from output:
        
          lion_po-pr-dr_UK.txt
          lion_po-pr-dr_US.txt
        
        However, the following records need to be taken out of the 2 above-mentioned files:
        
        =773  0\$tAfrican Writers Series
        =773  0\$tTwentieth-Century American Poetry, Second Edition
        =773  0\$tTwentieth-Century Drama Full-Text Database

        
        """
        uspdr=open('outputs/lion_USppd.txt','w')
        ukpdr=open('outputs/lion_UKppd.txt','w')
        for fl in lpdr:
            out=[]
            hdl=open(fl,'r')
            alldb=hdl.read()
            hdl.close()
            alldbrec=alldb.split('\n\n')
            for rec in alldbrec:
                if rec.find('=773  0\$tTwentieth-Century American Poetry, Second Edition')==-1 and  rec.find('=773  0\$tAfrican Writers Series')==-1 and rec.find('=773  0\$tTwentieth-Century Drama Full-Text Database')==-1:
                    out.append(rec)
            
            if fl.endswith('US.txt'):
                for x in out:
                    uspdr.write(x+'\n')
        
            else:
                for x in out:
                    ukpdr.write(x+'\n')
        #removing transitional datasets
        os.remove('outputs/lion_po-pr-dr_US.txt')
        os.remove('outputs/lion_po-pr-dr_UK.txt')
        print uspdr
        print ukpdr
        #are replace with lion-pdr_US.txt ..lion-pdr_UK.
        print "\n\nDone...check your files"
        ###\\mclaren\cc\Bibliographic\LION_MARC\Documentation\marc_creation_2009