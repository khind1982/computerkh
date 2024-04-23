# -*- mode: python -*-
# pylint: disable = C0301, W0212
'''
Generate the statements necessary to update the image and pagecollection
threading tables for the product.

Required values from the data:

article ID
image file name

page collection ID (corresponds to the issue ID)
path to coords files (without the file extension)

Collect update information into batches of 1000 and execute them. Also
create an SQL file to apply to the production server. This should make a
copy of the current threading and pagecollection_threading tables, append
the updates to them and then swap the update tables in place of the active
ones.

'''

import importlib
import os

from collections import OrderedDict

from applogging import get_logger
from confreader import ConfReader
from xpaths import get_xpaths

config = ConfReader()


class DocumentThreading(object):
    '''Gather information from each document relating to the image
    threading. Rather than directly updating the preprod instance of
    the database, and then having to synchronise the whole database
    for each damned update, create a simple CSV file with the new
    values to add, which can then be imported using the mysql command
    line. We will also need to check for duplicates, since that can
    confuse the media service.

    '''

    __shared_state = {
        'threading_file': None
    }

    def __init__(self, document, product, output_dir=None):
        ''' Receives an instance of etree.Element and a string denoting
        the product.'''
        self.__dict__ = self.__shared_state
        self.document = document
        if output_dir is None:
            self.output_dir = '.'
        else:
            self.output_dir = output_dir
        if self.threading_file is None:  # pylint: disable = E0203
            self.threading_file = open(
                    os.path.join(self.output_dir, 'threading.txt'), 'w')
        self.product = product   #  self.document._cfg['product']

    @property
    def xml(self):
        return self.document.data

    @property
    def xpaths(self):
        while True:
            try:
                return self._xpaths
            except AttributeError:
                self._xpaths = get_xpaths(self.product)

    @property
    def rules(self):
        while True:
            try:
                return self._rules
            except AttributeError:
                self._rules = self._import_rules(self.product)

    @property
    def articleid(self):
        return self.rules.articleid(
            self.document._cfg['pruned_basename']
        )

    @property
    def journalid(self):
        return self.rules.pmid(
            self.product, self.xml
        )

    @property
    def pcid(self):
        return self.rules.pcid(self.product, self.articleid)

    @property
    def pcid_img_path(self):
        return self.rules.pcid_img_path(
                self.product, self.document._cfg['pruned_basename'])

    @property
    def has_apdf(self):
        return self.xml.findtext('.//journal/apdf_available')


    def do_threading(self):
        ''' Extract the page's page number (the page sequence),
        joural ID, and image file name. Output is:
        {ARTICLEID}, , /{JID}/{YEAR}/{MONTH}/coords/{ARTICLEID}, co  (once per article)
        {ARTICLEID}, {PAGENO}, /{JID}/{PCID}/jpeg/{IMGFILENAME}   (per image)
        '''

        zones = self.xml.xpath(self.xpaths['zone'])
        coords = ",%(articleid)s,,/%(jid)s/%(year)s/%(month)s/coords/%(articleid)s,co\n" %  {
            'jid': self.journalid,
            'articleid': self.articleid,
            'year': self.year,
            'month': self.month,
        }

        if self.has_apdf:
            apdf = ",%(articleid)s,,/%(jid)s/%(pcid)s/apdf/%(apdf_name)s,apdf\n" % {
                    'jid': self.journalid,
                    'articleid': self.articleid,
                    'pcid': self.pcid_img_path,
                    'apdf_name': "%s.pdf" % self.articleid
                    }
            coords = "%s%s" % (coords, apdf)

        img_thr = OrderedDict()
        images_for_pc_threading = {}
        for zone in zones:
            image_name = zone.xpath(self.xpaths['images'])[0].text.replace('jp2', 'jpg')
            pageno = zone.xpath(self.xpaths['page_sequence'])[0].text
            img_data = {
                'image_name': image_name,
                'jid': self.journalid,
                'month': self.month,
                'pageno': pageno,
                'pcid': self.pcid_img_path,
                'year': self.year,
            }

            img_row = ",%(articleid)s,%(pageno)s,/%(jid)s/%(pcid)s/jpeg/%(image_name)s\n" % {
                'articleid': self.articleid,
                'pageno': pageno,
                'jid': self.journalid,
                'pcid': self.pcid_img_path,
                'image_name': image_name,
            }

            # We need to keep two sets of image data handy.
            # The first, img_thr, is used to build the threading
            # table data.
            # The second, images_for_pc_threading, is used to
            # build the pagecollection_threading data.
            img_thr[image_name] = img_row
            images_for_pc_threading[image_name] = img_data

        self.threading_data = '%s' % coords

        for line in img_thr.keys():
            # pylint: disable = W0201
            self.threading_data = '%s%s' % (self.threading_data, img_thr[line])
            img = images_for_pc_threading[line]
            PageCollectionThreading(self.pcid, img, self.output_dir)

        self.threading_file.write(self.threading_data)

    @staticmethod
    def _import_rules(product):
        # we need to import the correct set of rules from the mappings.rules
        # packages, but we don't know until runtime which we want. Since all
        # products produced according to the Leviathan spec will have a
        # mappingname value of "leviathan" in the config, we can check for
        # its presence and import the right set of rules.
        print "RULES: %s" % product
        if config.get(product, 'mappingname') in ['leviathan', 'gerritsen']:
            _rules = "LeviathanRules"
        else:
            _rules = "APSRules"

        return importlib.import_module('mappings.rules.%s' % _rules)

    @property
    def year(self):
        return self.pcid.split('_')[1][0:4]

    @property
    def month(self):
        return self.pcid.split('_')[1][4:6]

    @staticmethod
    def flush_pagecollection_threading():
        # a delegate method to flush PageCollectionThreading data.
        PageCollectionThreading('FLUSH')

