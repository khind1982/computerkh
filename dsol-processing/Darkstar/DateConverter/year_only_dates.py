'''
A very small module that has only one purpose - when given a year, it returns
the year with month and day data defaulted to '0101'. It is only interested in
the first four digits of the passed value, in case we get two years. Global Schema
rules say we're only interested in the first year for constructing the date.
'''

def year_only(datestring):
    return datestring[0:4] + '0101'
    

