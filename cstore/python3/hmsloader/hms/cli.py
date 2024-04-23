'''Functions and classes used in parsing the command line.'''
# pylint: disable = invalid-name

import argparse
import os
import sys


def parse_args():
    """Encapsulate argument processing behind a function def.
    """
    _parser = argparse.ArgumentParser(
            description="Submit objects to HMS for processing and storage.")
    _parser.add_argument(
        '-i', dest='hms_inst', action='store',
        choices=['dev', 'pre', 'prod'], required=True,
        help='Specify the HMS instance to target')
    _parser.add_argument(
        '-b', dest='s3_bucket', action='store',
        help='S3 bucket to use as the staging post')
    _parser.add_argument(
        '-v', dest='verbose', action='store_true',
        help='Be verbose')
    _parser.add_argument(
        '-n', dest='s3_load_first', action='store_false',
        help='If specified, do not attempt to load objects '
        'to S3 before submitting to HMS')
    _parser.add_argument(
        '-d', dest='dryrun', action='store_true',
        help="Dry run. Don't send anything to S3, just save "
        'a copy of the payload and headers to file')
    _parser.add_argument(
        '-f', dest='force', action='store_true',
        help='Force reloading of objects to S3 before '
        'sending to HMS')
    _parser.add_argument(
        '-c', dest='copyright_dir', action='store',
        default='/dc/eurobo-images/migrations-samples',
        help='Directory where the copyright text lookup files live')
    _parser.add_argument(
        '-o', dest='output_dir', action=CheckDir, default=sys.stdout,
        help='Directory where to write HMS responses')
    _parser.add_argument(
        '-D', dest='dpmi_dir', action=CheckDir,
        default='/dc/eurobo-images/migrations-samples/dpmi',
        help='Directory where to find the DPMI files')
    _parser.add_argument(
        '-C', dest='client_id', action='store', default='CH',
        help='Specify the HMS client ID. Almost always "CH"')
    _parser.add_argument(
        '-S', dest='stop_after_post', action='store_true', default=False,
        help='Stop execution after POST submitted to HMS. '
        'Only useful for testing')
    _parser.add_argument(
        '-T', dest='test_id', action='store', default=None,
        help='Specify a fake book ID for testing purposes')
    _parser.add_argument(
        'prefix', action='store',
        help='The S3 prefix where items for the current load are to be found')
    _parser.add_argument(
        'root_dir', action=CheckDir,
        help='Directory to scan for objects to submit')
    return _parser.parse_args()


class CheckDir(argparse.Action):  # pylint: disable = too-few-public-methods
    '''Check that the directory passed for the given option exists, and is
    writable, if it's intended to take output.'''

    def __call__(self, parser, namespace, values, option_string=None):
        _dir = os.path.abspath(values)
        if getattr(self, "check_%s" % self.dest)(_dir):
            setattr(namespace, self.dest, _dir)
        else:
            self.fail(_dir, self.dest)

    @staticmethod
    def check_output_dir(dirname):
        '''Check that the output directory named on the command line exists and
        is writable by the current user.'''
        return all([os.access(dirname, os.F_OK), os.access(dirname, os.W_OK)])

    @staticmethod
    def check_root_dir(dirname):
        '''Make sure the root_dir exists'''
        return os.path.isdir(dirname)

    # we apply the same check to root_dir, copyright_dir and dpmi_dir, so let's
    # just reuse the definition.
    check_dpmi_dir = check_copyright_dir = check_root_dir

    @staticmethod
    def fail(dirname, dest):
        '''Print an error message and quit'''
        message = "Error: %s does not exist"
        if dest == 'output_dir':
            message = "%s, or is not writable" % message
        print(message % dirname, file=sys.stderr, flush=True)
        sys.exit(1)
