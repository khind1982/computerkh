
import re, codecs, os
import MySQLdb
import copy
import warnings

from citations.base.baseRecord import BaseRecord, BaseRecordSet
from citations.base.dbconnector import dbconnector
from citations.jjson.templates import jj_record_template
from citations.jjson import jjlookups

#jjdbconnector = dbconnector(upd='jjson')
jjdbconnector = dbconnector(user='jjson', passwd='jjson', db='jjson', host="localhost")
databaseConnection = jjdbconnector.MakeConnection

# REGULAR EXPRESSIONS
linere = re.compile('^#(...)(.)(.*)$')
# for breaking up lines of original data
subtagre = re.compile('\$.')
# separate out subtags in original data
zre = re.compile('\|z')
flagre = re.compile('(?<=[a-z])([a-z])')
namere = re.compile('[345]..')
# tags in the 3-500s are all name tags and follow certain rules
ocrstripre = re.compile('</?w[^>]*>')
# don't want tags from ocr files
#shelfre = re.compile('^([^\d]*)((box|vol\.)? ([\d-]*))? \((\d*)(.*)\)')
shelfbracketre = re.compile('\((\d*)(.*)\)')
shelfboxre = re.compile('([Bb]ox|vol\.|) (\d[-\d]*)(.*)$')
# divide up shelfmarks to generate browse and sort formats

#mainlinere = re.compile('^#((1|0)00) (.*)$')

# SETTINGS
ocrdirectory = '/dc/jjohnson/handover/ocr'

"""
INPUTS:
a catalogue citation file (convert to unix format first)
a file which maps shelfmark (#950) to collection id
a file which maps  record id to image id
all the ocr full text files (location is ocrdirectory specified above)

The following lookups must all be up to date (all stored in jjlookups.py):
a list of tags mapped to search fields
a list of tags/subtags mapped to display instructions
a list of tags mapping number to xml name
a list of category code mappings
"""

"""
Remember to test output XML for well-formedness before handover
"""


class JJRecordSet(BaseRecordSet):

    def __init__(self, rawtext=None):

        self.databaseConnection = databaseConnection
        self.recordclass = JJRecord
        self.rawtext = rawtext
        self.tablename = "records"
        self.handoverset = []
        self.taglist = {}
        self.collections = {}
        self.imageids = {}
        self.ocrfiles = {}
        self.somhierarchies = {}
        self.fieldnames = ["recid", "category"]
    
    def populatefromraw(self):

        recdict = {}
        xmlnamelog = open('xmlnames.log', 'w')
        xmlnamelog.close()
        print "Creating xmlnames.log... (for missing entries in tagnumber / xml name lookup)"
        # expect rawtext to be a string
        rawlines = self.rawtext.split('\n')
        record = []
        for line in rawlines:
            if linere.search(line) != None:
                linematch = linere.search(line)
                if linematch.group(1) == '000':
                    if record != []:
                        #self.append(JJRecord(record))
                        recdict[recid] = record
                    recid = linematch.group(3)
                    record = [line]
                else:
                    record.append(line)
        recdict[recid] = record
        #self.append(JJRecord(record))
        for record in recdict.values():
            self.append(JJRecord(record))
        for record in self:
            record.populatefromlines()

    def fullpopulatefromdb(self):
    # Constructs a full record set from database contents
    # Adds in collection info, image ids and full text files using various lookups
    # Creates lookups mapping record to tags and tag to subtags to make it easier to identify
    # what each record actually contains.

        # Get all the subtags out
        # Also create a lookup so for any tag we can easily identify which subtags it has
        allsubtags = SubtagSet()
        allsubtags.freesearch("""SELECT * FROM subtags;""")
        self.subtaglup = {}
        for subtag in allsubtags:
            if not self.subtaglup.has_key(subtag.tag):
                self.subtaglup[subtag.tag] = []
            self.subtaglup[subtag.tag].append(subtag)
        
        # Get the tags and create a lookup mapping record to tags it has
        alltags = RecordTagSet()
        alltags.freesearch("""SELECT * FROM recordtags;""")
        self.taglup = {}
        for tag in alltags:
            if not self.taglup.has_key(tag.record):
                self.taglup[tag.record] = []
            self.taglup[tag.record].append(tag)
        
        
        # Assemble lookups of other info that will be needed for the records
        # i.e. collection info (keyed by shelfmark), image ids (keyed by record id), ocr files (keyed by image id) 
        self.getcollections()
        self.getimageids()
        self.findocrfiles()
        
        # get the records
        self.freesearch("""SELECT * FROM records;""")

        # insert collection, image and full text info into records
        # attach subtags to tags and tags to records using lookups (is this approach sensible?)
        colllog = open('jj_missing_collections.log', 'w')
        for rec in self:
            try:
                rec.collection = self.collections[rec.shelfmark]
            except KeyError:
                colllog.write("No collection: " + rec.shelfmark + "\n")
#            rec.getcollection()
#            rec.content.populatefromdb(record=rec.recid)
            try:
                rec.imageid, rec.mountid = self.imageids[rec.recid]
            except KeyError:
                rec.imageid = ''
                rec.mountid = ''
#                print "No imageid info: " + rec.recid
            rec.getfulltext(self.ocrfiles)
            if self.taglup.has_key(rec.recid):
                for tag in self.taglup[rec.recid]:
                    rec.content.append(tag)
            for tag in rec.content:
#                tag.subtags.populatefromdb(tag=tag.tagid)
#                print tag.tagid
                if self.subtaglup.has_key(tag.tagid):
                    for subtag in self.subtaglup[tag.tagid]:
                        tag.subtags.append(subtag)
        colllog.close()

        # put display attributes in (does this step belong here? It's for xml handover specifically)
        self.insertdisplayinfo()
        for rec in self:
            for tag in rec.content:
                # make a tag to subtags lookup that sits at tag object level; why? is it really
                # necessary to have this and the recordset level one (self.subtaglup)? and if so, why not
                # just get the info from self.subtaglup? was probably done in a rush
                tag.makesubtagdict()
                # apply rules to set author name display attributes. Again, for xml handover only.
                tag.setauthdisplay()
                tag.settowndisplay()
            
        
    def generaterecords(self):
    
        db = self.databaseConnection()
        cu = db.cursor()
        
        # compile lookups; hangover from old fullpopulatefromdb approach, so may be awkward way to do it
        # or may not be; consider when more time
        self.getcollections()
        self.getimageids()
        self.findocrfiles()
        
        # ways of mapping records to tags and tags to subtags in simple lookups so you don't
        # have to investigate the objects every time
        # (the way this is done is another hangover from fullpopulatefromdb)
        self.subtaglup = {}
        self.taglup = {}
        
        displup = jjlookups.getdisplayinfo()
        self.somhierarchies = jjlookups.getsomhierarchies()

        colllog = open('jj_missing_collections.log', 'w')

        cu.execute("""SELECT recid FROM records;""")
        recidtuple = cu.fetchall()
        reccount = 0
        for row in recidtuple:
            currentrecid = row[0]
            reccount += 1
            print "record " + str(reccount) + ':'
            print currentrecid
            self.freesearch("""SELECT * FROM records WHERE recid = '%s';""" % currentrecid)
