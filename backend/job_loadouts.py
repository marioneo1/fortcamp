"""Regular-character loadouts. Only authored, engine-supported skills are executable."""
from copy import deepcopy
from .combat_abilities import validate

CAPACITY = 5
JOBS = {}
SKILLS = {}


def active(key, name, description, effects, target='enemy', range=1, rule='melee', cooldown=2, range_shape='diamond', fury_cost=None):
    return validate(dict(id=key, name=name, description=description, type='active',
        source_kind='character', ability_version=1, self_only=any(e['type']=='area_attack' for e in effects), target=target, range=range,
        elevation_rule=rule, range_shape=range_shape, cost={'cooldown':cooldown, 'charges':None}, effects=effects,
        **({'fury_cost':fury_cost} if fury_cost is not None else {})))


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
    active('skullbreaker','Skullbreaker','Spend 2 Fury. Strike at 125% attack power; a hit stuns for two target turns. Boss resistance and control immunity apply. No cooldown; costs 2 Fury.',[{'type':'attack','power_percent':125},{'type':'status','status':'stun','turns':2,'conditions':[{'type':'hit'}]}],cooldown=0,fury_cost=2),
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
    ranger_active('poison_attack','Poison Attack','Main action. 150% attack and two Poison stacks, or four against your own quarry. Poison deals 10% of target maximum HP once at turn end, then one duration stack is removed; extra stacks extend duration, not damage; application resistance applies. Imbue your next successfully damaging attack with one Poison stack per landed hit. No cooldown.',power=150,cd=0))
def mage_active(key,name,description,cd=3,reach=5,target='enemy'):
    skill=dict(id=key,name=name,description=description,type='active',source_kind='character',ability_version=1,target=target,range=reach,elevation_rule='line_of_effect',cost={'cooldown':cd,'charges':None},effects=[{'type':'mage_spell','kind':key}])
    skill.update(mage_kind=key,self_only=key=='typhoon')
    return validate(skill)
register('mage','Mage','Fragile elemental caster: create Wet, Freeze and burning ground, then exploit those states with spells and allies.',
    mage_active('chain_lightning','Chain Lightning','150% primary / 125% chained attack power. Bounce to one nearest unhit enemy within two cells, continuing until none remain. Wet targets take 250% / 175% power and roll 25% Paralysis for one turn before resistance. Wet is retained. Clear sight required for each bounce. Cooldown 4.',4),
    mage_active('fireball','Fireball','Ground or unit centre; two-cell diamond radius, walls block the blast. Hits everyone, including allies and yourself. Centre 150%, outer 125% attack; applies one Burn stack. Consumes Wet to apply Blister: -10% outgoing damage and -10 accuracy for two target turns. Leaves Scorched ground that burns everyone for two caster turns: each committed tile entry adds Burn and triggers its current stack damage. Cooldown 3.',3),
    mage_active('typhoon','Typhoon','Target yourself. All OTHER units within a three-cell diamond, including allies, take 25% attack power and are pushed two cells away; applies Wet for two target turns. Resistance, walls, pits and collision damage apply. Cooldown 3.',3,1,'ally'))
def cleric_active(key,name,description,target='ally',reach=3,cd=0,charges=None,quick=False,self_only=False):
    skill=dict(id=key,name=name,description=description,type='active',source_kind='character',ability_version=1,
               target=target,range=reach,elevation_rule='line_of_effect',cost={'cooldown':cd,'charges':charges},
               effects=[{'type':'cleric_spell','kind':key}],cleric_kind=key,quick_action=quick,self_only=self_only)
    return validate(skill)
register('cleric','Cleric','Finite restoration and vulnerable Rest, or self-sustaining holy combat with Battle Priest.',
    cleric_active('mend','Mend','Restore your INT in HP, capped at 15% of target maximum HP (minimum 1), to yourself or an adjacent ally. Five charges per battle, no cooldown. Rest recovers charges.',reach=1,charges=5),
    cleric_active('rest','Rest','Main action. Begin resting until you move, attack, cast another skill, cancel, take direct HP damage, or suffer hard control/Mute. Take 75% more damage from ALL sources. Each completed resting turn restores 10% maximum HP and 1 Mend charge; every second restores 1 Heal and every third 1 Sanctuary. Continuous-session progress resets on interruption. Select Rest again to cancel freely. Battle Priest only receives the self-healing.',reach=1,self_only=True),
    cleric_active('holy_light','Holy Light','Choose ground or a unit as the centre. Holy light strikes enemies along a five-cell cross: the centre and one cell in each cardinal direction; walls block rays. 150% INT-based magical power. Landed hits apply Blind for one target turn before resistance. Allies are safe. Cooldown 4.',target='enemy',reach=4,cd=4))

