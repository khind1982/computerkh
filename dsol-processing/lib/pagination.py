#!/usr/local/bin/python2.7
# -*- mode: python -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

class Pagination(object):
    def __init__(self, pagelist):
        self.pagelist = pagelist
        self.numericallist = [self._cast_to_int_or_none(page) for page in self.pagelist]

        # These are used in formatted_string to determine the correct display
        # Assign them here so that we can split the code in formatted_string
        # into nice DRY pieces.
        self.listposition = 0
        self.pgdescentries = []
        self.inrange = False
        self.rangestart = None

    def __str__(self):
        return "Pagination: %s" % self.formatted_string

    # If the value of pgno can be successfully cast to an integer, return that integer.
    # Otherwise, return None
    @staticmethod
    def _cast_to_int_or_none(pgno):
        try:
            return int(pgno)
        except ValueError:
            return None

    @property
    def formatted_string(self):
        for listposition, pgno in enumerate(self.numericallist):
            self.listposition = listposition
            if pgno != None:            
                try:
                    if self.numericallist[listposition + 1] != None and self.numericallist[listposition + 1] - pgno == 1:
                        if self.inrange is False:
                            self.inrange = True
                            self.rangestart = str(pgno)
                    else:
                        self.nonconsecutive()
                except IndexError:
                    self.nonconsecutive()
            else:
                self.pgdescentries.append(self.pagelist[listposition])
        return (', ').join(self.pgdescentries)

    def nonconsecutive(self):
        if self.inrange is False:
            self.pgdescentries.append(self.pagelist[self.listposition])
        else:
            self.inrange = False
            self.pgdescentries.append('-'.join([self.rangestart, self.pagelist[self.listposition]]))
            self.rangestart = None


if __name__ == '__main__':
    test1 = ['1', '2', '3', '6', '8']
    print Pagination(test1).formatted_string
    print Pagination(test1)
    
    test2 = ['a', '1', '2a', '3', '4', '5', '6', '7b', '8']
    print Pagination(test2).formatted_string

    test3 = ['1-1-1', '2', '3', '4', '5a', '6', '7', '8']
    print Pagination(test3).formatted_string
    
