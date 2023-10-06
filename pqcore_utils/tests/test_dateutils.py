import pytest

import pqcoreutils

from pqcoreutils.dateutils import Seasons, SeasonTranslator, SeasonTranslatorRegistry


def test_interpolate_year():
    """It's useful to be able to interpolate the current year into a
    string, e.g. for copyright statements in XML, etc. By defaul, we
    replace the template in the string with the current year."""
    year = pqcoreutils.dateutils.current_year()
    result = pqcoreutils.dateutils.interpolate_year("test text <CURYEAR>")
    assert f"test text {year}" == result


def test_interpolate_year_specific_date():
    """The user can specify the year to interpolate. In this case,
    use the provided year, not the current year."""
    test_text = "test text <CURYEAR>"
    year = 1990
    result = pqcoreutils.dateutils.interpolate_year(test_text, year=year)
    assert result == f"test text {year}"


def test_interpolate_year_custom_template_string():
    """If the string contains a token other than <CURYEAR> that needs to
    be replaced with the year, allow the user to specify what it is."""
    test_text = "test text, custom template string: #replaceme#"
    year = 2010
    result = pqcoreutils.dateutils.interpolate_year(
        test_text, year=year, template_string="#replaceme#")
    assert result == f"test text, custom template string: 2010"


def test_interpolate_year_multiple_loci():
    """If there are multiple template strings in the input, make
    sure we catch 'em all.'"""
    test_text = "match 1: <CURYEAR>; match 2: <CURYEAR>; match 3: <CURYEAR>"
    year = pqcoreutils.dateutils.current_year()
    result = pqcoreutils.dateutils.interpolate_year(test_text)
    assert result == f"match 1: {year}; match 2: {year}; match 3: {year}"


def idfn(value):
    '''If your parametrized tests yield IDs with spaces, use this to
    convert the spaces to '--' instead.'''
    if isinstance(value, str):
        return value.replace(' ', '--')


@pytest.mark.parametrize("date,desired", [
    ('January 1 2021', (1, 2021, 1)),
    ('May 2021', (5, 2021, 1)),
    ('1st February 2021', (2, 2021, 1)),
    ('1989', (1, 1989, 1)),
    ('19600512', (5, 1960, 12)),
    ('12/5/2010', (5, 2010, 12))
], ids=idfn)
def test_date_object_from_patterns(date, desired):
    """Given a string date with a pattern, when it is processed by
    date_objects_from_pattern, then a date object is returned."""
    patterns = ['%d/%m/%Y', '%B %d %Y', '%Y%m%d', '%b %Y', '%dst %B %Y', '%Y']
    date = pqcoreutils.dateutils.date_object_from_patterns(
        date, patterns=patterns)
    month, year, day = desired
    assert date.month == month
    assert date.year == year
    assert date.day == day


@pytest.mark.parametrize("date,desired", [
    ("avril 1 1982", (4, 1982, 1)),
    ("abril 1 1982", (4, 1982, 1)),
    ("Dezember 31 1982", (12, 1982, 31))
])
def test_date_object_from_pattern_with_language_spec_passes(date, desired):
    patterns = ['%B %d %Y']
    languages = ['fr', 'es', 'de']
    date = pqcoreutils.dateutils.date_object_from_patterns(
        date, patterns=patterns,
        languages=languages
    )
    month, year, day = desired
    assert date.month == month
    assert date.year == year
    assert date.day == day


def test_date_object_from_pattern_with_language_spec_fails():
    patterns = ['%B %d %Y']
    languages = ['fr', 'es']
    with pytest.raises(ValueError):
        pqcoreutils.dateutils.date_object_from_patterns(
            'Juni 30 1989', patterns=patterns,
            languages=languages
        )


def test_date_object_from_pattern_with_garbage_language_fails():
    patterns = ['%B %d %Y']
    languages = ['nonesuch']
    with pytest.raises(RuntimeError):
        pqcoreutils.dateutils.date_object_from_patterns(
            'avril 1 1982', patterns=patterns,
            languages=languages
        )