def monk_technique(key, name, description, power, hits=1, cooldown=1, reach=1, stage=None, kind=None):
    skill=active(key,name,description,[{'type':'attack','power_percent':power,'hits':hits}],range=reach,cooldown=cooldown)
    skill.update(combo_kind=kind,melee_style='fist')
    if stage:skill['combo_stage']=stage
    return validate(skill)

register('monk','Monk','Chain close-range techniques into a powerful finishing strike, using footwork and defensive forms to stay alive.',
    monk_technique('rapid_palm','Rapid Palm','Three adjacent punches totaling 120% attack. Each landed punch adds 10% target vulnerability (maximum 30%) for three target turns; hits refresh it. Two landed punches guarantee Follow-up Ready; one has an 80% chance. Readiness lasts through your next two turns. Cooldown: 1 turn.',120,3,kind='opener'),
    monk_technique('iron_reversal','Iron Reversal','Requires Follow-up Ready. Adjacent 100% strike; a hit prepares the finisher and reduces the next direct attack against you by 20%, until your next turn, plus 25 evasion against the struck enemy for that window. Cooldown: 1 turn.',100,stage='follow_up',kind='follow_up'),
    monk_technique('heaven_piercing','Heaven-Piercing Strike','Requires Finisher Ready. Release a physical palm-force strike at 300% attack, up to three cells away with clear sight. Consumes readiness even on a miss. Cooldown: 3 turns.',300,cooldown=3,reach=3,stage='finisher',kind='finisher'))
def bard_active(key,name,description,effects,target='enemy',reach=6,rule='line_of_effect',cd=3,quick=False):
    skill=dict(id=key,name=name,description=description,type='active',source_kind='character',ability_version=1,
               self_only=False,target=target,range=reach,elevation_rule=rule,
               range_shape='diamond',cost={'cooldown':cd,'charges':None},effects=effects,
               bard_kind=key,quick_action=quick)
    return validate(skill)

def bard_song(key,name,description,no_linger=False,cd=1):
    skill=dict(id=key,name=name,description=description,type='active',source_kind='character',ability_version=1,
               self_only=True,target='ally',range=1,elevation_rule='physical_care',range_shape='diamond',
               cost={'cooldown':cd,'charges':None},effects=[{'type':'bard_song','song':key,'radius':1,'no_linger':no_linger}],bard_kind=key)
    skill['description'] += ' Main action to start or stop; walking is locked while performing. Maestro allows switching directly as a main action.'
    return validate(skill)

register('bard','Bard','Battlefield conductor: plant a performance space, command allies, and bend enemy priorities.',
    bard_active('jeering_verse','Jeering Verse','Long-range, non-resistable provocation. For two target activations the enemy must deliberately target the Bard when possible; both take 20% more direct incoming damage (not damage over time). Cooldown: 5 Bard activations.',[{'type':'bard_provoke','turns':2,'vulnerability_percent':20}],reach=6,cd=5),
    bard_active('cue_the_strike','Cue the Strike','Quick Action. Choose an allied character and a legal enemy target; the ally immediately makes a Basic Attack without spending its next activation. Use before your main action, including starting a Song, or on a later turn while already performing. The ally needs its normal weapon range and clear sight; no free movement. Cooldown: 4 Bard activations.',[{'type':'bard_command','kind':'cue_the_strike'}],reach=6,cd=4,quick=True),
    passive('battle_musician','Battle Musician','While performing a Song, you may still use your normal weapon attack. Attacking does not end the performance.',{}))
def druid_active(key,name,description,target='ally',reach=3,cd=5):
    shifting=key in {'prowler','bulwark','rat'}
    return validate(dict(id=key,name=name,description=description,type='active',source_kind='character',
        ability_version=1,self_only=shifting,target=target,range=1 if shifting else reach,
        elevation_rule='physical_care' if shifting else 'line_of_effect',range_shape='diamond',
        cost={'cooldown':0 if shifting else cd,'charges':None},effects=[{'type':'druid_spell','kind':key}],
        druid_kind=key,quick_action=shifting))

