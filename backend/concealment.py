"""Persistent first-sighting rules for bush cover, independent of combat AI."""
from .battle_maps import occupied_tiles

BUSH_SPRITES = frozenset({'dense_shrub', 'thorny_bramble', 'bush'})
HELP = ('Bushes can conceal enemies you have not spotted. Get within two tiles with a clear '
        'line of sight to reveal them. Leaving cover or attacking also reveals them. '
        'Once spotted, enemies stay visible for this battle.')


def cover_cells(battle):
    return {cell for entry in battle.get('terrain', []) + battle.get('decorations', [])
            if not entry.get('destroyed') and not entry.get('carried_by')
            and (entry.get('conceals_units') or entry.get('kind') == 'bush'
                 or entry.get('sprite') in BUSH_SPRITES)
            for cell in occupied_tiles(entry)}


def unseen(unit):
    return unit.get('team') == 'enemy' and unit.get('spotted') is False


def reveal(battle, unit):
    if not unseen(unit):
        return False
    unit['spotted'] = True
    battle.setdefault('log', []).append(f"{unit['name']} is spotted in the brush.")
    return True


def refresh(battle, line_of_sight):
    covers = cover_cells(battle)
    if not covers and not any(unseen(u) for u in battle.get('units', {}).values()):
        return False
    observers = [u for u in battle.get('units', {}).values() if u.get('team') == 'player'
                 and u.get('alive') and u.get('conscious', True)
                 and not u.get('extracted') and not u.get('carried_by')]
    searched = {tuple(p) for p in battle.get('searched_bushes', [])}
    observed = set()
    for x, y in covers:
        if any(abs(u['x']-x)+abs(u['y']-y) <= 2
               and line_of_sight(battle, u, {'x':x, 'y':y}) for u in observers):
            searched.add((x, y))
            observed.add((x, y))
    battle['searched_bushes'] = [list(p) for p in sorted(searched)]
    changed = False
    for unit in battle.get('units', {}).values():
        if unit.get('team') != 'enemy':
            continue
        # Older in-progress saves keep enemies already presented to the player visible.
        unit.setdefault('spotted', bool(battle.get('action_count', 0)) or (unit['x'],unit['y']) not in covers)
        if unseen(unit) and ((unit['x'],unit['y']) not in covers
                or (unit['x'],unit['y']) in observed
                or not unit.get('alive') or not unit.get('conscious', True)):
            changed = reveal(battle, unit) or changed
    return changed
