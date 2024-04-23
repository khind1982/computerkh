import os
import re
import shutil
import subprocess as _subp
import sys

_read_file = lambda x, m='r': open(x, m).readlines()
_comment = lambda x: re.search(r'^($|#)', x)

class NoSuchDirectoryError(Exception): pass

def list_from_file(filename, mode='r'):
    '''Convert the contents of a file to a list, or return the empty
    list if the file doesn't exist.
    '''
    try:
        with open(filename, mode) as fh:
            return [ln.strip() for ln in fh.readlines() if not _comment(ln)]
    except IOError as e:
        if e.errno is 2:
            return []
        else:
            raise

def copy_tree(src, dst, on_intr=None, delete_first=False):
    # If the destination directory already exists, it's probably from a
    # previous (failed) run, so can safely be deleted.
    if delete_first is True:
        if os.path.exists(dst):
            shutil.rmtree(dst)
    try:
        _subp.check_output(
            [
                '/usr/local/bin/rsync',
                '-av', '--progress',
                '--rsh=ssh',
                '--rsync-path=/usr/local/bin/rsync',
                '--partial-dir=.rsync-partial',
                '--delay-updates',
                src,
                dst
            ]
        )
    except KeyboardInterrupt:
        if on_intr is None:
            raise
        print "Received KeyboardInterrupt. Cleaning up, please wait...",
        on_intr(dst)
        print " Done."
        sys.exit()

    except _subp.CalledProcessError:
        raise NoSuchDirectoryError
    
