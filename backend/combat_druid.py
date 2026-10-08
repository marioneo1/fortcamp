"""Adaptive forms and grouped living terrain using the existing combat clocks."""
from copy import deepcopy
import random
from . import combat_conditions as conditions
from .combat_feedback import record as feedback

FORMS={'prowler','bulwark','rat'}
SPELLS={'rejuvenation','bramble_wall','living_armor'}

def has(unit,key):
    return any(p.get('id')=='job:druid:'+key for p in unit.get('passives',[]))

def form(unit):return unit.get('form',{}).get('id')

def roll(battle,actor,key):
    serial=battle.get('druid_roll',0);battle['druid_roll']=serial+1
    return random.Random(f"{battle.get('seed')}:druid:{actor['id']}:{key}:{serial}").randint(1,100)

def visual(battle,unit,kind,sound,position=None):
    from . import combat as c
    battle['attack_serial']=battle.get('attack_serial',0)+1
    packet=battle['attack_serial']
    c.martial.effect(battle,unit,kind,packet=packet)
    battle['animation_events'][-1]['attack_event']=True
    if position:battle['animation_events'][-1].update(x=position['x'],y=position['y'])
    c._record_sound(battle,sound)
    battle['animation_events'][-1]['attack_packet']=packet
    return packet

def restriction(unit,skill):
    kind=skill.get('druid_kind')
    if kind in SPELLS and form(unit):return 'Return to humanoid form to cast nature spells'
    if kind in FORMS:
        if unit.get('druid_changed_at')==unit.get('ability_activation',0):return 'Only one form change per activation'
        if unit.get('capture_weapon') or unit.get('carrying') or unit.get('carrying_object'):return 'Put down the payload and unequip capture tools before changing form'
    return None

def start(battle,unit):
    unit.pop('druid_move_remaining',None);unit.pop('druid_move_spent',None)
    for status in list(unit.get('statuses',[])):
        if status['id'] not in {'druid_rejuvenation','living_armor'}:continue
        from .combat_cleric import heal
        heal(battle,unit,max(1,round(unit['max_hp']*status['heal_percent']/100)),status.get('name','Nature regeneration'))
        status['ticks']-=1
        if status['ticks']<=0 and status['id']!='living_armor':conditions.remove(unit,status['id'])
    for tile in battle.get('terrain',[]):
        if tile.get('druid_owner')==unit['id'] and not tile.get('destroyed') and tile.get('expires_at',0)<=unit.get('ability_activation',0):
            wither(battle,tile)

def change(battle,actor,kind):
    from . import combat as c
    spent=actor.get('druid_move_spent',0)+(actor.get('movement_path') or [{}])[-1].get('cost',0)
    c._commit_player_movement(battle,actor)
    if not c._combat_active(actor):return
    destination='normal' if form(actor)==kind else kind
    c.spaces.change_form(actor,{'form':destination,'turns':3})
    if destination!='normal':
        original=actor['form']['original']
        actor['form'].update(persistent=True)
        actor.update(attack=1 if destination=='rat' else max(original.get('attack',1),actor.get('intelligence',4)),
                     melee_style={'prowler':'slash','bulwark':'blunt','rat':'stab'}[destination],
                     armor=original.get('armor',0),displacement_resistance=original.get('displacement_resistance',0),
                     move=1 if destination=='bulwark' else original.get('move',3)+(2 if destination=='prowler' else 1))
        if destination=='rat':actor['evasion']=90
    actor['druid_changed_at']=actor.get('ability_activation',0)
    actor['druid_move_spent']=spent
    actor.pop('druid_move_remaining',None)
    actor['druid_move_remaining']=max(0,c._movement_limit(actor)-spent)
    actor['movement_origin']={'x':actor['x'],'y':actor['y']}
    actor['movement_path']=[]
    packet=visual(battle,actor,'druid_'+destination,'druid_growth' if destination=='normal' else 'druid_'+destination)
    feedback(battle,actor,'form',attack_packet=packet)
    battle['log'].append(f"{actor['name']} takes {destination if destination!='normal' else 'humanoid'} form. One form change used this turn.")

