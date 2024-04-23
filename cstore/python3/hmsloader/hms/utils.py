'''Miscellaneous functions, mainly for file manipulations.'''
# pylint: disable = invalid-name

import hashlib
import multiprocessing
import os
import stat

from collections import defaultdict
from collections import namedtuple
from glob import glob
from itertools import chain

import mimetypes

import magic

TMPDIR = '/var/tmp'

SessionConfig = namedtuple('SessionConfig',
                           ['s3_bucket', 'aws_profile', 'hms_host'])
HMS_ENVS = {
    'dev': SessionConfig(
        'cbghms-pre', 'devel', 'http://hms-store.dev.proquest.com'),
    'pre': SessionConfig(
        'cbghms-pre', 'devel', 'https://hms-store.pre.proquest.com'),
    'prod': SessionConfig(
        'cbghms', 'prod', 'https://hms-store.prod.proquest.com'),
}


def debug(text):
    pass


def mimetype(filename):
    '''Guess the file's mimetype from its name, and return it.
    '''
    return mimetypes.guess_type(filename)[0]


def image_type(filename):
    '''Extract the image type from its mime type string and return it.
    E.g. "image/jpeg" returns the part after "/", "jpeg"
    '''
    return mimetype(filename).split('/')[-1]


def is_image_type(filename):
    '''Return True if the file's mime type indicates it is an image, False
    otherwise.
    '''
    try:
        return 'image' in str(mimetype(filename))
    except TypeError:
        return False


def is_dpmi_file(filename):
    '''Does filename point to a DPMI XML file?
    '''
    return filename.endswith('_dpmi.xml')


def is_archive_file(filename):
    '''Is this an archive file? That is, a gzip or bz2 compressed tar file,
    or an uncompressed tar file?
    '''
    with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as filemagic:
        filetype = filemagic.id_filename(filename)

    print(filetype)
    return filetype
    # return 'application/x-tar' in str(mimetype(filename))


def file_type(filename):
    '''Check the passed filename and return its type as "image" or "dpmi", or
    None if neither of these.
    '''
    if is_image_type(filename):
        return "image"
    if is_dpmi_file(filename):
        return "dpmi"
    if is_archive_file(filename):
        _type = mimetype(filename)
        if _type is None:
            # We are looking at an uncompressed tar file
            return 'tar'
        return _type
    return None


def stat_file_size(filename):
    '''Get the size of the given file
    '''
    return os.stat(filename)[stat.ST_SIZE]


def get_checksum(filename, prefix):
    '''Calculate the file's MD5 checksum. If we already have a cached checksum
    for the file, return it in a 2-tuple (checksum, False). If the cached
    checksum file is older than the object file (indicating the object has been
    modified), or there is no cached checksum, the return is (checksum, True),
    indicating that the object needs to be uploaded to S3.
    '''
    # We might need to modify this, if we're looking at something like EEB
    _fn = os.path.basename(filename)
    cache_file = os.path.join(
        TMPDIR,
        'hmsloader', prefix,
        _fn.replace('-', '/') if prefix == 'eeb' else _fn)
    if os.path.exists(cache_file):
        if os.path.getmtime(filename) < os.path.getmtime(cache_file):
            return (open(cache_file).read(), False)
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:  # pylint: disable = invalid-name
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)

    hexdigest = md5.hexdigest()

    # Make the leaf and branch directories for the current file,
    # setting `exist_ok` to True so we don't have to worry too much
    # about potential races and synchronisation problems with other
    # processes in the pool.
    # We are also setting each part's mode to 0o775, so that the tool
    # can be used by anyone.
    os.makedirs(os.path.dirname(cache_file), mode=0o775, exist_ok=True)
    with open(cache_file, 'w') as cache:
        cache.write(hexdigest)
    os.chmod(cache_file, 0o775)
    return (hexdigest, True)


def file_metadata(file_data):
    '''Wrap get_checksum and file_type calls.
    '''
    file_dict = file_data[0]
    filename = file_dict['filename']
    prefix = file_data[1]
    checksum, update_s3 = get_checksum(filename, prefix)
    file_dict['md5'] = checksum
    file_dict['update_s3'] = update_s3
    file_dict['file_type'] = file_type(filename)
    return file_dict


def hash_name(filename):
    '''Calculate the MD5 checksum of the passed in filename, and return the
    first 5 characters from it. This is used to help mitigate key partitioning
    problems on S3 by creating randomised portions of the keyspace.
    '''
    basename = os.path.basename(filename)
    return '%s-%s' % (
        hashlib.md5(basename.encode()).hexdigest()[0:5], basename)


def do_checksums(args, files):
    '''Starts a multiprocessing pool for calculating the MD5 checksums
    of the files in the passed in list. This is used to verify the integrity
    of files after transfer across the network.'''
    debug("Calculating file checksums...")
    md5pool = multiprocessing.Pool(processes=args.num_procs)
    results = md5pool.map(file_metadata, [
        (f, args.prefix) for f in
        chain(files['dpmi'], files['images'])])

    md5pool.close()
    md5pool.join()
    debug(" Done\n")
    return results


