import re
import MySQLdb
import amara
import xml
import urllib2
from urllib import urlencode

import entityShield

from fuzzyMatch import fuzzy
from citations.base.baseRecord import *
from citations.base.dbconnector import dbconnector
from citations.lion.templates import ris_poem, ris_volume
from citations.lion.templates import ris_poem_comcitn, ris_volume_comcitn
from citations.lion.templates import ris_poem_comcitn_redux, ris_volume_comcitn_redux

from entities import xmlbaseents

cspdbconnector = dbconnector(upd='lioncitations')
databaseConnection = cspdbconnector.MakeConnection

LIONAUTHORS = {}

inf = open('/dc/lion3/data/control/lionauth.rec', 'r')
lionauthrec = inf.read()
inf.close()

recs = lionauthrec.split('<rec')
rec_exp = re.compile('<authorid>(.*?)</authorid>.*?<lcname>(.*?)</lcname>', re.DOTALL)
for rec in recs:
    if rec_exp.search(rec) is not None:
        LIONAUTHORS[rec_exp.search(rec).group(1)] = rec_exp.search(rec).group(2)

class LionCitationError(Exception): pass

def dothelot():

    """i.e. for poetry, prose, drama, run the processes one after the other.
    
    WATCH OUT for the entityprotect stuff!
    
    EntityProtect is run on the source file as a first step and Unprotect is
    run on the same file as a last step. Apart from this being rather inefficient,
    it also means that when a file goes wrong, all the entities will be screwed up.
    
    For this reason you're probably best employed making a copy of the master data
    and running it on that rather than running it on it straight. Even though
    making a copy of all the poetry data takes bloody ages, it's safer to wait.
    """

    dodrama()
    doprose()
    dopoetry()

def dodrama():
    a = LionFileBatch(filepath='drama', extension='.one')
    a.ProcessBatch(workflow=a.total_insertion)
    a = LionFileBatch(filepath='drama/master', extension='.new')
    a.ProcessBatch(workflow=a.update_files)

def doprose():
    a = LionFileBatch(filepath='prose', extension='.one')
    a.ProcessBatch(workflow=a.total_insertion)
    a = LionFileBatch(filepath='prose/master', extension='.new')
    a.ProcessBatch(workflow=a.update_files)

def dopoetry():
    a = LionFileBatch(filepath='poetry', extension='.one')
    a.ProcessBatch(workflow=a.total_insertion)
    a = LionFileBatch(filepath='poetry/master', extension='.new')
    a.ProcessBatch(workflow=a.update_files)

class LionRecordSet(BaseRecordSet):

    def __init__(self):
        self.databaseConnection = databaseConnection

class LionFileBatch:

    """A class to represent a batch of Lion files such as all the files
    in one collection. At this time, the batch is defined as all the files
    underneath a filepath passed in at initialization."""

    def __init__(self, filepath, extension='.new'):
        self.filepath = filepath
        self.extension = extension

        # Some workflows
        self.total_insertion = ['ExtractVolumes', 'InsertVolumes', 'ExtractIdrefs', 'InsertIdrefs']
        self.update_files = ['ExtractIdrefs', 'UpdateComcitn']
        
    def ProcessBatch(self, workflow=['ExtractVolumes', 'InsertVolumes'], log=True):
        """Create a LionFile instance for each of the files in the batch.
        Run the method of the LionFile object passed in the method parameter."""
        import os
        outf = open('errors.log', 'w')
        outf.close()
        for root, dirs, filenames in os.walk(self.filepath):
            for filename in filenames:
                if filename.endswith(self.extension):
                    if log:
                        print os.path.join(root, filename)
                    entityShield.entityProtect(os.path.join(root, filename))
                    try:
                        thisfile = LionFile(os.path.join(root, filename))
                        for method in workflow:
                            print method
                            getattr(thisfile, method)()
                    except xml.sax._exceptions.SAXParseException, LionCitationError:
                        outf = open('errors.log', 'a')
                        outf.write(os.path.join(root,filename))
                        outf.write('\n')
                        outf.close()
                    entityShield.entityUnprotect(os.path.join(root, filename))

