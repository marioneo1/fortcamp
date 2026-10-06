"""Monk sequence state. Uses existing personal-turn clocks, never wall time."""
import random
from . import combat_conditions as conditions
from .combat_feedback import record as feedback


def has_passive(unit, key):
    return any(p.get('id') == 'job:monk:' + key for p in unit.get('passives', []))


def clock(unit):
    return int(unit.get('ability_activation', 0))


def readiness(unit):
    state = unit.get('monk_combo', {})
    now = clock(unit)
    stage = state.get('stage', 'neutral')
    if now > state.get('expires_at', -1):
        stage = 'neutral'
    return {'stage': stage, 'available': stage != 'neutral' and now >= state.get('available_at', 0),
            'turns_remaining': max(0, state.get('expires_at', now) - now + 1) if stage != 'neutral' else 0}


def restriction(unit, skill):
    required = skill.get('combo_stage')
    if not required:
        return None
    state = readiness(unit)
    label = {'follow_up': 'Follow-up Ready', 'finisher': 'Finisher Ready'}[required]
    if state['stage'] != required:
        return 'Requires ' + label
    return None if state['available'] else label + ' is available next turn'


def accuracy(unit, skill):
    if not skill or not has_passive(unit, 'perfect_rhythm') or restriction(unit, skill):
        return 0, False
    if skill.get('combo_stage') == 'finisher':
        return 0, True
    return (10, False) if skill.get('combo_stage') == 'follow_up' else (0, False)


def evasion_against(unit, attacker):
    return 25 if any(s['id']=='iron_reversal_evasion' and s.get('enemy_id')==attacker.get('id') for s in unit.get('statuses',[])) else 0


def parry_rate(unit,attacker,rule,skill=None):
    physical=rule in {'melee','ballistic'} and not (skill or {}).get('element',attacker.get('element'))
    area=any(e.get('type') in {'area_attack','leap_attack','dash_attack'} or e.get('radius') for e in (skill or {}).get('effects',[]))
    return 10 if physical and not area and conditions.has(unit,'dash_parry') else 0


def landed_attack(battle,source):
    if not direct_attack(source):return
    actor=battle.get('units',{}).get(source.get('id'))
    if not actor or not conditions.has(actor,'monk_siphon') or actor.get('alive') is False or actor.get('conscious') is False:return
    amount=min(3,max(0,actor['max_hp']-actor['hp']))
    if amount:
        actor['hp']+=amount;feedback(battle,actor,'heal',amount)
        battle['log'].append(f"{actor['name']} recovers {amount} HP from Combat Rhythm.")


def add_exposure(battle,actor,target,packet):
    if target.get('alive') is False or target.get('conscious') is False:return
    previous=next((s for s in target.get('statuses',[]) if s['id']=='palm_exposure'),{})
    stacks=min(3,previous.get('stacks',0)+1)
    if conditions.apply(target,'palm_exposure',3,actor):
        next(s for s in target['statuses'] if s['id']=='palm_exposure')['stacks']=stacks
        feedback(battle,target,'status',status_id='palm_exposure',attack_packet=packet)
    from . import combat_martial
    combat_martial.flush(battle,target)


def evasion_bonus(unit):
    return 10 if any(s['id'] == 'flowing_footwork' and clock(unit) <= s.get('expires_at', -1)
                     for s in unit.get('statuses', [])) else 0


def movement_bonus(unit):
    return 1 if any(s['id'] == 'flowing_footwork' and clock(unit) == s.get('expires_at')
                    for s in unit.get('statuses', [])) else 0


def direct_attack(source):
    return not any(source.get(k) for k in ('status_tick', 'environmental_fall', 'collision_attack', 'ground_damage'))


def incoming(target, source, amount):
    if not direct_attack(source):
        return amount
    exposure=next((s.get('stacks',0) for s in target.get('statuses',[]) if s['id']=='palm_exposure'),0)
    bonus=(.25 if conditions.has(target,'open_guard') else 0)+.1*exposure
    if bonus:amount=max(1,round(amount*(1+bonus)))
    if conditions.has(target, 'iron_reversal'):
        conditions.remove(target, 'iron_reversal')
        amount = max(1, round(amount * .8))
    return amount


def start_activation(battle, unit):
    # This is called by the existing activation stamp, including skipped turns.
    conditions.remove(unit, 'iron_reversal','iron_reversal_evasion','dash_parry')
    cleanup(battle)