#            self.freesearch_cu(cu, """SELECT * FROM records WHERE recid = '%s';""" % currentrecid)
            self[0].content.freesearch("""SELECT * FROM recordtags WHERE record = '%s';""" % currentrecid)
#            self[0].content.freesearch_cu(cu, """SELECT * FROM recordtags WHERE record = '%s';""" % currentrecid)
            for tag in self[0].content:
                tag.subtags.freesearch("""SELECT * FROM subtags WHERE tag = '%s';""" % tag.tagid)
#                tag.subtags.freesearch_cu(cu, """SELECT * FROM subtags WHERE tag = '%s';""" % tag.tagid)
                
                # now we have everything out of the database add this record's details to the records/tags/subtags lookups
                for subtag in tag.subtags:
                    if not self.subtaglup.has_key(subtag.tag):
                        self.subtaglup[subtag.tag] = []
                    self.subtaglup[subtag.tag].append(subtag)
                if not self.taglup.has_key(tag.record):
                    self.taglup[tag.record] = []
                self.taglup[tag.record].append(tag)
                
            # get collection info from the lookup on recordset
            try:
                self[0].collection = self.collections[self[0].recid]
            except KeyError:
                colllog.write("No collection: " + self[0].recid + "\n")
#            rec.getcollection()
#            rec.content.populatefromdb(record=rec.recid)
#            try:
#                self[0].imageid, self[0].mountid = self.imageids[self[0].recid]
#            except KeyError:
#                self[0].imageid = ''
#                self[0].mountid = ''
#                print "No imageid info: " + rec.recid
            #self[0].getfulltext(self.ocrfiles)
            
            self[0].insertdisplayinfo(displup)
       
            #taken from fullpopulatefrom db; do this bit better when poss:
            for tag in self[0].content:
                tag.makesubtagdict()
                tag.setauthdisplay()
                tag.settowndisplay()
                
            for rec in self.generatehandover():
                yield rec
            
            del self[0]
            self.taglup = {}
            self.subtaglup = {}
        
    
    def getcollections(self):
    
        db = self.databaseConnection()
        cu = db.cursor()
        
        cu.execute("""SELECT * FROM collections;""")
        for row in cu.fetchall():
            self.collections[row[0]] = row[1]
        
    def getimageids(self):

        db = databaseConnection()
        cu = db.cursor()

        cu.execute("""SELECT * FROM imageids;""")
        for row in cu.fetchall():
            self.imageids[row[0]] = [row[1], row[2]]
            
    def insertdisplayinfo(self):
    
        displup = jjlookups.getdisplayinfo()
        
        for rec in self:
            for tag in rec.content:
                if displup.has_key(tag.tagname):
                    tag.display = displup[tag.tagname]
                for subtag in tag.subtags:
                    fullsubtag = tag.tagname + subtag.subname
                    if displup.has_key(fullsubtag):
                        subtag.display = displup[fullsubtag]
                        
    def findocrfiles(self):
    
        self.ocrfiles = {}
#        print "got here 0"
        ocrcollections = os.listdir(ocrdirectory)
        for coll in ocrcollections:
            pathsofar = '/'.join([ocrdirectory, coll])
            if os.path.isdir(pathsofar) == True:
#                print "got here 1"
                ocrrecords = os.listdir(pathsofar)
                for rec in ocrrecords:
                    pathsofar = '/'.join([ocrdirectory, coll, rec])
                    if os.path.isdir(pathsofar) == True:
#                        print "got here 2"
                        ocrfilelist = os.listdir(pathsofar)
                        for ocrfile in ocrfilelist:
                            if ocrfile[:7] == 'johnson':
#                                print "got here 3"
                                imageid = ocrfile[:13]
                                if not self.ocrfiles.has_key(imageid):
                                    self.ocrfiles[imageid] = []
                                self.ocrfiles[imageid].append('/'.join([ocrdirectory, coll, rec, ocrfile]))
                        
        """
        self.ocrfiles = {}
        ocrfilelist = os.listdir(ocrdirectory)
        for ocrfile in ocrfilelist:
            imageid = ocrfile[:13]
            if not self.ocrfiles.has_key(imageid):
                self.ocrfiles[imageid] = []
            self.ocrfiles[imageid].append(ocrfile)
        """

    def populatedb(self):

        db = self.databaseConnection()
        cu = db.cursor()
        
        cu.execute("""SELECT tagid FROM recordtags ORDER BY tagid DESC LIMIT 1;""")
        tagidgot = cu.fetchall()
        if tagidgot == ():
            tagcounter = 0
        else:
            tagcounter = int(tagidgot[0][0])
        
        for rec in self:
            #replace 
            rec.InsertIntoDB_new()
            for tag in rec.content:
                tagcounter += 1
                tag.tagid = tagcounter
                tag.InsertIntoDB_new()
                for subtag in tag.subtags:
                    subtag.tag = tag.tagid
                    subtag.InsertIntoDB_new()
                                        
    def generatehandover(self):
    # function to construct output XML, assigning tags to search, display, summary of matches sections etc.
    # in some cases different copies of the same tag need putting in different places
    # sometimes these tags need different attributes depending on where they are
    # and sometimes we need to pick the best available tag for a data field
    # so it gets quite complicated.
    # It also empties the list of records to free memory
        
        # import lookups to tell us which tags should be searched and which only displayed
        srchlup = jjlookups.getsearchmappings()
        
#        self.handoverset = JJRecordSet()
        
        idstripre = re.compile('[:/$]')
        
        # set up list for checking whether a tag belongs in the summary of matches
        somtags = {
                    '100': '',
                    '101': '',    # 100 and 101 are concatenated to make category later
                    '510': '',    #engraver_lithographer - do want this
                    '240': ''    #first_line
                    #'284': '',    # don't want event_venue any longer as we already have place
                    #'434': '',    # town also superseded by place
                    #'437': '',    # products only applies to advertising and now superseded
                    #'950': ''
                    }
                    
        # set up list of tags for which we need to reformat date
        datetags = { '285': '', '290': '', '689': '', '690': '', '691': '' }
        # set up report file for problems with date indexable forms
        dateerr = open('dates_without_indexable_form.log', 'a')
        
        # prepare lookup for category codes
        # these break down supplied codes, which refer to a combination of descriptors, into one code for each descriptor
        catcodes = jjlookups.getcatcodes()
        
