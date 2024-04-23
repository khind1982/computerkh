# -*- mode: python -*-
from commonUtils.fileUtils import buildLut

def _get_cs():
    # We only want to build the lookup once...
    while True:
        try:
            return _cs
        except NameError:
            _cs = buildLut('epc_copyrights/eim.lut')

cs = _get_cs()
