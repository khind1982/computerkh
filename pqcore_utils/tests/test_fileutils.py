"""Tests for functions in the pqcoreutils.fileutils module."""
import datetime
import hashlib
import io
import os
import pathlib
import textwrap

import lxml.etree as et
import pytest

import pqcoreutils

from pqcoreutils import build_input_file_list
from pqcoreutils import read_lookup_file
from pqcoreutils import lazy_read_lookup_file
from pqcoreutils import parse_file_to_dict
from pqcoreutils import file_to_lookup
from pqcoreutils.fileutils import concatenate_singleton_files
from pqcoreutils.fileutils import parse_maybe_huge_xml


@pytest.fixture
def test_data_dir(tmpdir_factory):
    """Build a directory containing some files we can walk over to
    test the build_input_file_list function's behaviour."""
    rootdir = tmpdir_factory.mktemp("test_data")
    for i in range(3):
        subdir = rootdir.mkdir(f"test_subdir_{i}")
        for j in range(1, 11, 1):
            for sfx in ['xml', 'txt', 'log', 'bz2']:
                fn = subdir.join(f"test-file-{i}-{j}.{sfx}")
                fn.write("test file.")
    return rootdir


@pytest.fixture
def singleton_xml_files(tmpdir_factory):
    """Build a directory containing some single xml files we can use
    to test outputstreamhandler"""
    rootdir = tmpdir_factory.mktemp("test_xmls")
    xml = textwrap.dedent('''\
        <?xml version='1.0' encoding='utf-8'?>
        <root>
          <title>abc</title>
          <author>Someone</author>
        </root>
        ''')
    for i in range(3):
        fn = rootdir.join(f"{i}.xml")
        fn.write(xml)
    return rootdir


@pytest.fixture
def huge_tree_xml():
    return os.path.join(os.path.dirname(__file__), 'fixtures/huge_tree.xml')


@pytest.fixture
def cdata_xml():
    return os.path.join(os.path.dirname(__file__), 'fixtures/cdata.xml')


@pytest.fixture
def target_spec_file(tmpdir_factory):
    """Create a file containing file paths. It also contains a mix
    of Windows and UNIX line endings, just to be thorough."""
    fn = tmpdir_factory.mktemp("filespec").join("infiles.txt")
    fn.write("""# a comment\r\n/a/b/c.txt\r\n/a/b/d.txt\n/a/e/f.txt""")
    return fn


@pytest.fixture
def sample_flat_file(tmpdir_factory):
    fn = tmpdir_factory.mktemp("tests").join("sample_flat_file.txt")
    fn.write(textwrap.dedent(
        """\
        # Ignore this comment line
        line 1
        line 2
        line 3

        line 4
        """
        ))
    print(type(fn))
    print(isinstance(fn, os.PathLike))
    return fn


@pytest.fixture
def sample_lookup_file(tmpdir_factory):
    fn = tmpdir_factory.mktemp("tests").join("sample_lookup_file.txt")
    fn.write(textwrap.dedent(
        """\
        # Ignore this comment line

        key1|value1
        key2|value2_a;value2_b;value2_c
        key3|value3

        """
        ))
    return fn


@pytest.fixture
def multi_delimiters_lookup(tmpdir_factory):
    fn = tmpdir_factory.mktemp("tests").join("multi_delimiters_lookup.txt")
    fn.write(textwrap.dedent(
        """\
        # Comment

        key1|value1a|value1b
        key2|value2a|value2b
        """
        ))
    return fn


@pytest.fixture
def accumulate_dupe_keys_lookup(tmpdir_factory):
    fn = tmpdir_factory.mktemp("tests").join("accumulate_dks_lookup.txt")
    fn.write(textwrap.dedent(
        """\
        ; Comment

        key1|value1a
        key2|value2a
        key2|value2b
        """
        ))
    return fn


