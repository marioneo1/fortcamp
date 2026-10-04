"""Bounded battlefield zones and reversible forms; no general skill scripting."""
from copy import deepcopy
from . import combat_conditions as conditions

ZONES = {
    'ember': {'name': 'Ember Patch', 'relation': 'enemy', 'events': ['entry', 'start'],
              'status': 'burn', 'description': 'Applies Burn once per affected activation on committed entry or activation start.'},
    'binding': {'name': 'Binding Circle', 'relation': 'enemy', 'events': ['entry'],
                'status': 'bind', 'description': 'Committed entry attempts Bind. Control recovery and resistance apply.'},
    'thorns': {'name': 'Thornbed', 'relation': 'enemy', 'events': ['entry'], 'damage': 3,
               'description': 'Committed entry deals 3 damage once per activation. Standing still avoids it.'},
    'sanctuary': {'name': 'Consecrated Ground', 'relation': 'ally', 'events': ['start'], 'heal': 3,
                  'description': 'Restores 3 HP at activation start. Burn prevents this healing.'},
}
FORM_FIELDS = ('attack', 'attack_range', 'attack_elevation_rule', 'weapon', 'weapon_type',
               'move', 'armor', 'element', 'on_hit', 'knockout_finisher', 'displacement_resistance')
FORMS = {
    'prowler': {'name': 'Prowler', 'move_delta': 1, 'armor_delta': 0, 'resistance': 0,
                'description': 'Mobile melee form. Keeps HP, race and ground traversal; weapon techniques are unavailable.'},
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
    zones[:] = [z for z in zones if (z['owner_id'], z['kind']) != (owner['id'], effect['zone'])]
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
                        and active(battle['units'][z['owner_id']])]


def trigger_zones(battle, unit, event, active, hostile, apply_status, damage):
    if not active(unit):
        return
    for zone in sorted(battle.get('zones', []), key=lambda z: z['id']):
        owner = battle['units'].get(zone['owner_id'])
        rule = ZONES[zone['kind']]
        if not owner or not active(owner) or event not in rule['events']:
            continue
        if not any((p['x'], p['y']) == (unit['x'], unit['y']) for p in zone['cells']):
            continue
        enemy = hostile(unit, owner)
        if enemy != (rule['relation'] == 'enemy'):
            continue
        stamp = deepcopy(unit.get('status_activation'))
        hits = unit.setdefault('zone_hits', {})
        # Shared per kind, across all owners and start/entry events, not per zone ID.
        if zone['kind'] in hits and hits[zone['kind']] == stamp:
            continue
        hits[zone['kind']] = stamp
        if rule.get('status'):
            apply_status(owner, unit, rule['status'])
        if rule.get('damage'):
            damage(owner, unit, rule['damage'], rule['name'])
        if rule.get('heal') and not conditions.has(unit, 'burn'):
            amount = min(rule['heal'], max(0, unit['max_hp']-unit['hp']))
            unit['hp'] += amount
            if amount:
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
    if unit.get('form') and unit['form']['expires_at'] <= unit.get('ability_activation', 0):
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
                      'remaining': max(0, z['expires_at']-owner.get('ability_activation', 0))})
    return zones
