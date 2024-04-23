#!/usr/local/bin/python2.6
# -*- mode: python -*-

''' Some miscellaneous functions for lists and things. '''


def str_to_list(string, delimiter=None, maxsplit=-1):
    ''' Convert a string to a list, split on `delimiter', with all
    leading white space removed. '''
    return [word.lstrip() for word in string.split(delimiter, maxsplit)]
 
def flatten(lst):
    '''
    A nice neat little function to flatten a nested list or tuple.
    '''
    for elem in lst:
        if type(elem) in (tuple, list):
            for i in flatten(elem):
                yield i
        else:
            yield elem

def fastflatten(lst):
    '''
    A much faster way to flatten a list of lists, using list comprehensions.
    Only works to one level of nesting.
    Thanks to Alex Martelli on Stackoverflow.
    '''
    return [item for sublist in lst for item in sublist]

def uniq(seq, idfun=None):
    ''' Removes duplicate items from seq, and returns a new list
    consisting of just unique items. Retains seq order (taking account
    of removal of duplicate items) '''

    if idfun is None:
        idfun = lambda x: x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

def uniq_sort(seq, idfun=None):
    ''' Combines sorted and uniq '''
    return sorted(uniq(seq, idfun))