@pytest.fixture
def secondary_split_lookup(tmpdir_factory):
    fn = tmpdir_factory.mktemp("tests").join("2ary_split_lookup.txt")
    fn.write(textwrap.dedent(
        """\
        ; A comment

        key1|value1a;value1b;value1c
        key2|value2a
        key3|value3a;value3b
        key2|value2b;value2c
        """
        ))
    return fn


def test_build_file_list(test_data_dir, target_spec_file):
    """Run build_input_file_list with default params."""
    files = list(build_input_file_list(test_data_dir.strpath))
    assert len(files) == 120

    # Provide a file suffix pattern to limit filter the matches
    files = list(build_input_file_list(test_data_dir.strpath, pattern='*.xml'))
    assert len(files) == 30
    assert all([file.endswith('xml') for file in files])

    # Pass in two directories to scan, and check the output.
    dir1, dir2, dir3 = [
            os.path.join(test_data_dir.strpath, i) for i
            in sorted(os.listdir(test_data_dir.strpath))]
    files = list(build_input_file_list(
        [dir1, dir2], pattern='*.xml'))
    assert len(files) == 20
    assert all([file.endswith('xml') for file in files])

    # Pass in an explicit file name. Should just return it.
    filepath = os.path.join(
            dir1, sorted(os.listdir(dir1))[0])
    assert list(build_input_file_list(filepath)) == [filepath]

    # And the same again, but with the filename wrapped in a list.
    assert list(build_input_file_list([filepath])) == [filepath]

    # Check targets specified in a file. We want to accept
    # UNIX and Windows line endings, so people don't have to remember the
    # right one. Python's str.strip takes care of it for us.
    files = list(build_input_file_list(
        target_spec_file.strpath, from_file=True))
    assert files == ['/a/b/c.txt', '/a/b/d.txt', '/a/e/f.txt']

    # If we get more than one file and are told "from_file=True",
    # ignore all but the first and print a warning.
    files = list(
            build_input_file_list(
                [target_spec_file.strpath, dir1],
                from_file=True))
    assert len(files) == 3


def test_build_file_list_enumerated(test_data_dir, target_spec_file):
    '''The same as the previous test, just using the enumerated=True param to
    get an enumerated list.'''
    results = list(
        build_input_file_list(test_data_dir.strpath, enumerated=True))
    assert len(results) == 120

    assert isinstance(results[0], tuple)
    assert results[0][0] == 0
    assert results[1][0] == 1

    # Same thing, but set enumerated to an integer. Ensure counting starts at
    # this value
    results = list(
        build_input_file_list(test_data_dir.strpath, enumerated=2))

    assert results[0][0] == 2
    assert results[1][0] == 3

    # Check targets specified in a file. We want to accept
    # UNIX and Windows line endings, so people don't have to remember the
    # right one. Python's str.strip takes care of it for us.
    results = list(build_input_file_list(
        target_spec_file.strpath, from_file=True, enumerated=3))

    assert results[0] == (3, '/a/b/c.txt')
    assert results[1] == (4, '/a/b/d.txt')
    assert results[2] == (5, '/a/e/f.txt')
    assert len(results) == 3


def test_lazy_read_lookup_file(sample_flat_file):
    """The function lazy_read_lookup_file is an iterator generator."""
    results = lazy_read_lookup_file(sample_flat_file)
    assert hasattr(results, '__next__')


def test_read_lookup_file(sample_flat_file):
    """Check the file reader."""
    filename = sample_flat_file.strpath
    assert isinstance(filename, str)
    assert read_lookup_file(filename) == [
            'line 1', 'line 2', 'line 3', 'line 4']


def test_read_lookup_file_pathlike(sample_flat_file):
    """Check the file reader can handle an instance of
    os.PathLike."""
    assert isinstance(sample_flat_file, os.PathLike)
    assert read_lookup_file(sample_flat_file) == [
            'line 1', 'line 2', 'line 3', 'line 4']