#        catcodere = re.compile('[^|]{2}')
        catcodere = re.compile("|".join(map(re.escape, catcodes.keys( ))))
        
        physcatre = re.compile('(Single Sheet|Folded Sheet|Leaflet|Booklet|Book)$', re.I)

#        reccount = 0
        for rec in self:

#            reccount += 1
#            print "Record " + str(reccount) + "..."
            
            
            
            # set up the various attributes on rec that are only relevant to handover
            rec.search = {'subject_keyword': RecordTagSet(), 'place_keyword': RecordTagSet(), 'doctype_keyword': RecordTagSet()}
            rec.search['doctype_keyword'].append(RecordTag(xmlname = 'category', content = rec.category))
            rec.allegroid = rec.recid
            rec.recid = idstripre.sub('', rec.recid)
            rec.display = RecordTagSet()
            rec.namesearch = {'main': RecordTagSet(), 'other': RecordTagSet()}
                    
            rec.tagdict = {}
            
            # We run through the tags a couple of times, once before taking copies for the som and once after
            # This is the 'before' step
            # Make any changes to tags here that need to be carried over to the copies taken for the som
            # Leave any changes that must not be carried over to the som for the later step
            for tag in rec.content:
            
                # work through subtags gathering info and reformatting where necessary
                for subtag in tag.subtags:
                    # reformat dates
                    if datetags.has_key(tag.tagname):
                        if subtag.subname == '$i':
                            tag.startdate, tag.enddate, tag.approx = datetransform(subtag.content)
                    # get search fields that are in subtags rather than tags
                    # need to make sure these don't get duplicated later when all tags/subtags are output
                    # don't put entertainment genre in subject search any more 18/02/09
                    #if tag.tagname == '282':
                    #    if subtag.subname == '$g' or subtag.subname == '$o':
                    #        rec.search['subject_keyword'].append(RecordTag(xmlname=subtag.xmlname, content=subtag.content, display='none'))
                    if subtag.subname == '$x':
                        if namere.match(tag.tagname) != None:
                            rec.search['place_keyword'].append(RecordTag(xmlname=subtag.xmlname, content=subtag.content, display='none'))
                    elif subtag.subname == '$t':
                        if namere.match(tag.tagname) != None:
                            rec.search['place_keyword'].append(RecordTag(xmlname=subtag.xmlname, content=subtag.content, display='none'))
                    # crime and sentence
                    if tag.tagname == '460':
                        if subtag.subname == '$m':
                            rec.search['crime_keyword'] = [RecordTag(xmlname=subtag.xmlname, content=subtag.content, display='none')]
                        elif subtag.subname == '$s':
                            rec.search['sentence_keyword'] = [RecordTag(xmlname=subtag.xmlname, content=subtag.content, display='none')]

                if tag.tagname == '600':
                    if physcatre.match(tag.content) == None:
                        tag.physcatother = 'y'
                
                # make a dictionary of all tags in record
                if not rec.tagdict.has_key(tag.tagname):
                    rec.tagdict[tag.tagname] = []
                rec.tagdict[tag.tagname].append(tag)
                
            # reformat flag-type fields
            if rec.tagdict.has_key('095'):
                rec.tagdict['095'][0].content = flagre.sub('|\\1', rec.tagdict['095'][0].content)
            if rec.tagdict.has_key('091'):
                catflag = rec.tagdict['091'][0].content[0]
                rec.tagdict['091'][0].content = flagre.sub('|' + catflag + '\\1', rec.tagdict['091'][0].content)[2:]
                rec.tagdict['091'][0].content = catcodere.sub(lambda srch: catcodes[srch.group(0)], rec.tagdict['091'][0].content)
            
            rec.som = {}
            # for some of the som fields we need to use whichever of the available tags comes highest in a specified priority order
            rec.som['som_author'] = findprimaryfield(rec.tagdict, self.somhierarchies[rec.collection]['nameprior'])
#            dateerr.write(handoverrec.som['author'])
            rec.som['som_title'] = findprimaryfield(rec.tagdict, self.somhierarchies[rec.collection]['titleprior'])
            #rec.som['som_process'] = findprimaryfield(rec.tagdict, procprior)
            rec.som['som_image_subject'] = findprimaryfield(rec.tagdict, self.somhierarchies[rec.collection]['imgsubjprior'])
            rec.som['som_place'] = findprimaryfield(rec.tagdict, self.somhierarchies[rec.collection]['placeprior'])
            prodcheck = findprimaryfield(rec.tagdict, self.somhierarchies[rec.collection]['prodprior'])
            if prodcheck != None:
                rec.som['som_product'] = prodcheck
            
            # printing process needs yet another special rule:
            if rec.tagdict.has_key('680'):
                if rec.tagdict.has_key('681'):
                    rec.som['som_process'] = RecordTag(xmlname='printing_processes', content=', '.join([rec.tagdict['680'][0].content, rec.tagdict['681'][0].content]))
                else:
                    rec.som['som_process'] = rec.tagdict['680'][0]
            elif rec.tagdict.has_key('681'):
                rec.som['som_process'] = rec.tagdict['681'][0]
            elif rec.tagdict.has_key('095'):
                rec.som['som_process'] = rec.tagdict['095'][0]
            
            
            # get main date for som and put sort attribute on it for search fields
            maindate = findprimaryfield(rec.tagdict, self.somhierarchies[rec.collection]['dateprior'])
            if maindate == None:
                maindate = RecordTag(xmlname = 'nodate', tagname = 'nodate')
                maindate.sortatt = 'yes'
                maindate.approx = 'false'
                maindate.startdate = '99999999'
                maindate.enddate = '00000000'
                maindate.content = ''
                rec.tagdict['nodate'] = [maindate]
            else:
                rec.tagdict[maindate.tagname][0].sortatt = 'yes'
            rec.som['som_date'] = maindate
            
            rec.som['som_collection'] = RecordTag(xmlname = 'collection', content = rec.collection)
            rec.som['som_category'] = RecordTag(xmlname = 'category', content = rec.category)
            
            rec.som['som_shelfmarks'] = []
            for shelf in rec.tagdict['950']:
                rec.som['som_shelfmarks'].append(copy.deepcopy(shelf))

            taglist = []
            for tagset in rec.tagdict.values():
                taglist.extend(tagset)
            
            # Here's the second run-through of the tags
            # Now copies have been taken for the som you can do anything you like to these tags
            # without knock-on effects elsewhere
            for tag in taglist:


                # for date tags, if there was no $i subfield they won't have been given start and end dates
                # defaults need to be assigned and the lack of $i reported
                if datetags.has_key(tag.tagname):
                    if tag.startdate == '':
                        dateerr.write('Record ' + rec.recid + ': no indexable date for field ' + tag.tagname + '\n')
                        tag.startdate = '99999999'
                        tag.enddate = '00000000'
                        tag.approx = 'false'

                # create browse and sort versions of shelfmarks [would it be better if shelfmarks were a special
                # kind of recordtag class and this was done at init?]
                # also add image and mount ids to shelfmarks
                if tag.tagname == '950':
                    tag.shelfbrowse, tag.shelfsort = shelfmarkconverter(tag.content, rec.collection)
                    if tag.shelfbrowse == '':
                        # hijack dateerr for the moment - put somewhere more conspicuous later
                        dateerr.write('bad shelfmark: ' + tag.content + '\n')
                    if tag.content in self.imageids:
                        tag.imageid, tag.mountid = self.imageids[tag.content]
                        self[0].getfulltext(tag.imageid, self.ocrfiles)
                    dateerr.write(' '.join([tag.content, tag.shelfbrowse, tag.imageid, tag.mountid, '\n']))

                if srchlup.has_key(tag.tagname):
                    # all but first item in srchlup list should get a display="none" attribute. use disp variable.
                    disp = 'y'
                    for field in srchlup[tag.tagname]:
                        if not rec.search.has_key(field):
                            rec.search[field] = RecordTagSet()
                        # need copies of the tag so that one version can gain the attribute without affecting the other	
                        # deepcopy seems unable to cope with items that have bound methods
                        # http://techlists.org/archives/programming/pythonlist/2005-02/msg02378.shtml
                        # so need to define __deepcopy__ method on RecordTag for this to work
                        # this is quite time-consuming, maybe there's a better way
                        rec.search[field].append(copy.deepcopy(tag))
                        if disp == 'n':
                            rec.search[field][-1].display = 'none'
                            for sub in rec.search[field][-1].subtags:
                                sub.display = 'none'
                        disp = 'n'
                
                # treat anything we haven't picked up for search fields as a display field
                else:
                    rec.display.append(tag)

                                
                if somtags.has_key(tag.tagname):
                    rec.som['som_' + tag.xmlname] = copy.deepcopy(tag)
            
            # remove copynote etc. from som version of shelfmark
            for shelf in rec.som['som_shelfmarks']:
                shelf.subtags = []
            
            # join category fields together for som
            # don't do that any more 17/02/09
            #if rec.som.has_key('som_sub_category'):
            #    rec.som['som_category'].content = rec.som['som_sub_category'].content + ' ' + rec.som['som_category'].content
            #    del rec.som['som_sub_category']
            
            """
            for field in rec.som.keys():
#                if not type(rec.som[field]) == 'list':
                dateerr.write('record ' + rec.recid + ' somfield ' + field + '\n')
                if not hasattr(rec.som[field], 'xmlname'):
                    dateerr.write('no content: record ' + rec.recid + ' somfield ' + field + '\n')
            """

            yield rec
            
            # stop memory filling up with all these records
            #self[reccount - 1] = ''
