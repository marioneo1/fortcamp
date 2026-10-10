"""Bounded battlefield zones and reversible forms; no general skill scripting."""
from copy import deepcopy
from . import combat_conditions as conditions
from .combat_feedback import record as feedback

ZONES = {
    'tripline': {'name':'Tripline','relation':'enemy','events':['entry'],
                 'entry_per_cell':True,'trap':True,'statuses':['hobbled'],
                 'description':'A three-cell tripline: the first enemy crossing gains Hobble; the whole line then snaps. Forced movement counts.'},
    'fire_wall':{'name':'Fire Wall','relation':'everyone','events':['entry'],'status':'burn','entry_per_cell':True,'description':'Each tile entry applies Burn and triggers it, plus half the Fire Companion INT as fire damage. Allies are affected.'},
    'scorched': {'name':'Scorched ground','relation':'everyone','events':{'entry'},'status':'burn','entry_damage':0,'entry_per_cell':True,'description':'Each committed tile entry adds Burn and immediately triggers its current stack damage without consuming a stack. Re-entry counts; overlapping fire patches do not add damage. Burns everyone, including allies and the caster.'},
    'caltrops':{'name':'Caltrops','relation':'everyone','events':['entry','placement'],'entry_per_cell':True,'trap':True,'statuses':['bleed','hobbled'],'description':'Placement on an occupied tile and each tile entry attempt one Bleed and one Hobble stack for two target turns. Allies and push/pull count; Trap Expert avoids it. Overlapping strips do not multiply an entry.'},
    'ember': {'name': 'Ember Patch', 'relation': 'enemy', 'events': ['entry'],
              'status': 'burn', 'entry_damage':0, 'entry_per_cell':True,
              'description': 'Each entered flame tile adds Burn and immediately triggers its current stack damage without consuming a stack. Re-entry counts again; overlapping patches do not stack. Burn ticks normally and loses one stack at turn end. Allies are safe.'},
    'binding': {'name': 'Binding Circle', 'relation': 'enemy', 'events': ['entry'],
                'status': 'bind', 'description': 'Committed entry attempts Bind. Control recovery and resistance apply.'},
    'thorns': {'name': 'Thornbed', 'relation': 'enemy', 'events': ['entry'], 'damage': 3,
               'entry_per_cell':True,
               'description': 'Each thorn tile entered along the committed path deals 3 damage. Re-entry counts again; overlapping patches do not stack. Standing still avoids it.'},
    'sanctuary': {'name': 'Consecrated Ground', 'relation': 'ally', 'events': ['start'], 'heal': 3,
                  'description': 'Restores 3 HP at activation start. Burn prevents this healing.'},
}
FORM_FIELDS = ('attack', 'attack_range', 'attack_elevation_rule', 'weapon', 'weapon_type', 'melee_style',
               'move', 'armor', 'evasion', 'element', 'on_hit', 'knockout_finisher', 'displacement_resistance')
FORMS = {
    'prowler': {'name': 'Prowler', 'move_delta': 1, 'armor_delta': 0, 'resistance': 0,
                'description': 'Mobile melee form. Keeps HP, race and ground traversal; weapon techniques are unavailable.'},
    'rat':{'name':'Rat','move_delta':1,'armor_delta':0,'resistance':0,'description':'90% evasion against aimed attacks; AoE and cannot-miss attacks bypass it. Any received damage kills.'},
    'bulwark': {'name': 'Bulwark', 'move_delta': -1, 'armor_delta': 3, 'resistance': 50,
                 'description': 'Durable melee form with 50 added knockback resistance, lower movement, and no HP refill.'},
}


def validate_effect(effect):
    kind = effect['type']
    if kind == 'zone':
        if effect.get('zone') not in ZONES or effect.get('radius') not in (0, 1):
            raise ValueError('Unsupported zone or radius')
    elif effect.get('form') not in {*FORMS, 'normal'}:
        raise ValueError('Unsupported form')


def zone_cells(battle, target, radius, allowed):
    """Small diamond clipped by map bounds and the engine's terrain/sight rules."""
    return [{'x': x, 'y': y} for y in range(target['y']-radius, target['y']+radius+1)
            for x in range(target['x']-radius, target['x']+radius+1)
            if 0 <= x < battle['width'] and 0 <= y < battle['height']
            and abs(x-target['x'])+abs(y-target['y']) <= radius and allowed(x, y)]


def place_zone(battle, owner, effect, cells):
    if not cells:
        raise ValueError('No legal ground for this zone')
    zones = battle.setdefault('zones', [])
    # Recasting one's own type replaces its area; other owners do not multiply ticks.
    zones[:] = [z for z in zones if z.get('prepared_defense') or (z['owner_id'], z['kind']) != (owner['id'], effect['zone'])]
    serial = battle.get('zone_serial', 0)+1
    battle['zone_serial'] = serial
    zone = {'id': f'zone_{serial}', 'owner_id': owner['id'], 'team': owner['team'],
            'kind': effect['zone'], 'cells': deepcopy(cells),
            'expires_at': owner.get('ability_activation', 0)+effect['turns']}
    zones.append(zone)
    for unit in battle['units'].values():
        unit.setdefault('zone_location', [unit['x'], unit['y']])
    battle['log'].append(f"{owner['name']} creates {ZONES[zone['kind']]['name']}.")
    return zone