def outgoing(actor,amount):
    kind=form(actor)
    if actor.get('status_tick') or actor.get('druid_wall_attack'):return amount
    factor=(1.25 if has(actor,'wild_instinct') else 1.2) if kind=='prowler' else (1.5 if has(actor,'wild_instinct') else 1.25) if kind=='bulwark' else 1
    return max(1,round(amount*factor)) if amount else amount

def incoming(target,source,amount):
    if not amount:return amount
    if conditions.has(target,'living_armor'):amount=max(1,round(amount*.75))
    if form(target)=='prowler':amount=max(1,round(amount*1.2))
    elif form(target)=='bulwark' and not source.get('status_tick'):amount=max(1,round(amount*.75))
    return amount

def is_area(skill):
    return bool(skill and (skill.get('mage_kind') in {'fireball','meteor','flash_freeze','singularity','typhoon'} or
                   skill.get('cleric_kind')=='holy_light' or any(e['type'] in {'area_attack','leap_attack','dash_attack'} for e in skill.get('effects',[])))
                   )

def accuracy(target,skill,guaranteed,chance):
    if form(target)!='rat' or guaranteed or is_area(skill):return chance
    return 10

def landed(battle,actor,target,packet,damage=0):
    from . import combat as c
    kind=form(actor)
    if not c._combat_active(target) and kind!='bulwark':return
    if kind=='prowler':
        status=next((s for s in target.get('statuses',[]) if s['id']=='bleed'),None)
        count=c.conditions.dots.count(status) if status else 0
        first=has(actor,'wild_instinct') and target['id'] not in actor.setdefault('druid_opened',[])
        # With existing Bleed, doubling replaces the ordinary initial stack.
        additions=count if count else 1
        if first:additions+=1;actor['druid_opened'].append(target['id'])
        for _ in range(additions):conditions.add_stack(target,'bleed',1,actor)
        feedback(battle,target,'status',status_id='bleed',attack_packet=packet)
    elif kind=='bulwark' and roll(battle,actor,'bulwark') <= (85 if has(actor,'wild_instinct') else 75):
        c._apply_displacement(battle,actor,target,{'mode':'push','distance':1,'collision_damage':0},original_damage=damage,attack_packet=packet)
    elif kind=='rat' and has(actor,'wild_instinct') and roll(battle,actor,'rat')<=75:
        conditions.apply(target,'pestilence',2,actor)
        feedback(battle,target,'status',status_id='pestilence',attack_packet=packet)

def retaliate(battle,source,target):
    from . import combat as c
    if source.get('status_tick') or source.get('cleric_component') or source.get('druid_wall_attack'):return
    armor=next((s for s in target.get('statuses',[]) if s['id']=='living_armor' and s.get('retaliation')),None)
    attacker=battle.get('units',{}).get(source.get('id'))
    if armor and attacker and attacker['team']!=target['team'] and c._combat_active(attacker):
        # All hits in one authored technique share its resolver-owned budget.
        stamp=f"{source.get('ability_activation',0)}:{battle.get('action_count',0)}"
        key=f"{attacker['id']}:{target['id']}"
        if battle.get('druid_retaliation_stamp')!=stamp:
            battle['druid_retaliation_stamp']=stamp
            battle['druid_retaliations']=[]
        if key not in battle.setdefault('druid_retaliations',[]):
            battle['druid_retaliations'].append(key)
            conditions.add_stack(attacker,'bleed',1,{'id':armor['source_id'],'name':armor.get('source_name','Living Armor')})
            feedback(battle,attacker,'status',status_id='bleed')

def strip(battle,actor,x,y,rotation):
    from . import combat as c
    if type(x) is not int or type(y) is not int or rotation not in (0,1):return []
    cells=[{'x':x+(i if rotation==0 else 0),'y':y+(i if rotation==1 else 0)} for i in (-1,0,1)]
    for p in cells:
        if c._blocked(battle,p['x'],p['y'],None,actor.get('movement_type')) or c.tactics.pit_at(battle,p['x'],p['y']):return []
        if c._distance(actor,p)>3 or not c._line_of_sight(battle,actor,p):return []
        if c._ground_at(battle,p['x'],p['y'])[0]=='water':return []
    return cells

