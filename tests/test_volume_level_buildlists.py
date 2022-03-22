"""Tests for volume_level_buildlists, an application to create buildlists from Acta/PLD volumes.

Input would be the desired volume or volumes, as a file or direct to the command line files (nargs+)

Output would be a file of IDs

Dataflow:
- Parse arguments
- Set up target volumes list
- Iterate over input files (don't need to test - pqcoreutils)
- Collect IDs from target files (don't need to test - lxml)
- Write to output file (just test the argument scenarios)

"""
import latin_products.analysis.buildlists as vl

import os

import pytest

import pqcoreutils.fileutils as fileutils


@pytest.fixture
def output_dir(tmpdir_factory):
    """A base input directory for test output files."""
    return tmpdir_factory.mktemp("output")


class TestTargetVolumes:

    def test_target_volumes_file(self):
        inp = os.path.join(
            os.path.dirname(__file__), 'testdata/volumes.txt'
        )
        result = vl.target_volumes(inp)
        assert result == ['/dc/migrations/latin/acta/legacy_data/records/asa01.cvt']

    def test_target_volumes_single(self):
        inp = '/dc/migrations/latin/acta/legacy_data/records/asa01.cvt'
        result = vl.target_volumes(inp)
        assert result == ['/dc/migrations/latin/acta/legacy_data/records/asa01.cvt']

    def test_target_volumes_nargs(self):
        inp = ['/dc/migrations/latin/acta/legacy_data/records/asa01.cvt',
               '/dc/migrations/latin/acta/legacy_data/records/asa02.cvt']
        result = vl.target_volumes(inp)
        assert result == inp


@pytest.mark.parametrize("infile,num", [
    (os.path.join(os.path.dirname(__file__), 'testdata/volumes.txt'), 3364),
    (['/dc/migrations/latin/acta/legacy_data/records/asa01.cvt',
      '/dc/migrations/latin/acta/legacy_data/records/asa02.cvt'], 6451),
    ('/dc/migrations/latin/acta/legacy_data/records/asa01.cvt', 3364)
])
def test_main(output_dir, infile, num):
    """Given target volumes, the IDs from each volume are written to the specified
    output file"""
    outfile = f'{output_dir}/build_targets.txt'
    args = vl.parse_args([infile, '--idpath', './/idref/text()', '-o', outfile])
    vl.main(args)
    assert os.path.isfile(outfile)
    ids = fileutils.read_lookup_file(outfile)
    assert len(ids) == num
    assert ids[:3] == [
        'Z000068317',
        'Z100068318',
        'Z100068319'
    ]
