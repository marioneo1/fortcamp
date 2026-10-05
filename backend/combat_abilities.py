"""Small, versioned active-ability vocabulary. Definitions are data, never scripts."""
from copy import deepcopy
import math
from . import combat_spaces as spaces
from . import combat_entities as entities

VERSION = 1
STATUSES = {'stun','sleep','poison','bleed','charm','confuse','berserk','freeze',
            'burn','blind','bind','slow','paralyze','mute','fear','vulnerable','regeneration','braced','hobbled','armor_fracture'}
RULES = {'melee','ballistic','ignore','line_of_effect','physical_care'}


def _integer(value, low, high):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError('Ability number is outside its supported range')
    return value


def validate(skill):
    if not isinstance(skill, dict):
        raise ValueError('Ability definition must be an object')
    if skill.get('ability_version') != VERSION or skill.get('target') not in {'enemy','ally'}:
        raise ValueError('Unsupported ability version or target')
    if not isinstance(skill.get('id'), str) or not skill['id'] or len(skill['id']) > 100:
        raise ValueError('Ability needs a stable ID')
    if skill.get('elevation_rule') not in RULES:
        raise ValueError('Ability must declare an elevation rule')
    if skill.get('source_kind','equipment') not in {'equipment','character'}:
        raise ValueError('Unsupported ability source')
    _integer(skill.get('range'), 1, 20)
    if skill.get('range_shape','diamond') not in {'diamond','square'}:raise ValueError('Unsupported range shape')
    cost = skill.get('cost', {})
    if not isinstance(cost, dict) or set(cost) != {'cooldown','charges'}:
        raise ValueError('Unsupported ability cost')
    _integer(cost['cooldown'], 0, 20)
    if cost['charges'] is not None:
        _integer(cost['charges'], 1, 20)
    if not cost['cooldown'] and cost['charges'] is None:
        raise ValueError('Ability must have a cooldown or charge limit')
    effects = skill.get('effects')
    if not isinstance(effects, list) or not 1 <= len(effects) <= 4:
        raise ValueError('Ability needs one to four ordered effects')
    attacks = 0
    deployments = 0
    for effect in effects:
        if not isinstance(effect, dict):
            raise ValueError('Ability effect must be an object')
        kind = effect.get('type')
        allowed = {'attack': {'damage_bonus','armor_pierce','power_percent'}, 'heal': {'amount'},
                   'cleanse': {'statuses','radius'}, 'guard': set(), 'status': {'status','turns','chance'},
                   'barrier': {'amount','turns'}, 'mark': {'turns','accuracy'},
                   'displace': {'mode','distance','collision_damage','stop_adjacent','collision_stun'},
                   'leap_attack': {'radius','inner_push','outer_push','power_percent','collision_stun'},
                   'zone': {'zone','radius','turns'}, 'form': {'form','turns'}, 'deploy': {'entity'}}
        if kind not in allowed or set(effect) - (allowed[kind] | {'type','conditions'}):
            raise ValueError('Unsupported ability effect')
        if kind == 'attack':
            if skill['target'] != 'enemy' or attacks:
                raise ValueError('Only one enemy attack is supported')
            _integer(effect.get('damage_bonus',0), -30, 30)
            _integer(effect.get('armor_pierce',0), 0, 30)
        if kind in {'attack','leap_attack'}:_integer(effect.get('power_percent',100),100,250)
        if kind in {'displace','leap_attack'} and 'collision_stun' in effect and not isinstance(effect['collision_stun'],bool):
            raise ValueError('Invalid collision stun policy')
        if kind in {'heal','cleanse','guard','barrier'} and skill['target'] != 'ally':
            raise ValueError('Support effects require an ally target')
        if kind in {'mark','displace'} and skill['target'] != 'enemy':
            raise ValueError('Hostile tactical effects require an enemy target')
        if kind in {'zone','form'}:
            spaces.validate_effect(effect)
            _integer(effect.get('turns'),1,3)
            if kind=='zone':_integer(effect.get('radius'),0,1)
            if kind=='form' and skill['target']!='ally':
                raise ValueError('Forms require a self/ally target')
            if kind=='zone' and (skill['target']=='ally') != (spaces.ZONES[effect['zone']]['relation']=='ally'):
                raise ValueError('Zone target must match its ally/enemy policy')
        if kind=='deploy' and (effect.get('entity') not in entities.PROFILES or skill['target']!='ally'):
            raise ValueError('Deployment requires a supported entity and self/ally target')
        if kind=='deploy':
            deployments+=1
            if deployments>1:raise ValueError('Use one grouped deployment profile per ability')
        if kind in {'barrier','mark'}:
            _integer(effect.get('turns'),1,3)
            _integer(effect.get('amount') if kind=='barrier' else effect.get('accuracy',10),1,200 if kind=='barrier' else 15)
        if kind=='displace':
            if effect.get('mode') not in {'push','pull'}:raise ValueError('Unsupported displacement mode')
            _integer(effect.get('distance'),1,2)
            _integer(effect.get('collision_damage',0),0,10)
        if kind == 'leap_attack':
            if skill['target'] != 'enemy' or len(effects) != 1 or skill['range'] > 3:
                raise ValueError('Leap attacks require a short ground-targeted enemy ability')
            for field in ('radius','inner_push','outer_push'):_integer(effect.get(field),1,2)
        if kind == 'displace' and 'stop_adjacent' in effect and not isinstance(effect['stop_adjacent'],bool):
            raise ValueError('Invalid pull stopping policy')
        if kind == 'heal':
            _integer(effect['amount'], 1, 200)
        if kind == 'cleanse':
            if 'radius' in effect:_integer(effect['radius'],1,2)
            if not isinstance(effect.get('statuses'), list) or not effect['statuses'] or any(s not in STATUSES for s in effect['statuses']):
                raise ValueError('Unsupported cleansing status')
        if kind == 'status':
            if effect.get('status') not in STATUSES:
                raise ValueError('Unsupported status')
            _integer(effect.get('turns'),1,3)
            _integer(effect.get('chance',100),0,100)
        conditions = effect.get('conditions', [])
        if not isinstance(conditions, list) or len(conditions) > 2:
            raise ValueError('Too many ability conditions')
        for cond in conditions:
            if not isinstance(cond, dict):
                raise ValueError('Invalid ability condition')
            if cond.get('type') == 'hit' and set(cond) == {'type'}:
                if not attacks:
                    raise ValueError('Hit condition requires an earlier attack')
            elif cond.get('type') == 'target_has_status' and set(cond) == {'type','status'}:
                if cond['status'] not in STATUSES:raise ValueError('Unknown condition status')
            elif cond.get('type') == 'target_hp_below' and set(cond) == {'type','fraction'}:
                v=cond['fraction']
                if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0 < v <= 1:
                    raise ValueError('Invalid HP condition')
            else:
                raise ValueError('Unsupported ability condition')
        if kind == 'attack':
            attacks += 1
    return skill


