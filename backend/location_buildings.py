"""Mission-specific dressing of reusable, independently authored footprints.

Sharing a footprint is intentional: a reclaimed store can be an armory or cache,
but its furniture, ground and entrances should tell the appropriate story.
"""
from copy import deepcopy


def add_location_buildings(buildings):
    sources = ['tool_long_store', 'tool_divided_store', 'tool_annex_yard', 'tool_twin_sheds']
    for group, family, floor, labels, furniture, scenery in [
        ('chapel', 'limestone', 'chapel_cracked',
         ['Roadside chapel nave', 'Chapel and vestry', 'Chapel with burial annex', 'Twin chapels and memorial court'],
         ['chapel_altar', 'chapel_pew', 'chapel_pew', 'ancient_reliquary_closed'],
         ['fallen_church_bell', 'fallen_gravestone']),
        ('armory', 'iron', 'smithy_cobbles',
         ['Guarded weapon store', 'Armory and locked magazine', 'Armory with loading yard', 'Twin magazines and drill court'],
         ['weapon_rack', 'shield_rack', 'arrow_crate', 'armor_stand'],
         ['military_supply_coffer_closed', 'open_toolbox']),
        ('cache', 'timber', 'shed_floor',
         ['Raider storehouse', 'Divided raider hideout', 'Cache house and sorting yard', 'Twin stores and stolen-goods court'],
         ['crate_closed', 'bound_barrels', 'wooden_table', 'treasure_chest_bronze_closed'],
         ['dispatch_satchel', 'wooden_handcart']),
    ]:
        for index, source in enumerate(sources):
            plan = deepcopy(buildings[source])
            plan.update(label=labels[index], family=family, floor=floor,
                        door_name={'chapel':'Chapel Door','armory':'Magazine Door','cache':'Storehouse Door'}[group])
            plan['furniture'] = [(furniture[i % len(furniture)], x, y)
                                 for i, (_, x, y) in enumerate(plan['furniture'])]
            plan['decorations'] = [(scenery[i % len(scenery)], x, y)
                                   for i, (_, x, y) in enumerate(plan['decorations'])]
            if index == 3:
                # Even a small patrol should occupy both stores, not leave the
                # entire second building empty because the budget truncates.
                plan['enemies'] = [plan['enemies'][i] for i in (0,4,1,5,2,6,3,7)]
            # Chapels/armories are intact; raider stores keep their escape breach.
            if group != 'cache':
                for x, y in plan.pop('breaches', []):
                    plan['doors'].append((x, y, 'door'))
            buildings[f'{group}_{index + 1}'] = plan

    sources = ['workshop_forge_yard', 'workshop_repair_hall', 'workshop_l_forge', 'workshop_courtyard_pair']
    labels = ['Gated toll court', 'Through-road customs hall', 'Toll post and inspection wing', 'Paired watch posts and crossing court']
    furniture = ['toll_desk', 'bound_barrels', 'crate_closed', 'weapon_rack', 'wooden_table', 'shield_rack']
    for index, source in enumerate(sources):
        plan = deepcopy(buildings[source])
        plan.update(label=labels[index], family='fieldstone', floor='toll_cobbles',
                    door_name='Watch Post Door',gate_name='Toll Gate')
        plan['furniture'] = [(furniture[i % len(furniture)], x, y)
                             for i, (_, x, y) in enumerate(plan['furniture'])]
        plan['decorations'] = [('wooden_handcart' if i else 'dispatch_satchel', x, y)
                               for i, (_, x, y) in enumerate(plan['decorations'])]
        if index == 0:
            plan['doors'].append((9, 4, 'gate'))
        if index == 3:
            plan['enemies'] = [plan['enemies'][i] for i in (0,4,1,5,2,6,3,7)]
        buildings[f'checkpoint_{index + 1}'] = plan
