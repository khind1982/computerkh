'''
A set of functions to convert a 6 or 8 digit datestring into the ProQuest
alphanumeric format and the ProQuest default format.

>>> EUdate2pqan('20021201')
'Jan 12, 2002'
>>> USdate2pqan('20021201')
'Dec 1, 2002'
>>> EUdate2pqan('20020101')
'Jan 1, 2002'
>>> split_datestring('20021201')
['2002', '12', '01']
>>> split_datestring('021201')
['02', '12', '01']
'''

__all__ = ['EUdate2pqan', 'USdate2pqan', 'EUdate2pqdef', 'USdate2pqdef',
           'pqdef2pqan']

from base import *
from month import *

def EUdate2pqan(datestring):
    year, day, month = _split_datestring(datestring)
    return date2pqan(year, month, day)

def USdate2pqan(datestring):
    year, month, day = _split_datestring(datestring)
    return date2pqan(year, month, day)

def date2pqan(year, month, day):
    return num_to_abbrev(month) + " " + zero_trim(day) + ", " + year

def EUdate2pqdef(datestring):
    year, day, month = _split_datestring(datestring)
    return ''.join([year, month, day])
    
def USdate2pqdef(datestring): return datestring

#def pqan2pqdef(datestring):
    

def pqdef2pqan(datestring):
    return USdate2pqan(datestring)
'''
By using negative indexing in the list, we can handle both 6 and 8 digit 
numbers in one simple lambda - no matter what the input value, we always 
want to split it at four from the end and at two from the end. Neat.
'''
_split_datestring = lambda s : [s[:-4], s[-4:-2], s[-2:]]
    

if __name__ == "__main__":
    import doctest
    doctest.testmod()