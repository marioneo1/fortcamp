"""Paired, isolated combat trials. Never writes game state or patches runtime code."""
import csv
from copy import deepcopy
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import combat
from backend.battle_lab import layout_presets
from backend.combat_pacing import scaled
from backend.game import new_game
from backend.combat_stats import HP_BASE, ATTACK_BASE
from backend.recruit_perks import ATTRIBUTES as PERK_ATTRIBUTES
from tools.compare_character_growth import ATTRS, project

MODES = {'live': None, 'shared24': (24, 5), 'shared12': (12, 2)}
JOBS = ('fighter', 'barbarian', 'monk', 'rogue', 'ranger', 'mage')
MISSIONS = ('roadside_toll', 'highway_ambush', 'bone_patrol')


def prepare_trial(original, state, mode, rank):
    """Return an independent battle; flat gear/Job bonuses remain unscaled."""
    battle = deepcopy(original)
    if mode == 'live':
        return battle
    hp_base, attack_base = MODES[mode]
    characters = {c['id']: c for c in state['characters']}
    for unit in battle['units'].values():
        if unit['team'] == 'player':
            character = characters[unit['id']]
            body = character['attributes']
            full = {k: combat._effective_attribute(state, character, k) for k in ATTRS}
            roll = unit.get('battle_attribute_roll')
            if roll:
                full[roll['attribute']] = max(1, full[roll['attribute']] + roll['amount'])
            effective = {k: scaled(body[k], rank) + full[k] - body[k] for k in ATTRS}
            weapon = combat._equipped_weapon(state, character)
            scaling = 'str' if weapon.get('capture_weapon') else weapon.get('weapon_scaling', 'str')
            before = project(full, race=unit['race'], scaling=scaling, hp_base=HP_BASE, attack_base=ATTACK_BASE)
            after = project(effective, race=unit['race'], hp_base=hp_base,
                            attack_base=attack_base, scaling=scaling)
            # Difference preserves actual starter gear, combat training, race and Job bonuses.
            new_hp = max(1, unit['max_hp'] + after['hp'] - before['hp'])
            new_attack = max(1, unit['attack'] + after['attack'] - before['attack'])
            unit['armor'] = max(0, unit['armor'] + after['armor'] - before['armor'])
            unit['move'] = max(1, unit['move'] + after['move'] - before['move'])
            unit['initiative'] += effective['agi'] - full['agi']
        elif unit.get('recruitable_snapshot'):
            data = unit.get('rank_scaling', {})
            enemy_rank = data.get('rank', 'E')
            body = data.get('attribute_baseline')
            if enemy_rank != 'E' and body is None:
                raise ValueError('Missing pre-rank enemy body')
            body = body or unit['recruitable_snapshot']['attributes']
            scaling = 'dex' if unit['recruitable_snapshot']['job_id'] == 'ranger' else 'str'
            bonuses = dict.fromkeys(ATTRS, 0)
            for perk in unit.get('origin_perks', []):
                for key, value in PERK_ATTRIBUTES.get(perk, {}).items():
                    bonuses[key] += value
            roll = unit.get('battle_attribute_roll')
            if roll:
                bonuses[roll['attribute']] += roll['amount']
            ranked = {k: max(1, scaled(body[k], enemy_rank) + bonuses[k]) for k in ATTRS}
            after = project(ranked, 'E', unit['race'], hp_base, attack_base, scaling)
            effective = after['attributes']
            modifiers = unit.get('perk_modifiers', {})
            new_hp, new_attack = max(1, after['hp'] + modifiers.get('hp', 0)), after['attack']
            unit['armor'] = max(0, after['armor'] + modifiers.get('armor', 0))
            # Retain authored enemy role mobility/range and resistances, including mounted roles.
        else:
            continue
        delta = new_attack - unit['attack']
        for skill in unit.get('skills', []):
            if 'attack' in skill:
                skill['attack'] = max(1, skill['attack'] + delta)
        if unit.get('special') and 'attack' in unit['special']:
            # A special may alias a skill; it has already received its delta in that case.
            if not any(unit['special'] is skill for skill in unit.get('skills', [])):
                unit['special']['attack'] = max(1, unit['special']['attack'] + delta)
        unit.update(hp=new_hp, max_hp=new_hp, attack=new_attack,
                    strength=effective['str'], agility=effective['agi'], intelligence=effective['int'],
                    dexterity=effective['dex'], vitality=effective['vit'], luck=effective['luk'])
    # Re-sort for projected initiative; do not carry over an old activation stamp.
    order_key = 'turn_order' if 'turn_order' in battle else 'order'
    if order_key in battle:
        battle[order_key].sort(key=lambda uid: -battle['units'][uid]['initiative'])
        battle['turn_index'] = 0
    return battle


def opening_damage(battle, attacker_id, target_id):
    probe = deepcopy(battle)
    attacker, target = probe['units'][attacker_id], probe['units'][target_id]
    # Damage resolver only: excludes accuracy/distance legality, tested during full fights.
    combat._deal_damage(probe, attacker, target)
    return target['max_hp'] - target['hp']


