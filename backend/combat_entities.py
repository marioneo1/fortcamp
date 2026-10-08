"""Temporary owner-linked units. Fixed profiles, finite resources, no initiative turns."""
from copy import deepcopy

PROFILES = {
    'scrap_turret': {'name':'Scrap Turret','policy':'automatic','stationary':True,'hp':16,'armor':1,'attack':6,'range':4,'move':0,'rule':'ballistic','pool':'components','cost':2},
    'guard_automaton': {'name':'Guard Automaton','policy':'commanded','hp':24,'armor':2,'attack':7,'range':1,'move':2,'rule':'melee','pool':'components','cost':3},
    'companion': {'name':'Bonded Wolf','policy':'commanded','hp':18,'armor':0,'attack':7,'range':1,'move':3,'rule':'melee','pool':'capacity','cost':1,'sprite':'bonded_wolf'},
    'wisps': {'name':'Wisp','policy':'automatic','hp':8,'armor':0,'attack':3,'range':3,'move':2,'rule':'line_of_effect','pool':'capacity','cost':2,'count':2,'flying':True,'sprite':'blue_wisp'},
    'bulwark': {'name':'Stone Bulwark','policy':'commanded','hp':30,'armor':3,'attack':4,'range':1,'move':1,'rule':'melee','pool':'capacity','cost':2,'sprite':'stone_bulwark'},
    'grove_sprite': {'name':'Grove Sprite','policy':'automatic','hp':10,'armor':0,'attack':0,'range':2,'move':2,'rule':'line_of_effect','pool':'capacity','cost':1,'heal':3},
    'manifestation': {'name':'Astral Guardian','policy':'commanded','hp':32,'armor':2,'attack':9,'range':1,'move':2,'rule':'melee','pool':'capacity','cost':2,'once':True,'sprite':'astral_guardian'},
}


def owned(battle, owner):
    return [u for u in battle['units'].values() if u.get('temporary') and u.get('owner_id')==owner['id']
            and u.get('alive') and u.get('conscious',True) and not u.get('extracted')]


def usage(battle, owner):
    # A pair reserves two points collectively, not two per member.
    units=[u for u in owned(battle,owner) if u['resource_pool']=='capacity']
    groups={u['deployment_id']:u['capacity_cost'] for u in units if not u.get('summoner_creature')}
    return sum(groups.values())+sum(u['capacity_cost'] for u in units if u.get('summoner_creature'))


def available(battle,owner,kind):
    if kind not in PROFILES:raise ValueError('Unsupported deployment')
    profile=PROFILES[kind]
    if profile.get('once') and kind in owner.get('deployments_used',[]):return False
    if profile['pool']=='components':return owner.get('components',3)>=profile['cost']
    return usage(battle,owner)+profile['cost']<=owner.get('summon_capacity',2)


def deploy(battle,owner,kind,positions):
    if not available(battle,owner,kind):raise ValueError('Not enough Components/capacity, or this deployment is spent')
    profile=PROFILES[kind];count=profile.get('count',1)
    if len(positions)!=count:raise ValueError('Not enough legal deployment cells')
    serial=battle.get('entity_serial',0)+1;deployment=f"deployment_{serial}"
    units=[]
    for i,(x,y) in enumerate(positions):
        uid=f'entity_{serial}_{i}'
        unit={'id':uid,'name':profile['name']+(f' {i+1}' if count>1 else ''),'kind':'summon',
              'temporary':True,'owner_id':owner['id'],'deployment_id':deployment,'entity_kind':kind,
              'resource_pool':profile['pool'],'capacity_cost':profile['cost'],'policy':profile['policy'],
              'stationary':profile.get('stationary',False),'deployed_at':owner.get('ability_activation',0),
              'team':owner['team'],'x':x,'y':y,'hp':profile['hp'],'max_hp':profile['hp'],'armor':profile['armor'],
              'attack':profile['attack'],'attack_range':profile['range'],'attack_elevation_rule':profile['rule'],
              'move':profile['move'],'initiative':0,'evasion':0,'movement_type':'flying' if profile.get('flying') else 'ground',
              'weapon':profile['name'],'strength':3,'intelligence':4,'weight':2,'race':'Automaton' if profile['pool']=='components' else 'Summon',
              'alive':True,'conscious':True,'condition':'active','moved':False,'acted':False,'statuses':[],
              'skills':[],'reactions':[],'gear_rules':{},'perk_modifiers':{},'racial_resistances':[],
              'racial_weaknesses':[],'sprite':profile.get('sprite',kind),'entity_output':profile.get('heal',profile['attack']),
              'status_version':1,'ability_version':1,'ability_activation':0,'ability_state':{},'capture_weapon':None,
              'portrait':profile.get('portrait',''),'loyalty':100,'player_avatar':False}
        if kind=='wisps' and i==1:unit['sprite']='amber_wisp'
        units.append(unit)
    battle['entity_serial']=serial
    if not owner.get('ability_version'):owner['ability_version']=1
    if profile['pool']=='components':owner['components']=owner.get('components',3)-profile['cost']
    if kind not in owner.setdefault('deployments_used',[]):owner['deployments_used'].append(kind)
    for unit in units:battle['units'][unit['id']]=unit
    battle['log'].append(f"{owner['name']} deploys {profile['name']}. It can act from the next owner activation.")
    return units


def can_command(battle,owner,entity):
    return bool(owner.get('alive') and owner.get('conscious',True) and not owner.get('extracted') and not owner.get('carried_by')
                and entity and not entity.get('engineer_machine') and entity in owned(battle,owner) and entity['deployed_at']<owner.get('ability_activation',0)
                and not owner.get('acted') and not owner.get('forced_skip')
                and not entity.get('forced_skip') and not entity.get('panicked'))


def cleanup(battle,active):
    for unit in battle['units'].values():
        if not unit.get('temporary'):continue
        owner=battle['units'].get(unit['owner_id'])
        if not owner or not active(owner) or not active(unit):
            if unit.get('engineer_machine'):
                unit.update(alive=False,conscious=False,condition='dead',hp=0)
                continue
            unit.update(extracted=True,alive=False,conscious=False,condition='dismissed')


def dismiss(battle,owner,entity):
    if entity not in owned(battle,owner):raise ValueError('Choose an owned active deployment')
    # Dismissing either member releases the whole bonded pair and its capacity.
    for unit in owned(battle,owner):
        if unit['deployment_id']==entity['deployment_id']:
            unit.update(extracted=True,alive=False,conscious=False,condition='dismissed')
    battle['log'].append(f"{owner['name']} dismisses {entity['name']}.")


def start_owner(battle,owner,start):
    stamp=owner.get('ability_stamp')
    for unit in owned(battle,owner):
        if unit.get('owner_stamp')==stamp:continue
        unit['owner_stamp']=deepcopy(stamp)
        unit['status_activation']=['owner',owner['id'],owner.get('ability_activation',0)]
        unit['moved']=False;unit['acted']=False
        unit.pop('movement_origin',None);unit.pop('movement_path',None)
        start(unit)


def budget(owner):
    return max(0,min(20,int(owner.get('entity_output_budget',6))))
