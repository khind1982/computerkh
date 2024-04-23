'''This module implements the Bindery class, which is responsible for
renaming image files according to the Wellcome Library's rules. Each
manifestation needs to have the front cover and end papers appear
before the content of the book. Finally, we have the rear end papers
and back cover, followed by the spine and edge shots.

We take the PQ ID portion of the image name, prepend to it the current
manifestation's b-number, and followed by an incrementing sequence
number.

For example, hin-wel-all-00000004-001-002R.jp2 becomes
<b_number>_hin-wel-all-00000004_<seq>.jp2

The instance copies files from the input directory passed to the
bind_book() method, renaming them, into the output directory.

'''
import os
import shutil

import lxml.etree as ET

from wimp.bnumbertracker import BNumberTracker

# collections = {}
# del_list = os.path.join(os.path.dirname(__file__), '..', '..',
#                         'libdata/eeb/eurobo_published_collections.txt')

# # Make a dict out of the contents of the file in del_list.
# # Use it to locate the appropriate XML file for the book in order
# # to determine the order in which covers and end shots should be
# # bound to the internal image shots.
# with open(del_list) as f:
#     for line in f:
#         parts = line.strip().split('/')
#         bookid = '-'.join(parts[1:])
#         collections[bookid] = line.strip()

class BinderyAlreadyProcessed(Exception): pass

class Bindery(object):
    # pylint: disable = E1101
    def __init__(self, book, manifestation):
        self.book = book
        self.manifestation = manifestation
        self.b_numbers = BNumberTracker()
        self.sequence = 1
        self.seq = lambda: str(self.sequence).zfill(4)
        self.back_cover_order = {
            '0003L': 0, '0004R': 1,
            '0000B': 2, '0000S': 3,
            '0000X': 4, '0000Y': 5,
            '0000Z': 6
        }
        self.sort_back_covers = lambda x, y: cmp(
            self.back_cover_order[x.split('-')[-1][0:5]],
            self.back_cover_order[y.split('-')[-1][0:5]]
        )
        self.bnum = self.manifestation.b_number
        inum = self.manifestation.i_number
        if self.b_numbers.seen_combination(self.bnum, inum) is True:
            raise BinderyAlreadyProcessed

        self.unique_bnumbers = [
            line.strip() for line
            in open(
                '/data/prd/eeb/wellcome_marc/unique_bnumbers.txt'
            ).readlines()]

        self.handover_xml = ET.parse(
            '/handover/eurobo/Collection3/well/%s.xml' %
            self.manifestation.manifestation_id)

        
        
    def front_covers(self):
        return self.get_covers(['0000F', '0001L', '0002R'])

    # This is a little trickier, since the simple alphanumeric sort
    # order is not the same as the order we want to apply to the
    # renamed images. The covers_sequence dictionary allows them
    # to be sorted appropriately.
    # def back_covers(self):
    #     #covers = sorted(
    #     return sorted(
    #         self.get_covers(
    #             self.back_cover_order.keys()
    #         ),
    #         self.sort_back_covers
    #     )
    #     #return covers

    def back_covers(self):
        _back = []
        for i in self.manifestation.cover_images:
            img_tuple = self.manifestation.pagetypes[i]
            if img_tuple[1] in ["Back board", "Back endpaper", "Spine", "Head edge", "Tail edge", "Foredge" "Interior front binding"]:
                _back.append(img_tuple)
        _back = sorted(_back, lambda x,y: cmp(self.back_page_cover_order[x[1]],
                                              self.back_page_cover_order[y[1]]))
        _back = [img[0] for img in _back]
        print _back
        return _back
    
    def get_covers(self, covers):
        _covers = []
        for c in sorted(self.manifestation.cover_images):
            for pattern in covers:
                if pattern in c:
                    _covers.append(c)
        return _covers

    def glue_covers(self, pages):
        for f in pages:
            root, ext = self.split_filename(f)
            shutil.copy(
                os.path.join(
                    self.covers_dir, f
                ),
                os.path.join(
                    self.output_dir, "%s_%s_%s.%s" % (
                        self.manifestation.b_number,
                        root, self.seq(), ext
                    )
                )
            )
            self.sequence += 1

    def stitch_pages(self, input_dir):
        for f in sorted(self.manifestation.images):
            root, ext = self.split_filename(f)
            orig_name = os.path.join(input_dir, f)
            out_name = os.path.join(
                self.output_dir, "%s_%s_%s.%s" % (
                    self.manifestation.b_number,
                    root, self.seq(), ext
                )
            )
            shutil.copy(orig_name, out_name)
            self.sequence += 1

    @staticmethod
    def split_filename(filename):
        root, ext = os.path.splitext(filename)
        ext = ext.replace('.', '')
        root = '-'.join(root.split('-')[0:4])
        return (root, ext)

    def bind_book(self, input_dir, output_dir):
        setattr(
            self, 'covers_dir', os.path.join(
                os.path.dirname(input_dir),
                os.path.basename(self.book.covers.path)
            )
        )

        # For books that occur only once in the collection (that is, b-numbers
        # that occur only once), we must not include the sequence number, as
        # it confuses the ingestion system at the library.

        if self.bnum in self.unique_bnumbers:
            output_dir = output_dir.replace('_SEQ', '')
        else:
            output_dir = output_dir.replace(
                'SEQ', self.b_numbers.get_seq_id(
                    self.manifestation.b_number
                ).zfill(3)
            )

        setattr(self, 'output_dir', output_dir)
        # setattr(
        #     self, 'output_dir', output_dir.replace(
        #         'SEQ', self.b_numbers.get_seq_id(
        #             self.manifestation.b_number
        #         ).zfill(3)
        #     )
        # )
        os.makedirsp(self.output_dir)

        self.glue_covers(self.front_covers())
        self.stitch_pages(input_dir)
        self.glue_covers(self.back_covers())

        self.b_numbers.update_b_number(
            self.manifestation.b_number,
            self.manifestation.i_number
        )