def test_read_lookup_file_pathlib_path(sample_flat_file):
    """Check the file reader can handle an instance of
    pathlib.Path."""
    filename = pathlib.Path(sample_flat_file.strpath)
    assert isinstance(filename, pathlib.Path)
    assert read_lookup_file(filename) == [
            'line 1', 'line 2', 'line 3', 'line 4']


def test_read_lookup_file_with_string_io():
    """If passed a StringIO object, read it as though it were a file
    and behave as expected."""
    file_data = io.StringIO('''line 1\nline 2\nline 3\nline 4\n''')
    assert read_lookup_file(file_data) == [
        'line 1', 'line 2', 'line 3', 'line 4']


def test_read_lookup_file_with_bytes_io():
    """As above, but using a BytesIO object instead of StringIO"""
    file_data = io.BytesIO(b'''line 1\nline 2\nline 3\nline 4\n''')
    assert read_lookup_file(file_data) == [
        'line 1', 'line 2', 'line 3', 'line 4']


def test_read_lookup_file_fails_on_unknown_param_type():
    with pytest.raises(TypeError) as exc:
        read_lookup_file(123)
    assert "Unsupported type" in str(exc)


def test_read_lookup_file_includes_comments(sample_flat_file):
    data = read_lookup_file(
        sample_flat_file.strpath,
        transform=lambda l: l.strip(),
        strip_comments=False,
        comment_chars='#'
        )
    assert data[0].startswith('#')
    assert data[1:] == ['line 1', 'line 2', 'line 3', 'line 4']


def test_parse_file_to_dict(sample_lookup_file):
    """Make sure we get sensible values back when converting
    a lookup file to a dict"""
    data = parse_file_to_dict(sample_lookup_file.strpath)
    assert isinstance(data, dict)
    assert data['key1'] == 'value1'


def test_lookup_with_multiply_occurring_delimiter(multi_delimiters_lookup):
    """Sometimes, the delimiter will appear more than once on a line."""
    data = parse_file_to_dict(multi_delimiters_lookup.strpath)
    assert data['key1'] == 'value1a|value1b'


def test_accumulate_duplicated_keys(accumulate_dupe_keys_lookup):
    """Accumulate multiple values for a duplicated key"""
    data = parse_file_to_dict(
            accumulate_dupe_keys_lookup.strpath,
            comment_chars=';', accumulate_values=True)
    assert data['key1'] == ['value1a']
    assert data['key2'] == ['value2a', 'value2b']


def test_secondary_split_no_accumulation(secondary_split_lookup):
    """If the caller passes a value for secondary_delimiter, return a dict
    whose values are lists, generated from splitting the value on that
    secondary_delimiter. e.g. key1|value1a;value1b;value1c ->
    {'key1': ['value1a', 'value1b', 'value1c']}
    """
    data = parse_file_to_dict(
            secondary_split_lookup.strpath,
            comment_chars=';', delimiter='|',
            secondary_delimiter=';')
    assert data['key1'] == ['value1a', 'value1b', 'value1c']
    assert data['key2'] == ['value2b', 'value2c']
    assert data['key3'] == ['value3a', 'value3b']


def test_secondary_split_with_accumulation(secondary_split_lookup):
    """Now the same thing, but with accumulate_values=True as well"""
    data = parse_file_to_dict(
            secondary_split_lookup.strpath,
            comment_chars=';', delimiter='|',
            secondary_delimiter=';', accumulate_values=True)
    assert data['key2'] == ['value2a', 'value2b', 'value2c']


def test_file_to_lookup_causes_warning(sample_lookup_file):
    '''Make sure that a call to file_to_lookup results in a DeprecationWarning.
    It should also still return the expected results.'''
    with pytest.warns(DeprecationWarning):
        data = file_to_lookup(sample_lookup_file.strpath)

    assert isinstance(data, dict)
    assert data['key1'] == 'value1'


