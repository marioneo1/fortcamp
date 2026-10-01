"""Persisted scene checks and encounter setup, independent of HTTP and storage."""
import random
from copy import deepcopy
from .content import ITEMS, MISSION_TEMPLATES
from .game import effective_stat, effective_attribute, perk_rank
from .outcome_balance import classify_roll, outcome_probabilities
from .races import race_mission_bonus
from .perk_effects import character_perks

def initial_scene():
    return {'node':None,'revision':0,'history':[],'bonus_keys':[]}

def choice_check(state,mission,analysis,choice):
    party_ids=analysis.get('mission_party_ids') or analysis.get('party_ids',[])
    party=[c for c in state['characters'] if c['id'] in party_ids]
    stat=choice.get('stat')
    def rating(c):
        return effective_attribute(state,c,stat) if stat in {'str','dex','agi','vit','int','luk'} else effective_stat(state,c,stat)+race_mission_bonus(c.get('race'),stat,mission.get('mission_form','operation'))
    lead=max(party,key=lambda c:(rating(c),c['id'])) if party else None
    bonus=rating(lead) + min(2,max(0,len(party)-1)) if stat and lead else 0
    allowed=True
    if choice.get('requires')=='builder':
        allowed=any(perk_rank(c,'building')>=1 or 'engineer' in character_perks(state,c,ITEMS) for c in party)
    dc=int(choice.get('difficulty',14))
    probabilities={key:0 for key in ('critical_failure','failure','success','critical_success')}
    if stat:
        probabilities=outcome_probabilities(bonus,dc,mission.get('rank','E'),bool(analysis.get('critical_success_available',not mission.get('critical_any'))),severe_failure=False)
    return {'allowed':allowed,'bonus':bonus,'difficulty':dc,'stat':stat,'lead':lead['name'] if lead else '', 'probabilities':probabilities}

def classify(die,total,dc,rank="E",available=True,critical_roll=101):
    return classify_roll(die,total,dc,rank,available,critical_roll,severe_failure=False)


def decision_view(state,template,analysis):
    scene=analysis['scene'];definition=template['decision_scene']
    node_id=scene.get('node') or definition['start'];node=definition['nodes'][node_id]
    return {'node_id':node_id,'revision':scene['revision'],'title':node['title'],'text':node['text'],
        'history':scene['history'],'choices':[{'id':cid,'label':choice['label'],'description':choice['description'],
            'check':choice_check(state,template,analysis,choice)} for cid,choice in node['choices'].items()]}

def advance_scene(state,template,analysis,seed,node_id,revision,choice_id):
    scene=deepcopy(analysis['scene']);definition=template['decision_scene']
    current=scene.get('node') or definition['start']
    if node_id!=current or revision!=scene['revision']:raise ValueError('This decision has already changed. Reopen the mission.')
    choice=definition['nodes'][current]['choices'].get(choice_id)
    if not choice:raise ValueError('Unknown choice')
    check=choice_check(state,template,analysis,choice)
    if not check['allowed']:raise ValueError('This approach needs an Engineer or Constructor training in the assigned party')
    rng=random.Random(f'{seed}:scene:{current}:{revision}:{choice_id}')
    die=rng.randint(1,20) if choice.get('stat') else None
    outcome=classify(die,die+check['bonus'],check['difficulty'],template.get('rank','E'),bool(analysis.get('critical_success_available',not template.get('critical_any'))),rng.randint(1,100)) if die else 'success'
    transition=deepcopy(choice['success' if outcome=='critical_success' else outcome])
    scene['history'].append({'choice':choice['label'],'outcome':outcome,'die':die,'total':die+check['bonus'] if die else None,'difficulty':check['difficulty'] if die else None,'lead':check['lead'],'text':transition.get('text','')})
    if transition.get('bonus') and transition['bonus'] not in scene['bonus_keys']:scene['bonus_keys'].append(transition['bonus'])
    scene['revision']+=1
    if transition.get('next'):scene['node']=transition['next']
    return scene,transition

def setup_encounter(battle,transition):
    """Setup is applied before the first combat activation, never after enemy AI."""
    players=[u for u in battle['units'].values() if u['team']=='player']
    enemies=[u for u in battle['units'].values() if u['team']=='enemy']
    setup=transition.get('setup')
    if setup in {'ambush','alert'}:
        favored='player' if setup=='ambush' else 'enemy'
        battle['turn_order'].sort(key=lambda uid:(battle['units'][uid]['team']!=favored,-battle['units'][uid]['initiative'],uid))
        battle['turn_index']=0
    if setup=='blockade':
        taken={(u['x'],u['y']) for u in battle['units'].values()} | {(t['x'],t['y']) for t in battle.get('terrain',[])}
        candidates=[(3,y) for y in (2,6)] if battle['width']>=12 else [(1,5),(3,5)]
        for index,(x,y) in enumerate(candidates):
            if (x,y) in taken:continue
            battle['terrain'].append({'id':f'approach_cover_{index}','name':'Prepared Barricade','x':x,'y':y,'kind':'palisade','blocking':True,'destructible':True,'hp':14,'max_hp':14,'armor':1,'destroyed_kind':'rubble','destroyed_movement_cost':2})
    if transition.get('boss') and enemies:
        boss=next((u for u in enemies if u.get('boss') or u.get('kind')=='chieftain'),enemies[0])
        old_name=boss['name']
        role='Warhost Marshal' if boss.get('race') in {'Goblin','Hobgoblin'} else 'Chapel Oathkeeper' if boss.get('race')=='Undead' else 'Banner Retrieval Officer'
        boss['name']=f"{role} {old_name}"
        for objective in battle['objectives']:objective['name']=objective['name'].replace(old_name,boss['name'])
        battle['log']=[line.replace(old_name,boss['name']) for line in battle['log']]
        boss.update(boss=True,hp=round(boss['max_hp']*1.25),max_hp=round(boss['max_hp']*1.25),attack=boss['attack']+2)
        battle['complication_boss']=boss['id']
    battle['approach']=setup or 'direct'
    if transition.get('text'):battle['log'].insert(0,transition['text'])
    return battle
