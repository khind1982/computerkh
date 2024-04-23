# -*- mode: python -*-
from commonUtils.fileUtils import buildLut

def _get_cs():
    while True:
        try:
            return _cs
        except NameError:
            _cs = buildLut('epc_copyrights/npp.lut')

cs = _get_cs()
