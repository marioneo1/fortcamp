"""Offline structural checks for draft blueprints; never imports content or saves."""
import argparse
import json
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / 'docs/content/character-story-contract-v0.2.json'


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def read_json(path):
    def reject_constant(value):
        raise ValueError(f'Invalid JSON number: {value}')
    return json.loads(Path(path).read_text(encoding='utf-8-sig'),
                      object_pairs_hook=unique_object, parse_constant=reject_constant)


def walk(value, path='$'):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, f'{path}.{key}')
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f'{path}[{index}]')


def validate(data, contract, baseline=None):
    errors, warnings = [], []

    def fail(path, message):
        errors.append(f'{path}: {message}')

    def required(value, keys, path):
        if not isinstance(value, dict):
            fail(path, 'must be an object')
            return False
        for key in keys:
            if key not in value:
                fail(path, f'missing {key}')
        return True

    if not required(data, contract['output_contract']['top_level_required'], '$'):
        return errors, warnings
    if data.get('schema_version') != contract['schema_version']:
        fail('$.schema_version', 'does not match this authoring contract')
    if data.get('content_type') != 'character_blueprint':
        fail('$.content_type', 'this checker supports character_blueprint only')
    if not isinstance(data.get('batch_id'), str) or not data['batch_id']:
        fail('$.batch_id', 'must be a nonempty string')
    entries = data.get('entries')
    if not isinstance(entries, list) or not entries:
        fail('$.entries', 'must be a nonempty array')
        return errors, warnings
    ids = {}
    for path, value in walk(data):
        if not isinstance(value, dict):
            continue
        if 'id' in value:
            ident = value['id']
            if not isinstance(ident, str) or not ident:
                fail(path + '.id', 'must be a nonempty string')
            elif ident in ids:
                fail(path + '.id', f'duplicate ID {ident}')
            else:
                ids[ident] = path
        if 'starts_revealed' in value and type(value['starts_revealed']) is not bool:
            fail(path + '.starts_revealed', 'must be boolean')
        if 'review_required' in value and value['review_required'] is not True:
            fail(path + '.review_required', 'must be true for draft proposals')
        if 'repeat_key' in value:
            for key in ('repeat_key', 'scope', 'max_offers', 'retry'):
                if key not in value:
                    fail(path, f'missing {key}')
            if type(value.get('max_offers')) is not int or value['max_offers'] < 1:
                fail(path + '.max_offers', 'must be a positive integer')
            if value.get('scope') not in ('player', 'character'):
                fail(path + '.scope', 'must be player or character')
        if 'field' in value and 'op' in value:
            field, op = value['field'], value['op']
            fields = contract['predicate_contract']['fields']
            if not isinstance(field, str) or field not in fields or op not in fields[field]:
                fail(path, 'unregistered predicate field/operator; use a proposal')
            if 'value' not in value or value['value'] is None:
                fail(path + '.value', 'predicate requires a concrete value')
            elif field in ('speaker.conscious', 'target.present', 'target.known',
                           'target.hostile', 'target.living', 'target.blood_eligible'):
                if type(value['value']) is not bool:
                    fail(path + '.value', 'must be boolean')
            elif op in ('in', 'has_any') and not isinstance(value['value'], list):
                fail(path + '.value', 'operator requires an array')
        if 'prospective_loyalty_cap' in value and value['prospective_loyalty_cap'] is not None:
            cap = value['prospective_loyalty_cap']
            if required(cap, ('value', 'when', 'disclosed_before', 'cause',
                              'lift_condition', 'review_required'), path + '.prospective_loyalty_cap'):
                if type(cap.get('value')) is not int or not 0 <= cap['value'] <= 100:
                    fail(path + '.prospective_loyalty_cap.value', 'must be an integer from 0 to 100')
                warnings.append(f'{path}: loyalty-cap allocation and recovery need human review')

    shapes = contract['output_contract']['character_blueprint_shapes']
    refs = {'next', 'to', 'facet_id', 'reward_contract_id', 'core_facet_ids',
            'intro_reveal_ids', 'reward_contract_ids'}
    catalog = contract['existing_ids']
    for index, entry in enumerate(entries):
        path = f'$.entries[{index}]'
        if not required(entry, contract['output_contract']['character_blueprint_entry_required'], path):
            continue
        entry_id = entry.get('id')
        local_ids = {value['id'] for _, value in walk(entry)
                     if isinstance(value, dict) and isinstance(value.get('id'), str)}
        if not isinstance(entry_id, str):
            continue
        for ident in local_ids:
            if ident != entry_id and not ident.startswith(entry_id + '.'):
                fail(path, f'local ID outside entry namespace: {ident}')
        for section, shape in shapes.items():
            if not isinstance(shape, dict):
                continue
            value = entry.get(section)
            if 'required_per_item' in shape:
                if not isinstance(value, list):
                    fail(path + '.' + section, 'must be an array')
                else:
                    for j, item in enumerate(value):
                        required(item, shape['required_per_item'], f'{path}.{section}[{j}]')
            elif 'required' in shape:
                required(value, shape['required'], path + '.' + section)
        identity = entry.get('identity', {})
        if isinstance(identity, dict):
            for key, known in (('races', catalog['races']), ('genders', catalog['genders']),
                               ('base_personalities', catalog['personalities']), ('jobs', catalog['jobs'])):
                values = identity.get(key)
                if not isinstance(values, list) or any(v not in known for v in values):
                    fail(path + '.identity.' + key, 'must be an array of existing IDs')
        for item_path, value in walk(entry, path):
            if not isinstance(value, dict):
                continue
            for key in refs & value.keys():
                targets = value[key] if isinstance(value[key], list) else [value[key]]
                for target in targets:
                    if not isinstance(target, str) or target not in local_ids | {'end'}:
                        fail(item_path + '.' + key, f'unresolved local reference: {target!r}')
        routes = entry.get('routing')
        if not isinstance(routes, list) or not routes:
            fail(path + '.routing', 'explicit routing table required by current handoff')
        else:
            for j, route in enumerate(routes):
                route_path = f'{path}.routing[{j}]'
                if required(route, ('from', 'trigger', 'prerequisite', 'to', 'state_effect'), route_path):
                    if not isinstance(route.get('from'), str) or route['from'] not in local_ids | {'introduction'}:
                        fail(route_path + '.from', 'unknown route source')

    decisions = data.get('decision_points', [])
    if not isinstance(decisions, list):
        fail('$.decision_points', 'must be an array')
    else:
        shape = contract['output_contract']['authoring_handoff']['optional_decision_points']
        for i, decision in enumerate(decisions):
            path = f'$.decision_points[{i}]'
            if not required(decision, shape['required_per_item'], path):
                continue
            for key in ('alternatives', 'affected_ids'):
                if not isinstance(decision.get(key), list) or any(not isinstance(v, str) for v in decision[key]):
                    fail(path + '.' + key, 'must be an array of strings')
            if isinstance(decision.get('affected_ids'), list):
                for ref in decision['affected_ids']:
                    if not isinstance(ref, str) or ref not in ids:
                        fail(path + '.affected_ids', f'unknown ID {ref!r}')
            if type(decision.get('blocks_approval')) is not bool:
                fail(path + '.blocks_approval', 'must be boolean')
            if decision.get('blocks_approval'):
                warnings.append(f'{path}: unresolved decision blocks approval')

    review = data.get('self_review')
    if required(review, contract['output_contract']['self_review_required'], '$.self_review'):
        if type(review.get('entry_count')) is not int or review['entry_count'] != len(entries):
            fail('$.self_review.entry_count', 'must match actual entry count')
        for key in contract['output_contract']['self_review_required']:
            if key != 'entry_count' and (not isinstance(review.get(key), list)
                                        or any(not isinstance(v, str) for v in review[key])):
                fail('$.self_review.' + key, 'must be an array of strings')
    if baseline is not None:
        previous_ids = {v['id'] for _, v in walk(baseline)
                        if isinstance(v, dict) and isinstance(v.get('id'), str)}
        for ident in sorted(previous_ids - ids.keys()):
            fail('$', f'baseline ID removed; review retirement explicitly: {ident}')
        if data.get('batch_id') != baseline.get('batch_id'):
            fail('$.batch_id', 'revision must retain baseline batch ID')
        if type(data.get('revision')) is not int or data['revision'] <= baseline.get('revision', 1):
            fail('$.revision', 'must increase from baseline')
        old_keys = [v['repeat_key'] for _, v in walk(baseline)
                    if isinstance(v, dict) and 'repeat_key' in v]
        new_keys = [v['repeat_key'] for _, v in walk(data)
                    if isinstance(v, dict) and 'repeat_key' in v]
        if sorted(old_keys) != sorted(new_keys):
            fail('$', 'revision changed stable repeat keys; explicit review required')
    warnings.append('Structural checks only: conditional reachability, story quality, costs, rewards, '
                    'repeat/cap safety and engine support still require human review. Nothing imported.')
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path)
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    try:
        errors, warnings = validate(read_json(args.file), read_json(CONTRACT),
                                    read_json(args.baseline) if args.baseline else None)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Cannot validate: {exc}\n')
    for error in errors:
        print('ERROR:', error)
    for warning in warnings:
        print('REVIEW:', warning)
    print(f'{len(errors)} structural error(s). Passing is not content approval.')
    raise SystemExit(1 if errors else 0)


if __name__ == '__main__':
    main()
