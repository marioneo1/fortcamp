"""Regular-character loadouts. Only authored, engine-supported skills are executable."""
from copy import deepcopy
from .combat_abilities import validate

CAPACITY = 5
JOBS = {}
SKILLS = {}


def active(key, name, description, effects, target='enemy', range=1, rule='melee', cooldown=2, range_shape='diamond'):
    return validate(dict(id=key, name=name, description=description, type='active',
        source_kind='character', ability_version=1, self_only=any(e['type']=='area_attack' for e in effects), target=target, range=range,
        elevation_rule=rule, range_shape=range_shape, cost={'cooldown':cooldown, 'charges':None}, effects=effects))


def passive(key, name, description, modifiers=None, reaction=None):
    return dict(id=key, name=name, description=description, type='passive', source_kind='character',
                modifiers=modifiers or {}, reaction=reaction)


def register(key, name, description, first, second, third):
    ids=[]
    for skill in (first, second, third):
        skill=deepcopy(skill);skill['id']=f'job:{key}:{skill["id"]}';skill['source_name']=name
        SKILLS[skill['id']]=skill;ids.append(skill['id'])
    JOBS[key]={'name':name, 'description':description, 'starter_skills':ids}


def strike(key, name, description, extra, power_percent=100):
    return active(key,name,description,[{'type':'attack','damage_bonus':0,'power_percent':power_percent},
        {**extra,'conditions':[{'type':'hit'}]}])


register('fighter','Fighter','Protect allies or break enemy positions.',
    strike('bash','Driving Strike','Strike with 150% attack power and push one cell. Solid collisions add half the hit as damage and stun for one activation. Colliding with a person damages and stuns both, including allies. Knockback resistance and stun immunity apply.',{'type':'displace','mode':'push','distance':1,'collision_stun':True},150),
    active('cover','Chain Snare','Hit an enemy within three cells, pull it up to two cells toward you, stopping beside you, halve its movement and reduce armor by 30% for two activations. Requires a clear chain path; displacement resistance applies.',[{'type':'attack','damage_bonus':0},{'type':'displace','mode':'pull','distance':2,'stop_adjacent':True,'conditions':[{'type':'hit'}]},{'type':'status','status':'hobbled','turns':2,'conditions':[{'type':'hit'}]},{'type':'status','status':'armor_fracture','turns':2,'conditions':[{'type':'hit'}]}],range=3,rule='ballistic',cooldown=3,range_shape='square'),
    passive('intercept','Intercept','Redirect one attack against an adjacent ally. Shares your reaction allowance.',reaction={'id':'intercept','name':'Intercept'}))
register('barbarian','Barbarian','Innate Fury: enemy damage that reaches HP grants 1 Fury (maximum 5). Spend Fury on heavy control attacks. Self/friendly damage and fully absorbed hits grant none.',
    active('reckless_blow','Reckless Blow','Strike at 200% attack power and gain 1 Fury, even on a miss. Take 20% more damage from all sources until your next turn. Cooldown: 2 of your turns.',[{'type':'attack','power_percent':200}],cooldown=2),
    active('skullbreaker','Skullbreaker','Spend 2 Fury. Strike at 125% attack power; a hit stuns for two target turns. Boss resistance and control immunity apply. Cooldown: 4 of your turns.',[{'type':'attack','power_percent':125},{'type':'status','status':'stun','turns':2,'conditions':[{'type':'hit'}]}],cooldown=4),
    passive('bloodfury','Bloodfury','At 50% HP or below after a direct enemy hit, gain 2 Fury instead of 1. Enemy damage over time still grants 1. Fully absorbed hits grant none.'))
SKILLS['job:barbarian:reckless_blow']['fury_gain']=1
SKILLS['job:barbarian:skullbreaker']['fury_cost']=2
def rogue_active(key,name,description,effects,quick=False,reach=1,cd=2):
    skill=active(key,name,description,effects,range=reach,cooldown=cd)
    skill.update(rogue_kind=key,quick_action=quick)
    return validate(skill)

