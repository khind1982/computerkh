'''This module implements the BNumberTracker class. It is reponsible
for recording which b-number/i-number combinations we have already
processed, so that we can skip regenerating books we've already done.

'''
import os

from collections import defaultdict

from commonUtils.fileUtils import buildLut

class BNumberTracker(object):
    def __init__(self):
        self.logfile = '/dc/dsol/var/wellcome/collection3_b_numbers.log'
        self.data = defaultdict(list)
        for k, v in buildLut(self.logfile).items():
            self.data[k] = v.split()

    def __contains__(self, item):
        return item in self.data.keys()

    def update_b_number(self, b_number, i_number):
        if not i_number in self.data[b_number]:
            self.data[b_number].append(i_number)
        self.write_log_file()

    def write_log_file(self):
        fd = os.open(
            self.logfile, os.O_CREAT|os.O_WRONLY|os.O_TRUNC|os.O_EXLOCK
        )
        for k in sorted(self.data.keys()):
            os.write(fd, "%s|%s\n" % (k, ' '.join(self.data[k])))
        os.close(fd)

    def get_seq_id(self, b_number):
        return str(len(self.data[b_number]) + 1)

    def seen_combination(self, b_number, i_number):
        return i_number in self.data[b_number]
    