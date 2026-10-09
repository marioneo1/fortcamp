"""Small early equipment gaps; bear trophies stay exclusive to the radiant bear."""
from .gear_expansion import weapon
from .gear_progression import armor

GEAR = {
 'bear_claws':weapon('Bear Claws','rare','knuckles',2,'DEX-based knuckles with +1 DEX; improves weapon damage and Monk techniques without extra on-hit procs.',weapon_scaling='dex',attribute_bonuses={'dex':1}),
 'padded_handwraps':weapon('Padded Handwraps','common','knuckles',1,'DEX-based fighting wraps with +1 DEX.',weapon_scaling='dex',attribute_bonuses={'dex':1}),
 'brass_knuckles':weapon('Brass Knuckles','common','knuckles',2,'Solid knuckles for STR-based punches.'),
 'iron_knuckles':weapon('Iron Knuckles','common','knuckles',2,'Balanced DEX-based knuckles.',weapon_scaling='dex'),
 'duelist_cestus':weapon('Duelist Cestus','uncommon','knuckles',2,'DEX-based knuckles with +1 AGI.',weapon_scaling='dex',attribute_bonuses={'agi':1}),
 'stonefist_gauntlets':weapon('Stonefist Gauntlets','rare','knuckles',3,'Heavy knuckles with +1 STR and -1 AGI.',attribute_bonuses={'str':1,'agi':-1}),
 'balanced_dagger':weapon('Balanced Dagger','common','dagger',2,'A DEX-based close-combat dagger.',weapon_scaling='dex'),
 'skinners_knife':weapon("Skinner's Knife",'uncommon','dagger',2,'DEX-based knife with +1 DEX.',weapon_scaling='dex',attribute_bonuses={'dex':1}),
 'parrying_dagger':weapon('Parrying Dagger','uncommon','dagger',1,'A light DEX-based dagger with +1 AGI.',weapon_scaling='dex',attribute_bonuses={'agi':1}),
 'oak_war_mace':weapon('Oak War Mace','common','mace',2,'A weighted wooden mace for STR-based attacks.'),
 'flanged_mace':weapon('Flanged Mace','uncommon','mace',3,'A heavy steel mace with -1 AGI.',attribute_bonuses={'agi':-1}),
 'weathered_spellbook':weapon('Weathered Spellbook','common','grimoire',1,'An INT-based spell focus for ranged magic.'),
 'field_grimoire':weapon('Field Grimoire','common','grimoire',2,'A sturdy INT-based spell focus for ranged magic.'),
 'runebound_folio':weapon('Runebound Folio','uncommon','grimoire',2,'An INT-based spell focus with +1 INT.',attribute_bonuses={'int':1}),
 'cloth_headband':armor('Cloth Headband','head','common','Light headwear with +1 AGI.',{'agi':1}),
 'leather_wristguards':armor('Leather Wristguards','hands','common','Flexible wristguards with +1 DEX.',{'dex':1}),
 'padded_leggings':armor('Padded Leggings','legs','common','Padded legwear with +1 VIT.',{'vit':1}),
 'gripsole_boots':armor('Gripsole Boots','feet','common','Light field boots with +1 AGI.',{'agi':1}),
 'trappers_charm':armor("Trapper's Charm",'accessory','common','A small field charm with +1 INT.',{'int':1}),
 'thick_bear_pelt':armor('Thick Bear Pelt','body','uncommon','A heavy protective pelt with +2 VIT and -1 AGI.',{'vit':2,'agi':-1}),
}


def apply(items, loot):
    from copy import deepcopy
    for iid,item in GEAR.items():
        items[iid]=deepcopy(item)
        items[iid]['icon']=f'/assets/catalogue/items/{iid}.png'
        if iid not in {'bear_claws','thick_bear_pelt'}:
            loot.append((iid,'E' if item['rarity']=='common' else 'D',1))
