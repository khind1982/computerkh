# -*- mode: python; coding: utf-8 -*-
# pylint: disable = C0103, C0111, C0326

import os
import re
import sys

import ply.lex as lex
import ply.yacc as yacc

import datetool.patterns as patterns

# pylint: disable = W0611
from datetool.classes import DateRange, Date, Year, Month, Season, Day, Special, Wday

class ParserError(Exception):
    def __init__(self, message, lexer): # pylint: disable = W0621
        super(self.__class__, self).__init__()
        self.message = message
        self.lexer = lexer
        
    def __str__(self):
        return repr(self.message)

####
#### lex configuration starts here
####

tokens = patterns.wday_names + patterns.month_names + patterns.season_names + patterns.specials_names + [
    'EDGNUMBER', 'FDGNUMBER', 'NUMBER', 'ORD',
    'SLASH', 'HYPHEN', 'COMMA',
    'COLON', 'AMP', 'TO', 'ROMAN', 'AND'
]

# Define the functions that represent the month, season and special
# tokens.  The regexps are loaded from the module <patterns> and
# attached explicitly as the closure's __doc__ attribute.

def define_token_funcs():
    for name in ['wdays', 'months', 'seasons', 'specials']:
        for token in getattr(patterns, name):
            def define_token_func(token, name):
                klass = globals()[name.capitalize()[:-1]]
                def _func(t):
                    t.value = klass(token, t.value)
                    return t
                docstr = getattr(patterns, name)[token]
                if isinstance(docstr, tuple):
                    _func.__doc__ = docstr[0]
                else:
                    _func.__doc__ = docstr
                globals()['t_%s' % token] = _func
            define_token_func(token, name)
define_token_funcs()

t_EDGNUMBER = r'\d\d\d\d\d\d\d\d'
t_FDGNUMBER = r'\d\d\d\d'
t_NUMBER = r'\d\d?'
t_ORD    = r'(st|nd|rd|th)'
t_SLASH  = r'/'
t_HYPHEN = r'--?'
t_AND = r'and'
t_COMMA  = r','
#t_PERIOD = r'\.'
t_AMP = r'&(amp;)?'
t_COLON  = r':'
t_TO = 'to'
t_ROMAN = r'[IVXLCDMivxlcdm]+'
t_ignore = ' \t.*'

def t_error(t):
    raise ValueError("Illegal token '%s'" % t.value)

lexer = lex.lex(reflags=re.IGNORECASE, debug=0)

####
#### yacc configuration starts here
####

#### Note on dates in format Month Day - Month Day Year - Year; new function
#### will need to be constructed, with different p structure; p corresponds to
#### the parts of the docstring text on the other side of the colon

def p_datestring(p):
    """
    datestring : date
               | date end_date
               | date date
    """
    if len(p) == 2:
        p[0] = DateRange(p[1])
    elif len(p) == 3:
        p[0] = DateRange(p[1], p[2])

def p_end_date(p):
    """
    end_date : COLON date
             | HYPHEN date
             | SLASH date
             | TO date
    """
    p[0] = p[2]

def p_day_month(p):
    """
    day_month : day_comma month_comma
              | day_range month_comma
              | day_comma month sep day_comma month
    """
    p[0] = (p[1], p[2])

def p_day_sep_month(p):
    """
    day_sep_month : day_comma sep month_comma
    """
    p[0] = (p[1], p[3])

def p_month_day(p):
    """
    month_day : month_comma day sep month_comma day_comma
              | month_comma day_range
              | month_comma day_comma
              | month_range day_comma
    """
    p[0] = (p[2], p[1])

def p_wday_month_day(p):
    """
    wday_month_day : wday_comma month_comma day_comma
    """
    p[0] = (p[3], p[2])

def p_month_sep_day(p):
    """
    month_sep_day : month_comma sep day_comma
    """
    p[0] = (p[3], p[1])


def p_sep(_):
    """
    sep : HYPHEN
        | COMMA HYPHEN
        | SLASH
        | AMP
        | AND
    """
    pass

def p_wday(p):
    """
    wday : SUN
         | MON
         | TUE
         | WED
         | THU
         | FRI
         | SAT
    """
    p[0] = p[1]

def p_wday_comma(p):
    """
    wday_comma : wday
               | wday COMMA
    """
    p[0] = p[1]

def p_month_comma(p):
    """
    month_comma : month
                | month COMMA
    """
    p[0] = p[1]

