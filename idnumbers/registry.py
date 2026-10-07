"""
A registry of the supported countries, with lookup by ISO 3166-1 alpha-2 or alpha-3 code.

The registry answers "which validator handles the ID numbers of this country?" without knowing the name of the
country module in advance. Every public country module ``idnumbers.nationalid.<ISO3>`` is listed by its alpha-3 code,
its alpha-2 code and its English name. The lookups accept either code in any letter case, never raise, and return
``None`` for anything they don't know, such as a ``None`` argument, a non-``str`` value, a code with surrounding
whitespace or a non-ASCII look-alike such as the dotless ``'ın'``.

Importing :mod:`idnumbers` stays cheap: the table of codes and names is plain data, and a country module is imported
the first time a lookup needs it. :func:`list_supported_countries` imports them all.

:func:`register` adds a country the library doesn't ship, or an extra alias such as a 3-letter code that isn't ISO,
to the process-wide registry. A built-in country can't be replaced or widened.

The country names are the English names of Unicode CLDR 48.2.3 (``cldr-localenames-full/main/en/territories.json``)
with three adjustments: ``BIH`` is written "Bosnia and Herzegovina" (CLDR writes "&"), and ``HKG`` and ``MAC`` are
written "Hong Kong" and "Macao" (the CLDR default names carry the suffix "SAR China").

Example::

    from idnumbers import get_country, get_validator

    get_validator('tw').validate('A123456789')    # True
    get_country('AUS').name                       # 'Australia'
    get_country('XX')                             # None
"""

import importlib
import threading
from typing import Any, Dict, List, NamedTuple, Optional, Sequence, Set, Tuple, Type

__all__ = [
    'CountryEntry',
    'get_country',
    'get_validator',
    'list_supported_countries',
    'register',
    'resolve_country',
]


class CountryEntry(NamedTuple):
    """One country of the registry."""

    alpha3: str
    """The ISO 3166-1 alpha-3 code in upper case, such as ``'TWN'``. It is the key of the registry."""

    alpha2: str
    """The ISO 3166-1 alpha-2 code in upper case, such as ``'TW'``."""

    name: str
    """The English name of the country, such as ``'Taiwan'``."""

    national_id: Type[Any]
    """The ``NationalID`` of the country module, such as ``idnumbers.nationalid.TWN.NationalID``."""

    id_types: Tuple[Type[Any], ...]
    """Every ID class the country module exports, in the order of the module, without the alias names."""


