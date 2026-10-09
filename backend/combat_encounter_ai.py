"""Small authored encounter heuristics; use existing movement, attacks and personality."""
from copy import deepcopy
from . import combat_conditions as conditions
from .combat_feedback import record as feedback
from .relationships import personality_profile
from .wall_boundaries import crossed_walls


def active(u):
    return u.get('alive', True) and u.get('conscious', True) and not u.get('extracted') and not u.get('carried_by')


def weakness(u):
    return min(30, 5 * next((s.get('stacks', 1) for s in u.get('statuses', []) if s['id']=='rat_weakness'), 0))


def modify_damage(attacker, target, damage):
    # Environmental/status packets retain their owner's penalties only when they
    # carry actual owner status metadata; no HP-pool mutation or duplicate DoT.
    return damage * (1 - weakness(attacker)/100) * (1 + weakness(target)/100)


def bite(battle, attacker, target):
    if attacker.get('species_profile') != 'store_rat' or attacker.get('reaction_damage'):
        return
    status=next((s for s in target.get('statuses',[]) if s['id']=='rat_weakness'),None)
    if status is None:
        status={'id':'rat_weakness','stacks':0,'expiry':'target_end'}
        target.setdefault('statuses',[]).append(status)
    status['stacks']+=max(1,min(3,int(attacker.get('swarm_count',1))))
    status.update(turns=status['stacks'],source_id=attacker['id'],source_name=attacker['name'])
    from .combat_martial import try_unstoppable
    try_unstoppable(target)
    if conditions.has(target,'rat_weakness'):feedback(battle,target,'status',status_id='rat_weakness')


def adjacent(battle, a, b):
    return abs(a['x']-b['x'])+abs(a['y']-b['y'])==1 and not crossed_walls(battle,(a['x'],a['y']),(b['x'],b['y']))


def merge(battle, rat, other):
    """Consumes the acting rat's main action, never grants a second activation."""
    if rat is other or any(not active(u) or u.get('species_profile')!='store_rat' for u in (rat,other)):
        return False
    count=rat.get('swarm_count',1)+other.get('swarm_count',1)
    if count>3 or rat.get('team')!=other.get('team') or not adjacent(battle,rat,other):
        return False
    if any(conditions.has(u,sid) for u in (rat,other) for sid in conditions.CONTROL|{'bind'}):
        return False
    before=deepcopy(rat);donor=deepcopy(other)
    for key in ('hp','max_hp','attack','resolve','max_resolve'):
        if key in rat and key in other:rat[key]+=other[key]
    # Preserve negative/beneficial state; combining bodies is not a cleanse.
    for s in other.get('statuses',[]):
        old=next((q for q in rat.get('statuses',[]) if q['id']==s['id']),None)
        if old is None:rat.setdefault('statuses',[]).append(deepcopy(s))
        elif 'layers' in old and 'layers' in s:
            old['layers'].extend(deepcopy(s['layers']));old['stacks']=len(old['layers'])
        elif s['id']=='rat_weakness':old.update(stacks=old.get('stacks',1)+s.get('stacks',1),turns=old.get('stacks',1)+s.get('stacks',1))
        else:old['turns']=max(old.get('turns',0),s.get('turns',0))
    rat.update(swarm_count=count,name=f'Rat Swarm ×{count}',acted=True,
               portrait='/assets/animals-v1/rat_swarm.png')
    rat['statuses']=[s for s in rat.get('statuses',[]) if s['id']!='rat_swarm']+[{'id':'rat_swarm','stacks':count}]
    other.update(alive=False,conscious=False,extracted=True,condition='merged',merged_into=rat['id'])
    battle.setdefault('animation_events',[]).append({'type':'rat_merge','unit_id':other['id'],'target_id':rat['id'],
        'x':other['x'],'y':other['y'],'from':{'x':other['x'],'y':other['y']},'to':{'x':rat['x'],'y':rat['y']},
        'unit_snapshot':donor,'receiver_before':before,'receiver_after':deepcopy(rat)})
    feedback(battle,rat,'status',status_id='rat_swarm')
    battle['log'].append(f"The rats regroup into a {count}-rat swarm ({rat['hp']}/{rat['max_hp']} HP).")
    return True


