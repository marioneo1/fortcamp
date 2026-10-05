"""Solo camp production, bounded upgrades and persistent personal trade offers."""
import hashlib
import random
import time
from copy import deepcopy
from .starter_equipment import STARTER_PRICES

JOBS = {
    'wood': ('Logging clearing', 'building', 18),
    'stone': ('Stone outcrop', 'building', 16),
    'scrap': ('Salvage patch', 'scavenging', 10),
    'food': ('Foraging grounds', 'survival', 12),
    'medicine': ('Herb patch', 'medicine', 3),
}
PRODUCERS = {'lumbermill':'wood','quarry':'stone','salvage_yard':'scrap','farm':'food','herb_garden':'medicine'}
POINT_COST = {'E':1,'D':1,'C':2,'B':3,'A':4,'S':5}
CLAIM_COSTS = [{'wood':12,'stone':8,'gold':10}, {'wood':25,'stone':20,'gold':35},
               {'wood':45,'stone':40,'gold':90}, {'wood':80,'stone':70,'gold':200},
               {'wood':130,'stone':120,'gold':450}]
EXPANSIONS = [(16,8,{'wood':30,'stone':20,'gold':20}), (16,12,{'wood':60,'stone':45,'gold':60}),
              (20,12,{'wood':100,'stone':90,'gold':150})]
MEALS = {
    'trail_meal': {'name':'Trail Meal','food':4,'description':'Consume before departure: +1 Survival for one expedition.'},
    'study_meal': {'name':'Study Meal','food':5,'description':'Consume: +8 practice toward one noncombat proficiency.'},
    'rest_meal': {'name':'Rest Meal','food':6,'description':'Consume: reduce remaining injury recovery by 30 minutes.'},
}
RESEARCH = {'barracks':{'gold':15,'wood':8},'alchemy_lab':{'gold':25,'medicine':2},'arcane_sanctum':{'gold':45,'stone':12}}
FACTIONS = {
    'hedgerow': {'name':'Hedgerow Watch','goods':['trappers_roll','field_pack','short_bow','watch_ford_medallion']},
    'meridian': {'name':'Meridian Artificers','goods':['hard_hat','scrap_hatchet','ember_charm','meridian_workshop_ward']},
    'lantern': {'name':'Lantern Caravan','goods':['work_boots','medic_coat','supply_satchel','lantern_route_compass']},
}
PRACTICE_THRESHOLDS = [(12,'basic'),(60,'skilled'),(180,'expert'),(480,'master')]

def initialize(state, now=None):
    now = int(time.time()) if now is None else int(now)
    resources=state.setdefault('resources',{})
    # One-time value-preserving construction-currency migration.
    if not state.get('economy_v1'):
        resources['stone']=resources.get('stone',0)+resources.pop('cloth',0)
        state['economy_v1']=True
    resources.setdefault('stone',0)
    state.setdefault('camp_work','balanced')
    state.setdefault('production',{'settled_at':now,'fractions':{}})
    state.setdefault('base_size',{'w':12,'h':8})
    state.setdefault('claim_upgrade',0)
    state.setdefault('factions',{key:0 for key in FACTIONS})
    for key in FACTIONS:
        state['factions'].setdefault(key, 0)
    state.setdefault('meals',{})
    state.setdefault('trade',{'seed':hashlib.sha256(str(state.get('created_at',now)).encode()).hexdigest()[:16],'visits':{}})

def pay(state,cost):
    if any(state['resources'].get(key,0)<amount for key,amount in cost.items()):
        raise ValueError('Not enough resources: '+', '.join(f'{amount} {key}' for key,amount in cost.items()))
    for key,amount in cost.items():state['resources'][key]-=amount

def practice(character,track,amount):
    from .content import PERK_LEVELS
    progress=character.setdefault('practice',{})
    current=character.setdefault('perks',{}).get(track,'none')
    floor=next((threshold for threshold,level in PRACTICE_THRESHOLDS if level==current),0)
    progress[track]=max(float(progress.get(track,0)),floor)+amount
    for threshold,level in PRACTICE_THRESHOLDS:
        if progress[track]>=threshold and PERK_LEVELS.index(level)>PERK_LEVELS.index(character['perks'].get(track,'none')):
            character['perks'][track]=level