class LionFile:
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.volumes = []

    def ExtractVolumes(self):
        """For the Lion data file extract the information from the XML to
        populate a set of Lion Volume, Poem and AuthorAttribution objects
        and store them in the database."""
        for vol in amara.pushbind(self.filepath, u'/vlgroup/div0'):
            newvol = LionVolume(parentfile=self)
            newvol.ParseBinding(vol)
            self.volumes.append(newvol)
        
    
    def InsertVolumes(self):
        """Assuming that all the volumes have been extracted, insert the
        relevant rwos into the database."""
        for vol in self.volumes:
            vol.doSQL("DELETE FROM LionVolumes WHERE idref='"+vol.idref+"';")
            vol.InsertIntoDB_new()
            #for idrefmap in vol.child_idref_set:
            #    idrefmap.InsertIntoDB_new()
            if len(vol.author_attribution_set) > 0:
                vol.author_attribution_set[0].doSQL("DELETE FROM AuthorAttributions WHERE idref='"+vol.idref+"';")
                for attribution in vol.author_attribution_set:
                    attribution.InsertIntoDB_new()
            for poem in vol.poem_set:
                poem.doSQL("DELETE FROM LionPoems WHERE idref='"+poem.idref+"';")
                poem.InsertIntoDB_new()
                #for idrefmap in poem.child_idref_set:
                #    idrefmap.InsertIntoDB_new()
                if len(poem.author_attribution_set) > 0:
                    poem.author_attribution_set[0].doSQL("DELETE FROM AuthorAttributions WHERE idref='"+poem.idref+"';")
                    for attribution in poem.author_attribution_set:                    
                        attribution.InsertIntoDB_new()

    def UpdateComcitn(self):
        """The citations are held in a <comcitn> tag, one for each <idref>, throughout
        the data. This is the method to call to update the <comcitn>s in the file 
        with the contents of the database."""
        COMCITN_EXP = re.compile('<idref>(.*?)</idref>.*?</comhd', re.DOTALL)
        COMCITN2_EXP = re.compile('<comcitn>(.*?)</comcitn>', re.DOTALL)
        
        inf = open(self.filepath, 'r')
        data = inf.read()
        inf.close()

        for comcitnmatch in COMCITN_EXP.finditer(data):
    
            thisidref = comcitnmatch.group(1)
            print thisidref

            oldstring = comcitnmatch.group()
            newstring = COMCITN2_EXP.sub('', oldstring)
            
            citnidref = None
            #if hasattr(self, 'idreflookup'):
            #    if self.idreflookup.has_key(thisidref):
            #        citnidref = self.idreflookup[thisidref]
            #    else:
            #        citnidref = None

            if citnidref is None:
                i = LionRecordSet()
                i.tablename='idrefmap'
                i.recordclass = BaseRecord
                i.indexsearch(slave=thisidref)
                if len(i) > 0:
                    citnidref = i[0].master

            if citnidref is not None:
                v = LionRecordSet()
                v.tablename = 'LionVolumes'
                v.recordclass = LionVolume
                v.indexsearch(idref=citnidref)
                
                
                if len(v) == 0:
                    v = LionRecordSet()
                    v.tablename = 'LionPoems'
                    v.recordclass = LionPoem
                    v.indexsearch(idref=citnidref)
                    if len(v) > 0:
                        print v[-1].title
                        print v[-1].filepath
                        print v[-1].idref                        
                        v[-1].SeekVolume()
                        v[-1].SeekAuthorAttributions()
                        v[-1].currentidref = thisidref
                        v[-1].xmlFields.append('currentidref')
                        if newstring.find('</somhead') > 0:
                            newstring = newstring.replace('</somhead', v[-1].FillTemplate() + '</somhead')
                        else:
                            newstring = newstring.replace('</comhd', v[-1].FillTemplate() + '</comhd')
                else:
                    v[-1].SeekAuthorAttributions()
                    v[-1].currentidref = thisidref
                    v[-1].xmlFields.append('currentidref')
                    newstring = newstring.replace('</comhd', v[-1].FillTemplate() + '</comhd')
                    
                if len(v) > 0:                    
                    data = data.replace(
                        oldstring,
                        newstring
                    )

        try:
            outf = open(self.filepath + '.cit', 'w')
            outf.write(data)
            outf.close()
            entityShield.entityUnprotect(self.filepath + '.cit')
        except UnicodeEncodeError:
            outf = open('unicode_erros.log', 'a')
            outf.write(self.filepath + '\n')
            outf.close()
                        
    def ExtractIdrefs(self):
        """Every division (<div>) throughout the file has a corresponding idref.
        For every idref that we have a citation row for we need to know all the idrefs
        that sit below that div in the hierarchy.
        
        Doing this with amara takes ages so a regex approach is probably more efficient.
        We get a list of all the idrefs in the file and cycle through it. If the idref 
        has a citation row then it becomes the current parent to which all the following lines
        are assigned until we hit another idref with a citation row."""
        
        IDREF_EXP = re.compile('<idref>(.*?)</idref>')

        inf = open(self.filepath, 'r')
        data = inf.read()
        inf.close()

        self.idreflookup = {}
        
        allidrefs = IDREF_EXP.findall(data)
        idrefswithvrows = []
        idrefswithprows = []
        for vol in self.volumes:
            idrefswithvrows.append(vol.idref)
            for p in vol.poem_set:
                idrefswithprows.append(p.idref)

        currentvkey = None
        currentpkey = None
        for idref in allidrefs:
            if idref in idrefswithprows:
                currentpkey = idref
            if idref in idrefswithvrows:
                currentvkey = idref
                currentpkey = None

            self.idreflookup[idref] = currentvkey

