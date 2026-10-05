"""Regular-character loadouts. Only authored, engine-supported skills are executable."""
from copy import deepcopy
from .combat_abilities import validate

CAPACITY = 5
JOBS = {}
SKILLS = {}


def active(key, name, description, effects, target='enemy', range=1, rule='melee', cooldown=2, range_shape='diamond'):
    return validate(dict(id=key, name=name, description=description, type='active',
        source_kind='character', ability_version=1, target=target, range=range,
        elevation_rule=rule, range_shape=range_shape, cost={'cooldown':cooldown, 'charges':None}, effects=effects))


def passive(key, name, description, modifiers=None, reaction=None):
    return dict(id=key, name=name, description=description, type='passive',
                modifiers=modifiers or {}, reaction=reaction)


def register(key, name, description, first, second, third):
    ids=[]
    for skill in (first, second, third):
        skill=deepcopy(skill);skill['id']=f'job:{key}:{skill["id"]}';skill['source_name']=name
        SKILLS[skill['id']]=skill;ids.append(skill['id'])
    JOBS[key]={'name':name, 'description':description, 'starter_skills':ids}


def strike(key, name, description, extra, power_percent=100):
    return active(key,name,description,[{'type':'attack','damage_bonus':0,'power_percent':power_percent},
        {**extra,'conditions':[{'type':'hit'}]}])


register('fighter','Fighter','Protect allies or break enemy positions.',
    strike('bash','Driving Strike','Strike with 150% attack power and push one cell. Solid collisions add half the hit as damage and stun for one activation. Colliding with a person damages and stuns both, including allies. Knockback resistance and stun immunity apply.',{'type':'displace','mode':'push','distance':1,'collision_stun':True},150),
    active('cover','Chain Snare','Hit an enemy within three cells, pull it up to two cells toward you, stopping beside you, halve its movement and reduce armor by 30% for two activations. Requires a clear chain path; displacement resistance applies.',[{'type':'attack','damage_bonus':0},{'type':'displace','mode':'pull','distance':2,'stop_adjacent':True,'conditions':[{'type':'hit'}]},{'type':'status','status':'hobbled','turns':2,'conditions':[{'type':'hit'}]},{'type':'status','status':'armor_fracture','turns':2,'conditions':[{'type':'hit'}]}],range=3,rule='ballistic',cooldown=3,range_shape='square'),
    passive('intercept','Intercept','Redirect one attack against an adjacent ally. Shares your reaction allowance.',reaction={'id':'intercept','name':'Intercept'}))
register('barbarian','Barbarian','Disrupt nearby enemies, at the cost of staying exposed.',
    strike('shove','Brutal Shove','Melee hit pushes one cell; walls stop displacement. Hitting a solid obstacle adds half the hit as collision damage; hitting a person hurts both, including allies.',{'type':'displace','mode':'push','distance':1}),
    strike('expose','Crack Defenses','Melee hit applies Vulnerable for one target activation.',{'type':'status','status':'vulnerable','turns':1}),
    passive('anchored','Anchored','50 extra knockback resistance; does not prevent damage.',{'knockback_resistance':50}))
register('rogue','Rogue','Exploit weak targets and interfere with their attacks.',
    strike('bleed','Open Wound','Melee hit applies Bleed for two target activations.',{'type':'status','status':'bleed','turns':2}),
    strike('blind','Pocket Sand','Melee hit blinds for one target activation.',{'type':'status','status':'blind','turns':1}),
    passive('footwork','Footwork','Gain 5 evasion. Control effects still work.',{'evasion':5}))
register('ranger','Ranger','Set up accurate shots and control approaches.',
    active('mark','Track Quarry','Mark an enemy for two activations. Your first successful hit each activation gains 10 accuracy.',[{'type':'mark','turns':2,'accuracy':10}],range=5,rule='ballistic'),
    active('snare','Snaring Ground','Create binding ground at a chosen cell and adjacent legal cells for two of your activations.',[{'type':'zone','zone':'binding','radius':1,'turns':2}],range=4,rule='ballistic',cooldown=3),
    passive('footwork','Field Footwork','Gain 5 evasion; no extra damage.',{'evasion':5}))
