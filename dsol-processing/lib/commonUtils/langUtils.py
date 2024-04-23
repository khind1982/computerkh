#!/usr/local/bin/python2.6
# -*- mode: python -*-

import os
import sys
pathdir = os.path.join(os.path.dirname(__file__), '../../../../lib/python')
sys.path.append(pathdir)

from titlecase import titlecase
from commonUtils.fileUtils import buildLut
from commonUtils.listUtils import str_to_list

# Some functions to handle language data.

_iso2lang_map = buildLut('isolanguagecodes', delimiter=':')
_lang2iso_map = {}

for iso, language in _iso2lang_map.items():
    for ln in language.split(';'):
        ln = ln.lstrip()
        _lang2iso_map[ln] = iso

def lang_to_iso(language_name):
    ret = 'UND'
    lang = titlecase(language_name)
    if lang in _lang2iso_map.keys():
        ret = _lang2iso_map[lang]
    return ret


# Returns a list of languages. Well, just splits a string on delimiter
# and returns the resulting array.
def languages(language_list, delimiter='\t'):
    return str_to_list(language_list, delimiter)


# Takes a list of languages, such as output by languages(), and looks up each
# one's ISO code. Returns an array of two-key hashes - langName and langISOCode.
def lang_iso_codes(language_list):
    return [{'langName': lang, 'langISOCode': unicode(lang_to_iso(lang))} for lang in language_list]