register('druid','Druid','Adaptive animal forms or regenerative nature control. One Quick Action form change per turn; animals cannot cast nature spells.',
    druid_active('prowler','Prowler Form','Quick Action, no cooldown. Transform into Prowler, or select again to return humanoid. One form change per activation. +2 movement, +20% damage dealt and received. Successful attacks apply 1 Bleed to an unbled target, otherwise double all existing Bleed. Shared HP; cannot cast nature spells in animal form.'),
    druid_active('rejuvenation','Rejuvenation','Restore 10% of an ally or your own maximum HP at each of their next three turn starts. No instant healing. Range 3; humanoid only. Cooldown 5.'),
    druid_active('bramble_wall','Bramble Wall','Place a horizontal or vertical three-cell living wall on empty ground within 3 cells. Blocks walking; all segments share 20% of your maximum HP. Lasts four caster turns. Once per completed movement beside it, an enemy takes a 20%-ATK lash with 50% Bind chance before resistance. Humanoid only. Cooldown 5.',target='enemy'))
def engineer_active(key,name,description,cd=0,quick=False):
    return validate(dict(id=key,name=name,description=description,type='active',source_kind='character',ability_version=1,
        target='enemy',range=3,elevation_rule='ballistic',cost={'cooldown':cd,'charges':None},
        effects=[{'type':'engineer_technique','kind':key}],engineer_kind=key,quick_action=quick))
register('engineer','Engineer','Prepare stationary machinery and explosives. Construction time and active deployment slots replace Components.',
    engineer_active('sentry_turret','Sentry Turret','Main action to begin; two further full working activations complete construction. Walking locked; hard control pauses work and displacement cancels it. Three active slots, refunded on destruction. 2 HP, armor equal to twice your ATK (minimum 30); armor piercing and damage over time apply normally. Automatic 75% ATK bolt at range 4 each owner turn, starting next turn after completion. Select a construction skill while building to cancel.'),
    engineer_active('dynamite','Dynamite','Main action. Throw within three cells; detonates at the start of your next turn. One-cell square blast hits allies and enemies for 200% ATK, pushes one cell and attempts 75% Stun; failed Stun attempts Hobble. One-turn cooldown begins on explosion, preventing a new throw that turn. Walls block blast.',1),
    engineer_active('rapid_assembly','Rapid Assembly','Quick preparation: walking remains available. Your next turret build this activation completes instantly. Cooldown 5 starts only when consumed; unused preparation expires freely.',5,True))

def summoner_active(key,name,description,cd=3,quick=False):
    return validate(dict(id=key,name=name,description=description,type='active',source_kind='character',
        ability_version=1,target='enemy',range=3,elevation_rule='line_of_effect',range_shape='diamond',
        cost={'cooldown':cd,'charges':None},effects=[{'type':'summoner_spell','kind':key}],summoner_kind=key,quick_action=quick))

register('summoner','Summoner','Autonomous creatures occupy real tiles and act after your turn, beginning on your next activation. Persistent orders and Reclaim are innate. Three Wisp capacity; the Companion costs none.',
    summoner_active('bound_companion','Bound Companion','Choose Fire, Earth or Grass; place within two cells. One companion, no capacity. Inherits half your stats: Fire uses full INT; Earth full Max HP and -25% direct damage; Grass full INT and Max HP, with INT-powered melee attacks and healing support. Active skill becomes Quick Reclaim. Five-turn replacement cooldown starts only when it dies or is reclaimed.',5),
    summoner_active('transposition','Transposition','Quick Action. Swap yourself and an owned summon, or two owned summons, at unlimited distance. Destinations must be legal. Commits your position and ends normal walking for this activation. Cooldown 3.',3,True),
    summoner_active('life_pact','Life Pact','Give up 25% of your maximum HP, rounded up, to heal one owned summon by that amount at any range. Cannot cast if the cost would leave you below 1 HP or the summon is uninjured. Main action; cooldown 2.',2))
def captor_active(key,name,description,cd=0,reach=1,quick=False):
    skill=active(key,name,description,[{'type':'status','status':'hobbled','turns':1}],target='ally' if key=='blitz' else 'enemy',range=reach,rule='ballistic' if reach>1 else 'melee',cooldown=max(1,cd))
    skill['cost']['cooldown']=cd
    skill.update(captor_kind=key,quick_action=quick,self_only=key=='blitz',effects=[{'type':'captor_technique','kind':key}])
    return validate(skill)

