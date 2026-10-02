"""Ordinary contracts with explicit optional risks and post-fight decisions."""
def apply_branches(missions):
    from .mission_storylines import option
    from .tactical_contracts import TACTICAL_CONTRACTS
    from .mission_loot import SCENE_BONUSES
    records = {
        'caravan_account': ('The receipt that does not match',
            'The caravan register lists the same sack on two wagons. One porter has a stamped receipt; another says the clerk copied yesterday’s list. The guild can settle the count here or follow the disputed delivery.',
            'scavenging', 'Follow the disputed delivery',
            'The receipt names a roadside store where the cargo was sold twice. Fresh wagon marks still reach its door.',
            'The store’s guards refuse to release the records. The party must fight or leave the missing cargo unproved.',
            'A paid collector was waiting for anyone who checked the receipt. His command group blocks the return road.',
            'The recovered receipts', 'The store is no longer holding the records. The clerk can settle the cargo count with what you have; checking the second book may also identify the person who altered the list.',
            'caravan_ledger_seal', 'Human', 'road'),
        'waystation_wards': ('A ward around an occupied room',
            'A damaged ward runs through the wall of a room that is still occupied. Its keeper can close the room for a routine repair, but an unfamiliar mark beneath the floor may explain why the damage keeps returning.',
            'magic', 'Inspect the buried mark',
            'The buried mark draws power from the wrong boundary. Disconnecting it lets the main ward settle without switching off the room.',
            'Removing the floor mark exposes a watched entrance. The people using it move to silence the investigation.',
            'The mark is an alarm. Its keeper arrives with an armed reserve while the party is still beside the open floor.',
            'The ward’s second boundary', 'The occupants can use the room again. The removed mark bears a maker’s number that could warn another waystation, if the party can read it without reactivating the circuit.',
            'cleansing_salts', 'Human', 'ruin'),
        'watch_negotiation': ('Who covers the empty road?',
            'The watch can protect the fields or the ferry tonight, but not both with its current patrol. The ferryman offers an older route map. The keeper suspects somebody has marked a safer crossing that no longer exists.',
            'survival', 'Check the disputed crossing first',
            'The old crossing is gone, but a newer path reaches the ferry without leaving the fields unobserved. The keeper can use the revised route.',
            'Raiders are using the abandoned crossing as a camp. They move to stop the party before it can warn the keeper.',
            'The map led to the raiders’ command post. Their officer calls the reserve across the ford.',
            'The warning route', 'The watch has enough information to move its patrol safely. A captured signal strip could help expose the raiders’ next destination, but only if it is read correctly.',
            'watch_ford_medallion', 'Goblin', 'road'),
        'meridian_calibration': ('An instrument with two zeroes',
            'The workshop instrument returns to a different zero after every test. A routine calibration will make it usable today; following the error into its supply line may uncover the cause.',
            'building', 'Trace the error to the supply line',
            'The supply line contains a borrowed regulator set to a different measure. The party marks the mismatch and brings the instrument back to a stable zero.',
            'A salvage crew has taken control of the regulator yard. They block access when the party starts checking the line.',
            'The regulator belongs to the yard’s armed custodian. Its reserve crew closes the gate around the investigators.',
            'The regulator’s test record', 'The instrument works again. Its old test plate has an unused setting that might be valuable to the artificers; a careless reading will only ruin the optional plate.',
            'calibrators_focus', 'Human', 'camp'),
    }
    for mid, (title, opening, stat, risk_label, clean, fight, disaster, closing_title, closing, item, race, layout) in records.items():
        m = missions[mid]
        dc = 12 if m['rank'] == 'D' else 15
        key = 'branch:' + mid
        SCENE_BONUSES[key] = {'source': 'preserved contract evidence', 'chance': 10, 'critical_bonus': 5, 'reward': {'item': item}}
        # Faction-exclusive shop equipment must stay in trade, not become a quest cache.
        if item == 'watch_ford_medallion':
            SCENE_BONUSES[key]['reward'] = {'item': 'field_dressing'}
        TACTICAL_CONTRACTS[mid] = {'race': race, 'layout': layout, 'faction': 'guards at the disputed site', 'enemy_count': 2 if m['rank'] == 'D' else 3, 'leader_target': True}
        m['decision_scene'] = {'start': 'problem', 'nodes': {
            'problem': {'title': title, 'text': opening, 'choices': {
                'routine': option('Finish the ordinary work', 'A practical check. Success completes the contract; failure loses the fee. No optional encounter on this route.', stat=stat, dc=dc-2,
                    success={'finish': 'success', 'text': 'The party handles the immediate problem and leaves the disputed route for another day. The contact accepts the completed work.'},
                    failure={'finish': 'failure', 'text': 'The ordinary work cannot be completed with the information at hand. The contact withholds the fee.'}),
                'trace': option(risk_label, 'A practical check. Failure can bring opposition; a critical failure draws its stronger commander.', stat=stat, dc=dc+1,
                    success={'next': 'evidence', 'text': clean},
                    failure={'battle': 'contract:' + mid, 'after_battle': 'evidence_after_fight', 'text': fight},
                    critical_failure={'battle': 'contract:' + mid, 'boss': True, 'after_battle': 'evidence_after_fight', 'text': disaster}),
            }},
        }}
        for node, finish in [('evidence', 'success'), ('evidence_after_fight', 'battle_outcome')]:
            m['decision_scene']['nodes'][node] = {'title': closing_title, 'text': closing, 'choices': {
                'deliver': option('Deliver what is already reliable', 'Finish without risking an optional discovery.', success={'finish': finish, 'text': 'The contact receives the usable evidence before another decision depends on it. The guild keeps its agreed result.'}),
                'preserve': option('Check the remaining evidence', 'INT check for a separate item drop. Failure loses only the optional discovery.', stat='int', dc=dc,
                    success={'finish': finish, 'bonus': key, 'text': 'The last record confirms a detail the contact can act on. They offer something from their field stores in thanks.'},
                    failure={'finish': finish, 'text': 'The last record cannot be read reliably. The guild delivers the sound evidence and leaves the speculation out.'})}}
        m.update(resolution_mode='choices', bodyguard_slots=1, encounter_plan={'mode': 'branching', 'combat': 'possible'},
                 combat_critical_condition='Capture the commander alive, secure the field, and keep every party member standing.')
    # Existing beginner gathering branches now continue after fighting to a real handover.
    for mid in ('timber_creek', 'tool_shed', 'herbs_wall'):
        m = missions[mid]
        m['decision_scene']['nodes']['approach']['choices']['risk']['success']['after_battle'] = 'handover'
        text = {'timber_creek': 'The guarded timber is reachable now. The party can take it straight home or inspect the bindings for reusable fittings.',
                'tool_shed': 'The scavengers no longer block the shed. The tool rack is exposed; a few sealed drawers survived beneath it.',
                'herbs_wall': 'The garden gate is open. Most of the healthy plants are within reach now, but a small labeled box remains behind the healer’s old bench.'}[mid]
        key = 'gather:' + mid
        SCENE_BONUSES[key] = {'source': 'careful site recovery', 'chance': 30, 'critical_bonus': 10,
                             'reward': {'item': 'field_dressing' if mid == 'herbs_wall' else 'training_manual'}}
        m['decision_scene']['nodes']['handover'] = {'title': 'Before leaving the site', 'text': text, 'choices': {
            'return': option('Bring the recovered supplies home', 'Finish with the battle result and ordinary supplies.', success={'finish': 'battle_outcome', 'text': 'The party secures the useful load and leaves before another group can occupy the site.'}),
            'inspect': option('Inspect the sheltered stores', 'Scavenging check for an extra drop. Failure keeps the battle result.', stat='scavenging', dc=10,
                success={'finish': 'battle_outcome', 'bonus': key, 'text': 'The sheltered stores contain something still fit for field use. The party packs it separately from the main load.'},
                failure={'finish': 'battle_outcome', 'text': 'The sheltered stores have spoiled. The party leaves them and brings the sound supplies home.'})}}