register('mage','Mage','Create dangerous ground or protect a threatened ally.',
    active('embers','Ember Ground','Create burning ground for two of your activations. Each burned tile entered on a committed path deals 3 damage and applies Burn. Re-entry counts again; overlapping patches do not stack. Allies are safe.',[{'type':'zone','zone':'ember','radius':1,'turns':2}],range=3,rule='line_of_effect',cooldown=3),
    active('ward','Ward','Give an ally a 10 HP Barrier for two of their activations.',[{'type':'barrier','amount':10,'turns':2}],'ally',3,'line_of_effect',3),
    passive('footwork','Light Step','Gain 5 evasion. Mute still prevents spells.',{'evasion':5}))
register('cleric','Cleric','Treat wounds and maintain a safe fighting position.',
    active('mend','Mend','Restore 12 HP to a living ally. Cannot revive.',[{'type':'heal','amount':12}],'ally',3,'line_of_effect',3),
    active('cleanse','Cleanse','Remove Poison, Bleed, Burn and Slow from an ally.',[{'type':'cleanse','statuses':['poison','bleed','burn','slow']}],'ally',3,'line_of_effect',3),
    passive('steadfast','Steadfast','Gain 1 armor. Does not make healing mandatory.',{'armor':1}))
register('monk','Monk','Fight nearby enemies with displacement and retaliation.',
    strike('palm','Driving Palm','Melee hit pushes one cell. Knockback resistance applies. Hitting a solid obstacle adds half the hit as collision damage; hitting a person hurts both, including allies.',{'type':'displace','mode':'push','distance':1}),
    active('brace','Brace','Guard a nearby ally against the next incoming hit.',[{'type':'guard'}],'ally',1,'physical_care'),
    passive('riposte','Riposte','After surviving a melee hit, counter at half attack if in reach. Uses the shared reaction.',reaction={'id':'riposte','name':'Riposte'}))
register('bard','Bard','Keep allies fighting and weaken an enemy approach.',
    active('rally','Steady Song','Remove Fear and Slow from an ally and give an 8 HP Barrier for one activation.',[{'type':'cleanse','statuses':['fear','slow']},{'type':'barrier','amount':8,'turns':1}],'ally',3,'line_of_effect',3),
    active('discord','Discord','Slow an enemy for one activation. Resistance and immunities apply.',[{'type':'status','status':'slow','turns':1}],range=3,rule='line_of_effect',cooldown=3),
    passive('footwork','Stage Footwork','Gain 5 evasion.',{'evasion':5}))
register('druid','Druid','Change your fighting form or hold ground with thorns.',
    active('prowler','Prowler Form','Self only: INT-based melee and +1 movement for two of your activations. No healing on transformation.',[{'type':'form','form':'prowler','turns':2}],'ally',1,'line_of_effect',3),
    active('thorns','Thorn Ground','Create thorns around a chosen cell for two of your activations. Each thorn tile entered on a committed path deals 3 damage. Re-entry counts again; overlapping patches do not stack. Allies are safe.',[{'type':'zone','zone':'thorns','radius':1,'turns':2}],range=3,rule='line_of_effect',cooldown=3),
    passive('rooted','Rooted','Gain 25 knockback resistance.',{'knockback_resistance':25}))
register('engineer','Engineer','Spend finite Components on owner-linked machinery.',
    active('turret','Scrap Turret','Self only: spend 2 Components on a stationary automatic turret. No shot on the deployment turn.',[{'type':'deploy','entity':'scrap_turret'}],'ally',1,'physical_care',3),
    active('automaton','Guard Automaton','Self only: spend 3 Components on a commanded automaton. Its attacks consume your action.',[{'type':'deploy','entity':'guard_automaton'}],'ally',1,'physical_care',3),
    passive('reinforced','Reinforced Coat','Gain 1 armor. Does not increase device output.',{'armor':1}))
register('summoner','Summoner','Choose a commanded companion or automatic wisps.',
    active('wolf','Bonded Wolf','Self only: summon a commanded wolf, using 1 capacity. Its attacks spend your main action.',[{'type':'deploy','entity':'companion'}],'ally',1,'line_of_effect',3),
    active('wisps','Wisp Pair','Self only: summon two automatic wisps, using 2 capacity together. Share the automatic output budget.',[{'type':'deploy','entity':'wisps'}],'ally',1,'line_of_effect',3),
    passive('footwork','Keep Distance','Gain 5 evasion; your summons remain linked to you.',{'evasion':5}))