def settle(state,now=None):
    from .content import PERK_LEVELS
    initialize(state,now)
    now=int(time.time()) if now is None else int(now)
    production=state['production'];previous=int(production['settled_at'])
    if now<=previous:return
    cap=12+6*sum(b['type']=='storage_shed' for b in state.get('buildings',[]))
    hours=min(now-previous,cap*3600)/3600
    production['settled_at']=now
    rates={key:0.0 for key in JOBS}
    workers=[]
    player=next((c for c in state.get('characters',[]) if c.get('is_player')),None)
    if player and player.get('status')=='idle' and not player.get('assignment'):
        focus=state['camp_work'];targets=list(JOBS) if focus=='balanced' else [focus] if focus in JOBS else []
        workers.append((player,targets))
    for building in state.get('buildings',[]):
        key=PRODUCERS.get(building['type'])
        if not key:continue
        for cid in building.get('assigned',[]):
            character=next((c for c in state['characters'] if c['id']==cid and c.get('status')=='idle'),None)
            if character:workers.append((character,[key]))
    for character,targets in workers:
        for key in targets:
            track=JOBS[key][1];rank=PERK_LEVELS.index(character.get('perks',{}).get(track,'none'))
            level=max((b.get('level',1) for b in state.get('buildings',[]) if PRODUCERS.get(b['type'])==key),default=0)
            rates[key]+=JOBS[key][2]/len(targets)*(1+.15*rank)*(1+.3*level)
            practice(character,track,hours*2/len(targets))
    fractions=production['fractions']
    for key,rate in rates.items():
        value=float(fractions.get(key,0))+hours*rate
        whole=int(value);fractions[key]=value-whole
        state['resources'][key]=state['resources'].get(key,0)+whole

def public_economy(state):
    return {'jobs':{key:{'name':value[0],'track':value[1],'base_per_hour':value[2]} for key,value in JOBS.items()},
            'producers':PRODUCERS,'point_cost':POINT_COST,'claim_costs':CLAIM_COSTS,
            'expansions':[{'w':w,'h':h,'cost':cost} for w,h,cost in EXPANSIONS], 'meals':MEALS,'factions':FACTIONS,'research':RESEARCH}

def camp_action(state,action,**data):
    from .content import BUILDINGS, ITEMS, PERK_TRACKS
    settle(state)
    if action=='focus':
        focus=data.get('focus')
        if focus not in {*JOBS,'balanced','rest'}:raise ValueError('Unknown camp work')
        state['camp_work']=focus
    elif action=='expand':
        level=int(state.get('expansion_level',0))
        if level>=len(EXPANSIONS):raise ValueError('All plots are already unlocked')
        w,h,cost=EXPANSIONS[level];pay(state,cost)
        state['base_size']={'w':w,'h':h};state['expansion_level']=level+1
    elif action=='claims':
        if not any(b['type']=='guild_hall' for b in state['buildings']):raise ValueError('Build a Guild Hall first')
        level=int(state['claim_upgrade'])
        if level>=len(CLAIM_COSTS):raise ValueError('Maximum contract allowance reached')
        pay(state,CLAIM_COSTS[level]);state['claim_upgrade']=level+1
    elif action=='upgrade':
        building=next((b for b in state['buildings'] if b['id']==data.get('building_id')),None)
        if not building or building['type'] not in PRODUCERS:raise ValueError('Choose a production building')
        level=building.get('level',1)
        if level>=3:raise ValueError('Maximum production level reached')
        pay(state,{'wood':20*level,'stone':15*level,'gold':10*level*level});building['level']=level+1
    elif action=='cook':
        if not any(b['type']=='kitchen' for b in state['buildings']):raise ValueError('Build a Kitchen first')
        meal=data.get('meal');count=max(1,min(10,int(data.get('count',1))))
        if meal not in MEALS:raise ValueError('Unknown recipe')
        character=next(c for c in state['characters'] if c.get('is_player'))
        if character.get('status')!='idle':raise ValueError('Finish your expedition before cooking')
        pay(state,{'food':MEALS[meal]['food']*count});state['meals'][meal]=state['meals'].get(meal,0)+count
        practice(character,'alchemy',count*2)
    elif action=='research':
        blueprint=data.get('blueprint')
        if blueprint not in RESEARCH:raise ValueError('Unknown blueprint research')
        if blueprint in state['learned_blueprints']:raise ValueError('Blueprint already learned')
        pay(state,RESEARCH[blueprint]);state['learned_blueprints'].append(blueprint)
    elif action=='hire':
        raise ValueError('Camp hiring is unavailable. Find recruits through missions.')
    elif action=='eat':
        meal=data.get('meal');character=next((c for c in state['characters'] if c['id']==data.get('character_id')),None)
        if not character or character.get('status')=='mission':raise ValueError('Choose a character at camp')
        if state['meals'].get(meal,0)<1:raise ValueError('No prepared meal available')
        if meal=='trail_meal':character['prepared_meal']='trail_meal'
        elif meal=='study_meal':
            track=data.get('track','building')
            if track not in PERK_TRACKS or track=='combat':raise ValueError('Choose a work proficiency')
            practice(character,track,8)
        elif meal=='rest_meal':
            if character.get('status')!='incapacitated':raise ValueError('This character does not need injury recovery')
            character['recovers_at']=max(int(time.time()),int(character['recovers_at'])-1800)
        else:raise ValueError('Unknown meal')
        state['meals'][meal]-=1
    else:raise ValueError('Unknown camp action')