#            print str(len(self)) + ' records left'
            
#            self.handoverset.append(rec)
            
            
            
            
        #del self[:]
        
        dateerr.close()
    
    #---------Tasklist---------
    
    # data import needs to be record by record; but deleting previous versions seems to take ages so 
    # either find a way to speed that up or import whole data every time and use only last version of record
    # further refine writejj so it doesn't increase at all as it goes on
    # writejj might not be able to open the output file at the end if it gets much bigger
    
    # ent refs for & etc. Remove ordf? - done
    # empty titles
    # country codes lup (nathaniel mail)
    # collection specific som hierarchies
    # should 691 be treated as searchable/somdisplayable or not? should be
    # other names search
    # select from list tagging
    # nathaniel booktrade email
    # indexable townofpersonnamed versus normal
    # dates with s.a. to nodate - names with s. n.? places with s. l.? also nathaniel mail?
    # feed back dates lacking decent indexable forms; trim 691 from report and work out what to do with it
    # normalise capitalisation for select from lists????
    # updates e.g. to xmlnames; currently need to reimport all data; do differently - function? SQL file?
    # bodleian changes
    # combine subtags with main text for searches
    # tool to remove specified records from dbase? to fix mistakes e.g. forgetting to unixise first
    # multiple shelfmarks - for now, use first; later need to use all
    # coding - see latin-1 entities email from me to me
    # more bodelian corrections
    
    # crime search - some more subtags to add to search fields
    # memory problems - refine - (1) profiler (2) python speed fixes (3) network memory (4) break up?
    # memory problems - set up so we only output updated data somehow?
    # what if ocr listdir becomes too long? generally better to store ocr differently
    # multiple image sets for one record
    
    # som hierarchies: subtags; proc field different; new fields
    # criminal/crime/sentence: want to search separately; want to display in own field or together
    
    # for steady improvement?:
    # dates - do something with ones that lack indexable forms? improve conversion of indexable forms?
    # check inputs and lookups
    # what is input process? how do we make sure it's up to date?
    # shelfmark splitting and sorting
    # get coding to work - store as latin-1 and pass through template correctly
    
    #--------------------------
    
    # SPEED/MEMORY:
    # Push through record by record and add full text at the end?
    # deepcopy is time-expensive but no. of records is the big danger
    
class JJRecord(BaseRecord):

    def __init__(self, rawlines=None):
        self.rawlines = rawlines
        
        self.databaseConnection = databaseConnection

        self.tablename = "records"
#        self.requiredFields = ['recid', 'collection', 'category', 'content']
        self.requiredFields = ['recid', 'allegroid', 'category']
        self.optionalFields = ['tagdict']
        self.xmlFields = ['collection', 'content', 'search', 'display', 'som', 'imageid', 'mountid', 'fulltext', 'namesearch']

        self.content = RecordTagSet()
        self.collection = ''
        self.templateclass = jj_record_template.jj_record_template
        self.fulltext = ''
#        self.entityconverter = latin1everything()
        
    def populatefromlines(self):
    
        global fieldlup
        fieldlup = jjlookups.getfieldlup()
        for line in self.rawlines:
            linematch = linere.search(line)
            if linematch != None:
#               print "got here!"
                if linematch.group(1) == '000':
                    self.recid = linematch.group(3)
                elif linematch.group(1) == '100':
                # multiple categories possible?
                    self.category = linematch.group(3)
#                elif linematch.group(1) == '950':
#                    self.shelfmark = linematch.group(3)
                else:
                # deal with: repeats, subtags
                    if not tagstodrop.has_key(linematch.group(1)):
                        xmlname = getxmlname(linematch.group(1), fieldlup=fieldlup)
                        if xmlname != 'unknown_tag':
                            self.content.append(RecordTag(linematch.group(1), xmlname, linematch.group(2), linematch.group(3), self.recid))
                            self.content[-1].populate()
                            # now we've separated off subtags get shelfmark for records table
