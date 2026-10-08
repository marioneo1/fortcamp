"""Bard performance state and support-controller rules."""
from copy import deepcopy

from . import combat_conditions as conditions

# Songs establish a compact one-cell performance space around the Bard.
SONG_RADIUS = 1
SONGS = {
    'accelerando': {'status': 'bard_accelerando', 'no_linger': True, 'label': 'Accelerando'},
    'quickening_chorus': {'status': 'bard_quickening', 'no_linger': False, 'label': 'Quickening Chorus'},
    'war_anthem': {'status': 'bard_war_anthem', 'no_linger': False, 'label': 'War Anthem'},
    'song_of_peace': {'status': 'bard_song_peace', 'no_linger': True, 'label': 'Song of Peace'},
}

PEACE_DURATION = 2


def song_skill(skill):
    return skill.get('bard_kind') in SONGS


def active_song(unit):
    return (unit.get('bard_song') if unit and unit.get('bard_song') in SONGS
            and unit.get('alive', True) and unit.get('conscious', True) else None)


def _inside(battle, bard, unit):
    if not unit or not unit.get('alive', True) or not unit.get('conscious', True):
        return False
    return max(abs(bard['x'] - unit['x']), abs(bard['y'] - unit['y'])) <= SONG_RADIUS and _line_of_sight(battle, bard, unit)


def _line_of_sight(battle, source, target):
    # Importing combat here avoids its module-level cycle.
    from . import combat
    return combat._line_of_sight(battle, source, target)


def _status(unit, status_id, source_id=None):
    return next((s for s in unit.get('statuses', []) if s.get('id') == status_id and s.get('bard_song')), None)


def _remove_status(unit, status_id, source_id=None):
    unit['statuses'] = [s for s in unit.get('statuses', []) if not (
        s.get('id') == status_id and s.get('bard_song') and (source_id is None or s.get('source_id') == source_id))]


def stop_song(battle, bard):
    song = active_song(bard)
    if not song:
        return False
    definition = SONGS[song]
    if definition['no_linger']:
        for unit in battle.get('units', {}).values():
            _remove_status(unit, definition['status'], bard['id'])
    bard.pop('bard_song', None)
    bard.pop('bard_song_started', None)
    battle.setdefault('log', []).append(f"{bard['name']} stops playing {definition['label']}.")
    return True


def _acquire(battle, bard, unit, song):
    definition = SONGS[song]
    # Song of Peace is a true no-attack zone, including the performing Bard.
    # Other Songs either affect allies only or explicitly exclude the Bard.
    if unit['id'] == bard['id'] and song != 'song_of_peace':
        return
    if song == 'quickening_chorus' and unit['id'] == bard['id']:
        return
    current = _status(unit, definition['status'])
    if current:
        # A unit that remains properly settled inside the active performance
        # keeps the Song through its next activation. This is a
        # committed-position refresh, not a movement-tile poll: passing
        # through the radius still does nothing, while ending/staying inside
        # keeps the benefit alive.
        current['turns'] = 1
        current['applied_activation'] = deepcopy(unit.get('status_activation'))
        current.update(source_id=bard['id'], source_name=bard['name'])
        return
    # Duplicate copies of the same Song never stack, even with two Bards.
    if any(s.get('bard_song') == song for s in unit.get('statuses', [])):
        return
    conditions.apply(unit, definition['status'], 1, bard)
    status = next(s for s in unit.get('statuses', []) if s.get('id') == definition['status'])
    status.update(bard_song=song, bard_no_linger=definition['no_linger'], source_id=bard['id'], source_name=bard['name'])


def refresh(battle, moved=None):
    """Acquire Songs only at a committed resting position; remove NO LINGER immediately."""
    for unit in battle.get('units', {}).values():
        if unit.get('bard_song') in SONGS and (not unit.get('alive', True) or not unit.get('conscious', True)):
            _end_song_state(battle, unit, remove_no_linger=True)
    bards = sorted((u for u in battle.get('units', {}).values() if active_song(u)), key=lambda u: u['id'])
    for bard in list(bards):
        if (active_song(bard) == 'song_of_peace'
                and int(bard.get('ability_activation', 0)) - int(bard.get('bard_song_started', 0)) >= PEACE_DURATION):
            stop_song(battle, bard)
    bards = [u for u in bards if active_song(u)]
    active_sources = {u['id']: active_song(u) for u in bards}
    for unit in battle.get('units', {}).values():
        # Clear invalid live-area effects before another Bard can reacquire them.
        for status in list(unit.get('statuses', [])):
            if not status.get('bard_no_linger'):
                continue
            source = battle.get('units', {}).get(status.get('source_id'))
            if (not source or active_sources.get(source['id']) != status.get('bard_song')
                    or not _inside(battle, source, unit)):
                _remove_status(unit, status['id'], status.get('source_id'))
        for bard in bards:
            song = active_song(bard)
            if song != 'song_of_peace' and unit.get('team') != bard.get('team'):
                continue
            if _inside(battle, bard, unit):
                _acquire(battle, bard, unit, song)
            elif SONGS[song]['no_linger']:
                _remove_status(unit, SONGS[song]['status'], bard['id'])
        # Acquired lingering buffs expire on the recipient's clock, even if the
        # performance stops, switches or its source is defeated.


def _end_song_state(battle, bard, remove_no_linger=True):
    """End the performance itself, optionally preserving lingering buffs."""
    song = bard.get('bard_song') if bard.get('bard_song') in SONGS else None
    if not song:
        return False
    if remove_no_linger and SONGS[song]['no_linger']:
        for unit in battle.get('units', {}).values():
            _remove_status(unit, SONGS[song]['status'], bard['id'])
    bard.pop('bard_song', None)
    bard.pop('bard_song_started', None)
    return True


