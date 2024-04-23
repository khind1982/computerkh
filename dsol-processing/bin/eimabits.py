# -*- mode: python -*-

import os
import re
import sys
import warnings

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import MySQLdb


def populatethreading(product, directory):

    dbargs = {'user': 'root',
                'db': product,
                'host': 'mysql-server'
                }

    dbconn = MySQLdb.connect(**dbargs)
    cu = dbconn.cursor()
    # need to empty db here - or do it by article id later?

    #cu.execute("""TRUNCATE TABLE threading;""")

    pagere = re.compile(r'<APS_page_image.*?>(.*?)</APS_page_image>')
    pageseqre = re.compile('<APS_page_sequence>(.*?)</APS_page_sequence>')
    filesseen = 0

    def createimagepath(imagename):
        imagenamere = re.compile('((?:APS_)?(.*?)_.*?)-(.*?)\.jp(g|2)')
        if imagenamere.search(imagename) == None:
            print "Bad image name: " + imagename
            return ''
        else:
            pubid = imagenamere.search(imagename).group(2)
            issueid = imagenamere.search(imagename).group(1)
            # This is for Trench Journals, where the images are
            # delivered as JPEG2000, but are converted to plain
            # JPEG during the stamping process.
            imagename = imagename.replace('jp2', 'jpg')
            imagepath = '/'.join(['', pubid, issueid, 'jpeg', imagename])
            return imagepath

    for direc in os.walk(directory):
        for infile in direc[2]:
            if infile[-4:] == '.xml':
                filesseen += 1

                with open(os.path.join(direc[0], infile), 'r') as inp:
                    pageimages = {}
                    #recordid = infile[4:-4]
                    recordid = infile.replace('APS_', '')
                    recordid = recordid.replace('_final', '')
                    recordid = recordid.replace('.xml', '')
                    #pagelist = []

                    currentzone = ''
                    inthezone = 0

                    for line in inp:
                        if inthezone == 1:
                            currentzone += line
                        if line.find('</APS_zone>') != -1:
                            inthezone = 0
                            #outfile.write("A zone:" + currentzone)
                            try:
                                pageimage = pagere.search(currentzone).group(1)
                            except AttributeError:
                                print >> sys.stderr, "================================================"
                                print >> sys.stderr, "Error in %s" % infile
                                print >> sys.stderr, "Somewhere in or near %s" % currentzone
                                print >> sys.stderr, "================================================"
                                raise
                            pageseq = pageseqre.search(currentzone).group(1)
                            if pageimage not in pageimages:
                                pageimages[pageimage] = pageseq, createimagepath(pageimage)
                            currentzone = ''
                        if line.find('<APS_zone ') != -1:
                            inthezone = 1
                            currentzone = line


                        # """
                        # if pagere.search(line) != None:
                        #     pageimage = pagere.search(line).group(1)
                        #     if pageimage not in seenpages:
                        #         seenpages[pageimage] = ''
                        #         pagelist.append(createimagepath(pageimage))
                        # """

                    #sequenceno = 0
                    for page in pageimages.keys():
                        #sequenceno += 1
                        #sqlstatement = ("""INSERT INTO threading (aid, pageno, path) VALUES (%s, %s, %s);"""
                        #                                        % (recordid, str(sequenceno), page))
                        #print sqlstatement
                        cu.execute("""INSERT INTO threading (aid, pageno, path) VALUES ("%s", %s, "%s");"""
                                                            % (recordid, pageimages[page][0], pageimages[page][1]))

    cu.close()
    dbconn.close()

    print ' '.join(['Seen', str(filesseen), 'files'])