register('captor','Captor','Isolate a target or hold enemies for capture. Capture weapons remain necessary for Subdue.',
    active('bind','Binding Line','Attempt Bind for two target activations, leaving time for a follow-up capture. Range 2; 75% before resistance, no damage or guaranteed capture.',[{'type':'status','status':'bind','turns':2,'chance':75}],range=2,rule='ballistic',cooldown=3),
    active('pull','Reel In','Pull an enemy one cell toward you. Stable targets resist. No damage.',[{'type':'displace','mode':'pull','distance':1}],range=2,rule='ballistic'),
    passive('anchored','Sure Grip','Gain 25 knockback resistance and +4 capture chance with capture weapons. No damaging attack bonus.',{'knockback_resistance':25,'capture_chance':4}))


def later(job, *skills):
    unlocks=[]
    for threshold,original in zip((2,5,9),skills):
        skill=deepcopy(original);skill['id']=f'job:{job}:{skill["id"]}';skill['source_name']=JOBS[job]['name']
        SKILLS[skill['id']]=skill;unlocks.append({'skill_id':skill['id'],'contracts':threshold})
    JOBS[job]['unlocks']=unlocks


later('fighter',
    passive('riposte','Riposte','Counter a survived melee hit at half attack when in reach. Intercept and Riposte compete for one reaction.',reaction={'id':'riposte','name':'Riposte'}),
    active('pull','Earthbreaker','Leap up to three cells onto open ground. The landing shockwave strikes enemies within two cells with 200% attack power: the inner ring pushes two cells, the outer ring one. Collisions add half the impact damage to both people and stun surviving units for one activation. Walls, elevation and knockback resistance still matter. Ready again in five of your turns.',[{'type':'leap_attack','radius':2,'inner_push':2,'outer_push':1,'power_percent':200,'collision_stun':True}],range=3,rule='melee',cooldown=5),
    active('rally','Hold Together','Click your fighter. Remove Fear from yourself and allies within one cell. Each takes 25% less damage from their next direct hit and deals 25% more damage with their next attack, including all targets of an area attack. Each bonus is used separately; a missed attack spends the attack bonus. Walls block the effect. Bonuses do not stack.',[{'type':'cleanse','statuses':['fear'],'radius':1},{'type':'status','status':'rally_protection','turns':1,'radius':1},{'type':'status','status':'rally_power','turns':1,'radius':1}],'ally',1,'physical_care',4))
later('barbarian',
    passive('hide','Thick Hide','Gain 1 armor; offers durability instead of another active skill.',{'armor':1}),
    active('drive','Drive Back','Melee hit pushes up to two cells. Walls stop the push; pit rules and resistance apply. Hitting a solid obstacle adds half the hit as collision damage; hitting a person hurts both, including allies.',[{'type':'attack','damage_bonus':0},{'type':'displace','mode':'push','distance':2,'conditions':[{'type':'hit'}]}],cooldown=3),
    active('stand','Stand Your Ground','Remove Fear from yourself or an adjacent ally and grant Guard.',[{'type':'cleanse','statuses':['fear']},{'type':'guard'}],'ally',1,'physical_care',3))
later('rogue',
    strike('venom','Venom Edge','Melee hit attempts Poison for two target activations. Poison immunity applies.',{'type':'status','status':'poison','turns':2,'chance':75}),
    strike('pin','Pinning Strike','Melee hit attempts Bind for one activation. Control recovery prevents repeated locks.',{'type':'status','status':'bind','turns':1,'chance':75}),
    passive('riposte','Close Counter','Counter a survived melee hit at half attack when in reach. One shared reaction.',reaction={'id':'riposte','name':'Close Counter'}))
later('ranger',
    active('poison','Poisoned Dart','Attempt Poison at range 4 for two target activations. 75% before resistance; no direct damage.',[{'type':'status','status':'poison','turns':2,'chance':75}],range=4,rule='ballistic',cooldown=3),
    active('dust','Dust Shot','Attempt Blind at range 4 for one activation. 75% before resistance; no direct damage.',[{'type':'status','status':'blind','turns':1,'chance':75}],range=4,rule='ballistic',cooldown=3),
    passive('anchored','Steady Position','Gain 25 knockback resistance. Does not improve accuracy.',{'knockback_resistance':25}))
