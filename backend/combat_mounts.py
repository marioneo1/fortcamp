"""Real animal mounts: one body, separate health, no extra mounted activation."""
from copy import deepcopy
from math import ceil
import random
from . import recruit_perks, combat_conditions as conditions
from .combat_feedback import record as feedback

FALL_DESCRIPTION = 'Mount lost: 25% chance of half its max HP in damage + Stun, 50% chance of quarter + Hobble, or 25% chance of a clean landing.'


def fall_outcome(battle, rider, animal):
    """One saved, deterministic roll per lost mount; previews never roll."""
    counter=battle.get('mount_fall_counter',0)
    battle['mount_fall_counter']=counter+1
    roll=random.Random(f"{battle.get('seed')}:mount-fall:{rider['id']}:{animal['id']}:{counter}").randrange(100)
    return 'hard' if roll<25 else 'rough' if roll<75 else 'safe'


def active(unit):
    return bool(unit and unit.get('alive') and unit.get('conscious', True)
                and not unit.get('extracted') and not unit.get('carried_by'))


def mount(battle, rider):
    animal = battle['units'].get(rider.get('animal_mount_id'))
    return animal if active(animal) and animal.get('rider_id') == rider.get('id') else None


def linked(battle, first, second):
    a, b = battle['units'].get(first, {}), battle['units'].get(second, {})
    return bool(a and b and (a.get('animal_mount_id') == second and b.get('rider_id') == first
                            or b.get('animal_mount_id') == first and a.get('rider_id') == second))


def skill(unit):
    riding = bool(unit.get('animal_mount_id'))
    return {'id': 'innate:rider:mount', 'name': 'Dismount' if riding else 'Mount',
            'description': 'Step onto a free adjacent tile.' if riding else 'Ride an adjacent allied mount for its movement, protection and special technique.',
            'ability_version': 1, 'source_kind': 'innate', 'source_name': 'Rider perk',
            'type': 'active', 'target': 'ally', 'self_only': riding, 'range': 1,
            'elevation_rule': 'melee', 'quick_action': True, 'mount_kind': 'mount',
            'cost': {'cooldown': 0, 'charges': None}, 'effects': []}


def ensure_skill(unit):
    if not recruit_perks.has(unit, 'rider'):
        return
    entry = skill(unit)
    rows = unit.setdefault('skills', [])
    existing = next((s for s in rows if s.get('mount_kind')=='mount'), None)
    if existing is not None:
        existing.update(entry)
    else:
        rows.append(entry)
    if (unit.get('special') or {}).get('mount_kind')=='mount':
        unit['special'] = entry
    rows[:] = [s for s in rows if s.get('mount_kind') != 'boar_charge']
    if unit.get('animal_mount_id') and unit.get('animal_mount_species') == 'boar':
        rows.append(charge_skill())


def charge_skill():
    return {'id':'innate:rider:boar_charge','name':'Boar Charge',
            'description':'Charge an enemy in a clear straight line for 1.25–2× attack damage; a four-cell hit also attempts a one-turn Stun.',
            'ability_version':1,'source_kind':'character','source_name':'Boar mount',
            'type':'active','target':'enemy','range':4,'elevation_rule':'melee',
            'mount_kind':'boar_charge','cost':{'cooldown':3,'charges':None},
            'effects':[{'type':'attack','power_percent':125}]}


def charge_route(battle, rider, target):
    from . import combat as c
    animal=mount(battle,rider)
    if not animal or not animal.get('boar_mount') or not active(target) or target['team']==rider['team']:
        return None
    dx,dy=target['x']-rider['x'],target['y']-rider['y']
    distance=abs(dx)+abs(dy)
    if dx and dy or not 1<=distance<=4 or c._movement_limit(rider)==0:
        return None
    sx,sy=(dx>0)-(dx<0),(dy>0)-(dy<0)
    path=[];x,y=rider['x'],rider['y']
    for _ in range(distance-1):
        nx,ny=x+sx,y+sy
        if c._blocked(battle,nx,ny,rider['id']) or not c._can_step(battle,x,y,nx,ny,rider):return None
        path.append((nx,ny));x,y=nx,ny
    if not c._can_attack(battle,{**rider,'x':x,'y':y},target,1):return None
    return path,distance