register('captor','Captor','Attack Resolve, isolate and restrain enemies to take them alive; ordinary attacks remain lethal.',
    captor_active('subduing_blow','Subduing Blow','Deal 150% Resolve damage, increased by isolation and unique control effects, with a 25% chance of one control effect.'),
    captor_active('bola','Bola','Throw a bola for Resolve damage and four Hobble stacks.',5,3),
    captor_active('hook_and_drag','Hook and Drag','Damage Resolve and pull an enemy toward you; Quick Action against Hobbled targets.',4,3))


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
    active('groundbreaker','Groundbreaker','Spend 4 Fury. Strike enemies in all eight adjacent cells at 200% attack power and push them one cell. Walls block the wave; knockback resistance and collision damage apply. Allies are safe. Target yourself. No cooldown; costs 4 Fury.',[{'type':'area_attack','radius':1,'push':1,'power_percent':200}],'ally',1,'physical_care',0,fury_cost=4),
    passive('too_angry_to_fall','Too Angry to Fall','Once per battle, lethal damage leaves you at 1 HP. Further lethal damage cannot finish you until your next turn begins. You do not automatically die afterward; another lethal hit is needed. Does not prevent capture or disappearing into a lethal pit.'))
SKILLS['job:barbarian:groundbreaker'].update(fury_cost=4,self_only=True)
later('bard',
    bard_song('accelerando','Accelerando','Song: one cell around you, including diagonals, with clear sight. Allies settled inside cast Channeling abilities immediately, with normal actions and cooldowns. NO LINGER: leaving or ending the Song removes the benefit.',True),
    bard_song('quickening_chorus','Quickening Chorus','Song: one cell around you, including diagonals, with clear sight. Settled allies recover one extra cooldown tick at the start of each turn; you do not benefit. The buff lasts through their next turn after leaving or the Song ending. Staying inside refreshes it.',False),
    bard_song('war_anthem','War Anthem','Song: one cell around you, including diagonals, with clear sight. Settled allies deal 20% more direct damage, excluding damage over time. The buff lasts through their next turn after leaving or the Song ending. Staying inside refreshes it.',False))

later('engineer',
    engineer_active('man_the_guns','Man the Guns','Quick Action. Mount an adjacent owned machine. Sentry fires at 125% of your ATK, Heavy at 200%, range 7. Use Attack to fire manually; no extra automatic shot. Aimed direct attacks hit the machine first; areas and hazards can hit you. Select again and choose an adjacent exit tile to leave. Walking ends this activation.',0,True),
    engineer_active('heavy_emplacement','Heavy Emplacement','Main action to begin; three further full working activations complete construction. One active emplacement; destruction frees its slot. 50% of your maximum HP. Range 7; 150% ATK primary bolt with half-power cardinal splash hitting everyone. Fires every second owner turn. Mount to fire each activation at 200% ATK.'),
    engineer_active('proximity_charge','Proximity Charge','Main action. Place on empty ground within two cells; two active mines maximum. Any unit entering its one-cell square radius detonates it, including allies and forced movement. Guaranteed Stun unless immune; movement stops and offensive actions are disrupted for that activation even if Stun is immune. Trap Expert bypasses triggering. Cooldown 4.',4))
later('summoner',
    summoner_active('wisp_swarm','Wisp Swarm','Choose three separate empty tiles within two cells. Three flying autonomous Wisps, 1 HP each and 40% of your INT as ranged attack power. Costs three capacity. Reclaim All Wisps is Quick. Six-turn replacement cooldown starts after the last Wisp dies or is reclaimed.',6),
    summoner_active('spirit_projection','Spirit Projection','Choose an enemy within three cells and clear sight. Each owned summon within two cells contributes one INT-based magical hit. Separate accuracy, defenses and Barrier apply to each hit. Main action; cooldown 6.',6),
    summoner_active('sacrifice','Sacrifice','Choose a 3 by 3 area within three cells. All your summons inside die, each exploding into the eight neighboring cells and its center for one ATK-based hit, including allies and you. Walls block explosions. Blind refreshes to three target turns. Overlapping explosions hit separately. Cooldown 3.',3))
later('captor',
    captor_active('abduct','Abduct','Drag a Hobbled enemy to a chosen position using a separate movement allowance and force its attention onto you.',4),
    captor_active('restraining_hold','Restraining Hold','Hold an isolated Hobbled enemy, dealing 75% Resolve damage each tick and attempting capture when Resolve is zero.',3),
    captor_active('blitz','Blitz','Gain three movement and 25 evasion for two turns; its two-turn cooldown begins afterward.',2,1,True))




def add_unlocks(job, entries):
    for threshold, original in entries:
        skill=deepcopy(original);skill['id']=f'job:{job}:{skill["id"]}';skill['source_name']=JOBS[job]['name']
        SKILLS[skill['id']]=skill
        JOBS[job].setdefault('unlocks',[]).append({'skill_id':skill['id'],'contracts':threshold})


