def starter_kit(traits,perks):
    for trait,kit in [('fire_magic',['cracked_wand']),('scout',['frayed_bow']),('guard',['chipped_sword','splintered_shield']),('engineer',['worn_mallet']),('medic',['knotted_staff'])]:
        if trait in traits:return kit
    if perks.get('magic') not in (None,'none'):return ['cracked_wand']
    if perks.get('combat') not in (None,'none'):return ['chipped_sword']
    return ['rusty_knife']
