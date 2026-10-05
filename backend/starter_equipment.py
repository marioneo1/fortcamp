STARTING_ROLES = {
    'fighter': {'name':'Fighter','description':'A durable front-line fighter with a worn sword and shield.','perk':'guard','proficiency':'combat','kit':['chipped_sword','splintered_shield']},
    'ranger': {'name':'Ranger','description':'A mobile ranged fighter. Bow damage uses DEX.','perk':'scout','proficiency':'combat','kit':['frayed_bow']},
    'mage': {'name':'Mage','description':'A beginning spellcaster. Wand attacks use INT.','perk':'arcane_apprentice','proficiency':'magic','kit':['cracked_wand']},
    'captor': {'name':'Captor','description':'A restraint specialist. Capture checks reward balanced STR, DEX and INT; your weapon cannot kill.','perk':'captor','proficiency':'combat','kit':['frayed_capture_net']},
    'barbarian': {'name':'Barbarian','description':'Disrupt enemies with an axe, displacement and resistance to knockback.','perk':None,'proficiency':'combat','kit':['nicked_axe']},
    'rogue': {'name':'Rogue','description':'A DEX-based melee fighter who uses wounds and disabling tricks.','perk':None,'proficiency':'combat','kit':['pitted_dagger']},
    'cleric': {'name':'Cleric','description':'Fight with an INT-based prayer rod; heal living allies or remove harmful effects.','perk':None,'proficiency':'magic','kit':['tarnished_prayer_rod']},
    'monk': {'name':'Monk','description':'DEX-based close combat, displacement and a shared counter reaction.','perk':None,'proficiency':'combat','kit':['frayed_handwraps']},
    'bard': {'name':'Bard','description':'INT-based ranged basics, protection and interference.','perk':None,'proficiency':'magic','kit':['battered_song_focus']},
    'druid': {'name':'Druid','description':'INT-based ranged basics, melee forms and dangerous ground.','perk':None,'proficiency':'magic','kit':['weathered_grove_staff']},
    'engineer': {'name':'Engineer','description':'Spend finite Components on machinery. Personal mallet attacks use STR.','perk':'engineer','proficiency':'building','kit':['worn_mallet','bent_tool_kit']},
    'summoner': {'name':'Summoner','description':'INT-based ranged basics and owner-linked companions. Commanded attacks spend your action.','perk':None,'proficiency':'magic','kit':['faded_calling_focus']},
}

STARTER_PRICES={'rusty_knife':4,'chipped_sword':6,'splintered_shield':5,'frayed_bow':6,
    'cracked_wand':6,'frayed_capture_net':6,'worn_mallet':4,'knotted_staff':4,
    'worn_jacket':5,'work_boots':4,'nicked_axe':6,'pitted_dagger':6,
    'tarnished_prayer_rod':6,'frayed_handwraps':6,'battered_song_focus':6,
    'weathered_grove_staff':6,'faded_calling_focus':6,'bent_tool_kit':5}


def apply_starter_content(items):
    definitions={
        'nicked_axe':('Nicked Axe','axe','str',['melee','improvised'],'A cheap axe with a damaged edge.','scrap_hatchet'),
        'pitted_dagger':('Pitted Dagger','dagger','dex',['melee','improvised'],'A small worn blade. Basic attacks use DEX.','rusty_knife'),
        'tarnished_prayer_rod':('Tarnished Prayer Rod','wand','int',['magic','magic_focus','improvised'],'A battered prayer rod with a weak basic bolt.','ember_staff'),
        'frayed_handwraps':('Frayed Handwraps','unarmed','dex',['melee','improvised'],'Worn fighting wraps. Basic strikes use DEX.','rescue_gloves'),
        'battered_song_focus':('Battered Song Focus','wand','int',['magic','magic_focus','improvised'],'A chipped musical focus with a weak resonant bolt.','ember_staff'),
        'weathered_grove_staff':('Weathered Grove Staff','staff','int',['magic','magic_focus','improvised'],'A weathered staff that still carries a weak natural bolt.','ember_staff'),
        'faded_calling_focus':('Faded Calling Focus','wand','int',['magic','magic_focus','improvised'],'A faded summoning focus with a weak basic bolt.','ember_staff'),
    }
    for key,(name,kind,scaling,tags,description,icon) in definitions.items():
        items[key]={'name':name,'slot':'weapon','weapon_type':kind,'weapon_scaling':scaling,
            'power':1,'tags':tags,'bonuses':{'magic' if scaling=='int' else 'combat':1},
            'rarity':'common','description':description,'icon':f'/assets/catalogue/items/{icon}.png'}
    items['bent_tool_kit']={'name':'Bent Tool Kit','slot':'offhand','tags':['construction_gear','improvised'],
        'bonuses':{'building':1},'rarity':'common','description':'Poor tools for field work. Does not grant extra Components.',
        'icon':'/assets/catalogue/items/work_gloves.png'}

def starter_kit(traits,perks):
    if 'captor' in traits:return ['frayed_capture_net']
    if 'arcane_apprentice' in traits:return ['cracked_wand']
    for trait,kit in [('fire_magic',['cracked_wand']),('scout',['frayed_bow']),('guard',['chipped_sword','splintered_shield']),('engineer',['worn_mallet']),('medic',['knotted_staff'])]:
        if trait in traits:return kit
    if perks.get('magic') not in (None,'none'):return ['cracked_wand']
    if perks.get('combat') not in (None,'none'):return ['chipped_sword']
    return ['rusty_knife']
