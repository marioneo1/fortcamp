"""Bounded martial passives; shares resolved damage and owner activation clocks."""
from .combat_feedback import record as feedback

HARMFUL = ('disarm','captor_held','stun','freeze','sleep','paralyze','bind','charm','confuse','fear','mute',
           'blind','hobbled','slow','armor_fracture','vulnerable','open_guard','palm_exposure','poison','burn','bleed')


def effect(battle, unit, skill, packet=None, before_contact=False):
    event = {'type':'martial_effect','unit_id':unit['id'],'x':unit['x'],'y':unit['y'],'skill':skill}
    if packet is not None:
        event.update(attack_packet=packet,before_contact=before_contact)
    battle.setdefault('animation_events',[]).append(event)


def has_passive(unit, name):
    return any(p.get('id') == 'job:barbarian:'+name for p in unit.get('passives', []))


def passive_availability(unit, passive):
    key=passive['id'].split(':')[-1]
    clock=unit.get('ability_activation',0)
    state=unit.get('martial_state',{})
    if key in {'bloodthirst','unstoppable'}:
        active=key=='bloodthirst' and state.get('bloodthirst_window')==clock
        remaining=max(0,state.get(key+'_ready',0)-clock)
        return {'ready':active or remaining==0,'active_window':active,'cooldown_remaining':remaining if not active else 0}
    if key=='too_angry_to_fall':
        active=unit.get('angry_until') is not None
        return {'ready':active or not unit.get('angry_used',False),'active_window':active,'spent':bool(unit.get('angry_used')) and not active,'cooldown_remaining':0}
    if passive.get('reaction'):
        from .combat_tactics import reaction_available
        return {'ready':bool(reaction_available(unit)),'cooldown_remaining':0 if reaction_available(unit) else 1}
    return None


def attack_power(unit):
    base = int(unit.get('attack', 0))
    if any(s.get('id')=='pestilence' for s in unit.get('statuses',[])):base=max(1,round(base*.75))
    if not has_passive(unit, 'bloodied_strength'):
        return base
    maximum = max(1, int(unit.get('max_hp', 1)))
    loss = max(0, min(maximum-1, maximum-int(unit.get('hp', maximum))))
    return base + round(base * .5 * loss / max(1, maximum-1))


def incoming_damage(unit, amount):
    statuses = {s.get('id') for s in unit.get('statuses', [])}
    if 'reckless_exposure' in statuses:
        amount = max(1, round(amount * 1.2))
    if 'brace_defense' in statuses:
        amount = max(1, round(amount * .75))
    return amount


def gain_fury(battle, unit, amount):
    if unit.get('fury_cap') != 5:
        return
    previous = unit.get('fury', 0)
    unit['fury'] = min(5, previous + amount)
    if unit['fury'] > previous:
        feedback(battle, unit, 'fury', unit['fury']-previous)


def survive(battle, unit, intent):
    if unit.get('hp') != 0 or intent == 'nonlethal':
        return
    if unit.get('angry_until') is not None:
        unit['hp'] = 1
    elif has_passive(unit, 'too_angry_to_fall') and not unit.get('angry_used'):
        unit.update(hp=1, angry_used=True, angry_until=unit.get('ability_activation', 0)+1)
        unit.setdefault('statuses', []).append({'id':'death_defiance'})
        feedback(battle, unit, 'status', status_id='death_defiance')
        effect(battle,unit,'death_defiance')
        battle['log'].append(f"{unit['name']} refuses to fall. Lethal damage cannot finish them before their next turn.")


def heal(battle, unit, percent, reason):
    if not unit.get('alive', True) or not unit.get('conscious', True):
        return 0
    amount = min(max(0,unit['max_hp']-unit['hp']), max(1, round(unit['max_hp']*percent/100)))
    unit['hp'] += amount
    if amount:
        feedback(battle, unit, 'heal', amount)
        battle['log'].append(f"{unit['name']} restores {amount} HP with {reason}.")
    return amount


def after_damage(battle, attacker, target, previous_hp, ability):
    source = battle.get('units', {}).get(attacker.get('id'))
    hostile = bool(source and source.get('team') != target.get('team') and source['id'] != target['id'])
    actual = max(0,previous_hp-target['hp'])
    if hostile and actual and target.get('hp', 0)>0:
        direct = not any(attacker.get(k) for k in ('status_tick','environmental_fall','collision_attack'))
        amount = 2 if direct and target['hp']*2<=target['max_hp'] and has_passive(target,'bloodfury') else 1
        gain_fury(battle,target,amount)
    killed = previous_hp>0 and target.get('condition')=='dead' and hostile and not target.get('temporary')
    if not killed or not source or source.get('hp',0)<=0:
        return
    if ability and ability.get('id')=='job:fighter:victory_strike':
        heal(battle,source,10,'Victory Strike')
    if has_passive(source,'bloodthirst'):
        clock = source.get('ability_activation',0)
        state = source.setdefault('martial_state',{})
        if state.get('bloodthirst_window')==clock or clock>=state.get('bloodthirst_ready',0):
            state.update(bloodthirst_window=clock,bloodthirst_ready=clock+3)
            if heal(battle,source,20,'Bloodthirst'):
                effect(battle,source,'bloodthirst')


def try_unstoppable(unit):
    if not has_passive(unit,'unstoppable') or unit.get('fury',0)<1 or unit.get('hp',0)<=0:
        return
    state = unit.setdefault('martial_state',{})
    clock = unit.get('ability_activation',0)
    if clock < state.get('unstoppable_ready',0):
        return
    status = next((s for sid in HARMFUL for s in unit.get('statuses',[]) if s.get('id')==sid),None)
    if status is None:
        return
    unit['statuses'].remove(status)
    unit['fury'] -= 1
    state['unstoppable_ready'] = clock+3
    if status.get('elemental_freeze'):
        from . import combat_conditions as conditions
        conditions.apply(unit,'wet',status.get('wet_turns',2),{'id':status.get('source_id'),'name':status.get('source_name')})
    unit.setdefault('martial_feedback',[]).append(status['id'])
    if status['id'] in ('stun','sleep','freeze','paralyze'):
        unit.pop('forced_skip',None)
        unit.pop('paralyzed_move',None)


def flush(battle, unit):
    for sid in unit.pop('martial_feedback',[]):
        feedback(battle,unit,'cleanse',removed_statuses=[sid])
        effect(battle,unit,'unstoppable')
        battle['log'].append(f"{unit['name']} spends 1 Fury to remove {sid} with Unstoppable.")


def start_activation(battle, unit):
    if unit.get('angry_until') is not None and unit.get('ability_activation',0)>=unit['angry_until']:
        unit.pop('angry_until')
        unit['statuses']=[s for s in unit.get('statuses',[]) if s.get('id')!='death_defiance']
    unit['statuses']=[s for s in unit.get('statuses',[]) if s.get('id')!='reckless_exposure']
    try_unstoppable(unit)
    flush(battle,unit)
