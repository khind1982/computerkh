"""Miscellaneous functions that don't belong elsewhere"""
import functools
import sys
import warnings

from collections import namedtuple
from typing import Any, Callable

import lxml.etree as et
import tabulate as _tabulate

from colorama import Back
from colorama import Cursor
from colorama import Fore
from colorama import Style

from .meta import export as _export
from pqcoreutils import dateutils


def tabulate(tabular_data, *args, footer=None, **kwargs):
    table_data = _tabulate.tabulate(tabular_data, *args, **kwargs)
    if footer:
        table_data = f"{table_data}\n{footer}"
    return table_data


def deprecated(func):
    def wrap(*args, **kwargs):
        warnings.warn(
            f"""The function '{func.__name__}' has been moved to the module
            'dateutils'.  'misc.{func.__name__}' will be removed in a future release;
            please start using 'dateutils.{func.__name__}' instead.""",
            DeprecationWarning
        )
        return func(*args, **kwargs)
    return wrap


@deprecated
def interpolate_year(*args, **kwargs):
    return dateutils.interpolate_year(*args, **kwargs)


@deprecated
def current_year():
    return dateutils.current_year()


@deprecated
def today():  # pragma: no cover
    return dateutils.today()


season_to_month = {
    'Spring': 'April',
    'Summer': 'July',
    'Autumn': 'October',
    'Fall': 'October',
    'Winter': 'January',
    'hiver': 'January'}


@deprecated
def datetimeformat(*args, **kwargs):  # pragma: no cover
    return dateutils.datetimeformat(*args, **kwargs)


@deprecated
def date_object_from_patterns(date, patterns=None, languages=None):
    return dateutils.date_object_from_patterns(date, patterns, languages)


FieldHeaders = namedtuple('FieldHeaders', ['seen', 'done'])
FieldColours = namedtuple('FieldColours', ['seen', 'done', 'object'])

_default_field_headers = FieldHeaders(seen='Seen', done='Transformed')
_default_field_colours = FieldColours(seen=Fore.RED, done=Fore.GREEN, object=Fore.CYAN)

ProgressStatus = namedtuple('ProgressStatus', ['seen', 'done', 'object'])


@_export
class ProgressIndicator:
    '''A simple (i.e. simplistic) progress indicator.
    The user can specify labels to use in the output, and colours for text, by
    passing in instances of FieldHeaders and FieldColours respectively. By default,
    headers are "Seen" printed in red, and "Transformed" printed in green, with the
    current object ID printed in cyan inside parentheses.

    If :null: is True, any subsequent call to the instance will be silently ignored.
    This is useful if you want to provide a user-definable switch to enable/disable
    progress tracking. It is as simple as passing in the appropriate value, and there
    is no need for any extra logic in your own code.

    If :flush: is True, each time the instance is called, python will flush the
    stderr stream. This will cause every update to be printed to the terminal as it
    is executed, and will slow your code down a little. If :flush: is False, the
    default, this will not happen, and python will flush stderr only when the buffer
    is full. This will lead to what might look like incomplete or intermittent updates
    to the status indicator, but it should still be sufficient to convince most users
    that something is still happening.

    The easiest way to specify colours is probably to use the colorama package,
    which allows things like "colorama.Fore.RED + colorama.Back.YELLOW" These get
    expanded to the appropriate ANSI escape sequences, which can also be used to
    configure a ProgressIndicator instance.

    Once you have an instance, call it with an instance of the ProgressStatus
    namedtuple, or None to indicate the end of the run, and to reset terminal
    colours and styles.'''

    def __new__(cls, null=False, **kwargs):
        if null:
            def null_update(*_args):
                pass
            return null_update
        return object.__new__(cls)

    def __init__(self, **kwargs):
        self.fields = kwargs.get('headers', _default_field_headers)
        self.colours = kwargs.get('colours', _default_field_colours)
        self.flush = kwargs.get('flush', False)

    def __call__(self, progress=None):
        RESET_EVERYTHING = Fore.RESET + Back.RESET + Style.RESET_ALL
        if progress:
            seen = f'{self.colours.seen}{self.fields.seen}{Fore.RESET}: {progress.seen}'
            done = f'{self.colours.done}{self.fields.done}{Fore.RESET}: {progress.done}'
            cur_obj = f'({self.colours.object}{progress.object}{Fore.RESET})'
            trail = Cursor.BACK(1000) + RESET_EVERYTHING
            sys.stderr.buffer.write(
                bytes(
                    '{seen} {done} {cur_obj} {trail}'.format(
                        seen=seen, done=done, cur_obj=cur_obj, trail=trail), 'utf-8'))
        else:
            print(RESET_EVERYTHING + Cursor.BACK(1000) + '\n', file=sys.stderr)

        if self.flush:  # pragma: no cover
            sys.stderr.flush()


@_export
def releasing_iterparse(file_or_filelike, *args, **kwargs):
    '''A memory-efficient version of iterparse. It releases each element
    as it goes out of scope, so the document doesn't continually grow
    during the iteration.'''
    for event, element in et.iterparse(file_or_filelike, *args, **kwargs):
        yield (event, element)

        element.clear()

        for ancestor in element.xpath('ancestor-or-self::*'):
            while ancestor.getprevious() is not None:
                del ancestor.getparent()[0]


# Attach releasing_iterparse to lxml.etree
et.releasing_iterparse = releasing_iterparse


def fn_pipeline(*functions: Callable[[Any], Any]) -> Callable[[Any], Any]:
    '''Turns arbitrary multiple unary functions into a single pipelined
    function. Can help avoid nested function applications or multiple
    steps with intermediate variables. Functions with an arity of 2 or
    higher must be converted to instances of functools.partial in order
    to play nicely with this implementation.'''
    return functools.reduce(lambda f, g: lambda x: g(f(x)), functions)
