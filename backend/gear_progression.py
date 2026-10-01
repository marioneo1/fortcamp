"""Slot-balanced gear, positional builds and authored independent discoveries."""
from copy import deepcopy
from .gear_expansion import weapon,skill

def armor(name,slot,rarity,description,attributes=None,perks=None,rules=None,**extra):
    return {'name':name,'slot':slot,'rarity':rarity,'description':description,
            'bonuses':{},'attribute_bonuses':attributes or {},'granted_perks':perks or [],
            'tags':[],'combat_rules':rules or {},**extra}

SLOT_GEAR={
 'padded_travel_hood':armor('Padded Travel Hood','head','common','An ordinary padded hood for a first expedition.',{'vit':1}),
 'surveyors_visor':armor('Surveyor’s Visor','head','uncommon','An open visor for a scout who needs to move before the line closes.',perks=['scout']),
 'cinder_visor':armor('Cinder Visor','head','rare','A smoked visor that reduces fire damage and the chance of weapon-inflicted Burn.',rules={'resistances':['fire','burn']}),
 'bogkeeper_mask':armor('Bogkeeper’s Mask','head','rare','A fitted herb-filter mask. Prevents weapon-inflicted Poison; useful far beyond the garden wall.',perks=['medic'],rules={'resistances':['poison']}),
 'lastwatch_helm':armor('Lastwatch Helm','head','epic','Enter battle already guarding. The protection lasts until the first hit or the next round.',rules={'opening_guard':True},attributes={'agi':-1,'vit':1}),
 'empty_court_diadem':armor('Empty Court Diadem','head','legendary','A small crown clasp from the Empty Court. Adds damage against bosses without improving ordinary attacks.',rules={'boss_damage':2},attributes={'int':1}),
 'quilted_field_vest':armor('Quilted Field Vest','body','common','Plain traveling armor with no special technique.',{'vit':1}),
 'porters_coat':armor('Porter’s Coat','body','uncommon','A reinforced back panel makes bodies and loose objects easier to carry.',rules={'carry_strength':3}),
 'embersmith_apron':armor('Embersmith’s Apron','body','rare','A heat-resistant leather apron for breaching burning structures.',rules={'resistances':['fire','burn'],'breach_damage':1}),
 'trollstitch_coat':armor('Trollstitch Coat','body','epic','Slow, heavy living stitches restore 2 HP at each new round. Less suited to fast scouts.',attributes={'agi':-1},perks=['regeneration']),
 'roadward_mantle':armor('Roadward Mantle','body','rare','A traveling defender recovers a little health whenever they commit their action to Guard.',rules={'guard_heal':2}),
 'mercythread_robe':armor('Mercythread Robe','body','legendary','The procession’s repaired burial cloth prevents one lethal defeat per battle, leaving its wearer at 1 HP. Escape is still essential.',rules={'lifeline':True},attributes={'vit':-1}),
 'riveted_work_grips':armor('Riveted Work Grips','hands','common','Ordinary grips for a stronger first tool swing.',{'str':1}),
 'padded_capture_gloves':armor('Padded Capture Gloves','hands','uncommon','A padded gauntlet lets its wearer choose melee Subdue even with a sharp or magical weapon.',rules={'subdue_gloves':True}),
 'rescue_gloves':armor('Rescue Gloves','hands','rare','Grip straps provide +6 effective STR for carrying, without increasing attacks or throws.',rules={'carry_strength':6}),
 'breach_gauntlets':armor('Breach Gauntlets','hands','rare','Add 3 damage against destructible structures. Their weight costs agility.',attributes={'agi':-1},rules={'breach_damage':3}),
 'meridian_coil_grips':armor('Meridian Coil Grips','hands','epic','Choose a lightning discharge from the equipped skill list, even while carrying a melee weapon.',combat_skill=skill('Coil Discharge',4,'ignore',2,0),element='lightning'),
 'chieftains_chain_grips':armor('Chieftain’s Chain Grips','hands','legendary','Recovered only by bringing a chieftain back alive. Offer a two-tile nonlethal restraint and improved carrying.',rules={'carry_strength':3},combat_skill=skill('Chain Restraint',2,'melee',2,0,True)),
 'patched_travel_trousers':armor('Patched Travel Trousers','legs','common','Practical clothing with a little extra padding.',{'vit':1}),
 'scout_trail_leggings':armor('Scout’s Trail Leggings','legs','uncommon','A light alternative to plated greaves for moving between objectives.',perks=['pathfinder']),
 'quarry_greaves':armor('Quarry Greaves','legs','uncommon','A survey crew’s plated leggings. Stronger armor in exchange for agility.',attributes={'agi':-1},perks=['guard']),
 'creekwarden_waders':armor('Creekwarden Waders','legs','rare','Cross shallow water for 1 terrain movement cost. Climbing still costs its normal movement.',rules={'water_walk':True}),
 'bramble_chaps':armor('Bramble Chaps','legs','rare','Treated leggings resist weapon-inflicted Poison while leaving the wearer’s hands free.',rules={'resistances':['poison']},attributes={'vit':1}),
 'emberlined_skirt':armor('Emberlined Battle Skirt','legs','rare','Flexible fire-resistant panels reduce fire damage and weapon-inflicted Burn.',rules={'resistances':['fire','burn']},attributes={'dex':1}),
 'astral_fold_wraps':armor('Astral Fold Wraps','legs','epic','Start under a folding ward. Keeps the opening hit from becoming an immediate disaster.',rules={'opening_guard':True},perks=['magic_resistance']),
 'shepherds_carrier_wraps':armor('Shepherd’s Carrier Wraps','legs','legendary','The titan shepherd’s load harness improves carrying and thrown-payload range; it gives no ordinary attack power.',rules={'carry_strength':6,'throw_range':1},attributes={'agi':-1}),
 'softstep_boots':armor('Softstep Boots','feet','common','Ordinary light boots for an early scout.',{'agi':1}),
 'rubble_cleats':armor('Rubble Cleats','feet','uncommon','Destroyed barricades and rubble cost 1 terrain movement. They do not let you climb cliffs.',rules={'rubble_walk':True}),
 'ferrymans_boots':armor('Ferryman’s Boots','feet','rare','An old fisher’s boots make shallow-water movement cost 1; elevation rules still apply.',rules={'water_walk':True},perks=['pathfinder']),
 'counterweight_boots':armor('Counterweight Boots','feet','rare','A stable throwing stance adds one tile of payload range, up to the engine’s five-tile limit.',rules={'throw_range':1}),
 'cometstep_boots':armor('Cometstep Boots','feet','epic','Alien soles grip both shallow water and broken ground. They cannot cross pits.',rules={'water_walk':True,'rubble_walk':True}),
 'starless_anchor_boots':armor('Starless Anchor Boots','feet','legendary','Anchor against the first impact and cross broken terrain normally. They keep their wearer grounded, not flying.',rules={'opening_guard':True,'rubble_walk':True},perks=['magic_resistance']),
 'plank_buckler':armor('Plank Buckler','offhand','common','A first shield. Grants Guard’s passive armor while equipped.',perks=['guard']),
 'riveted_guard_shield':armor('Riveted Guard Shield','offhand','uncommon','Recover 2 HP when choosing Guard. Giving up the attack is part of the tradeoff.',rules={'guard_heal':2}),
 'field_triage_kit':armor('Field Triage Kit','offhand','rare','Recover 4 HP when guarding and gain Field Medic capability. It cannot revive unconscious units.',rules={'guard_heal':4},perks=['medic']),
 'cartmasters_tether_reel':armor('Cartmaster’s Tether Reel','offhand','uncommon','The cartmaster’s intact hauling reel provides +3 effective carrying STR. It must be recovered from a living captive.',rules={'carry_strength':3}),
 'charred_signal_lantern':armor('Charred Signal Lantern','offhand','rare','A fire focus usable beside a sword or bow. Choose Signal Flare instead of the weapon technique.',combat_skill=skill('Signal Flare',3,'ignore',1,0),element='fire'),
 'glacier_page_focus':armor('Glacier Page Focus','offhand','rare','An ice spell focus. Its ranged spell ignores elevation; it does not yet freeze targets.',combat_skill=skill('Glacier Ray',4,'ignore',1,0),element='ice'),
 'tide_bastion':armor('Tide Bastion','offhand','epic','An opening ward and poison-proof lining for a defender crossing contaminated ground.',rules={'opening_guard':True,'resistances':['poison']}),
 'meridian_field_projector':armor('Meridian Field Projector','offhand','legendary','The engine’s salvaged field lens grants a long-range lightning technique to any equipped weapon build.',combat_skill=skill('Field Lance',5,'ignore',3,1),element='lightning'),
 'parcelkeepers_string':armor('Parcelkeeper’s String','accessory','common','An ordinary delivery knot that helps organize salvage.',bonuses={'scavenging':1}),
 'glass_filter_charm':armor('Glass Filter Charm','accessory','uncommon','A small alchemical filter prevents weapon-inflicted Poison.',rules={'resistances':['poison']}),
 'flicker_charm':armor('Flicker Charm','accessory','uncommon','A modest charm reduces fire damage and the chance of weapon-inflicted Burn.',rules={'resistances':['fire','burn']}),
 'field_seal_knot':armor('Field Seal Knot','accessory','rare','Turn a defensive pause into a small recovery. Guard restores 2 HP.',rules={'guard_heal':2}),
 'bloodtrail_pendant':armor('Bloodtrail Pendant','accessory','rare','Adds 2 direct damage against targets already at half HP or lower. Damage-over-time cannot trigger it.',rules={'wounded_damage':2}),
 'second_chance_button':armor('Second-Chance Button','accessory','rare','A storehouse keepsake that prevents one lethal defeat per battle, leaving you at 1 HP. Does not protect against a nonlethal capture.',rules={'lifeline':True}),
 'rootbound_heart':armor('Rootbound Heart','accessory','epic','A preserved seed heart restores 2 HP at each new round. Regeneration gear shares a +4 HP cap.',perks=['regeneration']),
 'deadstar_orbit_pendant':armor('Deadstar Orbit Pendant','accessory','mythic','A pendant found beyond the final signal. Offers a long-range void strike and +2 direct damage against bosses.',rules={'boss_damage':2},combat_skill=skill('Deadstar Orbit',5,'ignore',3,0),element='void'),
 'field_crossbow':weapon('Field Crossbow','common','crossbow',1,'A compact first ranged weapon; shorter normal reach than a longbow.',attack_range=3),
 'brace_hook_pike':weapon('Brace-Hook Pike','uncommon','spear',1,'A low-power pike with +2 damage when breaking structures.',combat_rules={'breach_damage':2}),
 'triage_baton':weapon('Triage Baton','rare','club',2,'A medic’s nonlethal-capable baton. Guard restores 2 HP.',granted_perks=['medic'],combat_rules={'guard_heal':2}),
 'cinderhook_blade':weapon('Cinderhook Blade','rare','sword',2,'Low-power fire steel with a 20% Burn chance. Useful when an enemy resists brute force.',element='fire',on_hit={'id':'burn','chance':20,'turns':2}),
 'serpentglass_wand':weapon('Serpentglass Wand','epic','wand',2,'A poisonous spell focus; living targets face a 25% two-activation Poison chance.',on_hit={'id':'poison','chance':25,'turns':2}),
 'mooncord_sling':weapon('Mooncord Sling','rare','bow',1,'A weak normal ranged attack but a four-tile, armor-piercing nonlethal takedown.',attack_range=3,combat_skill=skill('Mooncord Takedown',4,'ballistic',1,-1,True)),
 'saltward_flail':weapon('Saltward Flail','rare','mace',2,'A chapel flail with Holy affinity and Exorcist’s anti-Deathless bonus.',element='holy',granted_perks=['exorcist']),
 'starburst_caster':weapon('Starburst Caster','legendary','wand',3,'An alien weapon that trades ordinary reach for one distant, armor-piercing discharge.',attack_range=2,element='void',combat_skill=skill('Starburst Discharge',6,'ignore',4,1)),
}

