"""Authored beginner opposition, separate from generic rank budgets.

Humanoid specialties use real learned/equipped Job skills. Animal traits are
species mechanics, never recruitable humanoid Jobs.
"""
from copy import deepcopy

from .job_loadouts import JOBS, snapshot
from .building_templates import BUILDINGS
from .wall_boundaries import crossed_walls

MISSION_IDS = frozenset({'rats_storehouse', 'roadside_toll', 'wolves_fence',
                         'goblin_pickpockets', 'ruined_well', 'supply_watch'})

# Same E-rank band: fewer bodies are tougher, larger groups have lighter bites.
# Placement and action economy still need actual combat checks, not budget sums alone.
SETUPS = {
    'goblin_pickpockets': [
        (2, 0, 0, 'cluster', 'A cutpurse and lookout watch the purse at the road bend.'),
        (2, 0, 0, 'spread', 'A cutpurse searches the handcart while a snarer covers the fork.'),
        (2, 0, 0, 'cluster', 'A snarer and cutpurse wait beside the narrow brush-lined road.'),
        (2, 0, 0, 'spread', 'A lookout watches the fallen tree while a cutpurse guards the passing place.'),
    ],
    'ruined_well': [
        (2, 0, 0, 'cluster', 'A salvage guard and sling scout search the abandoned cottage.'),
        (2, 0, 0, 'spread', 'A salvage guard covers the broken boundary; a snarer searches near the well.'),
        (2, 0, 0, 'spread', 'A sling scout and salvage guard occupy separate ruins around the well.'),
        (2, 0, 0, 'cluster', 'A salvage guard and snarer sort their haul in the wash court.'),
    ],
    'supply_watch': [
        (2, 0, 0, 'spread', 'A supply raider covers the store while a sling scout watches the approach.'),
        (3, 0, 0, 'spread', 'Three lightly armed pilferers search the paired supply shelters.'),
        (2, 0, 0, 'cluster', 'A supply raider and snarer hold the side store together.'),
        (3, 0, 0, 'spread', 'Two pilferers and a lookout search different sides of the delivery yard.'),
    ],
    'rats_storehouse': [
        (3, 17, 3, 'cluster', 'Rats crowd the grain inside the long shed.'),
        (4, 14, 2, 'spread', 'Smaller rats forage in both provision stores.'),
        (2, 25, 4, 'cluster', 'Two large rats feed near the rear annex.'),
        (4, 14, 2, 'outside', 'Rats feed inside the store; two scavenge outside beside the delivery yard.'),
    ],
    'wolves_fence': [
        (3, 22, 4, 'cluster', 'The pack gathers beside the broken fence.'),
        (2, 31, 5, 'spread', 'Two seasoned wolves watch different sides of the clearing.'),
        (4, 17, 3, 'spread', 'Four lean wolves are scattered across the paddocks.'),
        (3, 22, 4, 'spread', 'Wolves occupy separate approaches through the deep pasture.'),
    ],
    'roadside_toll': [
        (2, 0, 0, 'cluster', 'An enforcer and cutpurse block the toll court together.'),
        (2, 0, 0, 'spread', 'An enforcer blocks the road while a trapper watches from farther back.'),
        (2, 0, 0, 'cluster', 'A trapper waits beside the enforcer near the inspection wing.'),
        (2, 0, 0, 'spread', 'Two opportunists cover the paired watch posts.'),
    ],
}


def setup(mission_id, variation=1):
    if mission_id not in SETUPS:
        return None
    count, hp, attack, formation, description = SETUPS[mission_id][(int(variation)-1) % 4]
    return dict(count=count, hp=hp, attack=attack, formation=formation, description=description)


def deployment(mission_id, candidates, board=None, clear_tiles=None):
    if mission_id not in MISSION_IDS:
        return candidates
    spec = setup(mission_id, (board or {}).get('map_variation', 1))
    count = spec['count']
    candidates = list(candidates)
    outside = []
    if spec['formation'] == 'outside' and board and clear_tiles:
        building = board['building_templates'][0]
        rooms = BUILDINGS[building['id']]['rooms']
        east = building['anchor'][0] + max(x+w for x,y,w,h in rooms)
        gate_y = building['anchor'][1] + 3
        outside = sorted((p for p in clear_tiles if p['x'] == east),
                         key=lambda p: (abs(p['y']-gate_y), p['y']))[:2]
    if spec['formation'] == 'cluster':
        return sorted(candidates, key=lambda p: abs(p['x']-candidates[0]['x']) +
                      abs(p['y']-candidates[0]['y']))[:count]
    if outside:
        return candidates[:count-len(outside)] + outside
    # Separated groups use only legal authored spawn candidates.
    chosen = candidates[:1]
    remaining = candidates[1:]
    while remaining and len(chosen) < count:
        tile = max(remaining, key=lambda p: min(abs(p['x']-q['x']) + abs(p['y']-q['y']) for q in chosen))
        chosen.append(tile)
        remaining = [p for p in remaining if p != tile]
    return chosen


