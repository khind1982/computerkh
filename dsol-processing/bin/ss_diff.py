
import re
import os, os.path

"""
Go through all old files constructing a dictionary mapping record to
file it's in and location in file.

go through new files record by record
for each record use lookup to identify where previous record version is
open old file at that point and read out the next record
compare the two, ignoring lastlegacyupdatetime and actioncode
if there is a difference, output the legacyid to a file

Separate script: given the legacyid list, go through new data and copy
any records on that list into one or more new files (depending on number
of ids we got).

Likely problems:
Dictionary of old file locations may be too big to hold in memory
Means opening at least one big file per record

If the dictionary is too big, try creating a file mapping each new record's
location to each old record's location.

Not sure how to get round file I/O problem. Use the info in the filemap to
sort the files cleverly? I.e. do all operations where the oldfile/newfile
combination is the same together. You can figure out how many I/O operations
this will result in in advance.

Still to do: handle cases where new record has no equivalent in old record set
"""

class IngestFile:
    """
    Properly I should find a way of making this a subclass of file or similar;
    for now it can just open a file itself
    
    """

    def __init__(self, filename):
        self.sourcefile = filename
        self.openedfile = None
        
    def openfile(self):
        self.openedfile = open(self.sourcefile, 'r')

    def generate_ingest_records(self):
        """Return each ingest record from the input file in turn, with
        everything outside <IngestRecord> stripped.

        """
        if self.openedfile == None:
            self.openedfile = open(self.sourcefile, 'r')
        inrec = 0
        rec = ''
        recoffset = 0
        line = self.openedfile.readline()
        while line:
            recend = line.find('</IngestRecord>')
            if recend != -1:
                rec += line[:recend + 15]
                #ingrec = IngestRecord(rec)
                yield rec, recoffset
                #rec = ''
                inrec = 0
            recstart = line.find('<IngestRecord>')
            if recstart != -1:
                recoffset = self.openedfile.tell() - len(line) + recstart
                rec = line[recstart:]
                inrec = 1
            elif inrec == 1:
                rec += line
            line = self.openedfile.readline()
        self.openedfile.close()
        self.openedfile = None
            
    def getspecifiedrecord(self, offset):
        """Given a specific byte offset which should be a start of record,
        open file, seek to this offset, read to the end of record and
        then return the record.

        """
        
        self.openedfile = open(self.sourcefile, 'r')
        self.openedfile.seek(offset, 0)
        line = self.openedfile.readline()
        rec = ''
        while line:
            recend = line.find('</IngestRecord>')
            if recend != -1:
                rec += line[:recend + 15]
                #ingrec = IngestRecord(rec)
                return rec
            else:
                rec += line
            line = self.openedfile.readline()
        self.openedfile.close()
        self.openedfile = None
        

class IngestRecord:

    def __init__(self, rawrecord):
        self.rawrecord = rawrecord
        self.idre = re.compile('<LegacyID>(.*?)</LegacyID>')
        self.lastlegacyupdatetimere = re.compile('<LastLegacyUpdateTime>.*?</LastLegacyUpdateTime>')
        self.actioncodere = re.compile('ActionCode>.*?</ActionCode>')
        
    def get_id(self):
        """Search raw record text for an ID. This is pretty much guaranteed to
        work, but it would be good to get some proper error handling written.
        
        """

        idmatch =  self.idre.search(self.rawrecord)
        if idmatch == None:
            print "No ID found for record:\n\n" + self.rawrecord
        else:
            self.recid = idmatch.group(1)
            
    def prepareforcomparison(self):
        self.comparisonstring = self.rawrecord
        self.comparisonstring = self.lastlegacyupdatetimere.sub('', self.comparisonstring)
        self.comparisonstring = self.actioncodere.sub('', self.comparisonstring)

class RecordLocationsDict(dict):

    def __init__(self, filelist):
        self.recordfiles = filelist
        
    def populate(self):
        """Go through all the files in filelist gathering record ids; put each
        record id in self, mapped to file in which record is located and byte
        offset for the start of record.

        """
        
        for fi in self.recordfiles:
            ingfi = IngestFile(fi)
            for rec, offset in ingfi.generate_ingest_records():
                rec = IngestRecord(rec)
                rec.get_id()
                self[rec.recid] = fi, offset

