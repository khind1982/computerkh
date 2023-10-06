"""Functions and facilities for handling common file
operations."""

import io
import itertools as it
import os
import stat
import warnings

from collections import defaultdict
from functools import partial, singledispatch
from fnmatch import fnmatch

import lxml.etree as et

# The export decorator, which marks functions as exportable.
# This should keep things clean if someone does a splat import.
from .meta import export as _export
from .outputstream import OutputStreamHandler


@_export
def build_input_file_list(infiles, from_file=False, pattern=None, enumerated=False):
    """Yield filenames collected according to parameters.

    :param infiles: list of files or directories
    :param from_file: boolean. If given, read targets from file
    :param pattern: glob pattern used to filter results
    :param enumerated: boolean. If given, wrap list builder in enumerate
    :returns: generator producing target filenames

    By default, :infiles: is treated as a list of filenames or
    directories to scan for files matching :pattern:. If
    :from_file: is True, treat the first item in :infiles: as a
    text file containing the full paths to the required files. Each
    item is yielded in turn.

    If :from_file: is False (the default), each member of :infiles: is
    tested. If it is a file, it is yielded. If it is a directory, it
    is walked with os.walk, and files matching :pattern: are yielded.

    If :pattern: is not given, all files under a target directory will
    be returned. :pattern: is ignored when a file is named explicitly
    on the command line, or when targets are provided in a file. It is
    assumed in these cases that the user knows what they want...
    """
    if isinstance(infiles, str):
        infiles = [infiles]

    if from_file:
        file_list_builder = partial(targets_from_file, infiles[0])
    else:
        file_list_builder = partial(targets_from_fs_walk, infiles, pattern)

    if enumerated:
        if enumerated is True:
            start = 0
        else:
            start = enumerated

        file_list_builder = partial(enumerate, file_list_builder(), start)

    yield from file_list_builder()


def targets_from_file(infile):
    yield from lazy_read_lookup_file(infile)


def _fs_walk(root, pattern, sort=True):
    for root, dirs, files in os.walk(root):
        if sort:  # pragma: no cover
            dirs.sort()
            files.sort()
        for f in files:
            if pattern is None or fnmatch(f, pattern):
                yield os.path.join(root, f)


def targets_from_fs_walk(infiles, pattern):
    for i in infiles:
        if os.path.isfile(i):
            yield i
        else:
            yield from _fs_walk(i, pattern)


@_export
@singledispatch
def lazy_read_lookup_file(  # pragma: no cover
        path,
        *,
        transform=lambda line: line.strip(),
        strip_comments=True,
        comment_chars=None
        ):
    """Reads a file and yields each line, according to the passed parameters.

    :param path: the file to read. Either a file system path, or an instance
            of io.StringIO or io.BytesIO
    :param transform: a callable object that will be applied to each line in
            the file. By default, this is str.strip()
    :param strip_comments: boolean - if True (default) remove comment lines
            from the file before returning the list. If False, comments are
            left in the returned list
    :param comment_chars: string, the characters that are used to indicate
            a comment in the input file. By default, '#'. A string of
            multiple characters can be given, if the input file is patho-
            logically badly formed.

    The transform parameter can be any callable that accepts a single string
    argument, and returns a string.
    """
    raise TypeError(f"Unsupported type ({type(path)}) for {path}")


# This implementation is used when "path" is given as a string,
# an instance of os.PathLike (as is created by the tmpdir_factory fixture)
# or an instance of pathlib.Path (a subclass of the os.PathLike metaclass)
@lazy_read_lookup_file.register(str)
@lazy_read_lookup_file.register(os.PathLike)
def _(path, **kwargs):  # type: ignore[no-redef]
    with open(path) as infile:
        yield from _process_file(infile, **kwargs)


# This implementation is used when "path" is an in-memory text buffer
@lazy_read_lookup_file.register(io.StringIO)  # type: ignore[no-redef]
def _(path: io.StringIO, **kwargs):
    yield from _process_file(path, **kwargs)


# This implementation is used when "path" is an in-memory bytes buffer
@lazy_read_lookup_file.register(io.BytesIO)  # type: ignore[no-redef]
def _(path: io.BytesIO, **kwargs):
    yield from _process_file(io.TextIOWrapper(path), **kwargs)


def _process_file(
        file_handle,
        *,
        transform=lambda line: line.strip(),
        strip_comments=True,
        comment_chars=None
        ):
    if comment_chars is None:
        comment_chars = '#'

    for line in file_handle:
        if line == '\n':
            continue
        if strip_comments and line[0] in comment_chars:
            continue
        yield transform(line)


@_export
def read_lookup_file(path, **kwargs):
    """An eager equivalent of the lazy_read_lookup_file function. It uses the
    same underlying implementation, but collects all results in a list, which
    is returned to the caller."""
    return list(lazy_read_lookup_file(path, **kwargs))


@_export
def parse_file_to_dict(
        path,
        *,
        accumulate_values=False,
        comment_chars=None,
        delimiter='|',
        secondary_delimiter=None
        ):
    """Call read_lookup_file with the given path, and convert
    the returned list to a dict using the delimiters"""
    lookup_data = lazy_read_lookup_file(
        path, comment_chars=comment_chars,
        transform=lambda l: l.strip().split(delimiter, maxsplit=1))
    if accumulate_values:
        d = defaultdict(list)
        for k, v in lookup_data:
            d[k].append(v)
    else:
        d = dict(lookup_data)

    def split(item):
        return item.split(secondary_delimiter)

    if secondary_delimiter and accumulate_values:
        for k, v in d.items():
            d[k] = list(it.chain(*[split(i) for i in v]))
    elif secondary_delimiter:
        for k, v in d.items():
            d[k] = split(v)

    return d


@_export
def file_to_lookup(*args, **kwargs):
    warnings.warn(
        """The function 'file_to_lookup' has been renamed to 'parse_file_to_dict'.
        The name 'file_to_lookup' will be removed in a future release;
        please start using 'parse_file_to_dict' instead.""",
        DeprecationWarning)
    return parse_file_to_dict(*args, **kwargs)


def parse_maybe_huge_xml(xmlfile):
    parser = et.XMLParser(remove_blank_text=True, strip_cdata=False)
    while True:
        try:
            return et.parse(xmlfile, parser)
        except et.XMLSyntaxError:
            parser = et.XMLParser(remove_blank_text=True, huge_tree=True)


def concatenate_singleton_files(
        root,
        output_dir,
        product=None,
        pattern='*.xml',
        records=None
        ):
    if not product:
        raise TypeError('product must not be None')
    if not records:
        records = 5000
    output_handler = OutputStreamHandler(
        root_dir=output_dir, bundled_output=True, product=product,
        records=records)
    for f in build_input_file_list(root, pattern=pattern):
        output_handler.write_output(parse_maybe_huge_xml(f), f)


@_export
def file_size(filepath):
    """Use os.stat to get filepath's size in bytes."""
    return os.stat(filepath)[stat.ST_SIZE]


@_export
def file_checksum(filepath, algorithm='md5', hexdigest=True):
    """Using :algorithm:, calculate the one-way hash for
    :filepath:. Return the hexdigest representation, unless
    :hexdigest: is set to False, in which case, return the
    plain digest format."""
    import hashlib
    h = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        while True:
            buf = f.read(65536)
            if not buf:
                break
            h.update(buf)
    if hexdigest:
        return h.hexdigest()
    return h.digest()