class PageCollectionThreading(object):
    '''Gather pagecollection_threading data from XML files. We use shared
    state, because a pagecollection is made up of many files, so we
    need to keep hold of lots of different bits of information before
    a given pagecollection is complete.

    '''
    # Shared state.
    __shared_state = {
        'pcid_images': {},
        'pcid_issue': {},
        'pcid': None,
        'pcid_file': None,
    }

    def __init__(self, pcid=None, img_data=None, output_dir=None):
        #pylint:disable=E0203
        self.__dict__ = self.__shared_state
        if not pcid == self.pcid:
            if pcid == "FLUSH":
                self.flush_pc_images()
                return
            if self.pcid is not None:
                self.flush_pc_images()
            self.pcid = pcid
            self.pcid_images = {pcid: {}}
        self.output_dir = output_dir
        if self.pcid_file is None: # pylint: disable = E1101
            outf = os.path.join(self.output_dir, 'pagecollection_threading.txt')
            self.pcid_file = open(outf, 'w')
        self.img_data = img_data
        self.pcid_images[pcid][img_data['pageno']] = img_data['image_name']

    def __getattr__(self, attr):
        if attr.startswith('pcid_'):
            key = attr.split('_')[-1]
            return self.img_data[key]

    def flush_pc_images(self):
        self.write_pcid_to_file()
        self.pcid_images = {}

    def write_pcid_to_file(self):
        # Save a bit of typing (and duplication...)
        xml_path = "/%s/%s/%s/xml" % (self.pcid_jid, self.pcid_year, self.pcid_month)
        # Assemble the PCMI lines.
        pcmi = ",%(pcid)s,,%(xml_path)s/pcmi/%(pcid)s.xml,PCMI\n" % {
            'pcid': self.pcid,
            'xml_path': xml_path
        }

        # Next, we need to create the PAGEMAP and SCALED_IMG rows
        # for each image.
        pagemaps = []
        scaled_imgs = []
        img_rows = []
        for pageno in sorted([int(pageno) for pageno in self.pcid_images[self.pcid].keys()]):

            # PAGEMAP lines first
            pagemap = ",%(pcid)s,%(pageno)d,%(xml_path)s/pagemap/%(imgname)s,PAGEMAP\n" % {
                'pcid': self.pcid,
                'pageno': pageno,
                'xml_path': xml_path,
                'imgname': self.pcid_images[self.pcid][str(pageno)].replace('jpg', 'xml')
            }
            pagemaps.append(pagemap)
            # And finally the SCALED_IMG lines
            scaled_img = ",%(pcid)s,%(pageno)d,/%(jid)s/%(pcid_img_path)s/scaled/%(imgname)s,SCALED_IMG\n" % {
                'pcid': self.pcid,
                'pageno': pageno,
                'jid': self.pcid_jid,
                'imgname': self.pcid_images[self.pcid][str(pageno)],
                'pcid_img_path': self.img_data['pcid']
            }
            scaled_imgs.append(scaled_img)
            img_row = "%s%s" % (pagemap, scaled_img)
            img_rows.append(img_row)
        self.pcid_file.write(pcmi)
        for img_row in img_rows:
            self.pcid_file.write(img_row)
