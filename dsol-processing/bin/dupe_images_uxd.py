
import re, os, shutil

"""
Script for task requested by UXD August 2010

Copy config info from one product and apply it to all other products in a list
This means take the sample string below and repeat it for every product, replacing
product name each time.

Then make copies of the associated image files and put them in their own directory,
one directory per product. Plus create a copy of the '_small' file and store that
in the one master '_small' directory.
"""

samplestring = """
newsstand.gridStyle=imageLayout1
newsstand.image1Title=Newspaper on the press
newsstand.image2Title=Internet presence for newspapers
newsstand.image3Title=Current events on TV
newsstand.image4Title=Smart phone
newsstand.image5Title=Radio dial
"""

def makemonikerlist(monikerfile):

    monikers = []
    reanytext = re.compile('\w')
    
    mnkf = open(monikerfile, 'r')
    for line in mnkf:
        if reanytext.search(line) != None:
            monikers.append(line.strip())
            
    mnkf.close()
    return monikers
    
    
def makepropertieslist(monikerlist, outfile):

    outf = open(outfile, 'w')
    for m in monikerlist:
        outf.write(',' + m)
    outf.write('\n\n')
    for m in monikerlist:
        outf.write(samplestring.replace('newsstand', m))
    outf.close()
    
def copyfolders(monikerlist, parentpath):

    for m in monikerlist:
        """Make the small file"""
        shutil.copy(parentpath + '/_small/newsstand_small.png', parentpath + '/_small/' + m + '_small.png')
        """Make a new directory for the moniker and copy the images from newsstand"""
        os.mkdir(parentpath + '/' + m)
        for fi in os.listdir(parentpath + '/newsstand'):
            if fi[-4:] == '.jpg':
                shutil.copy(parentpath + '/newsstand/' + fi, parentpath + '/' + m + '/' + fi)
    
if __name__ == '__main__':
    
    monikerlist = makemonikerlist('monikers1.txt')
    makepropertieslist(monikerlist, 'test.txt')
    copyfolders(monikerlist, '/home/twilson/temp/product_image_duping')