register('rogue','Rogue','Exploit surrounding and debuffs with burst attacks; chain Quick Actions before the main action ends your turn.',
    rogue_active('cheap_shot','Cheap Shot','Main action. Cardinal surround determines attack power: alone 100%; two non-opposite sides 150%; opposite sides 200%; three sides 220%; four sides 250%. Highest only. Cooldown 1.',[{'type':'attack','power_percent':100}],cd=1),
    rogue_active('crippling_cut','Crippling Cut','Quick Action. 25% attack; a landed hit adds one Hobble stack for two target turns. Commits and locks normal walking; your main action and other Quick Actions remain. Cooldown 3.',[{'type':'attack','power_percent':25}],quick=True,cd=3),
    rogue_active('exploit_weakness','Exploit Weakness','Main action. 100% attack plus 50 percentage points per negative status stack, capped at 400%. Buffs and cooldown markers do not count. Cooldown 2.',[{'type':'attack','power_percent':100}],cd=2))
def ranger_active(key,name,description,power=100,cd=2,quick=False,reach=5):
    skill=active(key,name,description,[{'type':'mark','turns':3,'accuracy':1}] if key=='mark_quarry' else [{'type':'attack','power_percent':power}],range=reach,rule='ballistic',cooldown=max(1,cd))
    skill.update(ranger_kind=key,quick_action=quick);skill['cost']['cooldown']=cd
    return validate(skill)

register('ranger','Ranger','Mark your quarry for reliable shots. Exploit distance and stationary firing positions, or stack Poison and consume allied damage over time.',
    ranger_active('mark_quarry','Mark Quarry','Main action. Mark one target for three of its turns. All your attacks against your own marked target have 100% accuracy; other Rangers need their own mark. Marking a new quarry replaces your previous mark. No cooldown.',cd=0),
    ranger_active('longshot','Longshot','Requires your own Mark Quarry. Attack power by distance: 1-2 cells 100%; 3 cells 150%; 4 cells 175%; 5+ cells 200%. Has a 20% critical chance for double final damage before Barrier. Cooldown 2.'),
    ranger_active('poison_attack','Poison Attack','Main action. 150% attack and two Poison stacks, or four against your own quarry. Each stack deals 8% of your attack (minimum 1 HP) on the next two target turns; resistance applies. Imbue your next successfully damaging attack with one Poison stack per landed hit. No cooldown.',power=150,cd=0))
register('mage','Mage','Create dangerous ground or protect a threatened ally.',
    active('embers','Ember Ground','Create burning ground for two of your activations. Each burned tile entered on a committed path deals 3 damage and applies Burn. Re-entry counts again; overlapping patches do not stack. Allies are safe.',[{'type':'zone','zone':'ember','radius':1,'turns':2}],range=3,rule='line_of_effect',cooldown=3),
    active('ward','Ward','Give an ally a 10 HP Barrier for two of their activations.',[{'type':'barrier','amount':10,'turns':2}],'ally',3,'line_of_effect',3),
    passive('footwork','Light Step','Gain 5 evasion. Mute still prevents spells.',{'evasion':5}))
register('cleric','Cleric','Treat wounds and maintain a safe fighting position.',
    active('mend','Mend','Restore 12 HP to a living ally. Cannot revive.',[{'type':'heal','amount':12}],'ally',3,'line_of_effect',3),
    active('cleanse','Cleanse','Remove Poison, Bleed, Burn and Slow from an ally.',[{'type':'cleanse','statuses':['poison','bleed','burn','slow']}],'ally',3,'line_of_effect',3),
    passive('steadfast','Steadfast','Gain 1 armor. Does not make healing mandatory.',{'armor':1}))
def monk_technique(key, name, description, power, hits=1, cooldown=1, reach=1, stage=None, kind=None):
    skill=active(key,name,description,[{'type':'attack','power_percent':power,'hits':hits}],range=reach,cooldown=cooldown)
    skill.update(combo_kind=kind,melee_style='fist')
    if stage:skill['combo_stage']=stage
    return validate(skill)

register('monk','Monk','Chain close-range techniques into a powerful finishing strike, using footwork and defensive forms to stay alive.',
    monk_technique('rapid_palm','Rapid Palm','Three adjacent punches totaling 120% attack. Each landed punch adds 10% target vulnerability (maximum 30%) for three target turns; hits refresh it. Two landed punches guarantee Follow-up Ready; one has an 80% chance. Readiness lasts through your next two turns. Cooldown: 1 turn.',120,3,kind='opener'),
    monk_technique('iron_reversal','Iron Reversal','Requires Follow-up Ready. Adjacent 100% strike; a hit prepares the finisher and reduces the next direct attack against you by 20%, until your next turn, plus 25 evasion against the struck enemy for that window. Cooldown: 1 turn.',100,stage='follow_up',kind='follow_up'),
    monk_technique('heaven_piercing','Heaven-Piercing Strike','Requires Finisher Ready. Release a physical palm-force strike at 300% attack, up to three cells away with clear sight. Consumes readiness even on a miss. Cooldown: 3 turns.',300,cooldown=3,reach=3,stage='finisher',kind='finisher'))
