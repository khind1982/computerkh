"""Tests for the miscellaneous module."""

import pytest
import datetime

from io import BytesIO

import colorama
import lxml.etree as et
import tabulate

import pqcoreutils
import pqcoreutils.misc


# def test_tabulate_without_footer(capsys):
def test_tabulate_without_footer():
    """Make sure the output from misc.tabulate mathces what we'd get
    from tabulate.tabulate."""
    data = [['a', 'b', 'c'], ['x', 'y', 'z']]
    misc_tab = pqcoreutils.misc.tabulate(data)
    std_tab = tabulate.tabulate(data)
    assert misc_tab == std_tab


def test_tabulate_footer(capsys):
    """We wrap tabulate to enable printing of a footer line."""
    data = [['a', 'b', 'c'], ['x', 'y', 'z']]
    table = pqcoreutils.misc.tabulate(data, footer="Footer Text")
    assert "Footer Text" in table


def test_interpolate_year_causes_warning():
    '''Make sure that a call to interpolate_year results in a DeprecationWarning.
    It should also still return the expected results.'''
    with pytest.warns(DeprecationWarning):
        year = pqcoreutils.misc.current_year()
        result = pqcoreutils.misc.interpolate_year("test text <CURYEAR>")

    assert f"test text {year}" == result


def test_today_causes_warning():
    '''Make sure that a call to the today() method results in a DeprecationWarning.
    It should also return the expected results.'''
    with pytest.warns(DeprecationWarning):
        result = pqcoreutils.misc.today()
    assert result == datetime.datetime.today().strftime("%Y%m%d")


def test_date_object_from_patterns_causes_warning():
    '''Make sure that a call to the today() method results in a DeprecationWarning.
    It should also return the expected results.'''
    with pytest.warns(DeprecationWarning):
        result = pqcoreutils.misc.date_object_from_patterns(
            '1 November 2021', patterns=['%d %B %Y'])
        month, year, day = (11, 2021, 1)
        assert result.month == month
        assert result.year == year
        assert result.day == day


@pytest.mark.xfail
def test_datetimeformat_raises_warning():
    with pytest.raises(DeprecationWarning):
        date = pqcoreutils.misc.datetimeformat.strptime('2010', '%Y')
        assert date.pattern == '%Y'


# ProgressIndicator - print a simple running summary of work.
# Initialise with labels for the values. Defaults are "Seen" and
# "Transformed". If used to summarise something other than a
# transformation, you can specify the labels when creating the
# object.
def test_progress_indicator_with_default_labels(capsys):
    pi = pqcoreutils.misc.ProgressIndicator()
    assert pi.fields.seen == 'Seen'
    assert pi.fields.done == 'Transformed'
    assert pi.colours.seen == colorama.Fore.RED
    status = pqcoreutils.misc.ProgressStatus(1, 1, 'testdoc')
    pi(status)
    output = capsys.readouterr()
    assert colorama.Fore.RED + 'Seen' in output.err
    assert colorama.Fore.GREEN + 'Transformed' in output.err
    assert colorama.Fore.CYAN + 'testdoc' in output.err


def test_progress_indicator_with_user_labels_and_colours(capsys):
    '''Check that user-supplied labels and colours appear in the output'''
    fh = pqcoreutils.misc.FieldHeaders(seen='Count', done='Finished')
    fc = pqcoreutils.misc.FieldColours(
        seen=colorama.Fore.GREEN,
        done=colorama.Fore.YELLOW + colorama.Back.GREEN,
        object=colorama.Fore.MAGENTA)
    pi = pqcoreutils.misc.ProgressIndicator(headers=fh, colours=fc)
    assert pi.fields.seen == 'Count'
    assert pi.fields.done == 'Finished'

    assert pi.colours.seen == colorama.Fore.GREEN
    assert pi.colours.done == colorama.Fore.YELLOW + colorama.Back.GREEN
    assert pi.colours.object == colorama.Fore.MAGENTA

    status = pqcoreutils.misc.ProgressStatus(1, 2, 'testdoc')
    pi(status)
    output = capsys.readouterr()
    assert colorama.Fore.GREEN + 'Count' in output.err
    assert colorama.Fore.YELLOW + colorama.Back.GREEN + 'Finished' in output.err
    assert colorama.Fore.MAGENTA + 'testdoc' in output.err


def test_progress_indicator_terminate_report(capsys):
    '''The user should should call the progress indicator with None to correctly
    reset the terminal colours and line printing.'''
    pi = pqcoreutils.misc.ProgressIndicator()
    pi(progress=None)
    output = capsys.readouterr()
    assert colorama.Cursor.BACK(1000) in output.err


def test_null_progress_indicator(capsys):
    '''If the progress indicator is instantiated with null=True, calling it should
    be a no-op.'''
    pi = pqcoreutils.misc.ProgressIndicator(null=True, flush=True)
    status = pqcoreutils.misc.ProgressStatus(1, 2, 'testdoc')
    pi(status)
    output = capsys.readouterr()
    assert output.err == ''


def test_progress_inidicator_explicitly_not_null(capsys):
    '''Make sure the ProgressIndicator can tolerate being called with an
    explicit False value for null.'''
    assert pqcoreutils.misc.ProgressIndicator(null=False, flush=False)


@pytest.fixture
def sample_xml():
    xml_text = '''<root>
    <record><id>1</id></record>
    <record><id>2</id></record>
    <record><id>3</id></record>
    <record><id>4</id></record>
    <record><id>5</id></record>
    <record><id>6</id></record>
    <record><id>7</id></record>
    <record><id>8</id></record>
    <record><id>9</id></record>
    <record><id>10</id></record>
    <record><id>11</id></record>
    <record><id>12</id></record>
    <record><id>13</id></record>
    <record><id>14</id></record>
    <record><id>15</id></record>
    </root>'''
    return BytesIO(bytes(xml_text, encoding='utf-8'))


def test_releasing_iterparse(sample_xml):
    '''releasing_iterparse avoids potential pitfalls of using iterparse in
    lxml.etree, which incrementally builds the document in memory, one
    matching tag at a time. This has its advantages (e.g. any given matching
    tag knows about its place in the document, if that's important), but it
    also means the memory used during the iteration will grow throughout the
    execution. This implementation releases all but the closest preceding
    siblings of the matching tag, so we only ever have the current node
    and the handful that iterparse seems to preload as an optimisation.'''
    for _event, elem in pqcoreutils.misc.releasing_iterparse(
            sample_xml, tag='record'):
        assert elem.tag == 'record'

        # We should only ever have, at most, one preceding sibling in the
        # yielded fragment.
        assert len(elem.xpath('preceding-sibling::*')) <= 1


def test_releasing_iterparse_available_through_lxml_etree():
    '''Make sure the releasing_iterparse function is attached to the
    lxml.etree module for a minimally astonishing developer experience.'''
    assert hasattr(et, 'releasing_iterparse')
    assert et.releasing_iterparse is pqcoreutils.misc.releasing_iterparse
    import lxml.etree
    assert hasattr(lxml.etree, 'releasing_iterparse')


def test_fn_pipeline():
    '''fn_pipeline is a way of construcing a pipeline of unary functions.
    It can be used to simplify multiple function applications on the same
    object by freeing the programmer from having to work inside out.'''
    def add_two(n):
        return n + 2

    def times_three(n):
        return n * 3

    n = 2

    assert pqcoreutils.misc.fn_pipeline(
        add_two,
        add_two,
        times_three
    )(n) == times_three(add_two(add_two(n)))
