#!/usr/local/bin/python2.6
# -*- mode: python -*-

import codecs
import re

import namedentities
import xml.sax.saxutils

from commonUtils.fileUtils import buildLut
from commonUtils.listUtils import fastflatten

name2num = buildLut('entityrefs')

class EntRefError(Exception): pass

# Miscellaneous text handling functions.

# These two functions were imported from the now largely ignored (by me)
# EntityShield module in /packages/dsol/lib/python

def protect(string, change='&', target='&amp;'):
    '''Take a string and replace all instances of '&' with '&amp;'

    This function can also be used to perform other, arbitrary translations
    if given a change or target argument'''
    return __do_replace(string, change, target)

def unprotect(string, change='&amp;', target='&', pad=True):
    while re.search(change, string):
        string = __do_replace(string, change, target)
    if pad is True:
        return __do_replace(string, '& ', '&amp; ')
    else:
        return string

def __do_replace(string, change_this, to_this):
    return string.replace(change_this, to_this)


# If the operand is of type str or of type unicode, return True.
# Otherwise, return False.

def isStringy(data):
    return isinstance(data, basestring)

# Any string can be passed through this to replace entity references
# with their UTF-8 equivalent. It handles both named refs ('&eacute;')
# and numeric refs ('&#233;'), provided there is a mapping in the list
# of known entities. In the case of no mapping, we return the string
# unaltered, on the assumption that if it's not a named entity
# reference, it's probably a valid string. Once a named ent reference
# is successfully mapped to a numeric character entity reference, pass
# that value off to getunichr(), which will return the UTF-8
# character, or raise and exceoption.

def replace_entityrefs(string):
    numentrefre = re.compile('&#(x?[0-9a-fA-F]+);')
    entrefnamere = re.compile('(&[A-Za-z0-9]+;)')
    rstring = unprotect(string)
    matches = entrefnamere.search(rstring)
    if matches:
        if matches.group(0) in name2num.keys():
            rstring = entrefnamere.sub(lambda match: name2num.get(match.group(0)), rstring)
        else:
            # If we don't recognise the string as an entity reference, return it
            # unmolested - it's quite likely a perfectly innocent piece of textual
            # data, and doesn't deserve to be treated as an entity reference, any way.
            return rstring
    return numentrefre.sub(lambda match: getunichr(match.group(1)), rstring)

# Covnert the passed in value to a UTF-8 character, or, if that's not
# possible, raise EntRefError.
def getunichr(entref):
    if re.match('x', entref):
        base = 16
        string = re.search(r'x(.*)', entref).group(1)
    else:
        base = 10
        string = entref
    try:
        return unichr(int(string, base))
    except ValueError:
        raise EntRefError("&#%s; is not a valid entity reference" % entref)

def cleanAndEncode(string, strip=True, escape=True, entities=None, replaceEntities=True):
    if type(string) is unicode:
        string = string
    else:
        try:
            string = codecs.encode(string, 'utf8')
        except UnicodeDecodeError:
            string = unicode(codecs.decode(string, 'latin1'))
    if strip == True:
        string = string.strip()
    if replaceEntities == True:
        string = replace_entityrefs(protect(unprotect(string, pad=False)))
    string = re.sub(r'<<', unichr(171), string)
    string = re.sub(r'>>', unichr(187), string)
    string = re.sub(r'<>', ' ', string)

    if escape == True:
        #string = fix_named_ents(string)
        string = xmlEscape(string, entities)
    # try to fix mangled entity references without hitting any other, valid,
    # instances of "&amp;#" in the data.
        if re.search(r"&amp;#x?[0-9a-fA-F]+;", string):
            string = string.replace("&amp;#", "&#")
    #if type(escape) is dict:
    #    string = xmlEscape(string, entities = escape)

    # This occurs in PIO/PAO and needs to be fixed more elegantly.
    string = re.sub('&c.', '&amp;c.', string)

    return string

# These two are lifted from xml.sax.saxutils.
def __dict_replace(s, d):
    """Replace substrings of a string using a dictionary."""
    for key, value in d.items():
        s = s.replace(key, value)
    return s

def xmlEscape(data, entities=None):
    # Escape &, <, and > in a string of data.

    # You can escape other strings of data by passing a dictionary as
    # the optional entities parameter.  The keys and values must all be
    # strings; each key will be replaced with its corresponding value.

    if entities is not None:
        data = __dict_replace(data, entities)
    else:
        # must do ampersand first
        data = data.replace("&", "&amp;")
        data = data.replace(">", "&gt;")
        data = data.replace("<", "&lt;")
# Do we really need this? It's not required in character data, and
# all attributes are constructed in code anyway...
#        if quotes is True:
#            data = data.replace('"', "&quot;")
#            data = data.replace("'", "&apos;")
    return data