register('bard','Bard','Keep allies fighting and weaken an enemy approach.',
    active('rally','Steady Song','Remove Fear and Slow from an ally and give an 8 HP Barrier for one activation.',[{'type':'cleanse','statuses':['fear','slow']},{'type':'barrier','amount':8,'turns':1}],'ally',3,'line_of_effect',3),
    active('discord','Discord','Slow an enemy for one activation. Resistance and immunities apply.',[{'type':'status','status':'slow','turns':1}],range=3,rule='line_of_effect',cooldown=3),
    passive('footwork','Stage Footwork','Gain 5 evasion.',{'evasion':5}))
register('druid','Druid','Change your fighting form or hold ground with thorns.',
    active('prowler','Prowler Form','Self only: INT-based melee and +1 movement for two of your activations. No healing on transformation.',[{'type':'form','form':'prowler','turns':2}],'ally',1,'line_of_effect',3),
    active('thorns','Thorn Ground','Create thorns around a chosen cell for two of your activations. Each thorn tile entered on a committed path deals 3 damage. Re-entry counts again; overlapping patches do not stack. Allies are safe.',[{'type':'zone','zone':'thorns','radius':1,'turns':2}],range=3,rule='line_of_effect',cooldown=3),
    passive('rooted','Rooted','Gain 25 knockback resistance.',{'knockback_resistance':25}))
register('engineer','Engineer','Spend finite Components on owner-linked machinery.',
    active('turret','Scrap Turret','Self only: spend 2 Components on a stationary automatic turret. No shot on the deployment turn.',[{'type':'deploy','entity':'scrap_turret'}],'ally',1,'physical_care',3),
    active('automaton','Guard Automaton','Self only: spend 3 Components on a commanded automaton. Its attacks consume your action.',[{'type':'deploy','entity':'guard_automaton'}],'ally',1,'physical_care',3),
    passive('reinforced','Reinforced Coat','Gain 1 armor. Does not increase device output.',{'armor':1}))
register('summoner','Summoner','Choose a commanded companion or automatic wisps.',
    active('wolf','Bonded Wolf','Self only: summon a commanded wolf, using 1 capacity. Its attacks spend your main action.',[{'type':'deploy','entity':'companion'}],'ally',1,'line_of_effect',3),
    active('wisps','Wisp Pair','Self only: summon two automatic wisps, using 2 capacity together. Share the automatic output budget.',[{'type':'deploy','entity':'wisps'}],'ally',1,'line_of_effect',3),
    passive('footwork','Keep Distance','Gain 5 evasion; your summons remain linked to you.',{'evasion':5}))
register('captor','Captor','Isolate a target or hold enemies for capture. Capture weapons remain necessary for Subdue.',
    active('bind','Binding Line','Attempt Bind for two target activations, leaving time for a follow-up capture. Range 2; 75% before resistance, no damage or guaranteed capture.',[{'type':'status','status':'bind','turns':2,'chance':75}],range=2,rule='ballistic',cooldown=3),
    active('pull','Reel In','Pull an enemy one cell toward you. Stable targets resist. No damage.',[{'type':'displace','mode':'pull','distance':1}],range=2,rule='ballistic'),
    passive('anchored','Sure Grip','Gain 25 knockback resistance and +4 capture chance with capture weapons. No damaging attack bonus.',{'knockback_resistance':25,'capture_chance':4}))


def later(job, *skills):
    unlocks=[]
    for threshold,original in zip((2,5,9),skills):
        skill=deepcopy(original);skill['id']=f'job:{job}:{skill["id"]}';skill['source_name']=JOBS[job]['name']
        SKILLS[skill['id']]=skill;unlocks.append({'skill_id':skill['id'],'contracts':threshold})
    JOBS[job]['unlocks']=unlocks