def run_trial():
    rows = []
    for mission in MISSIONS:
        rank = 'E' if mission == 'roadside_toll' else 'D'
        for preset in layout_presets('contract:' + mission):
            for job in JOBS:
                state = new_game({'name': 'Trial', 'starting_role': job,
                                  'attributes': dict.fromkeys(ATTRS, 6)})
                ally = deepcopy(state['characters'][0])
                ally.update(id='ally', name='Partner', is_player=False, loyalty=100)
                state['characters'].append(ally)
                base = combat.create_contract_battle(state, ['player', 'ally'], preset['seed'], mission, True)
                for mode in MODES:
                    battle = prepare_trial(base, state, mode, rank)
                    enemies = [u for u in battle['units'].values() if u['team'] == 'enemy']
                    enemy = enemies[0]
                    player = battle['units']['player']
                    row = dict(mission=mission, layout=preset['id'], job=job, mode=mode,
                               player_hp=player['max_hp'], player_attack=player['attack'], player_armor=player['armor'],
                               enemy_hp=enemy['max_hp'], enemy_attack=enemy['attack'], enemy_armor=enemy['armor'],
                               outgoing=opening_damage(battle, 'player', enemy['id']),
                               incoming=opening_damage(battle, enemy['id'], 'player'))
                    try:
                        for step in range(160):
                            if battle['status'] != 'active':
                                break
                            combat.auto_step(battle)
                        row.update(outcome=battle.get('outcome') or 'stalled', rounds=battle['round'], error='')
                    except Exception as exc:
                        row.update(outcome='error', rounds=battle['round'], error=f'{type(exc).__name__}: {exc}')
                    party = [u for u in battle['units'].values() if u['team'] == 'player' and not u.get('temporary')]
                    row['surviving_allies'] = sum(bool(u.get('alive') and u.get('conscious')) for u in party)
                    row['party_hp_remaining_percent'] = round(100 * sum(max(0, u['hp']) for u in party) / sum(u['max_hp'] for u in party), 1)
                    rows.append(row)
            print(f"Completed {mission} / {preset['id']}: {len(rows)} trials", flush=True)
    return rows


def write_report(rows):
    destination = ROOT / 'docs/design/CHARACTER_GROWTH_TRIAL.csv'
    with destination.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    lines = ['# Shared-stat combat trial', '',
             'Offline experiment, October 9, 2026. No game saves, runtime formulas, server or production changes.', '',
             '## Method', '',
             'Three missions × four authored layouts × six starter Jobs × three formula arms = 216 paired fights. Two Human allies use legal 36-point all-6 bodies and actual starter equipment/skills. Each arm clones the same opening and seed. No growth advancement is invented for these bodies.', '',
             '- **live:** current player formulas and authored enemies; current players have no personal rank scaling.',
             '- **shared24:** shared bases 24 HP / 5 Attack; allocate attributes then apply E/D rank once.',
             '- **shared12:** shared bases 12 HP / 2 Attack; otherwise same as shared24.', '',
             'Player attribute gear bonuses and flat gear/training/Job bonuses are retained after body rank scaling. Enemies use recorded pre-rank recruit bodies, with no invented weapon power or combat-training bonus; their existing skills, perks, statuses and resistances remain. Enemy Armor is derived anew, so authored role-specific armor overrides are removed in both shared arms. Enemy role movement/range remains authored. This tests the untouched allocations, not optimized reconstructions or final equipment assignments.', '',
             'Cached skill Attack values receive the actor Attack delta; bespoke spell/heal/summon formulas are not rewritten. Full fights use existing targeting, hit rolls, AI, skill/status/damage resolution and termination rules. Opening damage columns call the real damage resolver on separate clones, bypassing hit/range checks; they mean damage **if the hit connects**, not expected DPS.', '',
             '## Results', '',
             '| Mission | Arm | Wins / fights | Failures | Stalls / errors | Mean rounds | Mean opening outgoing / incoming | Mean allies surviving |',
             '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for mission in MISSIONS:
        for mode in MODES:
            group = [r for r in rows if r['mission'] == mission and r['mode'] == mode]
            wins = sum(r['outcome'] in ('success', 'critical_success', 'victory') for r in group)
            failures = sum(r['outcome'] not in ('success', 'critical_success', 'victory', 'stalled', 'error') for r in group)
            bad = sum(r['outcome'] in ('stalled', 'error') for r in group)
            lines.append(f"| {mission} | {mode} | {wins}/{len(group)} | {failures} | {bad} | {statistics.mean(r['rounds'] for r in group):.1f} | {statistics.mean(r['outgoing'] for r in group):.1f} / {statistics.mean(r['incoming'] for r in group):.1f} | {statistics.mean(r['surviving_allies'] for r in group):.2f} / 2 |")
    lines += ['', 'Per-fight opening stats, damage, outcomes, rounds and errors: [CSV](CHARACTER_GROWTH_TRIAL.csv).', '',
              '## Limits', '',
              'Auto-play measures these starter-loadout heuristics, not human balance or support effectiveness. Human-only, two-character parties; no bosses, Ogre/Fairy, advanced equipment, all Jobs, high Growth or S-rank encounters covered. One fixed seed per layout is a small paired sample. Opening damage is not a skill rotation or survival probability. Victory rates cannot determine a global formula alone.', '',
              'Personal D-rank in shared arms is itself a new feature; live D players are still E-stat bodies. Consequently comparisons with live combine formula parity and proposed personal rank advancement. The two shared arms isolate the fixed-base choice. Before migration, reconstruct actual enemy gear/perks and role armor coherently, then rerun wider-race/manual trials.', '']
    (ROOT / 'docs/design/CHARACTER_GROWTH_TRIAL.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    if (HP_BASE, ATTACK_BASE) != (24, 5):
        raise SystemExit('Pre-migration trial archived. Use tools/audit_shared_combat_stats.py for current runtime; historical reports are retained.')
    write_report(run_trial())
