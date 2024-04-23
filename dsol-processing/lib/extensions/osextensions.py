# -*- mode: python -*-

'''
Extension functions for the `os' library module.

makedirsp - like os.makedirs, but don't raise an OSError if any of the prefix
directories already exist, like the standard POSIX mkdir -p flag.
'''

import os

def makedirsp(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if hasattr(e, 'errno') and e.errno == 17:
            pass
        else:
            raise

setattr(os, 'makedirsp', makedirsp)