# Each is an independent check on a successful resolution, including pure rolls.
# Low-rank identities never leak into higher-rank/general/event/faction caches.
EXCLUSIVE_DROPS={
 'rats_storehouse':('second_chance_button',1,1,False),
 'outcrop_survey':('quarry_greaves',4,2,False),
 'fishing_line':('ferrymans_boots',3,2,False),
 'goblin_pickpockets':('padded_capture_gloves',3,2,False),
 'herbs_wall':('bogkeeper_mask',3,2,False),
 'salvage_bells':('rescue_gloves',3,2,False),
 'goblin_armory':('breach_gauntlets',5,3,False),
 'meridian_calibration':('meridian_coil_grips',6,4,False),
 'chapel_gate':('saltward_flail',4,2,False),
 'ward_concord':('tide_bastion',4,2,False),
 'black_banner_court':('empty_court_diadem',4,2,True),
 'processions_empty_hearse':('mercythread_robe',4,2,True),
 'meridian_engine':('meridian_field_projector',4,2,True),
 'shepherd_of_titans':('shepherds_carrier_wraps',4,2,True),
 'door_between_dead_stars':('starless_anchor_boots',4,2,True),
}
CAPTURE_DROPS={
 'goblin_warcamp':{'target':'gob_chief','item':'chieftains_chain_grips','chance':4,'secured_bonus':2},
 'goblin_captive_cart':{'target':'cartmaster_vrak','item':'cartmasters_tether_reel','chance':6,'secured_bonus':2},
}
EVENT_EXCLUSIVES={
 'tomb_beyond_sky':('deadstar_orbit_pendant',2,2),
}

