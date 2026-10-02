"""Authored rank budgets. These do not depend on a player's roster."""
RANK_BUDGETS = {
    'E': (22, 14, 6, 4, 1, 0),
    'D': (56, 26, 10, 7, 2, 1),
    'C': (84, 38, 13, 9, 3, 2),
    'B': (112, 48, 17, 12, 4, 2),
    'A': (154, 62, 22, 15, 5, 3),
    'S': (210, 80, 29, 19, 6, 4),
}

def enemy_budget(rank, commander, racial):
    hp, escort_hp, attack, escort_attack, armor, escort_armor = RANK_BUDGETS[rank]
    multiplier = float(racial['hp_multiplier'])
    # Commanders have veteran durability; ordinary goblins retain their fragile identity.
    hp = round((hp if commander else escort_hp) * (max(.85, multiplier) if commander else multiplier))
    return {'hp': max(8, hp + int(racial['hp_bonus'])),
            'armor': max(0, (armor if commander else escort_armor) + int(racial['armor_bonus'])),
            'attack': attack if commander else escort_attack}
