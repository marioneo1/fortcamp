"""Personal quirks, compatible generation and deliberately rank-independent rarity."""
import random

DEFINITIONS = {}
EFFECTS = {}
GROUPS = {}
RARITY = {}

def _trait(key, name, description, effects, groups=(), rarity='common'):
    DEFINITIONS[key] = (name, description)
    EFFECTS[key] = effects
    GROUPS[key] = set(groups)
    RARITY[key] = rarity

for key, name, amount in [('hearty','Hearty',5),('robust','Robust',7),('stout','Stout',10),
                          ('frail','Frail',-5),('sickly','Sickly',-7),('delicate','Delicate',-10)]:
    _trait(key,name,f'{amount:+} maximum HP.',{'combat':{'hp':amount}},('constitution',),
           'rare' if abs(amount)==10 else 'uncommon' if abs(amount)==7 else 'common')

for key,name,stat,value,group in [
    ('sure_footed','Sure-Footed','evasion',5,'evasion'),('clumsy','Clumsy','evasion',-5,'evasion'),
    ('light_footed','Light-Footed','move',1,'movement'),('heavy_footed','Heavy-Footed','move',-1,'movement'),
    ('resilient','Resilient','incoming_reduction',1,'mitigation'),('thin_skinned','Thin-Skinned','incoming_reduction',-1,'mitigation'),
    ('quick_witted','Quick-Witted','initiative',2,'initiative'),('slow_to_react','Slow to React','initiative',-2,'initiative'),
    ('accurate','Accurate','accuracy',5,'accuracy'),('inattentive','Inattentive','accuracy',-5,'accuracy'),
    ('heavy_fisted','Heavy-Fisted','unarmed_bonus',3,'unarmed'),('weak_fisted','Weak-Fisted','unarmed_bonus',-1,'unarmed'),
    ('far_sighted','Far-Sighted','ranged_range',1,'range'),('short_sighted','Short-Sighted','ranged_range',-1,'range'),
    ('enterprising','Enterprising','mission_gold',1,'gold')]:
    desc = {'move':f'{value:+} normal movement; mobile units retain at least one tile.',
            'evasion':f'{value:+} evasion.', 'initiative':f'{value:+} initiative.', 'accuracy':f'{value:+} accuracy.',
            'incoming_reduction':f'{abs(value)}% {"less" if value>0 else "more"} damage received from all sources.',
            'unarmed_bonus':f'{value:+} unarmed damage per attack action, shared across its hits; does not affect Rat Form.',
            'ranged_range':f'{value:+} bow/crossbow weapon range for Rangers; fixed-range techniques are unchanged.',
            'mission_gold':'+1 gold when a mission you participate in awards gold.'}[stat]
    _trait(key,name,desc,{'combat':{stat:value}},(group,), 'uncommon' if stat in {'move','ranged_range','unarmed_bonus'} else 'common')

for key,name,values in [
    ('lucky','Lucky',{'luk':1}),('unlucky','Unlucky',{'luk':-1}),
    ('wiry','Wiry',{'str':-2,'agi':1}),
    ('broad_shouldered','Broad-Shouldered',{'str':1,'vit':1,'agi':-1}),
    ('keen_eyed','Keen-Eyed',{'dex':1,'str':-1}),('scholarly','Scholarly',{'int':2,'vit':-1}),
    ('superstitious','Superstitious',{'luk':1,'int':-1}),('meticulous','Meticulous',{'dex':1,'agi':-1}),
    ('brawny','Brawny',{'str':2,'int':-1}),('resolute','Resolute',{'vit':2,'dex':-1}),
    ('quick_fingered','Quick-Fingered',{'dex':2,'vit':-1}),('fleet','Fleet',{'agi':2,'vit':-1}),
    ('frail_scholar','Frail Scholar',{'int':2,'vit':-2}),('practical','Practical',{'vit':1,'str':1,'int':-1})]:
    groups=['luck'] if key in {'lucky','unlucky'} else ['redistribution']
    if 'luk' in values and key not in {'lucky','unlucky'}:groups.append('luck')
    effects={'attributes':values}
    if key=='keen_eyed':effects['combat']={'accuracy':5};groups.append('accuracy')
    _trait(key,name,', '.join(f'{v:+} {s.upper()}' for s,v in values.items()) + ('; +5 accuracy.' if key=='keen_eyed' else '.'),effects,groups)

for key,name,effects,groups in [
    ('athletic','Athletic',{'move':1,'evasion':-5},('movement','evasion')),
    ('impulsive','Impulsive',{'initiative':2,'accuracy':-5},('initiative','accuracy')),
    ('cautious','Cautious',{'evasion':5,'initiative':-2},('evasion','initiative'))]:
    _trait(key,name,', '.join(f'{v:+} {s}' for s,v in effects.items())+'.',{'combat':effects},groups)