_BUILTIN: Dict[str, Tuple[str, str]] = {
    'ALB': ('AL', 'Albania'),
    'ARE': ('AE', 'United Arab Emirates'),
    'ARG': ('AR', 'Argentina'),
    'AUS': ('AU', 'Australia'),
    'AUT': ('AT', 'Austria'),
    'BEL': ('BE', 'Belgium'),
    'BGD': ('BD', 'Bangladesh'),
    'BGR': ('BG', 'Bulgaria'),
    'BHR': ('BH', 'Bahrain'),
    'BIH': ('BA', 'Bosnia and Herzegovina'),
    'BRA': ('BR', 'Brazil'),
    'CAN': ('CA', 'Canada'),
    'CHE': ('CH', 'Switzerland'),
    'CHL': ('CL', 'Chile'),
    'CHN': ('CN', 'China'),
    'COL': ('CO', 'Colombia'),
    'CYP': ('CY', 'Cyprus'),
    'CZE': ('CZ', 'Czechia'),
    'DEU': ('DE', 'Germany'),
    'DNK': ('DK', 'Denmark'),
    'ESP': ('ES', 'Spain'),
    'EST': ('EE', 'Estonia'),
    'FIN': ('FI', 'Finland'),
    'FRA': ('FR', 'France'),
    'GBR': ('GB', 'United Kingdom'),
    'GEO': ('GE', 'Georgia'),
    'GRC': ('GR', 'Greece'),
    'HKG': ('HK', 'Hong Kong'),
    'HRV': ('HR', 'Croatia'),
    'HUN': ('HU', 'Hungary'),
    'IDN': ('ID', 'Indonesia'),
    'IND': ('IN', 'India'),
    'IRL': ('IE', 'Ireland'),
    'IRN': ('IR', 'Iran'),
    'IRQ': ('IQ', 'Iraq'),
    'ISL': ('IS', 'Iceland'),
    'ISR': ('IL', 'Israel'),
    'ITA': ('IT', 'Italy'),
    'JPN': ('JP', 'Japan'),
    'KAZ': ('KZ', 'Kazakhstan'),
    'KOR': ('KR', 'South Korea'),
    'KWT': ('KW', 'Kuwait'),
    'LKA': ('LK', 'Sri Lanka'),
    'LTU': ('LT', 'Lithuania'),
    'LUX': ('LU', 'Luxembourg'),
    'LVA': ('LV', 'Latvia'),
    'MAC': ('MO', 'Macao'),
    'MDA': ('MD', 'Moldova'),
    'MEX': ('MX', 'Mexico'),
    'MKD': ('MK', 'North Macedonia'),
    'MNE': ('ME', 'Montenegro'),
    'MYS': ('MY', 'Malaysia'),
    'NGA': ('NG', 'Nigeria'),
    'NLD': ('NL', 'Netherlands'),
    'NOR': ('NO', 'Norway'),
    'NPL': ('NP', 'Nepal'),
    'NZL': ('NZ', 'New Zealand'),
    'PAK': ('PK', 'Pakistan'),
    'PHL': ('PH', 'Philippines'),
    'PNG': ('PG', 'Papua New Guinea'),
    'POL': ('PL', 'Poland'),
    'PRT': ('PT', 'Portugal'),
    'ROU': ('RO', 'Romania'),
    'SGP': ('SG', 'Singapore'),
    'SMR': ('SM', 'San Marino'),
    'SRB': ('RS', 'Serbia'),
    'SVK': ('SK', 'Slovakia'),
    'SVN': ('SI', 'Slovenia'),
    'SWE': ('SE', 'Sweden'),
    'THA': ('TH', 'Thailand'),
    'TUR': ('TR', 'Türkiye'),
    'TWN': ('TW', 'Taiwan'),
    'UKR': ('UA', 'Ukraine'),
    'USA': ('US', 'United States'),
    'VEN': ('VE', 'Venezuela'),
    'VNM': ('VN', 'Vietnam'),
    'ZAF': ('ZA', 'South Africa'),
    'ZWE': ('ZW', 'Zimbabwe'),
}
"""The built-in countries: alpha-3 code -> (alpha-2 code, English name). A new country module is added here."""

_KEYS: Dict[str, str] = {}
"""Upper-case lookup key (alpha-3, alpha-2 or custom alias) -> alpha-3 code."""

_ENTRIES: Dict[str, CountryEntry] = {}
"""The loaded built-in entries and the registered custom entries, by alpha-3 code."""

_CUSTOM: Dict[str, Tuple[str, ...]] = {}
"""The alpha-3 code of every custom country -> its extra aliases in upper case."""

_LOCK = threading.RLock()
"""Guards the lazy loads and :func:`register`."""

for _alpha3, (_alpha2, _) in _BUILTIN.items():
    _KEYS[_alpha3] = _alpha3
    _KEYS[_alpha2] = _alpha3
del _alpha3, _alpha2, _


def resolve_country(country: str) -> Optional[str]:
    """
    Resolve an alpha-2 code, an alpha-3 code or a registered alias to the alpha-3 code.

    The match ignores the letter case but nothing else: surrounding whitespace, non-ASCII look-alikes and anything
    that isn't a ``str`` give ``None``. This function never raises and imports no country module.

    :param country: an ISO 3166-1 alpha-2 or alpha-3 code, or a registered alias, such as ``'tw'`` or ``'TWN'``.
    :return: the upper-case alpha-3 code, such as ``'TWN'``, or ``None`` when the country is unknown.
    """
    if not isinstance(country, str) or not country.isascii():
        return None
    return _KEYS.get(country.upper())


