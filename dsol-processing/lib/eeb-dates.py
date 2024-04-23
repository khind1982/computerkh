# -*- mode: python -*-

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'libdata/eeb'))


def std_date(date):
    year = re.findall('[0-9]{4}')
    print year