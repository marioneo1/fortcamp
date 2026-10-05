"""Authored combat routing for contracts that explicitly describe opposition."""

TACTICAL_CONTRACTS = {
    "highway_ambush": {"race": "Human", "layout": "road", "faction": "road raiders"},
    "bandit_outpost": {"race": "Human", "layout": "camp", "faction": "outpost bandits"},
    "goblin_warren": {"race": "Goblin", "layout": "ruin", "faction": "warren guards"},
    "goblin_chieftain": {"race": "Goblin", "layout": "camp", "faction": "chieftain's warband", "leader_target": True},
    "goblin_boar_riders": {"race": "Goblin", "layout": "road", "faction": "boar riders", "mounted": True},
    "hobgoblin_vanguard": {"race": "Hobgoblin", "layout": "camp", "faction": "hobgoblin vanguard", "armor_material":"chain"},
    "bone_patrol": {"race": "Undead", "layout": "road", "faction": "chapel dead"},
    "undead_bone_collectors": {"race": "Undead", "layout": "ruin", "faction": "Procession collectors"},
    "undead_death_knight": {"race": "Undead", "layout": "ruin", "faction": "fallen knight's retinue", "armor_material":"plate", "leader_target": True},
    "black_banner_convoy": {"race": "Human", "layout": "road", "faction": "Black Banner escort", "armor_material":"chain"},
    "black_banner_court": {"race": "Human", "layout": "court", "faction": "Black Banner captains", "armor_material":"plate"},
}


def apply_tactical_contracts(missions):
    for mission_id, spec in TACTICAL_CONTRACTS.items():
        mission = missions[mission_id]
        critical = "Secure the field and keep every party member standing."
        if spec["race"] != "Undead":
            critical = "Capture the commander alive, secure the field, and keep every party member standing."
        mission.update({
            "combat_encounter": {"id": f"contract:{mission_id}","name":mission['name'],"description":"A tactical encounter with breakable cover, defined exits, and faction-specific opposition."},
            "resolution_mode": "tactical", "bodyguard_slots": 0,
            "combat_critical_condition": critical,
            "objective": "Defeat or subdue the commander, then leave safely." if spec.get("leader_target") else "Break the enemy force and secure the route.",
        })