#            if currentpkey is not None:
#                if (int(idref[1]) > int(currentpkey[1])) or (currentpkey == idref):
#                    self.idreflookup[idref] = currentpkey

            if currentpkey is not None:
                if (currentpkey == idref):
                    self.idreflookup[idref] = currentpkey
                elif (int(idref[1]) <= int(currentpkey[1])):
                    currentpkey = None
                else:
                    self.idreflookup[idref] = currentpkey
                    

    def InsertIdrefs(self):
        idrefset = LionRecordSet()
        idrefset.tablename = 'idrefmap'
        idrefset.recordclass = BaseRecord
        
        for slave,master in self.idreflookup.items():
            newidrefmap = BaseRecord()
            newidrefmap.slave = slave
            newidrefmap.master = master
            newidrefmap.tablename = 'idrefmap'
            newidrefmap.databaseConnection = databaseConnection
            newidrefmap.requiredFields = ['slave', 'master']
            newidrefmap.optionalFields = []
            newidrefmap.doSQL("DELETE FROM idrefmap WHERE slave='"+slave+"' AND master='"+master+"';")
            newidrefmap.InsertIntoDB_new()

    def ExtractPoemPageNumbers(self):
    
        """Page numbers float throughout the file and are more likely outside the node
        which needs to know about them than inside.
        
        Rather than use an expression like u'preceding:://pb[1]/@n' which will be a bit
        time-consuming, we can build a dictionary mapping poem idrefs to page numbers
        for each file.
        
        """
        
        PB_EXP = re.compile('<pb n="(.*?)"')
        POEM_IDREF_EXP = re.compile('<poem.*?<idref>(.*?)</idref>', re.DOTALL)
        self.pagelookup = {}
        
        inf = open(self.filepath, 'r')
        data = inf.read()
        inf.close()

        # Set a default value for when there is no page number.
        for volume in data.split('<div0'):
            pagenumber = '[n. pag.]'
            for page in volume.split('<pb'):
    
                page = '<pb'+page
                if PB_EXP.search(page) is not None:
                    pagenumber = PB_EXP.search(page).group(1)

                for matchobj in POEM_IDREF_EXP.finditer(page):
                    idref = matchobj.group(1)
                    self.pagelookup[idref] = pagenumber