def test_date_object_from_patterns_raises_error_for_unrecognised_pattern():
    """Given a string date with a pattern, when it is processed by
    date_objects_from_pattern and does not match, then ValueError is raised"""
    pattern = ['%B %Y']
    with pytest.raises(ValueError):
        pqcoreutils.dateutils.date_object_from_patterns(
            'Octember 1982', patterns=pattern)


def test_date_object_from_patterns_includes_triggered_pattern():
    """The object returned from date_object includes a pattern attribute"""
    pattern = ['%Y']
    date_string = '2010'
    date = pqcoreutils.dateutils.date_object_from_patterns(date_string, pattern)
    assert date.pattern == '%Y'


def test_date_object_from_pattern_includes_season_pattern():
    pattern = ['%S %Y']
    date_string = 'Autumn 2021'
    date = pqcoreutils.dateutils.date_object_from_patterns(date_string, pattern)
    assert date.month == 10
    assert date.year == 2021

@pytest.mark.parametrize('season,lang,month', [('hiver', 'fr', 1), ('verano', 'es', 7)])
def test_date_object_from_pattern_non_english_seasonal_date(season, lang, month):
    pattern = ['%S %Y']
    date_string = f'{season} 2021'
    date = pqcoreutils.dateutils.date_object_from_patterns(date_string, pattern, languages=[lang])
    assert date.month == month
    assert date.year == 2021


def test_datetimeformat():
    date = pqcoreutils.dateutils.datetimeformat.strptime('2010', '%Y')
    assert date.pattern == '%Y'


SEASONS_TEST_DATA = [
    (Seasons.WINTER, False, 'January'),
    (Seasons.SPRING, False, 'April'),
    (Seasons.SUMMER, False, 'July'),
    (Seasons.AUTUMN, False, 'October'),
    (Seasons.WINTER, True, 'July'),
    (Seasons.SPRING, True, 'October'),
    (Seasons.SUMMER, True, 'January'),
    (Seasons.AUTUMN, True, 'April'),
]

@pytest.mark.parametrize(
    'season,sh,expected',
    SEASONS_TEST_DATA
    )
def test_seasons_knows_about_north_and_south(season, sh, expected):
    '''Can the Seasons Enum correctly convert an instance to the appropriate
    month name for Northern and Southern hemispheres?'''

    assert Seasons.to_name(season, southern_hemisphere=sh) == expected


ENG_DATA = [
    ('Winter', False, 'January'),
    ('Spring', False, 'April'),
    ('Summer', False, 'July'),
    ('Autumn', False, 'October'),
    ('Fall', False, 'October'),
    ('Winter', True, 'July'),
    ('Spring', True, 'October'),
    ('Summer', True, 'January'),
    ('Autumn', True, 'April'),
    ('Fall', True, 'April'),
]

FR_DATA = [
    ('hiver', False, 'January'),
    ('printemps', False, 'April'),
    ('été', False, 'July'),
    ('ete', False, 'July'),
    ('automne', False, 'October'),
    ('hiver', True, 'July'),
    ('printemps', True, 'October'),
    ('été', True, 'January'),
    ('ete', True, 'January'),
    ('automne', True, 'April'),
]

# There are, as far as I know, no German-speaking academic populations
# in the Southern Hemisphere...
DE_DATA = [
    ('Winter', False, 'January'),
    ('winter', False, 'January'),
    ('Frühling', False, 'April'),
    ('frühling', False, 'April'),
    ('fruhling', False, 'April'),
    ('Sommer', False, 'July'),
    ('sommer', False, 'July'),
    ('Herbst', False, 'October'),
    ('herbst', False, 'October')
]

@pytest.fixture(params=ENG_DATA)
def english_seasons(request):
    return request.param


@pytest.fixture(params=FR_DATA)
def french_seasons(request):
    return request.param


