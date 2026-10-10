"""Gender-compatible, deterministic names for newly generated people only."""
from functools import lru_cache
import json
from pathlib import Path
import random
import re
import unicodedata


def name_key(value):
    value = unicodedata.normalize('NFKC', value).translate(str.maketrans({
        '\u2018': "'", '\u2019': "'", '\u2010': '-', '\u2011': '-', '\u2013': '-', '\u2014': '-',
    }))
    return re.sub(r'\s+', ' ', value.strip()).casefold()


@lru_cache(maxsize=1)
def catalogue():
    return json.loads((Path(__file__).parent/'name_pools/race_names.json').read_text(encoding='utf-8'))


def name_rng(rng):
    """Keep naming choices from changing stat/loot rolls on the caller's RNG."""
    return random.Random(repr(rng.getstate()))


def generate_name(race, gender, rng, *, leader=False, used_names=(), role_context=None, epithet_context=None):
    data = catalogue(); entry = data['races'][race]
    if gender not in entry['allowed_genders']:
        raise ValueError(f'{race} does not allow gender {gender}')
    given_pool = entry['leader_given_names'] if leader else entry['given_names']
    given = given_pool[gender] + given_pool['shared']
    titles = [r['text'] for r in entry['leader_titles'] if r['role_context'] == role_context and r['gender'] in {gender,'any'}] if leader else []
    epithets = [r['text'] for r in entry['epithets'] if r['requires_context'] == epithet_context] if leader else []
    formats = [f for f in entry['leader_formats' if leader else 'ordinary_formats']
               if ('{title}' not in f or titles) and ('{epithet}' not in f or epithets)]
    # Most people receive a second component, while single-name traditions remain possible.
    extended = [f for f in formats if f != '{given}']
    unavailable = {name_key(n) for n in (*used_names, *data['protected_names'])}
    for _ in range(128):
        fmt = rng.choice(extended if extended and rng.random() < .8 else formats)
        parts = {'given': rng.choice(given)}
        for key, pool in entry['second_names'].items():
            if '{'+key+'}' in fmt: parts[key] = rng.choice(pool)
        if '{title}' in fmt: parts['title'] = rng.choice(titles)
        if '{epithet}' in fmt: parts['epithet'] = rng.choice(epithets)
        candidate = fmt.format(**parts)
        if len(candidate) <= 48 and name_key(candidate) not in unavailable:
            return candidate
    # Bounded fallback: never invent serial-number names or loop on a crowded pool.
    for first in given:
        for key, pool in entry['second_names'].items():
            for second in pool:
                fmt = next((f for f in formats if f in {'{given} {'+key+'}', '{'+key+'} {given}'}), None)
                if fmt:
                    candidate = fmt.format(given=first, **{key:second})
                    if len(candidate) <= 48 and name_key(candidate) not in unavailable: return candidate
        if name_key(first) not in unavailable: return first
    raise ValueError(f'No unused {race} names remain in this local group')