def charge(battle, rider, target, choice):
    from . import combat as c
    from . import combat_abilities as abilities
    available=abilities.availability(rider,choice)
    route=charge_route(battle,rider,target)
    if not available['available']:raise ValueError(available['reason'])
    if route is None:raise ValueError('Choose an enemy one to four cells away in a clear straight line')
    path,distance=route
    attack={**choice,'range':1,'effects':[{'type':'attack','power_percent':100+25*distance}]}
    attack.pop('mount_kind',None)
    if distance==4:
        attack['effects'].append({'type':'status','status':'stun','turns':1,'chance':100,'conditions':[{'type':'hit'}]})
    c._commit_player_movement(battle,rider)
    for x,y in path:
        start=(rider['x'],rider['y']);rider.update(x=x,y=y,moved=True)
        c._record_movement(battle,rider,start,[(x,y)])
        c._apply_tile_entry(battle,rider)
        if not active(rider) or not mount(battle,rider) or c._movement_limit(rider)==0 or rider.get('engineer_interrupted') or rider.get('mount_interrupted'):
            abilities.spend(rider,attack);rider['acted']=True
            return {'interrupted':True}
    result=c._resolve_ability(battle,rider,target,attack)
    return result


def restriction(unit, choice):
    if choice.get('mount_kind')=='boar_charge':
        return None if unit.get('animal_mount_id') and unit.get('animal_mount_species')=='boar' else 'Requires a boar mount'
    if unit.get('animal_mount_id') and (choice.get('engineer_kind')=='man_the_guns'
            or choice.get('druid_kind') in {'prowler','bulwark','rat','humanoid'}):
        return 'Dismount before entering another form or emplacement'
    if not choice.get('mount_kind'):
        return None
    if unit.get('mount_changed_activation') == unit.get('ability_activation', 0):
        return 'You already mounted or dismounted this activation'
    if unit.get('mounted_machine') or unit.get('carrying') or unit.get('carrying_object') or unit.get('druid_form'):
        return 'Leave your current form, emplacement or carried load first'
    if conditions.has(unit, 'bind') or conditions.has(unit, 'freeze') or unit.get('captor_hold') or unit.get('captor_held_by'):
        return 'Cannot mount or dismount while restrained'
    return None


def legal(battle, rider, animal):
    from .combat import crossed_walls
    return bool(active(rider) and active(animal) and animal.get('mountable')
                and animal.get('team') == rider.get('team') and not animal.get('rider_id')
                and not rider.get('animal_mount_id') and recruit_perks.has(rider, 'rider')
                and abs(rider['x']-animal['x']) + abs(rider['y']-animal['y']) == 1
                and not crossed_walls(battle,(rider['x'],rider['y']),(animal['x'],animal['y']))
                and not conditions.has(animal, 'freeze') and not conditions.has(animal, 'bind'))


def exits(battle, rider):
    from . import combat as c
    return [{'x': rider['x']+dx, 'y': rider['y']+dy} for dx,dy in ((0,-1),(1,0),(0,1),(-1,0))
            if not c._blocked(battle,rider['x']+dx,rider['y']+dy,rider['id'])
            and c._can_step(battle,rider['x'],rider['y'],rider['x']+dx,rider['y']+dy,rider)]


def board(battle, rider, animal, initial=False):
    from . import combat as c
    if not initial and not legal(battle,rider,animal):
        raise ValueError('Choose an adjacent, unoccupied allied mount')
    start = (rider['x'],rider['y'])
    rider['mount_original_movement_type']=rider.get('movement_type','walk')
    rider.update(animal_mount_id=animal['id'], mount_movement_bonus=1, movement_type=animal.get('movement_type','walk'))
    animal['rider_id'] = rider['id']
    rider['animal_mount_species']='boar' if animal.get('boar_mount') else animal.get('species_profile')
    rider.update(x=animal['x'],y=animal['y'])
    if not initial:
        c._record_movement(battle,rider,start,[(rider['x'],rider['y'])])
        battle['animation_events'][-1]['mount_boarding']=True
        battle['animation_events'][-1].pop('mount_partner_id',None)
        c._apply_tile_entry(battle,rider)
        animal['status_activation']=deepcopy(rider.get('status_activation'))
        rider['mount_changed_activation'] = rider.get('ability_activation',0)
        battle['log'].append(f"{rider['name']} mounts {animal['name']}.")
    ensure_skill(rider)


def dismount(battle, rider):
    from . import combat as c
    animal = mount(battle,rider)
    options = exits(battle,rider)
    if not animal or not options:
        raise ValueError('No free adjacent tile to dismount onto')
    start = (rider['x'],rider['y'])
    unlink(rider,animal)
    rider.update(options[0])
    rider['mount_changed_activation'] = rider.get('ability_activation',0)
    c._record_movement(battle,rider,start,[(rider['x'],rider['y'])])
    c._apply_tile_entry(battle,rider)
    battle['log'].append(f"{rider['name']} dismounts.")


def unlink(rider, animal):
    rider.pop('animal_mount_id',None)
    rider.pop('animal_mount_species',None)
    rider.pop('mount_movement_bonus',None)
    animal.pop('rider_id',None)
    rider.pop('mount_disabled',None)
    rider['movement_type']=rider.pop('mount_original_movement_type',rider.get('movement_type','walk'))
    ensure_skill(rider)


