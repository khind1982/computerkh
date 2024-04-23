# -*- mode: python -*-

import fnmatch
import glob
import hashlib
import os
import re
import stat
import sys

from functools import partial
from itertools import groupby


def locate(pattern, root=os.curdir, followlinks=False):
    if not os.path.isdir(root):
        raise RuntimeError(
            "Path does not exist, or is not a directory: %s" % root)

    for directory in sorted(glob.glob(os.path.abspath(root))):
        for path, dirs, files in os.walk(os.path.abspath(directory),
                                         followlinks=followlinks):
            dirs.sort()
            for filename in sorted(fnmatch.filter(files, pattern)):
                yield os.path.join(path, filename)


# Mimic the UNIX utility `touch' (when called with no options)
def touch(filename):
    try:
        os.utime(filename, None)
    except OSError:
        open(filename, 'a').close()


def buildLut(filename, delimiter='|', commentChars='#;', value_delimiter=None):
    ''' Open the named file and construct a lookup table from its contents.
    The field delimiter is the pipe '|' by default, but can be specified by the
    caller. Lines beginning with a character in commentChars are treated as
    comments and not included in the lookup data. Empty lines are also ignored.

    If value_delimiter is specified, the value is further split on that
    character, and the resulting list object is inserted into the lookup as
    the value. It is safe to use the same character for both delimiters, since
    the first split() is applied only once, to yield a key/value pair.

    If you are good, and put your lookup files in ../../libdata, then you only
    need to pass in the filename, without any path information. If your lookup
    file lives elsewhere, then you must make sure to supply enough path detail
    to allow this function to find it.
    '''

    commentRe = re.compile('^[' + commentChars + ']|$')
    luTable = {}
    try:
        with open(_buildPath(filename), 'r') as lutfile:
            for key, value in [line.rstrip().split(delimiter, 1) for line
                               in lutfile if not commentRe.match(line)]:
                if value_delimiter is not None:
                    value = [v.strip() for v in value.split(value_delimiter)]
                luTable[key] = value
    except IOError:
        # If the file doesn't exist, create it.
        touch(_buildPath(filename))
    return luTable

# buildListLut is a partially applied derivative of buildLut, with
# value_delimiter set to ','.
buildListLut = partial(buildLut, value_delimiter=',')


def _buildPath(filename):
    if os.path.isabs(filename):
        # Absolute path
        return filename
    elif os.path.exists(_defaultPath(filename)):
        # Relative path, with reference to ../../libdata
        return _defaultPath(filename)
    else:
        # Any other case. If the file doesn't exist, the context manager within
        # which we try to open the file, will complain accordingly.
        return filename


def _defaultPath(filename):
    return os.path.join(os.path.dirname(__file__), '../../libdata/', filename)


def stream_as_records(strio, delimiter):
    '''Split input file <strio> on <delimiter>, returning a tuple of values
    from itertools.groupby, except that instead of the group iterator, we
    coerce it to a list.
    '''
    l = []
    for key, group in groupby(strio, lambda line: line.startswith(delimiter)):
        l.append((key, list(group)))
    return l


def get_file_size(path):
    'Return the size in bytes of the file at <path>'
    return os.stat(path)[stat.ST_SIZE]


def get_file_checksum(path, scheme=None, hexdigest=True, blocksize=65536):
    'Return the checksum of <path>, according to <scheme>'
    if scheme is None:
        scheme = "md5"
    m = hashlib.new(scheme)
    _path = open(path, 'rb')
    buf = _path.read(blocksize)
    while len(buf) > 0:
        m.update(buf)
        buf = _path.read(blocksize)
    if hexdigest is True:
        return m.hexdigest()
    else:
        return m.digest()