class LionBase(BaseRecord):
    """This class contains the methods shared between LionVolume and LionPoem."""

    def ParseBinding(self, volbinding):
        """There are three stages here.
        1. Populate the attributes from the relevant xpath expression
        2. Find all the child idrefs
        3. Pull out all the author attributions
        
        As it happens, doing the idrefs this way is pretty horribly slow so there is an optimized
        way of doing that separately with the ExtractIdrefs methods.        
        """
        xmlcharconverter = xmlbaseents().converter
        
        print 'Populating standard xpaths'
        # Stage 1. Cycle through the xpath expressions and 
        # see if we can populate them. Currently -- delimiter
        # is used for nodesets longer than 1.
        for field in self.xpaths.keys():
            setattr(self, field,
                "--".join([xmlcharconverter(n.__str__().replace('\n', ' ')) for n in volbinding.xml_xpath(self.xpaths[field])])
            )
        
        # Stage 2. Pull out the idrefs
        
        #def PullIdrefs():
        #    for idref in volbinding.xml_xpath(u'//idref'):
#
        #        newidrefmap = self.child_idref_set.recordclass()
        #        newidrefmap.slave = unicode(idref)
        #        newidrefmap.master = self.idref
        #        newidrefmap.tablename = 'idrefmap'
        #        newidrefmap.databaseConnection = databaseConnection
        #        newidrefmap.requiredFields = ['slave']
        #        newidrefmap.optionalFields = ['master']
        #        self.child_idref_set.append(newidrefmap)
    
        # Stage 3. Pull out the author attributions
        # (i) we need to have all the <attautid> tags containing the authorid = newatts/attautid
        # (ii) we need to pull out all <somauth> tags = comhd0//somauth
        # (iii) we need to pull out all local <attpoet> tags = attribs/attpoet
        # (iv) pull out all the bibliographic header tags <author> and <addauth>

        print 'Populating author xpaths'
        for authorxpath in self.authorexpressions:
            for xpnode in volbinding.xml_xpath(authorxpath):
                print xpnode.xml()[:250]
                
                # A cheat here to deal with author forms where they are delimited by /
                myauthorstring = xpnode.xml()
                # And a find/replace so we don't need separate methods for volauth and somauth
                myauthorstring = myauthorstring.replace('volauth', 'somauth')
                # And another one because drama volauths contain somauths...
                myauthorstring = myauthorstring.replace('<somauth><somauth>', '<somauth>')
                myauthorstring = myauthorstring.replace('<somauth>\n<somauth>', '<somauth>')
                myauthorstring = myauthorstring.replace('</', '<#')
                myauthors = myauthorstring.split('/')
                if myauthorstring.startswith('<somauth>') and len(myauthors) > 0:
                    myauthors = myauthors[:1] + ['<somauth>'+myauthor.lstrip() for myauthor in myauthors[1:]]
                primaryauthor = 'y'
                for myauthor in myauthors:
                    myauthor = myauthor.replace('<#', '</') + '<'
                    print "Split author: " + myauthor
                    newattribution = AuthorAttribution(rawtext=myauthor, parent=self, primaryauthor=primaryauthor)
                    newattribution.ParseRawText()
                    self.author_attribution_set.append(newattribution)
                    primaryauthor = 'n'
        
        self.DeduplicateAttributions()
        #for attr in self.author_attribution_set:
        #    print attr
                
    def DeduplicateAttributions(self):
                        
        # 1. Deduplicate on id
        print "Deduplicating on id"
        print "Currently there are " + str(len(self.author_attribution_set)) + " attributions."
        
        dedupset = LionRecordSet()
        authoridmap = {}

        
        # This is a bit confusing. Main thing to remember is that attr is, here, an AuthorAttribution
        # rather than an attribute of an object.
        for attr in self.author_attribution_set:
            if hasattr(attr, 'authorid'):
                if authoridmap.has_key(attr.authorid):
                    authoridmap[attr.authorid].append(attr)
                else:
                    authoridmap[attr.authorid] = [attr]
            else:
                dedupset.append(attr)

        for authorid in authoridmap.keys():
            newattr = AuthorAttribution()
            newattr.authorid = authorid
            for oldattr in authoridmap[authorid]:
                if hasattr(oldattr, 'namefromdata'):
                    newattr.namefromdata = oldattr.namefromdata
                if hasattr(oldattr, 'role'):
                    newattr.role = oldattr.role
                if hasattr(oldattr, 'idref'):
                    newattr.idref = oldattr.idref
                newattr.primaryauthor = oldattr.primaryauthor

            dedupset.append(newattr)

        self.author_attribution_set = dedupset
        
        print "Now there are " + str(len(self.author_attribution_set)) + " attributions."
        
        # 2. Deduplicate on name

        print "Deduplicating on name"

        dedupset = LionRecordSet()
        namemap = {}
        for attr in self.author_attribution_set:
            if hasattr(attr, 'namefromdata'):                
                if namemap.has_key(attr.namefromdata):
                    namemap[attr.namefromdata].append(attr)
                else:
                    fuzzyflag = 0
                    for likename in namemap.keys():
                        stringa = likename
                        stringb = attr.namefromdata
                        if stringa.find('(') > 1:
                            stringa = stringa[:stringa.find('(')]
                        if stringb.find('(') > 1:
                            stringb = stringb[:stringb.find('(')]
                        stringa = stringa.strip()
                        stringb = stringb.strip()
                        
                        if fuzzy(stringa, stringb)[1] > 90:
                            namemap[likename] = [attr]
                            fuzf = open('fuzzylog.log', 'a')
                            fuzf.write(likename + ' = ' + attr.namefromdata + '\n')
                            fuzf.close()
                            fuzzyflag = 1
                            continue
                        else:
                            fuzf = open('fuzzylog.log', 'a')
                            fuzf.write(likename + ' <> ' + attr.namefromdata + '\n')
                            fuzf.close()                        
                    if fuzzyflag == 0:
                        namemap[attr.namefromdata] = [attr]
            else:
                dedupset.append(attr)

        for authorname in namemap.keys():
            newattr = AuthorAttribution()
            newattr.namefromdata = authorname
            for oldattr in namemap[authorname]:
                if hasattr(oldattr, 'authorid'):
                    newattr.authorid = oldattr.authorid
                if hasattr(oldattr, 'role'):
                    newattr.role = oldattr.role
                if hasattr(oldattr, 'idref'):
                    newattr.idref = oldattr.idref
                newattr.primaryauthor = oldattr.primaryauthor

            dedupset.append(newattr)

        self.author_attribution_set = dedupset
        print "Now there are " + str(len(self.author_attribution_set)) + " attributions."

        # Final cleanup
        dedupset = LionRecordSet()
        for attr in self.author_attribution_set:
            if hasattr(attr, 'namefromdata'):
                if len(attr.namefromdata) > 1:
                    dedupset.append(attr)
        self.author_attribution_set = dedupset
        
        print "Now there are " + str(len(self.author_attribution_set)) + " attributions."
        
        

    def SeekAuthorAttributions(self):
        self.author_attribution_set.indexsearch(idref=self.idref)
        # Make sure primary author comes first
        orderedset = LionRecordSet()
        nonprimaryset = LionRecordSet()
        for attr in self.author_attribution_set:
            if attr.primaryauthor == 'y':
                orderedset.append(attr)
            else:
                nonprimaryset.append(attr)
        orderedset = orderedset + nonprimaryset
        self.author_attribution_set = orderedset
            

