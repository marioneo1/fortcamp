"""Ordinary character stats shared by allies and reconstructed humanoid enemies."""
from .combat_pacing import RANK_PERCENT, scaled
from .races import race_gameplay

HP_BASE = 12
ATTACK_BASE = 2
ATTRIBUTE_NAMES = ('str', 'dex', 'agi', 'vit', 'int', 'luk')


def adventurer_rank(character):
    rank = character.get('adventurer_rank', 'E')
    return rank if rank in RANK_PERCENT else 'E'


def allocated_attribute(character, key):
    base = character.get('_battle_attribute_base', {}).get(key, character.get('attributes', {}).get(key, 5))
    return scaled(max(1, int(base)), adventurer_rank(character))


def health(vitality, racial, bonus=0):
    return max(1, max(8, round((HP_BASE + max(1, vitality) * 4) * float(racial['hp_multiplier']))
                          + int(racial['hp_bonus'])) + int(bonus))


def attack(attribute, power=0, training=0):
    return max(1, ATTACK_BASE + max(1, int(attribute)) // 2 + int(power) + int(training))


def armor(vitality, racial, bonus=0):
    return max(0, max(1, int(vitality)) // 3 + int(racial['armor_bonus'])) + int(bonus)


def derive(attributes, race, scaling='str', power=0, training=0, hp_bonus=0, armor_bonus=0):
    racial = race_gameplay(race)
    vit = attributes['vit']
    return dict(max_hp=health(vit, racial, hp_bonus),
                attack=attack(attributes[scaling], power, training),
                armor=armor(vit, racial, armor_bonus))


def rank_explanation(character):
    rank = adventurer_rank(character)
    return f"{rank} rank: allocated attributes ×{RANK_PERCENT[rank]/100:g}, rounded, before equipment and perk bonuses."


def sources(attributes, race, scaling='str', power=0, training=0, hp_bonus=0,
            armor_bonus=0, job_armor=0, equipment_armor=0):
    """Numeric player-facing formulas, shared by allies and ordinary NPCs."""
    racial = race_gameplay(race)
    vit = attributes['vit']
    atk = attack(attributes[scaling], power, training)
    hp = health(vit, racial, hp_bonus)
    arm = armor(vit, racial, armor_bonus + job_armor + equipment_armor)
    racial_hp = round((HP_BASE + vit * 4) * float(racial['hp_multiplier'])) + int(racial['hp_bonus'])
    hp_formula = f"(12 + 4 × VIT {vit}) × {racial['hp_multiplier']} racial modifier + {racial['hp_bonus']} racial HP = {racial_hp}, rounded"
    if racial_hp < 8:
        hp_formula += '; raised to the minimum 8 HP'
    hp_formula += f'; + {hp_bonus} bonus HP = {hp}'
    if max(8, racial_hp) + hp_bonus < 1:
        hp_formula += ' (minimum 1 HP)'
    return {
        'Attack': f"2 + ({scaling.upper()} {attributes[scaling]} ÷ 2, rounded down) + {power} weapon + {training} training = {atk}",
        'Health': hp_formula,
        'Armor': f"(VIT {vit} ÷ 3, rounded down) + {racial['armor_bonus']} racial + {equipment_armor + armor_bonus} equipment/perks + {job_armor} Job = {arm}",
    }