def _trait(key, name, description):
    return {'id': key, 'name': name, 'description': description, 'type': 'passive',
            'source_kind': 'species', 'source_name': 'Species', 'modifiers': {}}


def author(mission_id, unit, index):
    if mission_id not in MISSION_IDS:
        return
    unit.update(boss=False, kind='creature' if unit.get('creature') else 'raider',
                attack_range=1, attack_elevation_rule='melee', status_version=1,
                strength=5, agility=5, intelligence=4)
    if mission_id == 'rats_storehouse':
        spec = setup(mission_id, unit.get('encounter_variation', 1))
        unit.update(hp=spec['hp'], max_hp=spec['hp'], attack=spec['attack'], armor=0, move=4, initiative=12+index,
                    species_profile='store_rat', portrait='/assets/animals-v1/rat.png', evasion=10, swarm_count=1, personality_id='survivor',
                    on_hit=None,
                    passives=[_trait('species:rat:swarm', 'Regrouping Swarm',
                        'Wounded rats merge with nearby rats, up to three total; current HP, maximum HP and attack add together.'),
                              _trait('species:rat:plague', 'Gnawing Weakness',
                        'Each rat in a landed bite adds one Weakness stack: -5% damage dealt and +5% damage taken, capped at 30%; one stack fades at turn end.')])
    elif mission_id == 'wolves_fence':
        spec = setup(mission_id, unit.get('encounter_variation', 1))
        unit.update(hp=spec['hp'], max_hp=spec['hp'], attack=spec['attack'], armor=0, move=4, initiative=13+index,
                    species_profile='fence_wolf', portrait='/assets/animals-v1/wolf.png', evasion=5, personality_id='opportunist',
                    on_hit={'id': 'bleed', 'chance': 25, 'turns': 1},
                    passives=[_trait('species:wolf:pack', 'Pack Pressure',
                        'Bites deal 20% more damage per other wolf beside the victim (up to 40%); only cardinal neighbors count.'),
                              _trait('species:wolf:fangs', 'Tearing Fangs',
                        'Landed bites have a 25% chance to add Bleed: 5% maximum HP per stack at turn end, then one stack expires.')])
    elif mission_id in {'goblin_pickpockets', 'ruined_well', 'supply_watch'}:
        _author_second_batch(mission_id, unit, index)
    else:
        job = 'fighter' if index == 0 else 'rogue'
        keys = (['job:fighter:bash', 'job:fighter:intercept'] if index == 0
                else list(JOBS['rogue']['starter_skills']))
        # Roles are authored per layout rather than random unrelated kit swaps.
        mixed = index == 1 and unit.get('encounter_variation', 1) in (2, 3)
        if mixed: keys = ['job:rogue:cheap_shot','npc:bandit:road_bola','job:rogue:exploit_weakness']
        specialty = 'Road Enforcer' if index == 0 else 'Road Trapper' if mixed else 'Road Cutpurse'
        personality = 'guardian' if index == 0 else 'strategist' if mixed else 'opportunist'
        recruit = {'job_id': job, 'job_practice': 0, 'learned_skills': keys,
                   'equipped_skills': keys, 'skill_slots': 5,
                   'attributes': dict(str=6 if index == 0 else 4, dex=5, agi=4 if index == 0 else 6,
                                      vit=5 if index == 0 else 4, int=4, luk=4),
                   'combat_specialization': specialty, 'personality_id':personality}
        skills, passives, modifiers = snapshot(recruit)
        hp = 28 if index == 0 else 22
        unit.update(hp=hp, max_hp=hp, attack=5 if index == 0 else 4,
                    armor=1 if index == 0 else 0, move=3 if index == 0 else 4,
                    initiative=12 if index == 0 else 15, evasion=0 if index == 0 else 8,
                    weapon='Worn Cudgel' if index == 0 else 'Notched Knife',
                    melee_style='blunt' if index == 0 else 'stab',
                    armor_material='leather', job_id=job, ability_version=1,
                    skills=skills, passives=passives, skill_slot_order=list(keys),
                    reactions=[deepcopy(p['reaction']) for p in passives if p.get('reaction')],
                    perk_modifiers=modifiers, martial_version=1,
                    encounter_profile='road_enforcer' if index == 0 else 'road_cutpurse',
                    job_description=specialty + ': ' + ('Bola control, positional strikes and debuff exploitation.' if mixed else JOBS[job]['description']),
                    combat_specialization=specialty, personality_id=personality,
                    recruitable_snapshot=deepcopy(recruit),
                    strength=recruit['attributes']['str'], agility=recruit['attributes']['agi'],
                    intelligence=recruit['attributes']['int'])