add_unlocks('captor',[
    (12,captor_active('restraint','Restraint','Disarm and Hobble an adjacent enemy for two turns without fully immobilizing it.',3)),
    (16,passive('clean_capture','Clean Capture','Increase capture chance by your current HP percentage, up to double chance at full health.'))])
CAPTOR_DETAILS={
 'subduing_blow':'No cooldown. 150% Resolve power; cardinal isolation adds 100%, plus 50% each for unique Hobble, Disarm and Stun, up to 400%. A hit has 25% chance to select exactly one of those effects, then normal resistance applies.',
 'bola':'Range 3, cooldown 5. 100% Resolve power and four Hobble layers lasting four target activations; each layer checks normal Hobble resistance. Hobble never multiplies its movement penalty.',
 'hook_and_drag':'Range 3, cooldown 4. 75% Resolve power and a two-cell pull stopping beside you. Quick if the enemy was Hobbled before use; otherwise ends activation. Normal displacement resistance applies. No HP or collision damage.',
 'abduct':'Adjacent Hobbled enemy, cooldown 4, main action. Choose a legal destination; paired movement uses a separate allowance equal to your current maximum movement, including Blitz. Terrain, walls, occupants and hazards apply. Enemy deliberately targets only you for one activation.',
 'restraining_hold':'Adjacent isolated Hobbled enemy, main action. Consumes all Hobble layers to establish that many ticks, with no special cap. Initiation secures the Hold; each subsequent completed Captor activation deals 75% Resolve damage and makes one capture check if Resolve is zero. Captor is committed and target cannot act. Another adjacent unit, displacement, incapacitation or control breaks it. Release is free; cooldown 3 begins afterward.',
 'blitz':'Quick, self-targeted. +3 maximum movement and +25 evasion through your next activation; two-turn cooldown starts at the second following activation when Blitz expires.',
 'restraint':'Adjacent enemy, main action, cooldown 3. Attempt Disarm and Hobble for two target activations; successful Hobble limits movement to one cell. Disarm blocks basic and physical weapon attacks, not healing, defense or spells.',
 'clean_capture':'Passive. Final capture chance is multiplied by 1 + your current HP / maximum HP; full health doubles the chance. Base targets default to 35%, bosses/chieftains to 1%; capture gear quality and existing capture bonuses still apply. Maximum 95%.'
}
for _kind,_detail in CAPTOR_DETAILS.items():SKILLS['job:captor:'+_kind]['detailed_description']=_detail
for _kind in ('subduing_blow','bola','hook_and_drag'):
    SKILLS['job:captor:'+_kind]['detailed_description']+=' Every successful Resolve hit attempts capture if Resolve is zero afterward; a failed capture leaves the target conscious.'

add_unlocks('engineer',[
    (12,engineer_active('overclock','Overclock','Quick Action while mounted. Fire twice this activation and next activation. Cannot exit; machine breaks at the start of your second following turn. Cooldown 5 begins on expiry or early machine destruction.',5,True)),
    (16,engineer_active('scuttle_protocol','Scuttle Protocol','Main action to detonate a selected owned machine, mounted or not. Two-cell square explosion hits everyone for 50% of your maximum HP before mitigation, ignoring armor. This explosion alone leaves you at least 1 HP. If operating the machine, launch up to three cells toward your entry side; collision and hazards may still kill you. Cooldown 4.',4)),
])

add_unlocks('summoner',[
    (12,summoner_active('overload','Overload','At any range, triple one owned summon attack and maximum HP, preserving its current HP percentage. It dies at the start of your third following activation. Once per individual creature; cannot stack or refresh. Main action, no cooldown.',0)),
    (16,passive('rapid_conjuration','Rapid Conjuration','Bound Companion and Wisp Swarm become Quick Actions. Reclaim is already Quick. You may conjure then use Projection or Sacrifice in the same activation; creatures begin their own actions next owner turn.')),
])

