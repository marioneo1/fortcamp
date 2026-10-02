"""Capture is an action-limited probability check, not STR damage with a safe finisher."""
import math

def capture_preview(actor, target):
    profile = actor.get('capture_weapon')
    if not profile: return None
    attrs = actor.get('capture_attributes', {'str':actor.get('strength',4), 'dex':4, 'int':actor.get('intelligence',4)})
    values = [max(1, int(attrs.get(k,4))) for k in ('str','dex','int')]
    # Raising one attribute alone has much less effect than a balanced build.
    balanced = min(values) + (sum(values)/3-min(values))*.35
    stats = 16 * math.log1p(balanced/8)
    wounded = 36 * (1-max(0,min(1,target['hp']/max(1,target['max_hp']))))
    perks = actor.get('perk_modifiers', {})
    bonus = perks.get('capture_chance',0) + actor.get('gear_rules',{}).get('capture_chance',0)
    if target['hp'] <= target['max_hp']/2: bonus += perks.get('wounded_capture',0)
    boss = bool(target.get('boss') or target.get('kind') == 'chieftain')
    if boss: bonus += perks.get('boss_capture',0)
    statuses = {s['id'] for s in target.get('statuses',[])}
    setup = 10 if statuses & {'stun','sleep','ambush_sleep','freeze'} else 6 if statuses & {'bind','paralyze'} else 0
    chance = profile['base'] + stats + wounded + bonus + setup - target.get('evasion',0)*.5 - target.get('armor',0)*.6
    if target.get('guarding'): chance -= 8
    if boss: chance -= 20
    return {'chance':max(2,min(60 if boss else 95,round(chance))), 'capture':True, 'damage_bonus':0,
            'description':'One capture check. Failure deals no damage; success leaves the target unconscious. Lower HP and control effects help.',
            'balanced_rating':round(balanced,1)}

