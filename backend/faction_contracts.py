"""Owner-only faction jobs and consequences of completed story arcs."""
from copy import deepcopy

CONTACT_JOBS = {
    'hedgerow': [
        ('watch_shared_signals', 6, 'E', 'A Signal Both Sides Trust', 'survival',
         'Two farms use the same warning signal for different dangers. Agree a code before the next patrol leaves.',
         'The farmers lay their lanterns on the table. One signal means wolves to the northern farm and raiders to the southern farm. The keeper needs a plan both can remember under pressure.'),
        ('watch_missing_patrol', 20, 'C', 'The Patrol That Did Not Return', 'survival',
         'A missing watch patrol left fresh tracks toward an occupied road. Find its notes and decide which warning to send.',
         'The last watch post is empty. Its basket still holds fresh bread, and a patrol ribbon is tied around the wrong branch. Someone moved the signal after the patrol passed.'),
        ('watch_horn_network', 45, 'B', 'Three Horns, One Road', 'combat',
         'A warhost officer has learned the watch signals. Break the command group before false warnings empty the farms.',
         'Three horns sound in the order the keeper taught the guild. No watch fire answers. The enemy has copied the code and is drawing every patrol away from the same road.'),
    ],
    'meridian': [
        ('meridian_shared_measure', 6, 'E', 'A Measure Worth Sharing', 'building',
         'A workshop instrument gives different readings to two apprentices. Establish a safe common measure.',
         'Both apprentices insist their instrument is right. The difference is small enough to miss until a fitted gate jams. The foreman asks for a test that neither apprentice can quietly adjust.'),
        ('meridian_stolen_governor', 20, 'C', 'The Missing Governor', 'building',
         'Raiders took the governor from a Meridian pump. Recover it before the unregulated engine damages the settlement.',
         'The pump runs too fast, then stops. Its governor was unbolted cleanly; this was theft, not a breakdown. Fresh cart marks lead toward a guarded salvage yard.'),
        ('meridian_unsafe_custodian', 45, 'B', 'The Custodian Who Would Not Stop', 'magic',
         'A workshop custodian refuses a shutdown order. Reach its control room and choose what to preserve.',
         'The custodian repeats the last production order while its housings split from heat. Armed scavengers hold the control room and insist the machine belongs to them now.'),
    ],
    'lantern': [
        ('lantern_fair_manifest', 6, 'E', 'Every Sack Accounted For', 'scavenging',
         'A missing sack has stopped a caravan payment. Reconcile the records without blaming the wrong porter.',
         'The wagon master has counted every sack twice. The porter has a receipt for a delivery the clerk never entered. Nobody will move the wagon until the numbers agree.'),
        ('lantern_diverted_wagon', 20, 'C', 'The Wagon on the Wrong Road', 'survival',
         'A supply wagon followed a forged route notice. Recover its dispatches and decide how to protect the remaining convoy.',
         'The route notice bears the caravan stamp but names a bridge that washed away last spring. Wheel tracks turn toward a makeshift toll camp. The convoy behind you still trusts that notice.'),
        ('lantern_toll_captain', 45, 'B', 'Who Collects the Second Toll?', 'combat',
         'An armed toll captain charges caravans twice and takes their guides. Stop the levy and recover the route book.',
         'The first toll bought safe passage. At the next bend, the same seal hangs over another gate. A guide recognizes the captain and asks the guild to bring back the route book intact.'),
    ],
}

STORY_JOBS = {
    'laid_hearse_to_rest': ('lantern', 'hearse_names_returned', 'C', 'The Names Left on the Road',
        'After the hearse was laid to rest, the caravan found burial tags at its old stopping places. Return them before collectors sell them as relics.',
        'The hearse is gone, but its last route is still marked by scraps of ribbon. The caravan has gathered the burial tags it could reach. Several are missing, and a roadside collector is charging families to see them.'),
    'broke_black_banner_court': ('hedgerow', 'banner_last_collectors', 'C', 'The Last Collection Order',
        'The court has fallen. Its remaining collectors still carry sealed orders and refuse to release the villages from their debts.',
        'The order is dated before the court fell. Its bearer knows that, but the villages do not. He has moved the collection table to a road where news arrives late.'),
    'mastered_meridian_engine': ('meridian', 'engine_overflow_ward', 'B', 'Where the Spare Current Goes',
        'The controlled engine has exposed an unsafe overflow route. Secure its regulator before anyone turns the surplus into a weapon.',
        'The engine obeys its keeper now. A smaller gauge still rises after every shutdown. The spare current is reaching a workshop that never appeared on the original plan.'),
    'restored_titan_roads': ('hedgerow', 'titan_road_tolls', 'C', 'A Road Wide Enough for Everyone',
        'The restored titan road is drawing settlers and toll raiders. Establish a safe crossing without blocking the migration.',
        'The titans have left a level road where the old track broke into gullies. Travelers follow it immediately. So do raiders, who have built their gate at its narrowest surviving bridge.'),
    'sealed_starless_treaty': ('meridian', 'treaty_return_beacon', 'B', 'A Light on This Side',
        'The Starless Treaty holds, but stranded travelers cannot find the agreed crossing. Secure a beacon site and choose how to mark it.',
        'The crossing is quiet. On this side of it, three travelers wait where the treaty map promised a light. Someone took the beacon lens while the guild was sealing the gate.'),
}

