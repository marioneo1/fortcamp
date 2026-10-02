"""Saved building plans. Rectangles include the perimeter; doorways are world cells."""
BUILDING_PLANS = {
    'repair_yard': [
        {'id': 'enclosed_repair_yard', 'rooms': [], 'legacy': True},
        {'id': 'workshops_across_courtyard', 'rooms': [
            ('north_shop', (7,0,6,5), (9,4)), ('south_shop', (7,6,6,5), (9,6))],
         'furniture': [('repair_workbench',8,1),('carpenter_tool_rack',10,1),('small_coal_forge',11,3),
                       ('iron_anvil',8,9),('repair_workbench',10,9)],
         'enemies': [(8,3),(9,3),(10,3),(11,2),(8,7),(9,7),(10,7),(11,8)]},
        {'id': 'forge_house_and_open_bays', 'rooms': [('forge_house',(7,1,6,7),(7,4))],
         'furniture': [('small_coal_forge',11,2),('iron_anvil',9,2),('carpenter_tool_rack',11,6),
                       ('repair_workbench',5,8),('carpenter_sawhorse',8,9)],
         'enemies': [(8,3),(9,3),(10,3),(11,3),(8,5),(9,5),(10,5),(11,5)]},
    ],
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
