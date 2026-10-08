"""Read-only explanations of the combat snapshot, without hidden AI/personality data."""
def explanations(unit):
    sources=unit.get('stat_sources',{})
    armor=unit.get('effective_armor',unit.get('armor',0))
    attack=unit.get('effective_attack',unit.get('attack',0))
    statuses={s['id'] for s in unit.get('statuses',[])}
    base=unit.get('attack',0)
    attack_steps=[f'Battle attack {base}']
    if 'pestilence' in statuses:attack_steps.append(f'Pestilence × 0.75 → {max(1,round(base*.75))}')
    if any(p.get('id','').endswith(':bloodied_strength') for p in unit.get('passives',[])):
        attack_steps.append(f'Bloodied Strength: up to +50%, proportional to missing HP → {attack}')
    rat=unit.get('form',{}).get('id')=='rat'
    if unit.get('form'):
        sources={**sources,'Attack':f"Current {unit['form']['id']} form replaces weapon attack with this profile"}
    return {
        'Attack':sources.get('Attack','Authored battle/profile attack.')+'. '+ '; '.join(attack_steps)+f'. Effective ATK {attack}. Skill power, outgoing bonuses, target armor and mitigation then determine actual damage.'+(' Rat direct hits deal fixed 1 before Barrier.' if rat else ''),
        'Armor':sources.get('Armor','Authored battle/profile armor.')+f'. Battle armor {unit.get("armor",0)}'+(f' − ceil(30%) Armor Fracture = {armor}' if 'armor_fracture' in statuses else f'; effective armor {armor}')+f'. Subtract {armor} from incoming attack power after armor piercing, minimum 1 before other modifiers. Against 20 power: {max(1,20-armor)} damage before modifiers. Armor is flat reduction, not a fixed percentage. Percentage Burn/Poison/Bleed bypass armor.',
        'Health':sources.get('Health','Authored maximum HP.')+f'. Maximum {unit.get("max_hp",0)}; current {unit.get("hp",0)}. Forms share this HP pool.',
        'Movement':f'Profile movement {unit.get("move",0)} → currently {unit.get("effective_move",unit.get("move",0))}. Includes movement bonuses, carrying penalties, Slow, Hobble, control, performance locks and this activation’s form budget. Terrain can cost more than one point per tile.',
        'Range':f'Current basic weapon range {unit.get("attack_range",1)} cells. Sharpshooter adds 2 while established. Individual skills have their own range; line of sight and elevation still apply.',
        'Accuracy':'Base hit chance: ranged ballistic 90%, melee/magic 100%. Add elevation, Mark, rhythm and perk accuracy; subtract Blind (35 ranged/magic or 15 melee), Fear (15), Berserk (10), Blister (10) and target evasion. Evasion penalty: 100% of EVA for ballistic, 60% melee, 30% magic. Clamp to 5–100%, then apply parry. Owner Quarry and cannot-miss techniques guarantee hits. Actual target forecast includes these conditions.',
        'Evasion':('Rat form locks ordinary aimed attacks to 10% hit chance (90% evasion). AoE and guaranteed hits bypass this; any HP damage kills Rat.' if rat else sources.get('Evasion','Authored evasion.')+f'. Current {unit.get("evasion",0)} EVA, including active evasion bonuses. Subtract round(EVA × 1.0) from ballistic accuracy, × 0.6 from melee, × 0.3 from magic. EVA is not a separate dodge roll. Enemy-specific evasion and parry are shown under buffs.'),
        'Initiative':sources.get('Initiative','Authored initiative.')+f'. Current {unit.get("initiative",0)}. Higher initiative acts earlier in the round.',
        'Level':f'Character level {unit.get("level",1)}. Damage is calculated from actual battle stats and skills, not level alone.',
    }