def say(battle,unit,text,key):
    # One line per distinct tactical situation, at most once every three rounds.
    if key in unit.get('encounter_lines',[]) or battle.get('round',1)<unit.get('next_encounter_line_round',0):return
    unit.setdefault('encounter_lines',[]).append(key);unit['next_encounter_line_round']=battle.get('round',1)+3
    battle['log'].append(f"{unit['name']}: {text}")
    feedback(battle,unit,'dialogue',text=text)


def safe_cell(battle,unit,cell):
    from . import combat as c
    return not c._blocked(battle,*cell,unit['id'],unit.get('movement_type')) and not any(
        z.get('kind') in {'scorched','caltrops','fire_wall'} and any((p.get('x'),p.get('y'))==cell for p in z.get('cells',[]))
        for z in battle.get('zones',[]))


def strike(battle,unit,target):
    from . import combat as c
    if not active(unit) or unit.get('forced_skip') or unit.get('engineer_interrupted') or not c._can_attack(battle,unit,target) or not c.bard.can_attack(unit):
        c._guard(battle,unit);return
    c._perform_attack(battle,unit,target,unit.get('attack_elevation_rule','melee'))
    unit['acted']=True


def auto(battle,unit,targets,forced_target=None):
    from . import combat as c
    profile=unit.get('species_profile')
    bandit=unit.get('encounter_profile') in {'road_enforcer','road_cutpurse'}
    if profile not in {'store_rat','fence_wolf'} and not bandit or not targets:return False
    targets=[t for t in targets if active(t)]
    if not targets:return False
    hostiles={u['id'] for u in conditions.hostile_units(battle,unit,battle['units'].values())}
    allies=[u for u in battle['units'].values() if u['id']!=unit['id'] and u['id'] not in hostiles and u.get('team')==unit.get('team') and active(u)]
    behavior=personality_profile(unit)[2]
    if profile=='store_rat' and unit['hp']<unit['max_hp'] and unit.get('swarm_count',1)<3 and not forced_target and c._movement_limit(unit)>0 and not c.bard.locked(unit):
        partners=[a for a in allies if a.get('species_profile')==profile and a.get('swarm_count',1)+unit.get('swarm_count',1)<=3
                  and not any(conditions.has(a,sid) for sid in conditions.CONTROL|{'bind'})]
        if partners:
            partner=min(partners,key=lambda a:(c._distance(unit,a),a['id']))
            cells=[{'x':partner['x']+dx,'y':partner['y']+dy} for dx,dy in ((1,0),(-1,0),(0,1),(0,-1))
                   if safe_cell(battle,unit,(partner['x']+dx,partner['y']+dy))]
            before=(unit['x'],unit['y'])
            if cells:c._move_to_nearest_tile(battle,unit,cells)
            if active(unit) and merge(battle,unit,partner):return True
            if (unit['x'],unit['y'])!=before:
                c._guard(battle,unit);return True
    if bandit and not forced_target:
        healthy=[a for a in allies if a['hp']>=a['max_hp']*.5 and not a.get('forced_skip')]
        retreat_at=.35 if unit.get('personality_id') in {'reckless','berserker'} else .5
        if unit['hp']<unit['max_hp']*retreat_at and healthy and c._movement_limit(unit)>0 and not c.bard.locked(unit):
            costs,_=c._movement_tree(battle,unit)
            threat=lambda p:min(abs(p[0]-t['x'])+abs(p[1]-t['y']) for t in targets)
            origin=(unit['x'],unit['y'])
            choices=[p for p in costs if safe_cell(battle,unit,p) and min(abs(p[0]-a['x'])+abs(p[1]-a['y']) for a in healthy)<=2]
            if choices:
                dest=max(choices,key=lambda p:(threat(p),-costs[p]))
                if threat(dest)>threat(origin):
                    say(battle,unit,'Cover me. I need a way out!' if behavior=='survival' else 'Your turn. Keep them busy.','withdraw')
                    c._move_to_nearest_tile(battle,unit,[{'x':dest[0],'y':dest[1]}]);c._guard(battle,unit);return True
        if behavior=='guardian':
            wounded=[a for a in allies if a['hp']<a['max_hp']*.5]
            target=min(targets,key=lambda t:(min((c._distance(t,a) for a in wounded),default=c._distance(unit,t)),c._distance(unit,t)))
            if wounded:say(battle,unit,'Get behind me.','protect')
        elif unit.get('personality_id')=='opportunist':
            target=min(targets,key=lambda t:(t['hp']/max(1,t['max_hp']),c._distance(unit,t)))
        else:target=min(targets,key=lambda t:(c._distance(unit,t),t['hp']))
    elif forced_target:target=forced_target
    elif profile=='fence_wolf':
        key='wolf_pack_target:'+str(unit.get('team'))
        preferred=battle['units'].get(battle.get(key))
        target=preferred if preferred in targets else min(targets,key=lambda t:(sum(c._distance(a,t) for a in allies if a.get('species_profile')==profile)+c._distance(unit,t),t['hp']))
        battle[key]=target['id']
    else:target=min(targets,key=lambda t:(c._distance(unit,t),t['hp']))
    if bandit and c._distance(unit,target)<=3:
        say(battle,unit,{'guardian':'Watch the flanks. Stay behind me.','strategist':'Keep them where we want them.','opportunist':'That one looks easy.'}.get(unit.get('personality_id'),'Keep close.'),'engage')
    if bandit:
        if unit.get('job_id')=='ranger' and c.ranger.auto(battle,unit,targets):return True
        snare=next((s for s in unit.get('skills',[]) if s['id']=='npc:bandit:road_bola' and c.abilities.availability(unit,s)['available'] and c._can_attack(battle,unit,target,s['range'])),None)
        if snare and not conditions.has(target,'hobbled'):
            c._resolve_ability(battle,unit,target,snare);unit['acted']=True;return True
    if c._auto_open_gate(battle,unit,target):return 'finished'
    if int(unit.get('snared_until_round',0))>=int(battle.get('round',1)):
        strike(battle,unit,target);return True
    if profile=='fence_wolf' and not c.bard.locked(unit):
        costs,_=c._movement_tree(battle,unit)
        pack=[a for a in allies if a.get('species_profile')==profile and adjacent(battle,a,target)]
        cells=[(target['x']+dx,target['y']+dy) for dx,dy in ((1,0),(-1,0),(0,1),(0,-1))]
        legal=[p for p in cells if p in costs and safe_cell(battle,unit,p) and not crossed_walls(battle,p,(target['x'],target['y']))]
        if legal:
            def flank(p):return (sum(a['x']+p[0]==2*target['x'] and a['y']+p[1]==2*target['y'] for a in pack),-costs[p])
            dest=max(legal,key=flank);c._move_to_nearest_tile(battle,unit,[{'x':dest[0],'y':dest[1]}])
        elif not c._can_attack(battle,unit,target):c._move_toward(battle,unit,target)
    elif not c._can_attack(battle,unit,target):c._move_toward(battle,unit,target)
    if not active(unit) or unit.get('forced_skip') or unit.get('engineer_interrupted') or not c.bard.can_attack(unit):return True
    if bandit:
        snare=next((s for s in unit.get('skills',[]) if s['id']=='npc:bandit:road_bola' and c.abilities.availability(unit,s)['available'] and c._can_attack(battle,unit,target,s['range'])),None)
        if snare and not conditions.has(target,'hobbled'):
            say(battle,unit,'Hold still. This road is ours.','snare');c._resolve_ability(battle,unit,target,snare);unit['acted']=True;return True
        if unit.get('job_id')=='rogue' and c._auto_rogue_turn(battle,unit,[target]):
            # Rogue's helper owns finish_turn; signal that to the caller.
            return 'finished'
        technique=next((s for s in unit.get('skills',[]) if s['id']=='job:fighter:bash' and c.abilities.availability(unit,s)['available'] and c._can_attack(battle,unit,target,s['range'])),None)
        if technique:c._resolve_ability(battle,unit,target,technique);unit['acted']=True;return True
    strike(battle,unit,target)
    return True
