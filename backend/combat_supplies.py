"""Battle supplies are owned inventory copies, spent immediately under the player lock."""
from copy import deepcopy

SUPPLIES = {
    'field_dressing': {'name': 'Field Dressing', 'heal': 18, 'cleanses': ['bleed'], 'rarity': 'common', 'art': 'training_manual'},
    'restorative_tonic': {'name': 'Restorative Tonic', 'heal': 32, 'cleanses': [], 'rarity': 'uncommon', 'art': 'ember_charm'},
    'cleansing_salts': {'name': 'Cleansing Salts', 'heal': 0, 'cleanses': ['poison', 'burn', 'blind', 'mute', 'slow', 'bind', 'freeze', 'confuse', 'charm', 'berserk', 'paralyze', 'sleep', 'stun'], 'rarity': 'uncommon', 'art': 'warding_token'},
}

def sync_supplies(battle, state):
    battle['supplies'] = [dict(instance_id=i['instance_id'], item_id=i['item_id'], **deepcopy(SUPPLIES[i['item_id']]))
                          for i in state.get('inventory', []) if i['item_id'] in SUPPLIES]
    battle.setdefault('supplies_used', [])
    battle.setdefault('supply_limit', 3)

def remaining_uses(battle):
    return max(0, int(battle.get('supply_limit', 3)) - len(battle.get('supplies_used', [])))

def apply_combat_content(items, general):
    for iid, d in SUPPLIES.items():
        clears = ', '.join(d['cleanses'])
        description = f"Battle action: {'restore '+str(d['heal'])+' HP' if d['heal'] else 'treat an ally'} at range 1."
        if clears:
            description += f" Removes {clears}."
        description += ' Does not revive unconscious units. The party can use three supplies per battle.'
        items[iid] = {'name': d['name'], 'rarity': d['rarity'], 'slot': None, 'tags': ['consumable'],
                      'bonuses': {}, 'attribute_bonuses': {}, 'description': description,
                      'icon': f"/assets/catalogue/items/{d['art']}.png"}
        general.append((iid, 'E' if d['rarity'] == 'common' else 'D', 5))
    skills = {
        'medic_coat': ('Field Care', 1, 12, ['bleed']),
        'garden_healers_pin': ('Garden Remedy', 2, 14, ['poison']),
        'mourning_censer': ('Restoring Light', 3, 16, ['burn', 'blind']),
        'oathkeeper_shard': ('Break the Binding', 3, 0, ['bind', 'freeze', 'mute', 'charm', 'confuse']),
    }
    for iid, (name, reach, heal, clears) in skills.items():
        items[iid]['combat_skill'] = {
            'id': name.lower().replace(' ', '_'), 'name': name, 'target': 'ally', 'effect': 'support',
            'range': reach, 'elevation_rule': 'physical_care' if iid == 'medic_coat' else 'line_of_effect', 'scaling': 'int',
            'heal': heal, 'cleanses': clears,
            'description': f"One shared technique use per battle. Range {reach}; restores {heal} + half INT HP" if heal else f"One shared technique use per battle. Range {reach}; no healing",
        }
        items[iid]['combat_skill']['description'] += '; removes ' + ', '.join(clears) + '. Requires line of sight; cannot revive.'
    # Existing weapons acquire deliberate control identities, not universal elemental procs.
    for iid, sid, chance, turns in [
        ('winterglass_grimoire', 'freeze', 18, 1), ('weighted_sling', 'stun', 15, 1),
        ('goblin_net_bow', 'bind', 25, 2), ('hunters_bola', 'slow', 25, 2),
        ('goblin_notched_axe', 'bleed', 20, 2), ('prism_tuning_fork', 'paralyze', 18, 2),
    ]:
        items[iid]['on_hit'] = {'id': sid, 'chance': chance, 'turns': turns}
        items[iid]['description'] += f" Lethal hits have a {chance}% chance to inflict {sid} for {turns} activation{'s' if turns != 1 else ''}."