def test_concatenate_singleton_files(singleton_xml_files, tmpdir_factory):
    directory = singleton_xml_files.strpath
    output_dir = tmpdir_factory.mktemp("tempoutput")
    concatenate_singleton_files(
        directory, output_dir.strpath,
        product="test", pattern="*.xml")
    assert len(os.listdir(output_dir.strpath)) == 1
    # expected = [i.readlines() for i in os.listdir(directory)]
    expected = []
    for i in os.listdir(directory):
        for line in open(os.path.join(directory, i)).readlines():
            expected.append(line)
    outfilename = os.listdir(output_dir.strpath)[0]
    result = open(os.path.join(output_dir, outfilename)).readlines()
    assert result == expected


def test_concatenate_singleton_files_gets_product(
        singleton_xml_files, tmpdir_factory):
    directory = singleton_xml_files.strpath
    output_dir = tmpdir_factory.mktemp("tempoutput")
    with pytest.raises(TypeError):
        concatenate_singleton_files(
            directory, output_dir.strpath, pattern="*.xml")


def test_can_parse_huge_tree(huge_tree_xml):
    assert parse_maybe_huge_xml(huge_tree_xml)


def test_cdata_retained_from_parse_maybe_huge_xml(cdata_xml):
    tree = parse_maybe_huge_xml(cdata_xml)
    text = tree.xpath('.//text')[0]
    assert et.tostring(text) == b'<text><![CDATA[Some text]]></text>'


def test_concatenate_singleton_files_handles_input_record_numbers(
        singleton_xml_files, tmpdir_factory):
    output_dir = tmpdir_factory.mktemp("tempoutput")
    directory = singleton_xml_files.strpath
    date = datetime.date.today().strftime('%Y%m%d')
    concatenate_singleton_files(
        directory, output_dir.strpath,
        pattern="*.xml", product="product", records=2)
    assert os.path.isfile(f'{output_dir}/CH_SS_product_{date}_000.xml')
    assert os.path.isfile(f'{output_dir}/CH_SS_product_{date}_001.xml')


def test_file_size(sample_lookup_file, mocker):
    """Make sure we correctly call os.stat"""
    # We don't need to test the return value, since we can be
    # fairly sure os.stat's behaviour is fully tested in the
    # python test suite.
    mocker.patch('os.stat')
    pqcoreutils.fileutils.file_size(sample_lookup_file.strpath)
    assert os.stat.called_once_with(sample_lookup_file.strpath)


def test_file_checksum_generates_md5(sample_lookup_file):
    """Ensure we get back the expected value for the file's
    checksum."""
    # Note: Here we *do* want to test returns, since we have
    # logic that needs to be tested to do the right thing (i.e.
    # specifying the hash algorithm to use, and digest style we
    # want)
    d = hashlib.new('md5')
    with open(sample_lookup_file.strpath, 'rb') as f:
        while True:
            buf = f.read(65536)
            if not buf:
                break
            d.update(buf)

    md5 = d.hexdigest()
    assert md5 == pqcoreutils.fileutils.file_checksum(
        sample_lookup_file)


def test_file_checksum_generates_sha256(sample_lookup_file):
    """User requests the sha256 checksum"""
    d = hashlib.new('sha256')
    with open(sample_lookup_file.strpath, 'rb') as f:
        while True:
            buf = f.read(65536)
            if not buf:
                break
            d.update(buf)

    sha256 = d.hexdigest()
    assert sha256 == pqcoreutils.fileutils.file_checksum(
        sample_lookup_file.strpath, algorithm='sha256')


def test_file_checksum_returns_plain_digest(sample_lookup_file):
    """The user asked the plain sha256 digest"""
    d = hashlib.new('sha256')
    with open(sample_lookup_file.strpath, 'rb') as f:
        while True:
            buf = f.read(65536)
            if not buf:
                break
            d.update(buf)

    sha256_digest = d.digest()
    assert sha256_digest == pqcoreutils.fileutils.file_checksum(
        sample_lookup_file.strpath, algorithm='sha256',
        hexdigest=False)
