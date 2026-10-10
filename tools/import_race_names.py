"""Validate submitted names and build a reviewed, self-contained runtime pool."""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
from string import Formatter
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.races import RACE_CATALOG, generated_genders
from tools.build_race_names_brief import build


def normalized(value):
    value = unicodedata.normalize('NFKC', value).translate(str.maketrans({
        '\u2018': "'", '\u2019': "'", '\u2010': '-', '\u2011': '-', '\u2013': '-', '\u2014': '-',
    }))
    return re.sub(r'\s+', ' ', value.strip()).casefold()


def compile_pools(folder):
    registry = json.loads(build().split('## Complete race registry, batch manifest and exclusions')[1].split('```json')[1].split('```')[0])
    excluded = {normalized(n) for n in registry['excluded_existing_tokens']}
    protected = {normalized(n) for n in registry['protected_named_identities']}
    entries, errors, warnings, removed, sources = {}, [], [], [], []
    cross_race = defaultdict(set)
    for batch in registry['batches']:
        path = Path(folder) / (batch['batch_id'] + '.json')
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        if data.get('schema_version') != 'names-0.1' or data.get('batch_id') != batch['batch_id']:
            errors.append(f'{path.name}: invalid schema/batch')
        if [e['race_id'] for e in data['entries']] != batch['races']:
            errors.append(f'{path.name}: race manifest mismatch')
        sources.append({'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        for entry in data['entries']:
            race = entry['race_id']
            if race not in RACE_CATALOG or race in entries:
                errors.append(f'{race}: unknown or repeated race'); continue
            if entry['allowed_genders'] != list(generated_genders(race)):
                errors.append(f'{race}: gender mismatch')
            if entry['naming_style'] not in {'gendered', 'shared'}:
                errors.append(f'{race}: invalid naming style')
            if entry['convention_basis'] not in {'verified_dnd', 'dnd_inspired', 'original_proposal'}:
                errors.append(f'{race}: invalid convention basis')
            seen_given = set()
            for kind, keys, limit in [
                ('given_names', ('male', 'female', 'shared'), 18),
                ('leader_given_names', ('male', 'female', 'shared'), 18),
                ('second_names', ('family', 'clan', 'byname', 'designation'), 22),
            ]:
                if set(entry[kind]) != set(keys): errors.append(f'{race}: invalid {kind} keys')
                seen_second = set()
                for pool in keys:
                    clean = []
                    for value in entry[kind].get(pool, []):
                        if not isinstance(value, str) or not value.strip() or len(value.strip()) > limit or any(ord(c) < 32 for c in value):
                            errors.append(f'{race}: invalid {kind}/{pool} value'); continue
                        value = value.strip(); key = normalized(value)
                        seen = seen_second if kind == 'second_names' else seen_given
                        if key in excluded or key in protected or key in seen:
                            removed.append({'race': race, 'pool': f'{kind}/{pool}', 'value': value}); continue
                        seen.add(key); clean.append(value)
                        if kind != 'second_names': cross_race[key].add(race)
                    entry[kind][pool] = clean
            for gender in ('male', 'female'):
                if gender not in entry['allowed_genders'] and (entry['given_names'][gender] or entry['leader_given_names'][gender]):
                    errors.append(f'{race}: disallowed gender pool')
            for gender in entry['allowed_genders']:
                for kind in ('given_names', 'leader_given_names'):
                    if not (entry[kind][gender] or entry[kind]['shared']): errors.append(f'{race}: missing {gender}/{kind}')
            for key, context_key in [('leader_titles', 'role_context'), ('epithets', 'requires_context')]:
                seen = set()
                for record in entry[key]:
                    value = record.get('text', '')
                    if not isinstance(value,str) or not value.strip() or len(value) > 24 or not record.get(context_key):
                        errors.append(f'{race}: invalid {key} record')
                    if normalized(value) in seen: errors.append(f'{race}: repeated {key}')
                    seen.add(normalized(value))
                    if key == 'leader_titles' and record.get('gender') not in {*entry['allowed_genders'], 'any'}:
                        errors.append(f'{race}: invalid title gender')
            for kind in ('ordinary_formats', 'leader_formats'):
                formats = entry[kind]
                if not formats: errors.append(f'{race}: missing {kind}')
                for fmt in formats:
                    try:
                        parts = list(Formatter().parse(fmt))
                        if any(spec or conversion for _, _, spec, conversion in parts): raise ValueError('unsupported conversion')
                        fields = [field for _, field, _, _ in parts if field is not None]
                        if '{given}' not in fmt or set(fields) - {'given','family','clan','byname','designation','title','epithet'}:
                            raise ValueError('unsupported format')
                        for field in fields:
                            if field in entry['second_names'] and not entry['second_names'][field]: raise ValueError('empty pool')
                    except (ValueError, TypeError): errors.append(f'{race}: invalid {kind} format')
                if not any('{title}' not in f and '{epithet}' not in f for f in formats): errors.append(f'{race}: no context-free {kind}')
            entries[race] = entry
    if set(entries) != set(RACE_CATALOG): errors.append('Incomplete catalogue')
    overlap = {token: sorted(races) for token, races in cross_race.items() if len(races) > 1}
    if overlap: warnings.append(f'{len(overlap)} given-name tokens shared across races; permitted, full names checked locally at generation')
    totals = {kind: sum(len(values) for e in entries.values() for values in e[kind].values()) for kind in ('given_names','leader_given_names','second_names')}
    report = {'sources': sources, 'races': len(entries), 'totals': totals, 'removed': removed, 'errors': errors, 'warnings': warnings, 'cross_race_overlap': overlap,
              'source_note': 'Submitted style/source claims retained as author metadata, not independently verified D&D lore.',
              'context_policy': 'Titles/epithets require explicit matching known context; ordinary integration uses context-free formats.'}
    if errors: raise ValueError('\n'.join(errors))
    return {'version': 1, 'protected_names': sorted(registry['protected_named_identities']), 'races': entries}, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data, report = compile_pools(ROOT/'docs/content/drafts/names')
    path = ROOT/'backend/name_pools/race_names.json'
    text = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if args.check:
        if not path.exists() or path.read_text(encoding='utf-8') != text: raise SystemExit('Runtime names are stale; run importer')
    else:
        path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding='utf-8')
        (ROOT/'docs/content/reviews/RACE_NAMES_IMPORT.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('races','totals','errors','warnings')}, ensure_ascii=False))


if __name__ == '__main__': main()
