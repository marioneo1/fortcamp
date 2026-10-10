"""Opt-in identities for the audited humanoid encounters, preserved on recruits."""
RACES = {'Human': 'human', 'Goblin': 'goblin'}
GENDERS = {'male', 'female'}
PERSONALITIES = {'guardian', 'strategist', 'opportunist', 'survivor'}

def voice_key(unit):
    race = RACES.get(unit.get('race'))
    gender = unit.get('gender')
    personality = unit.get('personality_id')
    if race and gender in GENDERS and personality in PERSONALITIES:
        return f'{race}_{gender}_{personality}'
    return None

def assign(unit):
    snapshot = unit.get('recruitable_snapshot')
    key = voice_key(unit)
    if not snapshot or not key or unit.get('creature') or unit.get('species_profile'):
        return
    unit['combat_voice_key'] = key
    snapshot['combat_voice_key'] = key
