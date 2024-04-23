#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

import re

#/dc/elp/lionref/mla/utils_suite/utf8new_lut.mla is initially a copy of \\Mclaren\elp\lionref\mla\utils_suite\utf8new.lut
#/dc/elp/lionref/mla/utils_suite/utf8new_lut.mla will be updated  but not /dc/elp/lionref/mla/utils_suite/utf8new_lut
#this will allow to compare the original list to the one updated over the time


#from addentity import * 
#add()

#NEW unicode code point|new entity| new entities value
#will be first entered in /dc/elp/lionref/mla/utils_suite/newentity.txt'

def add():
    addtomap=open('/dc/lion3/data/control/entities_map.mla','a')
    addtolut=open('/dc/elp/lionref/mla/utils_suite/utf8new_lut.mla','a')
    newent=open('/dc/elp/lionref/mla/utils_suite/newentity.txt','rw')
    entconvregex='^\d+?\|&.*?\|.*'
    for line in newent.xreadlines():
        findentconv=re.search(entconvregex,line)
        if findentconv !=None:
            parts=line.split('|')
            print parts
            codep=unichr(int(parts[0]))
            newe=parts[1]
            repchar=parts[2]
            lutline=codep.encode('utf-8')+'|'+newe
            addtolut.write(lutline +'\n')
            mapline=newe+'|'+repchar
            addtomap.write(mapline)
    
    addtomap.close()
    addtomap.close()
    newent.close()
    
    clearnewent=open('/dc/elp/lionref/mla/utils_suite/newentity.txt','w')    
    clearnewent.write('#for each new entity enter the 3 following pipe separated values(each mapping should be on a new line...do not precede them with the comment sign "#")#unicode code point|new entity| new entities value\n#examples:\n# 123|&first|a\n# 456|&second|k)\n')
    clearnewent.close()

if __name__ == '__main__':
    add()

