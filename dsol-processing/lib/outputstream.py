# -*- mode: python -*-

import sys, os

from extensions.osextensions import makedirsp

# An abstraction to handle directing output to different destinations.
#
# Instance holds some state so it can keep track of how many records it's
# processed, where to write output files, etc.

class OutPutStream(object): #pylint: disable = too-many-instance-attributes
    def __init__(self, attrs):
        # Default values. These get overwritten later.
        self.records = 0      # No limit
        self.directory = '.'  # Output to current directory
        self.io = sys.stdout  # Write to STDOUT by default
        self.filename = ''    # No default filename.
        self.files = 0

        options = self.parseOutputOptions(attrs)
        for k, v in options.items():
            setattr(self, k, v)

        if type(self.io) is not file:
            self.filename = self.io
        self.counter = 0

    def updateIOHandle(self, newName):
        self.filename = newName

    @staticmethod
    def parseOutputOptions(options):
        # Output options control how the emitted data is saved. It can be
        # written to stdout (default if no other options are given, written to a
        # named file, or written to a series of files of x records long, where x
        # is 5000 by default.

        # The arguments must be comma-delimited, and key/value pairs separated
        # by '='

        # Keys that are understood are:
        # io: the IO object to write output to. Can be an io object, or the
        #     value "std" to generate files named appropriately for handover.
        # filename: the name of a file to write to
        # directory: the directory in which to write output files. Default is .
        # records: the number of records to write to a file

        ret = {}
        if options is not '':
            for opt in options.split(','):
                for k, v in [opt.split('=')]:
                    # discard anything invalid or stupid
                    if k in ['io', 'filename', 'directory', 'records']:
                        ret[k] = v
        return ret

    def _openIO(self):
        while True:
            try:
                return open(self._buildIOPath(), 'w')
            except IOError as e:
                if e.errno == 2:
                    #pylint: disable = no-member
                    makedirsp(os.path.dirname(self._buildIOPath()))

    def _buildIOPath(self):
        return os.path.join(
            self.directory, self.filename + str(self.files).zfill(3) + '.xml')

    def incrementcounter(self):
        self.counter += 1

    @property
    def _fh(self):
        while True:
            try:
                return self._openFileHandle
            except AttributeError:
                self._openFileHandle = self._openIO() #pylint:disable=W0201

    def close_fh(self):
        # Closes the current file handle and then deletes it from the
        # instance. This ensures that the next time write() is called, it
        # in turn calls _fh() and gets a newly created file handle for the
        # next output file.
        self._openFileHandle.close()
        del self._openFileHandle

    def write(self, data):
        if data is None:
            return
        # pylint: disable = attribute-defined-outside-init
        self.fh = self._fh
        # If ouput stream is STDOUT, it doesn't make sense to mess around with
        # file handles.
        if self.fh.name is '<stdout>':
            pass
        # This test is needed to avoid generating an empty file in the output!
        elif int(self.counter) == 0:
            pass
        elif self.records is not 0:
            if int(self.counter) % int(self.records) == 0:
                self.files += 1
                try:
                    self.close_fh()
                except IOError as e:
                    print >> sys.stderr, (self.fh.name)
                    print >> sys.stderr, (e)
                self.fh = self._fh
        self.fh.write(data)
        self.incrementcounter()