def wall(battle,actor,cells,rotation):
    serial=battle.get('druid_wall_serial',0)+1;battle['druid_wall_serial']=serial
    group=f'bramble_{serial}';strong=has(actor,'natures_persistence')
    hp=max(1,round(actor['max_hp']*(.5 if strong else .2)))
    for i,p in enumerate(cells):
        battle.setdefault('terrain',[]).append({**p,'id':group+'_'+str(i),'name':'Bramble Wall','kind':'bramble_wall',
            'bramble_group':group,'druid_owner':actor['id'],'team':actor['team'],'hp':hp,'max_hp':hp,'armor':0,
            'blocking':True,'blocks_sight':False,'destructible':True,'sprite':'druid_bramble','destroyed_sprite':'druid_bramble_broken',
            'expires_at':actor.get('ability_activation',0)+4,'lash_damage':max(1,round(actor['attack']*(.5 if strong else .2))),
            'retaliation':strong,'rotation':rotation*90,'movement_cost':1})
    visual(battle,actor,'druid_growth','druid_growth',cells[1])

def damage_wall(battle,tile,actor,packet):
    from . import combat as c
    segments=[t for t in battle['terrain'] if t.get('bramble_group')==tile['bramble_group']]
    for segment in segments:
        segment.update(hp=tile['hp'],destroyed=tile['hp']<=0,blocking=tile['hp']>0,
                       kind='bramble_wall' if tile['hp']>0 else 'rubble')
        if tile['hp']<=0:wither(battle,segment)
    if tile.get('retaliation') and actor['team']!=tile['team'] and c._combat_active(actor):
        conditions.add_stack(actor,'bleed',1,battle['units'].get(tile['druid_owner'],actor))
        feedback(battle,actor,'status',status_id='bleed',attack_packet=packet)

def adjacent_reactions(battle,unit,event):
    """One lash per wall per settled movement event, never on a render/poll."""
    from . import combat as c
    if not c._combat_active(unit):return
    groups={t['bramble_group']:t for t in battle.get('terrain',[]) if t.get('bramble_group') and not t.get('destroyed')
            and t['team']!=unit['team'] and abs(t['x']-unit['x'])+abs(t['y']-unit['y'])==1 and c._line_of_sight(battle,t,unit)}
    for tile in groups.values():
        stamp=f"{unit['id']}:{event}"
        stamps=battle.setdefault('bramble_reactions',{})
        if stamps.get(tile['bramble_group'])==stamp:continue
        stamps[tile['bramble_group']]=stamp
        owner=battle['units'].get(tile['druid_owner'])
        if not owner or not c._combat_active(owner):continue
        source={**owner,'attack':tile['lash_damage'],'form':{},'attack_elevation_rule':'melee','element':None,
                'gear_rules':{},'perk_modifiers':{},'on_hit':None,'druid_wall_attack':True}
        battle['attack_serial']=battle.get('attack_serial',0)+1;packet=battle['attack_serial']
        battle.setdefault('animation_events',[]).append({'type':'druid_lash','attack_packet':packet,'attack_event':True,
            'from':{'x':tile['x'],'y':tile['y']},'to':{'x':unit['x'],'y':unit['y']},'terrain_id':tile['id'],'target_id':unit['id'],'attacker_id':owner['id']})
        begin=len(battle['animation_events'])
        c._deal_damage(battle,source,unit)
        for e in battle['animation_events'][begin:]:e['attack_packet']=packet
        if c._combat_active(unit) and roll(battle,owner,'bramble')<=conditions.status_chance(unit,'bind',50):
            applied=conditions.apply(unit,'bind',1,owner)
            feedback(battle,unit,'status' if applied else 'resisted',status_id='bind',attack_packet=packet)
        c._record_sound(battle,'druid_vine_lash',offset=220);battle['animation_events'][-1]['attack_packet']=packet
        if not c._combat_active(unit):break

