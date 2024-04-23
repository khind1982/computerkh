# -*- mode: python -*-

# Monkey patch elixir.Entity so it always has the get_by_or_create() method
#import sys
#print sys.path

try:
    import elixir #pylint:disable=W0611
except ImportError:
    import site
    import sys
    site.addsitedir('/packages/dsol/lib/python%s.%s/site-packages' % (sys.version_info[0], sys.version_info[1]))
#    print sys.path
    import elixir
from elixir import * #pylint:disable=W0622,W0401,W0614

def get_by_or_create(cls, if_new_set={}, **params): #pylint:disable=W0102
    ''' Call get_by(). If no object is found, create one with
    the same params. If a new object is created, set any 
    initial values.'''
    
    result = cls.get_by(**params)
    if not result:
        result = cls(**params)
        result.set(**if_new_set)  #pylint:disable=W0142
    return result

Entity.get_by_or_create = classmethod(get_by_or_create)
