"""Authored early contracts and economic roles; applied after the legacy catalogue."""
from copy import deepcopy
from .tactical_contracts import TACTICAL_CONTRACTS
from .celestials import CELESTIAL_CHAIN_STEPS

# title, premise, stat, materials; each site has its own problem and reward identity.
EARLY = {
 'E': [
 ('timber_creek','Timber Across the Creek','A fallen bridge separates the camp from a small stack of cut timber. Recover the reachable logs or cross for the rest.','building',{'wood':8}),
 ('tool_shed','The Locked Tool Shed','A tenant left tools in a collapsed shed. Find a safe entrance before disturbing the roof.','scavenging',{'scrap':4}),
 ('herbs_wall','Herbs Behind the Wall','The healer needs plants growing beside an abandoned garden wall. Some patches are within easy reach; others are behind the gate.','medicine',{'medicine':2}),
 ('market_errand','A Parcel for the Market','Deliver a sealed parcel and settle a disagreement over its weight. The caravan clerk will remember reliable work.','survival',{}),
 ('outcrop_survey','Survey the Outcrop','Mark sound stone and loose edges before the camp starts a quarry. Bring a few usable pieces back.','building',{'stone':6}),
 ('camp_repairs','The Leaking Roof','Repair a local cottage before its owner loses another night of sleep. Salvaged fittings may still be usable.','building',{}),
 ('mushroom_baskets','Mushroom Baskets','A cook wants a basket of edible mushrooms, not the similar-looking ones growing beside them.','survival',{'food':5}),
 ('fishing_line','The Snagged Fishing Line','A fisher has lost a trap downstream. Retrieve it without spilling the catch.','survival',{'food':5}),
 ('lost_keys','Keys Under the Footbridge','Find a merchant’s dropped keys before the stream carries them away.','scavenging',{}),
 ('lantern_delivery','Lanterns for the Watch','Carry repaired lanterns to the watch posts and check the oil seals.','building',{}),
 ('first_aid_round','The Healer’s Round','Help the village healer change dressings and identify who needs further care.','medicine',{}),
 ('stone_cart','The Stuck Stone Cart','A small cart has sunk into a rut. Free it without breaking the axle; its owner offers surplus stone.','building',{'stone':8}),
 ('seed_exchange','Seeds at Briar Ford','The watch farms need someone to compare seed sacks and settle an exchange fairly.','survival',{}),
 ('salvage_bells','Bells in the Scrap Heap','A caravan repairer suspects usable brass fittings are buried among rusted tools.','scavenging',{'scrap':5}),
 ('old_waymarks','The Missing Waymark','Find where a roadside marker belongs before more travelers take the wrong path.','survival',{}),
 ('apprentice_notes','The Apprentice’s Notes','Recover a workshop apprentice’s scattered measurements and put them in usable order.','building',{}),
 ('rats_storehouse','Rats in the Storehouse','Disease-bearing rats have broken into the provision shed. Separate the swarm and clear the stores before they spoil the remaining sacks.','combat',{'food':4}),
 ('roadside_toll','The Unwanted Toll','Two opportunists are stopping villagers on a narrow road. Drive them off or bring them back alive.','combat',{}),
 ('wolves_fence','Wolves at the Fence','A hungry wolf pack has entered a fenced clearing. Keep it from surrounding you and clear the approach so its keeper can return.','combat',{}),
 ('goblin_pickpockets','The Goblin Pickpockets','Two goblins have trapped a dropped purse between them. Retrieve it and open the road.','combat',{}),
 ('ruined_well','Movement at the Old Well','An abandoned well has become a hiding place for a pair of armed scavengers. Clear the site safely.','combat',{}),
 ('supply_watch','The Small Supply Watch','A provision stop needs its approach cleared before the next delivery arrives.','combat',{}),
 ],
 'D': [
 ('caravan_account','The Caravan’s False Account','A supplier is charging the watch twice for the same delivery. Follow the receipts and confront the discrepancy.','scavenging',{}),
 ('quarry_braces','Braces for the Quarry','A quarry needs supports inspected before work resumes. Sound judgement is worth more than rushing the job.','building',{'stone':10}),
 ('fever_route','The Fever Route','Carry remedies between isolated households and identify the source of contaminated water.','medicine',{}),
 ('watch_negotiation','A Watchman’s Dispute','Two watch posts disagree over who should protect the ford. Find terms both can keep.','survival',{}),
 ('mill_gears','The Missing Mill Gears','Recover a shipment of fittings from a derailed wagon without damaging the working parts.','building',{'scrap':6}),
 ('orchard_signs','Tracks Through the Orchard','Identify what is taking fruit before the growers blame their neighbors.','survival',{'food':7}),
 ('road_cache','The Road Raiders’ Cache','A small raider crew is hiding stolen goods at a road bend. Recover the cache and secure an exit.','combat',{}),
 ('goblin_bridge','The Narrow Bridge Gang','A goblin gang is taking payment from travelers at an old bridge approach. Break its hold on the road.','combat',{}),
 ('chapel_patrol','The Chapel Patrol','Restless dead are stopping mourners outside a ruined chapel. Clear a route without disturbing the graves.','combat',{}),
 ('workshop_intruders','Intruders at the Workshop','Armed thieves have occupied a disused repair yard. The owner wants the site and its tools back.','combat',{}),
 ],
 'C': [
 ('meridian_calibration','The Meridian Calibration','A surviving survey instrument gives conflicting readings. Repair its reference marks before the artificers risk a field test.','magic',{}),
 ('trade_compact','A Compact at the Ford','Negotiate safe caravan passage with the watch and a village that no longer trusts it.','survival',{}),
 ('deep_seam','The Deep Seam Survey','Inspect a newly exposed seam and plan supports before the quarry expands.','building',{'stone':16}),
 ('antidote_exchange','The Antidote Exchange','Identify a useful remedy among mislabeled stock and arrange a fair exchange with the clinic.','medicine',{}),
 ('forged_manifest','The Forged Manifest','Separate a genuine caravan inventory from a clever forgery before the wrong cargo is impounded.','scavenging',{}),
 ('waystation_wards','Wards at the Waystation','Restore failing ward marks without redirecting their discharge through the travelers inside.','magic',{}),
 ('ford_enforcers','The Ford Enforcers','A well-equipped crew is replacing the watch’s toll records with its own. Secure the crossing.','combat',{}),
 ('goblin_armory','The Hidden Goblin Armory','A guarded goblin store supplies raids on nearby farms. Break the guard and recover its field equipment.','combat',{}),
 ('chapel_gate','The Chapel Gatekeepers','An organized patrol of dead soldiers controls the chapel approach. Open a safe path.','combat',{}),
 ('salvage_court','The Salvage Yard Court','A raider captain has turned a repair yard into a court for stolen goods. End the arrangement.','combat',{}),
 ],
 'B': [('meridian_pact','The Meridian Field Pact','Agree how a dangerous field test will be supervised and who receives its discoveries.','magic',{}),('caravan_missing','The Missing Caravan Register','Uncover who redirected a whole caravan without leaving a trustworthy trail.','scavenging',{})],
 'A': [('ward_concord','The Ward Concord','Settle conflicting ward networks before two allied settlements discharge them into each other.','magic',{})],
 'S': [('meridian_succession','The Meridian Succession','Negotiate control of an awakened network whose custodians disagree over who may use it.','magic',{})],
}

