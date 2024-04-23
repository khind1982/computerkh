# -*- mode: python -*-
# pylint: disable = R0903

import re
import commonUtils.textUtils


# A quite breathtaking implementation of the singleton DP.
# From http://wiki.python.org/moin/PythonDecoratorLibrary#The_Sublime_Singleton
def singleton(cls):
    instance = cls
    instance.__call__ = lambda: instance
    return instance


# A simple decorator class that catches IndexError raised
# in its subject method, and returns instead the string passed
# in as its sole argument.
#
# Useful for ensuring that a record without a title element gets
# '[untitled]'.

class catchEmptyList(object):
    def __init__(self, replacement):
        self.replacement = replacement

    def __call__(self, f):
        def wrapped(*args):
            try:
                val = f(*args)
            except IndexError:
                val = self.replacement
            if val == None or val.strip() == '':
                val = self.replacement
            return val
        return wrapped


class memoize(object):
    def __init__(self, memo, attr, f):
        self.memo = memo
        self.attr = attr
        self.f = f

    def __call__(self, f):
        def wrapped(*args):
            try:
                return self.memo[self.attr]
            except KeyError:
                self.memo[self.attr] = self.f(*args)
                return self.memo
        return wrapped


# A decorator to handle populating the title in APS
# derived documents. If no title is present in the
# source, then we take the value of APS_article[@type]
# an fix the case.
class normaliseEmptyTitle(object):
    def __init__(self, doctype):
        words = doctype.split('_')
        words[0] = words[0].capitalize()
        words[-1] = words[-1].capitalize()
        self.doctype = (' ').join(words)

    def __call__(self, f):
        def wrapped(*args):
            val = f(*args)
            if val == '':
                val = self.doctype
            return val
        return wrapped

# Pass all strings through the
# commonUtils.textUtils.strip_control_chars function
class stripControlChars(object):
    def __init__(self, f):
        print f
        self.f = f

    def __call__(self, string):
        if callable(string):
            return string
        print "string: %s" % string
        def wrapped(**kwargs):
            print "args: %s" % kwargs
        return wrapped

# A decorator function for performing a search and replace operation on the
# string returned by the wrapped function. Useful for tidying up the output
# of naive or broken functions, such as the xml.sax.saxutils.escape function,
# which will try to escape the already escaped strings "&amp;", "&lt;" and
# "&gt;" (which become "&amp;amp;", "&amp;lt;" and "&amp;gt;")

# `func' can be a lambda if you want to manipulate the return value of a method
# on a str instance, such as str.upper():
# snr(lambda x: x.upper(), search, replace)

def snr(func, search, replace):
    def wrapper(text):
        return re.sub(search, replace, func(text))
    return wrapper