def job_definition(state, template_id):
    for fid, jobs in CONTACT_JOBS.items():
        for mid, threshold, rank, name, *_ in jobs:
            if mid == template_id:
                return {'faction': fid, 'relationship': threshold, 'rank': rank, 'name': name}
    for flag, (fid, mid, rank, name, *_) in STORY_JOBS.items():
        if mid == template_id:
            return {'faction': fid, 'relationship': 0, 'rank': rank, 'name': name, 'requires_flag': flag}
    return None

def available_jobs(state):
    jobs = []
    for fid, entries in CONTACT_JOBS.items():
        for mid, threshold, rank, name, *_ in entries:
            jobs.append({'id': mid, 'faction': fid, 'name': name, 'rank': rank, 'required_relationship': threshold,
                         'locked': state.get('factions', {}).get(fid, 0) < threshold,
                         'completed': bool(state.get('flags', {}).get('completed:' + mid))})
    for flag, (fid, mid, rank, name, *_) in STORY_JOBS.items():
        if state.get('flags', {}).get(flag):
            jobs.append({'id': mid, 'faction': fid, 'name': name, 'rank': rank,
                         'required_relationship': 0, 'locked': False,
                         'completed': bool(state.get('flags', {}).get('completed:' + mid)), 'story_consequence': True})
    ranks = ['E', 'D', 'C', 'B', 'A', 'S']
    for job in jobs:
        if ranks.index(state.get('mission_rank', 'E')) < ranks.index(job['rank']):
            job.update(locked=True, lock_reason=f"Unlock {job['rank']}-Rank")
        elif job['locked']:
            job['lock_reason'] = 'Build relationship'
    return jobs

def validate_request(state, template_id):
    definition = job_definition(state, template_id)
    if not definition or state.get('factions', {}).get(definition['faction'], 0) < definition['relationship']:
        raise ValueError('This contact has not offered you that contract')
    if definition.get('requires_flag') and not state.get('flags', {}).get(definition['requires_flag']):
        raise ValueError('That story has not reached this consequence')
    if state.get('flags', {}).get('completed:' + template_id):
        raise ValueError('You have already completed this personal agreement')
    ranks = ['E', 'D', 'C', 'B', 'A', 'S']
    if ranks.index(state.get('mission_rank', 'E')) < ranks.index(definition['rank']):
        raise ValueError(f"Unlock {definition['rank']}-Rank contracts at the Guild Hall first")
    return definition