class LionVolume(LionBase):

    def __init__(self, parentfile=None):
        self.parentfile=parentfile
        self.tablename="LionVolumes"
        self.databaseConnection = databaseConnection
        self.templateclass=ris_volume_comcitn.ris_volume_comcitn

        self.requiredFields = []
        self.optionalFields = ['type', 'title', 'place', 'publisher', 'subject', 'filepubdate', 'pubdate',
                                'ISBN', 'liondatabase', 'idref', 'notes', 'copyright', 'filepath',
                                'country', 'city', 'description', 'filecity', 'filepublisher']
        self.xmlFields = ['author_attribution_set', 'child_idref_set', 'poem_set', 'excludere']
        
        self.author_attribution_set = LionRecordSet()
        self.author_attribution_set.tablename = 'AuthorAttributions'
        self.author_attribution_set.databaseConnection = databaseConnection
        self.author_attribution_set.recordclass = AuthorAttribution
        
        self.child_idref_set = LionRecordSet()
        self.child_idref_set.tablename = 'idrefmap'
        self.child_idref_set.databaseConnection = databaseConnection
        self.child_idref_set.recordclass = BaseRecord
        
        self.poem_set = LionRecordSet()
        self.poem_set.tablename = 'LionPoems'
        self.poem_set.databaseConnection = databaseConnection
        self.poem_set.recordclass = LionPoem

        # A collection of xpath expressions relative to the volume to populate fields
        self.xpaths = {
            'title': u'div1[1]/header/source/citn/pubtitle',
            'place': u'div1[1]/header/source/citn//city',
            'publisher': u'div1[1]/header/source/citn//publ',
            'subject': u'newatts/attsubj',
            'filepubdate': u'div1[1]/header/file/citn//pubdate',
            'pubdate': u'div1[1]/header/source/citn//pubdate',
            'country': u'div1[1]/header/source/citn//country',
            'city': u'div1[1]/header/source/citn//city',
            'description': u'div1[1]/header/source/citn//desc',
            'ISBN': u'div1[1]/header/source/citn/isbn',
            'liondatabase': u'div1[1]/header/file/citn//series',
            'idref': u'comhd0/idref',
            'notes': u'div1[1]/header/source/citn//pubnote',
            'copyright': u'div1[1]/header/source/citn//copyrite',
            'filecity': u'div1[1]/header/file/citn//city',
            'filepublisher': u'div1[1]/header/file/citn//publ'
        }

        # A collection of expressions follows for pulling out author information
        # It is in the form of a list of tuples where the first of each tuple is
        # an xpath expression and the second is a regular expression to pull out
        # the granular bits of information from that string representation of that
        # xml node.
        
        self.authorexpressions = [
#            u'newatts/attautid',
            u'comhd0//volauth'
#            u'div1[1]/header//author',
#            u'div1[1]/header//addauth'
        ]
    
        # Precompiled regular expression for removing contents of <exclude> from pubnote.
        self.excludere = re.compile('<exclude>.*?</exclude>', re.S)
    
    def ParseBinding(self, volbinding):
        LionBase.ParseBinding(self, volbinding)
        self.filepath = self.parentfile.filepath
        self.ExtractPoems(volbinding)

    def ExtractPoems(self, volbinding):
        for poem in volbinding.xml_xpath(u'.//poem'):
            newpoem = LionPoem(parentvolume=self)
            newpoem.ParseBinding(poem)
            self.poem_set.append(newpoem)

    def SeekPoems(self):
        self.poem_set.indexsearch(volume=self.idref)

    def workflow(self):
        self.SeekAuthorAttributions()
        self.SeekPoems()
        for poem in self.poem_set:
            poem.SeekAuthorAttributions()
    
