"""Saved arrival lighting; presentation only, independent of combat turns."""
from time import time

PHASES = {'day': (0, 28), 'dusk': (28, 30), 'night': (30, 58), 'dawn': (58, 60)}


def phase_at(minute):
    return next(phase for phase, (start, end) in PHASES.items() if start <= minute < end)


def initialize(battle, now=None):
    if (battle.get('lighting') or {}).get('version') == 1:
        return
    now = time() if now is None else now
    minute = (now / 60) % 60
    # Optional authored phase override. Never infer night from mission names.
    override = battle.get('lighting_phase')
    phase = override if override in PHASES else phase_at(minute)
    if override in PHASES:
        start, end = PHASES[phase]
        minute = (start + end) / 2
    battle['lighting'] = {'version': 1, 'arrived_at': now, 'arrival_minute': minute,
                         'phase': phase, 'mode': 'phase_locked'}


def presentation(battle, now=None):
    # Migration for older saved battles: choose once, then retain that arrival.
    initialize(battle, now)
    return {**battle['lighting'], 'server_now': time() if now is None else now,
            'indoor_cells': indoor_cells(battle)}


def indoor_cells(battle):
    from .building_templates import BUILDINGS, footprint
    cells={tuple(cell) for cell in battle.get('lighting_indoor_cells',[])}
    for building in battle.get('building_templates',[]):
        template=BUILDINGS.get(building.get('id'),{})
        if not template.get('roofed') or not building.get('anchor'):continue
        ax,ay=building['anchor']
        rotation=building.get('rotation',0)
        local=footprint(template)
        width=max(x for x,y in local)+1;height=max(y for x,y in local)+1
        for x,y,w,h in template.get('yard',[]):
            width=max(width,x+w);height=max(height,y+h)
        for x,y in local:
            if rotation==90:x,y=height-1-y,x
            elif rotation==180:x,y=width-1-x,height-1-y
            elif rotation==270:x,y=y,width-1-x
            cells.add((x+ax,y+ay))
    return [list(cell) for cell in sorted(cells)]