def p_month_dash(p):
    """
    month_dash : month HYPHEN
    """
    p[0] = p[1]
    
def p_month(p):
    """
    month : JAN
          | FEB
          | MAR
          | APR
          | MAY
          | JUN
          | JUL
          | AUG
          | SEP
          | OCT
          | NOV
          | DEC
    """
    p[0] = p[1]

def p_season(p):
    """
    season : SPRING
           | SUMMER
           | AUTUMN
           | WINTER
    """
    p[0] = p[1]

def p_season_comma(p):
    """
    season_comma : season
                 | season COMMA
    """
    p[0] = p[1]

def p_special_comma(p):
    """
    special_comma : special
                  | special COMMA
    """
    p[0] = p[1]

def p_special(p):
    """
    special : ANNUAL
            | CHRISTMAS
    """
    p[0] = p[1]

# Modified from month day_range month

def p_md_sep_dm_range(p):
    """
    md_sep_dm_range : month_day month
    """
    p[0] = p[1]

def p_date(p):
    """
    date : year
         | month_range year
         | month_range SLASH year
         | month SLASH year
         | month_dash year
         | month_comma year
         | day_month year
         | month_day year
         | wday_month_day year
         | md_sep_dm_range year
         | day_sep_month sep_year
         | month_sep_day sep_year
         | season_range year
         | season_comma year
         | special_comma year
         | numeric_date
    """
    if len(p) == 2:  # year only/numeric_date
        if isinstance(p[1], tuple): # numeric_date
            p[0] = Date(p[1][0], p[1][1], p[1][2])
        else:
            p[0] = Date(p[1])
    elif len(p) == 3:
        if isinstance(p[1], tuple): # day_month/month_day
            p[0] = Date(p[1][0], p[1][1], p[2])
        else:
            p[0] = Date(p[1], p[2])
    elif len(p) == 4:
        if p[2] is '/':  # Dates like "March/April/2001"
            p[0] = Date(p[1], p[3])

def p_day_comma(p):
    """
    day_comma : day
              | day COMMA
    """
    p[0] = p[1]

def p_day_range(p):
    """
    day_range : day HYPHEN day_comma
              | day SLASH day_comma
              | day SLASH day SLASH day_comma
              | day AMP day_comma
    """
    p[0] = p[1]

def p_day(p):
    """
    day : NUMBER
        | NUMBER ORD
        | ROMAN
    """
    if len(p[1]) > 2:
        raise ValueError("Invalid value '%r'" % p[1])
    elif len(p) == 3:
        p[0] = Day(p[1], p[2])
    else:
        p[0] = Day(p[1])

def p_sep_year(p):
    """
    sep_year : sep year
    """
    p[0] = p[2]

def p_year(p):
    """
    year : FDGNUMBER
    """
    p[0] = Year(p[1])

def p_numeric_date(p):
    """
    numeric_date : EDGNUMBER
    """
    m = patterns.month_names[int(p[1][4:6])-1]
    p[0] = (Year(p[1][0:4]), Month(m.upper(), m), Day(p[1][6:8]))

def p_month_range(p):
    """
    month_range : month_comma sep month_comma sep month_comma
                | month_comma sep month_comma day_comma
                | month_comma sep month_comma
                | month_dash month_comma
                | month_dash month_dash month
                | month SLASH month SLASH month_comma
                | month SLASH month_comma
    """
    p[0] = p[1]

def p_season_range(p):
    """
    season_range : season_comma sep season_comma
    """
    p[0] = p[1]

def p_error(p):
    raise ParserError("Unrecognised date format: %s" % p.lexer.lexdata, p.lexer)
    # raise ParserError("Syntax error in parser input '%s'" % repr(p), p.lexer)

parser = yacc.yacc(outputdir=os.path.dirname(__file__), debug=0,
                   write_tables=0)

if __name__ == '__main__':
    infile = sys.argv[1]
    dates = []

    with open(infile) as inf:
        for line in inf.readlines():
            dates.append(line.strip())

    for l, date in enumerate(dates, 1):
        try:
            r = parser.parse(date)
        except ValueError as e:
            print "%s: %s in '%s'" % (l, e.message, date)
            exit()
        except AttributeError as e:
            print e.message
            print "from input '%s' at line %s" % (date, l)
            exit()
        print "%s: \t %s \t %s \t %s" % (
            l, date,
            r.start_date.normalised_alnum_date,
            r.start_date.normalised_numeric_date)