class LionPoem(LionBase):

    def __init__(self, parentvolume=None):
        self.parentvolume=parentvolume
        self.tablename="LionPoems"
        self.databaseConnection = databaseConnection
        self.templateclass=ris_poem_comcitn.ris_poem_comcitn

        self.requiredFields = []
        self.optionalFields = ['type', 'title', 'startpage', 'idref', 'filepath', 'volume']
        self.xmlFields = ['author_attribution_set', 'child_idref_set', 'volume_set']
        self.author_attribution_set = LionRecordSet()
        self.author_attribution_set.tablename = 'AuthorAttributions'
        self.author_attribution_set.databaseConnection = databaseConnection
        self.author_attribution_set.recordclass = AuthorAttribution
        self.volume_set = LionRecordSet()
        self.volume_set.tablename = 'LionVolumes'
        self.volume_set.databaseConnection = databaseConnection
        self.volume_set.recordclass = LionVolume        
        self.child_idref_set = LionRecordSet()
        self.child_idref_set.tablename = 'idrefmap'
        self.child_idref_set.databaseConnection = databaseConnection
        self.child_idref_set.recordclass = BaseRecord

        # A collection of xpath expressions relative to the poem <poem> to populate fields
        self.xpaths = {
            'title': u'.//newatts/atttitle/mainhead',
            'idref': u'(*/idref)[1]'
        }

        self.authorexpressions = [
#            u'.//newatts/attautid',
#            u'.//attribs/attpoet',
            u'.//somhead/somauth'
        ]

    def ParseBinding(self, volbinding):
        LionBase.ParseBinding(self, volbinding)
        # Hack to catch poems like the ones in TS Eliot fa0501 where poem idref is one further div level down
        # than usual
        if self.idref == '':
            try:
                self.idref = volbinding.xml_xpath(u'(div/*/idref)[1]')[0].__str__()
                for attr in self.author_attribution_set:
                    attr.idref = self.idref
            except IndexError:
                pass
