#!/usr/local/bin/python2.6
# -*- mode: python -*-

''' An intermediate layer of abstraction between the truly abstract
AbstractStream and much more concrete XMLStream and TextStream types.
Its __init__() method handles correct construction of the file list
that points the streamdata() method to the right location on disk to
find the data we are transforming. '''

import os
import sys
#sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

import glob #, fnmatch
from streams.abstractstream import AbstractStream

from cstoreerrors import CStoreDataStreamSuffixError, CStoreDataStreamError
from commonUtils.fileUtils import locate

class FileStream(AbstractStream):
    def __init__(self, cfg):
        super(FileStream, self).__init__(cfg)
        self._stream = cfg['stream']
        self.cfg = cfg
        self.cfg['filesInStream'] = 0

        if 'dataRoot' in self.streamOpts.keys():
            # This is triggered if we want to run the process over
            # only a subsection of a data set which is divided by
            # journal/issue/date, like EIMA and Vogue. This is not
            # relevant for IIMP/IIPA, where the data is all contained
            # in a single directory. self.locate returns a generator.

            # We can optionally follow symlinks. This is not the
            # default behaviour, and must be explicitly requested by
            # the caller.
            if 'followlinks' in self.streamOpts.keys():
                followlinks = True
            else:
                followlinks = False

            self._files = locate(self._stream, self.streamOpts['dataRoot'], followlinks=followlinks)

        else:
            # There are three possible valid values for the stream:
            # A file glob pattern (which must be quoted on the commandline to prevent
            #  it being expanded by the shell)
            # A directory path, which contains files ending with the supplied suffix ('.xml' by default)
            # A single file
            suffix = cfg['suffix'] if 'suffix' in cfg else '.xml'
            fileglob = glob.glob(self._stream)

            if os.path.isfile(self._stream):
                self._files = [self._stream]
            elif os.path.isdir(self._stream):
                self._files = [os.path.join(self._stream, fn) for fn in os.listdir(self._stream) if fn.endswith(suffix)]
                if len(self._files) == 0:
                    raise CStoreDataStreamSuffixError("No files found ending with %s" % suffix)
            elif len(fileglob) > 0:
                self._files = fileglob
            else:
                raise CStoreDataStreamError("Invalid data stream: %s" % self._stream)

    # There is a limit to the number of files that glob.glob() will
    # return (49k ish) so we need to use a different approach when we
    # want to transform a large data set contained in a large number of
    # files, such as Vogue. The locate method takes a pattern (fnmatch
    # or glob compatible) and an optional path. It searches under the
    # path for files matching the pattern using os.walk and so is not
    # subject to the same limitation as glob.glob()

    # When using this method, it is safe to call it like this:

    # fileList = self.locate(pattern, root)

    # since Python will see the yield statement, and return an iterator
    # generator.  This generator can then be used in a loop (as we see
    # in the streamdata method) and will return one item at a time. No
    # expensive operations needed to build the complete list up front.

    # I have enhanced the locate method to take a glob pattern as the
    # second argument.  This allows us to provide patterns in any module
    # or app that uses this class, which in turn means we can split data
    # sets easily at run time. As an example, the metavogue script uses
    # the TextStream (which inherits from FileStream), and it has become
    # desirable to be able to run multiple instances of the script over
    # sections of the data. With this enhancement, that can be achieved
    # like this:

    # metavogue -s '/dc/vogue/handover/19[0-4]*' \
    #   -d /dc/scratch/bellatrix/vogue_metadata \
    #   -r ~/resize.list '*.xml'

    # metavogue -s '/dc/vogue/handover/19[5-9]*' \
    #   -d /dc/scratch/bellatrix/vogue_metadata \
    #   -r ~/resize.list '*.xml'

    # (run each in a separate terminal session)

    # Note that to take advantage of this new feature, the argument to
    # the -s flag must be enclosed in single quotes to prevent the shell
    # attempting to expand the pattern before it gets into the app. The
    # same applies to the pattern argument.

    # def locate(self, pattern, root=os.curdir):
    #     for directory in glob.glob(os.path.abspath(root)):
    #         for path, dirs, files in os.walk(os.path.abspath(directory)):
    #             dirs.sort()
    #             for filename in sorted(fnmatch.filter(files, pattern)):
    #                 self.cfg['filesInStream'] += 1
    #                 yield os.path.join(path, filename)
