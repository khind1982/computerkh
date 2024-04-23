# -*- mode: python -*-
# -*- coding: utf-8 -*-

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'libdata/eeb'))


class RegexDict(dict):
    
    def get_matching(self, event):
        return (self[key] for key in self if re.match(key, event))


def std_date(date):
    
    rnumconvert = {' I ': ' january ',
                   ' II ': ' february ',
                   ' III ': ' march ',
                   ' IV ': ' april ',
                   ' V ': ' may ',
                   ' VI ': ' june ',
                   ' VII ': ' july ',
                   ' VIII ': ' august ',
                   ' IX ': ' september ',
                   ' X ': ' october ',
                   ' XI ': ' november ',
                   ' XII ': ' december '}
    
    months = {'january|janvier|januari|januarius|januarii|gennaio|januar' : ['01', '31'],
              'february|fevrier|februari|februarius|februarii|febbraio|februar|februarĳ' : ['02', '28'],
              'march|mars|maart|martius|martii|marzo|marts' : ['03', '31'],
              'april|avril|aprilis|aprile' : ['04', '30'],
              'may|mai|mei|maius|maii|maggio|maj' : ['05', '31'],
              'june|juin|juni|junius|junii|giugno' : ['06', '30'],
              'july|juillet|juli|julius|julii|luglio' : ['07', '31'],
              'august|aout|augustus|augusti|agosto' : ['08', '31'],
              'september|septembre|septembris|settembre' : ['09', '30'],
              'october|octobre|oktober|octobris|ottobre' : ['10', '31'],
              'november|novembre|novembris' : ['11', '30'],
              'december|decembre|decembris|dicembre|décembre' : ['12', '31']}

    rmonths = RegexDict(months)

    for key in rnumconvert.keys():
        if key in date:
            date = date.replace(key, rnumconvert[key])

    rmonthkeys = []
    for i in rmonths.keys():
        j = i.split('|')
        for item in j:
            rmonthkeys.append(item.decode('utf-8'))

    year = re.findall('1[0-9]{3}|1[0-9]{2}X|1[0-9]{1}XX', date)
    mcomp = re.compile('[^\W\d_]+', re.UNICODE)
    month = re.findall(mcomp, date)
    month = [i for i in month if i in rmonthkeys]
    
    if len(year) == 2:
        starty = min(year)
        endy = max(year)
    elif len(year) == 1:
        starty = year[0].replace('X', '0')
        endy = year[0].replace('X', '9')
    else:
        return ''    

    if len(month) != 0 and month[0] in rmonthkeys:
        for o in rmonths.get_matching(month[0].encode('utf-8')):
            start = '%s%s01' % (starty, o[0])
            end = '%s%s%s' % (endy, o[0], o[1])
    else:
        start = '%s0101' % (starty)
        end = '%s1231' % (endy)
    
    machine = '%s-%s' % (start, end)
    return machine