def snapshot(skills, intelligence):
    """Adapt new-battle equipment techniques; old battle snapshots stay untouched."""
    result=[]
    for original in skills:
        skill=deepcopy(original)
        if skill.get('ability_version'):
            result.append(validate(skill))
            continue
        skill.update(ability_version=VERSION,target=skill.get('target','enemy'))
        cooldown={'precision_shot':2,'arc_bolt':2,'field_care':3,'shield_cover':3}.get(skill['id'],0)
        skill['cost']={'cooldown':cooldown,'charges':None if cooldown else 1}
        if skill['target']=='ally':
            effects=[]
            if skill.get('heal'):
                amount=skill['heal']+intelligence//2
                skill['resolved_heal']=amount
                effects.append({'type':'heal','amount':amount,
                                'conditions':[{'type':'target_hp_below','fraction':1}]})
            if skill.get('cleanses'):effects.append({'type':'cleanse','statuses':list(skill['cleanses'])})
            if skill.get('guard_ally'):effects.append({'type':'guard'})
        else:
            effects=[{'type':'attack','damage_bonus':skill.get('damage_bonus',3),
                      'armor_pierce':skill.get('armor_pierce',2 if skill['id']=='precision_shot' else 0)}]
        if skill.get('barrier'):
            effects.append({'type':'barrier','amount':skill['barrier'],'turns':1})
        if skill['id'] in {'hook_thrust','titan_thrust'}:
            mode='pull' if skill['id']=='hook_thrust' else 'push'
            effects.append({'type':'displace','mode':mode,'distance':1,'conditions':[{'type':'hit'}]})
            skill['description']=skill.get('description','')+f' On hit, {mode} the target one cell if terrain and resistance allow. No collision damage.'
        if skill['id']=='precision_shot':
            effects.append({'type':'mark','turns':2,'accuracy':10,'conditions':[{'type':'hit'}]})
            skill['description']=skill.get('description','')+' On hit, Mark for two target activations. Your first successful hit each activation gains 10 accuracy; allies do not inherit it.'
        skill['effects']=effects
        timing=(f'Ready again in {cooldown} of your turns.' if cooldown else 'One use of this technique per battle.')
        # Replace outdated availability wording; preserve actual technique description.
        skill['description']=skill.get('description','').replace('One shared technique use per battle.', '').replace('Once per battle.', '').strip()
        skill['description']=timing+' '+skill['description']
        result.append(validate(skill))
    return result