later('fighter',
    passive('riposte','Riposte','Counter a survived melee hit at half attack when in reach. Intercept and Riposte compete for one reaction.',reaction={'id':'riposte','name':'Riposte'}),
    active('pull','Earthbreaker','Leap up to three cells onto open ground. The landing shockwave strikes enemies within two cells with 200% attack power: the inner ring pushes two cells, the outer ring one. Collisions add half the impact damage to both people and stun surviving units for one activation. Walls, elevation and knockback resistance still matter. Ready again in five of your turns.',[{'type':'leap_attack','radius':2,'inner_push':2,'outer_push':1,'power_percent':200,'collision_stun':True}],range=3,rule='melee',cooldown=5),
    active('rally','Hold Together','Click your fighter. Remove Fear from yourself and allies within one cell. Each takes 25% less damage from their next direct hit and deals 25% more damage with their next attack, including all targets of an area attack. Each bonus is used separately; a missed attack spends the attack bonus. Walls block the effect. Bonuses do not stack.',[{'type':'cleanse','statuses':['fear'],'radius':1},{'type':'status','status':'rally_protection','turns':1,'radius':1},{'type':'status','status':'rally_power','turns':1,'radius':1}],'ally',1,'physical_care',4))
later('barbarian',
    passive('bloodied_strength','Bloodied Strength','Attack rises with missing HP: no bonus at full health, up to +50% attack at 1 HP. Healing reduces the bonus.'),
    active('groundbreaker','Groundbreaker','Spend 4 Fury. Strike enemies in all eight adjacent cells at 200% attack power and push them one cell. Walls block the wave; knockback resistance and collision damage apply. Allies are safe. Target yourself. Cooldown: 5 of your turns.',[{'type':'area_attack','radius':1,'push':1,'power_percent':200}],'ally',1,'physical_care',5),
    passive('too_angry_to_fall','Too Angry to Fall','Once per battle, lethal damage leaves you at 1 HP. Further lethal damage cannot finish you until your next turn begins. You do not automatically die afterward; another lethal hit is needed. Does not prevent capture or disappearing into a lethal pit.'))
SKILLS['job:barbarian:groundbreaker'].update(fury_cost=4,self_only=True)
later('mage',
    active('binding','Binding Circle','Create enemy-binding ground around a target for two of your activations. Entering triggers control recovery rules.',[{'type':'zone','zone':'binding','radius':1,'turns':2}],range=3,rule='line_of_effect',cooldown=3),
    active('scorch','Scorch','Attempt Burn for two target activations, 75% before resistance. No direct damage.',[{'type':'status','status':'burn','turns':2,'chance':75}],range=3,rule='line_of_effect',cooldown=3),
    passive('armored','Wardweave','Gain 1 armor; consumes a slot instead of another spell.',{'armor':1}))
later('cleric',
    active('sanctuary','Sanctuary','Create healing ground around a chosen cell for two of your activations. Restores 3 HP at ally activation start; Burn prevents healing.',[{'type':'zone','zone':'sanctuary','radius':1,'turns':2}],'ally',3,'line_of_effect',3),
    active('barrier','Shelter','Give an ally a 14 HP Barrier for two target activations. Replaces weaker Barriers; does not stack.',[{'type':'barrier','amount':14,'turns':2}],'ally',3,'line_of_effect',3),
    passive('intercept','Stand Beside Them','Intercept one direct attack against an adjacent ally. Shares your reaction allowance.',reaction={'id':'intercept','name':'Stand Beside Them'}))
later('bard',
    active('refrain','Restoring Refrain','Apply Regeneration for two ally activations. Cannot revive.',[{'type':'status','status':'regeneration','turns':2}],'ally',3,'line_of_effect',3),
    active('silence','Silencing Note','Attempt Mute for one target activation; 70% before resistance.',[{'type':'status','status':'mute','turns':1,'chance':70}],range=3,rule='line_of_effect',cooldown=3),
    active('cover','Protective Verse','Grant Guard to an ally at range 3. Mute prevents this spell.',[{'type':'guard'}],'ally',3,'line_of_effect',3))
later('druid',
    active('bulwark','Bulwark Form','Self only: INT-based melee, +3 armor, -1 movement and 50 knockback resistance for two of your activations. No HP refill.',[{'type':'form','form':'bulwark','turns':2}],'ally',1,'line_of_effect',3),
    active('sprite','Grove Sprite','Self only: deploy an automatic healing sprite using 1 capacity. It shares the owner output budget.',[{'type':'deploy','entity':'grove_sprite'}],'ally',1,'line_of_effect',3),
    active('bark','Bark Ward','Give yourself or an adjacent ally a 12 HP Barrier for two target activations.',[{'type':'barrier','amount':12,'turns':2}],'ally',1,'line_of_effect',3))
