"""Finite restoration, vulnerable rest and holy combat on existing activation clocks."""
from copy import deepcopy
import random
from . import combat_conditions as conditions
from .combat_feedback import record as feedback

GROUND = {'sanctuary', 'holy_light'}
LIMITS = {'mend': 5, 'heal': 2, 'sanctuary': 1}


def has(unit, name):
    return any(p.get('id') == 'job:cleric:' + name for p in unit.get('passives', []))


def healing(unit, target, kind):
    if kind == 'heal':
        return max(1, round(target['max_hp'] * .4))
    if kind == 'mend':
        return max(1, min(int(unit.get('intelligence', 4)), max(1, round(target['max_hp'] * .15))))
    return max(5, int(unit.get('intelligence', 4)) // 2)


def adapt(unit):
    """Adapt only equipped skill snapshots; never reset battle resource state."""
    priest = has(unit, 'battle_priest')
    for skill in unit.get('skills', []):
        kind = skill.get('cleric_kind')
        if kind in LIMITS:
            skill['cost'] = {'cooldown': {'mend':3, 'heal':5, 'sanctuary':6}[kind] if priest else 0,
                             'charges': None if priest else LIMITS[kind]}
            skill['self_only'] = priest
            skill['range'] = 1 if priest or kind == 'mend' else 3
            skill['name'] = 'Regeneration' if priest and kind == 'sanctuary' else kind.title()
            if priest:
                skill['description'] = (f'Self only. Restore {healing(unit, unit, kind)} HP' if kind != 'sanctuary'
                    else f'Self only. Restore {healing(unit, unit, kind)} HP at the start of each of your next three turns') + f'. No charges. Cooldown {skill["cost"]["cooldown"]} turns.'
        elif kind == 'smite':
            skill['cost']['cooldown'] = 4 if priest else 5
            if priest: skill['description'] = skill['description'].replace('Cooldown 5', 'Cooldown 4')
    if unit.get('special'):
        unit['special'] = next((s for s in unit.get('skills', []) if s['id'] == unit['special']['id']), unit['special'])


def stop_rest(unit):
    unit.pop('cleric_rest', None)
    conditions.remove(unit, 'cleric_rest')


def heal(battle, unit, amount, reason):
    from . import combat as c
    if not c._combat_active(unit): return 0
    amount = min(max(0, unit['max_hp'] - unit['hp']), max(0, amount))
    unit['hp'] += amount
    if amount:
        feedback(battle, unit, 'heal', amount)
        battle['log'].append(f"{unit['name']} restores {amount} HP with {reason}.")
        c.martial.effect(battle, unit, 'cleric_heal')
    return amount


def finish(battle, unit):
    from . import combat as c
    rest = unit.get('cleric_rest')
    if not rest or not c._combat_active(unit): return
    if unit.get('forced_skip') or any(conditions.has(unit,s) for s in conditions.RECOVERY|{'mute'}):
        stop_rest(unit); return
    stamp = deepcopy(unit.get('status_activation'))
    if rest.get('last_stamp') == stamp: return
    rest['last_stamp'] = stamp
    rest['turns'] += 1
    for status in unit.get('statuses',[]):
        if status['id']=='cleric_rest':status['completed_turns']=rest['turns']
    heal(battle, unit, max(1, round(unit['max_hp'] * .1)), 'Rest')
    if has(unit, 'battle_priest'): return
    for kind, period in {'mend':1, 'heal':2, 'sanctuary':3}.items():
        if rest['turns'] % period: continue
        key = 'job:cleric:' + kind
        if not any(s['id'] == key for s in unit.get('skills', [])): continue
        state = unit.setdefault('ability_state', {}).setdefault(key, {})
        state['uses'] = max(0, state.get('uses', 0) - 1)


def start(battle, unit):
    if any(conditions.has(unit, s) for s in conditions.RECOVERY | {'mute'}): stop_rest(unit)
    regen = next((s for s in unit.get('statuses', []) if s['id'] == 'cleric_regeneration'), None)
    if regen:
        heal(battle, unit, regen['healing'], 'Regeneration')
        regen['ticks'] -= 1
        if regen['ticks'] <= 0: conditions.remove(unit, 'cleric_regeneration')


def incoming(unit, amount):
    if has(unit,'battle_priest') and amount:amount=max(1,round(amount*.85))
    return max(1, round(amount * 1.75)) if unit.get('cleric_rest') and amount else amount


def cells(battle, center, kind):
    from . import combat as c
    radius = 1
    return [p for p in c._area_cells(battle, center, radius)
            if kind != 'holy_light' or p['x'] == center['x'] or p['y'] == center['y']]


def exorcist(battle, actor, target, packet=None):
    from . import combat as c
    if not has(actor, 'exorcist') or target.get('race') not in {'Undead','Revenant','Banshee','Vampire'} or not c._combat_active(target): return
    serial = battle.get('cleric_roll', 0); battle['cleric_roll'] = serial + 1
    chance = conditions.status_chance(target, 'stun', 50 if has(actor, 'battle_priest') else 25)
    if random.Random(f"{battle.get('seed')}:exorcist:{serial}:{actor['id']}").randint(1,100) <= chance:
        applied = conditions.apply(target, 'stun', 1, actor)
        feedback(battle, target, 'status' if applied else 'resisted', status_id='stun', attack_packet=packet)


def weapon_hit(battle, actor, target, ability=None, packet=None):
    from . import combat as c
    if actor.get('cleric_component') or actor.get('status_tick') or actor.get('capture_only'): return
    if (ability or {}).get('cleric_kind') or (ability or {}).get('mage_kind'): return
    if conditions.has(actor, 'cleric_smite') and c._combat_active(target) and (ability or {}).get('elevation_rule',actor.get('attack_elevation_rule')) in {'melee','ballistic','ignore'}:
        source = {**actor, 'cleric_component':True, 'attack':max(1, actor.get('intelligence',4)),
                  'attack_elevation_rule':'ignore', 'element':'holy', 'on_hit':None, 'damage_kind':'magic',
                  'knockout_finisher':0}
        begin=len(battle.setdefault('animation_events',[]))
        c._deal_damage(battle, source, target)
        for event in battle['animation_events'][begin:]:event['attack_packet']=packet
        c.martial.effect(battle, target, 'cleric_smite',packet)


def execute(battle, actor, target, skill):
    from . import combat as c
    kind = skill['cleric_kind']
    c._commit_player_movement(battle, actor)
    if not c._combat_active(actor) or actor.get('engineer_interrupted') and c.bard.attack_skill(skill): return
    stop_rest(actor)
    if kind in {'mend','heal'}:
        heal(battle, target, healing(actor,target,kind), skill['name'])
    elif kind == 'sanctuary':
        if has(actor,'battle_priest'):
            conditions.remove(actor,'cleric_regeneration')
            actor.setdefault('statuses',[]).append({'id':'cleric_regeneration','healing':healing(actor,actor,kind),'ticks':3})
            feedback(battle, actor, 'status', status_id='cleric_regeneration')
        else:
            zone = c.spaces.place_zone(battle,actor,{'zone':'sanctuary','turns':3},cells(battle,target,kind))
            zone['heal'] = healing(actor,actor,kind)
    elif kind == 'rest':
        actor['cleric_rest'] = {'turns':0, 'last_stamp':'not_completed'}
        actor.setdefault('statuses',[]).append({'id':'cleric_rest'})
        feedback(battle, actor, 'status', status_id='cleric_rest')
    elif kind == 'smite':
        conditions.apply(actor,'cleric_smite',2,actor)
        actor['cleric_smite_movement'] = actor.get('ability_activation',0)
        actor['movement_origin'] = {'x':actor['x'],'y':actor['y']}
        feedback(battle,actor,'status',status_id='cleric_smite')
        c.martial.effect(battle,actor,'cleric_smite')
    else:
        area = cells(battle,target,kind)
        c.engineer.area_hit(battle,actor,area)
        source = {**actor,'attack':max(1,actor.get('intelligence',4)), 'attack_elevation_rule':'ignore',
                  'element':'holy','on_hit':None,'cleric_component':True}
        for victim in list(battle['units'].values()):
            if victim['team'] == actor['team'] or not c._combat_active(victim) or {'x':victim['x'],'y':victim['y']} not in area: continue
            hit,preview,_ = c._attack_hits(battle,source,victim,'ignore',skill)
            packet = c.mage.packet(battle,actor,'holy_light',victim,0)
            if hit:
                c._deal_damage(battle,source,victim,max(1,source['attack']*150//100)-source['attack']+preview['damage_bonus'])
                if c._combat_active(victim):
                    applied = c.mage.roll(battle,actor,'holy_blind') <= conditions.status_chance(victim,'blind') and conditions.apply(victim,'blind',1,actor)
                    feedback(battle,victim,'status' if applied else 'resisted',status_id='blind',attack_packet=packet)
                    exorcist(battle,actor,victim,packet)
                c.martial.effect(battle,victim,'cleric_light',packet)
            else: feedback(battle,victim,'miss',attack_packet=packet)
            # Tie all damage/status feedback from this victim to its impact.
            for event in reversed(battle['animation_events']):
                if event.get('type') == 'mage_cast': break
                if event.get('type') == 'combat_feedback': event['attack_packet'] = packet
    c.abilities.spend(actor,skill)
    actor['acted'] = not skill.get('quick_action',False)
    c._record_sound(battle,'magic_cast' if kind not in {'rest','smite'} else 'guard')


def command(battle, actor, skill, cmd):
    from . import combat as c
    kind=skill['cleric_kind']
    if kind == 'rest' and actor.get('cleric_rest'):
        stop_rest(actor); return False
    if not c.abilities.availability(actor,skill)['available']: raise ValueError(c.abilities.availability(actor,skill)['reason'])
    target=battle['units'].get(cmd.get('target_id'))
    if skill.get('self_only'):
        if target and target['id'] != actor['id']: raise ValueError('This technique targets only yourself')
        target=actor
    elif kind in GROUND:
        if not target:
            x,y=cmd.get('x'),cmd.get('y')
            if type(x) is not int or type(y) is not int or not 0<=x<battle['width'] or not 0<=y<battle['height']: raise ValueError('Choose ground inside the map')
            target=c._ground_target(x,y)
    elif not target or target['team'] != actor['team'] or not c._combat_active(target): raise ValueError('Choose a conscious ally')
    if kind in {'mend','heal'} and target['hp'] >= target['max_hp']: raise ValueError('This character is already at full HP')
    if kind == 'holy_light' and not c.bard.can_attack(actor): raise ValueError('Cannot initiate this attack inside Song of Peace')
    if not skill.get('self_only') and c._apply_attack_approach(battle,actor,target,skill['range'],cmd): return False
    if not c._can_attack(battle,actor,target,skill['range']): raise ValueError('Target is outside range or clear sight')
    execute(battle,actor,target,skill)
    return not skill.get('quick_action',False)


def view_previews(battle, actor, skill, reachable, parents):
    from . import combat as c
    ground={};units={};kind=skill['cleric_kind']
    if not c.abilities.availability(actor,skill)['available']: return ground,units
    if kind=='holy_light' and not c.bard.can_attack(actor): return ground,units
    candidates = [actor] if skill.get('self_only') else [c._ground_target(x,y) for y in range(battle['height']) for x in range(battle['width'])] if kind in GROUND else c._living(battle,actor['team'])
    for target in candidates:
        if kind in {'mend','heal'} and target['hp']>=target['max_hp']:continue
        caster,path=c._attack_position(battle,actor,target,skill['range'],reachable,parents)
        if not caster:continue
        row={'chance':100,'support':kind!='holy_light',**(path or {})}
        if kind in {'mend','heal'}:row['heal']=min(target['max_hp']-target['hp'],healing(actor,target,kind))
        if kind in GROUND and not skill.get('self_only'):
            area=cells(battle,target,kind);row['zones']=[{'kind':'sanctuary' if kind=='sanctuary' else 'impact','cells':area}]
            if kind=='holy_light':
                row['target_forecasts']={}
                for victim in battle['units'].values():
                    if victim['team']==actor['team'] or not c._combat_active(victim) or {'x':victim['x'],'y':victim['y']} not in area:continue
                    source={**caster,'attack':max(1,caster.get('intelligence',4)),'attack_elevation_rule':'ignore','element':'holy'}
                    hit=c._attack_preview(battle,source,victim,'ignore',skill)
                    amount=c._damage_before_barrier({'animation_events':[]},source,deepcopy(victim),source['attack']*150//100-source['attack']+hit['damage_bonus'])
                    shield=max((s.get('amount',0) for s in victim.get('statuses',[]) if s['id']=='barrier'),default=0)
                    row['target_forecasts'][victim['id']]={'chance':hit['chance'],'damage_on_hit':max(0,amount-shield)}
            ground[f"{target['x']},{target['y']}"]=row
        else: units[target['id']]=row
    return ground,units


def auto(battle, actor, attack_targets=None):
    """Conservative healing; resting AI never assumes safety near enemies."""
    from . import combat as c
    skills=[s for s in actor.get('skills',[]) if s.get('cleric_kind') and c.abilities.availability(actor,s)['available']]
    for skill in sorted(skills,key=lambda s:s['cleric_kind']!='heal'):
        if skill['cleric_kind'] not in {'mend','heal'}:continue
        allies=[actor] if skill.get('self_only') else c._living(battle,actor['team'])
        wounded=[u for u in allies if u['hp']<u['max_hp']*.65 and c._can_attack(battle,actor,u,skill['range'])]
        if wounded:
            execute(battle,actor,min(wounded,key=lambda u:u['hp']/u['max_hp']),skill);return True
    enemies=[u for u in c._living(battle) if u['team']!=actor['team']]
    if actor.get('cleric_rest'):
        if any(c._distance(actor,u)<=u.get('move',3)+u.get('attack_range',1) for u in enemies):stop_rest(actor)
        else:return True
    if c.bard.can_attack(actor) and not actor.get('capture_weapon'):
        light=next((s for s in skills if s['cleric_kind']=='holy_light'),None)
        legal=[u for u in (enemies if attack_targets is None else attack_targets) if c._can_attack(battle,actor,u,light['range'])] if light else []
        if legal:
            target=max(legal,key=lambda u:sum({'x':e['x'],'y':e['y']} in cells(battle,u,'holy_light') for e in enemies))
            execute(battle,actor,target,light);return True
        smite=next((s for s in skills if s['cleric_kind']=='smite'),None)
        if smite and not conditions.has(actor,'cleric_smite') and any(c._can_attack(battle,actor,u,actor['attack_range']) for u in enemies):
            execute(battle,actor,actor,smite)
    if not has(actor,'battle_priest') and not any(c._distance(actor,u)<=u.get('move',3)+u.get('attack_range',1) for u in enemies):
        rest=next((s for s in skills if s['cleric_kind']=='rest'),None)
        if rest and any(actor.get('ability_state',{}).get(s['id'],{}).get('uses',0)>0 for s in actor.get('skills',[]) if s.get('cleric_kind') in LIMITS):
            execute(battle,actor,actor,rest);return True
    return False
