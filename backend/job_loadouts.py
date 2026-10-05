"""Regular-character loadouts. Only authored, engine-supported skills are executable."""
from copy import deepcopy
from .combat_abilities import validate

CAPACITY = 5
JOBS = {}
SKILLS = {}


def active(key, name, description, effects, target='enemy', range=1, rule='melee', cooldown=2):
    return validate(dict(id=key, name=name, description=description, type='active',
        source_kind='character', ability_version=1, target=target, range=range,
        elevation_rule=rule, cost={'cooldown':cooldown, 'charges':None}, effects=effects))


def passive(key, name, description, modifiers=None, reaction=None):
    return dict(id=key, name=name, description=description, type='passive',
                modifiers=modifiers or {}, reaction=reaction)


def register(key, name, description, first, second, third):
    ids=[]
    for skill in (first, second, third):
        skill=deepcopy(skill);skill['id']=f'job:{key}:{skill["id"]}';skill['source_name']=name
        SKILLS[skill['id']]=skill;ids.append(skill['id'])
    JOBS[key]={'name':name, 'description':description, 'starter_skills':ids}


def strike(key, name, description, extra):
    return active(key,name,description,[{'type':'attack','damage_bonus':0},
        {**extra,'conditions':[{'type':'hit'}]}])


register('fighter','Fighter','Protect allies or break enemy positions.',
    strike('bash','Driving Strike','Melee hit pushes one cell. Stable enemies resist.',{'type':'displace','mode':'push','distance':1}),
    active('cover','Cover','Give an ally a 10 HP Barrier for one of their activations.',[{'type':'barrier','amount':10,'turns':1}], 'ally',2,'physical_care',3),
    passive('intercept','Intercept','Redirect one attack against an adjacent ally. Shares your reaction allowance.',reaction={'id':'intercept','name':'Intercept'}))
register('barbarian','Barbarian','Disrupt nearby enemies, at the cost of staying exposed.',
    strike('shove','Brutal Shove','Melee hit pushes one cell; walls stop displacement.',{'type':'displace','mode':'push','distance':1}),
    strike('expose','Crack Defenses','Melee hit applies Vulnerable for one target activation.',{'type':'status','status':'vulnerable','turns':1}),
    passive('anchored','Anchored','50 extra knockback resistance; does not prevent damage.',{'knockback_resistance':50}))
register('rogue','Rogue','Exploit weak targets and interfere with their attacks.',
    strike('bleed','Open Wound','Melee hit applies Bleed for two target activations.',{'type':'status','status':'bleed','turns':2}),
    strike('blind','Pocket Sand','Melee hit blinds for one target activation.',{'type':'status','status':'blind','turns':1}),
    passive('footwork','Footwork','Gain 5 evasion. Control effects still work.',{'evasion':5}))
register('ranger','Ranger','Set up accurate shots and control approaches.',
    active('mark','Track Quarry','Mark an enemy for two activations. Your first successful hit each activation gains 10 accuracy.',[{'type':'mark','turns':2,'accuracy':10}],range=5,rule='ballistic'),
    active('snare','Snaring Ground','Create binding ground under an enemy and adjacent legal cells for two of your activations.',[{'type':'zone','zone':'binding','radius':1,'turns':2}],range=4,rule='ballistic',cooldown=3),
    passive('footwork','Field Footwork','Gain 5 evasion; no extra damage.',{'evasion':5}))
register('mage','Mage','Create dangerous ground or protect a threatened ally.',
    active('embers','Ember Ground','Create enemy-burning ground for two of your activations. No friendly fire.',[{'type':'zone','zone':'ember','radius':1,'turns':2}],range=3,rule='line_of_effect',cooldown=3),
    active('ward','Ward','Give an ally a 10 HP Barrier for two of their activations.',[{'type':'barrier','amount':10,'turns':2}],'ally',3,'line_of_effect',3),
    passive('footwork','Light Step','Gain 5 evasion. Mute still prevents spells.',{'evasion':5}))
register('cleric','Cleric','Treat wounds and maintain a safe fighting position.',
    active('mend','Mend','Restore 12 HP to a living ally. Cannot revive.',[{'type':'heal','amount':12}],'ally',3,'line_of_effect',3),
    active('cleanse','Cleanse','Remove Poison, Bleed, Burn and Slow from an ally.',[{'type':'cleanse','statuses':['poison','bleed','burn','slow']}],'ally',3,'line_of_effect',3),
    passive('steadfast','Steadfast','Gain 1 armor. Does not make healing mandatory.',{'armor':1}))
register('monk','Monk','Fight nearby enemies with displacement and retaliation.',
    strike('palm','Driving Palm','Melee hit pushes one cell. Knockback resistance applies.',{'type':'displace','mode':'push','distance':1}),
    active('brace','Brace','Guard a nearby ally against the next incoming hit.',[{'type':'guard'}],'ally',1,'physical_care'),
    passive('riposte','Riposte','After surviving a melee hit, counter at half attack if in reach. Uses the shared reaction.',reaction={'id':'riposte','name':'Riposte'}))
register('bard','Bard','Keep allies fighting and weaken an enemy approach.',
    active('rally','Steady Song','Remove Fear and Slow from an ally and give an 8 HP Barrier for one activation.',[{'type':'cleanse','statuses':['fear','slow']},{'type':'barrier','amount':8,'turns':1}],'ally',3,'line_of_effect',3),
    active('discord','Discord','Slow an enemy for one activation. Resistance and immunities apply.',[{'type':'status','status':'slow','turns':1}],range=3,rule='line_of_effect',cooldown=3),
    passive('footwork','Stage Footwork','Gain 5 evasion.',{'evasion':5}))
register('druid','Druid','Change your fighting form or hold ground with thorns.',
    active('prowler','Prowler Form','Self only: INT-based melee and +1 movement for two of your activations. No healing on transformation.',[{'type':'form','form':'prowler','turns':2}],'ally',1,'line_of_effect',3),
    active('thorns','Thorn Ground','Create thorns around an enemy for two of your activations.',[{'type':'zone','zone':'thorns','radius':1,'turns':2}],range=3,rule='line_of_effect',cooldown=3),
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
    active('bind','Binding Line','Bind an enemy for one activation. Range 2; no damage or guaranteed capture.',[{'type':'status','status':'bind','turns':1,'chance':75}],range=2,rule='ballistic',cooldown=3),
    active('pull','Reel In','Pull an enemy one cell toward you. Stable targets resist. No damage.',[{'type':'displace','mode':'pull','distance':1}],range=2,rule='ballistic'),
    passive('anchored','Sure Grip','Gain 25 knockback resistance. Does not improve capture chance.',{'knockback_resistance':25}))


def eligible(character):
    return character.get('source_kind') not in {'champion','celestial'} and not character.get('temporary_mercenary')


def initialize(character):
    # Legacy characters opt in deliberately. No inferred class or equipment replacement.
    if eligible(character):
        character.setdefault('job_id',None)
        character.setdefault('learned_skills',[])
        character.setdefault('equipped_skills',[])
        character.setdefault('skill_slots',CAPACITY)
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


def public_catalog():
    return {'jobs':deepcopy(JOBS),'skills':deepcopy(SKILLS),'capacity':CAPACITY}