def availability(unit, skill):
    if not skill:return {'available':False,'reason':'No technique selected'}
    if not skill.get('ability_version'):
        return {'available':not unit.get('acted') and not unit.get('special_used',False),
                'reason':'Main action already used' if unit.get('acted') else 'Shared technique use spent' if unit.get('special_used') else None}
    state=unit.get('ability_state',{}).get(skill['id'],{})
    charges=skill['cost']['charges']
    if charges is not None and state.get('uses',0)>=charges:
        return {'available':False,'reason':'No uses remaining','uses_remaining':0,'cooldown_remaining':0}
    remaining=max(0,state.get('ready_at',0)-unit.get('ability_activation',0))
    restriction = ('Weapon techniques are unavailable in this form' if unit.get('form') and skill.get('source_kind','equipment')=='equipment' and any(e['type'] in {'attack','leap_attack'} for e in skill['effects']) else
                   'Capture weapons cannot perform damaging techniques' if unit.get('capture_weapon') and any(e['type'] in {'attack','leap_attack'} for e in skill['effects']) else
                   'Mute prevents this spell' if skill['elevation_rule'] in {'ignore','line_of_effect'} and any(s.get('id')=='mute' for s in unit.get('statuses',[])) else None)
    return {'available':remaining==0 and not unit.get('acted') and not restriction,'reason':'Main action already used' if unit.get('acted') else restriction or (f'Ready in {remaining} of your turns' if remaining else None),
            'cooldown_remaining':remaining,'uses_remaining':None if charges is None else charges-state.get('uses',0)}


def spend(unit, skill):
    if not availability(unit,skill)['available']:
        raise ValueError(availability(unit,skill)['reason'])
    if not skill.get('ability_version'):
        unit['special_used']=True
        return
    state=unit.setdefault('ability_state',{}).setdefault(skill['id'],{})
    state['uses']=state.get('uses',0)+1
    state['ready_at']=unit.get('ability_activation',0)+skill['cost']['cooldown']


def start_activation(unit, stamp):
    if unit.get('ability_stamp') != stamp:
        unit['ability_stamp']=list(stamp)
        unit['ability_activation']=unit.get('ability_activation',0)+1


def matches(condition, target, context):
    kind=condition['type']
    if kind=='hit':return bool(context.get('hit'))
    if kind=='target_has_status':return any(s['id']==condition['status'] for s in target.get('statuses',[]))
    return target['hp'] < target['max_hp']*condition['fraction']


def resolve(skill, target, handlers):
    """Fixed handler vocabulary; no expressions, arbitrary callbacks or trigger loops in data."""
    validate(skill)
    context={}
    for effect in skill['effects']:
        target=context.get('target',target)
        if context.get('interrupted'):break
        # A lethal hit still carries physical momentum, but cannot debuff a body.
        if target.get('hp',0)<=0 or not target.get('conscious',True):
            if effect['type']!='displace' or not context.get('hit'):continue
        if all(matches(c,target,context) for c in effect.get('conditions',[])):
            context.update(handlers[effect['type']](effect) or {})
    return context
