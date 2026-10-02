STARTING_ROLES = {
    'fighter': {'name':'Fighter','description':'A durable front-line fighter with a worn sword and shield.','perk':'guard','proficiency':'combat','kit':['chipped_sword','splintered_shield']},
    'ranger': {'name':'Ranger','description':'A mobile ranged fighter. Bow damage uses DEX.','perk':'scout','proficiency':'combat','kit':['frayed_bow']},
    'mage': {'name':'Mage','description':'A beginning spellcaster. Wand attacks use INT.','perk':'arcane_apprentice','proficiency':'magic','kit':['cracked_wand']},
    'captor': {'name':'Captor','description':'A restraint specialist. Capture checks reward balanced STR, DEX and INT; your weapon cannot kill.','perk':'captor','proficiency':'combat','kit':['frayed_capture_net']},
    'medic': {'name':'Medic','description':'Treat allies in battle. The worn wand uses INT, which also improves healing.','perk':'medic','proficiency':'medicine','kit':['cracked_wand']},
    'engineer': {'name':'Engineer','description':'Build and prepare defenses; wield a discarded STR-based mallet in battle.','perk':'engineer','proficiency':'building','kit':['worn_mallet']},
}

def starter_kit(traits,perks):
    if 'captor' in traits:return ['frayed_capture_net']
    if 'arcane_apprentice' in traits:return ['cracked_wand']
    for trait,kit in [('fire_magic',['cracked_wand']),('scout',['frayed_bow']),('guard',['chipped_sword','splintered_shield']),('engineer',['worn_mallet']),('medic',['knotted_staff'])]:
        if trait in traits:return kit
    if perks.get('magic') not in (None,'none'):return ['cracked_wand']
    if perks.get('combat') not in (None,'none'):return ['chipped_sword']
    return ['rusty_knife']