def command(battle, rider, choice, request):
    from .combat_abilities import availability
    if not availability(rider,choice)['available']:
        raise ValueError(availability(rider,choice)['reason'])
    if choice.get('mount_kind')=='boar_charge':
        return charge(battle,rider,battle['units'].get(request.get('target_id'),{}),choice)
    if rider.get('animal_mount_id'):
        if request.get('target_id') != rider['id']:
            raise ValueError('Target yourself to dismount')
        dismount(battle,rider)
    else:
        board(battle,rider,battle['units'].get(request.get('target_id'),{}))
    rider['quick_actions_used'] = rider.get('quick_actions_used',0)+1


def previews(battle, rider, choice):
    from .combat_abilities import availability
    if not availability(rider,choice)['available']:
        return {}
    if choice.get('mount_kind')=='boar_charge':
        from . import combat as c
        entries={}
        for target in battle['units'].values():
            route=charge_route(battle,rider,target)
            if route is None:continue
            path,distance=route
            x,y=path[-1] if path else (rider['x'],rider['y'])
            attack={**choice,'range':1,'effects':[{'type':'attack','power_percent':100+25*distance}]}
            row=c._strike_preview(battle,{**rider,'x':x,'y':y},target,'melee',1,attack)
            row.update(charge_distance=distance,charge_power=100+25*distance,
                       stun_chance=conditions.status_chance(target,'stun') if distance==4 else 0)
            entries[target['id']]=row
        return entries
    if mount(battle,rider):
        options = exits(battle,rider)
        return {rider['id']: {'support':True,'chance':100,'damage_on_hit':0,'mount_exit':options[0]}} if options else {}
    return {u['id']: {'support':True,'chance':100,'damage_on_hit':0} for u in battle['units'].values() if legal(battle,rider,u)}


def incoming(unit, damage):
    return damage*.75 if unit.get('animal_mount_id') or unit.get('rider_id') else damage


def sync(battle, unit):
    """Coordinates always move together, including forced displacement."""
    other = battle['units'].get(unit.get('animal_mount_id') or unit.get('rider_id'))
    if other and active(other):
        other.update(x=unit['x'],y=unit['y'])


def face(battle, unit, origin, destination):
    """Persist only this pair's own deliberate movement/attack facing."""
    animal=unit if unit.get('boar_mount') else mount(battle,unit)
    if not animal:return
    dx,dy=destination['x']-origin['x'],destination['y']-origin['y']
    if not dx and not dy:return
    animal['mount_facing']=('s' if dy>0 else 'n') if abs(dy)>abs(dx) else ('e' if dx>0 else 'w')
    if abs(dx)==abs(dy):animal['mount_facing']=('s' if dy>0 else 'n')+('e' if dx>0 else 'w')


def entry(battle, unit):
    from . import combat as c
    other = battle['units'].get(unit.get('animal_mount_id') or unit.get('rider_id'))
    if other and active(other) and not battle.get('_mount_entry_resolving'):
        sync(battle,unit)
        movement=next((e for e in reversed(battle.get('animation_events',[])) if e.get('type')=='movement' and e.get('unit_id')==unit['id']),None)
        if movement and not movement.get('mount_boarding') and movement.get('points',[])[-1:]==[{'x':unit['x'],'y':unit['y']}]:
            movement['mount_partner_id']=other['id']
        battle['_mount_entry_resolving']=True
        try:
            c._apply_tile_entry(battle,other)
        finally:
            battle.pop('_mount_entry_resolving',None)


def start(battle, rider, stamp):
    animal = mount(battle,rider)
    if animal and animal.get('status_activation') != list(stamp):
        animal['status_activation'] = list(stamp)
        animal['ability_activation'] = animal.get('ability_activation',0)+1
        conditions.start_activation(battle,animal)
        rider['mount_disabled'] = bool(animal.get('forced_skip') or animal.get('paralyzed_move') or conditions.has(animal,'bind'))


def finish(battle, rider):
    from . import combat as c
    animal = mount(battle,rider)
    if animal:
        c._tick_gear_statuses(battle,animal)
        conditions.finish_activation(animal)


