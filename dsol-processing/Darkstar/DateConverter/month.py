'''
month - a set of functions intended for use with the Darkstar date filter
library.

Functions:
    
    num_to_abbrev() -> takes a one or two digit month representation and returns
        a three-letter abbreviation
    num_to_name() -> takes a one or two digit month representation and returns
        the month's full name
    name_to_num() -> takes a month's full name, or its three-letter abbreviation,
        and returns a two-digit numerical representation.

Constants:
    
    months_num2name = a dict mapping numerical representation to full name
    months_name2num = a dict mapping in the opposite direction. Constructed from
        months_num2name by simply inverting keys and values.


>>> numeric = range(1, 13)
>>> for number in numeric:
...   num_to_abbrev(number)
'Jan'
'Feb'
'Mar'
'Apr'
'May'
'Jun'
'Jul'
'Aug'
'Sep'
'Oct'
'Nov'
'Dec'
>>> for num in range(1, 13):
...   num_to_name(num)
'January'
'February'
'March'
'April'
'May'
'June'
'July'
'August'
'September'
'October'
'November'
'December'
>>> months = []
>>> for num in range(1, 13):
...   months.append(num_to_abbrev(num))
>>> for mon in months:  #doctest: +ELLIPSIS
...   name_to_num(mon)
'01'
'02'
'03'
...
'10'
'11'
'12'
'''

import re
from base import *

__all__ = ["num_to_name", "num_to_abbrev", "name_to_num"]

months_num2name = { '01':'January', '02':'February', '03':'March', 
           '04':'April', '05':'May', '06':'June',
           '07':'July', '08':'August', '09':'September', 
           '10':'October', '11':'November', '12':'December' }

months_name2num = dict([(v, k) for k, v in months_num2name.iteritems()])

def num_to_name(month):
    return months_num2name[zero_pad(month)]
    
def num_to_abbrev(month):
    return months_num2name[zero_pad(month)][0:3]
    
def name_to_num(month):
    for key in months_name2num.keys():
        if re.match(month, key):
            return months_name2num[key]

if __name__ == "__main__":
    import doctest
    doctest.testmod()