def trade_view(state,player_key,now=None):
    from .content import ITEMS
    initialize(state,now);now=int(time.time()) if now is None else int(now)
    # One independent daily arrival check per player. Event/region can influence future pools.
    day=now//86400;visits=state['trade']['visits'];key=str(day)
    if key not in visits:
        rng=random.Random(f'merchant:{player_key}:{day}')
        visiting=rng.random()<.45
        pool=['training_manual','field_pack','short_bow','scrap_hatchet','medic_coat']
        chosen=rng.sample(pool,3) if visiting else []
        if chosen and rng.random()<.12:chosen[-1]='merchant_wayfarer_ring'
        visits[key]={'arrived':visiting,'offers':[{'id':f'visitor:{day}:{iid}','item':iid,'price':rng.randint(18,35) if ITEMS[iid].get('rarity')!='rare' else rng.randint(65,95),'stock':1} for iid in chosen]}
        for old in list(visits):
            if int(old)<day-2:del visits[old]
    # Persist a full browsing day from first encounter, including arrivals while absent.
    visit=visits[key]
    if visit['arrived']:visit.setdefault('expires_at',now+86400)
    live=[v for v in visits.values() if v.get('arrived') and v.get('expires_at',0)>now]
    merchant=live[0] if live else None
    # A faction trader stays for 48 hours; each player has a stable rotation offset.
    rotation_slot = now // (48 * 3600)
    faction_ids = list(FACTIONS)
    offset = int(hashlib.sha256(player_key.encode()).hexdigest()[:8], 16) % len(faction_ids)
    active_faction = faction_ids[(rotation_slot + offset) % len(faction_ids)]
    rotation_visits = state['trade'].setdefault('rotation_visits', {})
    active_faction = rotation_visits.setdefault(str(rotation_slot), active_faction)
    for old in list(rotation_visits):
        if int(old) < rotation_slot - 3:
            del rotation_visits[old]
    next_faction = faction_ids[(rotation_slot + offset + 1) % len(faction_ids)]
    from .faction_contracts import available_jobs
    jobs = available_jobs(state)
    factions=[]
    for fid,definition in FACTIONS.items():
        relationship=state['factions'].get(fid,0)
        offers=[]
        for index,iid in enumerate(definition['goods'] if fid == active_faction else []):
            threshold=(0,15,35,65)[index]
            discount = .10 if relationship >= 45 else .05 if relationship >= 20 else 0
            offers.append({'id':f'faction:{rotation_slot}:{fid}:{iid}','item':iid,'price':round((12,30,65,120)[index] * (1-discount)),
                'stock':max(0,1-state['trade'].get('purchases',{}).get(f'{rotation_slot}:{fid}:{iid}',0)),
                'required_relationship':threshold,'locked':relationship<threshold})
        factions.append({'id':fid,'name':definition['name'],'relationship':relationship,'offers':offers,
                         'visiting':fid == active_faction, 'contracts':[j for j in jobs if j['faction'] == fid]})
    # Keep purchase history bounded without resetting current stock.
    for old in list(state['trade'].get('purchases', {})):
        try:
            if int(old.split(':')[0]) < rotation_slot - 3:
                del state['trade']['purchases'][old]
        except ValueError:
            continue
    return {'merchant':deepcopy(merchant),'factions':factions,
            'rotation':{'faction':active_faction,'ends_at':(rotation_slot+1)*48*3600,'next_name':FACTIONS[next_faction]['name']},
            'camp_items':[{'id':f'camp:{iid}', 'item':iid, 'price':price, 'stock':999}
                          for iid,price in [('field_dressing',8),('restorative_tonic',18),('cleansing_salts',14),
                           *STARTER_PRICES.items()]],
            'supplies':[{'resource':'food','price':2},{'resource':'medicine','price':6}]}

def purchase(state,player_key,offer_id,now=None):
    now=int(time.time()) if now is None else int(now)
    view=trade_view(state,player_key,now)
    if offer_id.startswith('supplies:'):
        resource=offer_id.split(':')[1];price={'food':2,'medicine':6}.get(resource)
        if not price:raise ValueError('Unknown supply')
        pay(state,{'gold':price});state['resources'][resource]+=1;return
    offers=[o for f in view['factions'] for o in f['offers']]+(view['merchant']['offers'] if view['merchant'] else [])+view['camp_items']
    offer=next((o for o in offers if o['id']==offer_id),None)
    if not offer or offer.get('locked') or offer['stock']<1:raise ValueError('Offer is unavailable')
    pay(state,{'gold':offer['price']})
    state['inventory'].append({'instance_id':'item_'+hashlib.sha256(f'{player_key}:{offer_id}:{now}:{len(state["inventory"])}'.encode()).hexdigest()[:12],'item_id':offer['item']})
    if offer_id.startswith('visitor:'):
        for visit in state['trade']['visits'].values():
            for original in visit.get('offers',[]):
                if original['id']==offer_id:original['stock']-=1
    elif offer_id.startswith('faction:'):
        _,day,fid,iid=offer_id.split(':');state['trade'].setdefault('purchases',{})[f'{day}:{fid}:{iid}']=1

def earn_relationship(state,mission,outcome):
    initialize(state)
    if outcome not in {'success','critical_success'}:return
    fid=mission.get('faction')
    if fid in FACTIONS:state['factions'][fid]=min(100,state['factions'].get(fid,0)+(5 if outcome=='critical_success' else 3))
