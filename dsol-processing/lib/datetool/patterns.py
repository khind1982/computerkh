# -*- coding: utf-8 -*-
# pylint: disable = invalid-name, missing-docstring

from collections import OrderedDict

# Token names used by the lexer.
# Split for mnemonic and semantic purposes, not technical.

# We're using OrderedDict so that we get back our token names
# in the same order we define them.

# Modify the patterns to accommodate new values. Bear in mind that
# when we build the lexer, we tell it to ignore case in the matches.
# This can make a difference in how you structure the patterns. This
# is Python, though, so if it doesn't work one way, change it!

wdays = OrderedDict([
    ('SUN', r'Sun(day)?'),
    ('MON', r'Mon(day)?'),
    ('TUE', r'Tues?(day)?'),
    ('WED', r'Wed(nesday)?'),
    ('THU', r'Thu(rsday)?'),
    ('FRI', r'Fri(day)?'),
    ('SAT', r'Sat(urday)?'),
])

months = OrderedDict([
    ('JAN', r'Jan(uary?|vier)?|enero|gen(naio)?'),
    ('FEB', r'Feb(ruary?|rero|braio)?|fév(rier)?'),
    ('MAR', r'Mar(ch|s|zo)?|März?'),
    ('APR', r'Apr(il(e)?)?|avr(il)?|abr(illio)'),
    ('MAY', r'May|Mai|mai|mayo|mag(gio)?'),
    ('JUN', r'Jun[ei]?|juin|junio|giu(g(no)?)?'),
    ('JUL', r'Jul[iy]?|juillet|julio|lug(lio)?'),
    ('AUG', r'Aug(ust)?|août|ag(o(sto)?)?'),
    ('SEP', r'Sep(t(ember)?)?|set(t(embre)?)?'),
    ('OCT', r'O[ckt]t(ob[er]{2})?'),
    ('NOV', r'Nov(emb[er]{2})?'),
    ('DEC', r'De[cz](ember)?|d[éi]c(embre)?'),
])


# The values here are two-tuples, where the second element is the month to which
# the season is normalised.
seasons = OrderedDict([
    ('SPRING', (r'Spr(ing)?', 'Apr')),
    ('SUMMER', (r'Summer|été|Sommer', 'Jul')),
    ('AUTUMN', (r'Autumn|Fall|autonne', 'Oct')),
    ('WINTER', (r'Winter|hiver|invierno', 'Jan')),
])

# The values here are three-tuples, where the second and third elements are the
# month and day to which the special date is normalised.
#
# If you add a new token here, don't forget to add it to the p_special rule in
# the dateparser.py file! If you don't, it won't be parsed and will continue
# to be considered an illegal token.

specials = OrderedDict([
    ('ANNUAL', (r'Annual', 'Dec', '1')),
    ('CHRISTMAS', (r'(X|Christ)mas', 'Dec', '1'))
])

wday_names = wdays.keys()
month_names = months.keys()
season_names = seasons.keys()
specials_names = specials.keys()
