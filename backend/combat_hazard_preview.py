"""Read-only route warnings using the same zone eligibility and damage rules as combat."""
from copy import deepcopy
from . import combat_conditions as conditions, combat_dots as dots, combat_spaces as spaces


def forecast(battle, actor, path, active, damage_before_barrier, living):
    zones = [z for z in battle.get('zones', []) if z.get('kind') in spaces.ZONES and 'entry' in spaces.ZONES[z['kind']]['events']]
    mines=[h for h in battle.get('engineer_hazards',[]) if h['kind']=='mine' and (h.get('team')==actor.get('team') or h.get('revealed'))]
    from .combat_rogue import trap_expert
    mine_cells=[] if trap_expert(actor) else [p for p in path if any(max(abs((p['x'] if isinstance(p,dict) else p[0])-h['x']),abs((p['y'] if isinstance(p,dict) else p[1])-h['y']))<=1 for h in mines)]
    mine_warning={'damage':0,'effects':{'engineer_disruption':{'stacks':1,'chance':100}},'cells':mine_cells[:1],'uncertain':False,'lethal':False} if mine_cells else None
    if mine_cells:
        path = path[:path.index(mine_cells[0])+1]
    if not zones or not path:
        return mine_warning
    route_cells = {(p['x'], p['y']) if isinstance(p, dict) else tuple(p) for p in path}
    if not any((p['x'], p['y']) in route_cells for z in zones for p in z['cells']):
        return mine_warning
    probe = deepcopy(actor)
    preview_battle = {**battle, 'zones': zones, 'animation_events': [], 'log': []}
    effects, cells = {}, []
    total = 0
    uncertain = False

    def damage(owner, target, amount, name, sid=None):
        nonlocal total
        source = {'id': owner.get('id'), 'attack': amount, 'weapon': name,
                  'status_tick': True, 'damage_kind': sid or 'thorns'}
        if name==spaces.ZONES['fire_wall']['name']:source.update(damage_kind='fire',element='fire')
        if sid:
            source['percent_dot'] = sid
        raw = damage_before_barrier(preview_battle, source, target, armor_pierce=target.get('armor', 0))
        dealt, _ = conditions.absorb(target, raw)
        total += dealt
        target['hp'] -= dealt

    def apply(owner, target, sid, stacking=False):
        nonlocal uncertain
        chance = conditions.status_chance(target, sid)
        if chance <= 0:
            return
        count = (2 if owner['scorched_source'].get('burn_debuffer') else 1) if owner.get('scorched_source') else 1
        # Uncertain applications are shown as an upper bound, never as guaranteed rolls.
        applied = False
        for _ in range(count):
            applied = (conditions.add_stack(target, sid, 2, owner) if stacking or sid in dots.PERCENT
                       else conditions.apply(target, sid, 1, owner)) or applied
        if not applied:
            return
        entry = effects.setdefault(sid, {'stacks': 0, 'chance': chance})
        entry['stacks'] += count
        uncertain |= chance < 100
        if sid == 'burn':
            status = next((s for s in target['statuses'] if s['id'] == 'burn'), None)
            if not status:
                return
            damage(owner, target, dots.base_damage(target, sid, dots.count(status)), 'Burn', sid)

    for point in path:
        x, y = (point['x'], point['y']) if isinstance(point, dict) else point
        if probe.get('zone_location') == [x, y]:
            continue
        probe.update(x=x, y=y, zone_location=[x, y])
        before = (total, deepcopy(effects))
        spaces.trigger_zones(preview_battle, probe, 'entry', active,
                             lambda target, owner: target['id'] in {u['id'] for u in conditions.hostile_units(battle, owner, living(battle))},
                             apply, damage)
        if before != (total, effects):
            cells.append({'x': x, 'y': y})
        if not active(probe):
            break
    if mine_warning:
        effects.update(mine_warning['effects']);cells+=mine_warning['cells']
    if not total and not effects:
        return None
    return {'damage': total, 'effects': effects, 'cells': cells,
            'uncertain': uncertain, 'lethal': total >= actor['hp']}