later('engineer',
    active('trap','Binding Trap','Create enemy-binding ground around a target for two of your activations. Range 2; control recovery applies.',[{'type':'zone','zone':'binding','radius':1,'turns':2}],range=2,rule='ballistic',cooldown=3),
    active('plate','Cover Plate','Give yourself or an adjacent ally Guard and an 8 HP Barrier for one target activation.',[{'type':'guard'},{'type':'barrier','amount':8,'turns':1}],'ally',1,'physical_care',3),
    passive('brace','Braced Frame','Gain 50 knockback resistance. No extra Components or device damage.',{'knockback_resistance':50}))
later('summoner',
    active('bulwark','Stone Bulwark','Self only: deploy a durable commanded defender using 2 capacity. Attacks consume your action.',[{'type':'deploy','entity':'bulwark'}],'ally',1,'line_of_effect',3),
    active('sprite','Grove Sprite','Self only: deploy an automatic healing sprite using 1 capacity. Shares the automatic output budget.',[{'type':'deploy','entity':'grove_sprite'}],'ally',1,'line_of_effect',3),
    active('manifest','Astral Guardian','Self only: once per encounter, deploy a commanded guardian using 2 capacity. Attacks consume your action.',[{'type':'deploy','entity':'manifestation'}],'ally',1,'line_of_effect',3))
later('captor',
    active('field','Restraint Field','Create enemy-binding ground around a target for two of your activations. Entering attempts Bind; does not capture.',[{'type':'zone','zone':'binding','radius':1,'turns':2}],range=2,rule='ballistic',cooldown=3),
    active('dust','Blinding Powder','Attempt Blind for one target activation at range 2. 75% before resistance; no damage.',[{'type':'status','status':'blind','turns':1,'chance':75}],range=2,rule='ballistic',cooldown=3),
    passive('coat','Padded Coat','Gain 1 armor. Does not improve capture chance.',{'armor':1}))



def add_unlocks(job, entries):
    for threshold, original in entries:
        skill=deepcopy(original);skill['id']=f'job:{job}:{skill["id"]}';skill['source_name']=JOBS[job]['name']
        SKILLS[skill['id']]=skill
        JOBS[job].setdefault('unlocks',[]).append({'skill_id':skill['id'],'contracts':threshold})


add_unlocks('ranger',[
    (2,ranger_active('multi_shot','Multi-Shot','Fire 2-4 arrows, each at 75% attack and 50% base accuracy. Your quarry guarantees every arrow hits. Poison imbue applies one stack per damaging arrow. Generic weapon procs have one volley budget. Cooldown 2.',power=75)),
    (5,ranger_active('rapid_fire','Rapid Fire','Quick Action. Select an enemy; randomly execute a currently usable equipped Ranger attack that can reach it, without spending the selected attack cooldown. Basic Attack fallback if none qualify. Commits and locks normal walking; your main action remains. Cooldown 4.',cd=4,quick=True)),
    (9,passive('sharpshooter','Sharpshooter','Finish a full turn without changing tiles to gain +10% damage and +2 attack/technique range. Lasts while you stay put. Committed or forced movement ends it; discarded movement previews do not.')),
    (12,ranger_active('pestilence_shot','Pestilence Shot','100% attack. A hit reduces target attack by 25% and increases damage it receives from ALL sources by 25%, including allied attacks and Poison/Bleed, for three target turns. Adds to other incoming-damage vulnerabilities. Cooldown 4.',cd=4)),
    (16,ranger_active('rupturing_blow','Rupturing Blow','150% attack. On a landed hit, consume all allied Poison and Bleed and immediately deal 50% of their remaining base damage, amplified by Pestilence. Bleed potential assumes future exertion. A miss consumes nothing. Cooldown 2.',power=150)),
])