def execute(battle,actor,target,skill,rotation=0):
    from . import combat as c
    kind=skill['druid_kind']
    if kind in FORMS:
        c.abilities.spend(actor,skill)
        change(battle,actor,kind)
        return
    cells=strip(battle,actor,target['x'],target['y'],rotation) if kind=='bramble_wall' else None
    if kind=='bramble_wall' and not cells:raise ValueError('Choose three empty ground tiles within reach')
    c._commit_player_movement(battle,actor)
    if not c._combat_active(actor):return
    if kind=='bramble_wall':wall(battle,actor,cells,rotation)
    else:
        strong=has(actor,'natures_persistence') and kind=='living_armor'
        sid='druid_rejuvenation' if kind=='rejuvenation' else 'living_armor'
        conditions.remove(target,sid)
        target.setdefault('statuses',[]).append({'id':sid,'source_id':actor['id'],'source_name':actor['name'],
            'ticks':4 if strong else 3,'heal_percent':10 if kind=='rejuvenation' else 7 if strong else 5,
            'retaliation':strong,'name':skill['name']})
        packet=visual(battle,target,'druid_growth','druid_growth')
        feedback(battle,target,'status',status_id=sid,attack_packet=packet)
    c.abilities.spend(actor,skill);actor['acted']=True

def command(battle,actor,skill,cmd):
    from . import combat as c
    state=c.abilities.availability(actor,skill)
    if not state['available']:raise ValueError(state['reason'])
    kind=skill['druid_kind']
    target=actor if kind in FORMS else battle['units'].get(cmd.get('target_id'))
    if kind=='bramble_wall':
        target={'x':cmd.get('x'),'y':cmd.get('y')}
        if not strip(battle,actor,target['x'],target['y'],cmd.get('rotation',0)):raise ValueError('Choose three empty legal ground cells')
    elif kind not in FORMS:
        if not target or not c._combat_active(target) or target['team']!=actor['team']:raise ValueError('Choose a conscious ally or yourself')
        if c._apply_attack_approach(battle,actor,target,skill['range'],cmd):return False
        if not c._can_attack(battle,actor,target,skill['range']):raise ValueError('Target is outside range or clear sight')
    execute(battle,actor,target,skill,cmd.get('rotation',0))
    return kind not in FORMS

def previews(battle,actor):
    from . import combat as c
    result={}
    for skill in actor.get('skills',[]):
        if skill.get('druid_kind')!='bramble_wall' or not c.abilities.availability(actor,skill)['available']:continue
        result[skill['id']]={'kind':'bramble_wall','strips':{f'{x},{y},{r}':points
            for x in range(max(0,actor['x']-3),min(battle['width'],actor['x']+4))
            for y in range(max(0,actor['y']-3),min(battle['height'],actor['y']+4)) for r in (0,1)
            if (points:=strip(battle,actor,x,y,r))}}
    return result

def presentation(unit):
    kind=form(unit)
    if kind not in FORMS or not unit.get('form',{}).get('persistent'):return
    unit.update(portrait=f'/assets/druid-v1/portrait_{kind}.png',portrait_thumbnail=f'/assets/druid-v1/portrait_{kind}.png',
                portrait_full=f'/assets/druid-v1/portrait_{kind}.png',portrait_frame={'x':.5,'y':.5,'size':1,'image':'square'})
    for s in [*unit.get('skills',[]),*([unit['special']] if unit.get('special') else [])]:
        if s.get('druid_kind')==kind:
            s['form_return']=True;s['name']='Humanoid Form';s['description']='Quick Action. Return to humanoid form. Counts as your one form change this activation.'