def apply_capture_content(items, missions, general, events, perks, effects):
    definitions = {
        'frayed_capture_net':('Frayed Capture Net','common',8,1,'melee','E','goblin_net_bow'),
        'patrol_capture_net':('Patrol Capture Net','common',16,2,'ballistic','E','goblin_net_bow'),
        'weighted_capture_net':('Weighted Capture Net','uncommon',20,3,'ballistic','D','goblin_net_bow'),
        'wardens_mancatcher':('Warden’s Mancatcher','rare',24,2,'melee','C','hooked_spear'),
        'runebinding_focus':('Runebinding Focus','rare',23,3,'line_of_effect','C','winterglass_grimoire'),
        'prototype_stun_rod':('Prototype Stun Rod','epic',28,2,'melee','B','prism_tuning_fork'),
        'magistrates_seal':('Magistrate’s Binding Seal','legendary',31,3,'line_of_effect','A','oathkeeper_shard'),
        'warcamp_master_mesh':('Warhost Master Mesh','rare',26,3,'ballistic',None,'goblin_net_bow'),
        'starless_containment_lens':('Starless Containment Lens','mythic',35,4,'line_of_effect',None,'starless_gate_sigil'),
    }
    for iid,(name, rarity, base, reach, rule, rank, art) in definitions.items():
        items[iid] = {'name':name,'slot':'weapon','rarity':rarity,'weapon_type':'capture','weapon_scaling':'balanced',
            'power':0,'attack_range':reach,'bonuses':{},'attribute_bonuses':{},'granted_perks':[],
            'tags':['capture']+(['mission_exclusive'] if rank is None else []),
            'capture_weapon':{'base':base,'range':reach,'elevation_rule':rule}, 'icon':f'/assets/catalogue/items/{art}.png',
            'description':f'Capture weapon. Range {reach}; repeated STR/DEX/INT checks instead of damaging attacks. Never kills. Wounded or controlled targets are easier; bosses resist. '+('Frayed starter gear with a low capture chance.' if iid=='frayed_capture_net' else '')}
        if rank: general.append((iid,rank,7))
    # Existing genuine restraint tools become capture weapons; no damage-mode loophole.
    for iid,base,reach in [('goblin_net_bow',20,3),('hunters_bola',18,2),('mooncord_sling',25,4)]:
        item=items[iid];item.update(weapon_type='capture',weapon_scaling='balanced',power=0,
            capture_weapon={'base':base,'range':reach,'elevation_rule':'ballistic'},attack_range=reach)
        item.pop('combat_skill',None);item.pop('on_hit',None)
        item['description']='A dedicated capture weapon. Repeated balanced STR/DEX/INT capture checks; never deals lethal damage. Lower HP and control effects help.'
    for item in items.values():
        item['tags']=[t for t in item.get('tags',[]) if t!='nonlethal']
        skill=item.get('combat_skill')
        if skill and skill.get('nonlethal'):
            skill['nonlethal']=False
            skill['description']=skill['description'].replace(' Knocks out instead of killing.','')+' This is a damaging strike, not a capture action.'
    replacements={
        'worn_mallet':'A carpenter’s discarded mallet. Ordinary STR-based blunt attacks; cannot choose Capture.',
        'knotted_staff':'A worn walking staff. Ordinary STR-based blunt attacks, not a magical focus or capture tool.',
        'weighted_sling':'An ordinary short-range sling. Dazing Stone and its Stun proc provide control, not capture.',
        'mercykeepers_maul':'A heavy armor-piercing maul. Mercy Strike is damaging; neither attack guarantees live capture.',
        'triage_baton':'A medic’s blunt baton. Ordinary damaging attacks; Guard restores 2 HP.',
        'padded_capture_gloves':'Capture-handler gloves. +3 capture chance with a capture weapon and +1 carrying STR. Do not turn other weapons into capture tools.',
        'chieftains_chain_grips':'Grips taken from a live-captured chief. +3 carrying STR; Chain Brace guards an ally and removes Bind.',
    }
    for iid,text in replacements.items(): items[iid]['description']=text
    items['watchmans_cudgel'].update(name='Blackwatch Cudgel', knockout_finisher=5,
        description='An infamous STR-based club. Ordinary attacks can kill. On a killing direct blow, 5% chance to knock the target unconscious instead. Cannot choose Capture.')
    items['padded_capture_gloves']['combat_rules']={'capture_chance':3,'carry_strength':1}
    items['chieftains_chain_grips']['combat_skill']={'id':'chain_brace','name':'Chain Brace','target':'ally','effect':'support',
        'range':2,'elevation_rule':'physical_care','scaling':'int','heal':0,'guard_ally':True,'cleanses':['bind'],
        'description':'One shared technique use per battle. Guard a conscious ally and remove Bind at range 2 with line of sight. Does not capture or revive.'}
    perks['captor']={'name':'Captor','description':'Trained to restrain dangerous targets without killing them.',
        'effect':'+3 capture chance with dedicated capture weapons. Ordinary blunt weapons remain lethal.', 'modifiers':{'combat':{'capture_chance':3}}}
    effects['captor']={'combat':{'capture_chance':3}}
    perks['arcane_apprentice']={'name':'Arcane Apprentice','description':'A beginning mage with a general magical education.',
        'effect':'+1 INT. Does not choose an element or permanently lock your equipment.', 'modifiers':{'attributes':{'int':1}}}
    effects['arcane_apprentice']={'attributes':{'int':1}}
    missions['goblin_warcamp'].setdefault('reward_rolls',[]).append({'source':'chief’s restraint mesh','chance':3,'critical_bonus':2,'reward':{'item':'warcamp_master_mesh'}})
    missions['door_between_dead_stars'].setdefault('reward_rolls',[]).append({'source':'sealed containment lens','chance':2,'critical_bonus':2,'requires_chain_parent':True,'reward':{'item':'starless_containment_lens'}})
    for event,iid in [('goblin_warhost','weighted_capture_net'),('arcane_convergence','runebinding_focus'),('starfall_omen','prototype_stun_rod')]:
        if event in events: events[event].setdefault('loot',[]).append((iid,'D' if iid=='weighted_capture_net' else 'C' if iid=='runebinding_focus' else 'B',6))
