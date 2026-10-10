"""Offline design comparison; never changes saves, encounters or runtime formulas."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.combat_pacing import scaled
from backend.races import race_gameplay

ATTRS = ('str', 'dex', 'agi', 'vit', 'int', 'luk')


def allocation_cost(attributes, graduated=False):
    """Full budget, including minimum attributes; costs apply before rank."""
    def cost(value):
        if value < 1:
            raise ValueError('Allocated attributes must be positive')
        if not graduated:
            return value
        return min(value, 10) + 2 * max(0, min(value, 15) - 10) + 3 * max(0, value - 15)
    return sum(cost(attributes[key]) for key in ATTRS)


def project(attributes, rank='E', race='Human', hp_base=24, attack_base=5,
            scaling='str', weapon_power=0, training=0):
    """Controlled naked-body probe, not full combat resolution or spell damage."""
    effective = {key: scaled(attributes[key], rank) for key in ATTRS}
    racial = race_gameplay(race)
    return dict(
        attributes=effective,
        hp=max(8, round((hp_base + 4 * effective['vit']) * racial['hp_multiplier']) + racial['hp_bonus']),
        attack=attack_base + effective[scaling] // 2 + weapon_power + training,
        armor=max(0, effective['vit'] // 3 + racial['armor_bonus']),
        move=max(1, min(8, 3 + (effective['agi'] >= 8) + racial['move_bonus'])),
    )


def allocate(budget, weights, graduated):
    """Repeatable illustrative builds: distribute toward stated priorities."""
    attributes = dict.fromkeys(ATTRS, 4)
    if budget < allocation_cost(attributes, graduated):
        raise ValueError('Budget cannot cover the illustrative starting body')
    while True:
        key = min(ATTRS, key=lambda k: ((attributes[k] - 4) / weights[k], ATTRS.index(k)))
        candidate = dict(attributes)
        candidate[key] += 1
        if allocation_cost(candidate, graduated) > budget:
            return attributes
        attributes = candidate


def samples():
    # Create isolated previews from current code; no API, save or command execution.
    from backend import combat
    from backend.battle_lab import layout_presets
    from backend.game import new_game
    for mission in ('roadside_toll', 'goblin_pickpockets', 'highway_ambush', 'bone_patrol', 'goblin_boar_riders'):
        presets = layout_presets('contract:' + mission)
        battle = combat.create_contract_battle(new_game({'name': 'Offline comparison'}), ['player'], presets[0]['seed'], mission, True)
        for unit in battle['units'].values():
            recruit = unit.get('recruitable_snapshot')
            if unit.get('team') != 'enemy' or not recruit:
                continue
            rank_data = unit.get('rank_scaling', {})
            rank = rank_data.get('rank', 'E')
            baseline = rank_data.get('attribute_baseline')
            if rank != 'E' and baseline is None:
                raise ValueError('Ranked recruit lacks an unranked baseline: ' + unit['id'])
            yield mission, unit, dict(baseline or recruit['attributes']), rank


def profile_text(profile):
    return f"{profile['hp']} / {profile['attack']} / {profile['armor']}"


def report():
    lines = ['# Character growth comparison', '',
             'October 9, 2026. Offline proposal: no live stats, saves, ranks or equipment changed.', '',
             '## Encounter formula comparison', '',
             'Current opponents use authored combat stats. These projections retain their unranked recruit allocation and apply Adventurer Rank once before deriving stats. Growth stage is deliberately unassigned: a stat total cannot prove a completed advancement.', '',
             'All values below are **HP / Attack / Armor**. Projections include current racial HP/Armor, but exclude gear, training, perks and Job bonuses. They use STR for melee and DEX for Ranger. Thus they are body probes, not complete reconstructed enemy kits. Current encounters retain all their existing modifiers.', '',
             'A uses current player bases: HP = 24 + 4×VIT; Attack = 5 + scaling attribute÷2, rounded down. B is an **unapproved global experiment** with bases 12 and 2; it is not an enemy-only discount.', '',
             '| Mission / role | Race / Rank | Base allocation STR/DEX/AGI/VIT/INT/LUK | Budget | Current encounter | A | B |',
             '| --- | --- | --- | --- | --- | --- | --- |']
    for mission, unit, attributes, rank in samples():
        race = unit.get('race', 'Human')
        scaling = 'dex' if unit['recruitable_snapshot'].get('job_id') == 'ranger' else 'str'
        a = project(attributes, rank, race, scaling=scaling)
        b = project(attributes, rank, race, hp_base=12, attack_base=2, scaling=scaling)
        old = dict(hp=unit['max_hp'], attack=unit['attack'], armor=unit['armor'])
        allocation = '/'.join(str(attributes[k]) for k in ATTRS)
        lines.append(f"| {mission}: {unit.get('combat_specialization', unit['name'])} | {race} / {rank} | {allocation} | {allocation_cost(attributes)} | {profile_text(old)} | {profile_text(a)} | {profile_text(b)} |")
    lines += ['', '### What this means', '',
              '- Current player formulas have a Human HP floor of 28 at VIT 1, and an untrained/unarmed Attack floor of 5. Allocation and Growth labels alone cannot reproduce the lighter enemies below those floors.',
              '- B moves enemies closer to current encounters, but also weakens players: an all-6 Human goes from 48 HP / 8 Attack to 36 HP / 5 Attack at E. At S it goes from 84 / 12 to 72 / 9. Gear and training add afterward; these are not final player builds.',
              '- Neither formula preserves the original 1.3× combat outputs at D. Attribute-first scaling intentionally scales only attribute contributions; fixed bases and weapon power do not receive that multiplier.',
              '- Keep current encounters until a shared formula and player baseline are approved. Then rebuild coherent allocations and equipment together, preserve kits/range/movement identity, and run all-layout fights. Do not hide residual mismatches in unexplained encounter multipliers.', '',
              '## Allocation costs at S rank', '',
              'Five E→S Growth advances of +4–6 yield budgets 56–66 from the starting 36; 61 is the average, not a cap. These examples use current player bases, Human race, no gear/training/perks, and S rank ×2.5 applied once. No existing creator ceiling is imposed: raising it would be part of a future implementation.', '',
              'Linear: every raw attribute costs 1. Graduated: 1 through 10, 2 for 11–15, 3 above 15. All current legal creator builds retain their existing cost. Priorities are illustrative rather than optimized; exact distribution is reproducible in the tool.', '',
              '| Build | Budget (spent) | Costs | Base STR/DEX/AGI/VIT/INT/LUK | HP / Attack / Armor | Move |',
              '| --- | --- | --- | --- | --- | --- |']
    builds = {
        'Tank': ((2, 1, 1, 5, 1, 1), 'str'),
        'Melee DPS': ((5, 1, 2, 2, 1, 1), 'str'),
        'Marksman': ((1, 5, 2, 2, 1, 1), 'dex'),
        'Caster': ((1, 1, 2, 2, 5, 1), 'int'),
    }
    for name, (weights, scaling) in builds.items():
        for budget in (56, 61, 66):
            for graduated in (False, True):
                attributes = allocate(budget, dict(zip(ATTRS, weights)), graduated)
                p = project(attributes, 'S', scaling=scaling)
                lines.append(f"| {name} | {budget} ({allocation_cost(attributes, graduated)}) | {'Graduated' if graduated else 'Linear'} | {'/'.join(str(attributes[k]) for k in ATTRS)} | {profile_text(p)} | {p['move']} |")
    lines += ['', '### Recommendation', '',
              'Keep attribute-first rank scaling and trial the graduated costs. This leaves current creation intact while charging more for extreme specialization; +4–6 means allocation points, not guaranteed +4–6 raw attribute increases. Preserve actual rolled budgets, including totals above 61.', '',
              'Do not assign Growth by looking up a point-total band. Generated characters need a declared completed stage plus an allocation allowance; below-E bodies need a recorded catch-up deficit. Existing enemies require an explicit reconstruction/migration record, not a guessed advancement history.', '',
              'The consequential unresolved choice is the shared fixed bases. A preserves existing player formulas but raises light-enemy strength. B better approximates light enemies but reduces baseline player strength. Neither should be shipped automatically from this comparison. Recommend evaluating a small player-and-enemy trial together before selecting the final bases.', '',
              '## Limits and next validation', '',
              'This report samples the first authored variation of five humanoid missions, not every race, boss or layout. Caster Attack is a staff/INT weapon pool illustration, not a promise that every spell uses it. Armor is flat subtraction: actual durability depends on incoming damage, penetration, resistances and mitigation; it cannot be summarized as one universal reduction percentage.', '',
              'Future trial must compare basic/technique damage through the real resolver, incoming attacks and survival turns, racial damage reduction, gear/perk modifiers, and full encounter action economy. No battle simulation or win-rate claim is made by this calculator. Movement/range percentages, cooldowns, statuses and species kits require independent review rather than rank multiplication.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = report()
    if args.output:
        args.output.write_text(result, encoding='utf-8')
    else:
        print(result)


if __name__ == '__main__':
    main()