add_unlocks('druid',[
    (2,druid_active('bulwark','Bulwark Form','Quick Action, no cooldown. One form change per activation; select your active form again to return humanoid. Movement 1; direct damage taken -25%; damage dealt +25%; successful hits have 75% chance to push one cell before resistance. Shares HP. Animals cannot cast nature spells.')),
    (5,druid_active('living_armor','Living Armor','For three upcoming target turn starts, heal an ally or yourself for 5% maximum HP. While active, take 25% less damage from all sources. Humanoid only; range 3. Cooldown 5.')),
    (9,druid_active('rat','Rat Form','Quick Action, no cooldown. One form change per activation; select again to return humanoid. +1 movement. Ordinary aimed attacks have only 10% hit chance; AoE and cannot-miss attacks bypass this evasion. ANY received HP damage kills you, including DoT, hazards and nonlethal hits; survival safeguards cannot save Rat. Rat attacks deal fixed 1 damage before Barrier absorption, regardless of attack bonuses or enemy armor. Animals cannot cast nature spells.')),
    (12,passive('natures_persistence',"Nature's Persistence",'Bramble Wall shares 50% of your maximum HP and lashes for 50% ATK; direct attackers gain 1 Bleed. Living Armor heals 7% for four target turn starts and gives direct attackers 1 Bleed once per attack action.')),
    (16,passive('wild_instinct','Wild Instinct','Prowler damage bonus becomes 25%; its first successful hit on each enemy adds one extra Bleed (2 on a fresh target), once per enemy per battle. Existing global Bleed still doubles. Bulwark deals 150% damage and pushes on 85% of hits before resistance. Rat hits have 75% chance to apply -25% ATK and +25% damage received for two target turns, refreshing rather than stacking.')),
])

add_unlocks('cleric', [
    (2,cleric_active('heal','Heal','Restore 40% of the target maximum HP at range three, with clear sight. Two charges per battle, no cooldown. Rest recovers charges.',charges=2)),
    (5,cleric_active('sanctuary','Sanctuary','Place a fixed 3 by 3 restoration zone at range three. Heals allies at their turn start for max(5, INT / 2 rounded down) HP. Lasts three caster turns; walls block its area. Burn prevents zone healing. One charge per battle, no cooldown. Overlapping Sanctuaries do not stack.',charges=1)),
    (9,cleric_active('smite','Smite','Quick Action. Weapon hits gain a separate INT-based holy magical component for three turns (this turn and your next two), with normal armor, magic resistance and Barrier. Commits your current position; remaining normal walking is limited to one tile this turn. Cooldown 5.',reach=1,cd=5,quick=True,self_only=True)),
    (12,passive('exorcist','Exorcist','Each successful direct attack against Undead, Revenants, Banshees or Vampires has a 25% chance to Stun for one target turn before selective resistance. Battle Priest raises this to 50%.')),
    (16,passive('battle_priest','Battle Priest','Take 15% less damage from all sources. Trade allied healing for self-sustain: Mend is self-only, cooldown 3; Heal restores 40% of your maximum HP, cooldown 5; Sanctuary becomes three-turn personal Regeneration, cooldown 6. No healing charges. Smite cooldown falls from 5 to 4; Exorcist chance rises from 25% to 50%. Rest still heals you but does not restore charges.')),
])

add_unlocks('bard', [
    (2, bard_song('song_of_peace','Song of Peace','Song: one cell around you, including diagonals, with clear sight. Ends automatically at the start of your second following turn. Everyone inside, including you, cannot initiate basic attacks or damaging skills. Movement and non-attack utility remain legal. Attacks initiated outside may enter or hit the area. NO LINGER: leaving or ending the Song removes the restriction. Cooldown: 5 of your turns.',True,cd=5)),
    (5, passive('maestro','Maestro','You may replace an active Song directly with another Song as your normal action. Stopping completely still costs one normal action.',{})),
])


add_unlocks('mage',[
    (2,mage_active('flash_freeze','Flash Freeze','Arm a two-cell diamond Freeze Zone. After your next activation, everyone still inside, including allies and yourself, rolls Freeze for two target turns. No channel: you may act normally. Direct HP damage breaks ice after its full hit; ending Freeze applies Wet for two turns. Resisted Freeze applies Wet immediately. Boss duration limits and selective resistance apply. Cooldown 4.',4)),
    (5,mage_active('enchant_weapon','Enchant Weapon','Choose Fire, Frost or Lightning for one ally, lasting two ally turns. Fire: one Burn per successful weapon hit. Frost: each hit rolls 20% Freeze before resistance. Lightning: each hit against Wet rolls 25% Paralysis for one turn; one successful paralysis per target per enchant. Multi-hit techniques roll per hit; selective control resistance applies. Replaces an existing enchant. Cooldown 5.',5,4,'ally')),
    (9,mage_active('singularity','Singularity','Two-cell diamond radius. Centre 200%, outer 25% attack power, then pull everyone affected, including allies and yourself, one cell toward the centre. Terrain, occupied cells, resistance and hazards apply; collisions deal half the hit. Cooldown 5.',5)),
    (12,passive('debuffer','Debuffer','Direct Mage spell damage is halved. Mage Burn applications add twice as many stacks; Wet, Blister and weapon enchantments last twice as long. Hard-control durations and terrain lifetimes are unchanged. Does not halve basic attacks, Burn ticks or ground damage.')),
    (16,mage_active('meteor','Meteor','Channel until your next activation. Impact hits everyone, including allies and yourself, and consumes that activation: inner two-cell diamond 400% attack, outer ring to three cells 300%. Applies Burn and leaves Scorched ground that burns everyone for two caster turns. Defeat, hard control, Mute or forced movement interrupts; ordinary damage does not. Enemies can leave the visible impact zone. Cooldown 6.',6)),
])

