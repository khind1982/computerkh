#!/usr/local/bin/python2.7

import re
import glob
import os.path

masterfilelocations = [
                        '/dc/lion3/data/poetry',
                        '/dc/lion3/data/prose',
                        '/dc/lion3/data/drama'
                        ]

errlogfile = "dupe_idrefs.err"
reportlogfile = "dupe_idrefs.log"

def createinputfilelist():
    filelist = []
    for path in masterfilelocations:
        filesfrompath = glob.glob(os.path.join(path, '*.one'))
        filelist.extend(filesfrompath)
    return filelist
                                    
class IDRefStore:

    def __init__(self):
        self.idrefs = {
                        'idref': {},
                        'attidref': {},
                        'noteidref': {},
                        'tableidref': {}
        }
        self.expectedcounts = {
                            'idref': 1,
                            'attidref': 2,
                            'noteidref': 1,
                            'tableidref': 1
                            }

    def addnewidref(self, idreftype, idref, location):
        relevantdict = self.idrefs[idreftype]
        if not idref in relevantdict:
            relevantdict[idref] = []
        relevantdict[idref].append(location)

    def writeduplicates(self, outfile):
        with open(outfile, 'w') as log:
            for idreftype in self.idrefs:
                for idref in self.idrefs[idreftype]:
                    idrefcount = len(self.idrefs[idreftype][idref])
                    if idrefcount > self.expectedcounts[idreftype]:
                        log.write("{0} {1} occurs {2} times:\n".format(
                                                idreftype,
                                                idref,
                                                unicode(idrefcount)
                                                ))
                        for filename, lineno in self.idrefs[idreftype][idref]:
                            log.write("File {0}: Line number {1}\n".format(
                                                    filename,
                                                    unicode(lineno)
                                                    ))


def getidrefsfromfile(filepath, errlog):
    with open(filepath, 'r') as lionfile:
        for lineno, line in enumerate(lionfile, 1):
            try:
                testlinehasnoerrors(line)
            except IncompleteElementException as iee:
                errlog.write("{0}: Line {1}: {2}\n".format(
                                                 filepath,
                                                 unicode(lineno),
                                                 unicode(iee)
                                                 ))

            for idref in re.findall('<idref>([^<]*?)</idref>', line):
                yield idref, lineno, 'idref'
            for attidref in re.findall('<attidref>([^<]*?)</attidref>', line):
                yield attidref, lineno, 'attidref'
            for noteidref in re.findall(
                                    '<note[^>]*?idref=["\'](.*?)["\']',
                                    line
                                    ):
                yield noteidref, lineno, 'noteidref'
            for tableidref in re.findall(
                                    '<table[^>]*?idref=["\'](.*?)["\']',
                                    line
                                    ):
                yield tableidref, lineno, 'tableidref'

def testlinehasnoerrors(line):
    """Because we're not parsing the files properly we need to check for
    things like idref elements spread across multiple lines.

    """

    tests = [
            ('<idref>[^<]*?<(?!/idref>)',
                                "<idref> not closed before next tag"),
            ('<idref>[^<]*?$', "<idref> not closed before end of line"),
            ('<attidref>[^<]*?<(?!/attidref>)',
                                "<attidref> not closed before next tag"),
            ('<attidref>[^<]*?$',
                                "<attidref> not closed before end of line")
            ]
            
    for regex, errormsg in tests:
        if re.search(regex, line):
            raise IncompleteElementException(errormsg)

    notematch = re.search('<note [^>]*?[>|$]', line)
    if notematch:
        if not re.search('idref=', notematch.group(0)):
            raise IncompleteElementException(
                        "Opening <note tag but no idref on same line"
                        )
                        
    tablematch = re.search('<table [^>]*?[>|$]', line)
    if tablematch:
        if not re.search('idref=', tablematch.group(0)):
            raise IncompleteElementException(
                        "Opening <table tag but no idref on same line"
                        )

    # Locate kittens
    #if re.search('kitten', line):
    #    raise IncompleteElementException("There is a kitten in this file")

def getallidrefs(filelist, errlogfile):
    allidrefs = IDRefStore()
    filecount = 0
    with open(errlogfile, 'w') as errlog:
        for infile in filelist:
            for idref, lineno, idreftype in getidrefsfromfile(infile, errlog):
                allidrefs.addnewidref(idreftype, idref, (infile, lineno))
            filecount += 1
            if filecount % 100 == 0:
                print "{0} files checked so far...".format(unicode(filecount))
    return allidrefs

class IncompleteElementException(Exception):
    pass

def test():
    filelist = createinputfilelist()
    allidrefs = getallidrefs(filelist)
    allidrefs.writeduplicates(reportlog)


if __name__ == '__main__':
    
    print "Checking for duplicate idrefs in all *.one files in " \
                    "the following locations:"
    for location in masterfilelocations:
        print location 
    
    filelist = createinputfilelist()
    allidrefs = getallidrefs(filelist, errlogfile)
    allidrefs.writeduplicates(reportlogfile)

    print "Check for duplicate idrefs has finished."
    print "See dupe_idrefs.log for any duplicates found."
    print "See dupe_idrefs.err for any issues that may have prevented " \
                    "script from finding them."
    
# if only LION were XML data with referenced DTD...    
    #filexml = etree.parse(filepath)
    #for idrefelem in filexml.xpath('//idref'):
    #    print idrefelem.text
    #    print idrefelem.sourceline

# The lxml HTML Parser does not capture line number - sourceline is None in every case
    #parser = etree.HTMLParser()
    #filexml = etree.parse('/dc/lion3/data/poetry/abarnett.one', parser)
    #for idrefelem in filexml.xpath('//idref'):
    #    print idrefelem.text
    #    print idrefelem.sourceline