def defeat(battle, unit):
    """Called only after the actual damage/death event, never during previews."""
    from . import combat as c
    if active(unit):
        return
    if unit.get('animal_mount_id'):
        animal = battle['units'].get(unit['animal_mount_id'])
        if animal:
            battle.setdefault('animation_events',[]).append({'type':'mount_release','unit_id':animal['id'],
                'x':animal['x'],'y':animal['y'],'unit_snapshot':deepcopy(animal)})
            unlink(unit,animal)
            relocate_released(battle,animal,unit)
    elif unit.get('rider_id'):
        unit['mounted_death'] = True
        rider = battle['units'].get(unit['rider_id'])
        if not rider:
            unit.pop('rider_id',None)
            return
        before = deepcopy(rider)
        unlink(rider,unit)
        outcome=fall_outcome(battle,rider,unit)
        battle.setdefault('animation_events',[]).append({'type':'mount_fall','unit_id':rider['id'],
            'mount_id':unit['id'],'x':rider['x'],'y':rider['y'],'unit_snapshot':before,'outcome':outcome})
        if active(rider):
            amount = max(1,ceil(unit['max_hp']*(.5 if outcome=='hard' else .25))) if outcome!='safe' else 0
            source = {'id':unit['id'],'name':unit['name'],'weapon':'a mount fall','status_tick':True,'damage_kind':'fall'}
            dealt=c._deal_damage(battle,source,rider,resolved_damage=amount) if amount else 0
            if active(rider) and outcome=='hard':
                # Losing a mount is a physical fall, not a resistible spell proc.
                conditions.remove(rider,'stun')
                rider.setdefault('statuses',[]).append({'id':'stun','turns':1,'source_id':unit['id'],'applied_activation':deepcopy(rider.get('status_activation'))})
                feedback(battle,rider,'status',status_id='stun')
                order=battle.get('turn_order',[]);index=battle.get('turn_index',0)
                if index<len(order) and order[index]==rider['id']:
                    rider.update(mount_interrupted=True,forced_skip=True)
            elif active(rider) and outcome=='rough':
                conditions.add_stack(rider,'hobbled',1,unit)
                feedback(battle,rider,'status',status_id='hobbled')
            text=f'{dealt} damage and one-turn Stun' if outcome=='hard' else f'{dealt} damage and one-turn Hobble' if outcome=='rough' else 'a clean landing, unharmed'
            battle['log'].append(f"{rider['name']} loses the boar: {text}.")


def relocate_released(battle, animal, rider):
    """A living released animal cannot share its rider's captured/corpse tile."""
    from . import combat as c
    for point in exits(battle,animal):
        start=(animal['x'],animal['y']);animal.update(point)
        c._record_movement(battle,animal,start,[(animal['x'],animal['y'])]);c._apply_tile_entry(battle,animal)
        break


def auto(battle, rider):
    if rider.get('animal_mount_id') or not recruit_perks.has(rider,'rider') or restriction(rider,skill(rider)):
        return
    animal = next((u for u in battle['units'].values() if legal(battle,rider,u)),None)
    if animal:
        board(battle,rider,animal)


def cleanup(battle):
    for rider in list(battle['units'].values()):
        if not rider.get('animal_mount_id') or not rider.get('extracted'):
            continue
        animal=battle['units'].get(rider['animal_mount_id'])
        if animal:
            animal.update(extracted=True,fled=rider.get('fled',False))
            unlink(rider,animal)


def setup(battle):
    if battle.get('encounter_id') != 'contract:goblin_boar_riders':
        return
    from . import combat as c
    riders = [u for u in battle['units'].values() if u.get('team')=='enemy']
    for index,rider in enumerate(riders):
        uid = rider['id']+':boar'
        hp = 12 if battle.get('map_variation')==4 else 16
        boar = {'id':uid,'name':'Saddled Boar','team':rider['team'],'kind':'beast','race':'Beast',
                'portrait':'/assets/animals-v1/boar.png','creature':True,'species_profile':'saddle_boar',
                'mountable':True,'boar_mount':True,'x':rider['x'],'y':rider['y'],
                'hp':hp,'max_hp':hp,'attack':3,'armor':0,'move':4,'initiative':rider['initiative']-1,
                'strength':4,'agility':4,'intelligence':1,'evasion':0,'weapon':'Tusks','weapon_type':'unarmed',
                'attack_range':1,'attack_elevation_rule':'melee','melee_style':'bite',
                'alive':True,'conscious':True,'condition':'active','statuses':[],'status_version':1,
                'skills':[],'passives':[],'moved':False,'acted':False,'guarding':False,'special':None,
                'weight':5,'capture_immune':True,'adventurer_rank':'D'}
        battle['units'][uid] = boar
        # The fourth layout mixes already-mounted riders and nearby fresh mounts.
        if battle.get('map_variation')==4 and index>=2:
            options = exits(battle,boar)
            if options:
                boar.update(options[0])
            else:
                board(battle,rider,boar,initial=True)
        else:
            board(battle,rider,boar,initial=True)
        battle['turn_order'].append(uid)
    battle['turn_order'].sort(key=lambda uid:battle['units'][uid]['initiative'],reverse=True)
