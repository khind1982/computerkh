#!/usr/local/bin/python2.6
# -*- mode: python -*-

import os
import optparse

parser = optparse.OptionParser()
parser.add_option('-d', '--directoryRoot', dest="directoryRoot", help='Root directory. Please supply full path.')
parser.add_option('-s', '--sort', dest="sort", action="store_true", help='Produces sorted tree (optional and slower)')

(options, args) = parser.parse_args()

if options.directoryRoot is None:
    parser.print_help()
    exit(1)

if not os.path.isdir(options.directoryRoot):
    print 'Directory not found!'
    exit(1)


def print_sorted(directory):
    all_directories = [root for root, dirs, files in os.walk(directory)]
    all_directories.sort()
    for d in all_directories:
        print d


def print_unsorted(directory):
    for root, dirs, files in os.walk(directory):
        print root


def sort_directories(directory, sort):
    if sort is True:
        print_sorted(directory)
    else:
        print_unsorted(directory)

if __name__ == '__main__':

    sort_directories(options.directoryRoot, options.sort)
