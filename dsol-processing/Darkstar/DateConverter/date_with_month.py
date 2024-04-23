'''
A set of functions to handle dates in the following formats:
    
    mmm. dd, yyyy
    M dd, yyyy
    dd mmm yyyy
    ymmdd
    mm/dd/yyyy and dd/mm/yyyy

In each case, return the normalised PQDEF date format.
'''
from month import *
from base import *

def conv_mdy(datestring):
    month, day, year = datestring.split(' ')
    return result(year, month, day)
    
def conv_dmy(datestring):
    day, month, year = datestring.split(' ')
    return result(year, month, day)
    
def conv_my(datestring):
    month, year = datestring.split(' ')
    return result(year, month)
    
def conv_slash_mdy(datestring):
    month, day, year = datestring.split('/')
    return slash_result(year, month, day)
    
def conv_slash_dmy(datestring):
    day, month, year = datestring.split('/')
    return slash_result(year, month, day)
    
def conv_mdy_pqan(datestring):
    month, day, year = datestring.split(' ')
    return pqan_result(month, day, year)
    
def conv_dmy_pqan(datestring):
    day, month, year = datestring.split(' ')
    return pqan_result(month, day, year)
    
def conv_slash_mdy_pqan(datestring):
    month, day, year = datestring.split('/')
    return pqan_slash_result(month, day, year)
    
def conv_slash_dmy_pqan(datestring):
    day, month, year = datestring.split('/')
    return pqan_slash_result(month, day, year)
    
def conv_my_pqan(datestring):
    month, year = datestring.split(' ')
    return month[0:3].capitalize() + ' ' + year
    
result = lambda y, m, d='01' : ''.join([y, name_to_num(ds_trim(m)), zero_pad(ds_trim(d))])
slash_result = lambda y, m, d='01' : ''.join([y, zero_pad(m), zero_pad(d)])

pqan_result = lambda m, d, y : m[0:3].capitalize() + ' ' + zero_trim(d) + ', ' + y
pqan_slash_result = lambda m, d, y : num_to_abbrev(m) + ' ' + zero_trim(d) + ', ' + y