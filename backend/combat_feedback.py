"""Presentation facts from resolved combat, never a second damage simulation."""


def record(battle, unit, kind, amount=0, **details):
    battle.setdefault('animation_events', []).append({
        'type': 'combat_feedback', 'unit_id': unit['id'],
        'x': unit['x'], 'y': unit['y'], 'kind': kind,
        'amount': max(0, int(amount)), **details,
    })
