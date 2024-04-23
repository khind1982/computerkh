import os

import lxml.etree as ET

from collections import OrderedDict

from commonUtils.fileUtils import buildLut
from wimp.image import Image
    
# We have a file that maps the Wellcome's i-number to their b-number.
# Slurp it in as a dict.
bnumber_mapping = buildLut('/data/prd/eeb/wellcome_marc/bnumber_mapping.txt')

class Manifestation(object):
    __nsmap = {
        'x': 'http://www.w3.org/2001/XMLSchema',
        'mets': 'http://www.loc.gov/METS/',
        'mix': 'http://www.loc.gov/mix/v20',
        'mods': 'http://www.loc.gov/mods/v3',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    }

    def __init__(self, path, working_dir):
        self.path = path
        self.working_dir = working_dir
        self.manifestation_id = os.path.basename(self.path)
        if path.endswith('000'):
            self.covers = True
            self.manifest_file = None
        else:
            self.covers = False
            self.manifest_file = os.path.join(
                self.path, '%s.xml' % self.manifestation_id
            )
            self.xml = ET.parse(self.manifest_file)

            # Grab the handover XML file, and parse it to get the page type
            # for the current manifestation's images. Store in a dict keyed
            # on image name, with the suffix removed.
            self.handover_xml = ET.parse(
                '/data/prd/eeb/wellcome/handover_docs/%s.xml' %
                self.manifestation_id
            )
            self.pagetypes = OrderedDict()
            for page in self.handover_xml.xpath('//itemimage'):
                self.pagetypes[
                    page.xpath(
                        './itemimagefile1')[0].text] = page.xpath(
                            './pagetype')[0].text 
            
    def __getattr__(self, attr):
        if attr in ['b_number', 'i_number']:
            id_type = attr[0]
            while True:
                try:
                    return self._id_numbers[id_type]
                except AttributeError:
                    setattr(self, "_id_numbers", self._get_ids_from_manifest())
        elif attr in ['png_dir', 'jp2_dir', 'raw_dir', 'out_dir']:
            output = attr.split('_')[0]
            return os.path.join(self.working_dir, output)
        else:
            raise AttributeError(
                "%s instance has no attribute '%s'" % (
                    self.__class__.__name__, attr
                )
            )

    @property
    def all_images(self):
        if self.covers is True:
            raise TypeError(
                "It is not possible to get image information for covers through"
                "the covers manifestation. Use the first manifestation proper"
                "and ask it for its cover_images"
            )
        while True:
            try:
                return self._all_images
            except AttributeError:
                setattr(self, "_all_images", {})
                for amdSec in [amdSec for amdSec
                               in self._manifest_xpath('//mets:amdSec')
                               if amdSec.attrib['ID'].startswith('IMG')]:
                    img_name = self._manifest_xpath(
                        './/mix:objectIdentifierValue', amdSec
                    )[0].text
                    self._all_images[img_name] = Image(
                        img_name, amdSec, self.__nsmap
                    )

    @property
    def images(self):
        while True:
            try:
                return self._images
            except AttributeError:
                setattr(self, "_images", {})
                for image in self.all_images.keys():
                    if image.split('-')[-2] != "000":
                        self._images[image] = self.all_images[image]

    @property
    def cover_images(self):
        while True:
            try:
                return self._cover_images
            except AttributeError:
                setattr(self, "_cover_images", {})
                for image in self.all_images.keys():
                    if image.split('-')[-2] == "000":
                        self._cover_images[image] = self.all_images[image]

    def _manifest_xpath(self, xpath, element=None):
        if element is None:
            element = self.xml
        return element.xpath(
            xpath, namespaces=self.__nsmap
        )

    def _get_ids_from_manifest(self):
        fst, snd = self._manifest_xpath(
            '//mods:recordContentSource'
        )[0].text.split('|')
        if fst.startswith('i'):
            i = fst
        else:
            i = snd
        # Make sure the b-number has exactly one b at the
        # beginning.
        b = bnumber_mapping[i]
        return {'b': b, 'i': i}
