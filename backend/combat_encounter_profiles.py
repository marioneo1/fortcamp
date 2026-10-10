"""Authored beginner opposition, separate from generic rank budgets.

Humanoid specialties use real learned/equipped Job skills. Animal traits are
species mechanics, never recruitable humanoid Jobs.
"""
from copy import deepcopy

from .job_loadouts import JOBS, snapshot
from .building_templates import BUILDINGS
from .wall_boundaries import crossed_walls
from .d_rank_locations import ROSTERS as D_ROSTERS, LOCATIONS as D_LOCATIONS, ACTIVITY as D_ACTIVITY
from .combat_pacing import scaled, scale_unit

D_IDS = frozenset(D_ROSTERS)

WORKSITE_IDS = frozenset({'timber_creek', 'tool_shed', 'herbs_wall'})
PRISON_IDS = frozenset({'prison_rival_e','prison_former_e','prison_proof_e'})
PREPARED_IDS = frozenset({'frontier_watch_defense', 'prison_rescue_e'})
MISSION_IDS = frozenset({'rats_storehouse', 'roadside_toll', 'wolves_fence',
                         'goblin_pickpockets', 'ruined_well', 'supply_watch'}) | WORKSITE_IDS | PRISON_IDS | PREPARED_IDS | D_IDS

