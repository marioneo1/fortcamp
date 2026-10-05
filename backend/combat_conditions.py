"""Small persistent status rules; random choices are seeded by activation."""
import random
from copy import deepcopy
from .combat_feedback import record as feedback

CONTROL = {'stun', 'sleep', 'freeze', 'paralyze'}
RECOVERY = CONTROL | {'bind'}

def has(unit, sid):
    return any(s.get('id') == sid for s in unit.get('statuses', []))

def remove(unit, *ids):
    unit['statuses'] = [s for s in unit.get('statuses', []) if s.get('id') not in ids]

def apply(unit, sid, turns, source=None):
    if sid in (RECOVERY if unit.get('status_version') else CONTROL) and unit.get('control_immunity', 0) > 0:
        return False
    if unit.get('status_version') and sid in RECOVERY and any(has(unit,s) for s in RECOVERY):
        return False
    remove(unit, sid)
    status = {'id': sid, 'turns': max(1, min(3, int(turns))),
              'applied_activation': unit.get('status_activation')}
    if unit.get('boss') or unit.get('kind') == 'chieftain':
        if sid in (RECOVERY if unit.get('status_version') else CONTROL):
            status['turns'] = 1
    if source:
        status.update(source_id=source.get('id'), source_name=source.get('name'), source_weapon=source.get('weapon'))
    if unit.get('status_version'):
        status['expiry'] = 'target_start' if sid in {'poison','burn'} else 'target_end'
        status['applied_activation'] = deepcopy(unit.get('status_activation'))
    unit.setdefault('statuses', []).append(status)
    return True

def start_activation(battle, unit):
    """Called once by the engine's persistent activation stamp."""
    unit.pop('paralyzed_move', None)
    unit.pop('forced_skip', None)
    unit['control_immunity'] = max(0, int(unit.get('control_immunity', 0)) - 1)
    if unit.get('status_version'):
        unit['reaction_ready'] = True
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
            feedback(battle,unit,'heal',amount)
            battle['log'].append(f"{unit['name']} recovers {amount} HP from regeneration.")

def finish_activation(unit):
    stamp=unit.get('status_activation')
    if unit.get('status_version') and stamp is not None:
        if unit.get('status_finished_stamp')==stamp:return
        unit['status_finished_stamp']=deepcopy(stamp)
    for status in list(unit.get('statuses', [])):
        if status.get('id') in {'burn', 'poison', 'ambush_sleep'} or 'turns' not in status:
            continue
        if status.get('applied_activation') == unit.get('status_activation'):
            continue
        status['turns'] -= 1
        if status['turns'] <= 0:
            unit['statuses'].remove(status)
            if status['id'] in (RECOVERY if unit.get('status_version') else CONTROL):
                unit['control_immunity'] = 2


def barrier(unit, amount, turns, source):
    """One finite shield. A smaller recast cannot extend a stronger shield."""
    current=next((s for s in unit.get('statuses',[]) if s['id']=='barrier'),None)
    if current and current.get('amount',0)>amount:
        return False
    apply(unit,'barrier',turns,source)
    next(s for s in unit['statuses'] if s['id']=='barrier')['amount']=amount
    return True


def absorb(unit, damage):
    shield=next((s for s in unit.get('statuses',[]) if s['id']=='barrier'),None)
    absorbed=min(damage,shield.get('amount',0)) if shield else 0
    if absorbed:
        shield['amount']-=absorbed
        if shield['amount']<=0:remove(unit,'barrier')
    return damage-absorbed,absorbed


def mark(battle, source, target, turns, accuracy=10):
    # One target per owner; different owners can mark the same target.
    for unit in battle['units'].values():
        unit['statuses']=[s for s in unit.get('statuses',[]) if not (s['id']=='mark' and s.get('source_id')==source['id'])]
    target.setdefault('statuses',[]).append({'id':'mark','source_id':source['id'],'source_name':source['name'],
        'turns':turns,'accuracy':accuracy,'expiry':'target_end',
        'applied_activation':deepcopy(target.get('status_activation'))})


def mark_bonus(attacker,target):
    if attacker.get('reaction_attack') or ('mark_hit_activation' in attacker and attacker['mark_hit_activation']==attacker.get('status_activation')):
        return 0
    return max((s.get('accuracy',10) for s in target.get('statuses',[]) if s['id']=='mark' and s.get('source_id')==attacker.get('id')),default=0)

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
