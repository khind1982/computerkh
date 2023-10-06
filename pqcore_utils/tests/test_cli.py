import sys

import pytest

import pqcoreutils.cli  # noqa
import pqcoreutils.fileutils


def test_cli():
    """Make sure the CLI parser works correctly."""
    args = pqcoreutils.cli.bundler_parse_args(
        ['-p', 'product', '-g', 'pattern', '-r', '1', '/tmp', '/tmp'])
    assert '/tmp' == args.outdir
    assert '/tmp' == args.indir
    assert 1 == args.records
    assert isinstance(args.records, int)
    assert 'product' == args.product
    assert 'pattern' == args.pattern


def test_cli_arguments_valid():
    sys.argv = [
        'program', '-p', 'product', '-g',
        'pattern', '-r', '1', 'notdir', '/tmp']
    with pytest.raises(ValueError):
        pqcoreutils.cli.bundler_main()


def test_bundler_main(mocker):
    mocker.patch('pqcoreutils.fileutils.concatenate_singleton_files')
    sys.argv = [
        'program', '-p', 'product',
        '-g', 'pattern', '-r', '1', '/tmp', '/tmp']
    pqcoreutils.cli.bundler_main()
    pqcoreutils.fileutils.concatenate_singleton_files.assert_called_once_with(
        '/tmp', '/tmp', 'product', 'pattern', 1)
