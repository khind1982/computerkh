# -*- mode: python -*-

# LGBT Magazine Archive copyright handler.

from commonUtils.fileUtils import buildLut

def _get_cs():
    # We only want to build the lookup once...
    while True:
        try:
            return _cs
        except NameError:
            _cs = buildLut('epc_copyrights/lgb.lut')

cs = _get_cs()
