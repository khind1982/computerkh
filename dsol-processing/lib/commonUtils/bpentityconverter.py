#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os, re
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

from singleton import Singleton

class bpEntityConverter(Singleton):

    def __init__(self):
        self.refToUtf8Dict = {
                        '<alpha>': unichr(945),
                        '<beta>': unichr(946),
                        '<gamma>': unichr(947),
                        '<delta>': unichr(948),
                        '<epsilon>': unichr(949),
                        '<zeta>': unichr(950),
                        '<eta>': unichr(951),
                        '<theta>': unichr(952),
                        '<iota>': unichr(953),
                        '<kappa>': unichr(954),
                        '<lambda>': unichr(955),
                        '<mu>': unichr(956),
                        '<nu>': unichr(957),
                        '<xi>': unichr(958),
                        '<omicron>': unichr(959),
                        '<pi>': unichr(960),
                        '<rho>': unichr(961),
                        '<sigma>': unichr(963),
                        '<tau>': unichr(964),
                        '<upsilon>': unichr(965),
                        '<phi>': unichr(966),
                        '<chi>': unichr(967),
                        '<psi>': unichr(968),
                        '<omega>': unichr(969),
                        '<ALPHA>': unichr(913),
                        '<BETA>': unichr(914),
                        '<GAMMA>': unichr(915),
                        '<DELTA>': unichr(916),
                        '<EPSILON>': unichr(917),
                        '<ZETA>': unichr(918),
                        '<ETA>': unichr(919),
                        '<THETA>': unichr(920),
                        '<IOTA>': unichr(921),
                        '<KAPPA>': unichr(922),
                        '<LAMBDA>': unichr(923),
                        '<MU>': unichr(924),
                        '<NU>': unichr(925),
                        '<XI>': unichr(926),
                        '<OMICRON>': unichr(927),
                        '<PI>': unichr(928),
                        '<RHO>': unichr(929),
                        '<SIGMA>': unichr(931),
                        '<TAU>': unichr(932),
                        '<UPSILON>': unichr(933),
                        '<PHI>': unichr(934),
                        '<CHI>': unichr(935),
                        '<PSI>': unichr(936),
                        '<OMEGA>': unichr(937),
                        '<symbol>': u'&lt;symbol&gt;',
                        '< symbol>': u'&lt;symbol&gt;',
                        '& ': u'&amp; ',
                        '&#167;': unichr(167),
			'&quot&quot;': u'&quot;&quot;',
			'&pound;': unichr(163),
			'&deg;': unichr(176),
			'&sect;': unichr(167),
			'&c.': '&amp;c.'
                        }
                        
    def convert(self, instring):
        entsre = re.compile("|".join(map(re.escape, self.refToUtf8Dict.keys( ))))
        newstring = entsre.sub(lambda srch: self.refToUtf8Dict[srch.group(0)], instring)
        return newstring
            
  
def entityToItalicsTag(instring):
    outstring = instring.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
    return outstring