def apply_slot_gear(items,missions,general,events):
    items.update(deepcopy(SLOT_GEAR))
    upgrades={
      'gravity_boots':{'water_walk':True,'rubble_walk':True},
      'tower_shield':{'guard_heal':2},'ironcap_buckler':{'opening_guard':True},
      'saints_censer':{'guard_heal':4},'bell_of_last_rites':{'guard_heal':3},
      'starfall_core':{'lifeline':True},
    }
    for iid,rules in upgrades.items():items[iid].setdefault('combat_rules',{}).update(rules)
    exclusive={row[0] for row in EXCLUSIVE_DROPS.values()}|{row['item'] for row in CAPTURE_DROPS.values()}|{row[0] for row in EVENT_EXCLUSIVES.values()}
    for iid in exclusive:items[iid]['tags'].append('mission_exclusive')
    for mid,(iid,chance,critical,chain) in EXCLUSIVE_DROPS.items():
        if mid not in missions:raise ValueError(f'Unknown authored gear mission: {mid}')
        missions[mid].setdefault('reward_rolls',[]).append({'source':items[iid]['name']+' discovery','chance':chance,'critical_bonus':critical,'requires_chain_parent':chain,'reward':{'item':iid}})
        missions[mid].setdefault('reward_preview',[]).append(f"Exclusive: {items[iid]['name']} ({chance}% / {chance+critical}% critical success)")
    # The shrine itself is a rare event contract; its keepsake never enters random caches.
    for mid,(iid,chance,critical) in EVENT_EXCLUSIVES.items():
        if mid not in missions:raise ValueError(f'Unknown event gear mission: {mid}')
        missions[mid].setdefault('reward_rolls',[]).append({'source':'fallen-star reliquary','chance':chance,'critical_bonus':critical,'reward':{'item':iid}})
        missions[mid].setdefault('reward_preview',[]).append(f"Exclusive: {items[iid]['name']} ({chance}% / {chance+critical}% critical success)")
    for mid,drop in CAPTURE_DROPS.items():missions[mid].setdefault('reward_preview',[]).append(f"Live-capture exclusive: {items[drop['item']]['name']} (drop chance)")
    minimum={'common':'E','uncommon':'E','rare':'C','epic':'B','legendary':'A','mythic':'S'}
    weight={'common':9,'uncommon':7,'rare':5,'epic':3,'legendary':1,'mythic':1}
    for iid in SLOT_GEAR:
        if iid not in exclusive:general.append((iid,minimum[items[iid]['rarity']],weight[items[iid]['rarity']]))
    themed={
     'goblin_warhost':['plank_buckler','riveted_guard_shield','lastwatch_helm','bloodtrail_pendant'],
     'ashen_procession':['padded_travel_hood','glass_filter_charm','field_triage_kit','trollstitch_coat'],
     'arcane_convergence':['quilted_field_vest','surveyors_visor','glacier_page_focus','astral_fold_wraps'],
     'great_beast_tide':['softstep_boots','porters_coat','bramble_chaps','rootbound_heart'],
     'starfall_omen':['field_crossbow','rubble_cleats','counterweight_boots','cometstep_boots','starburst_caster'],
    }
    for eid,ids in themed.items():
        entries=[(iid,minimum[items[iid]['rarity']],weight[items[iid]['rarity']]) for iid in ids]
        events[eid]['loot'].extend(entries)
        for mission in missions.values():
            if mission.get('event')==eid and mission.get('loot_pool'):mission['loot_pool'].extend(entries)
