#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'libdata/eeb'))

import lxml.etree as ET
from commonUtils.fileUtils import locate


try:
    indir = sys.argv[1]
    # outdir = sys.argv[2]
except IndexError:
    print "Usage: eeb-strip_cerl.py [input directory]\n"
    exit(1)

# if not os.path.exists(outdir):
#     os.makedirs(outdir)

# This part looks through the input directory to find the xml files

def strip_cerl(inputdir):
    recs = 0
    cerlfields = ['pop_cerl', 'cop_cerl', 'aut_cerl', 'pub_cerl', 'aut_other_cerl']
    for f in locate('*.xml', inputdir):
        
        shutil.copyfile(f, f.replace('.xml', '.stripbak'))
        # outfile = '%s/%s' % (os.path.abspath(outdir), os.path.basename(f))
        
        froot = ET.parse(f).getroot()
        rec_search = froot.find('.//rec_search')
                    
        for cerl in cerlfields:
            for c in froot.findall('.//%s' % cerl):
                c.getparent().remove(c)
        
        with open(f, 'w') as out:
            out.write(ET.tostring(froot, pretty_print=True))
        recs += 1

        sys.stdout.write('\033[92mCerl Stripped:\033[0m %s \033[92mFile:\033[0m %s      \r' % (recs, f))
        sys.stdout.flush()
    print '\n'


if __name__ == '__main__':
    strip_cerl(indir)                    