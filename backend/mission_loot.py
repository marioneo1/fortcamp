"""Drop checks, rarity rolls, mixed faction pools, and contract exclusives."""
from copy import deepcopy
RARITY_WEIGHTS={
 'E':{'common':80,'uncommon':20},'D':{'common':60,'uncommon':32,'rare':8},
 'C':{'common':42,'uncommon':38,'rare':18,'epic':2},'B':{'common':25,'uncommon':35,'rare':32,'epic':8},
 'A':{'common':15,'uncommon':25,'rare':40,'epic':17,'legendary':3},
 'S':{'common':5,'uncommon':15,'rare':40,'epic':28,'legendary':10,'mythic':2}}

def gear(name,slot,rarity,perks,description,**fields):
    return {'name':name,'slot':slot,'rarity':rarity,'tags':['mission_exclusive'],'bonuses':{},'attribute_bonuses':{},'granted_perks':perks,'description':description,**fields}

SIGNATURE_ITEMS={
 'signal_lens':gear('Signal-Lens Charm','accessory','rare',['scout'],'A relay lens recovered by reading the signal fire. Improves movement and initiative.'),
 'ledger_ring':gear('Toll Clerk’s Signet','accessory','rare',['precision_core'],'A signet identifying the clerk who exposed the tribute route. Grants +5 accuracy.',attribute_bonuses={'int':1}),
 'chapel_thread':gear('Chapel Binding Thread','accessory','rare',['exorcist'],'Recovered without disturbing the chapel dead. Supports magic checks and attacks against Deathless.'),
 'marshal_hook':gear('Warhost Marshal’s Hook','weapon','epic',['guard'],'The hooked spear of an unexpectedly powerful commander. Grants armor for a fighter holding the line.',attribute_bonuses={'str':2},weapon_type='spear',weapon_scaling='str',power=2),
 'oathkeeper_shard':gear('Oathkeeper’s Ward','offhand','epic',['magic_resistance','graveward'],'A ward recovered from the chapel oathkeeper. Reduces magical damage and helps fight Deathless.'),
 'retrieval_seal':gear('Banner Retrieval Seal','accessory','epic',['engineer','bannerbreaker'],'The seal of the officer sent to recover the ledger. Enables technical approaches and improves armor and initiative.'),
 'warcamp_command_spur':gear('Warcamp Command Spur','feet','rare',['pathfinder'],'The warcamp commander’s route-marked spur. Grants movement and survival capability.',attribute_bonuses={'agi':1}),
 'highway_guard_mantle':gear('Highway Guard Mantle','body','rare',['guard'],'A reinforced mantle recovered from the occupied highway. Grants an extra point of armor.',attribute_bonuses={'vit':1}),
}
SCENE_BONUSES={key:{'source':SIGNATURE_ITEMS[key]['name'],'chance':35,'critical_bonus':10,'reward':{'item':key}} for key in ('signal_lens','ledger_ring','chapel_thread')}
SCENE_BONUSES['ledger_ring_intact']={'source':'intact convoy cipher','chance':60,'critical_bonus':10,'reward':{'item':'ledger_ring'}}
SCENE_BONUSES['watch_contact']={'source':'watch training','chance':25,'critical_bonus':10,'reward':{'standalone_perk':'guard'}}
BOSS_BONUSES={'goblin_smoke_signals':'marshal_hook','black_banner_ledger':'retrieval_seal','bell_beneath_mud':'oathkeeper_shard'}

def apply_loot(items,missions):
    items.update(SIGNATURE_ITEMS)
    for mission_id,mission in missions.items():
        if mission_id.startswith(('goblin','hobgoblin')):mission['loot_faction']='goblin'
    for mission_id,item_id in [('goblin_warcamp','warcamp_command_spur'),('highway_ambush','highway_guard_mantle')]:
        missions[mission_id].setdefault('reward_rolls',[]).append({'source':'contract exclusive','chance':18,'critical_bonus':12,'reward':{'item':item_id}})
        missions[mission_id].setdefault('reward_preview',[]).append(f"Exclusive: {items[item_id]['name']} (drop chance)")

def scene_reward_template(template,analysis):
    mission=deepcopy(template)
    mission['chain_reward_eligible']=bool(analysis.get('chain_parent_id'))
    mission['reward_rolls']=[roll for roll in mission.get('reward_rolls',[]) if not roll.get('requires_chain_parent') or analysis.get('chain_parent_id')]
    for key in analysis.get('scene',{}).get('bonus_keys',[]):
        if key in SCENE_BONUSES:mission.setdefault('reward_rolls',[]).append(deepcopy(SCENE_BONUSES[key]))
    if analysis.get('scene_boss'):
        key=BOSS_BONUSES.get(analysis.get('scene_template_id'))
        if key:mission.setdefault('reward_rolls',[]).append({'source':'unexpected commander','chance':28,'critical_bonus':12,'reward':{'item':key}})
    return mission

def roll_item_pool(mission,rank,rng,items,general,event,ranks,force_faction=False):
    eligible=lambda table:[(iid,weight) for iid,minrank,weight in table if iid in items and ranks.index(minrank)<=ranks.index(rank) and 'mission_exclusive' not in items[iid].get('tags',[])]
    common=eligible(general);faction=eligible(event.get('loot',[])) if event else []
    faction=eligible(mission.get('loot_pool',[])) or faction
    if not faction and (mission.get('event')=='goblin_warhost' or mission.get('loot_faction')=='goblin'):
        faction=[(iid,8) for iid in ('goblin_notched_axe','goblin_net_bow','rusty_knife','short_bow','ironcap_buckler','warhost_banner','smokecaller_staff','crooked_shaman_staff') if iid in items and items[iid].get('rarity','common') in RARITY_WEIGHTS[rank]]
    table=faction if faction and (force_faction or rng.randint(1,100)<=60) else common
    source='faction cache' if table is faction else 'general cache'
    groups={}
    for iid,weight in table:groups.setdefault(items[iid].get('rarity','common'),[]).append((iid,weight))
    rarities=[(r,w) for r,w in RARITY_WEIGHTS[rank].items() if r in groups]
    if not rarities:return None,source,None
    rarity=rng.choices([r for r,w in rarities],weights=[w for r,w in rarities],k=1)[0]
    entries=groups[rarity];iid=rng.choices([i for i,w in entries],weights=[w for i,w in entries],k=1)[0]
    return iid,source,rarity
