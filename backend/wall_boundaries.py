"""Tile-edge walls separate spaces without occupying the interior floor.

Legacy structures without wall_edges continue to occupy their complete tile.
"""
SIDES = {'north': (0, -1), 'east': (1, 0), 'south': (0, 1), 'west': (-1, 0)}


def crossed_walls(battle, start, end, sight=False):
    """Return active edge structures crossed by a center-to-center segment.

    Inclusive segment ends stop diagonal shots slipping through a closed corner.
    An open or destroyed gate never leaves a hidden movement/sight boundary.
    """
    x0, y0 = start; x1, y1 = end
    dx, dy = x1-x0, y1-y0
    found = []
    adjacent = abs(dx)+abs(dy) == 1
    for wall in battle.get('terrain', []):
        edges=wall.get('wall_edges', [])
        active=wall.get('blocks_sight',wall.get('blocking',False)) if sight else wall.get('blocking',False)
        if not edges or wall.get('destroyed') or not active:
            continue
        if adjacent and (wall['x'],wall['y']) not in (start,end):
            continue
        for side in edges:
            sx, sy = SIDES[side]
            x, y = wall['x'], wall['y']
            if sx and dx:
                t = (x+sx*.5-x0)/dx
                hit = 0 < t < 1 and y-.5-1e-9 <= y0+t*dy <= y+.5+1e-9
            elif sy and dy:
                t = (y+sy*.5-y0)/dy
                hit = 0 < t < 1 and x-.5-1e-9 <= x0+t*dx <= x+.5+1e-9
            else:
                hit = False
            if hit:
                found.append(wall)
                break
    return found


def can_operate_gate(unit, gate):
    if 'wall_edges' not in gate:
        from .battle_maps import occupied_tiles
        return min(abs(unit['x']-x)+abs(unit['y']-y) for x,y in occupied_tiles(gate)) == 1
    cell = (unit['x'], unit['y'])
    if cell == (gate['x'], gate['y']):
        return True
    return any(cell == (gate['x']+dx, gate['y']+dy)
               for dx, dy in (SIDES[side] for side in gate['wall_edges']))


def gate_controls(gate):
    """Two small controls straddling the actual doorway, with approach cells.

    Coordinates use cell centers (like units), not CSS percentages. Edge doors
    use their physical boundary; older centered gates use the footprint edge.
    """
    x, y = int(gate['x']), int(gate['y'])
    if gate.get('edge_wall') and gate.get('wall_edges'):
        dx, dy = SIDES[gate['wall_edges'][0]]
        cx, cy = x + dx * .5, y + dy * .5
        cells = [(x, y), (x + dx, y + dy)]
    else:
        from .battle_maps import occupied_tiles
        cells_covered = occupied_tiles(gate)
        right = max(px for px, _ in cells_covered)
        bottom = max(py for _, py in cells_covered)
        cx, cy = (x + right) / 2, (y + bottom) / 2
        if int(gate.get('rotation', 0)) % 180:
            dx, dy = 1, 0
            cells = [(x - 1, int(cy)), (right + 1, int(cy))]
        else:
            dx, dy = 0, 1
            cells = [(int(cx), y - 1), (int(cx), bottom + 1)]
    return [{'x': cx + sign * dx * .23 - dy * .23,
             'y': cy + sign * dy * .23 + dx * .23,
             'approach': {'x': ax, 'y': ay}}
            for sign, (ax, ay) in zip((-1, 1), cells)]