brace=active('brace','Brace','Self only: take 25% less damage from all sources for your next three turns. Cooldown: 5 of your turns.',[{'type':'status','status':'brace_defense','turns':3}],'ally',1,'physical_care',5)
brace['self_only']=True
wind=active('second_wind','Second Wind','Self only: immediately restore 50% of maximum HP, up to full health. One use per battle.',[{'type':'heal','max_hp_percent':50}],'ally',1,'physical_care',1)
wind.update(self_only=True,cost={'cooldown':0,'charges':1})
add_unlocks('fighter',[(12,brace),(16,wind),(20,active('victory_strike','Victory Strike','Strike at 150% attack power. Killing the target restores 10% of your maximum HP. Cooldown: 2 of your turns.',[{'type':'attack','power_percent':150}],cooldown=2))])
add_unlocks('barbarian',[(12,passive('bloodthirst','Bloodthirst','A killing blow restores 20% of maximum HP. Multiple kills during the same turn each heal you. Then unavailable for 3 of your turns.')),
                       (16,passive('unstoppable','Unstoppable','Automatically spend 1 Fury to remove one harmful status. Prioritizes disabling effects. Cooldown: 3 of your turns. Does not remove the exposure from Reckless Blow.'))])

BARBARIAN_OLD_IDS = dict(zip(('shove','expose','anchored','hide','drive','stand'),
                           ('reckless_blow','skullbreaker','bloodfury','bloodied_strength','groundbreaker','too_angry_to_fall')))

dash=active('sweeping_dash','Sweeping Dash','Dash through up to three cells to empty ground. Each crossed enemy takes one 50% attack attempt. Walls, closed gates and pits block the route; ground hazards still hurt. Grants 10% parry against single-target physical melee/ranged attacks until your next turn; excludes magic/AoE. Does not advance your combo. Cooldown: 2 turns.',[{'type':'dash_attack','power_percent':50}],range=3,cooldown=2)
dash['melee_style']='fist'
add_unlocks('monk',[(2,passive('perfect_rhythm','Perfect Rhythm','Follow-ups gain 10 percentage points of accuracy. Your ready finisher cannot miss, but armor, Barrier and interception still apply.')),
    (5,monk_technique('crushing_fist','Crushing Fist','Adjacent 150% strike. A hit has a 70% chance to grant Follow-up Ready. Successful advancement also rolls a 50% one-turn stun chance, reduced by resistance. More immediate damage, less reliable setup. Cooldown: 1 turn.',150,kind='opener')),
    (9,dash),
    (12,monk_technique('breaking_combination','Breaking Combination','Requires Follow-up Ready. Two adjacent punches totaling 120% attack. Any hit prepares the finisher and opens the target guard: +25% direct attack damage from all allies until the end of your next turn. Does not amplify damage over time or collisions. Grants Combat Rhythm: each landed attack heals 3 HP for your next three turns, including individual punches and enemies crossed by Dash. Cooldown: 2 turns.',120,2,2,stage='follow_up',kind='follow_up')),
    (16,passive('flowing_footwork','Flowing Footwork','Advancing your combo grants +1 movement on your next turn and +10 evasion until that turn ends. Refreshes without stacking. Ten evasion points reduce normal melee hit chance by about 6 percentage points and ranged hit chance by 10.'))])

add_unlocks('rogue',[(2,rogue_active('shadowstep','Shadowstep','Quick Action. Choose a visible enemy within three cells, then a legal cardinal adjacent landing. Confirm to teleport. Locks normal walking; no damage. Cooldown 3.',[{'type':'rogue_utility','kind':'shadowstep'}],True,3,3)),
    (5,rogue_active('caltrops','Caltrops','Quick Action. Place a horizontal or vertical 1x3 strip within three cells. Placement on an occupied tile and each actual entry attempt one Bleed and one Hobble stack for two target turns, including allies and forced movement. Strip lasts two of your activations. Locks normal walking. Cooldown 4.',[{'type':'rogue_utility','kind':'caltrops'}],True,3,4)),
    (9,rogue_active('backflip','Backflip','Quick Action. Leap one to three cells in a cardinal direction to legal ground. Walls and immobilization block it. Locks normal walking but keeps your main action. Cooldown 2.',[{'type':'rogue_utility','kind':'backflip'}],True,3,2)),
    (12,passive('trap_expert','Trap Expert','You do not trigger tagged traps, including allied or enemy Caltrops. Fire, poison zones, pits and other terrain hazards still affect you.')),
    (16,rogue_active('throwing_knife','Throwing Knife Technique','Deliver an equipped Cheap Shot, Exploit Weakness or basic Attack at an enemy beyond melee reach and within three cells. Uses the selected main action and both cooldowns, without extra damage. Cheap Shot uses a virtual cardinal strike side. Cancel spends nothing. Cooldown 3.',[{'type':'rogue_utility','kind':'throwing_knife'}],False,3,3))])
