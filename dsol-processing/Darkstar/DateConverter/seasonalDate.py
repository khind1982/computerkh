'''
Functions to convert dates like "Spring 2002" to '20020401'.

The conversion rules are:
    Winter begins Jan 1 (0101)
    Spring begins Apr 1 (0401)
    Summer begins Jul 1 (0701)
    Autumn begins Oct 1 (1001) (Fall is a synonym for Autumn)
    
'''

from base import *

season_dates = {'Winter':'0101', 'Spring':'0401', 'Summer':'0701',
           'Autumn':'1001', 'Fall':'1001'}

def conv_season(datestring):
    '''Return a normalized numeric datestring
    >>> conv_season('spring 2002')
    '20020401'
    '''
    season, year = datestring.split(' ')
    return year + season_dates[unabbreviate(season)]

def conv_season2pqan(datestring):
    '''Return a normalized text date string
    >>> conv_season2pqan('spring, 2002')
    'Spring 2002'
    '''
    season, year = datestring.split(' ')
    return ds_trim(unabbreviate(season)).capitalize() + ' ' + year

def conv_season_double(datestring):
    '''Return a normalized double-issue season date string
    >>> conv_season_double('Spring 2002/Summer 2002')
    '20020401'
    '''
    s1, s2 = datestring.split('/')
    return build_date(unabbreviate(s1), unabbreviate(s2))
    
'''def conv_season_double2pqan(datestring):
    s1, s2 = datestring.split('/')
    s1_season, s1_year = s1.split(' ')
   ''' 
    
def conv_season_multiple(datestring):
    s1, s2 = datestring.split('-')
    return build_date(unabbreviate(s1),unabbreviate(s2))
    
def conv_season_multiple2pqan(datestring):
    s1, s2 = datestring.split('-')
    s1 = s1.strip()
    s2 = s2.strip()
    s1_season, s1_year = s1.split(' ')
    s2_season, s2_year = s2.split(' ')
    return ds_trim(unabbreviate(s1_season)).capitalize() + ' ' + s1_year + \
           '-' + ds_trim(unabbreviate(s2_season)).capitalize() + ' ' + s2_year
    
def unabbreviate(s):
    if s == "Win": return u'Winter'
    if s == "Fal": return u'Fall'
    if s == "Spr": return u'Spring'
    if s == "Sum": return u'Summer'
    return s
           
def build_date(s1,s2):
    if len(s1.split(' ')) == 2:
        season, year = s1.split(' ')
    else:
        season = s1
        year = s2.split(' ')[1]
    return year + season_dates[season.capitalize()]
