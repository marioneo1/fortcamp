"""Isolated beginner balance smoke run; does not load or write game saves.

Run from the checkout: .venv/Scripts/python tools/audit_beginner_combat.py
Auto-play results measure current AI, not the limits of human play.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend import combat
from backend.battle_lab import layout_presets
from backend.game import new_game
from backend.job_loadouts import JOBS

MISSIONS = ('rats_storehouse', 'roadside_toll', 'wolves_fence')


def basic_turn(battle, actor):
    """A legal attack-only probe: deliberately forgo techniques, not stats/gear."""
    targets = combat._visible_enemies(battle)
    if targets:
        target = min(targets, key=lambda u: (combat._distance(actor, u), u['hp']))
        if combat._auto_open_gate(battle, actor, target):
            return
        if not combat._can_attack(battle, actor, target):
            combat._move_toward(battle, actor, target)
        if combat._can_attack(battle, actor, target) and combat.bard.can_attack(actor):
            combat._perform_attack(battle, actor, target, actor['attack_elevation_rule'])
        else:
            combat._guard(battle, actor)
    else:
        combat._search_brush(battle, actor)
        return
    actor['acted'] = True
    combat._finish_turn(battle)


def run(seeds=2, races=('Human',), jobs=None, policy='auto', all_variants=False, missions=MISSIONS, radiant_seed=None):
    rows = []
    for race in races:
        for job in jobs or JOBS:
            for mission in missions:
                seed_keys = ([p['seed'] for p in layout_presets('contract:' + mission)]
                             if all_variants else [f'audit-{index}' for index in range(seeds)])
                if radiant_seed is not None: seed_keys=[radiant_seed]
                for seed_key in seed_keys:
                    state = new_game({'name': 'Audit', 'race': race, 'starting_role': job})
                    player = state['characters'][0]
                    player['loyalty'] = 100
                    if radiant_seed is None:
                        battle = combat.create_contract_battle(state, [player['id']], seed_key, mission, True)
                    else:
                        from backend import combat_radiant
                        battle = combat.create_battle(state,[player['id']],seed_key,'contract:'+mission,True)
                        if not combat_radiant.pending(battle): raise ValueError('Choose a seed that rolls the radiant encounter')
                        combat_radiant.choose(battle,'continue')
                    initial = battle['units'][player['id']]['max_hp']
                    error = None
                    try:
                        for step in range(40):
                            combat._advance_to_player(battle)
                            if battle.get('decision_pending') or battle['status'] != 'active':
                                break
                            actor = combat._current_unit(battle)
                            if actor and actor['team'] == 'player':
                                if policy == 'basic':
                                    basic_turn(battle, actor)
                                else:
                                    combat._player_auto_turn(battle, actor, 'balanced')
                            combat._check_end(battle)
                            battle['action_count'] += 1
                    except Exception as exc:
                        error = f'{type(exc).__name__}: {exc}'
                    rows.append(dict(race=race, job=job, mission=mission, seed=seed_key, policy=policy,
                                     variation=battle.get('map_variation'),
                                     won=bool(battle.get('battle_won')), status=battle['status'],
                                     rounds=battle['round'], starting_hp=initial,
                                     remaining_hp=battle['units'][player['id']]['hp'],
                                     enemies_remaining=len(combat._living(battle, 'enemy')), error=error))
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seeds', type=int, default=2)
    parser.add_argument('--all-variants', action='store_true',
                        help='Use every authored layout preset once per race/Job, instead of --seeds random samples.')
    parser.add_argument('--races', nargs='+', default=['Human'])
    parser.add_argument('--jobs', nargs='+')
    parser.add_argument('--missions', nargs='+', default=list(MISSIONS),
                        help='Explicit contracts to audit; direct creation excludes optional radiant encounters.')
    parser.add_argument('--radiant-seed', help='Exercise a same-map radiant entry using a known seed (74), instead of ordinary layouts.')
    parser.add_argument('--policy', choices=['auto', 'basic'], default='auto')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    rows = run(args.seeds, args.races, args.jobs, args.policy, args.all_variants, args.missions, args.radiant_seed)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(rows, indent=2), encoding='utf-8')
    for job in dict.fromkeys(row['job'] for row in rows):
        selected = [row for row in rows if row['job'] == job]
        print(f"{job}: {sum(row['won'] for row in selected)}/{len(selected)} wins; "
              f"mean rounds {sum(row['rounds'] for row in selected)/len(selected):.1f}")
