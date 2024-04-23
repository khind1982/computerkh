# -*- mode: python -*-

'''
A few convenience functions for some common hashlib operations.
'''

import hashlib


def hash_file(path, scheme=None):
    ''' Calculate and return the hexdigest representation of 'scheme'
    applied to 'path'. 'scheme' defaults to 'sha256'.'''
    if scheme is None:
        scheme = 'sha256'
    return getattr(hashlib, scheme)(file(path).read()).hexdigest()