ROGUE_OLD_IDS=dict(zip(('bleed','blind','footwork','venom','pin','riposte'),('cheap_shot','crippling_cut','trap_expert','exploit_weakness','shadowstep','backflip')))

MONK_OLD_IDS=dict(zip(('palm','brace','riposte','bind','returning','stance'),
                     ('rapid_palm','iron_reversal','perfect_rhythm','crushing_fist','sweeping_dash','flowing_footwork')))

def eligible(character):
    return character.get('source_kind') not in {'champion','celestial'} and not character.get('temporary_mercenary')


def initialize(character):
    # Legacy characters opt in deliberately. No inferred class or equipment replacement.
    if eligible(character):
        character.setdefault('job_id',None)
        character.setdefault('learned_skills',[])
        character.setdefault('equipped_skills',[])
        character.setdefault('skill_slots',CAPACITY)
        character.setdefault('job_practice',0)
        character.setdefault('job_contract_credits',[])
        if character.get('job_id')=='barbarian':
            for field in ('learned_skills','equipped_skills'):
                character[field]=list(dict.fromkeys('job:barbarian:'+BARBARIAN_OLD_IDS.get(key.split(':')[-1],key.split(':')[-1]) if key.startswith('job:barbarian:') else key for key in character[field]))
        if character.get('job_id')=='ranger' and character.get('ranger_kit_version',0)<1:
            replacements={'mark':'mark_quarry','snare':'multi_shot','footwork':'sharpshooter','anchored':'sharpshooter','poison':'poison_attack','dust':'pestilence_shot'}
            legacy=any(k.startswith('job:ranger:') and k.split(':')[-1] in replacements for k in character['learned_skills'])
            for field in ('learned_skills','equipped_skills','combat_skill_order'):
                if field in character:character[field]=list(dict.fromkeys('job:ranger:'+replacements.get(k.split(':')[-1],k.split(':')[-1]) if k.startswith('job:ranger:') else k for k in character[field]))
            for key in JOBS['ranger']['starter_skills']:
                if key not in character['learned_skills']:character['learned_skills'].append(key)
            character['ranger_kit_version']=1
            if legacy:character['job_migration_note']='Ranger now uses owner-specific Quarry, distance shots and stacking Poison. Existing choices and earned practice are preserved; additional learned techniques can be equipped while idle.'
        if character.get('job_id')=='rogue' and character.get('rogue_kit_version',0)<1:
            legacy=any(k.startswith('job:rogue:') and k.split(':')[-1] in ROGUE_OLD_IDS for k in character['learned_skills'])
            for field in ('learned_skills','equipped_skills','combat_skill_order'):
                if field in character:character[field]=list(dict.fromkeys('job:rogue:'+ROGUE_OLD_IDS.get(k.split(':')[-1],k.split(':')[-1]) if k.startswith('job:rogue:') else k for k in character[field]))
            for key in JOBS['rogue']['starter_skills']:
                if key not in character['learned_skills']:character['learned_skills'].append(key)
            if legacy and len(character['equipped_skills'])<CAPACITY and 'job:rogue:exploit_weakness' not in character['equipped_skills']:character['equipped_skills'].append('job:rogue:exploit_weakness')
            character['rogue_kit_version']=1
            if legacy:character['job_migration_note']='Rogue now uses positional burst, stacking traps and Quick Actions. Prior skills were mapped to replacements; earned practice and order are preserved.'
        if character.get('job_id')=='monk' and character.get('monk_kit_version',0)<1:
            legacy=any(key.startswith('job:monk:') and key.split(':')[-1] in MONK_OLD_IDS for key in character['learned_skills'])
            for field in ('learned_skills','equipped_skills','combat_skill_order'):
                if field in character:
                    character[field]=list(dict.fromkeys('job:monk:'+MONK_OLD_IDS.get(key.split(':')[-1],key.split(':')[-1]) if key.startswith('job:monk:') else key for key in character[field]))
            for key in JOBS['monk']['starter_skills']:
                if key not in character['learned_skills']:character['learned_skills'].append(key)
            if legacy and 'job:monk:heaven_piercing' not in character['equipped_skills']:
                if len(character['equipped_skills'])<CAPACITY:character['equipped_skills'].append('job:monk:heaven_piercing')
            character['monk_kit_version']=1
            if legacy:character['job_migration_note']='Monk now uses combo techniques. Existing choices were mapped to replacements; earned practice and learned skills are preserved. Heaven-Piercing Strike is learned; equip it if your five slots were already full.'
        job=JOBS.get(character.get('job_id'))
        if job:
            for unlock in job['unlocks']:
                if character['job_practice']>=unlock['contracts'] and unlock['skill_id'] not in character['learned_skills']:
                    character['learned_skills'].append(unlock['skill_id'])
    return character


