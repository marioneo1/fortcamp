"""Persistent first-sighting rules for bush cover, independent of combat AI."""
from .battle_maps import occupied_tiles

BUSH_SPRITES = frozenset({'dense_shrub', 'thorny_bramble', 'bush'})
HELP = ('Bushes can hide enemies, even beside you. They reveal themselves when attacking, '
        'leaving cover, or when you run into their occupied tile. '
        'Once revealed, enemies stay visible for this battle.')


def cover_cells(battle):
    return {cell for entry in battle.get('terrain', []) + battle.get('decorations', [])
            if not entry.get('destroyed') and not entry.get('carried_by')
            and (entry.get('conceals_units') or entry.get('kind') == 'bush'
                 or entry.get('sprite') in BUSH_SPRITES)
            for cell in occupied_tiles(entry)}


def unseen(unit):
    return unit.get('team') == 'enemy' and unit.get('spotted') is False


def reveal(battle, unit, reason=None):
    if not unseen(unit):
        return False
    unit['spotted'] = True
    message = (f"You run into {unit['name']} hiding in the brush." if reason == 'contact'
               else f"{unit['name']} is revealed in the brush.")
    battle.setdefault('log', []).append(message)
    return True


def refresh(battle):
    covers = cover_cells(battle)
    if not covers and not any(unseen(u) for u in battle.get('units', {}).values()):
        return False
    observers = [u for u in battle.get('units', {}).values() if u.get('team') == 'player'
                 and u.get('alive') and u.get('conscious', True)
                 and not u.get('extracted') and not u.get('carried_by')]
    searched = {tuple(p) for p in battle.get('searched_bushes', [])}
    # Looking at brush does not clear it. Only physically checked cells are searched.
    searched.update((u['x'], u['y']) for u in observers if (u['x'], u['y']) in covers)
    battle['searched_bushes'] = [list(p) for p in sorted(searched)]
    changed = False
    for unit in battle.get('units', {}).values():
        if unit.get('team') != 'enemy':
            continue
        # Older in-progress saves keep enemies already presented to the player visible.
        unit.setdefault('spotted', bool(battle.get('action_count', 0)) or (unit['x'],unit['y']) not in covers)
        if unseen(unit) and ((unit['x'],unit['y']) not in covers
                or not unit.get('alive') or not unit.get('conscious', True)):
            changed = reveal(battle, unit) or changed
    return changed