def translateDate(datestring):
    ''' Edge cases go here. These are things that will take too much time to
    try and fix elegantly, so they'll have to be hacks. '''
    dateMatch = re.match('June/Juin (\d{2,4})', datestring)
    if dateMatch:
        return "June " + dateMatch.group(1)

    dateMatch = re.match('Awards (\d{4})', datestring)
    if dateMatch:
        return dateMatch.group(1)
    dateMatch = re.match('Special (\d{4})', datestring)
    if dateMatch:
        return dateMatch.group(1)
    dateMatch = re.match('^Proms (\d{4})$', datestring)
    if dateMatch:
        return u'Summer ' + dateMatch.group(1)

    # Take a date string in a foreign language, and attempt to translate it
    # into English.
    #
    # It turns out there's absolutely no point in trying to be clever
    # here. Some records claim to be in French, but have German dates,
    # some are apparently English and have foreign dates...

    datestring = codecs.encode(datestring, 'utf8')

    datestring = re.sub(r'^.{2}t.{2} ', 'Summer ',    datestring)

    datestring = re.sub(r'1er', '1', datestring)

    datestring = re.sub(r'janv\.',    'January',   datestring)
    datestring = re.sub(r'[jJ]anvier','January',   datestring)
    datestring = re.sub(r'f.*vr\.',   'February',  datestring)
    datestring = re.sub(r'[Ff][^ ]*vrier','February',  datestring)
    datestring = re.sub(r'[Mm]ars',      'March',     datestring)
    datestring = re.sub(r'[Aa]vril',     'April',     datestring)
    datestring = re.sub(r'[Mm]ai',    'May',       datestring)
    datestring = re.sub(r'MAI',    'May',   datestring)
    datestring = re.sub(r'[Jj]uin',      'June',      datestring)
    datestring = re.sub(r'JUIN',      'June',      datestring)
    datestring = re.sub(r'juil\.',    'July',      datestring)
    datestring = re.sub(r'[jJ]uillet','July',      datestring)
    datestring = re.sub(r'JUILLET','July',      datestring)
    datestring = re.sub(r'[Aa]o[^ ]+t', 'August',  datestring)
    datestring = re.sub(r'AO[^ ]+T', 'August', datestring)
    #datestring = re.sub(r'ao.{2}t',   'August',    datestring)
    #datestring = re.sub(r'ao&#251;t', 'August',    datestring)
    datestring = re.sub(r'sept\.',    'September', datestring)
    datestring = re.sub(r'(septembre|SEPTEMBRE)', 'September', datestring)
    datestring = re.sub(r'oct\.',     'October',   datestring)
    datestring = re.sub(r'(octobre|OCTOBRE)', 'October',  datestring)
    datestring = re.sub(r'nov\.',     'November',  datestring)
    datestring = re.sub(r'[Nn]ovembre',  'November', datestring)
    datestring = re.sub(r'd.*c\.',    'December',  datestring)
    datestring = re.sub(r'd&#233;c',  'December',  datestring)
    datestring = re.sub(r'[Dd][^ ]+cembre', 'December', datestring)

    datestring = re.sub(r'genn\.',  'January', datestring)
    datestring = re.sub(r'mar\.',   'March', datestring)
    datestring = re.sub(r'apr\.',   'April', datestring)
    datestring = re.sub(r'giugno',  'June', datestring)
    datestring = re.sub(r'luglio',  'July', datestring)
    datestring = re.sub(r'sett\.',  'September', datestring)
    datestring = re.sub(r'ott\.',   'October', datestring)

    datestring = re.sub(r'Jan\.', 'January', datestring)
    datestring = re.sub(r'M.*rz', 'March', datestring)
    datestring = re.sub(r'Juli', 'July', datestring)
    datestring = re.sub(r'Sept\.', 'September', datestring)
    datestring = re.sub(r'Okt\.', 'October', datestring)
    datestring = re.sub(r'Dez\.', 'December', datestring)

    return codecs.decode(datestring)

CONTROL_CHARS = fastflatten([range(0x00, 0x1f), range(0x7f, 0x9f), [0xa0]])

RUBBISH_CHARS = [
    0x25a0,
    0x2122,
    0x00ae,
    0x00a9,
    0x2014,
    0xab,
    0xa7,
    0xbb,
    0xb0,
    0x2022,
    0xb1,
    0x20ac,
]

def strip_control_chars(string):
    return __strip_chars_from_set(CONTROL_CHARS, string)

def remove_unwanted_chars(string, charlist=None):
    if charlist is not None:
        # pylint: disable = W0621
        delete_these = fastflatten([RUBBISH_CHARS, charlist])
    else:
        delete_these = RUBBISH_CHARS
    return __strip_chars_from_set(delete_these, string)


def __strip_chars_from_set(charset, string):
    for char in charset:
        try:
            string = string.replace(unichr(char), '')
        except UnicodeDecodeError:
            string = string.replace(chr(char), '')
    return string

# Return a function that takes a single argument, a string, and applies func()
# to the string, replacing matches on `search' with `replace' in the result.
# Useful as a function factory - see xmlescape, below.
def snr(func, search, replace):
    def wrapper(text):
        return re.sub(search, replace, func(text))
    return wrapper

xmlescape = snr(xml.sax.saxutils.escape, r'&((?:[aA][mM][pP];)+(\w+);)', r'&\2;')

#fixamps = snr(lambda x: x, r'&((?:[aA][mM][pP];)+((\w){2,});)', r'&\2;') # this needs modifying
fixamps = snr(lambda x: x, r'(&amp;)(amp;)+', r'\1')
#fixamps = snr(lambda x: x, r'(?<!&)amp;', r'')

def fix_named_ents(data):
    data = fixamps(data)   #xmlescape(data))
    # since str.replace() will replace all instances of the pattern in the
    # target string, we can avoid unnecessary calls to it by recording what's
    # already been done.
    seen = ['&amp;', '&AMP;']
    for match in [m.group(0) for m in re.finditer(r'(&([A-Za-z0-9]){2,};)', data)]:
        if not match in seen:
            data = data.replace(match, namedentities.unicode_entities(match))
            seen.append(match)
    return data