later('mage',
    active('binding','Binding Circle','Create enemy-binding ground around a target for two of your activations. Entering triggers control recovery rules.',[{'type':'zone','zone':'binding','radius':1,'turns':2}],range=3,rule='line_of_effect',cooldown=3),
    active('scorch','Scorch','Attempt Burn for two target activations, 75% before resistance. No direct damage.',[{'type':'status','status':'burn','turns':2,'chance':75}],range=3,rule='line_of_effect',cooldown=3),
    passive('armored','Wardweave','Gain 1 armor; consumes a slot instead of another spell.',{'armor':1}))
later('cleric',
    active('sanctuary','Sanctuary','Create healing ground around a chosen cell for two of your activations. Restores 3 HP at ally activation start; Burn prevents healing.',[{'type':'zone','zone':'sanctuary','radius':1,'turns':2}],'ally',3,'line_of_effect',3),
    active('barrier','Shelter','Give an ally a 14 HP Barrier for two target activations. Replaces weaker Barriers; does not stack.',[{'type':'barrier','amount':14,'turns':2}],'ally',3,'line_of_effect',3),
    passive('intercept','Stand Beside Them','Intercept one direct attack against an adjacent ally. Shares your reaction allowance.',reaction={'id':'intercept','name':'Stand Beside Them'}))
later('monk',
    strike('bind','Joint Lock','Melee hit attempts Bind for one activation; 75% before resistance.',{'type':'status','status':'bind','turns':1,'chance':75}),
    passive('returning','Returning Hand','After an enemy misses a melee attack, counter at half attack if in reach. Competes with Riposte for one reaction.',reaction={'id':'returning_hand','name':'Returning Hand'}),
    passive('stance','Patient Stance','Gain 1 armor. Trades a slot for staying power.',{'armor':1}))
later('bard',
    active('refrain','Restoring Refrain','Apply Regeneration for two ally activations. Cannot revive.',[{'type':'status','status':'regeneration','turns':2}],'ally',3,'line_of_effect',3),
    active('silence','Silencing Note','Attempt Mute for one target activation; 70% before resistance.',[{'type':'status','status':'mute','turns':1,'chance':70}],range=3,rule='line_of_effect',cooldown=3),
    active('cover','Protective Verse','Grant Guard to an ally at range 3. Mute prevents this spell.',[{'type':'guard'}],'ally',3,'line_of_effect',3))
later('druid',
    active('bulwark','Bulwark Form','Self only: INT-based melee, +3 armor, -1 movement and 50 knockback resistance for two of your activations. No HP refill.',[{'type':'form','form':'bulwark','turns':2}],'ally',1,'line_of_effect',3),
    active('sprite','Grove Sprite','Self only: deploy an automatic healing sprite using 1 capacity. It shares the owner output budget.',[{'type':'deploy','entity':'grove_sprite'}],'ally',1,'line_of_effect',3),
    active('bark','Bark Ward','Give yourself or an adjacent ally a 12 HP Barrier for two target activations.',[{'type':'barrier','amount':12,'turns':2}],'ally',1,'line_of_effect',3))
later('engineer',
    active('trap','Binding Trap','Create enemy-binding ground around a target for two of your activations. Range 2; control recovery applies.',[{'type':'zone','zone':'binding','radius':1,'turns':2}],range=2,rule='ballistic',cooldown=3),
    active('plate','Cover Plate','Give yourself or an adjacent ally Guard and an 8 HP Barrier for one target activation.',[{'type':'guard'},{'type':'barrier','amount':8,'turns':1}],'ally',1,'physical_care',3),
    passive('brace','Braced Frame','Gain 50 knockback resistance. No extra Components or device damage.',{'knockback_resistance':50}))
later('summoner',
    active('bulwark','Stone Bulwark','Self only: deploy a durable commanded defender using 2 capacity. Attacks consume your action.',[{'type':'deploy','entity':'bulwark'}],'ally',1,'line_of_effect',3),
    active('sprite','Grove Sprite','Self only: deploy an automatic healing sprite using 1 capacity. Shares the automatic output budget.',[{'type':'deploy','entity':'grove_sprite'}],'ally',1,'line_of_effect',3),
    active('manifest','Astral Guardian','Self only: once per encounter, deploy a commanded guardian using 2 capacity. Attacks consume your action.',[{'type':'deploy','entity':'manifestation'}],'ally',1,'line_of_effect',3))
