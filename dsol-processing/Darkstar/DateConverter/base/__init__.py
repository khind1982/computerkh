#!/usr/local/bin/python2.5

'''
Base functions used throughout the suite.

This module's main purpose is to import other modules that are provided for
date manipulations. It defines only one lambda, which is so universal in its
application that it doesn't really belong anywhere else.

>>> month #doctest: +ELLIPSIS +SKIP
<module 'month' ...>
>>> type(simpleConversion)
<type 'module'>

Convert numerical months to either a full name or abbreviated name:
(These functions are imported from the base submodule)
>>> num_to_abbrev('01')
'Jan'
>>> num_to_name('01')
'January'
>>> name_to_num('Jan.')
'01'
>>> name_to_num('January')
'01'

>>> ds_trim('01.')
'01'
>>> ds_trim('01')
'01'
>>> ds_trim('Jan.,')
'Jan'
'''

import re

''' Remove any trailing full stops and commas. '''
ds_trim = lambda s : re.match(r'^([a-zA-Z0-9]+)[.,]*', s).group(1)
''' Trim leading zero from passed value '''
zero_trim = lambda number : re.match(r'^0?([1-9][0-9]?)', number).group(1)
''' The opposite... '''
zero_pad = lambda number : "%02i" % int(number)

if __name__ == "__main__":
    import doctest
    doctest.testmod()