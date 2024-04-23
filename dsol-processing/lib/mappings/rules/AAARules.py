# -*- mode: python -*-
import mappings.rules.copyrightstatements.aaa as acs

__acs = acs.cs

def aaa_copyright_statements():
    return __acs

def known_jids():
    return __acs.keys()
