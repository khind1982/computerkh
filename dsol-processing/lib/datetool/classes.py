# -*- mode: python; coding: utf-8 -*-
# pylint: disable = missing-docstring

"""
Classes used by the lex/yacc date parsing library
"""

import roman

import datetool.patterns as patterns

# Raised by the normalised_alnum_value method on Day if there is no
# need to output the day in a normalised date.
class NoAlnumRepr(Exception): pass

class DateRange(object): # pylint: disable = R0903
    def __init__(self, start_date, end_date=None):
        self.start_date = start_date
        self.end_date = end_date

class Date(object):
    def __init__(self, *components):
        for component in components:
            setattr(self, component.__class__.__name__.lower(), component)

        if hasattr(self, 'special'):
            # pylint: disable = E1101
            self.day = self.special.day
            self.month = self.special.month
        if not hasattr(self, 'day'):
            self.day = Day('1', num_only=True)
        if not hasattr(self, 'season') and not hasattr(self, 'month'):
            self.month = Month('JAN', 'Jan')  #, num_only=True)

    @property
    def normalised_numeric_date(self):
        return "%s%s%s" % (
            getattr(self, 'year').normalised_numeric_value,
            self.month_or_season().normalised_numeric_value,
            getattr(self, 'day').normalised_numeric_value
        )

    @property
    def normalised_alnum_date(self):
        try:
            return "%s %s, %s" % (
                self.month_or_season().normalised_alnum_value,
                getattr(self, 'day').normalised_alnum_value,
                getattr(self, 'year').normalised_alnum_value,
            )
        except NoAlnumRepr:
            return "%s %s" % (
                self.month_or_season().normalised_alnum_value,
                getattr(self, 'year').normalised_alnum_value
            )

    def month_or_season(self):
        try:
            return getattr(self, 'month')
        except AttributeError:
            return getattr(self, 'season')

class Day(object):
    def __init__(self, value, ordinal=None, num_only=False):
        try:
            # Try to convert `value' from Roman. If this fails, it's Arabic. Probably.
            self.value = str(roman.fromRoman(value.upper()))
        except roman.InvalidRomanNumeralError:
            self.value = value
        self.num_only = num_only
        if ordinal is None:
            self.ordinal = None
        else:
            # Convert ordinal to lower case so capitals don't cause problems.
            ordinal = ordinal.lower()
            if self.validate_day_and_ordinal(ordinal):
                self.ordinal = ordinal
            else:
                raise ValueError("Inappropriate suffix %s for %s" % (
                    ordinal, self.value
                ))

    @property
    def normalised_alnum_value(self):
        if self.num_only is False:
            return str(int(self.value))
        else:
            raise NoAlnumRepr

    @property
    def normalised_numeric_value(self):
        return self.value.zfill(2)

    def validate_day_and_ordinal(self, ordinal):
        # Check that the combination of number and ordinal suffix are valid
        # Applies only to English dates for now.
        if self.value in ['11', '12', '13']:
            if ordinal == "th":
                return True
        elif self.value.endswith('1') and ordinal == 'st':
            return True
        elif self.value.endswith('2') and ordinal == 'nd':
            return True
        elif self.value.endswith('3') and ordinal == 'rd':
            return True
        elif self.value[-1] in '4567890' and ordinal == 'th':
            return True
        else:
            return False

class Special(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value
        # Translate special dates to normalised values
        month = patterns.specials[name][1]
        self.month = Month(month.upper(), month)
        self.day = Day(patterns.specials[name][2])

    @property
    def normalised_alnum_value(self):
        return "%s %s" % (self.month.normalised_alnum_value,
                          self.day.normalised_alnum_value)

    @property
    def normalised_numeric_value(self):
        return "%s%s" % (self.month.normalised_numeric_value,
                         self.day.normalised_numeric_value)

class Season(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value
        # The patterns OrderedDict values are tuples, where the second element
        # is the three-letter month name for the normalised date.
        self.start_month = patterns.seasons[name][1]
        self.start_date = '01'

    @property
    def number(self):
        return patterns.season_names.index(self.name) + 21

    @property
    def normalised_alnum_value(self):
        return self.start_month

    @property
    def normalised_numeric_value(self):
        # Ask an instance of Month for the current value of self.month what
        # its normalised numeric value is.
        return Month(
            self.start_month.upper(),
            self.start_month).normalised_numeric_value

class Month(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return self.normalised_alnum_value

    @property
    def long_name(self):
        return self.value

    @property
    def number(self):
        return patterns.month_names.index(self.name) + 1

    @property
    def normalised_alnum_value(self):
        return self.name.capitalize()

    @property
    def normalised_numeric_value(self):
        return str(self.number).zfill(2)

class Year(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    @property
    def normalised_numeric_value(self):
        return self.value

    @property
    def normalised_alnum_value(self):
        return str(self.normalised_numeric_value)

class Wday(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return self.value

    @property
    def normalised_numeric_value(self):
        return

    @property
    def normalised_alnum_value(self):
        return
