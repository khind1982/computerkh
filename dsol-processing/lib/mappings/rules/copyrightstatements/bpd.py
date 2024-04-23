# -*- mode: python -*-
#import datetime

from commonUtils.fileUtils import buildLut

def _get_cs():
    #year = datetime.datetime.now().year
    while True:
        try:
            return _cs
        except NameError:
            _cs = buildLut('epc_copyrights/bpd.lut')

cs = _get_cs()