def update(state, character_id, skill_ids, job_id=None):
    character=next((c for c in state.get('characters',[]) if c['id']==character_id),None)
    if not character or not eligible(character):raise ValueError('Choose a regular character')
    if character.get('status','idle')!='idle' or character.get('assignment'):
        raise ValueError('Change skills while idle and unassigned')
    if not isinstance(skill_ids,list) or any(not isinstance(s,str) for s in skill_ids) or len(set(skill_ids))!=len(skill_ids):
        raise ValueError('Select distinct skills')
    draft=deepcopy(character);initialize(draft)
    if job_id is not None:
        if job_id not in JOBS:raise ValueError('Choose a valid Job')
        if draft['job_id'] and draft['job_id']!=job_id:raise ValueError('Job changes are not available yet')
        if not draft['job_id']:
            draft['job_id']=job_id;draft['learned_skills']=list(JOBS[job_id]['starter_skills'])
    if len(skill_ids)>CAPACITY:raise ValueError('Active and passive skills share five slots')
    if any(s not in draft['learned_skills'] or s not in SKILLS for s in skill_ids):
        raise ValueError('Equip only skills this character has learned')
    draft['equipped_skills']=list(skill_ids)
    character.update(draft)
    return character


def snapshot(character):
    if not eligible(character):return [],[],{}
    initialize(character)
    equipped=character.get('equipped_skills',[])
    if len(equipped)>CAPACITY or len(set(equipped))!=len(equipped):raise ValueError('Invalid character loadout')
    actives=[];passives=[];modifiers={}
    for key in equipped:
        if key not in character.get('learned_skills',[]) or key not in SKILLS:raise ValueError('Unknown or unlearned equipped skill')
        skill=deepcopy(SKILLS[key])
        if skill['type']=='active':actives.append(skill)
        else:
            passives.append(skill)
            for stat,value in skill['modifiers'].items():modifiers[stat]=modifiers.get(stat,0)+value
    return actives,passives,modifiers


def save_skill_order(state, character_id, skill_ids):
    """Presentation only: never alters skills, availability or a battle snapshot."""
    character=next((c for c in state['characters'] if c['id']==character_id),None)
    if character is None:raise ValueError('Character not found')
    if len(skill_ids)>100 or len(set(skill_ids))!=len(skill_ids) or any(not isinstance(k,str) or not k or len(k)>160 for k in skill_ids):
        raise ValueError('Invalid skill order')
    character['combat_skill_order']=list(skill_ids)
    return list(skill_ids)


def credit_contract(state, party_ids, outcome, contract_key, debug=False):
    """One practice per successful expedition; never grant retroactive stats/slots."""
    if debug or outcome not in {'success','critical_success'}:return []
    results=[]
    for character in state.get('characters',[]):
        if character['id'] not in party_ids or not eligible(character) or character.get('job_id') not in JOBS:continue
        initialize(character)
        if contract_key in character['job_contract_credits']:continue
        character['job_contract_credits']=(character['job_contract_credits']+[contract_key])[-32:]
        character['job_practice']+=1
        learned=[]
        for unlock in JOBS[character['job_id']]['unlocks']:
            key=unlock['skill_id']
            if character['job_practice']>=unlock['contracts'] and key not in character['learned_skills']:
                character['learned_skills'].append(key);learned.append(key)
        results.append({'character_id':character['id'],'name':character.get('name','Adventurer'),
                        'practice':character['job_practice'],'learned':learned})
    return results


def public_catalog():
    return {'jobs':deepcopy(JOBS),'skills':deepcopy(SKILLS),'capacity':CAPACITY}
