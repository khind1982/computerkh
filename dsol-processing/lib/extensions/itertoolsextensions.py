# -*- mode: python -*-

'''This module contains functions that complement those found in the
itertools module in the standard library:

grouped(iterable, number): return <number> items from <iterable> at a
time. Drop extra items if <iterable> is not divisible by <number>

grouped_all(iterable, number, fillvalue=None): return <number> items
at a time from <iterable>. If <iterable> is not divisible by <number>,
extra values are filled with <fillvalue>.

'''

from itertools import izip
from itertools import izip_longest


# TODO find a way to remove the duplication in these two functions.

def grouped(iterable, number):
    '''yield <number> items at a time from <iterable>.
    If <iterable> is not divisible by <number>, extra
    items are simply and silently dropped.
    '''
    for g in izip(
            *[iterable[i::number] for i in range(number)]
    ):
        yield g

def grouped_all(iterable, number, fillvalue=None):
    '''As above, but return partial tuples if <iterable> isn't
    divisible by <number>, filling in blanks with <fillvalue>.
    '''
    for g in izip_longest(
            *[iterable[i::number] for i in range(number)], fillvalue=fillvalue
    ):
        yield g
