"""Reconstruct ordinary NPC bodies from encounter targets, retaining real traits.

Only fresh battles are rebuilt. Saved battles and legacy recruits are not rewritten.
"""
from copy import deepcopy
from . import combat_stats as stats
from .combat_pacing import RANK_PERCENT
from .content import ITEMS
from .job_loadouts import snapshot
from .perk_effects import modifiers


def rebuild(unit, rank='E'):
    if unit.get('creature') or unit.get('temporary') or unit.get('engineer_machine'):
        return
    from .game import effective_attribute
    from .general_perks import battle_character
    target = {k: unit[k] for k in ('max_hp', 'attack', 'armor')}
    recruit = deepcopy(unit.get('recruitable_snapshot') or {})
    recorded = unit.get('rank_scaling', {}).get('attribute_baseline')
    recruit['attributes'] = dict(recorded or recruit.get('attributes') or
                                dict(str=5, dex=5, agi=5, vit=4, int=4, luk=4))
    recruit.update(adventurer_rank=rank, combat_stat_version=2)
    recruit.setdefault('perks', {'combat': 'none'})
    recruit.setdefault('traits', [])
    if not recruit.get('job_id'):
        recruit['job_id'] = 'ranger' if unit.get('attack_elevation_rule') == 'ballistic' else 'mage' if unit.get('attack_elevation_rule') == 'ignore' else 'fighter'
    recruit['race'] = unit.get('race', 'Human')
    recruit['id'] = unit['id']
    scaling = 'dex' if unit.get('attack_elevation_rule') == 'ballistic' else 'int' if unit.get('attack_elevation_rule') == 'ignore' else 'str'
    state = {'inventory': []}
    perks = modifiers(state, recruit, ITEMS, 'combat')
    job_bonus = snapshot(recruit)[2]
    training = {'none':0, 'basic':1, 'skilled':2, 'expert':3, 'master':4}.get(recruit['perks'].get('combat'), 0)
    attribute_bonuses = {key: effective_attribute(state, recruit, key) - stats.allocated_attribute(recruit, key)
                         for key in stats.ATTRIBUTE_NAMES}
    _, attribute_roll = battle_character(recruit, unit.get('perk_battle_seed'))

    def body():
        # Roll metadata once per battle, with the same seed and ID as ordinary allies.
        values = {key: max(1, stats.allocated_attribute(recruit, key) + attribute_bonuses[key])
                  for key in stats.ATTRIBUTE_NAMES}
        if attribute_roll:
            key = attribute_roll['attribute']
            raw = recruit['attributes'][key]
            values[key] = max(1, values[key] + max(1, raw + attribute_roll['amount']) - raw)
        return values, attribute_roll

    def values():
        attrs, _ = body()
        return stats.derive(attrs, recruit['race'], scaling, training=training,
                            hp_bonus=perks.get('hp', 0),
                            armor_bonus=perks.get('armor', 0) + job_bonus.get('armor', 0))

    # HP and attack come from allocation, not a hidden encounter damage multiplier.
    # Prefer avoiding excess Armor when two VIT allocations give comparable HP.
    original = recruit['attributes']['vit']
    options = []
    # A boss's large HP target can otherwise buy substantial new Armor as a
    # side effect. Preserve its endurance band without doubling down on armor.
    armor_weight = .15 if unit.get('boss') or unit.get('kind') == 'chieftain' else .06
    for value in range(1, 81):
        recruit['attributes']['vit'] = value
        result = values()
        if result['max_hp'] < target['max_hp'] * .8:
            continue
        score = abs(result['max_hp'] - target['max_hp']) / max(1, target['max_hp']) + armor_weight * max(0, result['armor'] - target['armor'])
        options.append((score, abs(value-original), value))
    recruit['attributes']['vit'] = min(options)[2]
    original = recruit['attributes'][scaling]
    options = []
    for value in range(1, 81):
        recruit['attributes'][scaling] = value
        options.append((abs(values()['attack'] - target['attack']), abs(value-original), value))
    recruit['attributes'][scaling] = min(options)[2]
    result = values()
    equipment_armor = max(0, target['armor'] - result['armor'])
    result['armor'] += equipment_armor
    attrs, roll = body()
    unit.update(hp=result['max_hp'], **result, adventurer_rank=rank,
                combat_stat_version=2, attributes=deepcopy(attrs),
                strength=attrs['str'], dexterity=attrs['dex'], agility=attrs['agi'],
                vitality=attrs['vit'], intelligence=attrs['int'], luck=attrs['luk'],
                battle_attribute_roll=roll,
                combat_equipment={'name':unit.get('weapon', 'Worn weapon'),
                                  'weapon_power':0, 'weapon_scaling':scaling,
                                  'weapon_type':unit.get('weapon_type','unarmed'), 'armor':equipment_armor},
                recruitable_snapshot=deepcopy(recruit))
    unit.setdefault('perk_modifiers', {}).update(perks)
    unit['body_reconstruction']={'reference':target, 'equipment_armor':equipment_armor}
    unit['rank_scaling'] = dict(rank=rank, percent=RANK_PERCENT[rank],
                               attribute_baseline=deepcopy(recruit['attributes']),
                               baseline={}, method='attributes_once')
    unit['stat_sources'] = stats.sources(attrs, recruit['race'], scaling, training=training,
                                        hp_bonus=perks.get('hp', 0), armor_bonus=perks.get('armor', 0),
                                        job_armor=job_bonus.get('armor', 0), equipment_armor=equipment_armor)
    unit['stat_sources']['Attack'] += '; ' + stats.rank_explanation(recruit)
    # Capture HP/Resolve is initialized lazily from the rebuilt body.
    unit.pop('max_resolve', None)
    unit.pop('resolve', None)