#        else:
#            poemlog = open('poemlog.txt', 'a')
#            poemlog.write(self.idref + '\n')
#            poemlog.close()
        self.filepath = self.parentvolume.parentfile.filepath
        self.volume = self.parentvolume.idref
        if not hasattr(self.parentvolume.parentfile, 'pagelookup'):
            self.parentvolume.parentfile.ExtractPoemPageNumbers()
        if self.parentvolume.parentfile.pagelookup.has_key(self.idref):
            self.startpage = self.parentvolume.parentfile.pagelookup[self.idref]

    def SeekVolume(self):
        self.volume_set.indexsearch(idref=self.volume)

    def workflow(self):
        self.SeekAuthorAttributions()
        self.SeekVolume()
        for vol in self.volume_set:
            vol.SeekAuthorAttributions()
    
class AuthorAttribution(BaseRecord):

    def __init__(self, rawtext=None, parent=None, primaryauthor='n'):
        self.rawtext=rawtext
        self.parent=parent
        self.primaryauthor = primaryauthor
        self.tablename="AuthorAttributions"
        self.databaseConnection = databaseConnection
        #self.templateclass=CSPrecord_template.CSPrecord_template

        self.requiredFields = ['id']
        self.optionalFields = ['authorid', 'role', 'primaryauthor', 'namefromdata', 'idref']
        self.xmlFields = ['author']

        if self.parent is not None:
            self.idref = self.parent.idref

    def __str__(self):
        ret =''
        if hasattr(self, 'authorid'):
            ret+= 'authorid: ' + str(self.authorid) + '\n'
        if hasattr(self, 'namefromdata'):
            ret+= 'namefromdata: ' + str(self.namefromdata) + '\n'
        if hasattr(self, 'role'):
            ret+= 'role: ' + str(self.role) + '\n'
        return ret

    def ParseRawText(self):
        """The incoming rawtext for an author attribution will be one of the following:
        <attautid>1234</attautid>
        <somauth>Morgan, Richard <sombiog>1234</sombiog> (ed).</somauth> where the sombiog
        and role in brackets are optional.
        <author> ... <nameinv>Morgan, Richard</nameinv> ... <authrole>(ed.)</authrole></author>
        <addauth> ... <nameinv>Morgan, Richard</nameinv> ... <authrole>(ed.)</authrole></addauth>
        <attpoet>Morgan, Richard (trans.)</attpoet>
        """

        print "Raw text: " + self.rawtext
        
        def fetchauthors():
            authorid_exp = re.compile('<attautid>(.*?)</attautid>')
            if authorid_exp.search(self.rawtext) is not None:
                self.authorid = authorid_exp.search(self.rawtext).group(1)
                if LIONAUTHORS.has_key(self.authorid):
                    self.namefromdata = LIONAUTHORS[self.authorid]
                    return
                else:
                    thisauthor = LionAuthor(authorid=self.authorid)
                    #thisauthor.ReadFromLionAuthRec()
                    #thisauthor.ReadFromAuthorGateway()
                    if hasattr(self, 'lcname'):
                        self.namefromdata = thisauthor.lcname
                    else:
                        self.namefromdata = 'unknown'
                return

            somauth_exp = re.compile('<somauth>')
