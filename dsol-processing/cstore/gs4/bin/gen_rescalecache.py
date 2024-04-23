#!/usr/bin/env python2.7
# -*- mode:python -*-

# Manage BSDdb cache files of image resize factors for
# APS-derived content sets.

# Store cache files rooted at /dc/dsol/np/ms/image_rescale_cache/<product>
# Within the root, separate files by pmid, and then one file per year,
# yielding something like this:

# /dc/dsol/np/ms/image_rescale_cache/wwd/WWD001/1919.700
# /dc/dsol/np/ms/image_rescale_cache/wwd/WWD001/1919.2880

import os.path
import sys
lib_path = os.path.abspath(
        os.path.join(
            os.path.abspath(
                os.path.dirname(__file__)), '..', 'lib'))
sys.path.append(lib_path)

from bsddb.db import DBNoSuchFileError  # noqa
from decimal import Decimal, getcontext  # noqa
from optparse import OptionParser  # noqa

from mappings.rules import APSRules  # noqa
from dbcache import DBCacheManager  # noqa

getcontext().prec = 6


class Rescale(object):
    def __init__(self, product, size, line):
        self.image_path, before, after = line.split()
        self.image_id = os.path.splitext(os.path.basename(self.image_path))[0]
        self.product = product
        self.rescale_factor = str(Decimal(before) / Decimal(after))
        while True:
            try:
                self.rescale_cache = DBCacheManager(
                        "%s/%s" % (self.jid, self.year),
                        size, getattr(self, 'cachefile_path_%s' % size))
                break
            except DBNoSuchFileError:
                os.makedirs(os.path.dirname(
                    getattr(self, 'cachefile_path_%s' % size)))

    @property
    def jid(self):
        return APSRules.jid(self.image_path.split('/')[0])

    @property
    def issue(self):
        return self.image_path.split('/')[1].replace('APS_', '')

    @property
    def year(self):
        #if self.product in ['wwd', 'bpc']:
        if len(self.issue.split('_')) == 3:
            y = self.issue.split('_')[-2][0:4]
        else:
            y = self.issue.split('_')[-1][0:4]
        return y

    @property
    def outdir(self):
        return os.path.join('/dc/dsol/np/ms/image_rescale_cache', self.product)

    @property
    def cachefile_path_700(self):
        return self._cachefile_path('700')

    @property
    def cachefile_path_2880(self):
        return self._cachefile_path('2880')

    def _cachefile_path(self, which):
        return "%s/%s/%s.%s" % (self.outdir, self.jid, self.year, which)

    def add_or_update(self):
        self.rescale_cache[self.image_id] = self.rescale_factor


class RescaleCacheWrapper(object):
    #pylint:disable=W0631,W0621
    def __init__(self, product, size, infile):
        self.product = product
        self.size = size
        self.infile = infile

    def iterlines(self):
        with open(self.infile) as infile:
            for count, line in enumerate(infile.readlines(), start=1):
                try:
                    Rescale(self.product, self.size, line).add_or_update()
                except ValueError as e:
                    print >> sys.stderr, "Invalid entry at line %s: %s" % (count, line.strip())
                    if e.message == "need more than 1 value to unpack":
                        print >> sys.stderr, "\t(no rescale number generated during stamping/scaling?)\n"
                    continue

            try:
                print "Added %s entries" % count
            except UnboundLocalError:
                # If we get here, the input file was probably empty - we fell
                # straight off the for-loop, suggesting no lines in the input.
                print >> sys.stderr, "No entries added - is the input file empty?"
                exit(1)


optparser = OptionParser()
optparser.add_option('-s', dest='size', default=None)
optparser.add_option('-p', dest='product', default=None)
(opts, args) = optparser.parse_args()

# We can't carry on with no product name
# Possible enhancement - autodetect product. Should be easy:
# If the issue part of the image_path contains APS, we're
# doing EIMA. Depends on what we decide to use as the pmid
# for AAA.

if opts.product is None:
    print >> sys.stderr, "Please specify a product with -p"
    exit(1)

try:
    infile = args[0]
except IndexError:
    print >> sys.stderr, "Please provide the path to a rescale file"
    exit(1)

if opts.size is None:
    opts.size =  os.path.splitext(infile)[1].replace('.', '')
    if not opts.size in ['700', '2880']:
        print >> sys.stderr, "Cannot determine rescale size. Please provide it with -s"
        exit(1)

# Now get on and do it!
RescaleCacheWrapper(opts.product, opts.size, infile).iterlines()