#                            if self.content[-1].tagname == '950':
#                                if self.shelfmark == '':
#                                    self.shelfmark = self.content[-1].content
                            
    def fulldbinsert(self, tagcount=0):
    
        if tagcount == 0:
            tagcount = gettagcountfromdb()
        self.InsertIntoDB_new()
        for tag in self.content:
            tagcount += 1
            tag.tagid = tagcount
            tag.InsertIntoDB_new()
            for subtag in tag.subtags:
                subtag.tag = tag.tagid
                subtag.InsertIntoDB_new()
        return tagcount
        
    
    def getfulltext(self, imageid, ocrfiles):
    
        errs = open('ocrreport.log', 'a')
        ocrstring = ''
        #if self.imageid != '':
#            errs.write('got here 1\n')
        if ocrfiles.has_key(imageid):
#                errs.write('got here 2: ' + self.imageid + '\n')
            for ocrfile in ocrfiles[imageid]:
#                    errs.write('got here 3:' + ocrfile + '\n')
                ocrfi = codecs.open(ocrfile, 'r', 'latin-1')
                ocrtext = ocrfi.read()
                ocrtext = ocrstripre.sub('', ocrtext)
                ocrtext = ocrtext.replace('\r\n', ' ').replace('<acc></acc>', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                ocrtext = ocrtext.encode('ascii', 'xmlcharrefreplace')
                ocrfi.close()
                ocrstring += ocrtext
            self.fulltext = ' '.join([self.fulltext, ocrstring])
        errs.close()
    
    def insertdisplayinfo(self, displup):
        
        for tag in self.content:
            if displup.has_key(tag.tagname):
                tag.display = displup[tag.tagname]
            for subtag in tag.subtags:
                fullsubtag = tag.tagname + subtag.subname
                if displup.has_key(fullsubtag):
                    subtag.display = displup[fullsubtag]

    
"""
    def getcollection(self):
    
        db = self.databaseConnection()
        cu = db.cursor()
        
        cu.execute("SELECT collection FROM recordtags t, collections c WHERE t.record = %s AND t.tagname = '950' AND t.content = c.shelfmark;" , (self.recid))
        try:
            self.collection = cu.fetchall()[0][0]
        except IndexError:
            print self.recid
"""

class RecordTagSet(BaseRecordSet):

    def __init__(self):

        self.recordclass = RecordTag
        self.tablename = "recordtags"
        self.databaseConnection = databaseConnection
        self.fieldnames = ["tagid", "tagname", "xmlname", "sequence", "content", "zflag", "record"]

class RecordTag(BaseRecord):
# involves setting up a lot of attributes that are only used by specific tag types
# perhaps different types of tags - shelfmark, date etc. - should be subclasses??

    def __init__(self, tagname=None, xmlname=None, sequence=None, rawtext=None, record=None, content=None, display=''):

        self.databaseConnection = databaseConnection
        self.tagname = tagname
        self.xmlname = xmlname
        self.sequence = sequence
        self.rawtext = rawtext
        self.record = record
        self.tablename = "recordtags"
#        self.requiredFields = ['tagid', 'tagname', 'xmlname', 'sequence', 'content', 'record', 'subtags']
        self.requiredFields = ['tagid', 'tagname', 'xmlname', 'sequence', 'content', 'record', 'zflag']
        self.xmlFields = ['subtags', 'tagtext', 'startdate', 'enddate', 'display', 'approx', 'sortatt']
        self.optionalFields = []
        self.subtags = SubtagSet()
        self.tagtext = ''
        self.startdate = ''
        self.enddate = ''
        self.sortatt = ''
        self.display = display
        self.approx = ''
        self.content = content
        self.zflag = ''
        self.subtagdict = {}
        self.sfl = ''
        self.shelfbrowse = ''
        self.shelfsort = ''
        self.imageid = ''
        self.mountid = ''

    def populate(self):

        if self.tagname == '0rr':
            self.content = self.rawtext
        else:
            subtagnames = subtagre.findall(self.rawtext)
            splitcontents = subtagre.split(self.rawtext)
            newsplitcontents = []
            for subtext in splitcontents:
                if zre.search(subtext) != None:
                    subtext = zre.sub('', subtext)
                    self.zflag = 'y'
                newsplitcontents.append(subtext)
            splitcontents = newsplitcontents
            self.content = splitcontents.pop(0)
            subtagtuple = zip(subtagnames, splitcontents)
            for subtagitem in subtagtuple:
                xmlname = getxmlname(self.tagname, fieldlup=fieldlup, subtag=subtagitem[0])
                if xmlname != 'unknown_tag':
                    self.subtags.append(Subtag(subtagitem[0], xmlname, subtagitem[1]))
                
    def __deepcopy__(self, memo):
    
        newcopy = RecordTag(tagname=self.tagname, xmlname=self.xmlname, record=self.record, content=self.content)
        newcopy.subtags = SubtagSet()
        for subtag in self.subtags:
            newcopy.subtags.append(copy.copy(subtag))
        newcopy.databaseConnection = self.databaseConnection
        newcopy.requiredFields = self.requiredFields
        newcopy.optionalFields = self.optionalFields
        newcopy.tagtext = self.tagtext
        newcopy.startdate = self.startdate
        newcopy.enddate = self.enddate
        newcopy.sortatt = self.sortatt
        newcopy.display = self.display
        newcopy.approx = self.approx
        newcopy.shelfbrowse = self.shelfbrowse
        newcopy.shelfsort = self.shelfsort
        newcopy.imageid = self.imageid
        newcopy.mountid = self.mountid
        
        return newcopy
        
    def makesubtagdict(self):
    
        for subtag in self.subtags:
            if not self.subtagdict.has_key(subtag.subname):
                self.subtagdict[subtag.subname] = []
            self.subtagdict[subtag.subname].append(subtag)
    
    def setauthdisplay(self):
    
        if namere.match(self.tagname) != None:
            if self.subtagdict.has_key('$i'):
                self.display = 'none'
            
    def settowndisplay(self):
    
        if namere.match(self.tagname) != None:
            if self.subtagdict.has_key('$x'):
                for s in self.subtagdict['$x']:
                    s.display = 'comma'
                if self.subtagdict.has_key('$t'):
                    for s in self.subtagdict['$t']:
                        s.display = 'none'
            elif self.subtagdict.has_key('$t'):
                for s in self.subtagdict['$t']:
                    s.display = 'comma'


"""
# old version of setauthdisplay: it used to matter whether we had library of congress version (i.e. zflag = 'y') or not


        if namere.match(self.tagname) != None:
            if self.zflag == 'y':
                if self.subtagdict.has_key('$i'):
                    self.display = 'none'
                else:
                    # would it have epithet if no indexable form?
                    if self.subtagdict.has_key('$e'):
                        for subtag in self.subtagdict['$e']:
                            subtag.display = 'none'
            else:
                if self.subtagdict.has_key('$i'):
                    for subtag in self.subtagdict['$i']:
                        subtag.display = 'none'
                if self.subtagdict.has_key('$e'):
                    for subtag in self.subtagdict['$e']:
                        subtag.display = 'none'
"""    

class SubtagSet(BaseRecordSet):

    def __init__(self):

        self.databaseConnection = databaseConnection
        self.recordclass = Subtag
        self.tablename = "subtags"
        self.fieldnames = ["subtagid", "subname", "xmlname", "content", "tag"]
    
class Subtag(BaseRecord):

    def __init__(self, subname=None, xmlname=None, content=None):

        self.databaseConnection = databaseConnection
        self.subname = subname
        self.xmlname = xmlname
        self.content = content
        self.tablename = "subtags"
        self.requiredFields = ['subname', 'xmlname', 'content', 'tag']
        self.xmlFields = ['display']
        self.optionalFields = []

def shelfmarkconverter(shelfmark, collection):
# take shelfmark, produce browse and sort forms
# not sure where to put this yet
# these are the regexes
# shelfbracketre = re.compile('\((\d*)(.*)\)')
# shelfboxre = re.compile('([Bb]ox|vol\.|) (\d[-\d]*)(.*)$')
# is there a less excruciating way to do this?
    
    shelfbracketmatch = shelfbracketre.search(shelfmark)
    if shelfbracketmatch == None:
        return '', ''
    else:
        brackno = shelfbracketmatch.group(1)
        bracksuffix = shelfbracketmatch.group(2)
        choppedshelf = shelfbracketre.sub('', shelfmark).rstrip()
#        print choppedshelf
        
    shelfboxmatch = shelfboxre.search(choppedshelf)
    if shelfboxmatch == None:
        boxorvol = ''
        boxno = ''
        boxsuffix = ''
    else:
        choppedshelf = shelfboxre.sub('', choppedshelf).rstrip()
#        print choppedshelf
        boxorvol = shelfboxmatch.group(1)
        boxno = shelfboxmatch.group(2)
        boxsuffix = shelfboxmatch.group(3)
        
    shbrowse = '#'.join([collection, choppedshelf])
    if boxorvol != '':
        shbrowse = ''.join([shbrowse, '#', boxorvol, ' ', boxno, boxsuffix])
    elif boxno != '':
        shbrowse = ''.join([shbrowse, '#', boxno, boxsuffix])
        
    shsort = choppedshelf
    if boxorvol == 'vol.':
        boxno = boxno[-4:]
    elif boxno != '':
        boxno = boxno.zfill(4)
    shsort = shsort + ' '
    if boxorvol != '':
        shsort = ''.join([shsort, boxorvol, ' '])
    if boxno != '':
        shsort = ''.join([shsort, boxno, boxsuffix, ' '])
    if brackno != '':
        shsort = ''.join([shsort, brackno.zfill(4), bracksuffix, ' '])
    shsort = shsort[:-1]
    
    return shbrowse, shsort
    
        
def populatecollections(colleclup):

    #luplinere = re.compile(' *(\d\d) \| (.*)\n')
    #luplinere = re.compile('(.*)\|(\d\d)\n')
    luplinere = re.compile('(.*?)\|(.*)\n')
    """
    #collno lookup no longer used - lookup gives us direct collection now - but keep in case we revert
    collnos = {
                '10': 'Entertainment',
                '11': 'Entertainment',
                '20': 'Crime',
                '30': 'Booktrade',
                '40': 'Prints',
                '50': 'Advertising'
            }
    """
    
    db = databaseConnection()
    cu = db.cursor()
    
    collup = open(colleclup, 'r')
    colluptext = collup.read()
    print len(luplinere.findall(colluptext))
    for match in luplinere.findall(colluptext):
        #print "got here"
        cu.execute("""REPLACE INTO collections SET recid = %s, collection = %s;""" , (match[0], match[1]))
    print "Collections table updated"
    
def updateimageids(imglup):

#    from citations.jjson.jjson import *
#    updateimageids('img.lut')

    luplinere = re.compile('^(.*?)\|(.*?)\|([^|]*?)\|?$', re.M)
    
    db = databaseConnection()
    cu = db.cursor()
    
    imgs = open(imglup, 'r')
    imgtext = imgs.read()

#    imglines = imgtext.split('\n')
    

    for match in luplinere.findall(imgtext):
        #print "got here"
        cu.execute("""REPLACE INTO imageids SET shelfmark = %s, imageid = %s, mountid = %s;""" , (match[0], match[1], match[2]))
    print "Image IDs table updated with the contents of " + imglup

def gettagcountfromdb():

    db = databaseConnection()
    cu = db.cursor()
        
    cu.execute("""SELECT tagid FROM recordtags ORDER BY tagid DESC LIMIT 1;""")
    tagidgot = cu.fetchall()
    if tagidgot == ():
        tagcount = 0
    else:
        tagcount = int(tagidgot[0][0])
    return tagcount

def makenewupdonlyfile(infile):
# takes a concatenated Bodleian input file and writes out a new version containing
# only the latest versions of duplicate records

    inf = open(infile, 'r')
    outf = open(infile[:-4] + '_upd.txt', 'w')
    record = []
    recdict = {}
    for line in inf:
        if linere.search(line) != None:
            linematch = linere.search(line)
            if linematch.group(1) == '000':
                if record != []:
                    recdict[recid] = record
                recid = linematch.group(3)
                record = [line]
            else:
                record.append(line)
    recdict[recid] = record
    for record in recdict.values():
        for line in record:
            outf.write(line)
        outf.write('\n')
    inf.close()
    outf.close()
    return infile[:-4] + '_upd.txt'


def jjloaddata(infile):
# Loads a full, cumulative data file into the database.
# Probably faster than updating existing database even for large files because updating means
# you have to find and delete all the tags and subtags for updated records which takes ages.

    # Kick off by truncating old tables
    db = databaseConnection()
    cu = db.cursor()
        
    cu.execute("""TRUNCATE TABLE records;""")
    cu.execute("""TRUNCATE TABLE recordtags;""")
    cu.execute("""TRUNCATE TABLE subtags;""")
        
    # Make a version of input file with old versions of updated records stripped out 
    newinfile = makenewupdonlyfile(infile)
    
    inf = codecs.open(newinfile, 'r', 'latin-1')
    tagcount = 0
    record = []

    for line in inf:
        line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('*', '&#42;')
        line = line.encode('ascii', 'xmlcharrefreplace')
        if linere.search(line) != None:
            linematch = linere.search(line)
            if linematch.group(1) == '000':
                if record != []:
                    newrec = JJRecord(record)
                    newrec.populatefromlines()
                    tagcount = newrec.fulldbinsert()
                record = [line]
            else:
                record.append(line)
    # get the last record in
    newrec = JJRecord(record)
    newrec.populatefromlines()
    tagcount = newrec.fulldbinsert()


def jjupdate(newfile):
# puts new catalogue data in, checking by recid whether a record is already in there
# seems to take a long time to delete the tags and subtags for updated records
# and still stores all the new records in memory
# Need a new process to fix these two problems

    warnings.warn(("jjupdate has problems with memory usage and should only be used, if at all,"
    " to add a small update to the database. It is preferable to replace the full data set using"
    " jjloaddata instead."), DeprecationWarning)
    
    inf = codecs.open(newfile, 'r', 'latin-1')
    rawtext = inf.read()
    rawtext = rawtext.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('*', '&#42;')
    rawtext = rawtext.encode('ascii', 'xmlcharrefreplace')
    inrecs = JJRecordSet(rawtext)
    inrecs.populatefromraw()
    
    newrecs = JJRecordSet()
    newrecdict = {}
    recstodelete = []
    tagstodelete = []
    oldrecdict = {}

    db = databaseConnection()
    cu = db.cursor()

    print "getting existing recids"
    cu.execute("""SELECT recid FROM records;""")
    for row in cu.fetchall():
        oldrecdict[row[0]] = ''

    print "identifying records to overwrite"
    for rec in inrecs:
        newrecdict[rec.recid] = rec
        if oldrecdict.has_key(rec.recid):
            recstodelete.append(rec.recid)
    
    print "deleting old versions of records"
    for recid in recstodelete:
        cu.execute("""SELECT tagid FROM recordtags WHERE record = %s;""", (recid))
        for row in cu.fetchall():
            tagstodelete.append(row[0])
        for tagid in tagstodelete:
            cu.execute("""DELETE FROM subtags WHERE tag = %s;""", (tagid))
        cu.execute("""DELETE FROM recordtags WHERE record = %s""", (recid))

    print "populating db with new records"
    for rec in newrecdict.values():
        newrecs.append(rec)
    
    newrecs.populatedb()


    
# next bits are part of the whole character encoding mess; work in progress, tread carefully!
#latin1decoder = codecs.getdecoder('latin1')

class latin1everything:
# This is an attempt to feed the FillTemplate method on BaseRecord with an entityconverter value
# to catch whatever format comes out of MySQL before it goes into cheetah
# Current plan is to encode everything as latin-1, which seems to have worked on other projects
# But encoding is currently basic ascii with numerical charrefs anyway - was a quicker way of getting it to work
# So if we wanted to test this out we would need to (a) reimport data in latin 1 format (requires tweaks to script)
# (b) uncomment the self.entityconverter line on JJRecord's __init__ function.
# Not necessary for now.
    
    def __init__(self):
        pass
    
    def convert(self, value):
#        value = latin1decoder(value, 'utf8')[0]
        value = value.encode('latin-1')
        print 'got here'
        return value


def writeJJ():
# the main function to pull everything out of the database and deliver as XML

    from entities import latin1Converter
    from entityShield import entityProtect
    
    # specify output filename here
    writetofile = 'jjdata_oct10_beta.xml'
    # jj data arrives in a weird format; this will be used to tidy; could be done earlier?

    jj = JJRecordSet()

    outf = open(writetofile + 'temp', 'w')

    for rec in jj.generaterecords():
        recout = rec.FillTemplate() 
        outf.write(recout)
    outf.close()
    print "Template applied. Encoding output file..."
    
    
    convf = open(writetofile + 'temp', 'r')
    outf = open(writetofile, 'w')
    outf.write('<johnjohnson>\n')
    # my entref odd jobs class; to be used to strip out control character rubbish
    lc = latin1Converter()

#    outtext = convf.read()
    for line in convf:
        line = lc.convert(line, 'control')
        line = line.replace('&#170;', '')
        outf.write(line)
    convf.close()
    outf.write('</johnjohnson>')
    outf.close()
    del lc
    print "Data encoded as ASCII with XML numerical character references"
    print "All done"


def splitdb(idfile):
# temporary function to divide up contents of one database into two
# necessary workaround because generatehandover func as of 06/02/08 causes MemoryError on >c.10,000 records.
# use for short-term handovers and process profiling

    iddict = {}
    idf = open(idfile, 'r')
    for line in idf:
        iddict[line.strip()] = ''
    
    jj = JJRecordSet()
    print "Retrieving data from MySQL database..."
    jj.fullpopulatefromdb()
    
    jj1 = JJRecordSet()
    jj2 = JJRecordSet()
    
    for rec in jj:
        if iddict.has_key(rec.recid):
            jj1.append(rec)
        else:
            jj2.append(rec)
            
    print "filling jjson_split_1"
    jj1_connector = dbconnector(user='jjson', passwd='jjson', db='jjson_split_1')
    jj1.databaseConnection = jj1_connector.MakeConnection
    for rec in jj1:
        rec.databaseConnection = jj1_connector.MakeConnection
        for tag in rec.content:
            tag.databaseConnection = jj1_connector.MakeConnection
            for subtag in tag.subtags:
                subtag.databaseConnection = jj1_connector.MakeConnection
    jj1.populatedb()
    
    print "filling jjson_split_2"
    jj2_connector = dbconnector(user='jjson', passwd='jjson', db='jjson_split_2')
    jj2.databaseConnection = jj2_connector.MakeConnection
    for rec in jj2:
        rec.databaseConnection = jj2_connector.MakeConnection
        for tag in rec.content:
            tag.databaseConnection = jj2_connector.MakeConnection
            for subtag in tag.subtags:
                subtag.databaseConnection = jj2_connector.MakeConnection
    jj2.populatedb()
    
    print "done."


    
"""
Some handy command lines for copying:

from citations.jjson.jjson import *
filldatabase('biggersample.txt')
filldatabase('alltw.txt')

jjupdate('jjall071112.txt')
jjupdate('trythis.txt')

from citations.jjson.jjson import *
testxml()
writeJJ()

test = JJRecordSet()
test.fullpopulatefromdb()
test.brutexml()

populatecollections('catgroups.txt')

updateimageids('img.lut')

"""

# ----------------------
# Scraps in need of a proper home:

townre = re.compile('[3-5]\d\d\$[tx]')

def getxmlname (tag, fieldlup=jjlookups.getfieldlup(), subtag=None):

    if subtag != None:
        tag = tag + subtag
    if fieldlup.has_key(tag):
        return fieldlup[tag]
# $t (or $x if present) subfield from any #3, #4 and #5 field = <town_of_person_named>
    elif townre.match(tag) != None:
        return 'town_of_person_named'
    else:
        log = open('xmlnames.log', 'a')
        log.write('No xmlname found for ' + tag + '\n')
        log.close()
#        print 'No xmlname found for ' + tag
        return 'unknown_tag'


global tagstodrop
tagstodrop = {
                '0rt': '',
                '805': ''
                }
                
def findprimaryfield(tagset, prioritylist):

    for tag in prioritylist:
        if tagset.has_key(tag):
            return tagset[tag][0]


"""
global authprior, titleprior, dateprior, procprior
authprior = ['300', '408', '330', '350', '340', '438', '430', '432', '431', '570', '301', '354', '571', '310', '320', '331', '334', '351', '352', '353', '400', '401', '405', '420', '421', '422', '423', '424', '440', '450', '501', '505', '572', '573', '580', '581', '582', '730', '732', '738']
titleprior = ['200', '282', '283', '248', '210', '220', '224', '245', '270', '278', '205', '223']
dateprior = ['690', '285', '689', '290', '691']
procprior = ['680', '681']
"""

nondigitre = re.compile('[^\d]*')

def datetransform(indexable):
# give me the contents of an indexable date field, and I'll try to make a start and end date from it

    if indexable.find('[s.a.]') != -1:
        return '99999999', '00000000', 'false'
    
    stripped = nondigitre.sub('', indexable)
    approx = 'true'
    if len(stripped) == 8:
    	sdt = stripped
    	edt = stripped
    	approx = 'false'
    elif len(stripped) == 6:
        sdt = stripped + '01'
        edt = stripped + '31'
    elif len(stripped) < 5 and len(stripped) > 0:
        sdt = stripped.ljust(4, '0') + '0101'
        edt = stripped.ljust(4, '9') + '1231'
    else:
        sdt = '99999999'
        edt = '00000000'
        approx = 'false'
    
    return sdt, edt, approx


def time_cu():

    import time
    db = databaseConnection()
    cu = db.cursor()
    timefirst = time.time()
    timetest = time.time()
    timefortime = timetest - timefirst
    print str(timefortime) + " seconds to run time()"
    timethen = time.time()
    cu.execute("""SELECT * FROM subtags WHERE tag = '57213'""")
    timenow = time.time()
    print str(timenow - timethen) + " seconds to execute query and check time"
    print "= " + str(timenow - timethen - timefortime) + " seconds to execute query"

# --------------------
    #-------- Old tasks --------------

    # stop columns truncating - done
    # rename srch fields? - done
    # find category; get doctype in - done
    # add advertising-specific fields - done
    # list other fields for display - done
    # get non-alphanumeric stuff out of ids - done
    
    # som prioritisation - done
    # speed issues - done
    # get subtag stitching-together working properly so display is ok - done
    # flag-type fields - done
    # dates need to be numerical - something is wrong here - done
    # need certain fields in certain formats for filters - done
    # update xmlname list - done
    
    # handle repeats of records - done
    # assorted alan changes - done
    # category codes - done
    
    # character conversion - fix utf8 (encode: xmlcharrefreplace?), then replace with entrefs (latin1converter.convert?) - done
    # what does |z mean again? loc form, special name rule - done

    # images - done
    # ocr - done
    # several records on one backing sheet - done

    # somtags not containing source field name - done
    # shelfmark sorting and browsing - done
    # make sure all data is xml-friendly; incorporate tidying steps - done
    # may need to intervene with xml tagnames when duplicated or in som to make sure unique - done
    # xmlnames getting truncated - done
    # check inputs; collections lookup is currently out of date - done
    # extend catcodes lookup beyond entertainment ones - done

"""
Some old versions of functions

def jjupdateold(newfile):
# puts new catalogue data into the database. If it finds a later version of an existing record (even within
# the import file) it overwrites with the latest.

# problem: it creates a python object containing all records in existing db to compare with
# which runs out of memory. obsolete now.

    inf = codecs.open(newfile, 'r', 'latin-1')
    rawtext = inf.read()
    rawtext = rawtext.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    rawtext = rawtext.encode('ascii', 'xmlcharrefreplace')
    inrecs = JJRecordSet(rawtext)
    inrecs.populatefromraw()
    
    oldrecs = JJRecordSet()
    oldrecs.fullpopulatefromdb()
    oldrecids = {}
    # oldrecs.taglup currently best way of getting all record ids?
    for oldrec in oldrecs.taglup.keys():
        oldrecids[oldrec] = ''
    
    newrecs = JJRecordSet()
    newrecdict = {}
    recstodelete = []
    
    for rec in inrecs:
        newrecdict[rec.recid] = rec
        if oldrecids.has_key(rec.recid):
            print "repeat rec: " + rec.recid
            recstodelete.append(rec.recid)
            
    tagstodelete = []
    subtagstodelete = []
    for rec in recstodelete:
        for tag in oldrecs.taglup[rec.recid]:
            tagstodelete.append(tag.tagid)
            for subtag in oldrecs.subtaglup[tag.tagid]:
                subtagstodelete.append(subtag.subtagid)
                
    db = databaseConnection()
    cu = db.cursor()
    
    for sub in subtagstodelete:
        cu.execute(DELETE FROM subtags WHERE subtagid = %s;, (sub))
        
    for tag in tagstodelete:
        cu.execute(DELETE FROM tags WHERE tagid = %s, (tag))

    for rec in newrecdict.values():
        newrecs.append(rec)
    
    newrecs.populatedb()
    
def writeJJold():
# the main function to pull everything out of the database and deliver as XML
# currently need to run this twice, once on each of the _split_ databases, specifying which database
# as part of jjdbconnector variable at top of file

    from entities import latin1Converter
    from entityShield import entityProtect
    
    # specify output filename here
    writetofile = 'jjdata_may_alpha_handover.xml'
    # jj data arrives in a weird format; this will be used to tidy; could be done earlier?
#    latin1decoder = codecs.getdecoder('latin1')

    jj = JJRecordSet()
#    print "Retrieving data from MySQL database..."
#    jj.fullpopulatefromdb()
#    print "Data retrieved. Preparing for output..."
    #jj.generatehandover()

#    print "Preparation done. Applying template..."
    outf = open(writetofile, 'w')
#    outf = codecs.open(writetofile, 'w', 'utf-8')
#    outf = codecs.open(writetofile, 'w', 'latin-1')
"""
#    g = jj.generaterecords()
#    for i in range(0, 29):
#        rec = g.next()
"""
    for rec in jj.generaterecords():
        recout = rec.FillTemplate()
        outf.write(recout)
#        outf.write(rec.FillTemplate())
#        outf.write(latin1decoder(rec.FillTemplate(), 'latin-1')[0])
    outf.close()
    print "Template applied. Encoding output file..."
    
    
#    convf = codecs.open(writetofile, 'r', 'utf-8')
    convf = open(writetofile, 'r')
    
    # my entref odd jobs class; to be used to strip out control character rubbish
    lc = latin1Converter()

    outtext = convf.read()
    outtext = lc.convert(outtext, 'control')
    outtext = outtext.replace('&#170;', '')
    convf.close()
    outf = open(writetofile, 'w')
    outf.write('<johnjohnson>\n' + outtext + '\n</johnjohnson>')
    outf.close()
    outtext = ''
    del lc
    print "Data encoded as ASCII with XML numerical character references"
    print "All done"

"""