for sid, entries in {
    'burn':[('hardy','Hardy',25),('heat_hardened','Heat-Hardened',50),('heat_sensitive','Heat-Sensitive',-25)],
    'poison':[('iron_stomached','Iron-Stomached',25),('toxin_hardened','Toxin-Hardened',50),('sensitive_stomach','Sensitive Stomach',-25)],
    'bleed':[('thick_blooded','Thick-Blooded',25),('quick_clotting','Quick-Clotting',50),('bleeds_easily','Bleeds Easily',-25)],
}.items():
    for key,name,value in entries:
        _trait(key,name,f'{abs(value)}% {"less" if value>0 else "more"} {sid.title()} damage; does not prevent its application.',
               {'combat':{f'{sid}_damage_reduction':value}},(f'{sid}_damage',),'rare' if value==50 else 'uncommon')

for sid,entries in {
    'sleep':[('alert','Alert',25),('wakeful','Wakeful',50),('restless','Restless',75)],
    'stun':[('tough','Tough',25),('unflinching','Unflinching',50),('steadfast','Steadfast',75)],
    'fear':[('brave','Brave',25),('fearless','Fearless',75)],
    'bind':[('slippery','Slippery',25),('escape_artist','Escape Artist',50)],
}.items():
    for key,name,value in entries:
        _trait(key,name,f'{value}% {sid.title()} application resistance; uses the strongest applicable resistance.',
               {'combat':{f'{sid}_resistance':value}},(f'{sid}_resistance',),'rare' if value==75 else 'uncommon')

_trait('stubborn','Stubborn','25% displacement resistance; −1 AGI.',
       {'attributes':{'agi':-1},'combat':{'displacement_resistance':25}},('redistribution','displacement'),'uncommon')
_trait('adaptable','Adaptable','+1 random attribute for each battle; rolled once, never changes permanent attributes.',
       {'combat':{'battle_attribute':1}},('redistribution','battle_attribute'),'uncommon')
_trait('distracted','Distracted','−1 random attribute for each battle; rolled once, attributes remain at least one.',
       {'combat':{'battle_attribute':-1}},('redistribution','battle_attribute'))
_trait('naturally_gifted','Naturally Gifted','+1 STR, DEX, AGI, VIT, INT and LUK.',
       {'attributes':{s:1 for s in ('str','dex','agi','vit','int','luk')}},(),'exceptional')

# Existing backgrounds share the same single-profile rule.
for key in ('strong_armed','nimble','bookish','steady_handed'):
    GROUPS[key]={'redistribution'}

def compatible(existing, candidate):
    if candidate in existing:return False
    groups=GROUPS.get(candidate,set())
    return not any(groups & GROUPS.get(key,set()) for key in existing)

def extend(existing, candidates):
    result=list(dict.fromkeys(existing))
    for key in candidates:
        if compatible(result,key):result.append(key)
    return result

def roll(existing, rng, *, job_id=None, rank='E', level=1, encounter=False):
    """One optional quirk. Rank and level deliberately cannot exclude rare traits."""
    # Separate probability from pool size: adding traits never dilutes Gifted.
    point=rng.random()
    if point<.000001:
        if encounter:return None  # The encounter's opening roll already handles Gifted.
        tier='exceptional'
    elif point<.005001:tier='rare'
    elif point<.080001:tier='uncommon'
    elif point<.600001:tier='common'
    else:return None
    def rarity(key):
        effect=EFFECTS[key]
        # Preserve authored encounter HP budgets in ordinary rolls; exceptional
        # constitutions remain possible, rather than being level-gated.
        if encounter and RARITY[key]!='exceptional' and (effect.get('combat',{}).get('hp') or effect.get('attributes',{}).get('vit')):
            return 'rare'
        return RARITY[key]
    pool=[key for key in DEFINITIONS if rarity(key)==tier and compatible(existing,key)
          and (key not in {'far_sighted','short_sighted'} or job_id=='ranger')]
    return rng.choice(pool) if pool else None

def generated_traits(existing, seed, job_id=None):
    perk=roll(existing,random.Random(f'{seed}:general-quirk'),job_id=job_id)
    return extend(existing,[perk]) if perk else list(existing)

def battle_character(character, seed):
    """Temporary stat overlay before the normal derived-stat and skill snapshot."""
    from copy import deepcopy
    amount=sum(EFFECTS.get(k,{}).get('combat',{}).get('battle_attribute',0) for k in character.get('traits',[]))
    if not amount:return character,None
    result=deepcopy(character)
    stat=random.Random(f'{seed}:attribute:{character["id"]}').choice(('str','dex','agi','vit','int','luk'))
    attrs=result.setdefault('attributes',{})
    result['_battle_attribute_base']={stat:int(attrs.get(stat,5))}
    attrs[stat]=max(1,int(attrs.get(stat,5))+amount)
    return result,{'attribute':stat,'amount':amount}

def incoming(unit, source, damage):
    perks=unit.get('perk_modifiers',{})
    damage*=1-perks.get('incoming_reduction',0)/100
    sid=source.get('percent_dot')
    if sid in {'burn','poison','bleed'}:damage*=1-perks.get(f'{sid}_damage_reduction',0)/100
    return max(0,damage)
