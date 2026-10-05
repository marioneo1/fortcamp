"""Visual/audio delivery only; these profiles never change damage or capture."""
import re

STYLES = {'slash', 'hack', 'crush', 'blunt', 'fist', 'stab'}
WEAPON_STYLES = {
    'sword': 'slash', 'blade': 'slash', 'axe': 'hack',
    'hammer': 'crush', 'mace': 'crush', 'flail': 'crush',
    'club': 'blunt', 'quarterstaff': 'blunt', 'baton': 'blunt',
    'unarmed': 'fist', 'fist': 'fist', 'knuckles': 'fist',
    'spear': 'stab', 'dagger': 'stab', 'knife': 'stab', 'pike': 'stab',
}
SKILL_STYLES = {'job:fighter:bash': 'blunt'}


def weapon_style(weapon):
    explicit = weapon.get('melee_style')
    if explicit in STYLES:
        return explicit
    kind = weapon.get('weapon_type')
    # The one legacy blade item is explicitly a knife.
    if kind == 'blade' and re.search(r'\b(knife|dagger)\b', weapon.get('weapon', weapon.get('name', '')).lower()):
        return 'stab'
    if kind in WEAPON_STYLES:
        return WEAPON_STYLES[kind]
    # Legacy/monster battle snapshots predate typed weapons. Prefer their name
    # until the next battle is created; unknown physical attacks stay blunt.
    name = weapon.get('weapon', weapon.get('name', '')).lower()
    for words, style in [
        (r'\b(unarmed|fists?|handwraps|claws?)\b', 'fist'),
        (r'\b(spear|pike|lance|knife|dagger)\b', 'stab'),
        (r'\b(axe|hatchet|cleaver)\b', 'hack'),
        (r'\b(hammer|maul|mace|flail|morningstar)\b', 'crush'),
        (r'\b(sword|blade|sabre|saber)\b', 'slash'),
    ]:
        if re.search(words, name):
            return style
    return 'blunt'


def attack_style(attacker, ability=None):
    if ability and ability.get('id') in SKILL_STYLES:
        return SKILL_STYLES[ability['id']]
    return weapon_style(attacker)


def capture_style(weapon):
    if weapon.get('capture_weapon') and re.search(r'\b(net|mesh)\b',weapon.get('weapon',weapon.get('name','')).lower()):
        return 'net'
    return None


def armor_material(item):
    explicit=item.get('armor_material')
    if explicit:return explicit
    name=item.get('name','').lower()
    if re.search(r'\b(plate|chain|chainmail|ringmail|mail|metal|iron|steel)\b',name):return 'metal'
    if re.search(r'\b(leather|hide|vest)\b',name):return 'leather'
    return 'cloth' if item else 'none'


def impact_surface(target):
    # Anatomy wins over clothing: a robot wearing a cloak is still mechanical.
    race=str(target.get('race','Human')).lower().replace(' ','')
    if race=='automaton' or target.get('body_material')=='metal':return 'metal'
    if race in {'golem','undead','revenant','banshee','slimefolk'}:return 'rigid'
    if target.get('body_material') in {'stone','bone','ethereal','slime'}:return 'rigid'
    if target.get('impact_surface') in {'metal','flesh','rigid'}:return target['impact_surface']
    if target.get('armor_material') in {'metal','plate','chain','chainmail','mail'}:return 'metal'
    return 'flesh'