class SteadyStateDiffProcessor:

    def __init__(self, oldfiles, newfiles):
        self.oldfiles = oldfiles
        self.newfiles = newfiles
        self.idlist = []
        self.newidlist = []
        
    def process(self):
        recordlocations = RecordLocationsDict(self.oldfiles)
        recordlocations.populate()
        
        comparer = RecordComparer()

        for fi in self.newfiles:
            ingfi = IngestFile(fi)
            for rec, offset in ingfi.generate_ingest_records():
                rec = IngestRecord(rec)
                rec.get_id()
                if rec.recid in recordlocations:
                    oldfi = IngestFile(recordlocations[rec.recid][0])
                    oldrec = oldfi.getspecifiedrecord(recordlocations[rec.recid][1])
                    oldrec = IngestRecord(oldrec)
                    changedrec = comparer.compare(oldrec, rec)
                    if changedrec != None:
                        self.idlist.append(changedrec)
                    comparer.report()
                else:
                    self.newidlist.append(rec.recid)
                
        idfile = open('ss_diff_ids.txt', 'w')
        for recid in self.idlist:
            idfile.write(recid + "\n")
        idfile.write("\n\nNew records:\n\n")
        for recid in self.newidlist:
            idfile.write(recid + "\n")
        idfile.close()

class RecordComparer:

    def __init__(self):
        self.count = 0
        self.diffs = 0
        self.nodiffs = 0

    def compare(self, oldrecord, newrecord):
        oldrecord.prepareforcomparison()
        newrecord.prepareforcomparison()
        self.count += 1
        if newrecord.comparisonstring == oldrecord.comparisonstring:
            self.nodiffs += 1
            return None
        else:
            self.diffs += 1
            return newrecord.recid

    def report(self):
        print ''.join([str(self.count), " records compared, ", str(self.diffs),
                " with differences, ", str(self.nodiffs), " without."])

class IngestFileWriter:
    
    def __init__(self, filelimit=5000):
        """Take the output of ingestrecordsource and populate ingest
        record files with it.
        
        """
        
        self.filelimit = filelimit
        self.currentfile = None
        self.currentfilecount = 0
        self.totalcount = 0
        self.basefilename = 'CH_SS_general_update_'
        self.filecount = 0
            
    def writeonerecord(self, record):
        
        if self.currentfile == None:
            self.currentfile = open(self.generatenextfilename(), 'w')
            self.currentfilecount = 0
        
        self.currentfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.currentfile.write(''.join([record, '\n']))
        self.totalcount += 1
        self.currentfilecount += 1
        
        if self.currentfilecount == self.filelimit:
            self.currentfile.close()
            self.currentfile = None
        
    def setbasefilename(self, basefilename):
        self.basefilename = basefilename
        
    def generatenextfilename(self):
        nextfilename = self.basefilename + str(self.filecount).zfill(3) + '.xml'
        self.filecount += 1
        return nextfilename

    def tidyup(self):
        """If the current file is still open, close it."""
       
        if self.currentfile != None:
            self.currentfile.close()
            self.currentfile = None

def extractingestrecordsbyid(iddict, filelist, baseoutputfilename):

    writer = IngestFileWriter()
    writer.setbasefilename(baseoutputfilename)
    
    for fi in filelist:
        ingfi = IngestFile(fi)
        for rec, offset in ingfi.generate_ingest_records():
            rec = IngestRecord(rec)
            rec.get_id()
            if rec.recid in iddict:
                writer.writeonerecord(rec.rawrecord)
    
    writer.tidyup()


def test():
    """Compare two specified input files in the current directory."""
    
    proc = SteadyStateDiffProcessor(['CH_SS_iimp_08092010_000.xml'], ['CH_SS_iimp_08122010_000.xml'])
    proc.process()

def test2():
    """Compare a set of files specified in a list with files in a specified directory.
    NB the list just contains filenames so the directory path is prepended as well.
    
    """

    oldfiles = []
    oldlistfile = open('/dc/scratch/vega/samples/bp/prod2/ssjournals.log', 'r')
    for line in oldlistfile:
        oldfiles.append(os.path.join('/dc/scratch/vega/samples/bp/prod2', line.strip()))
    newfiles = []
    for fi in os.listdir('/dc/scratch/vega/samples/bp/ss'):
        if fi[-4:] == '.xml':
            newfiles.append(os.path.join('/dc/scratch/vega/samples/bp/ss', fi))
    proc = SteadyStateDiffProcessor(oldfiles, newfiles)
    proc.process()
        
def testextraction():
    """Extract the records specified in an id list file from the specified set
    of files. Write them to a new set of files with the specified base name appended
    with 'nnn.xml' where nnn is a three-digit counter.
    
    """
    
    iddict = {}
    idfile = open('/home/twilson/svn/trunk/cstore/gs4/bin/ss_diff_ids_bp_secondrun_input.txt', 'r')
    for line in idfile:
        iddict[line.strip()] = ''
    filelist = []
    for fi in os.listdir('/dc/scratch/vega/samples/bp/ss/'):
        if fi[-4:] == '.xml':
            filelist.append(os.path.join('/dc/scratch/vega/samples/bp/ss/', fi))
    extractingestrecordsbyid(iddict, filelist, '/dc/scratch/vega/samples/bp/ss/final/CH_SS_bp_20101217_extra_')
