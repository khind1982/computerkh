#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os, re
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))


# Various utilities of varying utility...

# A very simple set of functions to test if a string represents True or False
def checkBoolean(value):
    if re.search('1|on|t(rue)?|y(es)?', value, re.I):
        return True
    elif re.search('0|off|f(alse)?|no?', value, re.I):
        return False

def isTrue(value):
    return (True if checkBoolean(value) == True else False)

def isFalse(value):
    return (True if checkBoolean(value) == False else False)
