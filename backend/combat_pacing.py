"""Fixed E-relative rank budgets; never adaptive to the player's roster."""
RANK_PERCENT = dict(zip('EDCBAS', (100,130,160,190,220,250)))

def scaled(value, rank):
    # Positive integer rounding, including .5; zero Armor stays zero.
    return (int(value)*RANK_PERCENT[rank]+50)//100

RANK_BUDGETS = {rank:tuple(scaled(v,rank) for v in (28,24,5,4,1,0)) for rank in RANK_PERCENT}

def scale_unit(unit, rank, fields=('hp','max_hp','attack','armor','strength','agility','intelligence','dexterity','vitality','luck')):
    baseline={key:int(unit[key]) for key in fields if key in unit}
    for key,value in baseline.items():unit[key]=scaled(value,rank)
    unit['rank_scaling']={'rank':rank,'percent':RANK_PERCENT[rank],'baseline':baseline}

def enemy_budget(rank, commander, racial):
    hp, escort_hp, attack, escort_attack, armor, escort_armor = RANK_BUDGETS['E']
    multiplier = float(racial['hp_multiplier'])
    # Commanders have veteran durability; ordinary goblins retain their fragile identity.
    hp = round((hp if commander else escort_hp) * (max(.85, multiplier) if commander else multiplier))
    return {'hp': scaled(max(8, hp + int(racial['hp_bonus'])),rank),
            'armor': scaled(max(0, (armor if commander else escort_armor) + int(racial['armor_bonus'])),rank),
            'attack': scaled(attack if commander else escort_attack,rank)}
