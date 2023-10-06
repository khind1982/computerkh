import enum
import re
import datetime
import unicodedata

from typing import Dict, List, Mapping, Optional, Sequence, Type

import dateparser


def interpolate_year(text: str, *, year=None, template_string="<CURYEAR>") -> str:
    if year is None:
        year = current_year()

    return text.replace(template_string, str(year))


def current_year() -> int:
    return datetime.datetime.now().year


def today() -> str:  # pragma: no cover
    return datetime.datetime.today().strftime("%Y%m%d")


class datetimeformat(datetime.datetime):
    """Custom datetime class which stores the format used to instantiate the
    object when calling strptime.

    When wanting to create a string date from this object, the stored format
    can be used to get back the original date_string.
    """
    @classmethod
    def strptime(cls, date_string: str, format: str, languages=None) -> datetime.datetime:
        # string, format -> new datetime parsed from a string (like time.strptime()).
        if languages is None:
            languages = ['en']

        original_format = format
        if "%S" in format:
            format = format.replace('%S', '%B')
            for season, month in SeasonTranslatorRegistry().translations(
                    language=languages[0]).items():
                date_string = re.sub(fr'(?i){season}', month, date_string)

        date_object: Optional[datetime.datetime]

        if re.match(r'\d{4}', date_string):
            date_object = super().strptime(date_string, format)
        else:
            date_object = dateparser.parse(
                date_string, date_formats=[format],
                settings={'PREFER_DAY_OF_MONTH': 'first'},
                languages=languages)

        if date_object is None:
            raise ValueError

        date_object = cls(date_object.year, date_object.month, date_object.day)
        setattr(date_object, 'pattern', original_format)

        return date_object


def date_object_from_patterns(date, patterns=None, languages=None) -> datetime.datetime:
    """Datetime objects from input patterns."""
    if languages is None:
        languages = ['en']
    for pattern in patterns:
        try:
            return datetimeformat.strptime(date, pattern, languages)
        except ValueError as exc:
            if "Unknown language" in str(exc):
                raise RuntimeError from exc
    raise ValueError(f'Date format not recognised: "{date}". Accepted formats are {patterns}')


class Seasons(enum.Enum):
    '''An enumeration representing the seasons of the year, and the
    month they are considered to start in the Northern and Southern
    Hemispheres. It is not expected to be used directly - the various
    translator classes will use it to handle converting source language
    season names into the corresponding month names for normalised PQ
    dates.'''
    WINTER = (1, 7)
    SPRING = (4, 10)
    SUMMER = (7, 1)
    AUTUMN = (10, 4)

    @classmethod
    def to_name(cls, instance: 'Seasons', southern_hemisphere: bool = False) -> str:
        month = instance.value[1 if southern_hemisphere else 0]
        return datetime.datetime(1900, month, 1).strftime("%B")


class SeasonTranslator:
    @classmethod
    def from_dict(cls, language: str, mapping: Mapping) -> Type['SeasonTranslator']:
        '''Creates a new SeasonTranslator from values passed in as a dict. The dict's keys must
        be "winter", "spring", "summer" and "autumn" or the method will fail.'''
        return cls._build_translator_subclass(
            language,
            ((value, getattr(Seasons, key.upper())) for key, value in mapping.items()))

    @classmethod
    def from_sequence(cls, language: str, values: Sequence) -> Type['SeasonTranslator']:
        '''Create a new SeasonTranslator class from the passed sequence. Season names in the
        target language must be presented in the order "winter", "spring", "summer", "autumn",
        or the translation sequence will be incorrect.'''
        return cls._build_translator_subclass(language, zip(values, Seasons))

    @classmethod
    def _build_translator_subclass(cls, language: str, data):
        translation_table = {}
        for name, season in data:
            for n in [n.strip().lower() for n in name.split(',')]:
                if not n.isascii():
                    translation_table[cls._normalize_non_ascii_chars(n)] = season
                translation_table[n] = season
        return type(language, (SeasonTranslator,), {'translation_table': translation_table})

    @staticmethod
    def _normalize_non_ascii_chars(text):
        # Converts any accented chars in :text: to their plain ASCII base value.
        # E.G. é --> e, Ñ --> N, etc.
        return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')

    def __call__(self, season: str, southern_hemisphere: bool = False) -> str:
        '''When treated like a callable and given a season name in the source language, return the
        corresponding month name, if found.'''
        return Seasons.to_name(
            getattr(self, 'translation_table')[season.lower()],
            southern_hemisphere=southern_hemisphere)

    def translations(self, southern_hemisphere=False) -> Mapping[str, str]:
        '''Returns a dict of the source language season names and corresponding
        English month names.'''
        return {k: Seasons.to_name(v, southern_hemisphere=southern_hemisphere)
                for k, v in getattr(self, 'translation_table').items()}


English = SeasonTranslator.from_sequence(
    'English', ('winter', 'spring', 'summer', 'autumn,fall'))

French = SeasonTranslator.from_sequence(
    'French', ('hiver', 'printemps', 'été', 'automne'))

Spanish = SeasonTranslator.from_sequence(
    'Spanish', ('invierno', 'primavera', 'verano', 'otoño'))


class SeasonTranslatorRegistry:
    __registry: Dict[str, SeasonTranslator] = {
        'en': English(),
        'fr': French(),
        'es': Spanish()
    }

    __default_translator = 'en'

    @property
    def known_translators(self) -> List[str]:
        return list(self.__class__.__registry.keys())

    @property
    def registry(self) -> Mapping[str, SeasonTranslator]:
        return self.__class__.__registry

    @property
    def default_translator(self) -> str:
        return self.__class__.__default_translator

    @default_translator.setter
    def default_translator(self, new_value) -> None:
        self.__class__.__default_translator = new_value

    def register(
            self, lang_code: str, translator: SeasonTranslator, default: bool = False
            ) -> None:
        '''Register a new :translator: for :lang_code:. :translator: may be given as a subclass of
        SeasonTranslator, or as an instance of a subclass of SeasonTranslator.'''
        if isinstance(translator, type):
            translator = translator()
        self.__class__.__registry[lang_code] = translator
        if default:
            self.default_translator = lang_code

    def translations(
            self, language: str = None, *, southern_hemisphere: bool = False
            ) -> Mapping[str, str]:
        return self.registry[language or self.default_translator].translations(
            southern_hemisphere=southern_hemisphere)
