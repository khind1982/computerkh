# -*- mode: python -*-

import os, sys, re
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'lib', 'python'))

sys.path.append('/packages/dsol/lib/python')

from cstoreerrors import IncompleteTextualDateError
from cstoreerrors import UnhandledDateFormatException
from time import localtime, strftime
import DateConverter #pylint:disable=F0401

DAYS = {1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
        7: 'Sunday'
        }

MONTHS = {1: 'January',
          2: 'February',
          3: 'March',
          4: 'April',
          5: 'May',
          6: 'June',
          7: 'July',
          8: 'August',
          9: 'September',
          10: 'October',
          11: 'November',
          12: 'December'
          }

def fourteenDigitDate(date=None):
    if date == None:
        date = localtime()
    return strftime("%Y%m%d%H%M%S", date)

def today(asInteger=False):
    _today = strftime("%Y%m%d", localtime())
    if asInteger:
        return int(_today)
    else:
        return _today

def numeric_to_alpha_date(datestring):
    return DateConverter.USdate2pqan(datestring)

def today_pqan(noday=False):
    date = localtime()
    return DateConverter.EUdate2pqan(strftime("%Y%d%m", date))

# def XnormaliseDate(datestring):
#     if re.search('^' + _months, datestring):
#         #print "MONTHS"
#         return normaliseMonthsFirst(datestring)
#     elif re.search('^' + _seasons, datestring):
#         #print "SEASONS"
#         return normaliseSeasonsFirst(datestring)
#     else:
#         return "normaliseDate dispatcher: FIXTHIS " + datestring


# def normaliseSeasonsFirst(datestring):
#     if re.search(r'^' + _seasons + ' ' + _year + '$', datestring):
#         return DateConverter.conv_season2pqan(datestring)
#     elif re.search(r'^' + _seasons + '[/-]' + _seasons + ' ' + _year + '$', datestring):
#         return datestring
#     else:
#         return "normaliseSeasonsFirst dispatcher: FIXTHIS " + datestring


_days = r'\d{1,2}'
_months = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*[,.]?'
_seasons = u'(?:Spr(?:ing)?|Sum(?:mer)?|Autumn|Fall?|Win(?:ter)?)'
_year = r'\d{4}'
_quarters = u'(?:First|Second|Third|Fourth)(?: Quarter)?'

def _setregexes():
    return [
        r'\d{1,2}',
        r'(?i)(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|AUG)\w*[,.]?',
        u'(?:Spr(?:ing)?|Sum(?:mer)?|Autumn|Fall?|Win(?:ter)?)',
        r'\d{4}',
        u'(?:First|Second|Third|Fourth)(?: Quarter)?'
        ]