@pytest.fixture(params=DE_DATA)
def german_seasons(request):
    return request.param


class TestSeasonTranslator:

    def test_create_translator_from_dict(self, english_seasons):
        '''The SeasonTranslator.from_dict method should be able to construct a new
        derived class from the passed values. If a value has non-ASCII characters,
        it will appear twice in the resulting dict - once as is (case-folded to lower),
        and the other with non-ASCII characters normalised to their plain ASCII base.
        That is, 'é' will be normalised to 'e', etc.
        If a value includes a comma, then it is assumed that the comma separates
        alternative names for the season, such as 'autumn,fall' for English. In these
        cases, each season name gets an entry in the dict, subject to the foregoing rules.'''
        English = SeasonTranslator.from_dict(
            'English', {'winter': 'Winter', 'spring': 'Spring',
                        'summer': 'Summer', 'autumn': 'Autumn,Fall'})

        tr = English()
        season, sh, expected = english_seasons
        assert tr(season, southern_hemisphere=sh) == expected

    def test_create_translator_from_dict_out_of_sequence(self, english_seasons):
        '''Although Python now preserves dictionary items insertion order,
        relying on it still feels like an anti-pattern. Make sure we can
        successfully create a new SeasonTranslator subclass when given a dict
        whose keys aren't given in the strict winter, spring, summer, autumn
        sequence.'''
        English = SeasonTranslator.from_dict(
            'English', {
                'spring': 'Spring', 'winter': 'Winter',
                'summer': 'Summer', 'autumn': 'Autumn,Fall'})

        tr = English()
        season, sh, expected = english_seasons
        assert tr(season, southern_hemisphere=sh) == expected

    def test_create_translator_from_list(self, english_seasons):
        '''The SeasonTranslator.from_sequence method should construct a new derived class
        from values passed in a sequence - a list, tuple, etc. Rules about multiple
        names and non-ASCII characters are the same as for from_dict.'''
        English = SeasonTranslator.from_sequence(
            'English', ['winter', 'spring', 'summer', 'autumn,fall'])

        tr = English()
        season, sh, expected = english_seasons
        assert tr(season, southern_hemisphere=sh) == expected

    def test_create_translator_from_tuple(self, english_seasons):
        '''The SeasonTranslator.from_sequence method should construct a new derived class
        from values passed in a sequence - a list, tuple, etc. Rules about multiple
        names and non-ASCII characters are the same as for from_dict.'''
        English = SeasonTranslator.from_sequence(
            'English', ('winter', 'spring', 'summer', 'autumn,fall'))

        tr = English()
        season, sh, expected = english_seasons
        assert tr(season, southern_hemisphere=sh) == expected

    def test_create_translator_with_non_ascii_chars(self, french_seasons):
        French = SeasonTranslator.from_sequence(
            'French', ('hiver', 'printemps', 'été', 'automne'))

        tr = French()
        season, sh, expected = french_seasons
        assert tr(season, southern_hemisphere=sh) == expected

    def test_create_translator_is_case_insensitive_on_lookup(self, german_seasons):
        '''Make sure we can use capitalised and all lower case values in the lookup.
        German also uses non-ASCII chars.'''
        German = SeasonTranslator.from_sequence(
            'German', ('Winter', 'Frühling', 'Sommer', 'Herbst'))

        tr = German()
        season, sh, expected = german_seasons
        assert tr(season, southern_hemisphere=sh) == expected

    def test_returns_all_translations_as_a_mapping(self):
        '''In addition to calling the instance with the single season name to translate,
        it is possible to get a dict-like view of all translations for a given translator.'''
        French = SeasonTranslator.from_sequence(
            'French', ('hiver', 'printemps', 'été', 'automne'))

        tr = French()
        assert isinstance(translations := tr.translations(), dict)
        for season, trans in translations.items():
            assert trans == tr(season)


