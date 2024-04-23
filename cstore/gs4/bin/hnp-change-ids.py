#!/usr/local/bin/python2.7

# In the tif files, update hnp_53850 to 294128
# In the XML files, update hnp_53850 to 294128
# In the folder names, change hnp_53850 to 294128
# In the XML files, update the <HN_start_page_image> elements from hnp_53850 to 294128
# /HN_article/HN_start_page_image
# In the XML files, update the <HN_zone_image> elements from hnp_53850 to 294128
# /HN_article/HN_zone/HN_zone_image
# In the XML files, update the <HN_page_image> elements from hnp_53850 to 294128
# One function to process the XMLs
# One function to change the dirs and fnames

# Change the XMLs first!
# Change the directory paths last!
# Change the filenames between the last two commands.  

import sys
import os

import argparse
import shutil

import lxml.etree as et

parser = et.XMLParser(remove_blank_text=True)

def main(args):
    indir = args[0]
    oldstring = args[1]
    newstring = args[2]

    process_xmls(indir, oldstring, newstring, parser)

    process_dirs(indir, oldstring, newstring)

    print "Finished."

def walk_dirs_xml(indir):
    for root, dirs, files in os.walk(indir):
        for f in files:
            yield os.path.join(root, f)

def process_xmls(indir, oldstring, newstring, parser):
    # pass
    for f in walk_dirs_xml(indir):
        if f.endswith('.tif'):
            print "Processing file %s" % f
            image_process(f, oldstring, newstring)
        elif f.endswith('.xml'):
            print "Processing file %s" % f
            xmlfile = et.parse(f, parser)
            shutil.copyfile(f, "%s.bak" % f)
            for page in xmlfile.xpath('//HN_start_page_image'):
                newspage = change_text(page, oldstring, newstring)
            for zimage in xmlfile.xpath('//HN_zone_image'):
                newzimage = change_zone_text(zimage, oldstring, newstring)
            for page in xmlfile.xpath('//HN_page_image'):
                newhnpage = change_text(page, oldstring, newstring)
            print f
            newfname = fname_change(f, oldstring, newstring)
            with open(newfname, 'w') as writefile:
                writefile.write(et.tostring(xmlfile, pretty_print=True, xml_declaration=True, encoding="UTF-8"))
        else:
            continue

def change_text(page, oldstring, newstring):
    textfrag = page.text.split('_')
    if textfrag[1] == oldstring:
        page.text = '%s_%s_%s' % (textfrag[0], newstring, textfrag[2])
        return page

def change_zone_text(zimage, oldstring, newstring):
    textfrag = zimage.text.split('_')
    if textfrag[1] == oldstring:
        zimage.text = '%s_%s_%s_%s_%s' % (textfrag[0], newstring, textfrag[2], textfrag[3], textfrag[4])
        return zimage.text

def fname_change(f, oldstring, newstring):
    fcheck = f.split('_')
    if fcheck[3] == oldstring:
        newfname = '%s_%s_%s_%s_%s_%s' % (fcheck[0], fcheck[1], fcheck[2], newstring, fcheck[4], fcheck[5])
        if os.path.exists(f):
            os.rename(f, newfname)
            return newfname

def image_process(f, oldstring, newstring):
    if len(f.split('_')) == 5:
        imagefrag = f.split('_')
        if imagefrag[3] == oldstring:
            newimagename = '%s_%s_%s_%s_%s' % (imagefrag[0], imagefrag[1], 
            imagefrag[2], newstring, imagefrag[4])
            os.rename(f, newimagename)
    elif len(f.split('_')) == 7:
        imagefrag = f.split('_')
        if imagefrag[3] == oldstring:
            newimagename = '%s_%s_%s_%s_%s_%s_%s' % (imagefrag[0], imagefrag[1], 
            imagefrag[2], newstring, imagefrag[4], imagefrag[5], imagefrag[6])
            os.rename(f, newimagename)

def process_dirs(indir, oldstring, newstring):
    for root, dirs, files in os.walk(indir):
        print "Processing directory name %s" % root
        dirfrag = root.split('_')
        try:
            if dirfrag[1] == oldstring:
                newdir = '%s_%s_%s' % (dirfrag[0], newstring, dirfrag[2])
                os.rename(root, newdir)
        except IndexError:
            continue

if __name__ == '__main__':
    main(sys.argv[1:])