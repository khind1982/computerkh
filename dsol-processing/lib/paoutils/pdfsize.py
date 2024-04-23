import sys
import os
import re

sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib'))

from stat import ST_SIZE
from dbcache import DBCache

from commonUtils.fileUtils import locate

pdf_size_cache = DBCache(os.path.abspath(os.path.join(__file__, '../../../var/pio/pdf_size_cache1')))

class SkipTabFileException(Exception): pass

def pdfSizeEstimate(originalCHLegacyID, originalPubID):
    cachedValue = pdf_size_cache[originalCHLegacyID]
    if cachedValue is not None:
        return cachedValue
    else:
        try:
            with open ('/dc/pao/pci/build/threading/%s.tab' % originalPubID, 'r') as threading:
                imageFiles = [line.replace('\t', ' ').split(' ')[-1].strip() for line in threading.readlines() if re.search(originalCHLegacyID, line)]
        except IOError:
            raise SkipTabFileException
            #print "%s, %s" % (originalCHLegacyID, originalPubID)
            #raise
        pdfSize = 0
        imgPath = '/sd/web/images/pao'
        for image in imageFiles:
            try:
                pdfSize += os.stat(imgPath + image)[ST_SIZE]
            except OSError:
                pass
        pdfSize = str(int(pdfSize * 1.1))    
        pdf_size_cache[originalCHLegacyID] = pdfSize
        return pdfSize

if __name__ == '__main__':
    for filename in locate('*.gen', root='/dc/pcinext'):
        journalID = os.path.basename(filename)
        journalID = os.path.splitext(journalID)[0]
        with open(filename, 'r') as infile:
            for line in infile:
                if line.startswith('035'):
                    docid = line[8:].strip()
                    try:
                        pdfSizeEstimate(docid, journalID)        
                    except SkipTabFileException:
                        break
