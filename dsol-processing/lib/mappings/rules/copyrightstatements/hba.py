# -*- mode: python -*-
#

import datetime

year = datetime.datetime.now().year

def _get_cs():
    return "&#xa9; Copyright %s ProQuest LLC." % str(year)

cs = _get_cs()