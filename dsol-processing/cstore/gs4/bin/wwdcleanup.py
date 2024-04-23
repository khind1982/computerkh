#!/usr/bin/env python2.7
# coding=utf-8

import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

from commonUtils.fileUtils import locate

for jpeg in locate('*.jpg', '/dc/wwd-images/master'):
    print os.path.basename(jpeg), time.ctime(os.path.getmtime(jpeg))
