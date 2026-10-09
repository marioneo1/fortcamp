"""Small, saved entry encounters. No character-story rolls or live generated text."""
import random

ELIGIBLE = frozenset({'goblin_pickpockets','ruined_well','supply_watch'})
BEAR_ID = 'radiant_foraging_bear'


def prepare(battle):
    mission = battle.get('encounter_id','').removeprefix('contract:')
    if mission not in ELIGIBLE or 'radiant_encounter' in battle:
        return
    roll = random.Random(f"{battle['seed']}:radiant:foraging_bear:v1").randint(1,100)
    battle['radiant_encounter'] = {'id':'radiant:foraging_bear','roll':roll,'chance':3,'state':'absent'}
    if roll > 3:
        return
    from . import combat as c
    party = c._living(battle,'player')
    scenery={p for obj in battle.get('decorations',[]) if not obj.get('ground_edging') for p in c.occupied_tiles(obj)}
    cells = [(x,y) for y in range(1,battle['height']-1) for x in range(1,battle['width']-1)
             if not c._blocked(battle,x,y)
             and (x,y) not in scenery
             and min((abs(x-u['x'])+abs(y-u['y']) for u in party),default=0)>=6]
    if not cells:
        return
    locals_ = [u for u in c._living(battle,'enemy') if not u.get('wildlife_hostile_all')]
    # Prefer an existing skirmish beside a local, never inside a prop or a wall.
    skirmish = [(p,u) for p in cells for u in locals_
                if abs(p[0]-u['x'])+abs(p[1]-u['y'])==1
                and not c.crossed_walls(battle,p,(u['x'],u['y']))]
    opponent = None
    if skirmish:
        (x,y),opponent=max(skirmish,key=lambda entry:(min(abs(entry[0][0]-u['x'])+abs(entry[0][1]-u['y']) for u in party),entry[1]['id']))
    else:
        x,y = max(cells,key=lambda p:(min(abs(p[0]-u['x'])+abs(p[1]-u['y']) for u in party),p))
    entry=battle['radiant_encounter']
    entry.update(state='pending',position={'x':x,'y':y},
        title='An unexpected third party',
        text='A foraging bear is fighting the local raiders.' if opponent else 'A foraging bear is roaming this battlefield.',
        reward='It attacks both sides. You can finish the contract without killing it; a recovered bear yields a pelt and has a 5% chance to yield Bear Claws.')
    bear=c._enemy(BEAR_ID,'Foraging Bear','raider',x,y)
    bear.update(race='Bear',kind='creature',creature=True,species_profile='foraging_bear',boss=False,hp=34,max_hp=34,
        attack=5,armor=1,move=2,initiative=7,evasion=0,movement_type='ground',
        weight=90,strength=8,agility=3,intelligence=2,weapon='Claws',melee_style='slash',
        attack_range=1,attack_elevation_rule='melee',portrait='/assets/animals-v1/bear.png',
        portrait_full='/assets/animals-v1/bear.png',racial_resistances=[],racial_weaknesses=[],
        wildlife_hostile_all=True,radiant_id='radiant:foraging_bear',combat_specialization='Independent Wildlife',corpse_item='bear_claws',corpse_item_chance=5,
        corpse_bonus_items=['thick_bear_pelt'],corpse_gold=(0,0),
        skills=[],passives=[],reactions=[],statuses=[],guarding=False)
    battle['units'][BEAR_ID]=bear
    battle['turn_order']=sorted(battle['units'],key=lambda uid:(-battle['units'][uid]['initiative'],uid))
    battle['turn_index']=0
    if opponent:
        # Authored arrival state: the fight predates the party, with no skipped
        # current-turn attack, status proc, death, or invisible animation to replay.
        bear['hp']-=6
        opponent['hp']=max(1,opponent['hp']-4)
        entry['skirmish_target_id']=opponent['id']
        battle['log'].append(f"The guild arrives during a skirmish: {opponent['name']} and a wild bear are already wounded. The bear belongs to neither side.")
    else:
        battle['log'].append('A wild bear is already on the battlefield. It belongs to neither side.')


def pending(battle):
    return battle.get('radiant_encounter',{}).get('state')=='pending'


def choose(battle, choice):
    if not pending(battle) or choice != 'continue':
        raise ValueError('Acknowledge the bear encounter before continuing')
    battle['radiant_encounter']['state']='active'


def corpse_rewards(state, result, unit):
    # Called only for actually recovered dead bodies by the normal completion path.
    import uuid
    for item_id in unit.get('corpse_bonus_items',[]):
        state.setdefault('inventory',[]).append({'instance_id':f'item_{uuid.uuid4().hex}','item_id':item_id})
        result['rewards'].setdefault('items',[]).append(item_id)
