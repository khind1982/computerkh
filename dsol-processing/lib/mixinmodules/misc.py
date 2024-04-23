#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

# Miscellaneous mixin methods. So far, just stuff like providing visual feedback

class MiscMixin(object):
    def visualFeedBackBasic(self):
        if self._cfg['provideFeedBack'] == True:
            if self._cfg['seen'] % 100 == 0:
                sys.stderr.write(str(self._cfg['seen']))
            elif self._cfg['seen'] % 10 == 0:
                sys.stderr.write('.')

    def visualFeedBack(self):
        if self._cfg['provideFeedBack'] == True:
            sys.stderr.write('\r\033[0K')
            sys.stderr.write('Seen: \033[92m%s\033[0m\ttransformed: \033[91m%s\033[0m\t(\033[96m%s\033[0m)' % (self._cfg['index'], self._transformedCount, self._cfg['basename']))