later('captor',
    active('field','Restraint Field','Create enemy-binding ground around a target for two of your activations. Entering attempts Bind; does not capture.',[{'type':'zone','zone':'binding','radius':1,'turns':2}],range=2,rule='ballistic',cooldown=3),
    active('dust','Blinding Powder','Attempt Blind for one target activation at range 2. 75% before resistance; no damage.',[{'type':'status','status':'blind','turns':1,'chance':75}],range=2,rule='ballistic',cooldown=3),
    passive('coat','Padded Coat','Gain 1 armor. Does not improve capture chance.',{'armor':1}))


def eligible(character):
    return character.get('source_kind') not in {'champion','celestial'} and not character.get('temporary_mercenary')


def initialize(character):
    # Legacy characters opt in deliberately. No inferred class or equipment replacement.
    if eligible(character):
        character.setdefault('job_id',None)
        character.setdefault('learned_skills',[])
        character.setdefault('equipped_skills',[])
        character.setdefault('skill_slots',CAPACITY)
        character.setdefault('job_practice',0)
        character.setdefault('job_contract_credits',[])
    return character


def update(state, character_id, skill_ids, job_id=None):
    character=next((c for c in state.get('characters',[]) if c['id']==character_id),None)
    if not character or not eligible(character):raise ValueError('Choose a regular character')
    if character.get('status','idle')!='idle' or character.get('assignment'):
        raise ValueError('Change skills while idle and unassigned')
    if not isinstance(skill_ids,list) or any(not isinstance(s,str) for s in skill_ids) or len(set(skill_ids))!=len(skill_ids):
        raise ValueError('Select distinct skills')
    draft=deepcopy(character);initialize(draft)
    if job_id is not None:
        if job_id not in JOBS:raise ValueError('Choose a valid Job')
        if draft['job_id'] and draft['job_id']!=job_id:raise ValueError('Job changes are not available yet')
        if not draft['job_id']:
            draft['job_id']=job_id;draft['learned_skills']=list(JOBS[job_id]['starter_skills'])
    if len(skill_ids)>CAPACITY:raise ValueError('Active and passive skills share five slots')
    if any(s not in draft['learned_skills'] or s not in SKILLS for s in skill_ids):
        raise ValueError('Equip only skills this character has learned')
    draft['equipped_skills']=list(skill_ids)
    character.update(draft)
    return character


def snapshot(character):
    if not eligible(character):return [],[],{}
    equipped=character.get('equipped_skills',[])
    if len(equipped)>CAPACITY or len(set(equipped))!=len(equipped):raise ValueError('Invalid character loadout')
    actives=[];passives=[];modifiers={}
    for key in equipped:
        if key not in character.get('learned_skills',[]) or key not in SKILLS:raise ValueError('Unknown or unlearned equipped skill')
        skill=deepcopy(SKILLS[key])
        if skill['type']=='active':actives.append(skill)
        else:
            passives.append(skill)
            for stat,value in skill['modifiers'].items():modifiers[stat]=modifiers.get(stat,0)+value
    return actives,passives,modifiers


def credit_contract(state, party_ids, outcome, contract_key, debug=False):
    """One practice per successful expedition; never grant retroactive stats/slots."""
    if debug or outcome not in {'success','critical_success'}:return []
    results=[]
    for character in state.get('characters',[]):
        if character['id'] not in party_ids or not eligible(character) or character.get('job_id') not in JOBS:continue
        initialize(character)
        if contract_key in character['job_contract_credits']:continue
        character['job_contract_credits']=(character['job_contract_credits']+[contract_key])[-32:]
        character['job_practice']+=1
        learned=[]
        for unlock in JOBS[character['job_id']]['unlocks']:
            key=unlock['skill_id']
            if character['job_practice']>=unlock['contracts'] and key not in character['learned_skills']:
                character['learned_skills'].append(key);learned.append(key)
        results.append({'character_id':character['id'],'name':character.get('name','Adventurer'),
                        'practice':character['job_practice'],'learned':learned})
    return results


def public_catalog():
    return {'jobs':deepcopy(JOBS),'skills':deepcopy(SKILLS),'capacity':CAPACITY}
