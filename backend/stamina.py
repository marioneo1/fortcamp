"""Timestamp-based expedition stamina. Reads never write recovered balances."""
import math
import time

CAPACITY = 100
RECOVERY_SECONDS = 1800
COSTS = dict(E=1, D=3, C=5, B=10, A=50, S=100)


def initialize(character, now=None):
    character.setdefault('stamina', {'balance': CAPACITY, 'updated_at': time.time() if now is None else now})


def view(character, now=None):
    now = time.time() if now is None else now
    saved = character.get('stamina', {})
    balance = min(CAPACITY, float(saved.get('balance', CAPACITY)) +
                  max(0, now - float(saved.get('updated_at', now))) * CAPACITY / RECOVERY_SECONDS)
    return {'current': balance, 'maximum': CAPACITY, 'eligible': balance >= 1,
            'ready_in_seconds': max(0, math.ceil((1-balance)*RECOVERY_SECONDS/CAPACITY)),
            'full_in_seconds': max(0, math.ceil((CAPACITY-balance)*RECOVERY_SECONDS/CAPACITY))}


def preview(characters, rank, now=None):
    now = time.time() if now is None else now
    cost = COSTS.get(rank, COSTS['E'])
    rows = [{'id': c['id'], 'name': c['name'], **view(c, now)} for c in characters]
    for row in rows:
        row['after'] = row['current'] - cost
        row['borrowing'] = row['eligible'] and row['after'] < 0
    return {'cost_per_character': cost, 'eligible': all(row['eligible'] for row in rows), 'characters': rows}


def spend(state, ids, rank, now=None):
    now = time.time() if now is None else now
    ids = set(ids)
    characters = [c for c in state['characters'] if c['id'] in ids]
    if len(characters) != len(ids):
        raise ValueError('A selected character is missing')
    check = preview(characters, rank, now)
    if not check['eligible']:
        names = ', '.join(row['name'] for row in check['characters'] if not row['eligible'])
        raise ValueError(f'Not enough stamina: {names}. Recover to at least 1 point before departing.')
    by_id = {row['id']: row for row in check['characters']}
    for character in characters:
        character['stamina'] = {'balance': by_id[character['id']]['after'], 'updated_at': now}
    # Hired copies disappear after settlement; keep their debt on the saved offer.
    for offer in state.get('mercenaries', []):
        if offer['id'] in by_id:
            offer['character']['stamina'] = dict(next(c['stamina'] for c in characters if c['id'] == offer['id']))
    return check