def auto(battle,actor,targets):
    from . import combat as c
    skills=[s for s in actor.get('skills',[]) if s.get('druid_kind') and c.abilities.availability(actor,s)['available']]
    if not skills:return False
    wounded=[u for u in c._living(battle,actor['team']) if u['hp']<u['max_hp']*.65 and not conditions.has(u,'druid_rejuvenation') and c._can_attack(battle,actor,u,3)]
    healing_known=next((s for s in actor.get('skills',[]) if s.get('druid_kind')=='rejuvenation'),None)
    healing_ready=healing_known and actor.get('ability_state',{}).get(healing_known['id'],{}).get('ready_at',0)<=actor.get('ability_activation',0) and not conditions.has(actor,'mute')
    # Return before casting; never let the AI select fragile Rat speculatively.
    if form(actor) and (form(actor)=='rat' or wounded and healing_ready):
        returning=next((s for s in skills if s.get('druid_kind')==form(actor)),None)
        if returning:
            execute(battle,actor,actor,returning)
            skills=[s for s in actor.get('skills',[]) if s.get('druid_kind') and c.abilities.availability(actor,s)['available']]
    healing=next((s for s in skills if s.get('druid_kind')=='rejuvenation'),None)
    if healing and wounded:execute(battle,actor,min(wounded,key=lambda u:u['hp']/u['max_hp']),healing);return True
    protection=next((s for s in skills if s.get('druid_kind')=='living_armor'),None)
    threatened=[u for u in c._living(battle,actor['team']) if not conditions.has(u,'living_armor') and c._can_attack(battle,actor,u,3) and any(c._distance(u,t)<=2 for t in targets)]
    if protection and threatened:execute(battle,actor,min(threatened,key=lambda u:u['hp']/u['max_hp']),protection);return True
    if form(actor)=='rat':
        skill=next((s for s in skills if s.get('druid_kind')=='rat'),None)
        if skill:execute(battle,actor,actor,skill)
    elif not form(actor) and targets:
        desired='bulwark' if actor['hp']<actor['max_hp']*.4 else 'prowler'
        skill=next((s for s in skills if s.get('druid_kind')==desired),None)
        if skill:execute(battle,actor,actor,skill)
    if not any(c._can_attack(battle,actor,t) for t in targets):
        wall=next((t for t in battle.get('terrain',[]) if t.get('bramble_group') and not t.get('destroyed') and t['team']!=actor['team'] and c._can_attack(battle,actor,t)),None)
        if wall:c._damage_terrain(battle,actor,wall['id']);actor['acted']=True;return True
    return False


def settle(battle,unit):
    position=[unit['x'],unit['y']]
    if unit.get('druid_settled_position',position)==position:return
    unit['druid_settled_position']=position
    battle['druid_move_serial']=battle.get('druid_move_serial',0)+1
    adjacent_reactions(battle,unit,f"move:{battle['druid_move_serial']}")


def finish(unit):
    if any(s['id']=='living_armor' and s.get('ticks',0)<=0 for s in unit.get('statuses',[])):
        conditions.remove(unit,'living_armor')


def wither(battle,tile):
    tile.update(destroyed=True,blocking=False,blocks_sight=False,hp=0,kind='rubble')
    tile.setdefault('bramble_died_round',battle.get('round',1))


def cleanup(battle):
    """Living terrain withers when its caster can no longer sustain it."""
    from . import combat as c
    for tile in battle.get('terrain',[]):
        if not tile.get('bramble_group'):continue
        if tile.get('destroyed') or not c._combat_active(battle['units'].get(tile['druid_owner'],{})):
            wither(battle,tile)
            tile['bramble_fading']=battle.get('round',1)>tile['bramble_died_round']
    battle['terrain'][:]=[t for t in battle.get('terrain',[]) if not t.get('bramble_group') or
                          not t.get('destroyed') or battle.get('round',1)<t['bramble_died_round']+2]


def view_previews(battle,actor,skill,reachable,parents):
    from . import combat as c
    if not c.abilities.availability(actor,skill)['available'] or skill['druid_kind']=='bramble_wall':return {}
    targets=[actor] if skill.get('self_only') else c._living(battle,actor['team'])
    entries={}
    for target in targets:
        caster,path=c._attack_position(battle,actor,target,skill['range'],reachable,parents)
        if caster:entries[target['id']]={'chance':100,'support':True,**(path or {})}
    return entries