def _author_second_batch(mission_id, unit, index):
    variation = (int(unit.get('encounter_variation', 1))-1) % 4
    rosters = {
        'goblin_pickpockets': [('cutpurse','lookout'), ('cutpurse','snarer'),
                              ('snarer','cutpurse'), ('lookout','cutpurse')],
        'ruined_well': [('guard','lookout'), ('guard','snarer'),
                       ('lookout','guard'), ('guard','snarer')],
        'supply_watch': [('guard','lookout'), ('pilferer','pilferer','pilferer'),
                         ('guard','snarer'), ('pilferer','pilferer','light_lookout')],
    }
    role = rosters[mission_id][variation][index]
    goblin = mission_id == 'goblin_pickpockets'
    job = 'fighter' if role == 'guard' else 'ranger' if 'lookout' in role else 'rogue'
    keys = {'fighter':['job:fighter:bash','job:fighter:intercept'],
            'ranger':['job:ranger:mark_quarry','job:ranger:longshot'],
            'rogue':['job:rogue:cheap_shot','job:rogue:crippling_cut']}[job]
    if role == 'snarer': keys = ['npc:bandit:road_bola','job:rogue:cheap_shot']
    names = {'guard':'Salvage Guard' if mission_id=='ruined_well' else 'Supply Raider',
             'cutpurse':'Goblin Cutpurse','snarer':'Goblin Snarer' if goblin else 'Scavenger Snarer',
             'lookout':'Goblin Lookout' if goblin else 'Sling Scout',
             'pilferer':'Supply Pilferer','light_lookout':'Supply Lookout'}
    attributes = dict(str=6 if job=='fighter' else 4, dex=6 if job=='ranger' else 5,
                      agi=6 if goblin or job=='rogue' else 4, vit=5 if job=='fighter' else 4, int=4, luk=4)
    personality = 'guardian' if role=='guard' else 'strategist' if role=='snarer' else 'survivor' if 'lookout' in role else 'opportunist'
    recruit = dict(job_id=job, job_practice=0, learned_skills=list(keys), equipped_skills=list(keys),
                   skill_slots=5, attributes=attributes, combat_specialization=names[role], personality_id=personality)
    skills, passives, modifiers = snapshot(recruit)
    light = role in {'pilferer','light_lookout'}
    hp = 19 if light else 28 if role=='guard' else 24 if goblin else 23
    ranged = job == 'ranger'
    unit.update(hp=hp,max_hp=hp,attack=3 if light else 5 if role=='guard' else 4,
                armor=1 if role=='guard' else 0,move=4 if goblin or job=='rogue' else 3,
                initiative=16 if goblin else 12+index,evasion=12 if goblin else 6 if job=='rogue' else 0,
                weapon='Weighted Sling' if ranged else 'Worn Cudgel' if role=='guard' else 'Notched Knife',
                weapon_type='bow' if ranged else 'club' if role=='guard' else 'dagger',
                melee_style='blunt' if role=='guard' else 'stab',
                attack_range=3 if ranged else 1,attack_elevation_rule='ballistic' if ranged else 'melee',
                armor_material='leather',job_id=job,ability_version=1,martial_version=1,
                skills=skills,passives=passives,skill_slot_order=list(keys),perk_modifiers=modifiers,
                reactions=[deepcopy(p['reaction']) for p in passives if p.get('reaction')],
                encounter_profile='road_enforcer' if role=='guard' else 'road_cutpurse',
                combat_specialization=names[role],job_description=names[role]+': '+JOBS[job]['description'],
                personality_id=personality,recruitable_snapshot=deepcopy(recruit),
                strength=attributes['str'],agility=attributes['agi'],intelligence=attributes['int'],
                corpse_item='weighted_sling' if ranged else 'watchmans_cudgel' if role=='guard' else 'balanced_dagger',
                corpse_item_chance=20)


def attack_percent(battle, attacker, target):
    """Direct bite power only; shared by forecasts and actual damage."""
    if attacker.get('status_tick') or attacker.get('reaction_damage'):
        return 100
    profile = attacker.get('species_profile')
    if profile != 'fence_wolf':
        return 100
    center = target
    neighbors = sum(1 for unit in battle.get('units', {}).values()
                    if unit['id'] != attacker['id'] and unit.get('species_profile') == profile
                    and unit.get('team') == attacker.get('team') and unit.get('alive')
                    and unit.get('conscious', True) and not unit.get('extracted')
                    and not unit.get('carried_by')
                    and not any(s.get('id') in {'stun', 'freeze', 'sleep', 'paralyze'} for s in unit.get('statuses', []))
                    and abs(unit['x']-center['x']) + abs(unit['y']-center['y']) == 1
                    and not crossed_walls(battle, (unit['x'], unit['y']), (center['x'], center['y']), sight=True))
    return 100 + min(2, neighbors) * 20