# Same E-rank band: fewer bodies are tougher, larger groups have lighter bites.
# Placement and action economy still need actual combat checks, not budget sums alone.
SETUPS = {
    'frontier_watch_defense': [
        (4,0,0,'spread','A goblin guard and snarer lead two scouts along the northern flank.'),
        (4,0,0,'spread','Two goblin guards cover a cutpurse and lookout on the southern approach.'),
        (5,0,0,'spread','A ringleader splits four lightly armed raiders across both flanks.'),
        (5,0,0,'spread','A guard covers a staggered column of four lightly armed raiders.'),
    ],
    'prison_rescue_e': [
        (2,0,0,'spread','A goblin guard and lookout stand beside the halted prisoner wagon.'),
        (2,0,0,'spread','A guard inspects the wagon while a snarer watches the road.'),
        (3,0,0,'spread','Two light raiders and a lookout escort the wagon across the muddy stretch.'),
        (3,0,0,'spread','Two light raiders and a lookout change guard around the wagon.'),
    ],
    'prison_rival_e': [
        (2,0,0,'cluster','A road enforcer and trapper hold the disputed crossing.'),
        (2,0,0,'spread','A skirmisher watches the pull-off while an enforcer guards the bend.'),
        (2,0,0,'spread','A trapper covers the roadblocks while a skirmisher watches the flank.'),
        (2,0,0,'spread','An enforcer and skirmisher occupy the two checkpoints.'),
    ],
    'prison_former_e': [
        (2,0,0,'cluster','A warband warden and bruiser hold the old command post.'),
        (2,0,0,'spread','A warden guards the through-door post while a skirmisher covers its rear.'),
        (2,0,0,'spread','A bruiser holds the annex while a trapper guards the approach.'),
        (2,0,0,'spread','A warden and bruiser watch the paired command stores.'),
    ],
    'prison_proof_e': [
        (2,0,0,'spread','A bruiser controls the sparring court while a sling scout covers the lane.'),
        (2,0,0,'spread','A warden controls the practice yard while a skirmisher watches the range.'),
        (2,0,0,'spread','A bruiser and skirmisher occupy separate drill courts.'),
        (2,0,0,'spread','A warden and sling scout hold the deep training court.'),
    ],
    'timber_creek': [
        (2, 0, 0, 'cluster', 'A salvage guard and sling scavenger sort cut logs on the far bank.'),
        (3, 0, 0, 'spread', 'Two lightly armed pilferers search the log piles while a lookout watches the crossing.'),
    ],
    'tool_shed': [
        (2, 0, 0, 'cluster', 'A salvage guard and tool snatcher sort tools inside the long store.'),
        (2, 0, 0, 'spread', 'A snarer and sling scavenger search separate parts of the divided store.'),
        (2, 0, 0, 'spread', 'A salvage guard covers the annex while a snarer searches the yard.'),
        (3, 0, 0, 'spread', 'Two lightly armed pilferers and a lookout search the paired sheds.'),
    ],
    'herbs_wall': [
        (2, 0, 0, 'cluster', 'A salvage guard and sling scavenger gather plants behind the garden wall.'),
        (2, 0, 0, 'spread', 'A garden snarer and forager search the herb beds and annex.'),
        (3, 0, 0, 'spread', 'Two lightly armed foragers and a lookout search separate garden beds.'),
        (2, 0, 0, 'spread', 'A garden snarer and sling scavenger collect herbs near the wash court.'),
    ],
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
for _location, _mid in D_LOCATIONS.items():
    SETUPS[_mid] = [(len(roster),0,0,'authored',D_ACTIVITY[_location][i])
                    for i,roster in enumerate(D_ROSTERS[_mid])]


def setup(mission_id, variation=1):
    if mission_id not in SETUPS:
        return None
    count, hp, attack, formation, description = SETUPS[mission_id][(int(variation)-1) % len(SETUPS[mission_id])]
    return dict(count=count, hp=hp, attack=attack, formation=formation, description=description)


def deployment(mission_id, candidates, board=None, clear_tiles=None):
    if mission_id not in MISSION_IDS:
        return candidates
    spec = setup(mission_id, (board or {}).get('map_variation', 1))
    count = spec['count']
    candidates = list(candidates)
    if spec['formation'] == 'authored':
        return candidates[:count]
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
    elif mission_id in {'goblin_pickpockets', 'ruined_well', 'supply_watch'} | WORKSITE_IDS | PRISON_IDS | PREPARED_IDS | D_IDS:
        _author_humanoid_batch(mission_id, unit, index)
    else:
        job = 'fighter' if index == 0 else 'rogue'
        keys = (['job:fighter:bash', 'job:fighter:intercept'] if index == 0
                else list(JOBS['rogue']['starter_skills']))
        # Roles are authored per layout rather than random unrelated kit swaps.
        mixed = index == 1 and unit.get('encounter_variation', 1) in (2, 3)
        if mixed: keys = ['job:rogue:cheap_shot','npc:bandit:road_bola','npc:bandit:tripline','job:rogue:exploit_weakness']
        elif index==0:keys=['job:fighter:bash','job:fighter:intercept','npc:bandit:shakedown']
        else:keys=['job:rogue:cheap_shot','npc:bandit:parting_cut','job:rogue:crippling_cut']
        specialty = 'Road Enforcer' if index == 0 else 'Road Trapper' if mixed else 'Road Cutpurse'
        personality = 'guardian' if index == 0 else 'strategist' if mixed else 'opportunist'
        recruit = {'job_id': job, 'job_practice': 0, 'learned_skills': keys,
                   'equipped_skills': keys, 'skill_slots': 5,
                   'attributes': dict(str=6 if index == 0 else 4, dex=5, agi=4 if index == 0 else 6,
                                      vit=5 if index == 0 else 4, int=4, luk=4),
                   'combat_specialization': specialty, 'personality_id':personality}
        from .recruit_perks import assign
        assign(recruit,mission_id,'enforcer' if index==0 else 'trapper' if mixed else 'skirmisher',unit['id']+unit['name'])
        recruit.update(origin_mission_id=mission_id)
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
                    perk_modifiers=modifiers, origin_perks=list(recruit['traits']), martial_version=1,
                    encounter_profile='road_enforcer' if index == 0 else 'road_cutpurse',
                    job_description=specialty + ': ' + ('Bola control, positional strikes and debuff exploitation.' if mixed else JOBS[job]['description']),
                    combat_specialization=specialty, personality_id=personality,
                    recruitable_snapshot=deepcopy(recruit),
                    strength=recruit['attributes']['str'], agility=recruit['attributes']['agi'],
                    intelligence=recruit['attributes']['int'])
        from .recruit_perks import decorate_enemy
        decorate_enemy(unit,recruit)

    from .combat_vocals import assign as assign_vocals
    assign_vocals(unit)


