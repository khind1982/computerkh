import os
from glob import glob

from wimp.manifestation import Manifestation

class Book(object):
    # pylint: disable = E1101
    def __init__(self, bookpath, working_dir):
        self.bookpath = bookpath
        self.working_dir = working_dir

    @property
    def delivery(self):
        return self.bookpath.split('/')[-2]

    @property
    def bookid(self):
        while True:
            try:
                return self._bookid
            except AttributeError:
                # pylint: disable = W0201
                self._bookid = self.bookpath.split('/')[-1]

    @property
    def manifest(self):
        while True:
            try:
                return self._manifest
            except AttributeError:
                setattr(
                    self, '_manifest', os.path.join(
                        '/data/prd/eeb/manifests', '%s.xml' % self.bookid
                    )
                )

    @property
    def manifestations(self):
        while True:
            try:
                return self._manifestations
            except AttributeError:
                # pylint: disable = W0201
                self._manifestations = [
                    Manifestation(path, self.working_dir) for path
                    in sorted(glob('%s/*' % self.bookpath))
                ]

    @property
    def covers(self):
        while True:
            try:
                return self._covers
            except AttributeError:
                for manifestation in self.manifestations:
                    if manifestation.manifestation_id.endswith('000'):
                        # pylint: disable = W0201
                        self._covers = manifestation
