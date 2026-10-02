"""Small persistent status rules; random choices are seeded by activation."""
import random

CONTROL = {'stun', 'sleep', 'freeze', 'paralyze'}

def has(unit, sid):
    return any(s.get('id') == sid for s in unit.get('statuses', []))

def remove(unit, *ids):
    unit['statuses'] = [s for s in unit.get('statuses', []) if s.get('id') not in ids]

def apply(unit, sid, turns, source=None):
    if sid in CONTROL and unit.get('control_immunity', 0) > 0:
        return False
    remove(unit, sid)
    status = {'id': sid, 'turns': max(1, min(3, int(turns))),
              'applied_activation': unit.get('status_activation')}
    if unit.get('boss') or unit.get('kind') == 'chieftain':
        if sid in CONTROL:
            status['turns'] = 1
    if source:
        status.update(source_id=source.get('id'), source_name=source.get('name'), source_weapon=source.get('weapon'))
    unit.setdefault('statuses', []).append(status)
    return True

def start_activation(battle, unit):
    """Called once by the engine's persistent activation stamp."""
    unit.pop('paralyzed_move', None)
    unit.pop('forced_skip', None)
    unit['control_immunity'] = max(0, int(unit.get('control_immunity', 0)) - 1)
    if has(unit, 'stun') or has(unit, 'sleep'):
        unit['forced_skip'] = True
    if has(unit, 'paralyze'):
        rng = random.Random(f"{battle.get('seed')}:paralyze:{unit['id']}:{unit.get('status_activation')}")
        if rng.random() < .3:
            unit['forced_skip'] = True
        else:
            unit['paralyzed_move'] = True
    if has(unit, 'regeneration') and not has(unit, 'burn'):
        amount = min(max(0, unit['max_hp'] - unit['hp']), max(2, round(unit['max_hp'] * .05)))
        unit['hp'] += amount
        if amount:
            battle['log'].append(f"{unit['name']} recovers {amount} HP from regeneration.")

def finish_activation(unit):
    for status in list(unit.get('statuses', [])):
        if status.get('id') in {'burn', 'poison', 'ambush_sleep'} or 'turns' not in status:
            continue
        if status.get('applied_activation') == unit.get('status_activation'):
            continue
        status['turns'] -= 1
        if status['turns'] <= 0:
            unit['statuses'].remove(status)
            if status['id'] in CONTROL:
                unit['control_immunity'] = 2

def hostile_units(battle, unit, living):
    others = [u for u in living if u['id'] != unit['id']]
    if has(unit, 'berserk') or unit.get('mercenary_hostile_all'):
        return others
    charm = next((s for s in unit.get('statuses', []) if s.get('id') == 'charm'), None)
    source = battle['units'].get(charm.get('source_id')) if charm else None
    team = source.get('team', unit['team']) if source else unit['team']
    return [u for u in others if u['team'] != team or u.get('mercenary_hostile_all')]

def confused_target(battle, attacker, target, in_range):
    if not has(attacker, 'confuse'):
        return target
    rng = random.Random(f"{battle.get('seed')}:confuse:{attacker['id']}:{attacker.get('status_activation')}:{battle.get('roll_counter',0)}")
    others = [u for u in battle['units'].values() if u['id'] != attacker['id'] and u.get('alive')
              and u.get('conscious', True) and not u.get('extracted') and not u.get('carried_by') and in_range(u)]
    if others and rng.random() < .35:
        redirected = rng.choice(others)
        if redirected['id'] != target['id']:
            battle['log'].append(f"{attacker['name']} is confused and targets {redirected['name']} instead.")
        return redirected
    return target
