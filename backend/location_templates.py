"""Saved building plans. Rectangles include the perimeter; doorways are world cells."""
BUILDING_PLANS = {
    'tool_shed': [{'id':name,'building':name,'anchor':(5,1)} for name in
        ['tool_long_store','tool_divided_store','tool_annex_yard','tool_twin_sheds']],
    'repair_yard': [{'id':name,'building':name,'anchor':(5,1)} for name in
        ['workshop_forge_yard','workshop_courtyard_pair','workshop_l_forge','workshop_repair_hall']],
    'open_armory': [
        {'id':'armory_north_south_stores','rooms':[
            ('north_store',(7,0,6,4),(9,3)),('south_store',(7,7,6,4),(9,7))],
         'furniture':[('weapon_rack',8,1),('shield_rack',10,1),('arrow_crate',11,1),
                      ('weapon_rack',8,9),('armor_stand',11,9)],
         'enemies':[(8,2),(9,2),(10,2),(11,2),(8,8),(9,8),(10,8),(11,8)]},
        {'id':'armory_east_west_stores','rooms':[
            ('west_store',(2,1,4,6),(5,4)),('east_store',(9,1,4,6),(9,4))],
         'furniture':[('weapon_rack',3,5),('shield_rack',4,5),('arrow_crate',10,5),('armor_stand',11,5)],
         'enemies':[(3,2),(4,2),(3,3),(4,3),(10,2),(11,2),(10,3),(11,3)],
         'players':[(5,9),(6,9),(7,9),(8,9)],
         'exit':[(x,10) for x in range(4,10)]},
    ],
}

# The earlier two armory enclosures remain in docs/maps/archive; current maps
# share calibrated building parts rather than the legacy enclosure assembler.
for _location, _group in [('chapel_approach', 'chapel'), ('open_armory', 'armory'),
                           ('raider_cache', 'cache'), ('toll_post', 'checkpoint')]:
    BUILDING_PLANS[_location] = [
        {'id': f'{_group}_{i}', 'building': f'{_group}_{i}', 'anchor': (5, 1)}
        for i in range(1, 5)
    ]
# A reclaimed workshop uses the same four footprints with a different owner.
BUILDING_PLANS['salvage_court'] = [dict(plan) for plan in BUILDING_PLANS['repair_yard']]
