"""Short, read-only stat help and numeric formulas for the pinned inspector."""
import re


def readable_source(text):
    # Older saved battles can still contain the former code-style explanations.
    return re.sub(r'(\w+)\s*//\s*(\d+)', r'(\1 ÷ \2, rounded down)', str(text)).rstrip('. ')


def explanations(unit):
    sources = {key: readable_source(value) for key, value in unit.get('stat_sources', {}).items()}
    armor = unit.get('effective_armor', unit.get('armor', 0))
    attack = unit.get('effective_attack', unit.get('attack', 0))
    base = unit.get('attack', 0)
    statuses = {s['id'] for s in unit.get('statuses', [])}
    form = unit.get('form', {}).get('id')
    rat = form == 'rat'

    attack_formula = sources.get('Attack', f'{base} weapon/profile power')
    if form:
        original = unit['form'].get('original', {}).get('attack', base)
        attack_formula = (f'Rat profile = 1' if rat else
                          f'Higher of original Attack {original} and INT {unit.get("intelligence", 4)} = {base}' if unit['form'].get('persistent') else
                          f'{form.title()} profile = {base}')
    if 'pestilence' in statuses and not rat:
        attack_formula += f'; Pestilence: {base} × 0.75 = {max(1, round(base * .75))}, rounded'
    if any(p.get('id', '').endswith(':bloodied_strength') for p in unit.get('passives', [])) and not rat:
        attack_formula += f'; Bloodied Strength adds {attack - max(1, round(base * .75)) if "pestilence" in statuses else attack-base} = {attack} current Attack'
    attack_help = ('Rat hits deal 1 damage before Barrier; other forms share your HP.' if rat else
                   'Attack with capture equipment is a lethal Punch; Subdue uses separate Resolve power.' if unit.get('capture_weapon') else
                   'Attack is your weapon power before target defenses; skills and damage bonuses can modify the result.')

    armor_formula = sources.get('Armor', f'{unit.get("armor", 0)} profile Armor')
    if 'armor_fracture' in statuses:
        armor_formula += f'; Armor Fracture: {unit.get("armor", 0)} − {unit.get("armor", 0)-armor} = {armor} (30% reduction, rounded up)'
    move = unit.get('move', 0)
    movement = unit.get('effective_move', move)
    movement_formula = sources.get('Movement', f'{move} profile movement') if not form else f'{move} {form.title()} profile movement'
    if movement != move:
        movement_formula += f'; {move} {movement-move:+} from active modifiers and limits = {movement}'
    reach = unit.get('attack_range', 1)
    base_range = unit.get('ranger_base_range', reach)
    eva = unit.get('evasion', 0)
    evasion_formula = sources.get('Evasion', f'{unit.get("evasion_base", eva)} profile Evasion')
    if unit.get('evasion_base') is not None:
        evasion_formula += f'; active bonus +{eva-unit["evasion_base"]} = {eva}'
    if 'captor_blitz' in statuses:
        evasion_formula += f'; Blitz +25 = {eva+25} against aimed attacks'
    rule = unit.get('attack_elevation_rule', 'melee')
    base_chance = 90 if rule == 'ballistic' else 100
    factor = 1 if rule == 'ballistic' else .3 if rule == 'ignore' else .6

    return {
        'Attack': f'{attack_help}\nFormula: {attack_formula}',
        'Armor': f'Armor subtracts {armor} from hits that use Armor, after armor piercing; percentage Burn, Poison and Bleed bypass it. For example, 20 attack power becomes {max(1,20-armor)} damage before other modifiers.\nFormula: {armor_formula}',
        'Health': 'Maximum HP is the health pool shared by all your forms.\nFormula: ' + sources.get('Health', f'{unit.get("max_hp",0)} maximum HP from this profile'),
        'Movement': f'You can currently spend {movement} movement points; difficult terrain can cost extra. Control effects, carrying and form restrictions can reduce this allowance.\nFormula: {movement_formula}',
        'Range': f'Your basic attack reaches {reach} cells, subject to line of sight and elevation; individual skills can have different ranges.\nFormula: {base_range} weapon/profile range + {reach-base_range} active bonus = {reach}',
        'Accuracy': 'Hit chance is calculated for each target using elevation, effects and target Evasion. Guaranteed-hit attacks bypass normal accuracy and Parry.\nFormula: ' + f'{base_chance}% base + accuracy bonuses − penalties − (target Evasion × {factor:g}, rounded), limited to 5–100%\nAfter Parry: hit chance × (100 − Parry %) ÷ 100',
        'Evasion': ('Rat has 90% Evasion: ordinary aimed attacks have a 10% hit chance. AoE and guaranteed hits bypass it; any HP damage kills Rat.\nFormula: 100% − 90% = 10% hit chance' if rat else
                    f'Evasion lowers incoming accuracy instead of rolling a separate dodge. Ranged attacks subtract 100% of Evasion, melee 60% and magic 30%; attacker-specific bonuses appear in the target preview.\nFormula: {evasion_formula}'),
        'Initiative': 'Higher Initiative acts earlier in the round.\nFormula: ' + sources.get('Initiative', f'{unit.get("initiative",0)} profile Initiative'),
        'Level': 'Level shows character progression; damage comes from combat stats and skills.\nValue: ' + str(unit.get('level',1)),
    }