#            somauth_name = re.compile('(?:<somauth>|[^<][/]{1}|^)(.*?)[</(]')
            somauth_name = re.compile('(?:<somauth>|[^<][/]{1}|^)(.*?)[</]')
            somauth_authorid = re.compile('<sombiog>(.*?)</sombiog>')
            somauth_role = re.compile('([(][^0-9]+?[)]).*?</somauth>')
            if somauth_exp.search(self.rawtext) is not None:
                try:
                    if somauth_name.search(self.rawtext) is not None:
                        self.namefromdata = somauth_name.search(self.rawtext).group(1).strip()
                        print 'somauth: ' + self.namefromdata
                    if somauth_authorid.search(self.rawtext) is not None:
                        self.authorid = somauth_authorid.search(self.rawtext).group(1)
#                    if somauth_role.search(self.rawtext) is not None:
#                        self.role = somauth_role.search(self.rawtext).group(1)
                except IndexError:
                    print self.rawtext
                return

            authorexp = re.compile('<author>|<addauth>')
            author_name = re.compile('<nameinv>(.*?)</nameinv>')
            author_role = re.compile('<authrole>(.*?)</authrole>')
            if authorexp.search(self.rawtext) is not None:
                try:
                    if author_name.search(self.rawtext) is not None:
                        self.namefromdata = author_name.search(self.rawtext).group(1)
                        print 'author/addauth: ' + self.namefromdata
                    if author_role.search(self.rawtext) is not None:
                        self.role = author_role.search(self.rawtext).group(1)
                except IndexError:
                    print self.rawtext
                return
        
            attpoetexp = re.compile('<attpoet>(.*?)</attpoet>')
            attpoetname = re.compile('(?:<attpoet>|^)(.*?)[(<]')
            attpoetrole = re.compile('([(][^0-9]+?[)]).*?</attpoet>')
            if attpoetexp.search(self.rawtext) is not None:
                try:
                    if attpoetrole.search(self.rawtext) is not None:
                        self.role = attpoetrole.search(self.rawtext).group(1)
                    if attpoetname.search(self.rawtext) is not None:
                        self.namefromdata = attpoetname.search(self.rawtext).group(1)
                        print 'attpoet: ' + self.namefromdata
                except IndexError:
                    print self.rawtext        
        
        fetchauthors()
#        if hasattr(self, 'namefromdata'):
#            self.namefromdata = self.namefromdata.replace('&amp;ndash;', '-')
#            self.namefromdata = self.namefromdata.replace('&ndash;', '-')
        
    def SeekAuthor(self):
        pass
    
class LionAuthor:
    
    def __init__(self, authorid=None):
        self.authorid = authorid
        
    def ReadFromLionAuthRec(self):
    
        print "Reading from LionAuthRec"
        assert self.authorid
        auth_exp = re.compile('<rec>.*?<authorid>'+self.authorid+'</authorid>.*?</rec>', re.DOTALL)
        lcname_exp = re.compile('<lcname>(.*?)</lcname>')
        if auth_exp.search(lionauthrec) is not None:
            thisauthor = entityShield.entityProtectString(auth_exp.search(lionauthrec).group())
            if lcname_exp.search(thisauthor) is not None:
                self.lcname = lcname_exp.search(thisauthor).group(1)
                LIONAUTHORS[self.authorid] = self.lcname
        else:
            return
    
    def ReadFromAuthorGateway(self):
        """Read in controlled information about an author from an
        XML gateway to an Oracle database of authors."""
        import entityShield
        assert self.authorid
        sqlquery = 'select * from new_bbdb.author where id=%s' % self.authorid
        baseurl = 'http://reynard.private.chadwyck.co.uk:9100/gateway/xmlgateway.php'
        # print baseurl +'?' + urlencode({'sql': sqlquery})
        try:
            f = urllib2.urlopen(baseurl+'?'+urlencode({'sql': sqlquery}))
            data = entityShield.entityProtectString(f.read())
        except urllib2.URLError:
            print baseurl+'?'+urlencode({'sql': sqlquery})
            return
        self.authordoc = amara.parse(data)
        self.lcname = self.authordoc.main.DATA_RECORD.LCNAME.__unicode__()
        LIONAUTHORS[self.authorid] = self.lcname
        