def apply_progression(buildings,missions,items,tracks,hall_upgrades):
    for definition in buildings.values():
        cost=definition.get('cost',{});cloth=cost.pop('cloth',0)
        if cloth:cost['stone']=cloth*2
    for cost in hall_upgrades.values():
        cloth=cost.pop('cloth',0)
        if cloth:cost['stone']=cloth*3
    buildings['guild_hall']['cost']={'wood':30,'stone':12,'scrap':8}
    for fid,key in [('lumbermill','wood'),('quarry','stone'),('salvage_yard','scrap'),('farm','food'),('herb_garden','medicine')]:
        buildings[fid]={'name':{'lumbermill':'Lumbermill','quarry':'Quarry','salvage_yard':'Salvage Yard','farm':'Garden Farm','herb_garden':'Herb Garden'}[fid],
            'w':2,'h':2,'workers':1,'production':key,'cost':{'wood':14,'stone':8},
            'description':'Improves this camp work by 30% per level. Upgrade to level 3 for more output and worker slots; usable by a solo player.'}
    buildings['kitchen']={'name':'Kitchen','w':2,'h':2,'workers':1,'cost':{'wood':18,'stone':10},'description':'Batch-cook lasting optional meals from Food. The player can cook without a hired chef.'}
    buildings['alchemy_lab']['cost'].pop('medicine',None)
    buildings['infirmary']['cost']['medicine']=2
    tracks['scavenging']['facility']='salvage_yard'
    tracks['building']['facility']='workshop'
    tracks['survival']['facility']='farm'
    # Cloth is no longer a construction reward. Preserve resource-specific contracts only.
    resource_ids={'roadside_store','fallen_orchard','creekside_scrap','charcoal_camp','herb_meadow','goblin_supply_carts'} | set(CELESTIAL_CHAIN_STEPS)
    for mid,mission in missions.items():
        for key in ['rewards','critical_rewards']:
            block=mission.get(key,{})
            materials=block.get('materials',{})
            cloth=materials.pop('cloth',0)
            if cloth:materials['stone']=materials.get('stone',0)+cloth
            if mid not in resource_ids:
                block.pop('materials',None)
            elif materials:
                block['materials']={r:max(1,round(v*.45)) for r,v in materials.items()}
        mission['reward_preview']=[p for p in mission.get('reward_preview',[]) if not any(word in p.lower() for word in ['material','supplies','lumber','scrap','cloth'])]
        if mid.startswith(('hedgerow','goblin')):mission.setdefault('faction','hedgerow')
        elif mid.startswith(('arcane','meridian','industrial')):mission.setdefault('faction','meridian')
        elif mid.startswith(('road','caravan','field_clinic')):mission.setdefault('faction','lantern')
    levels={'E':8,'D':11,'C':14,'B':17,'A':20,'S':23}
    for rank,rows in EARLY.items():
        for index,(mid,name,premise,stat,materials) in enumerate(rows):
            faction='meridian' if stat in {'building','magic'} else 'lantern' if stat in {'medicine','scavenging'} else 'hedgerow'
            mission={'name':name,'description':premise,'rank':rank,'stat':stat,'difficulty':levels[rank],
                'party_size':1 if rank=='E' else 2 if rank in {'D','C'} else 3,'durations':[0],
                'pool_weight':3,'claim_requirements':[],'modifiers':[],'critical_any':[],
                'rewards':{'materials':materials} if materials else {},'critical_rewards':{},
                'reward_preview':['Equipment drop chance','Faction relationship'], 'pays_gold':not bool(materials),
                'faction':faction,'region':'settlements','mission_form':'operation','resolution_mode':'roll',
                'objective':premise,'visible_hints':[],'bodyguard_slots':0,'audited':True,'reward_rolls':[],
                'encounter_plan':{'mode':'roll','combat':'unknown'},
                'story_thread':'meridian' if faction=='meridian' else 'frontier_watch' if faction=='hedgerow' else 'caravan_roads',
                'story_thread_name':'The Meridian Workshops' if faction=='meridian' else 'The Briar Ford Watch' if faction=='hedgerow' else 'The Lantern Road',
                'world_context':'These jobs keep the settlements around Briar Ford supplied while the watch tracks the Black Banner and the artificers repair the old Meridian network.',
                'narrative':{
                    'intro':f'{{party}} accepted the job at {name}. {premise}',
                    'approach':[f'{{lead}} checked the approach before starting. {premise}',f'The expedition first asked what had already been tried at {name}. That gave {{lead}} somewhere to begin.'],
                    'success':'{lead} found a workable approach. The job was finished, and the people waiting on it could get back to their own work.',
                    'critical_success':'{lead} checked the part everyone else had overlooked. That extra care settled the job and gave the party time to search for something worth bringing home.',
                    'failure':'The first approach did not hold up. {party} returned without finishing the job, leaving it for someone better prepared.',
                    'critical_failure':'A mistake put {lead} in danger. The expedition had to withdraw and deal with the injury before trying again.'}}
            if materials:mission['reward_preview'].append('Small recovered '+', '.join(materials))
            else:mission['reward_preview'].append('Contract payment')
            if stat=='combat':
                race='Goblin' if 'goblin' in mid else 'Undead' if 'chapel' in mid else 'Human'
                creature={'wolves_fence':'Wolf','rats_storehouse':'Rat'}.get(mid)
                if creature:race=creature
                TACTICAL_CONTRACTS[mid]={'race':race,'layout':'ruin' if 'chapel' in mid or 'well' in mid else 'camp' if 'store' in mid or 'workshop' in mid or 'yard' in mid else 'road','faction':name.lower(),'enemy_count':2 if rank=='E' else 3,'rookie':rank=='E','creature':creature}
                if mid in {'rats_storehouse','wolves_fence'}:TACTICAL_CONTRACTS[mid]['enemy_count']=3
                mission.update(combat_encounter={'id':'contract:'+mid,'name':name},resolution_mode='tactical',mission_form='hunt',combat_critical_condition='Secure the field and keep the expedition standing.')
                mission['reward_preview'].append('Recovered creature provisions' if mid=='wolves_fence' else 'Recovered enemy equipment')
                if rank!='E':mission['combat_critical_condition']='Capture the commander alive, secure the field, and keep the expedition standing.' if race!='Undead' else 'Secure the field and keep the expedition standing.'
                mission['encounter_plan']={'mode':'tactical','combat':'expected'}
            if mid in {'timber_creek','tool_shed','herbs_wall'}:
                TACTICAL_CONTRACTS[mid]={'race':'Goblin','layout':'ruin' if mid=='tool_shed' else 'road','faction':'opportunistic scavengers','enemy_count':2,'rookie':True}
                mission['combat_critical_condition']='Clear the site and return safely.'
                mission['decision_scene']={'start':'approach','nodes':{'approach':{'title':name,'text':premise,'choices':{
                    'safe':{'label':'Take the reachable supplies','description':'A modest load, no fighting. Check whether you can recover it safely.','stat':stat,'difficulty':8,
                        'success':{'finish':'success','text':'The party recovered the reachable supplies and left the dangerous section alone.'},'failure':{'finish':'failure','text':'The accessible supplies were already spoiled.'},'critical_failure':{'finish':'failure','text':'The party left before an unstable section collapsed.'}},
                    'risk':{'label':'Enter the guarded section','description':'Fight the scavengers for access to the site. An exclusive tool may be among their possessions.',
                        'success':{'battle':'contract:'+mid,'text':'The scavengers moved to stop the expedition at the far approach.'}}
                }}}}
                mission['has_decisions']=True
                mission['resolution_mode']='choices → tactical'
                mission['encounter_plan']={'mode':'branching','combat':'possible'}
            missions[mid]=mission
    successes={
        'timber_creek':'{lead} lashed the loose logs together before pulling them across. The camp received sound timber instead of another broken bridge.',
        'tool_shed':'{lead} lifted the fallen beam just far enough to reach the tool rack. Most of the handles were rotten, but the metal fittings could still be used.',
        'herbs_wall':'The useful plants grew on the dry side of the wall. {lead} separated them from the damaged leaves and brought a small bundle to the healer.',
        'market_errand':'The clerk weighed the sealed parcel in front of both parties. {lead} pointed out the extra packing on the invoice, and the argument ended before the market closed.',
        'outcrop_survey':'{lead} marked the sound face and left the loose edge alone. The first stone came away cleanly, giving the camp a place to start without risking a collapse.',
        'camp_repairs':'The leak was under the overlapping boards, not the hole the owner had patched. {lead} reset the joint and stayed long enough to check it with a bucket of water.',
        'mushroom_baskets':'{lead} rejected the pale mushrooms beside the roots and filled the basket from the higher ground. The cook inspected the haul before putting a pot on.',
        'fishing_line':'The trap was caught under a branch. {lead} freed the line slowly enough to keep its catch inside, then brought it back to the fisher.',
        'lost_keys':'{lead} found the keys in the gravel below the footbridge. The merchant opened the storeroom before anyone had to break its lock.',
        'lantern_delivery':'One lantern leaked at its cap. {lead} replaced the seal before handing the lights to the watch, saving them a dark post later that night.',
        'first_aid_round':'{lead} helped the healer sort the ordinary dressing changes from wounds that needed attention. The last household received fresh supplies before the round ended.',
        'stone_cart':'The axle held once the weight was moved off the sinking wheel. {lead} helped the owner pack the rut, and the surplus stone came back to camp.',
        'seed_exchange':'{lead} laid out both seed samples before the farmers agreed to trade. Each side left knowing what it was planting, and the watch gained another reliable contact.',
        'salvage_bells':'The brass was buried under cracked hinges. {lead} separated usable fittings from the scraps and left the dangerous blades for the repairer.',
        'old_waymarks':'{lead} matched the marker to the old foundation beside the road. The next travelers followed it toward the ford instead of the abandoned crossing.',
        'apprentice_notes':'The missing measurements were on the backs of the sketches. {lead} put the pages in order, and the apprentice could finally finish the frame.',
        'caravan_account':'Two receipts carried the same wagon number. {lead} put them beside the delivery record, and the supplier withdrew the second charge.',
        'quarry_braces':'{lead} found a brace resting on loose fill. The crew reset its footing before hauling stone past it, then cleared a small load for the camp.',
        'fever_route':'The households shared a water barrel upstream. {lead} warned the keeper, helped the healer finish the round, and left clear instructions at each door.',
        'watch_negotiation':'{lead} arranged an overlap at the changing of the watch. Both posts kept their patrols, and the ford no longer stood empty between them.',
        'mill_gears':'{lead} packed the gears separately before shifting the wagon. The repairer received working teeth rather than a sack of chipped metal.',
        'orchard_signs':'The tracks stopped at a gap beneath the fence. {lead} showed the growers where to close it, settling the accusation before it became a feud.',
        'meridian_calibration':'{lead} checked the instrument against a fixed marker. Its second reading held, and the artificers approved a supervised field test.',
        'trade_compact':'{lead} wrote down who would escort each stretch of road and where responsibility changed hands. The caravan accepted the terms, and the village reopened its gate.',
        'deep_seam':'The promising seam ran beneath unstable ground. {lead} marked a supported approach, letting the quarry expand without committing the crew to a dangerous shortcut.',
        'antidote_exchange':'{lead} identified the remedy by its preparation notes rather than its label. The clinic accepted the exchange after testing a small sample.',
        'forged_manifest':'The forged list named a wagon that had never crossed the ford. {lead} traced the real cargo through the toll book and stopped the wrong shipment being seized.',
        'waystation_wards':'{lead} disconnected the damaged mark before restoring the circuit. The ward settled without discharging through the occupied room.',
        'meridian_pact':'{lead} secured limits on the test and a shared record of its results. The artificers accepted witnesses from both camps instead of keeping the experiment secret.',
        'caravan_missing':'The missing register had been replaced with a copied route. {lead} checked the ferry ledger and found where the caravan had actually turned.',
        'ward_concord':'{lead} separated the two ward networks and agreed a common boundary with their keepers. Neither settlement had to switch off its protection.',
        'meridian_succession':'{lead} gave the rival custodians separate responsibilities and a shared shutdown rule. The awakened network answered its first command without taking a side.',
    }
    for mid,text in successes.items():
        mission=missions[mid];mission['narrative']['success']=text
        mission['narrative']['critical_success']=text+' The party checked the result before leaving; nothing needed a second trip.'
    for mid in ['market_errand','seed_exchange','watch_negotiation','trade_compact','meridian_pact','ward_concord','meridian_succession']:
        missions[mid]['mission_form']='diplomacy'
    # Reliable early blueprint knowledge is camp-side; rare loot never gates basic services.
    for mid in ['timber_creek','outcrop_survey','apprentice_notes','seed_exchange']:
        missions[mid]['rewards']['blueprint']={'timber_creek':'lumbermill','outcrop_survey':'quarry','apprentice_notes':'workshop','seed_exchange':'farm'}[mid]
    # Rare lower-rank discoveries with working perks, unavailable in all generic/high-rank pools.
    discoveries=[('rats_storehouse','cellar_guard_charm','Cellar Guard Charm','accessory','guard'),
        ('roadside_toll','ford_runner_boots','Ford Runner Boots','feet','pathfinder'),
        ('wolves_fence','fencekeepers_buckle','Fencekeeper’s Buckle','accessory','guard'),
        ('timber_creek','creekwright_gloves','Creekwright Gloves','hands','engineer'),
        ('tool_shed','lockkeepers_lens','Lockkeeper’s Lens','accessory','scout'),
        ('herbs_wall','garden_healers_pin','Garden Healer’s Pin','accessory','medic'),
        ('caravan_account','caravan_ledger_seal','Caravan Ledger Seal','accessory','precision_core'),
        ('road_cache','raiders_route_spur','Raider’s Route Spur','feet','pathfinder'),
        ('chapel_patrol','chapel_watch_bead','Chapel Watch Bead','accessory','graveward'),
        ('meridian_calibration','calibrators_focus','Calibrator’s Focus','accessory','magic_resistance'),
        ('trade_compact','ford_envoys_signet','Ford Envoy’s Signet','accessory','guard'),
        ('goblin_armory','armory_breach_gloves','Armory Breach Gloves','hands','engineer')]
    for mid,iid,name,slot,perk in discoveries:
        items[iid]={'name':name,'slot':slot,'rarity':'rare','tags':['mission_exclusive'],'bonuses':{},'attribute_bonuses':{},'granted_perks':[perk],
            'description':f'Exclusive to {missions[mid]["name"]}. A rare find that grants {perk.replace("_"," ")}; higher-rank loot pools cannot award it.',
            'icon':'/assets/catalogue/items/warding_token.png'}
        missions[mid]['reward_rolls']=[{'source':'site-exclusive discovery','chance':3,'critical_bonus':2,'reward':{'item':iid},**({'requires_combat':True} if mid in {'timber_creek','tool_shed','herbs_wall'} else {})}]
        missions[mid]['reward_preview'].insert(0,name+' · 3% discovery')
    items['merchant_wayfarer_ring']={'name':'Wayfarer’s Trade Ring','slot':'accessory','rarity':'rare','tags':['merchant_exclusive'],
        'bonuses':{'survival':1},'attribute_bonuses':{},'granted_perks':['pathfinder'],'description':'Only visiting merchants carry this route-finding ring.',
        'icon':'/assets/catalogue/items/warding_token.png'}
    for iid,name,perks in [('watch_ford_medallion','Watch-Ford Medallion',['guard','bannerbreaker']),('meridian_workshop_ward','Meridian Workshop Ward',['magic_resistance','engineer']),('lantern_route_compass','Lantern Route Compass',['pathfinder','scout'])]:
        items[iid]={'name':name,'slot':'accessory','rarity':'rare','tags':['faction_exclusive'],'bonuses':{},'attribute_bonuses':{},'granted_perks':perks,
            'description':'Available only through trusted faction trade. Grants '+', '.join(p.replace('_',' ') for p in perks)+'.','icon':'/assets/catalogue/items/warding_token.png'}