class TestSeasonTranslatorRegistry:
    def test_has_default_translators(self):
        '''There should be a registry of known translators. It will be
        pre-populated with translators for English, French and Spanish, and
        should be easy for a developer to define and register a new one for any
        language they need.'''
        registry = SeasonTranslatorRegistry()
        for language in ['en', 'fr', 'es']:
            assert language in registry.known_translators

    def test_registry_has_default_language(self):
        '''The registry has a default translator it will use when methods are
        called with no explicit indication of which language is required.'''
        registry = SeasonTranslatorRegistry()
        default = registry.default_translator
        assert default == 'en'
        assert registry.default_translator == 'en'

    def test_multiple_instances_share_translators_and_default(self):
        '''No matter how many registries are created in an application, they should
        all use the same underlying state to avoid surprises.'''
        reg1 = SeasonTranslatorRegistry()
        reg2 = SeasonTranslatorRegistry()

        assert reg1.registry is reg2.registry

    def test_get_translations_for_specified_language(self, english_seasons):
        '''Return the translations for the given language.'''
        registry = SeasonTranslatorRegistry()
        season, sh, month = english_seasons
        assert registry.translations('en', southern_hemisphere=sh)[season.lower()] == month

    def test_get_translations_for_default_language(self, english_seasons):
        '''When SeasonTranslatorRegistry.translations() is called with no language code,
        return the translations for the default translator'''
        registry = SeasonTranslatorRegistry()
        season, sh, month = english_seasons
        assert registry.translations(southern_hemisphere=sh)[season.lower()] == month

    def test_register_new_translator(self):
        '''Allow users to specify and register new translator classes. We accept either class
        derived from SeasonTranslator, or an instance of the derived class.'''
        pt_translator = SeasonTranslator.from_sequence(
            'Portuguese', ('inverno', 'primavera', 'verão', 'outono'))

        registry = SeasonTranslatorRegistry()
        registry.register('pt', pt_translator)
        registry.register('pt_BR', pt_translator())
        assert 'pt' in registry.known_translators
        assert isinstance(registry.registry['pt'], SeasonTranslator)
        assert isinstance(registry.registry['pt_BR'], SeasonTranslator)

    def test_register_new_default_translator(self):
        '''When registering a new translator, it is possible to tell the registry to treat it as
        the default translator.'''
        registry = SeasonTranslatorRegistry()

        pt_translator = SeasonTranslator.from_sequence(
            'Portuguese', ('inverno', 'primavera', 'verão', 'outono'))

        registry.register('pt', pt_translator, default=True)
        assert registry.default_translator == 'pt'
        assert registry.translations()['inverno'] == 'January'

    def test_set_default_translator(self):
        '''Allow setting the default translator at any arbitrary point in time, not just when
        a new translator is registered.'''
        registry = SeasonTranslatorRegistry()

        registry.default_translator = 'es'
        assert registry.default_translator == 'es'

        # Make sure that all instances see the same default translator
        reg2 = SeasonTranslatorRegistry()
        assert reg2.default_translator == 'es'


def test_base_translators_on_dateutils_module_ns():
    '''The three base SeasonTranslators (en, fr and es) should be available on the
    dateutils namespace, as well as in the SeasonTranslatorRegistry.'''
    for lang in ['English', 'French', 'Spanish']:
        tr = getattr(pqcoreutils.dateutils, lang)
        assert isinstance(tr, type)
        assert issubclass(tr, SeasonTranslator)


@pytest.mark.skip(reason="Is this needed?")
def test_new_translators_are_registered_on_dateutils():
    '''If the user registers a new translator through the SeasonTranslatorRegistry, make
    it available on dateutils as well.'''
    SeasonTranslatorRegistry().register(
        'fi', SeasonTranslator.from_sequence(
            'Finnish',
            ('talvi', 'kevät', 'kesä', 'syksy')))
    tr = getattr(pqcoreutils.dateutils, 'Finnish')
    assert isinstance(tr, type)
    assert issubclass(tr, SeasonTranslator)
