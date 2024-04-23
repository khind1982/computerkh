#!/usr/local/versions/Python-2.6.2/bin/python2.6

import os, os.path, re, sys, shutil

def check_stdzd(inputdir):

    authelemre = re.compile('<mods:namePart>(.*?)</mods:namePart>', re.I)
    authlupre = re.compile('^(.*?)\|')
    imprintelemre = re.compile('<mods:publisher>(.*?)</mods:publisher>', re.I)
    imprintlupre = re.compile('<publisher_printer>(.*?)</publisher_printer>', re.I)
    placeelemre = re.compile('<mods:placeTerm>(.*?)</mods:placeTerm>', re.I)
    placelupre = re.compile('<place_of_publication>(.*?)</place_of_publication>', re.I)

    authorluppath = '/dc/eurobo/content/authors/author_lookup.lut'
    placeluppath = '/dc/eurobo/content/metadata_enhancement/imprint_places.lut'
    imprintluppath = '/dc/eurobo/content/metadata_enhancement/imprint_names.lut'


    standardauthors = getlupkeys(authorluppath, authlupre)
    standardimprints = getlupkeys(imprintluppath, imprintlupre)
    standardplaces = getlupkeys(placeluppath, placelupre)
    
    filestates = {}
    infilecount = 0
    
    for filename in os.listdir(inputdir):
        #print "got here"
        infilecount += 1
        print infilecount
        if not filename.endswith(".xml"):
            continue
        #if not os.path.exists(os.path.join(olddir, 'bakfiles20130916', filename + ".bak")):
        #    #print os.path.join(olddir, filename + ".bak")
        #    continue
        with open(os.path.join(inputdir, filename), 'r') as fi:
            fileok = True
            for line in fi:
                if authelemre.search(line) != None:
                    #print "got an author"
                    author = authelemre.search(line).group(1)
                    if author not in standardauthors:
                        #print "not in the author lup though"
                        fileok = False
                if placeelemre.search(line) != None:
                    #print "got a place"
                    place = placeelemre.search(line).group(1)
                    if place not in standardplaces:
                        #print "not in place lookup though"
                        if place.find("COUNTRY") == -1:
                            fileok = False
                if imprintelemre.search(line) != None:
                    #print "got an imprint"
                    imprint = imprintelemre.search(line).group(1)
                    if imprint not in standardimprints:
                        #print "not in imprint lup though"
                        if imprint.find("CCS Content Conversion Specialists GmbH") == -1:
                            fileok = False
        #print fileok
        #if fileok == True:
        #    print filename
        #    shutil.move(os.path.join(olddir, filename), newdir)
        filestates[filename] = fileok
        
    filestates = checkcompletevolumes(filestates)
        
    for filename in filestates.keys():
        if filestates[filename] != False:
            print filename
        
def checkcompletevolumes(filestates):

    volumes = {}
    #print len(filestates.keys())
    #filecount = 0
    #filecountb = 0
    for filename in filestates.keys():
        volumeid = filename[:-8]
        if not volumes.has_key(volumeid):
            volumes[volumeid] = True
        if filestates[filename] == False:
            volumes[volumeid] = False
        #filecount += 1
        #print "".join([str(filecount), " files checked for complete volumes"])
        
    for filename in filestates.keys():
        volumeid = filename[:-8]
        if volumes[volumeid] == False:
            filestates[filename] = False
        #filecountb += 1
        #print "".join([str(filecountb), " files updated after volume check"])
            
    return filestates
        
def getlupkeys(luppath, lupre):
    lupkeys = {}
    with open(luppath, 'r') as lup:
        for line in lup:
            if lupre.search(line) != None:
                lupkeys[lupre.search(line).group(1)] = ''
    return lupkeys
    
if __name__ == '__main__':

    check_stdzd(sys.argv[1])