def normaliseDate(datestring):
    day, months, seasons, year, quarters = _setregexes()
    datestring = datestring.replace('Jaunuary', 'January') # Speeling mistaek in IIMP...
    if datestring == "n.d.":
        return u"Jan 1, 1"
    elif re.search(r'^' + year + '-' + year + ' Nueva .*$', datestring):
        return re.search(r'^(' + year + ').*$', datestring).group(1)
    ###1972/3
    ###1933:abr.
    ###1980:1er TRIMESTRE
    ###1982:III TRIMESTRE
    ###1982:IV TRIMESTRE
    ###1989:New Year
    ###1940:Lent Term
    ###1940:Summer Term
    ###1947:Christmas
    ###1940:Christmas Term
    ###1941:Lent Term
    ###1941:Summer and Christmas Term
    ###1942:Lent and Summer Term
    ###1948:Easter Term
    ###1978:Late Fall
    ###1969:Early Spring
    ###1969:Late Spring
    ###1969:Late Summer
    ###1983:winter
    ###1940:Christmas
    ###1972:1 er semestre
    ###1972:2  semestre
    ###1907:PRIMER TRIMESTRE
    ###1907:SEGUNDO TRIMESTRE
    ###1907:TERCER TRIMESTRE
    ###1907:CUARTO TRIMESTRE
    ###1917:SEGUNDO TRIMESTRE/TERCER TRIMESTRE
    ###1964:4 trimestre-1965:1er trimestre
    ###1968:3 trimestre/4{}me trimestre
    ###1981:Early Winter
    ###1982:Late Winter
    ###1977:Mar. sic
    ###1989:Fall Preview
    ###1881:JULHO
    ###1881:AGOSTO
    ###1881:SETEMBRO
    ###1881:OUTUBRO
    ###1859:dec.
    ###1860:janv.
    ###1860:fevr.
    ###1945:Special
    ###1958:Midsummer
    ###1959:Easter
    ###1960:Christmas
    ###1987:SPECIAL ANNIVERSARY ISSUE
    ###1965:4{}me trimestre
    ###1966:1er trimestre
    ###1977:Michaelmas Term
    ###1980:enero/abr.-urtarrilla/apirila
    elif re.search(r'^n\.d\.[- ]' + year + '$', datestring):
        return re.search(r'^n\.d\.[- ](' + year + ')$', datestring).group(1)
    elif re.search(r'^n\.d\.[- ]\(' + year + r'\)$', datestring):
        return re.search(r'^n\.d\.[- ]\((' + year + r')\)$', datestring).group(1)
    elif re.search(r'^' + months + r' \[' + year + r'\]$', datestring):
        m, y = re.search(r'^(' + months + r') \[(' + year + r')\]$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    ###1923:Dec.
    elif re.search(r'^' + year + ':' + months + '$', datestring):
        y, m = re.search(r'^(' + year + '):(' + months + ')$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    ###1964/1965:August
    elif re.search(r'^' + year + '/' + year + ':' + months + '$', datestring):
        y, m = re.search(r'^(' + year + ')/' + year + ':(' + months + ')$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    ###1929/1930:Nov./Dec./Jan.
    elif re.search(r'^' + year + '/' + year + ':' + months + '/' + months + '/' + months + '$', datestring):
        y, m = re.search(r'^(' + year + ')/' + year + ':(' + months + ')/' + months + '/' + months + '$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    ###1915/1916:Sept./Dec.-Sept./Dec.
    elif re.search(r'^' + year + '/' + year + ':' + months + '/' + months + '-' + months + '/' + months + '$', datestring):
        y, m = re.search(r'^(' + year + ')/' + year + ':(' + months + ')/' + months + '-' + months + '/' + months + '$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    ###1909:Dec. 17
    elif re.search(r'^' + year + ':' + months + ' ' + day + '$', datestring):
        y, m, d = re.search(r'^(' + year + '):(' + months + ') (' + day + ')$', datestring).group(1, 2, 3)
        return DateConverter.conv_dmy_pqan(d + ' ' + m + ' ' + y)
    ###1976:June/Dec.
    elif re.search(r'^' + year + ':' + months + '/' + months + '$', datestring):
        y, m = re.search(r'^(' + year + '):(' + months + ')/' + months + '$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    ###1926:Aug./Sept./Oct.
    elif re.search(r'^' + year + ':' + months + '/' + months + '/' + months + '$', datestring):
        y, m = re.search(r'^(' + year + '):(' + months + ')/' + months + '/' + months + '$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    ###1987:July/Aug./Sept./Oct.
    elif re.search(r'^' + year + ':' + months + '/' + months + '/' + months + '/' + months + '$', datestring):
        y, m = re.search(r'^(' + year + '):(' + months + ')/' + months + '/' + months + '/' + months + '$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    ###1995:Sept.-Dec./Sept.-Dec.
    elif re.search(r'^' + year + ':' + months + '-' + months + '/' + months + '-' + months + '$', datestring):
        y, m = re.search(r'^(' + year + '):(' + months + ')-' + months + '/' + months + '-' + months + '$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    ###1980:January/April.-January/February
    elif re.search(r'^' + year + ':' + months + '/' + months + '-' + months + '/' + months + '$', datestring):
        y, m = re.search(r'^(' + year + '):(' + months + ')/' + months + '-' + months + '/' + months + '$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    ###1951:July/Oct.-1952:Jan./Apr.
    elif re.search(r'^' + year + ':' + months + '/' + months + '-' + year + ':' + months + '/' + months + '$', datestring):
        y, m = re.search(r'^(' + year + '):(' + months + ')/' + months + '-' + year + ':' + months + '/' + months + '$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    ###1978:Dec. 20/27
    elif re.search(r'^' + year + ':' + months + ' ' + day + '/' + day + '$', datestring):
        y, m, d = re.search(r'^(' + year + '):(' + months + ') (' + day + ')/' + day + '$', datestring).group(1, 2, 3)
        return DateConverter.conv_dmy_pqan(d + ' ' + m + ' ' + y)
    ###1990:Nov. 28/Dec. 4
    elif re.search(r'^' + year + ':' + months + ' ' + day + '/' + months + ' ' + day + '$', datestring):
        y, m, d = re.search(r'^(' + year + '):(' + months + ') (' + day + ')/' + months + ' ' + day + '$', datestring).group(1, 2, 3)
        return DateConverter.conv_dmy_pqan(d + ' ' + m + ' ' + y)
    ###1863:Nov. 20-1864:Nov. 11
    elif re.search(r'^' + year + ':' + months + ' ' + day + '-' + year + ':' + months + ' ' + day + '$', datestring):
        y, m, d = re.search(r'^(' + year + '):(' + months + ') (' + day + ')-' + year + ':' + months + ' ' + day + '$', datestring).group(1, 2, 3)
        return DateConverter.conv_dmy_pqan(d + ' ' + m + ' ' + y)
    ###1977:Aug./Sept. 27/3
    elif re.search(r'^' + year + ':' + months + '/' + months + ' ' + day + '/' + day + '$', datestring):
        y, m, d = re.search(r'^(' + year + '):(' + months + ')/' + months + ' (' + day + ')/' + day + '$', datestring).group(1, 2, 3)
        return DateConverter.conv_dmy_pqan(d + ' ' + m + ' ' + y)
    ###1938:Dec.-1939:Jan.
    elif re.search(r'^' + year + ':' + months + '-' + year + ':' + months + '$', datestring):
        y, m = re.search(r'^(' + year + '):(' + months + ')-' + year + ':' + months + '$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    ###1994:Dec.-1995:Jan. 31/7
    elif re.search(r'^' + year + ':' + months + '-' + year + ':' + months + ' ' + day + '/' + day + '$', datestring):
        y, m, d = re.search(r'^(' + year + '):(' + months + ')-' + year + ':' + months + ' (' + day + ')/' + day + '$', datestring).group(1, 2, 3)
        return DateConverter.conv_dmy_pqan(d + ' ' + m + ' ' + y)
    ###1926:Nov./Dec.-1927:Jan.
    elif re.search(r'^' + year + ':' + months + '/' + months + '-' + year + ':' + months + '$', datestring):
        y, m = re.search(r'^(' + year + '):(' + months + ')/' + months + '-' + year + ':' + months + '$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    elif re.search(r'^' + day + '-' + day + ' ' + months + ' ' + year + '$', datestring):
        day, rest = re.search(r'^(' + day + ')-' + day + ' (' + months + ' ' + year + ')$', datestring).group(1, 2)
        return DateConverter.conv_dmy_pqan(day + ' ' + rest)
    elif re.search(r'^' + day + ' ' + months + '-' + day + ' ' + months + ' ' + year + '$', datestring):
        pre, post = re.search(r'(^' + day + ' ' + months + '-)(' + day + ' ' + months + ' ' + year + '$)', datestring).group(1, 2)
        pre = re.sub(r'^(\d{1,2}) (.*)-', r'\2 \1-', pre)
        return pre + DateConverter.conv_dmy_pqan(post)
    elif re.search(r'^' + day + ' ' + months + ' ' + year + '-' + day + ' ' + months + ' ' + year, datestring):
        date1, date2 = datestring.split('-')
        return DateConverter.conv_dmy_pqan(date1) + '-' + DateConverter.conv_dmy_pqan(date2)
    elif re.search(r'^' + day + ' ' + months + ' ' + year + '/' + day + ' ' + months + ' ' + year + '$', datestring):
        date1, date2 = datestring.split('/')
        return DateConverter.conv_dmy_pqan(date1) + '/' + DateConverter.conv_dmy_pqan(date2)
    elif re.search(r'^(?P<datestr>' + day + ' ' + months + ' ' + year + ')|(?P=datestr)$', datestring):
        return DateConverter.conv_dmy_pqan(datestring.split('|', 1)[0])
    elif re.search(r'^' + months + ' *' + year + '$', datestring):
        m, y = re.search('^(' + months + ') *(' + year + ')', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    elif re.search(r'^' + months + ' ' + year + '[/-]' + year + '$', datestring):
        m, y = re.search(r'^(' + months + ') (' + year + ')[/-]' + year +'$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    elif re.search(r'^' + months + ' ?-' + months + ' ?' + year, datestring):
        m, y = re.search('^(' + months + ').*(' + year + ')$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    elif re.search(r'^' + seasons + ' ' + year + '$', datestring):
        return DateConverter.conv_season2pqan(datestring)
    # Spring [1966] -> Spring 1966
    elif re.search(r'^' + seasons + ' \[' + year +'\]$', datestring):
        return re.sub(r'(\[|\])', '', datestring)
    elif re.search(r'^' + seasons + '[/-]' + seasons + ' ' + year + '$', datestring):
        return datestring
    elif re.search(r'^' + seasons + ' ' + year + '[/-]' + seasons + ' ' + year + '$', datestring):
        s, y = re.search(r'^(' + seasons + ') (' + year + ')[/-]' + seasons + ' ' + year + '$', datestring).group(1, 2)
        return DateConverter.conv_season2pqan(s + ' ' + y)
    elif re.search(r'^' + seasons + '-' + year + ':' + seasons + ' ' + year + '$', datestring):
        s, y = re.search(r'^(' + seasons + ')-.*(' + year + ')$', datestring).group(1, 2)
        return DateConverter.conv_season2pqan(s + ' ' + y)
    ###1976:Autumn-1977:Winter
    elif re.search(r'^' + year + ':' + seasons + '-' + year + ':' + seasons + '$', datestring):
        y, s = re.search(r'^(' + year + '):(' + seasons + ')-' + year + ':' + seasons + '$', datestring).group(1, 2)
        return DateConverter.conv_season2pqan(s + ' ' + y)
    ###1976:Autumn/1977:Winter
    elif re.search(r'^' + year + ':' + seasons + '/' + year + ':' + seasons + '$', datestring):
        y, s = re.search(r'^(' + year + '):(' + seasons + ')/' + year + ':' + seasons + '$', datestring).group(1, 2)
        return DateConverter.conv_season2pqan(s + ' ' + y)
    ###1933/1934:Winter
    elif re.search(r'^' + year + '/' + year + ':' + seasons + '$', datestring):
        y, s = re.search(r'^(' + year + ')/' + year + ':(' + seasons + ')$', datestring).group(1, 2)
        return DateConverter.conv_season2pqan(s + ' ' + y)
    ###1960:Spring/Autumn
    elif re.search(r'^' + year + ':' + seasons + '/' + seasons + '$', datestring):
        y, s = re.search(r'^(' + year + '):(' + seasons + ')/' + seasons + '$', datestring).group(1, 2)
        return DateConverter.conv_season2pqan(s + ' ' + y)
    ###1991/1992:Fall/Winter
    elif re.search(r'^' + year + '/' + year + ':' + seasons + '/' + seasons + '$', datestring):
        y, s = re.search(r'^(' + year + ')/' + year + ':(' + seasons + ')/' + seasons + '$', datestring).group(1, 2)
        return DateConverter.conv_season2pqan(s + ' ' + y)
    ###1986:Winter/Spring/Summer/Fall
    elif re.search(r'^' + year + ':' + seasons + '/' + seasons + '/' + seasons + '/' + seasons + '$', datestring):
        y, s = re.search(r'^(' + year + '):(' + seasons + ')/' + seasons + '/' + seasons + '/' + seasons + '$', datestring).group(1, 2)
        return DateConverter.conv_season2pqan(s + ' ' + y)
    ###1986:Winter/Spring-Summer/Fall
    elif re.search(r'^' + year + ':' + seasons + '/' + seasons + '-' + seasons + '/' + seasons + '$', datestring):
        y, s = re.search(r'^(' + year + '):(' + seasons + ')/' + seasons + '-' + seasons + '/' + seasons + '$', datestring).group(1, 2)
        return DateConverter.conv_season2pqan(s + ' ' + y)

    # HERE ###
    elif re.search(r'^' + seasons + ' ' + year + '[/-]' + year + '$', datestring):
        s, y = re.search(r'^(' + seasons + ') ' + year + '[/-](' + year + ')$', datestring).group(1, 2)
        return DateConverter.conv_season2pqan("%s %s" % (s, y))
    elif re.search(r'^' + day + '(?:st|nd|rd|th)? ' + months + ' ' + year + '$', datestring):
        return DateConverter.conv_dmy_pqan(datestring)
    elif re.search(r'^' + months + ' ' + day + ',? ' + year + '\.?$', datestring):
        return DateConverter.conv_mdy_pqan(datestring.replace('.', ''))
    # Oct 9,1980  (in WWD sample, 16 April 2013 DB)
    elif re.search(r'^' + months + ' ' + day + ',' + year + '$', datestring):
        _date = ' '.join(datestring.replace(',', ' ').split())
        return DateConverter.conv_mdy_pqan(_date)    #datestring.replace(',', ', '))
    elif re.search(r'^' + months + ' ' + year + '[/-]' + months + ' ' + year + '$', datestring):
        date1, date2 = re.split('[/-]', datestring)
        return DateConverter.conv_my_pqan(date1) + '-' + DateConverter.conv_my_pqan(date2)
    elif re.search(r'^' + months + ' ' + year + '$', datestring):
        return DateConverter.conv_my_pqan(datestring)
    # December 2009|December 2009
    elif re.search(r'^(?P<date>' + months + ' ' + year + ')|(?P=date)$', datestring):
        return DateConverter.conv_my_pqan(datestring.split('|')[0])
    # December 1992-January -> Dec 1992
    elif re.search(r'^' + months + ' ' + year + '-' + months + '$', datestring):
        return DateConverter.conv_my_pqan(datestring.split('-')[0])
    # December -1953:January 1952 -> December 1952-January 1953
    elif re.search(r'^' + months + ' -' + year + ':' + months + ' ' + year + '$', datestring):
        mf, yf, mt, yt = re.search(r'^(' + months + ') -(' + year + '):(' + months + ') (' + year + ')$', datestring).group(1, 4, 3, 2)
        return "%s %s-%s %s" % (mf, yf, mt, yt)

    elif re.search(r'^%s(?:st|nd|rd|th)?(?: %s)? ?/ ?%s(?:st|nd|rd|th)? %s$' % (day, months, day, months), datestring, re.IGNORECASE):
        raise IncompleteTextualDateError
    
    elif re.search(r'^' + months + ' ?/ ?' + months + ' \d{4}', datestring):
        datestring = datestring.replace(' /', '/')
        months, year = datestring.split(' ')
        month1, month2 = months.split('/')
        retval = DateConverter.num_to_abbrev(DateConverter.name_to_num(month1[:3]))
        retval += '/'
        retval += DateConverter.num_to_abbrev(DateConverter.name_to_num(month2[:3]))
        retval += ', ' + year
        return retval
    elif re.search(r'^' + months + ' ?- ?' + months + ' ?\d{4}', datestring):
        bits = datestring.split(' ')
        year = bits[-1]
        months_ = ''.join(bits[0:-1])
        month1, month2 = months_.split('-')
        retval = DateConverter.num_to_abbrev(DateConverter.name_to_num(month1))
        retval += '-'
        retval += DateConverter.num_to_abbrev(DateConverter.name_to_num(month2))
        retval += ', ' + year
        sys.stderr.write(retval + ' --- ' + datestring)
        return retval
    elif re.search(r'^' + year + '$', datestring):
        return datestring
#    elif re.search(r'^(?P<yearstr>' + year + '-' + year + ')|(?P=yearstr)|(?P=yearstr)$', datestring):
#        return datestring.split('|', 1)[0].split
    elif re.search(r'^' + year + '-' + months + ' \d{2}$', datestring):
        y, m = re.search(r'^(' + year + ')-(' + months + ') \d{2}$', datestring).group(1, 2)
        return DateConverter.conv_my_pqan(m + ' ' + y)
    elif re.search(r'^(?P<yearstr>' + year + '-' + year + ')(|(?P=yearstr)){0,}$', datestring):
#        print >> sys.stderr, ("DEBUG: " + datestring)
#        print >> sys.stderr, ('/'.join(datestring.split('|')[0].split('-')))
        return '/'.join(datestring.split('|')[0].split('-'))
    elif re.search(r'^' + year + ', ' + year + '$', datestring):
        return ('/').join(datestring.split(', '))
    elif re.search(r'^' + year + '/' + year + '$', datestring):
        return datestring
    elif re.search(r'^(?P<yearstr>' + year + ')|(?P=yearstr)$', datestring):
        return datestring.split('|', 1)[0]
    elif re.search(r'^' + seasons + '\] *\[' + year, datestring):
        s, y = re.search(r'^(' + seasons + ')\] *\[(' + year + ')', datestring).group(1, 2)
        return DateConverter.conv_season2pqan(s + ' ' + y)
    elif re.search(r'^' + quarters + ' ' + year + '$', datestring):
        return DateConverter.quarter2pqan(datestring)
    elif re.search(r'^Holiday ' + year + '$', datestring):
        return DateConverter.conv_my_pqan(datestring.replace('Holiday', 'December'))
    elif re.search(r'^Christmas,? ' + year + r'\.?$', datestring, re.IGNORECASE):
        return DateConverter.conv_my_pqan(datestring.lower().replace('christmas', 'December'))
    elif re.search(r'^Xmas ' + year + '$', datestring):
        return DateConverter.conv_my_pqan(datestring.replace('Xmas', 'December'))
    elif re.search(r'^Annual,? %s' % year, datestring):
        return DateConverter.conv_my_pqan(datestring.replace('Annual', 'December'))
    elif re.search('^' + day + '\d?$', datestring):
        return u"Jan 1, 1"
    elif re.search(r'^' + day + ' ' + months + ' ' + day + '$', datestring):
        return u"Jan 1, 1"
    elif re.search(r'^' + seasons + ' | ' + day + '$', datestring):
        return u"Jan 1, 1"
    elif re.search(r'^' + seasons + '[- /]' + seasons + ' ' + year + '$', datestring):
        return u"Jan 1, 1"
    elif re.search(r'^' + months + ' |  ' + day + '[0-9]?$', datestring):
        return u"Jan 1, 1"
    elif re.search(r'^' + months + '[- /]' + months + ' ' + day + '$', datestring):
        return u"Jan 1, 1"
    elif re.search(r'^\d{,3}-\d{,3}$', datestring):
        return u"Jan 1, 1"
    elif re.search(r'^\d \d{4}$', datestring):
        return re.search(r'^\d (\d{4})$', datestring).group(1)
    else:
        return datestring


def pq_numeric_date(datestring):
    day, months, seasons, year, quarters = _setregexes()
    # datestring should be a ProQuest standardised alpha-numeric string
    if datestring == 'Jan 1, 1':
        return u'00010101'
    if re.search(r'^\[?\d{4}\]?$', datestring):
        return DateConverter.year_only(re.sub(r'\[|\]', '', datestring))
    elif re.search(r'^' + seasons + ' ' + year + '$', datestring):
        return DateConverter.conv_season(datestring)
    elif re.search(r'^' + seasons + ' \[' + year + '\]$', datestring):
        return DateConverter.conv_season(re.sub('\[|\]', '', datestring))
    elif re.search(r'^' + seasons + ' ' + year + '-' + year + '$', datestring):
        return DateConverter.conv_season(datestring.split('-')[0])
    elif re.search(r'^' + seasons + ' ' + year + '/' + year + '$', datestring):
        return DateConverter.conv_season(datestring.split('/')[0])
    elif re.search(r'^' + seasons + '/' + seasons + ' ' + year + '/' + year + '$', datestring):
        s, y = re.search(r'^(' + seasons + ')/[A-Za-z]+ (' + year + ')/\d{4}$', datestring).group(1, 2)
        return DateConverter.conv_season(s + ' ' + y)
    elif re.search(r'^' + seasons + '/' + seasons + ' ' + year, datestring):
        return DateConverter.conv_season_double(datestring)
    elif re.search(r'^' + seasons + '-' + seasons + ' ' + year + '$', datestring):
        return DateConverter.conv_season_multiple(datestring)
    elif re.search(r'^' + seasons + '-' + seasons + ' ' + year + '-' + year + '$', datestring):
        s = datestring.split(' ')[0].split('-')[0]
        y = datestring.split(' ')[1].split('-')[0]
        return DateConverter.conv_season(s + ' ' + y)
    elif re.search(r'^' + seasons + ' ' + year + '-' + seasons + ' ' + year + '$', datestring):
        return DateConverter.conv_season(datestring.split('-')[0])
    elif re.search(r'^' + seasons + '/' + seasons + '-' + year + ':' + seasons + '/' + seasons + ' ' + year + '$', datestring):
        s, y = re.search(r'^(' + seasons +').*(' + year + ')$', datestring).group(1, 2)
        return DateConverter.conv_season(s + ' ' + y)
    elif re.search(r'^' + months + ' ' + day + ',? ' + year + '-' + months + ' ' + day + ',? ' + year, datestring):
        return DateConverter.conv_mdy(datestring.split('-')[0])
    elif re.search(r'^' + months + ' ' + day + ',? ' + year + '$', datestring):
        return DateConverter.conv_mdy(datestring)
    elif re.search(r'^' + day + ' ' + months + ' ' + year + '$', datestring):
        return DateConverter.conv_dmy(datestring)
    elif re.search(r'^' + months + '[-/]' + months + ' ' + year + '$', datestring):
        month, year = re.search(r'([A-Za-z]+)[-/][A-Za-z]+,? (\d{4})', datestring).group(1,2)
        return DateConverter.conv_my(month + ' ' + year)
    elif re.search(r'^\[?' + months + '\]? ' + year + '$', datestring):
        return DateConverter.conv_my(re.sub(r'\[|\]', '', datestring))
    elif re.search(r'^' + months +'-' + year + ':' + months + ' ' + year, datestring):
        m, y = re.search('^(' + months + ').*(' + year + ')$', datestring).group (1, 2)
        return DateConverter.conv_my(m + ' ' + y)
    elif re.search(r'^' + months + ' ' + year + '[-/]' + months + '( ' + year + ')?', datestring):
        return DateConverter.conv_my(re.search(r'([A-Za-z]+ \d{4}).*', datestring).group(1))
#    elif re.search(r'^' + months + ' ' + year + '-' + year + '$', datestring):

    elif re.search(r'^' + year + '[/-]' + year + '$', datestring):
        return DateConverter.year_only(datestring)
    elif re.search(r'^' + quarters + ' ' + year + '$', datestring):
        return DateConverter.quarter(datestring)
    elif re.search(r'^' + months + ' ' + day + '-' + months + ' ' + day + ', ' + year + '$', datestring):
        date, year = re.search(r'^(' + months + ' ' + day + ')-' + months + ' ' + day + ', (' + year + ')$', datestring).group(1,2)
        return DateConverter.conv_mdy(date + ' ' + year)

    elif re.search(r'^' + months + ' ' + day + ', ' + year + '/' + months + ' ' + day + ', ' + year + '$', datestring):
        month, day, year = re.search(r'^(' + months + ') (' + day + '), (' + year + ')/.*$', datestring).group(1, 2, 3)
        #date, year = re.search(r'^(' + months + ' ' + day + ', ' + year ')/' + months + ' ' + day + ', (' + year + ')$', datestring).group(1,2)
        return DateConverter.conv_mdy(month + ' ' + day + ' ' + year)

    elif re.search(r'^%s %s.?' % (months, year), datestring):
        return DateConverter.conv_my(datestring.replace('.', ''))
    #elif re.search('^' + months + '-' + months + year, datestring):
    #    m, y = re.search('^(' + months + ').*(\d{4})', datestring).group(1, 2)
    #    return DateConverter.conv_my(m + ' ' + y)
    else:
        raise UnhandledDateFormatException(datestring)