def begin_song(battle, bard, song):
    if song not in SONGS:
        raise ValueError('Unknown Bard Song')
    current = active_song(bard)
    if current:
        if not has_maestro(bard):
            raise ValueError('Stop the current Song before starting another; Maestro enables direct switching')
        # Maestro replaces the performance but does not erase a lingering
        # Song buff. NO-LINGER effects are removed immediately; War Anthem and
        # Quickening Chorus continue through their normal expiry window.
        previous = current
        _end_song_state(battle, bard, remove_no_linger=True)
        battle.setdefault('log', []).append(f"{bard['name']} switches from {SONGS[previous]['label']}.")
    bard['bard_song'] = song
    bard['bard_song_started'] = bard.get('ability_activation', 0)
    refresh(battle)
    battle.setdefault('log', []).append(f"{bard['name']} begins {SONGS[song]['label']}.")


def has_maestro(unit):
    return any(p.get('bard_kind') == 'maestro' or p.get('id','').endswith(':maestro') for p in unit.get('passives', []))


def locked(unit):
    return bool(active_song(unit))


def cooldown_bonus(unit):
    return bool(any(s.get('id') == 'bard_quickening' and s.get('bard_song') == 'quickening_chorus'
                    for s in unit.get('statuses', [])))


def can_attack(unit):
    if unit.get('engineer_disrupted')==unit.get('ability_activation',0):return False
    if unit.get('captor_held_by') or unit.get('captor_hold'):return False
    return not any(s.get('id') == 'bard_song_peace' and s.get('bard_song') == 'song_of_peace'
                   for s in unit.get('statuses', []))


def attack_skill(skill):
    if not skill:return False
    if skill.get('captor_kind') not in {None,'blitz'}:return True
    if skill.get('engineer_kind') in {'scuttle_protocol','dynamite'}:return True
    if skill.get('summoner_kind') in {'spirit_projection','sacrifice'}:return True
    """Whether a normal ability is an offensive action for Song of Peace."""
    if not skill:
        return False
    if any(effect.get('type') in {'attack', 'leap_attack', 'area_attack', 'dash_attack'}
           for effect in skill.get('effects', [])):
        return True
    if skill.get('mage_kind') not in {None, 'enchant_weapon'}:
        return True
    if skill.get('ranger_kind') not in {None, 'mark_quarry'}:
        return True
    if skill.get('rogue_kind') not in {None, 'shadowstep', 'backflip'}:
        return True
    return False


def performance_cells(battle, bard):
    return [
        {'x': x, 'y': y}
        for y in range(max(0, bard['y'] - SONG_RADIUS), min(battle.get('height', 0), bard['y'] + SONG_RADIUS + 1))
        for x in range(max(0, bard['x'] - SONG_RADIUS), min(battle.get('width', 0), bard['x'] + SONG_RADIUS + 1))
        if _line_of_sight(battle, bard, {'x': x, 'y': y})
    ]


def presentation(battle):
    """Return non-gameplay overlays for active Bard performance spaces."""
    result = []
    for bard in sorted((u for u in battle.get('units', {}).values() if active_song(u)), key=lambda u: u['id']):
        song = active_song(bard)
        cells = performance_cells(battle, bard)
        result.append({'id': f"bard-song:{bard['id']}", 'kind': 'bard_song', 'song': song,
                       'name': SONGS[song]['label'], 'owner_id': bard['id'], 'owner_name': bard['name'],
                       'remaining': '', 'description': 'Active performance space', 'cells': cells})
    return result


def forced_target(battle, unit):
    status = next((s for s in unit.get('statuses', []) if s.get('id') in {'bard_jeering','captor_abducted'}), None)
    if not status:
        return None
    target = battle.get('units', {}).get(status.get('source_id'))
    return target if target and target.get('alive') and target.get('conscious', True) else None


def apply_jeering(battle, bard, target):
    for unit in (target, bard):
        unit['statuses'] = [s for s in unit.get('statuses', []) if s.get('id') not in {'bard_jeering', 'bard_jeer_vulnerable'}]
    conditions.apply(target, 'bard_jeering', 2, bard)
    taunt = next(s for s in target['statuses'] if s['id'] == 'bard_jeering')
    taunt.update(source_id=bard['id'], source_name=bard['name'], bard_jeering=True)
    conditions.apply(target, 'bard_jeer_vulnerable', 2, bard)
    conditions.apply(bard, 'bard_jeer_vulnerable', 2, target)
    for unit in (target, bard):
        status = next(s for s in unit['statuses'] if s['id'] == 'bard_jeer_vulnerable')
        status.update(bard_jeering=True, damage_taken_percent=20)
    battle.setdefault('log', []).append(f"{target['name']} is drawn into {bard['name']}'s Jeering Verse.")


def cue_strike(battle, bard, ally, target):
    from . import combat
    if not ally or ally.get('team') != bard.get('team') or not combat._combat_active(ally):
        raise ValueError('Choose a conscious allied performer')
    if not target or target.get('team') == bard.get('team') or not combat._combat_active(target):
        raise ValueError('Choose a living enemy for Cue the Strike')
    if not can_attack(ally):
        raise ValueError('Song of Peace prevents the ally from attacking here')
    if not combat._can_attack(battle, ally, target, ally.get('attack_range', 1)):
        raise ValueError('The commanded ally cannot make a legal basic attack from here')
    combat._perform_attack(battle, ally, target, ally.get('attack_elevation_rule', 'melee'), 0, 0, ability=None)
    battle.setdefault('log', []).append(f"{bard['name']} cues {ally['name']} to strike {target['name']}.")