def expire_zones(battle, owner):
    battle['zones'] = [z for z in battle.get('zones', []) if z['owner_id'] != owner['id']
                       or z['expires_at'] > owner.get('ability_activation', 0)]


def cleanup_zones(battle, active):
    if 'zones' in battle:
        battle['zones']=[z for z in battle['zones'] if z['owner_id'] in battle['units']
                        and (active(battle['units'][z['owner_id']]) or z.get('persistent_defeat_trap') and battle.get('round',1)<z['expires_round'])]


def trigger_zones(battle, unit, event, active, hostile, apply_status, damage, only_zone=None):
    if not active(unit):
        return
    triggered = set()
    for zone in sorted(battle.get('zones', []), key=lambda z: z['id']):
        if only_zone is not None and zone['id'] != only_zone:continue
        owner = battle['units'].get(zone['owner_id'])
        rule = ZONES[zone['kind']]
        if not owner or not (active(owner) or zone.get('persistent_defeat_trap') and battle.get('round',1)<zone['expires_round']) or event not in rule['events']:
            continue
        if not any((p['x'], p['y']) == (unit['x'], unit['y']) for p in zone['cells']):
            continue
        if rule.get('trap'):
            from .combat_rogue import trap_expert
            if trap_expert(unit):continue
        enemy = hostile(unit, owner)
        if rule['relation']!='everyone' and enemy != (rule['relation'] == 'enemy'):
            continue
        stamp = deepcopy(unit.get('status_activation'))
        hits = unit.setdefault('zone_hits', {})
        # Overlapping owners share one hit per entry. Control/healing and other
        # zones retain their activation cap; burning ground counts every entry.
        trigger_key='fire_ground' if zone['kind'] in {'ember','scorched'} else zone['kind']
        if trigger_key in triggered:
            continue
        per_entry = event in {'entry','placement'} and rule.get('entry_per_cell')
        if not per_entry and zone['kind'] in hits and hits[zone['kind']] == stamp:
            continue
        triggered.add(trigger_key)
        hits[zone['kind']] = stamp
        for sid in rule.get('statuses',[]):apply_status(owner,unit,sid,True)
        if zone['kind']=='tripline':
            from .enemy_specialties import effect
            battle['zones']=[z for z in battle.get('zones',[]) if z['id']!=zone['id']]
            effect(battle,unit,'tripline',zone_id=zone['id'],zone_snapshot=deepcopy(zone))
            battle.setdefault('animation_events',[]).append({'type':'sound','cues':[{'name':'specialty_tripline_snap','offset':0}]})
        if rule.get('status'):
            apply_status({**owner,'scorched_source':zone} if zone['kind']=='scorched' else owner, unit, rule['status'])
        if rule.get('damage'):
            damage(owner, unit, rule['damage'], rule['name'])
        if event=='entry' and zone.get('entry_damage',rule.get('entry_damage')):
            damage(owner,unit,zone.get('entry_damage',rule.get('entry_damage')),rule['name'])
        if rule.get('heal') and not conditions.has(unit, 'burn'):
            amount = min(zone.get('heal',rule['heal']), max(0, unit['max_hp']-unit['hp']))
            unit['hp'] += amount
            if amount:
                feedback(battle,unit,'heal',amount)
                battle['log'].append(f"{unit['name']} recovers {amount} HP on {rule['name']}.")
        if not active(unit):
            break


def end_form(unit):
    form = unit.pop('form', None)
    if not form:
        return
    for key in FORM_FIELDS:
        if key in form['original']:
            unit[key] = deepcopy(form['original'][key])
        else:
            unit.pop(key, None)


def change_form(unit, effect):
    if unit.get('capture_weapon') or unit.get('carrying') or unit.get('carrying_object'):
        raise ValueError('Put down the payload and unequip capture tools before changing form')
    end_form(unit)
    if effect['form'] == 'normal':
        return
    rule = FORMS[effect['form']]
    original = {k: deepcopy(unit[k]) for k in FORM_FIELDS if k in unit}
    unit['form'] = {'id': effect['form'], 'original': original,
                    'expires_at': unit.get('ability_activation', 0)+effect['turns']}
    unit.update(attack=max(3, min(12, 3+unit.get('intelligence', 4)//2)),
                attack_range=1, attack_elevation_rule='melee', weapon=rule['name'],
                weapon_type='form', element=None, on_hit=None, knockout_finisher=0,
                move=max(1, unit['move']+rule['move_delta']), armor=unit['armor']+rule['armor_delta'],
                displacement_resistance=min(100, original.get('displacement_resistance', 0)+rule['resistance']))


def expire_form(unit):
    if unit.get('form') and not unit['form'].get('persistent') and unit['form']['expires_at'] <= unit.get('ability_activation', 0):
        end_form(unit)


def presentation(battle):
    zones = []
    for z in battle.get('zones', []):
        owner = battle['units'].get(z['owner_id'])
        if not owner:
            continue
        rule = ZONES[z['kind']]
        zones.append({**deepcopy(z), 'name': rule['name'], 'description': rule['description'],
                      'owner_name': owner['name'],
                      'remaining': max(0,z['expires_round']-battle.get('round',1)) if z.get('persistent_defeat_trap') else max(0, z['expires_at']-owner.get('ability_activation', 0)),
                      **({'description':f"Restores {z['heal']} HP to allies at turn start; Burn prevents healing."} if 'heal' in z else {})})
    return zones