def get_country(country: str) -> Optional[CountryEntry]:
    """
    Look up a country by its alpha-2 code, alpha-3 code or a registered alias.

    A built-in country module is imported on its first lookup, and only that module. This function never raises
    for a bad argument.

    :param country: an ISO 3166-1 alpha-2 or alpha-3 code, or a registered alias, in any letter case.
    :return: the :class:`CountryEntry` of the country, or ``None`` when the country is unknown.
    """
    alpha3 = resolve_country(country)
    if alpha3 is None:
        return None
    return _entry(alpha3)


def get_validator(country: str) -> Optional[Type[Any]]:
    """
    Return the ``NationalID`` class of a country, which has the static ``validate()`` method.

    :param country: an ISO 3166-1 alpha-2 or alpha-3 code, or a registered alias, in any letter case.
    :return: the ``NationalID`` class of the country, or ``None`` when the country is unknown.
    """
    entry = get_country(country)
    return None if entry is None else entry.national_id


def list_supported_countries() -> List[CountryEntry]:
    """
    List every country of the registry, the built-in ones and the registered ones.

    This imports every built-in country module.

    :return: a new list of :class:`CountryEntry`, sorted by the alpha-3 code.
    """
    with _LOCK:
        return [_entry(alpha3) for alpha3 in sorted(set(_BUILTIN) | set(_CUSTOM))]


def register(
    alpha3: str,
    validator: Type[Any],
    *,
    alpha2: Optional[str] = None,
    name: Optional[str] = None,
    aliases: Sequence[str] = (),
) -> None:
    """
    Add a country to the process-wide registry.

    The call is atomic: when it raises, the registry is unchanged. A registered country can't be removed. Calling
    it again with exactly the same arguments does nothing, and so does registering a built-in country with its own
    ``NationalID``. Any other attempt to change a built-in or an earlier registration raises ``ValueError``.

    :param alpha3: the 3-letter code of the country, which becomes the key of the entry. It is stored in upper case.
    :param validator: a class with a ``METADATA`` attribute and a static ``validate()`` method.
    :param alpha2: the 2-letter code of the country. It defaults to ``validator.METADATA.iso3166_alpha2``.
    :param name: the English name of the country. It defaults to the upper-case ``alpha3``.
    :param aliases: extra lookup keys of the country, such as a legacy code. Each one is stored in upper case.
    :raises TypeError: when ``validator`` isn't a class with ``METADATA`` and a callable ``validate``, when a code, the
        name or an alias isn't a ``str``, or when ``aliases`` is a single ``str``.
    :raises ValueError: when a code, the name or an alias is malformed, when a key is repeated, or when a key is
        already taken by another country or the registration conflicts with an earlier one.
    """
    _check_types(alpha3, validator, alpha2, name, aliases)
    if not _is_code(alpha3, 3):
        raise ValueError(f'alpha3 must be exactly 3 ASCII letters, got {alpha3!r}')
    key3 = alpha3.upper()
    code2 = alpha2 if alpha2 is not None else getattr(validator.METADATA, 'iso3166_alpha2', None)
    if not isinstance(code2, str) or not _is_code(code2, 2):
        raise ValueError(f'alpha2 must be exactly 2 ASCII letters, got {code2!r} for {key3}')
    key2 = code2.upper()
    if name is not None and not name:
        raise ValueError(f'the name of {key3} must not be empty')
    keys_of_aliases = tuple(_alias_key(key3, alias) for alias in aliases)
    all_keys = (key3, key2) + keys_of_aliases
    for key in all_keys:
        if all_keys.count(key) > 1:
            raise ValueError(f'the code {key!r} is repeated in the registration of {key3}')

    with _LOCK:
        if key3 in _BUILTIN:
            _check_builtin_noop(key3, validator, key2, name, keys_of_aliases)
            return
        resolved_name = key3 if name is None else name
        if key3 in _CUSTOM:
            _check_custom_noop(key3, validator, key2, resolved_name, keys_of_aliases)
            return
        for key in all_keys:
            owner = _KEYS.get(key)
            if owner is not None and owner != key3:
                raise ValueError(f'the code {key!r} of {key3} is already used by {owner}')
        _ENTRIES[key3] = CountryEntry(key3, key2, resolved_name, validator, (validator,))
        _CUSTOM[key3] = keys_of_aliases
        for key in all_keys:
            _KEYS[key] = key3