def make_hms_img_name(file_data, idx):
    '''Given a basename and a sequence index, munge them together to make an
    object ID for HMS.
    '''
    filename = file_data['basename']
    fname = os.path.splitext(filename)[0]
    return "EEB_%s_%s_image" % (fname, idx)


def make_dpmi_name(file_data, idx):
    '''Generate and return a name to use as the object ID for DPMI files in
    HMS.
    '''
    filename = file_data['basename'].replace("_dpmi.xml", "")
    return "EEB_%s_pagethread_%s" % (filename, idx)


def unique_book_id(book_id, args):
    '''This wraps the plain CH-style book id (ned-kbn-all-000123456) in
    the HMS-style 'EEB_*_book' affixes. However, if we set a test ID using
    the -T flag, simply return it as is.
    '''
    if args.test_id:
        return args.test_id
    return "EEB_%s_book" % book_id


def find_in_env(args, attr):
    '''Get the passed attr from the HMS_ENVS key in args.hms_inst
    '''
    return getattr(HMS_ENVS[args.hms_inst], attr)


def get_s3_profile(args):
    '''Extract the HMS env from the args object and return it.
    '''
    return find_in_env(args, 'aws_profile')


def get_hms_host(args):
    '''Extract the HMS env from args, and return the corresponding HMS
    hostname.  '''
    return find_in_env(args, 'hms_host')


def get_bucket(args):  # pylint: disable = redefined-outer-name
    '''Return the name of the S3 bucket to use for the current session. This is
    either specified by the user with the `-b' option, in which case it is
    found in args.bucket, or is defaulted according to the value passed with
    the `-i' parameter.

    '''
    try:
        return args.bucket
    except AttributeError:
        return find_in_env(args, 's3_bucket')


class CopyrightTextNotFoundError(Exception):
    pass


def get_copyright(args, book_id):
    '''Get the copyright text for the current book. For the vast majority of
    books, we just want to use the Library's copyright text, but there are a
    few that have their own text. Check these first.'''

    general = os.path.join(
        args.copyright_dir, "copyright_statements_general.lut")
    special = os.path.join(
        args.copyright_dir, "copyright_statements_special.lut")

    # First we look for the book ID in the special case file. If it's there,
    # use the associated text. If it's not, extract the Library code from the
    # book ID (the group of characters after the first '-' in the book ID),
    # and look for it in the general case file. If not found there either,
    # quit with an error message.
    try:
        return find_copyright_text(special, book_id)
    except CopyrightTextNotFoundError:
        try:
            library_code = book_id.split('-')[1]
            return find_copyright_text(general, library_code)
        except CopyrightTextNotFoundError:
            raise RuntimeError('No copyright statement found for %s' % book_id)


def find_copyright_text(data_file, search):
    '''Open data_file and look for search term. If found, return the
    appropriate text, with ~ converted to new line. If not found, raise the
    custom CopyrightTextNotFoundError exception.'''
    with open(data_file) as crdata:
        for line in crdata.readlines():
            if line.startswith(search):
                return line.strip().split('|')[-1].replace('~', '\n')
    raise CopyrightTextNotFoundError


def build_file_data(args, book_id):
    files = defaultdict(list)

    debug("Getting file sizes and hashed names...")
    for f in get_dpmi_files(args.dpmi_dir, book_id):
        files['dpmi'].append({
            'filename': f,
            'basename': os.path.basename(f),
            'size': stat_file_size(f),
            'hashed_name': hash_name(f)
        })

    for f in get_image_files(args.book_images_path, args.cover_images_path):
        files['images'].append({
            'filename': f,
            'basename': os.path.basename(f),
            'size': stat_file_size(f),
            'hashed_name': hash_name(f)
        })
    debug(" Done\n")
    return files


def get_image_files(book_img_dir, cover_img_dir):
    """Walk the given directory, yielding each root/filename along the way.
    """
    # for root, dirs, files in os.walk(directory):
    for img_dir in [cover_img_dir, book_img_dir]:
        for root, dirs, files in os.walk(img_dir):
            try:
                dirs.remove('ocr')
            except ValueError:
                pass
            for filename in files:
                # print(filename)
                if is_image_type(filename):
                    yield os.path.join(root, filename)


def get_dpmi_files(directory, book):
    '''Look in the given directory for all DPMI files that match the current
    book, and yield them.
    '''
    debug("BOOK ID: %s" % book)
    for _file in sorted(glob(os.path.join(directory, "%s*_dpmi.xml" % book))):
        yield _file


def write_result(args, text):
    '''Attempts to write `text' to args.output_dir. This succeeds if it
    contains sys.stdout. Otherwise, it opens a file in args.output_dir named
    `book_id'.json and writes to that.  '''
    book_id = args.book_id
    try:
        args.output_dir.write(text)
    except AttributeError:
        outfile = os.path.join(args.output_dir, '%s.json' % book_id)
        with open(outfile, 'w') as outf:
            outf.write(text)
