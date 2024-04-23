import re
from base import *

quarters = {'First': '0101',
            'Second': '0401',
            'Third': '0701',
            'Fourth': '1001'
            }

numericQs = {'31': '0101',
             '32': '0401',
             '33': '0701',
             '34': '1001'
             }
            
qs = {  
    1:['First',  '31', '0101'],
    2:['Second', '32', '0401'],
    3:['Third',  '33', '0701'],
    4:['Fourth', '34', '1001']
    }
             
def quarter2pqan(datestring):
    if re.search(r'^(First|Second|Third|Fourth),? Quarter \d{4}', datestring):
        return unicode(datestring)
    elif re.search(r'^\d{4}3(1|2|3|4)$', datestring):
        y, q = re.search(r'^(\d{4})3(\d)$', datestring).group(1, 2)
        return unicode(qs[int(q)][0] + ' Quarter ' + y)
        
def quarter(datestring):
    q, y = re.search(r'^(First|Second|Third|Fourth),? Quarter (\d{4})$', datestring).group(1, 2)
    return unicode(y + quarters[q])