def _entry(alpha3: str) -> CountryEntry:
    """Return the entry of a known alpha-3 code, importing the country module when it isn't loaded yet."""
    entry = _ENTRIES.get(alpha3)
    if entry is not None:
        return entry
    with _LOCK:
        # Another thread may have loaded it while this one waited for the lock.
        return _ENTRIES.setdefault(alpha3, _ENTRIES.get(alpha3) or _load_builtin(alpha3))


def _load_builtin(alpha3: str) -> CountryEntry:
    """Import ``idnumbers.nationalid.<alpha3>`` and describe it."""
    alpha2, name = _BUILTIN[alpha3]
    module = importlib.import_module('idnumbers.nationalid.' + alpha3)
    id_types = tuple(dict.fromkeys(obj for obj in vars(module).values() if _is_id_type(obj)))
    return CountryEntry(alpha3, alpha2, name, module.NationalID, id_types)


def _is_id_type(obj: object) -> bool:
    """Whether ``obj`` is an ID class of a country module, which has ``METADATA`` and is not an alias."""
    metadata = getattr(obj, 'METADATA', None)
    return isinstance(obj, type) and metadata is not None and getattr(metadata, 'alias_of', None) is None


def _is_code(code: str, length: int) -> bool:
    """Whether ``code`` is exactly ``length`` ASCII letters."""
    return len(code) == length and code.isascii() and code.isalpha()


def _check_types(alpha3: object, validator: object, alpha2: object, name: object, aliases: Any) -> None:
    """Raise ``TypeError`` for an argument of :func:`register` that has the wrong type."""
    if not isinstance(alpha3, str):
        raise TypeError(f'alpha3 must be a str, got {type(alpha3).__name__}')
    if not isinstance(validator, type) or not hasattr(validator, 'METADATA'):
        raise TypeError(f'the validator of {alpha3} must be a class with a METADATA attribute, got {validator!r}')
    if not callable(getattr(validator, 'validate', None)):
        raise TypeError(f'the validator of {alpha3} must have a callable validate attribute, got {validator!r}')
    if alpha2 is not None and not isinstance(alpha2, str):
        raise TypeError(f'alpha2 of {alpha3} must be a str, got {type(alpha2).__name__}')
    if name is not None and not isinstance(name, str):
        raise TypeError(f'the name of {alpha3} must be a str, got {type(name).__name__}')
    if isinstance(aliases, str):
        raise TypeError(f'aliases of {alpha3} must be a sequence of str, not the single str {aliases!r}')
    for alias in aliases:
        if not isinstance(alias, str):
            raise TypeError(f'an alias of {alpha3} must be a str, got {type(alias).__name__}')


def _alias_key(alpha3: str, alias: str) -> str:
    """Validate an alias of ``alpha3`` and return its upper-case lookup key."""
    if not alias or not alias.isascii() or any(char.isspace() for char in alias):
        raise ValueError(f'an alias of {alpha3} must be non-empty ASCII without whitespace, got {alias!r}')
    return alias.upper()


def _check_builtin_noop(
    alpha3: str, validator: Type[Any], alpha2: str, name: Optional[str], aliases: Tuple[str, ...]
) -> None:
    """Accept only the registration that repeats a built-in country exactly, raise ``ValueError`` otherwise."""
    entry = _entry(alpha3)
    if validator is not entry.national_id or alpha2 != entry.alpha2 or name not in (None, entry.name) or aliases:
        raise ValueError(f'{alpha3} is a built-in country and can be neither replaced nor widened')


def _check_custom_noop(
    alpha3: str, validator: Type[Any], alpha2: str, name: str, aliases: Tuple[str, ...]
) -> None:
    """Accept only the registration that repeats an earlier one exactly, raise ``ValueError`` otherwise."""
    entry = _ENTRIES[alpha3]
    same_aliases: Set[str] = set(_CUSTOM[alpha3])
    if (
        validator is not entry.national_id
        or alpha2 != entry.alpha2
        or name != entry.name
        or same_aliases != set(aliases)
    ):
        raise ValueError(f'{alpha3} is already registered with different arguments')