add_unlocks('ranger',[
    (2,ranger_active('multi_shot','Multi-Shot','Fire 2-4 arrows, each at 75% attack and 50% base accuracy. Your quarry guarantees every arrow hits. Poison imbue applies one stack per damaging arrow. Generic weapon procs have one volley budget. Cooldown 2.',power=75)),
    (5,ranger_active('rapid_fire','Rapid Fire','Quick Action. Select an enemy; randomly execute a currently usable equipped Ranger attack that can reach it, without spending the selected attack cooldown. Basic Attack fallback if none qualify. Commits and locks normal walking; your main action remains. Cooldown 4.',cd=4,quick=True)),
    (9,passive('sharpshooter','Sharpshooter','Finish a full turn without changing tiles to gain +10% damage and +2 attack/technique range. Lasts while you stay put. Committed or forced movement ends it; discarded movement previews do not.')),
    (12,ranger_active('pestilence_shot','Pestilence Shot','100% attack. A hit reduces target attack by 25% and increases damage it receives from ALL sources by 25%, including allied attacks and Poison/Bleed, for three target turns. Adds to other incoming-damage vulnerabilities. Cooldown 4.',cd=4)),
    (16,ranger_active('rupturing_blow','Rupturing Blow','150% attack. On a landed hit, consume all allied Poison and Bleed and immediately deal 50% of their remaining base damage, amplified by Pestilence. Remaining damage counts successive turn ends as one stack is removed each time. A miss consumes nothing. Cooldown 2.',power=150)),
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
BARD_OLD_IDS=dict(zip(('rally','discord','footwork','refrain','silence','cover'),
                      ('jeering_verse','cue_the_strike','battle_musician','accelerando','song_of_peace','war_anthem')))

def eligible(character):
    return character.get('source_kind') not in {'champion','celestial'} and not character.get('temporary_mercenary')

from .combat_skill_copy import summarize
for _skill in SKILLS.values():
    summarize(_skill)
    if _skill.get('engineer_kind') in {'rapid_assembly','overclock'}:_skill.update(self_only=True,target='ally')
    elif _skill.get('engineer_kind') in {'man_the_guns','scuttle_protocol'}:_skill['target']='ally'


def initialize(character):
    # Legacy characters opt in deliberately. No inferred class or equipment replacement.
    if eligible(character):
        character.setdefault('job_id',None)
        character.setdefault('learned_skills',[])
        character.setdefault('equipped_skills',[])
        character.setdefault('skill_slots',CAPACITY)
        character.setdefault('job_practice',0)
        character.setdefault('job_contract_credits',[])
        if character.get('job_id')=='captor' and character.get('captor_kit_version',0)<1:
            replacements={'bind':'bola','pull':'hook_and_drag','anchored':'clean_capture','field':'restraining_hold','dust':'restraint','coat':'blitz'}
            for field in ('learned_skills','equipped_skills','combat_skill_order'):
                if field in character:character[field]=list(dict.fromkeys('job:captor:'+replacements.get(k.split(':')[-1],k.split(':')[-1]) if k.startswith('job:captor:') else k for k in character[field]))
            for key in JOBS['captor']['starter_skills']:
                if key not in character['learned_skills']:character['learned_skills'].append(key)
            character['captor_kit_version']=1
        if character.get('job_id')=='barbarian':
            for field in ('learned_skills','equipped_skills'):
                character[field]=list(dict.fromkeys('job:barbarian:'+BARBARIAN_OLD_IDS.get(key.split(':')[-1],key.split(':')[-1]) if key.startswith('job:barbarian:') else key for key in character[field]))
        if character.get('job_id')=='engineer' and character.get('engineer_kit_version',0)<1:
            replacements={'turret':'sentry_turret','operate':'man_the_guns','calibration':'man_the_guns','trap':'proximity_charge','plate':'rapid_assembly','brace':'heavy_emplacement'}
            for field in ('learned_skills','equipped_skills','combat_skill_order'):
                if field in character:character[field]=list(dict.fromkeys('job:engineer:'+replacements.get(k.split(':')[-1],k.split(':')[-1]) if k.startswith('job:engineer:') else k for k in character[field]))
            for key in JOBS['engineer']['starter_skills']:
                if key not in character['learned_skills']:character['learned_skills'].append(key)
            character['engineer_kit_version']=1
            character['job_migration_note']='Engineer now uses construction time and active machinery slots. Prior choices mapped; practice and skill order preserved.'
        if character.get('job_id')=='mage' and character.get('mage_kit_version',0)<1:
            replacements={'embers':'fireball','ward':'enchant_weapon','footwork':'debuffer','binding':'flash_freeze','bind':'flash_freeze','scorch':'chain_lightning','armored':'debuffer'}
            for field in ('learned_skills','equipped_skills','combat_skill_order'):
                if field in character:character[field]=list(dict.fromkeys('job:mage:'+replacements.get(k.split(':')[-1],k.split(':')[-1]) if k.startswith('job:mage:') else k for k in character[field]))
            for key in JOBS['mage']['starter_skills']:
                if key not in character['learned_skills']:character['learned_skills'].append(key)
            character['mage_kit_version']=1
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
        if character.get('job_id')=='summoner' and character.get('summoner_kit_version',0)<1:
            replacements={'wolf':'bound_companion','wisps':'wisp_swarm','footwork':'rapid_conjuration','bulwark':'bound_companion','sprite':'life_pact','manifest':'spirit_projection'}
            for field in ('learned_skills','equipped_skills','combat_skill_order'):
                if field in character:character[field]=list(dict.fromkeys('job:summoner:'+replacements.get(k.split(':')[-1],k.split(':')[-1]) if k.startswith('job:summoner:') else k for k in character[field]))
            for key in JOBS['summoner']['starter_skills']:
                if key not in character['learned_skills']:character['learned_skills'].append(key)
            character['summoner_kit_version']=1
            character['job_migration_note']='Summons now act autonomously. Old selections mapped; practice and skill order preserved.'
        if character.get('job_id')=='druid' and character.get('druid_kit_version',0)<1:
            replacements={'thorns':'bramble_wall','rooted':'natures_persistence','sprite':'rejuvenation','bark':'living_armor'}
            for field in ('learned_skills','equipped_skills','combat_skill_order'):
                if field in character:character[field]=list(dict.fromkeys('job:druid:'+replacements.get(k.split(':')[-1],k.split(':')[-1]) if k.startswith('job:druid:') else k for k in character[field]))
            for key in JOBS['druid']['starter_skills']:
                if key not in character['learned_skills']:character['learned_skills'].append(key)
            character['druid_kit_version']=1
            character['job_migration_note']='Druid now uses persistent once-per-turn Quick Action forms and humanoid nature spells. Prior skills were mapped; earned practice and order remain.'
        if character.get('job_id')=='cleric' and character.get('cleric_kit_version',0)<1:
            replacements={'cleanse':'heal','steadfast':'exorcist','barrier':'smite','intercept':'holy_light'}
            for field in ('learned_skills','equipped_skills','combat_skill_order'):
                if field in character:
                    character[field]=list(dict.fromkeys('job:cleric:'+replacements.get(k.split(':')[-1],k.split(':')[-1]) if k.startswith('job:cleric:') else k for k in character[field]))
            for key in JOBS['cleric']['starter_skills']:
                if key not in character['learned_skills']:character['learned_skills'].append(key)
            character['cleric_kit_version']=1
            character['job_migration_note']='Cleric uses finite healing charges and Rest, or self-only cooldown healing with Battle Priest. Prior choices were mapped; earned practice is preserved.'
        if character.get('job_id')=='bard' and character.get('bard_kit_version',0)<1:
            for field in ('learned_skills','equipped_skills','combat_skill_order'):
                if field in character:
                    character[field]=list(dict.fromkeys('job:bard:'+BARD_OLD_IDS.get(key.split(':')[-1],key.split(':')[-1]) if key.startswith('job:bard:') else key for key in character[field]))
            for key in JOBS['bard']['starter_skills']:
                if key not in character['learned_skills']:character['learned_skills'].append(key)
            character['bard_kit_version']=1
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