def _author_humanoid_batch(mission_id, unit, index):
    variation = (int(unit.get('encounter_variation', 1))-1) % len(SETUPS[mission_id])
    rosters = {
        'frontier_watch_defense': [('guard','snarer','cutpurse','lookout'), ('guard','guard','cutpurse','lookout'),
                                   ('ringleader','pilferer','pilferer','pilferer','light_lookout'),
                                   ('guard','pilferer','pilferer','light_lookout','pilferer')],
        'prison_rescue_e': [('guard','lookout'), ('guard','snarer'),
                            ('pilferer','pilferer','light_lookout'), ('pilferer','light_lookout','pilferer')],
        'prison_rival_e':[('enforcer','trapper'),('skirmisher','enforcer'),('trapper','skirmisher'),('enforcer','skirmisher')],
        'prison_former_e':[('warden','bruiser'),('warden','skirmisher'),('bruiser','trapper'),('warden','bruiser')],
        'prison_proof_e':[('bruiser','lookout'),('warden','skirmisher'),('bruiser','skirmisher'),('warden','lookout')],
        'timber_creek': [('guard','lookout'), ('pilferer','pilferer','light_lookout')],
        'tool_shed': [('guard','cutpurse'), ('snarer','lookout'),
                      ('guard','snarer'), ('pilferer','pilferer','light_lookout')],
        'herbs_wall': [('guard','lookout'), ('snarer','cutpurse'),
                       ('pilferer','pilferer','light_lookout'), ('snarer','lookout')],
        'goblin_pickpockets': [('cutpurse','lookout'), ('cutpurse','snarer'),
                              ('snarer','cutpurse'), ('lookout','ringleader')],
        'ruined_well': [('guard','lookout'), ('guard','snarer'),
                       ('lookout','guard'), ('guard','snarer')],
        'supply_watch': [('guard','lookout'), ('pilferer','pilferer','pilferer'),
                         ('guard','snarer'), ('pilferer','pilferer','light_lookout')],
    }
    rosters.update(D_ROSTERS)
    role = rosters[mission_id][variation][index]
    goblin = mission_id in {'goblin_pickpockets','goblin_boar_riders'} or mission_id in WORKSITE_IDS | PREPARED_IDS
    job = 'barbarian' if role=='bruiser' else 'fighter' if role in {'guard','warden','enforcer','ringleader'} else 'ranger' if 'lookout' in role else 'rogue'
    keys = {'fighter':['job:fighter:bash','job:fighter:intercept'],
            'ranger':['job:ranger:mark_quarry','job:ranger:longshot'],
            'rogue':['job:rogue:cheap_shot','job:rogue:crippling_cut'],
            'barbarian':['job:barbarian:reckless_blow','npc:bandit:cornered_fury']}[job]
    if role == 'snarer': keys = ['npc:bandit:road_bola','job:rogue:cheap_shot']
    if role=='trapper':keys=['npc:bandit:tripline','npc:bandit:road_bola']
    if role=='enforcer':keys=['npc:bandit:shakedown','job:fighter:intercept']
    if role=='warden':keys=['npc:bandit:heel_cut','job:fighter:intercept']
    if role=='skirmisher':keys=['npc:bandit:parting_cut','job:rogue:cheap_shot']
    if role=='ringleader':keys=['npc:bandit:tag_team','job:fighter:intercept']
    if goblin and role=='cutpurse':keys=['npc:bandit:ankle_bite','job:rogue:cheap_shot']
    if goblin and 'lookout' in role:keys=['npc:bandit:goliath_shot','job:ranger:mark_quarry']
    names = {'guard':'Salvage Guard' if mission_id=='ruined_well' else 'Supply Raider',
             'cutpurse':'Goblin Cutpurse','snarer':'Goblin Snarer' if goblin else 'Scavenger Snarer',
             'lookout':'Goblin Lookout' if goblin else 'Sling Scout',
             'pilferer':'Supply Pilferer','light_lookout':'Supply Lookout',
             'enforcer':'Bandit Enforcer','trapper':'Bandit Trapper','skirmisher':'Bandit Skirmisher',
             'warden':'Warband Warden','bruiser':'Warband Bruiser','ringleader':'Goblin Ringleader'}
    if mission_id in WORKSITE_IDS:
        names.update(guard='Goblin Salvage Guard', lookout='Sling Scavenger',
                     snarer='Garden Snarer' if mission_id=='herbs_wall' else 'Worksite Snarer',
                     cutpurse='Goblin Forager' if mission_id=='herbs_wall' else 'Tool Snatcher',
                     pilferer='Goblin Forager' if mission_id=='herbs_wall' else 'Worksite Pilferer',
                     light_lookout='Worksite Lookout')
    attributes = dict(str=6 if job=='fighter' else 4, dex=6 if job=='ranger' else 5,
                      agi=6 if goblin or job=='rogue' else 4, vit=5 if job=='fighter' else 4, int=4, luk=4)
    attribute_baseline = dict(attributes)
    if mission_id in D_IDS:
        attributes = {key:scaled(value,'D') for key,value in attributes.items()}
        if mission_id == 'bone_patrol':
            names.update(warden='Relic Warden',guard='Bone Shieldbearer',lookout='Chapel Archer',
                         pilferer='Bone Carrier',light_lookout='Bone Scout')
        elif mission_id == 'goblin_boar_riders':
            names.update(guard='Boar Vanguard',skirmisher='Mounted Skirmisher',lookout='Rider Slinger',
                         ringleader='Boar Ringleader',pilferer='Young Rider',light_lookout='Young Rider Slinger')
        else:
            names.update(lookout='Highway Lookout',pilferer='Road Raider',light_lookout='Road Lookout')
    personality = 'guardian' if role=='guard' else 'strategist' if role=='snarer' else 'survivor' if 'lookout' in role else 'opportunist'
    recruit = dict(job_id=job, job_practice=0, learned_skills=list(keys), equipped_skills=list(keys),
                   skill_slots=5, attributes=attributes, combat_specialization=names[role], personality_id=personality)
    from .recruit_perks import assign
    assign(recruit,mission_id,role,unit['id']+unit['name']+str(variation))
    if mission_id == 'goblin_boar_riders':
        recruit.setdefault('traits',[]).append('rider')
    recruit.update(origin_mission_id=mission_id)
    skills, passives, modifiers = snapshot(recruit)
    light = role in {'pilferer','light_lookout'}
    heavy=role in {'guard','enforcer','warden','bruiser'}
    hp = (17 if mission_id in WORKSITE_IDS else 19) if light else 28 if heavy else 24 if goblin else 24 if mission_id in PRISON_IDS else 23
    # Shared VIT/racial rounding must not make the three-body layouts exceed
    # the two-body encounter budget. These remain allocation targets, not
    # post-formula HP overrides.
    if mission_id in WORKSITE_IDS and not light and not heavy:
        hp = 25
    elif mission_id == 'supply_watch' and not light and not heavy:
        hp = 26
    attack = 3 if light else 5 if heavy else 4
    if mission_id in PREPARED_IDS:
        count = len(rosters[mission_id][variation])
        hp = (24 if count == 4 else 20) if mission_id == 'frontier_watch_defense' else (28 if count == 2 else 20)
        attack = (4 if count == 4 else 3) if mission_id == 'frontier_watch_defense' else (5 if role == 'guard' else 4) if count == 2 else 3
        names.update(guard='Watch Raider' if mission_id == 'frontier_watch_defense' else 'Wagon Guard',
                     snarer='Raider Snarer' if mission_id == 'frontier_watch_defense' else 'Escort Snarer',
                     pilferer='Light Raider' if mission_id == 'frontier_watch_defense' else 'Light Escort',
                     light_lookout='Raider Lookout' if mission_id == 'frontier_watch_defense' else 'Escort Lookout')
        recruit['combat_specialization'] = names[role]
    ranged = job == 'ranger'
    unit.update(hp=hp,max_hp=hp,attack=attack,
                armor=1 if role=='guard' else 0,move=4 if goblin or job=='rogue' else 3,
                initiative=16 if goblin else 12+index,evasion=12 if goblin else 6 if job=='rogue' else 0,
                weapon='Weighted Sling' if ranged else 'Worn Cudgel' if role=='guard' else 'Notched Knife',
                weapon_type='bow' if ranged else 'club' if role=='guard' else 'dagger',
                melee_style='blunt' if role=='guard' else 'stab',
                attack_range=3 if ranged else 1,attack_elevation_rule='ballistic' if ranged else 'melee',
                armor_material='leather',job_id=job,ability_version=1,martial_version=1,
                skills=skills,passives=passives,skill_slot_order=list(keys),perk_modifiers=modifiers,origin_perks=list(recruit['traits']),
                reactions=[deepcopy(p['reaction']) for p in passives if p.get('reaction')],
                encounter_profile='road_enforcer' if role=='guard' else 'road_cutpurse',
                combat_specialization=names[role],job_description=names[role]+': '+JOBS[job]['description'],
                personality_id=personality,recruitable_snapshot=deepcopy(recruit),
                strength=attributes['str'],agility=attributes['agi'],intelligence=attributes['int'],
                corpse_item='weighted_sling' if ranged else 'watchmans_cudgel' if role=='guard' else 'balanced_dagger',
                corpse_item_chance=20)
    from .recruit_perks import decorate_enemy
    if mission_id in D_IDS:
        # Goblin/Human role HP already matches the audited E-rank racial kits.
        # Apply the Undead profile to the comparable role before rank scaling.
        # Core attributes above already scaled and also persist on recruitment.
        from .races import race_gameplay
        racial = race_gameplay(unit['race'])
        base_hp = max(8,round(hp*float(racial['hp_multiplier']))+int(racial['hp_bonus'])) if unit['race']=='Undead' else hp
        unit.update(hp=base_hp,max_hp=base_hp,
                    armor=unit['armor']+int(racial['armor_bonus']),
                    move=max(1,unit['move']+int(racial['move_bonus'])),
                    dexterity=attributes['dex'],vitality=attributes['vit'],luck=attributes['luk'])
        scale_unit(unit,'D',fields=('hp','max_hp','attack','armor'))
        unit['rank_scaling']['attribute_baseline'] = attribute_baseline
        if mission_id == 'bone_patrol':
            unit.update(armor_material='chain',weapon='Chapel Bow' if ranged else 'Chapel Blade',
                        weapon_type='bow' if ranged else 'sword',melee_style='slash')
        # Boar mounts are real units created after encounter placement.
    decorate_enemy(unit,recruit)


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