def apply_faction_content(missions, items):
    from .mission_storylines import option
    from .tactical_contracts import TACTICAL_CONTRACTS
    records = [(fid, mid, rank, name, stat, premise, opening) for fid, entries in CONTACT_JOBS.items()
               for mid, threshold, rank, name, stat, premise, opening in entries]
    records += [(fid, mid, rank, name, 'survival' if fid != 'meridian' else 'building', premise, opening)
                for fid, mid, rank, name, premise, opening in STORY_JOBS.values()]
    for fid, mid, rank, name, stat, premise, opening in records:
        combat = rank != 'E'
        dc = {'E': 11, 'C': 15, 'B': 17}[rank]
        reward_id = mid + '_keepsake'
        skills = {
            'hedgerow': {'name': 'Steady the Line', 'range': 3, 'elevation_rule': 'line_of_effect', 'heal': 0, 'guard_ally': True,
                         'cleanses': ['fear'], 'description': 'One shared technique use per battle. Range 3, line of sight. Grant an ally Guard and remove Fear. No healing; cannot revive.'},
            'meridian': {'name': 'Ground the Discharge', 'range': 3, 'elevation_rule': 'line_of_effect', 'heal': 0,
                         'cleanses': ['bind', 'mute', 'freeze', 'paralyze'], 'description': 'One shared technique use per battle. Range 3, line of sight. Remove Bind, Mute, Freeze and Paralyze. No healing; cannot revive.'},
            'lantern': {'name': 'Roadside Treatment', 'range': 2, 'elevation_rule': 'physical_care', 'heal': 16,
                        'cleanses': ['bleed', 'poison'], 'description': 'One shared technique use per battle. Range 2, line of sight. Heal 16 + half INT HP; treat Bleed and Poison. Works while muted; cannot revive.'},
        }
        skill = {**skills[fid], 'id': mid + '_ward', 'target': 'ally', 'effect': 'support', 'scaling': 'int'}
        keepsake_names = {
            'watch_shared_signals': 'Shared-Signal Brooch', 'watch_missing_patrol': 'Patrolkeeper Lantern',
            'watch_horn_network': 'Three-Horn Gorget', 'meridian_shared_measure': 'True-Measure Gloves',
            'meridian_stolen_governor': 'Governor Grounding Band', 'meridian_unsafe_custodian': 'Custodian Shutdown Seal',
            'lantern_fair_manifest': 'Porter’s Honest Seal', 'lantern_diverted_wagon': 'Waybill Medic’s Wrap',
            'lantern_toll_captain': 'Free-Road Satchel', 'hearse_names_returned': 'Namesake Censer',
            'banner_last_collectors': 'Unlevied Watch Badge', 'engine_overflow_ward': 'Overflow Grounding Coil',
            'titan_road_tolls': 'Wide-Road Warden Boots', 'treaty_return_beacon': 'Return-Beacon Lens',
        }
        items[reward_id] = {'name': keepsake_names[mid],
            'slot': {'meridian_shared_measure': 'hands', 'titan_road_tolls': 'feet'}.get(mid, 'accessory'), 'rarity': 'rare' if rank == 'E' else 'epic', 'tags': ['mission_exclusive'],
            'bonuses': {}, 'attribute_bonuses': {}, 'granted_perks': [],
            'combat_rules': {'opening_guard': True} if fid == 'hedgerow' else {'resistances': ['lightning']} if fid == 'meridian' else {'carry_strength': 3},
            'combat_skill': skill, 'description': 'A keepsake from this agreement. Grants ' + skill['name'] + ' and ' + {'hedgerow': 'Guard at battle start.', 'meridian': 'lightning resistance.', 'lantern': 'three extra carrying strength.'}[fid],
            'icon': '/assets/catalogue/items/warding_token.png'}
        decision = {'start': 'meeting', 'nodes': {}}
        if not combat:
            decision['nodes']['meeting'] = {'title': name, 'text': opening, 'choices': {
                'practical': option('Work through the problem together', 'A practical check. A failed proposal can be revised instead of ending the talks.', stat=stat, dc=dc,
                    success={'next': 'agreement', 'text': 'The group tests the proposal rather than accepting another promise. The first result holds, and the contact asks how the guild will keep its side of the agreement.'},
                    failure={'next': 'revision', 'text': 'The demonstration exposes a gap. The contact gives the guild one chance to correct it before closing the meeting.'}),
                'leave': option('Leave the agreement open for another day', 'End this attempt without payment or rewards.', success={'finish': 'failure', 'text': 'The guild leaves without making a promise it cannot keep.'}),
            }}
            decision['nodes']['revision'] = {'title': 'A workable compromise', 'text': 'The contact has explained exactly where the proposal fails. Correcting it takes a new approach, not the same argument again.', 'choices': {
                'revise': option('Revise the plan using the shared records', 'INT check. Failure ends this attempt; your relationship is preserved.', stat='int', dc=dc+1,
                    success={'next': 'agreement', 'text': 'The revised plan gives each person a task they can check. The contact accepts it.'},
                    failure={'finish': 'failure', 'text': 'The second plan still depends on information nobody has. The contact postpones the agreement.'})}}
            decision['nodes']['agreement'] = {'title': 'The agreement', 'text': 'The work is ready to hand over. You can keep a copy for the guild or spend time checking the contact’s older records for another useful lead.', 'choices': {
                'finish': option('Hand over the agreed work', 'Complete the agreement without risking its payment.', success={'finish': 'success', 'text': 'The guild hands over its copy, receives the agreed fee, and leaves with a contact who has seen the work hold up in practice.'}),
                'records': option('Check the older records as well', 'INT check for a separate keepsake drop. Failure loses only that extra opportunity.', stat='int', dc=dc+2,
                    success={'finish': 'success', 'bonus': mid, 'text': 'An older entry explains why the original problem kept returning. The contact checks the field stores for a suitable token of thanks.'},
                    failure={'finish': 'success', 'text': 'The older entries add nothing reliable. The guild finishes the agreement and takes its ordinary payment.'})}}
        else:
            TACTICAL_CONTRACTS[mid] = {'race': 'Goblin' if fid == 'hedgerow' else 'Human',
                'layout': 'camp' if fid == 'meridian' else 'road', 'faction': 'raiders holding the contact’s route', 'enemy_count': 3 if rank == 'C' else 4, 'leader_target': True, 'caster': fid == 'meridian'}
            decision['nodes']['meeting'] = {'title': name, 'text': opening, 'choices': {
                'quiet': option('Find an unwatched approach', 'Survival check. Success gives three quiet preparation rounds; failure alerts the defenders.', stat='survival', dc=dc,
                    success={'battle': 'default', 'setup': 'ambush', 'after_battle': 'recovery', 'text': 'The party finds the camp during its rest watch and crosses the outer approach without waking anyone.'},
                    failure={'battle': 'default', 'setup': 'alert', 'after_battle': 'recovery', 'text': 'A sentry sees the party on the approach. The defenders take their positions.'},
                    critical_failure={'battle': 'default', 'boss': True, 'setup': 'alert', 'after_battle': 'recovery', 'text': 'The party enters the officer’s reserve post. A stronger commander closes the route.'}),
                'direct': option('Break the command group openly', 'Begin the battle normally. Defeat or subdue its commander and leave safely.',
                    success={'battle': 'default', 'after_battle': 'recovery', 'text': 'The party advances along the known route and forces the command group to answer.'}),
            }}
            decision['nodes']['recovery'] = {'title': 'What the fight left behind', 'text': 'With the command group stopped, the party can deliver the recovered records immediately. Several damaged pages might still reveal who sent the raiders; preserving them will take care.', 'choices': {
                'deliver': option('Deliver the recovered records', 'Keep the battle result and finish the agreement.', success={'finish': 'battle_outcome', 'text': 'The contact receives the records while they can still prevent another loss. The guild’s fee is counted out before the party leaves.'}),
                'restore': option('Preserve the damaged pages', 'INT check for a separate keepsake drop. Failure loses the extra lead, not your battle victory.', stat='int', dc=dc,
                    success={'finish': 'battle_outcome', 'bonus': mid, 'text': 'The recovered pages connect the raid to a route the contact can now protect. The contact checks for a useful token while the clerk counts the agreed fee.'},
                    failure={'finish': 'battle_outcome', 'text': 'The remaining ink cannot be saved. The usable records still reach the contact, and the guild keeps its battle victory.'})}}
        missions[mid] = {'name': name, 'description': premise, 'rank': rank, 'stat': stat, 'difficulty': dc,
            'party_size': {'E': 1, 'C': 2, 'B': 3}[rank], 'durations': [1], 'pool_weight': 0, 'chain_only': True,
            'faction': fid, 'mission_form': 'diplomacy' if not combat else 'investigation', 'resolution_mode': 'choices → tactical' if combat else 'choices',
            'audited': True, 'objective': premise, 'reward_rolls': [],
            'world_context': opening, 'encounter_plan': {'mode': 'branching' if combat else 'dialogue', 'combat': 'expected' if combat else 'unknown'},
            'decision_scene': decision, 'claim_requirements': [], 'modifiers': [], 'critical_any': [], 'special_events': [], 'pays_gold': True,
            'rewards': {'world_flag': {'id': 'completed:' + mid, 'name': 'Fulfilled ' + name}}, 'critical_rewards': {},
            'reward_preview': ['Agreed guild fee', 'Improved faction relationship', 'Possible personal keepsake'],
            'visible_hints': ['Your contact has offered this agreement personally.'],
            'bodyguard_slots': 1 if not combat else 0,
            'combat_encounter': {'id': 'contract:' + mid, 'name': name} if combat else None,
            'combat_critical_condition': 'Capture the commander alive, secure the field, and keep every party member standing.' if combat else None,
            'narrative': {'approach': opening, 'success': 'The agreement gives the contact something they can use immediately. The guild returns with its payment and a clearer place in the route’s affairs.',
                          'critical_success': 'The contact can settle the immediate problem and prevent its return. The guild leaves with the full result intact.',
                          'failure': 'The contact cannot rely on the unfinished work. The agreement stays open for another attempt.',
                          'critical_failure': 'The expedition cannot complete the agreement. The surviving party returns to camp to recover.'}}
        from .mission_loot import SCENE_BONUSES
        SCENE_BONUSES[mid] = {'source': 'personal agreement keepsake', 'chance': 12 if rank == 'E' else 18, 'critical_bonus': 7,
                             'reward': {'item': reward_id}}
