"""Small tactical helpers shared by command resolution and previews."""
from . import combat_conditions as conditions


def displacement_resistance(unit):
    base=unit.get('displacement_resistance',25 if unit.get('boss') or unit.get('kind')=='chieftain' else 0)
    if conditions.has(unit,'braced'):base+=50
    return max(0,min(100,int(base)))


def displacement_path(actor,target,distance,mode):
    dx,dy=target['x']-actor['x'],target['y']-actor['y']
    # Dominant cardinal direction; never route around a wall or another unit.
    if not dx and not dy:return []
    sx,sy=((1 if dx>0 else -1),0) if abs(dx)>=abs(dy) else (0,(1 if dy>0 else -1))
    if mode=='pull':sx,sy=-sx,-sy
    return [(target['x']+sx*n,target['y']+sy*n) for n in range(1,distance+1)]


def pit_at(battle,x,y):
    tile=next((t for t in battle.get('terrain',[]) if t.get('kind')=='pit' and not t.get('destroyed') and t['x']==x and t['y']==y),None)
    if tile:return tile
    return next((t for t in battle.get('void_tiles',[]) if t['x']==x and t['y']==y),None)


def pit_kind(tile):
    # Old untyped flight-only pits stay safe from speculative instant kills.
    return tile.get('pit_kind','shallow' if tile.get('kind')=='pit' else 'blocked')


def reaction_available(unit):
    return (unit.get('reaction_ready',True) and unit.get('alive',True) and unit.get('conscious',True)
        and not unit.get('extracted') and not unit.get('carried_by') and not unit.get('panicked')
        and not any(conditions.has(unit,s) for s in ('stun','sleep','ambush_sleep','freeze','paralyze','charm','berserk','pit_trapped')))
