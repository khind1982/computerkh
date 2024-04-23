#!/usr/bin/env python
# -*- mode: python -*-
#pylint:disable=W0621,W0212,F0401

import sys
import os
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'lib')))

import glob
import re
import shutil

from optparse import OptionParser # This is deprecated in 2.7, but the
                                  # replacement, argparse, isn't
                                  # available in 2.6

from commonUtils.fileUtils import locate

from mappings.rules import APSRules
from mappings.rules import EIMARules
from msthreading import DocumentThreading
from pagecollection import PagefileReader
from pagecollection import PcmiGenerator, PagemapGenerator
from streams.etreestream import EtreeStream

# a new approach to generating the media services metadata files and
# the MySQL threading database.

optparser = OptionParser()
optparser.set_usage('{prog} [-d <destination>] [-p <pagefileroot>] <product> <handover_dir>'.format(
    prog = os.path.basename(__file__)))
optparser.add_option('-d', dest='destroot', default=None)
optparser.add_option('-p', dest='pagefileroot', default=None)

(options, args) = optparser.parse_args()

def build_issue_list(directory):
    print "building list of issues to convert from %s..." % directory
    if product == 'eima':
        eima_jids = EIMARules.known_jids()
    issues_to_build = {}
    for f in locate('*.xml', root=directory):
        pathelems = f.split('/')
        if product == 'bpc':
            filename = pathelems[-1]
            jid = filename.split('_')[0]
            issue = '_'.join(filename.split('_')[1:2])
        else:
            for part in pathelems:
                if (product == 'eima' and APSRules.jid(part) in eima_jids) or part.startswith(product.upper()):
                    jid = APSRules.jid(part)
                    issue = APSRules.mserv_issueid(pathelems[pathelems.index(part) + 1])
                    break
                else:
                    continue
        try:
            issues_to_build[jid].add(issue)
        except KeyError:
            # use a set here so duplicates are discarded silently.
            issues_to_build[jid] = set([issue])
    return issues_to_build

def do_gen_pagemap(pagefile):
    #print "PAGEFILE: %s" % pagefile._cfg['filename']
    #print "DESTROOT: %s" % destroot
    pcidpath = os.path.dirname(pagefile._cfg['filename'])
    pagefile_xml = pagefile.data
    pagemap = PagemapGenerator(pagefile_xml, destroot)
    pagemap.build_and_finalise()

    pcid = pagemap.pcid
    pcids[pcid] = pcidpath

# Build the list of directories to scan for pagefiles.
# If issues is ALL, we want to (re)build the whole lot.
# Otherwise, we just want the issues mentioned for each
# jid.
def directories_to_scan():
    while True:
        try:
            return dirs_to_scan
        except NameError:
            if issues == 'ALL':
                dirs_to_scan = glob.glob('%s/*/*' % dataroot)
            else:
                dirs_to_scan = []
                for jid in sorted(issues.keys()):
                    for issue in sorted(issues[jid]):
                        for globdir in glob.glob('%s/%s/%s*' % (dataroot, jid, '%s_%s' % (jid, issue))):
                            dirs_to_scan.append(globdir)

# We always need the product as the first argument.
# Not giving it is an error
try:
    product = args[0]
except IndexError:
    print >> sys.stderr, optparser.usage
    exit(1)


# Set a default path to save output. If the user passes in a
# different directory, we can use this default to copy the files
# from the user-supplied location to the default, where the master
# set of pagemap, pcmi and hit highlighting files live.
default_destroot = '/dc/dsol/steadystate/mediaservices/out/%s' % product

# If no destroot is specified, write to the default location
if options.destroot is None:
    destroot = default_destroot
else:
    destroot = re.sub('/$', '', options.destroot)

# If no pagefileroot is specified, take pagefiles from the
# standard location
if options.pagefileroot is None:
    dataroot = '/dc/scratch/np/ms/pagefiles/%s' % product
else:
    try:
        dataroot = args[1]
    except IndexError:
        print >> sys.stderr, optparser.usage
        exit(1)

threading_dataroot = args[1]

# If the path to the handover directory is not given,
# we know we need to process all pagefiles for the
# product. If a handover is given, only process pagefiles
# relevant to that handover.
try:
    issues = build_issue_list(args[1])
except IndexError:
    #issues = build_issue_list('%s/%s' % (dataroot, product))
    issues = 'ALL'

# A list to record the PCIDs we see while generating the pagemap files.
# We later use this list to create a PCMI file per PCID.
pcids = {}

print >> sys.stderr, "Generating pagemap files"
for directory in directories_to_scan():
    for pagefile in PagefileReader(directory):
        do_gen_pagemap(pagefile)

print >> sys.stderr, "Generating PCMI files"
for pcid in sorted(pcids.keys()):
    pcmi = PcmiGenerator(destroot)
    for pagefile in PagefileReader(pcids[pcid]):
        pagefile_xml = pagefile.data
        pcmi.append_page(pagefile_xml)
    pcmi.build_file()

###
if issues != 'ALL':
    print >> sys.stderr, "Generating threading data"
    streamOpts = "dataRoot=%s" % threading_dataroot
    for doc in EtreeStream({'stream': '*.xml', 'streamOpts': streamOpts}).streamdata():
        thr = DocumentThreading(doc, product, destroot)
        thr.do_threading()
    thr.flush_pagecollection_threading()
else:
    print >> sys.stderr, "Cannot generate threading data without source XML!"


if destroot != default_destroot:
    print >> sys.stderr, "Copying files from %s to the master directory (%s)" % (destroot, default_destroot)

    for f in locate('*.xml', root=destroot):
        target = f.replace(destroot, default_destroot)
        while True:
            try:
                shutil.copyfile(f, target)
            except IOError:
                os.makedirs(os.path.dirname(target))
                continue
            break
        try:
            os.chmod(target, 0664)
        except OSError:
            pass

    # Build a list of paths to the issues whose pos and idx files we
    # want to grab the issues dict from earlier can be used here - its
    # keys are the JIDs in the current handover, and its values are
    # the 8 digit date representing the date of publication
    print >> sys.stderr, "Finding hit highlighting files..."

    # We use sets here to avoid copying files more than once if two or
    # more issues were published in the same month.
    hhtabs = set([])
    try:
        for jid in issues.keys():
            for issue in issues[jid]:
                hhtabs.add(os.path.join(default_destroot, jid, '%s/%s' % (issue[0:4], issue[4:6])))
                #hhtabs.add(os.path.join(default_destroot, product, jid, '%s/%s' % (issue[0:4], issue[4:6])))
    except AttributeError:
        hhtabs.add(os.path.join(default_destroot, product))

    # And now copy those pos and idx files out of the master archive
    # into the bundle for the current handover.
    for directory in sorted(hhtabs):
        new_dir = directory.replace(default_destroot, destroot)
        print >> sys.stderr, "Copying hit highlighting files from master archive to %s" % new_dir
        for hhfile_type in ['pos', 'idx']:
            for hhfile in locate('*.%s' % hhfile_type, root=directory):
                jid, issue = hhfile.split('/')[-1].split('_')[0:2]
                if issue in issues[jid]:
                    new_hhfile = hhfile.replace(default_destroot, destroot)
                    while True:
                        try:
                            shutil.copy(hhfile, new_hhfile)
                        except IOError:
                            os.makedirs(os.path.dirname(new_hhfile))
                            continue
                        break
                    os.chmod(new_hhfile, 0664)