def cleanup(battle, ending_unit=None):
    complete = battle.get('status') == 'complete'
    for unit in battle.get('units', {}).values():
        if complete or unit.get('alive') is False or unit.get('conscious') is False or unit.get('extracted'):
            unit.pop('monk_combo', None)
            conditions.remove(unit, 'iron_reversal', 'iron_reversal_evasion', 'flowing_footwork','monk_siphon','dash_parry')
        elif clock(unit) > unit.get('monk_combo', {}).get('expires_at', clock(unit)):
            unit.pop('monk_combo', None)
        if ending_unit is unit:
            if clock(unit) >= unit.get('monk_combo', {}).get('expires_at', clock(unit) + 1):
                unit.pop('monk_combo', None)
            for status in list(unit.get('statuses', [])):
                if status['id'] in {'flowing_footwork','monk_siphon'} and clock(unit) >= status['expires_at']:
                    conditions.remove(unit, status['id'])
        for status in list(unit.get('statuses', [])):
            if status['id'] != 'open_guard':
                continue
            owner = battle['units'].get(status.get('source_id'))
            if (complete or not owner or owner.get('alive') is False or owner.get('conscious') is False
                    or owner.get('extracted') or clock(owner) > status['expires_at']
                    or ending_unit is owner and clock(owner) >= status['expires_at']):
                conditions.remove(unit, 'open_guard')


def _status(unit, key, expires_at, source):
    conditions.remove(unit, key)
    unit.setdefault('statuses', []).append({'id': key, 'expiry': 'source_end' if key == 'open_guard' else 'owner_end',
        'expires_at': expires_at, 'source_id': source['id'], 'source_name': source.get('name', '')})


def complete_technique(battle, actor, target, skill, hits, packet):
    category = skill.get('combo_kind')
    if not category:
        return
    previous = readiness(actor)['stage']
    if category == 'finisher':
        actor.pop('monk_combo', None)
        return
    advanced = bool(hits)
    if category == 'opener':
        actor.pop('monk_combo', None)
        chance = (100 if hits >= 2 else 80) if skill['id'].endswith(':rapid_palm') else 70
        count = battle.get('combo_roll_counter', 0)
        battle['combo_roll_counter'] = count + 1
        advanced = bool(hits) and random.Random(f"{battle.get('seed')}:combo:{count}:{actor['id']}").randint(1, 100) <= chance
    if not advanced or actor.get('conscious') is False or actor.get('alive') is False:
        return
    stage = 'follow_up' if category == 'opener' else 'finisher'
    now = clock(actor)
    actor['monk_combo'] = {'stage': stage, 'available_at': now + 1, 'expires_at': now + 2}
    feedback(battle, actor, 'combo', stage=stage, attack_packet=packet)
    if stage != previous and has_passive(actor, 'flowing_footwork'):
        _status(actor, 'flowing_footwork', now + 1, actor)
        feedback(battle, actor, 'status', status_id='flowing_footwork', attack_packet=packet)
    if skill['id'].endswith(':crushing_fist') and target.get('alive',True) and target.get('conscious',True):
        count=battle.get('monk_stun_counter',0);battle['monk_stun_counter']=count+1
        chance=conditions.status_chance(target,'stun',50)
        if random.Random(f"{battle.get('seed')}:monk-stun:{count}:{actor['id']}").randint(1,100)<=chance and conditions.apply(target,'stun',1,actor):
            feedback(battle,target,'status',status_id='stun',attack_packet=packet)
    if skill['id'].endswith(':iron_reversal'):
        _status(actor, 'iron_reversal', now + 1, actor)
        _status(actor,'iron_reversal_evasion',now+1,actor)
        evasion=next(s for s in actor['statuses'] if s['id']=='iron_reversal_evasion')
        evasion.update(enemy_id=target['id'],enemy_name=target.get('name','the struck enemy'))
        feedback(battle, actor, 'status', status_id='iron_reversal', attack_packet=packet)
    if skill['id'].endswith(':breaking_combination'):
        _status(actor,'monk_siphon',now+3,actor)
        feedback(battle,actor,'status',status_id='monk_siphon',attack_packet=packet)
    if skill['id'].endswith(':breaking_combination') and target.get('conscious', True) and target.get('alive', True):
        _status(target, 'open_guard', now + 1, actor)
        from . import combat_martial
        combat_martial.try_unstoppable(target)
        if conditions.has(target, 'open_guard'):
            feedback(battle, target, 'status', status_id='open_guard', attack_packet=packet)
        combat_martial.flush(battle, target)


def view(unit, battle):
    state = readiness(unit)
    if unit.get('job_id') == 'monk' or any(s.get('combo_kind') for s in unit.get('skills', [])):
        unit['combo'] = state
    for status in unit.get('statuses', []):
        if status['id'] in {'iron_reversal','iron_reversal_evasion','flowing_footwork','open_guard','monk_siphon','dash_parry'}:
            owner = battle['units'].get(status.get('source_id'), unit)
            status['turns'] = max(0, status.get('expires_at', clock(owner)) - clock(owner) + 1)
