"""Shared bounded perk mechanics; equipment grants use the same rules."""
from copy import deepcopy

PERK_EFFECTS = {
    'scout':{'combat':{'move':1,'initiative':2}}, 'guard':{'combat':{'armor':1}},
    'engineer':{'capabilities':{'building':2}}, 'medic':{'capabilities':{'medicine':2}},
    'tracker':{'capabilities':{'survival':2}}, 'pathfinder':{'combat':{'move':1},'capabilities':{'survival':1}},
    'goblin_hunter':{'combat':{'damage_goblin':2}}, 'undead_hunter':{'combat':{'damage_deathless':2}},
    'exorcist':{'capabilities':{'magic':1},'combat':{'damage_deathless':1}},
    'fire_magic':{'attributes':{'int':1}}, 'divine_magic':{'attributes':{'int':1},'capabilities':{'medicine':1}},
    'priestess':{'capabilities':{'medicine':2}}, 'knight':{'combat':{'armor':1,'hp':4}},
    'swordsman':{'combat':{'melee_damage':1}}, 'magic_resistance':{'combat':{'magic_reduction':20}},
    'warhost_veteran':{'combat':{'damage_goblin':1,'hp':3}}, 'graveward':{'combat':{'damage_deathless':1}},
    'ley_touched':{'capabilities':{'magic':1}}, 'beast_bond':{'capabilities':{'survival':1}},
    'star_touched':{'attributes':{'int':1}}, 'night_paws':{'combat':{'initiative':2,'evasion':3}},
    'feral_agility':{'combat':{'move':1}}, 'scaled_hide':{'combat':{'armor':1}},
    'precision_core':{'combat':{'accuracy':5}}, 'regeneration':{'combat':{'regeneration':2}},
    'troll_blood':{'combat':{'hp':5}}, 'iron_stomach':{'attributes':{'vit':1}},
    'alchemical_body':{'capabilities':{'alchemy':2}}, 'radiant_soul':{'combat':{'damage_deathless':1}},
    'wailing_magic':{'attributes':{'int':1}}, 'bannerbreaker':{'combat':{'armor':1,'initiative':2}},
    'keeper_of_last_rites':{'combat':{'damage_deathless':2}}, 'meridian_attunement':{'capabilities':{'magic':2,'building':1}},
    'riftwalker':{'combat':{'move':1}}, 'trapper':{'capabilities':{'survival':1}},
    'field_fortifier':{'capabilities':{'building':1}},
    'darkvision':{'combat':{'accuracy':3,'initiative':1}},
    'verdant_soul':{'combat':{'hp':4},'capabilities':{'medicine':1}},
    'wildsong':{'capabilities':{'survival':1}},
    'foxfire':{'attributes':{'int':1}},
    'trickster':{'combat':{'evasion':5}},
    'waterborn':{'capabilities':{'survival':1}},
    'tide_sense':{'capabilities':{'survival':2}},
    'draconic_legacy':{'combat':{'hp':5}},
    'glamour':{'combat':{'evasion':5}},
    'amorphous':{'combat':{'evasion':3}},
    'incorporeal':{'combat':{'move':1}},
    'alien_physiology':{'attributes':{'vit':1}},
    'aether_hunger':{'capabilities':{'magic':2},'combat':{'hp':-4}},
    'heatproof':{'attributes':{'vit':1},'capabilities':{'survival':1}},
    'goblin_survivor':{'combat':{'hp':4},'capabilities':{'survival':1}},
    'moon_sense':{'combat':{'initiative':1},'capabilities':{'survival':1}},
    'warhost_command':{'combat':{'initiative':3},'capabilities':{'combat':1}},
    'stellar_aegis':{'combat':{'armor':2,'magic_reduction':10}},
    'astral_sense':{'combat':{'accuracy':5},'capabilities':{'magic':1}},
    'soul_anchor':{'combat':{'hp':4}},
    'void_sight':{'combat':{'accuracy':5}},
    'stormbound':{'combat':{'initiative':2},'capabilities':{'magic':1}},
}
COMBAT_LABELS={'move':'movement','initiative':'initiative','armor':'armor','hp':'maximum HP','evasion':'evasion (percentage points)','accuracy':'accuracy (percentage points)','regeneration':'HP restored each new round','damage_goblin':'damage against Goblinoids','damage_deathless':'damage against Deathless','melee_damage':'melee damage','magic_reduction':'% less incoming magic damage','capture_chance':'capture chance (percentage points)'}

def annotate_perks(definitions):
    for key,effects in PERK_EFFECTS.items():
        if key not in definitions:continue
        definition=definitions[key];definition['modifiers']=deepcopy(effects)
        parts=[f'+{value} {stat.upper()}' for stat,value in effects.get('attributes',{}).items()]
        parts += [f'+{value} {stat} capability' for stat,value in effects.get('capabilities',{}).items()]
        parts += [f'{value}% less incoming magic damage' if stat=='magic_reduction' else f'+{value} {COMBAT_LABELS[stat]}' for stat,value in effects.get('combat',{}).items()]
        definition['effect']='. '.join(parts)+'. '+definition['effect']

def character_perks(state,character,items):
    found=set(character.get('traits',[]));inventory={i['instance_id']:i for i in state.get('inventory',[])}
    for iid in character.get('equipment',{}).values():found.update(items.get(inventory.get(iid,{}).get('item_id'),{}).get('granted_perks',[]))
    return found

def modifiers(state,character,items,section):
    totals={}
    for perk in sorted(character_perks(state,character,items)):
        for key,value in PERK_EFFECTS.get(perk,{}).get(section,{}).items():totals[key]=totals.get(key,0)+value
    caps={'move':2,'armor':3,'evasion':12,'accuracy':15,'magic_reduction':40,'regeneration':4,'hp':15,'initiative':6,'damage_goblin':3,'damage_deathless':3,'melee_damage':2}
    return {key:min(value,caps.get(key,4)) for key,value in totals.items()}
