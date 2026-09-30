"""Deterministic tactical combat engine for Fortcamp's first battle encounter."""
from __future__ import annotations

import random
import heapq
from copy import deepcopy

from .battle_maps import compile_battle_map, compile_generated_battle_map, occupied_tiles
from .content import ITEMS, RECRUIT_PROFILES, MISSION_TEMPLATES
from .tactical_contracts import TACTICAL_CONTRACTS
from .portraits import choose_pool_portrait, portrait_pool_key
from .races import race_gameplay
from .perk_effects import modifiers


STATUS_DEFINITIONS = {
    "stun": {"name": "Stun", "icon": "✦", "description": "Cannot act during the next activation."},
    "sleep": {"name": "Sleep", "icon": "Zz", "description": "Cannot act. Taking direct damage wakes the unit."},
    "poison": {"name": "Poison", "icon": "☠", "description": "Takes damage at activation start; armor does not reduce it."},
    "bleed": {"name": "Bleed", "icon": "◆", "description": "Takes physical damage after moving or using a physical action."},
    "charm": {"name": "Charm", "icon": "♥", "description": "Treats the charmer's faction as friendly and former allies as hostile."},
    "confuse": {"name": "Confuse", "icon": "?", "description": "Offensive actions may redirect to another valid nearby target."},
    "berserk": {"name": "Berserk", "icon": "‼", "description": "Must attack if possible and treats every nearby unit as hostile."},
    "freeze": {"name": "Freeze", "icon": "❄", "description": "Cannot move and takes increased impact damage; fire removes it."},
    "burn": {"name": "Burn", "icon": "♨", "description": "Takes damage at activation start and may ignite flammable terrain."},
    "blind": {"name": "Blind", "icon": "◉", "description": "Greatly reduces ranged accuracy and limits reaction range."},
    "bind": {"name": "Bind", "icon": "⌁", "description": "Cannot move until the bind is broken, removed, or expires."},
    "slow": {"name": "Slow", "icon": "◷", "description": "Reduces movement and delays the next initiative position."},
    "paralyze": {"name": "Paralyze", "icon": "ϟ", "description": "May lose movement or the main action when the activation begins."},
    "mute": {"name": "Mute", "icon": "◇", "description": "Cannot use spells or actions with a verbal component."},
    "fear": {"name": "Fear", "icon": "!", "description": "Cannot willingly move closer to the source and suffers reduced accuracy against it."},
    "vulnerable": {"name": "Vulnerable", "icon": "▽", "description": "The next damaging hit ignores part of the target's armor."},
    "regeneration": {"name": "Regeneration", "icon": "+", "description": "Restores health at activation start; fire can suppress it."},
    "panic": {"name": "Panic", "icon": "↯", "description": "Control is lost. The unit will run toward the nearest valid escape tile."},
}

LARGE_OBJECT_FOOTPRINTS = {
    "prisoner_pen": [2, 2],
    "iron_rescue_cage": [2, 2],
    "wooden_rescue_cage": [2, 2],
    "stone_sarcophagus": [2, 1],
    "prisoner_stocks": [2, 1],
}


def _goblin_chieftain_identity(rng: random.Random) -> tuple[str, str, dict]:
    profile = RECRUIT_PROFILES["goblin_boss"]
    genders = list(profile.get("genders", ["male", "female"]))
    preferred_gender = rng.choice(genders)
    chief_name = f"{rng.choice(profile['first_names'])} {rng.choice(profile['last_names'])}"
    ordered_genders = [preferred_gender, *(gender for gender in genders if gender != preferred_gender)]
    portrait = {"portrait": "", "portrait_thumbnail": "", "portrait_pool": ""}
    selected_gender = preferred_gender
    for gender in ordered_genders:
        candidate = choose_pool_portrait(
            portrait_pool_key(profile["race"], gender, "fighter", special=True), rng,
        )
        if candidate.get("portrait"):
            selected_gender, portrait = gender, candidate
            break
        if gender == preferred_gender:
            portrait = candidate
    return chief_name, selected_gender, portrait


def _goblin_npc_identity(seed: str, unit_id: str, archetype: str = "fighter") -> dict:
    rng = random.Random(f"{seed}:{unit_id}")
    profile = RECRUIT_PROFILES["goblin"]
    preferred_gender = rng.choice(profile.get("genders", ["male", "female"]))
    portrait = {"portrait": "", "portrait_thumbnail": "", "portrait_pool": ""}
    selected_gender = preferred_gender
    for gender in [preferred_gender, "male" if preferred_gender == "female" else "female"]:
        candidate = choose_pool_portrait(portrait_pool_key("Goblin", gender, archetype), rng)
        if candidate.get("portrait"):
            selected_gender, portrait = gender, candidate
            break
        if gender == preferred_gender:
            portrait = candidate
    return {
        "name": f"{rng.choice(profile['first_names'])} {rng.choice(profile['last_names'])}",
        "gender": selected_gender, **portrait,
    }


def _captive_cart_identities(seed: str) -> tuple[dict, dict]:
    courier_rng = random.Random(f"{seed}:courier")
    courier_first = ["Lysa", "Mara", "Tessa", "Nell", "Orin", "Dain", "Sella", "Corin"]
    courier_last = ["Vale", "Reed", "Ashdown", "Morrow", "Fen", "Dale", "Grey", "Hale"]
    preferred_gender = courier_rng.choice(["female", "male"])
    courier_portrait = {"portrait": "", "portrait_thumbnail": "", "portrait_pool": ""}
    courier_gender = preferred_gender
    for gender in [preferred_gender, "male" if preferred_gender == "female" else "female"]:
        candidate = choose_pool_portrait(portrait_pool_key("Human", gender, "scout"), courier_rng)
        if candidate.get("portrait"):
            courier_gender, courier_portrait = gender, candidate
            break
        if gender == preferred_gender:
            courier_portrait = candidate
    courier = {
        "name": f"Courier {courier_rng.choice(courier_first)} {courier_rng.choice(courier_last)}",
        "gender": courier_gender, **courier_portrait,
    }

    cartmaster_rng = random.Random(f"{seed}:cartmaster")
    cartmaster_name, cartmaster_gender, cartmaster_portrait = _goblin_chieftain_identity(cartmaster_rng)
    cartmaster = {
        "name": f"Cartmaster {cartmaster_name}", "gender": cartmaster_gender, **cartmaster_portrait,
    }
    return courier, cartmaster


def _ensure_battle_schema(battle: dict) -> None:
    """Upgrade active prototype battles with explicit, known combat rules."""
    map_id = battle.get("map_id")
    if map_id and "decorations" not in battle:
        battle["decorations"] = compile_battle_map(map_id).get("decorations", [])
    special_rules = {"precision_shot": "ballistic", "arc_bolt": "ignore"}
    for unit in battle.get("units", {}).values():
        unit.setdefault("statuses", [])
        unit.setdefault("conscious", bool(unit.get("alive", True)))
        unit.setdefault("condition", "active" if unit.get("alive", True) else "dead")
        unit.setdefault("carrying", None)
        unit.setdefault("carrying_object", None)
        unit.setdefault("carried_by", None)
        unit.setdefault("strength", max(4, int(unit.get("attack", 4))))
        unit.setdefault("weight", 3)
        unit.setdefault("panicked", False)
        unit.setdefault("exit_ready", False)
        unit.setdefault("fled", False)
        racial = race_gameplay(unit.get("race", "Human"))
        unit.setdefault("evasion", int(racial["evasion"]))
        unit.setdefault("movement_type", racial["movement_type"])
        unit.setdefault("racial_resistances", list(racial["resistances"]))
        unit.setdefault("racial_weaknesses", list(racial["weaknesses"]))
        special = unit.get("special")
        if special and special.get("id") == "power_strike":
            unit["special"] = special = None
        if special and "elevation_rule" not in special:
            special["elevation_rule"] = special_rules[special["id"]]
        if "attack_elevation_rule" not in unit:
            unit["attack_elevation_rule"] = (
                "ballistic" if unit.get("kind") == "archer" or special and special.get("id") == "precision_shot"
                else "ignore" if special and special.get("id") == "arc_bolt"
                else "melee"
            )
    for index, tile in enumerate(battle.get("terrain", [])):
        tile.setdefault("id", f"terrain_{index}")
        tile.setdefault("name", tile.get("kind", "terrain").replace("_", " ").title())
        tile.setdefault("movement_cost", 1)
        tile.setdefault("destroyed", False)
        tile.setdefault("footprint", [1, 1])
        tile.setdefault("rotation", 0)
        if tile.get("destructible"):
            tile.setdefault("max_hp", int(tile.get("hp", 10)))
            tile.setdefault("hp", tile["max_hp"])
            tile.setdefault("armor", 0)
    for obj in battle.get("objects", {}).values():
        obj.setdefault("blocking", not obj.get("portable", False))
        obj.setdefault("carried_by", None)
        obj.setdefault("footprint", deepcopy(LARGE_OBJECT_FOOTPRINTS.get(obj.get("id"), [1, 1])))
        obj.setdefault("rotation", 0)
        if obj.get("portable"):
            obj.setdefault("weight", 2)
            obj.setdefault("impact_damage", 2)
            obj.setdefault("carry_penalty", max(0, int(obj["weight"]) - 2))
    battle.setdefault("void_tiles", [])
    if battle.get("encounter_id") == "goblin_warcamp":
        chief = battle.get("units", {}).get("gob_chief")
        if chief and chief.get("name") == "Rattle-Crown":
            identity_rng = random.Random(battle.get("seed", "legacy-goblin-warcamp"))
            chief_name, gender, portrait = _goblin_chieftain_identity(identity_rng)
            chief.update({
                "name": chief_name, "gender": gender, "race": "Goblin",
                "portrait": portrait.get("portrait_thumbnail") or portrait.get("portrait", ""),
                "portrait_full": portrait.get("portrait", ""),
                "portrait_pool": portrait.get("portrait_pool", ""),
            })
            for objective in battle.get("objectives", []):
                if objective.get("id") == "chieftain":
                    objective["name"] = f"Defeat {chief_name}"
            battle["log"] = [line.replace("Rattle-Crown", chief_name) for line in battle.get("log", [])]
            for field in ("victory_title", "victory_log"):
                if isinstance(battle.get(field), str):
                    battle[field] = battle[field].replace("Rattle-Crown", chief_name)
        battle.setdefault("extraction", {"name": "South Approach", "tiles": [{"x": x, "y": 7} for x in range(4)]})
        battle.setdefault("enemy_extraction", {"name": "Broken Camp Perimeter", "tiles": [{"x": 7, "y": y} for y in range(8)] + [{"x": x, "y": 0} for x in (2, 3, 4, 6)]})
        battle.setdefault("elevation", [
            {"x": 4, "y": 1, "height": 1, "kind": "command_mound"},
            {"x": 6, "y": 2, "height": 1, "kind": "firing_platform"},
            {"x": 0, "y": 0, "height": 2, "kind": "rocky_rise"},
            {"x": 1, "y": 0, "height": 4, "kind": "high_cliff"},
        ])
    elif battle.get("encounter_id") == "goblin_captive_cart":
        courier = battle.get("units", {}).get("captive_courier")
        cartmaster = battle.get("units", {}).get("cartmaster_vrak")
        if courier and cartmaster and (courier.get("name") == "Courier Lysa" or cartmaster.get("name") == "Cartmaster Vrak"):
            courier_identity, cartmaster_identity = _captive_cart_identities(battle.get("seed", "legacy-captive-cart"))
            old_names = {"Courier Lysa": courier_identity["name"], "Cartmaster Vrak": cartmaster_identity["name"]}
            courier.update({
                "name": courier_identity["name"], "gender": courier_identity["gender"], "race": "Human",
                "portrait": courier_identity.get("portrait_thumbnail") or courier_identity.get("portrait", ""),
                "portrait_full": courier_identity.get("portrait", ""), "portrait_pool": courier_identity.get("portrait_pool", ""),
            })
            cartmaster.update({
                "name": cartmaster_identity["name"], "gender": cartmaster_identity["gender"], "race": "Goblin",
                "portrait": cartmaster_identity.get("portrait_thumbnail") or cartmaster_identity.get("portrait", ""),
                "portrait_full": cartmaster_identity.get("portrait", ""), "portrait_pool": cartmaster_identity.get("portrait_pool", ""),
            })
            def replace_names(text: str) -> str:
                for old, new in old_names.items():
                    text = text.replace(old, new)
                return text
            for objective in battle.get("objectives", []):
                objective["name"] = replace_names(objective.get("name", ""))
            battle["log"] = [replace_names(line) for line in battle.get("log", [])]
            for field in ("victory_title", "victory_description", "victory_log", "continue_log", "completion_log"):
                if isinstance(battle.get(field), str):
                    battle[field] = replace_names(battle[field])


def _equipped_weapon(state: dict, character: dict) -> dict:
    inventory = {item["instance_id"]: item for item in state.get("inventory", [])}
    instance = inventory.get(character.get("equipment", {}).get("weapon"))
    return ITEMS.get(instance.get("item_id"), {}) if instance else {}


def _effective_attribute(state: dict, character: dict, attribute: str) -> int:
    from .game import effective_attribute
    return effective_attribute(state,character,attribute)


def _race_weight(race: str) -> int:
    normalized = str(race or "human").lower().replace(" ", "_")
    if normalized in {"fairy", "pixie", "sprite"}:
        return 1
    if normalized in {"goblin", "kobold", "halfling", "gnome", "slimefolk"}:
        return 2
    if normalized in {"orc", "half_orc", "werewolf", "minotaur", "centaur", "ogre"}:
        return 4
    if normalized in {"troll", "giant", "golem", "dragonkin"}:
        return 5
    return 3


def _player_unit(state: dict, character: dict, x: int, y: int) -> dict:
    weapon = _equipped_weapon(state, character)
    scaling = weapon.get("weapon_scaling", "str")
    weapon_type = weapon.get("weapon_type", "unarmed")
    ranged = weapon_type in {"bow", "crossbow"}
    magical = weapon_type in {"staff", "wand", "grimoire"}
    attack_range = 4 if ranged else 3 if magical else 1
    special = (
        {"id": "precision_shot", "name": "Precision Shot", "range": 5, "description": "Long shot that partially ignores armor.", "elevation_rule": "ballistic"}
        if ranged else
        {"id": "arc_bolt", "name": "Arc Bolt", "range": 4, "description": "A focused magical strike with reliable damage.", "elevation_rule": "ignore"}
        if magical else
        None
    )
    vit = _effective_attribute(state, character, "vit")
    agi = _effective_attribute(state, character, "agi")
    scaling_value = _effective_attribute(state, character, scaling)
    strength = _effective_attribute(state, character, "str")
    combat_training = {"none": 0, "basic": 1, "skilled": 2, "expert": 3, "master": 4}.get(character.get("perks", {}).get("combat", "none"), 0)
    race = character.get("race", "Human")
    racial = race_gameplay(race)
    perks = modifiers(state,character,ITEMS,'combat')
    base_hp = 24 + vit * 4
    max_hp = max(8, round(base_hp * float(racial["hp_multiplier"])) + int(racial["hp_bonus"])) + perks.get('hp',0)
    return {
        "id": character["id"], "name": character.get("name", "Adventurer"), "team": "player",
        "x": x, "y": y, "hp": max_hp, "max_hp": max_hp,
        "armor": max(0, vit // 3 + int(racial["armor_bonus"])) + perks.get('armor',0),
        "move": max(2, min(8, 3 + (1 if agi >= 8 else 0) + int(racial["move_bonus"]) + perks.get('move',0))),
        "initiative": 10 + agi + int(racial["initiative_bonus"]) + perks.get('initiative',0), "attack_range": attack_range,
        "evasion": int(racial["evasion"]) + perks.get('evasion',0), "movement_type": racial["movement_type"],
        "perk_modifiers":perks,
        "racial_resistances": list(racial["resistances"]), "racial_weaknesses": list(racial["weaknesses"]),
        "race": race, "race_summary": racial["summary"],
        "strength": strength, "weight": _race_weight(character.get("race", "human")),
        "attack": 5 + scaling_value // 2 + int(weapon.get("power", 0)) + combat_training,
        "attack_elevation_rule": "ballistic" if ranged else "ignore" if magical else "melee",
        "nonlethal_capable": weapon_type in {"unarmed", "hammer", "club", "mace"} or "nonlethal" in weapon.get("tags", []),
        "weapon": weapon.get("name", "Unarmed"), "scaling": scaling,
        "portrait": character.get("portrait_thumbnail") or character.get("portrait", ""),
        "special": special, "special_used": False, "guarding": False,
        "moved": False, "acted": False, "alive": True, "conscious": True, "condition": "active",
        "statuses": [], "carrying": None, "carrying_object": None, "carried_by": None, "panicked": False, "fled": False,
        "loyalty": 100 if character.get("is_player") or character["id"] == "player" else int(character.get("loyalty", 100)),
        "player_avatar": bool(character.get("is_player") or character["id"] == "player"),
    }


def _enemy(enemy_id: str, name: str, kind: str, x: int, y: int, portrait: dict | None = None) -> dict:
    definitions = {
        "chieftain": (28, 2, 4, 18, 1, "Jagged Cleaver"),
        "raider": (18, 1, 3, 14, 1, "Scrap Spear"),
        "archer": (14, 0, 3, 16, 4, "Short Bow"),
        "horncaller": (15, 1, 3, 15, 1, "Notched Axe"),
        "reinforcement": (14, 0, 3, 13, 1, "Rusty Blade"),
    }
    hp, armor, move, initiative, attack_range, weapon = definitions[kind]
    attack = {"chieftain": 7, "raider": 5, "archer": 4, "horncaller": 4, "reinforcement": 4}[kind]
    strength = {"chieftain": 11, "raider": 8, "archer": 6, "horncaller": 7, "reinforcement": 7}[kind]
    weight = {"chieftain": 3, "raider": 2, "archer": 2, "horncaller": 2, "reinforcement": 2}[kind]
    portrait = portrait or {}
    racial = race_gameplay("Goblin")
    return {
        "id": enemy_id, "name": name, "kind": kind, "team": "enemy",
        "x": x, "y": y, "hp": hp, "max_hp": hp, "armor": armor,
        "move": max(2, move + int(racial["move_bonus"])),
        "initiative": initiative + int(racial["initiative_bonus"]), "attack_range": attack_range, "attack": attack,
        "evasion": int(racial["evasion"]), "movement_type": racial["movement_type"],
        "racial_resistances": list(racial["resistances"]), "racial_weaknesses": list(racial["weaknesses"]),
        "strength": strength, "weight": weight,
        "weapon": weapon,
        "portrait": portrait.get("portrait_thumbnail") or portrait.get("portrait", ""),
        "portrait_full": portrait.get("portrait", ""),
        "portrait_pool": portrait.get("portrait_pool", ""),
        "gender": portrait.get("gender", ""), "race": "Goblin",
        "guarding": False,
        "attack_elevation_rule": "ballistic" if kind == "archer" else "melee",
        "moved": False, "acted": False, "alive": True, "conscious": True, "condition": "active",
        "statuses": [], "carrying": None, "carrying_object": None, "carried_by": None, "panicked": False, "fled": False,
    }


def create_goblin_warcamp_battle(state: dict, party_ids: list[str], seed: str, defer_start: bool = False) -> dict:
    characters = {character["id"]: character for character in state.get("characters", [])}
    starts = [(1, 7), (2, 7), (0, 7), (3, 7)]
    units = {
        character_id: _player_unit(state, characters[character_id], *starts[index])
        for index, character_id in enumerate(party_ids)
    }
    rng = random.Random(seed)
    chief_name, chief_gender, chief_portrait = _goblin_chieftain_identity(rng)
    chief_portrait["gender"] = chief_gender
    guard_identity = _goblin_npc_identity(seed, "gob_guard")
    archer_identity = _goblin_npc_identity(seed, "gob_archer", "scout")
    horn_identity = _goblin_npc_identity(seed, "gob_horn")
    enemies = [
        _enemy("gob_chief", chief_name, "chieftain", 4, 1, chief_portrait),
        _enemy("gob_guard", guard_identity["name"], "raider", 3, 2, guard_identity),
        _enemy("gob_archer", archer_identity["name"], "archer", 6, 2, archer_identity),
        _enemy("gob_horn", horn_identity["name"], "horncaller", 6, 4, horn_identity),
    ]
    units.update({unit["id"]: unit for unit in enemies})
    order = sorted(units, key=lambda uid: (-(units[uid]["initiative"] + rng.random()), uid))
    battle = {
        **compile_battle_map("goblin_warcamp"),
        "version": 1, "encounter_id": "goblin_warcamp", "name": "Goblin Warcamp",
        "round": 1, "turn_index": 0, "turn_order": order,
        "units": units,
        "objects": {
            "prisoner_pen": {"id": "prisoner_pen", "name": "Prisoner Pen", "x": 5, "y": 5,
                             "state": "locked", "footprint": [2, 2], "rotation": 0},
            "alarm_horn": {"id": "alarm_horn", "name": "Alarm Horn", "x": 7, "y": 1, "state": "active"},
            "supply_crate": {"id": "supply_crate", "name": "Loose Supply Crate", "x": 0, "y": 6, "state": "ground", "portable": True, "blocking": False, "weight": 4, "impact_damage": 5, "carry_penalty": 1, "breaks_on_throw": True, "icon": "📦"},
            "loose_stone": {"id": "loose_stone", "name": "Loose Camp Stone", "x": 3, "y": 6, "state": "ground", "portable": True, "blocking": False, "weight": 1, "impact_damage": 2, "carry_penalty": 0, "breaks_on_throw": False, "icon": "●"},
        },
        "objectives": [
            {"id": "chieftain", "name": f"Defeat {chief_name}", "required": True, "complete": False},
            {"id": "captives", "name": "Free the captives", "required": False, "complete": False},
            {"id": "alarm", "name": "Disable the alarm horn", "required": False, "complete": False},
        ],
        "status": "active", "outcome": None, "reinforcements_spawned": False,
        "battle_won": False, "decision_pending": False, "victory_phase": None,
        "battlefield_secured": False, "auto_looted_ids": [], "retreat_all": False,
        "log": [f"The party enters through the south approach. {chief_name} is inside the palisade. The captives and alarm horn are on opposite sides of the camp."],
        "seed": seed, "action_count": 0,
    }
    if not defer_start:
        _advance_to_player(battle)
    return battle


def create_captive_cart_battle(state: dict, party_ids: list[str], seed: str, defer_start: bool = False) -> dict:
    """Build the first extraction-first encounter with a live-capture bonus."""
    characters = {character["id"]: character for character in state.get("characters", [])}
    starts = [(1, 4), (1, 5), (0, 4), (0, 5)]
    units = {
        character_id: _player_unit(state, characters[character_id], *starts[index])
        for index, character_id in enumerate(party_ids)
    }
    courier_identity, cartmaster_identity = _captive_cart_identities(seed)
    courier_name = courier_identity["name"]
    cartmaster_name = cartmaster_identity["name"]
    courier = _enemy("captive_courier", courier_name, "archer", 8, 4, courier_identity)
    courier.update({
        "team": "neutral", "hp": 8, "max_hp": 18, "alive": True, "conscious": False,
        "condition": "unconscious", "weapon": "None", "attack": 0, "capture_role": "rescue",
        "weight": 3, "race": "Human", "gender": courier_identity["gender"],
    })
    cartmaster = _enemy("cartmaster_vrak", cartmaster_name, "raider", 7, 3, cartmaster_identity)
    cartmaster.update({
        "kind": "cartmaster", "boss": True, "hp": 24, "max_hp": 24,
        "armor": 2, "attack": 6, "strength": 9, "capture_role": "live_target",
    })
    guard_one = _goblin_npc_identity(seed, "cart_guard_1")
    guard_two = _goblin_npc_identity(seed, "cart_guard_2")
    cart_archer = _goblin_npc_identity(seed, "cart_archer", "scout")
    enemies = [
        cartmaster,
        _enemy("cart_guard_1", guard_one["name"], "raider", 6, 2, guard_one),
        _enemy("cart_guard_2", guard_two["name"], "raider", 6, 5, guard_two),
        _enemy("cart_archer", cart_archer["name"], "archer", 8, 2, cart_archer),
    ]
    units.update({unit["id"]: unit for unit in [courier, *enemies]})
    rng = random.Random(seed)
    active_ids = [unit_id for unit_id, unit in units.items() if unit["team"] != "neutral"]
    order = sorted(active_ids, key=lambda uid: (-(units[uid]["initiative"] + rng.random()), uid))
    battle = {
        **compile_battle_map("captive_cart_road"),
        "version": 1, "encounter_id": "goblin_captive_cart", "name": "The Captive Cart",
        "round": 1, "turn_index": 0, "turn_order": order,
        "units": units,
        "objects": {
            "dispatch_satchel": {"id": "dispatch_satchel", "name": "Stolen Dispatch Satchel", "x": 7, "y": 5, "state": "ground", "portable": True, "blocking": False, "weight": 1, "impact_damage": 1, "carry_penalty": 0, "breaks_on_throw": False, "objective_item": True, "icon": "▣"},
            "loose_wheel": {"id": "loose_wheel", "name": "Loose Wagon Wheel", "x": 5, "y": 2, "state": "ground", "portable": True, "blocking": False, "weight": 3, "impact_damage": 4, "carry_penalty": 1, "breaks_on_throw": False, "icon": "◉"},
        },
        "objectives": [
            {"id": "rescue_courier", "name": f"Extract {courier_name} alive", "required": True, "complete": False},
            {"id": "capture_cartmaster", "name": f"Capture {cartmaster_name} alive", "required": False, "complete": False},
            {"id": "recover_satchel", "name": "Recover the stolen dispatch satchel", "required": False, "complete": False},
        ],
        "status": "active", "outcome": None, "reinforcements_spawned": False,
        "battle_won": False, "decision_pending": False, "victory_phase": None,
        "battlefield_secured": False, "auto_looted_ids": [], "retreat_all": False,
        "victory_title": f"{courier_name} is safe.",
        "victory_description": f"Withdraw with the rescue secured, or stay to capture {cartmaster_name} and recover the stolen dispatches.",
        "claim_victory_label": "Complete Extraction",
        "continue_log": f"With {courier_name} safe, the guild turns back toward the cart to pursue {cartmaster_name} and the stolen dispatches.",
        "log": [f"The guild springs its ambush beside the captive cart. {courier_name} lies wounded near the wagon; {cartmaster_name} and the stolen dispatch satchel are still inside the escort line."],
        "seed": seed, "action_count": 0,
    }
    if not defer_start:
        _advance_to_player(battle)
    return battle


def create_smoke_signals_battle(state: dict, party_ids: list[str], seed: str, defer_start: bool = False) -> dict:
    """Create the combat branch of the E-rank hedgerow investigation."""
    map_data = compile_generated_battle_map("hedgerow_signal_site", seed)
    characters = {character["id"]: character for character in state.get("characters", [])}
    player_starts = [(entry["x"], entry["y"]) for entry in map_data["spawn_zones"]["player"]]
    enemy_starts = [(entry["x"], entry["y"]) for entry in map_data["spawn_zones"]["enemy"]]
    units = {
        character_id: _player_unit(state, characters[character_id], *player_starts[index])
        for index, character_id in enumerate(party_ids)
    }
    leader_identity = _goblin_npc_identity(seed, "signal_captain", "scout")
    runner_identity = _goblin_npc_identity(seed, "signal_runner", "scout")
    knife_identity = _goblin_npc_identity(seed, "hedgerow_knife")
    captain = _enemy("signal_captain", leader_identity["name"], "archer", *enemy_starts[4], leader_identity)
    captain.update({"boss": True, "hp": 18, "max_hp": 18, "attack": 5, "capture_role": "signal_leader"})
    enemies = [
        captain,
        _enemy("signal_runner", runner_identity["name"], "archer", *enemy_starts[1], runner_identity),
        _enemy("hedgerow_knife", knife_identity["name"], "raider", *enemy_starts[7], knife_identity),
    ]
    units.update({unit["id"]: unit for unit in enemies})
    rng = random.Random(seed)
    order = sorted(units, key=lambda uid: (-(units[uid]["initiative"] + rng.random()), uid))
    chart_x, chart_y = enemy_starts[3]
    battle = {
        **map_data,
        "version": 1, "encounter_id": "goblin_smoke_signals", "name": "Smoke over the Hedgerows",
        "round": 1, "turn_index": 0, "turn_order": order, "units": units,
        "objects": {
            "signal_chart": {"id": "signal_chart", "name": "Marked Farm Chart", "x": chart_x, "y": chart_y,
                             "state": "ground", "portable": True, "blocking": False, "weight": 1,
                             "impact_damage": 1, "carry_penalty": 0, "breaks_on_throw": True,
                             "objective_item": True, "icon": "▤"},
        },
        "objectives": [
            {"id": "signal_captain", "name": f"Break {captain['name']}'s signal crew", "required": True, "complete": False},
            {"id": "signal_chart", "name": "Recover the marked farm chart", "required": False, "complete": False},
        ],
        "status": "active", "outcome": None, "reinforcements_spawned": False,
        "battle_won": False, "decision_pending": False, "victory_phase": None,
        "battlefield_secured": False, "auto_looted_ids": [], "retreat_all": False,
        "victory_title": "The signal crew is broken.",
        "victory_description": "Leave with the investigation secured, or pursue the fleeing scouts and recover their marked chart.",
        "claim_victory_label": "End the Investigation",
        "victory_log": f"{captain['name']} falls and the other scouts run for the far hedgerow.",
        "completion_log": "The investigators return to Fortcamp before another signal crew can erase the site.",
        "log": [f"The smoke trail leads into an ambush. {captain['name']} orders the scouts to seize the investigators' notes."],
        "seed": seed, "action_count": 0,
    }
    if not defer_start:
        _advance_to_player(battle)
    return battle


def _equipped_tags_and_perks(state: dict, character: dict) -> tuple[set[str], set[str]]:
    inventory = {item["instance_id"]: item for item in state.get("inventory", [])}
    tags: set[str] = set()
    perks = set(character.get("traits", []))
    for instance_id in character.get("equipment", {}).values():
        instance = inventory.get(instance_id)
        item = ITEMS.get(instance.get("item_id"), {}) if instance else {}
        tags.update(item.get("tags", []))
        perks.update(item.get("granted_perks", []))
    return tags, perks


def create_frontier_watch_defense_battle(state: dict, party_ids: list[str], seed: str) -> dict:
    """Prepared defense vertical slice used by Private Contracts."""
    map_data = compile_generated_battle_map("frontier_watch_defense", seed)
    characters = {character["id"]: character for character in state.get("characters", [])}
    starts = [(entry["x"], entry["y"]) for entry in map_data["spawn_zones"]["player"]]
    enemy_starts = [(entry["x"], entry["y"]) for entry in map_data["spawn_zones"]["enemy"]]
    units = {
        character_id: _player_unit(state, characters[character_id], *starts[index])
        for index, character_id in enumerate(party_ids)
    }
    objective = map_data["objective_position"]
    keeper = {
        "id": "watch_keeper", "name": "Keeper Mara Fen", "team": "player", "kind": "protected",
        "x": objective["x"], "y": objective["y"], "hp": 24, "max_hp": 24, "armor": 1,
        "move": 0, "initiative": 0, "attack_range": 1, "attack": 2, "evasion": 0,
        "movement_type": "ground", "racial_resistances": [], "racial_weaknesses": [],
        "strength": 5, "weight": 3, "weapon": "Watch Spear", "portrait": "", "race": "Human",
        "guarding": False, "attack_elevation_rule": "melee", "moved": False, "acted": False,
        "alive": True, "conscious": True, "condition": "active", "statuses": [], "carrying": None,
        "carrying_object": None, "carried_by": None, "panicked": False, "fled": False,
        "defense_objective": True,
    }
    units[keeper["id"]] = keeper

    enemy_count = min(7, max(4, len(party_ids) + 2))
    enemy_kinds = ["raider", "raider", "archer", "raider", "archer", "horncaller", "raider"]
    for index in range(enemy_count):
        unit_id = f"watch_raider_{index + 1}"
        identity = _goblin_npc_identity(seed, unit_id, "scout" if enemy_kinds[index] == "archer" else "fighter")
        enemy = _enemy(unit_id, identity["name"], enemy_kinds[index], *enemy_starts[index], identity)
        units[unit_id] = enemy

    available = [
        {"id": "barricade", "name": "Wooden Barricade", "cost": 2, "limit": 2,
         "description": "Blocks movement and sight until attackers destroy its 12 HP."},
        {"id": "spike_trap", "name": "Spike Trap", "cost": 1, "limit": 3,
         "description": "Hidden until an enemy enters its tile, then deals 4 damage."},
    ]
    base_budget = 4 + len(party_ids) * 2
    defense_bonus = min(3, sum(max(0, int(race_gameplay(characters[cid].get("race", "Human"))["form_bonuses"].get("defense", 0))) for cid in party_ids))
    all_tags: set[str] = set()
    all_perks: set[str] = set()
    for character_id in party_ids:
        tags, perks = _equipped_tags_and_perks(state, characters[character_id])
        all_tags.update(tags); all_perks.update(perks)
    if "Kobold" in {characters[cid].get("race") for cid in party_ids} or "trapper" in all_perks or "trapping_gear" in all_tags:
        available.append({
            "id": "snare_trap", "name": "Iron-Jaw Snare", "cost": 2, "limit": 2,
            "description": "Deals 2 damage and stops an enemy's next movement. Unlocked by a Kobold, Trapper, or trapping gear.",
        })
    if "engineer" in all_perks or "construction_gear" in all_tags or "field_fortifier" in all_perks:
        available.append({
            "id": "watch_platform", "name": "Raised Watch Platform", "cost": 3, "limit": 1,
            "description": "Adds two levels of elevation for a ranged firing position. Unlocked by an Engineer or construction gear.",
        })
    gear_bonus = 2 if "defense_gear" in all_tags or "field_fortifier" in all_perks else 0
    budget = base_budget + defense_bonus + gear_bonus
    rng = random.Random(seed)
    order_ids = [*party_ids, *(unit_id for unit_id in units if units[unit_id]["team"] == "enemy")]
    order = sorted(order_ids, key=lambda uid: (-(units[uid]["initiative"] + rng.random()), uid))
    return {
        **map_data,
        "version": 1, "encounter_id": "frontier_watch_defense", "name": "Hold the Hedgerow Watch",
        "round": 1, "turn_index": 0, "turn_order": order, "units": units, "objects": {},
        "objectives": [
            {"id": "protect_keeper", "name": f"Keep {keeper['name']} alive", "required": True, "complete": False},
            {"id": "break_attack", "name": "Defeat the raiding party", "required": True, "complete": False},
        ],
        "status": "preparing", "outcome": None, "reinforcements_spawned": False,
        "battle_won": False, "decision_pending": False, "victory_phase": None,
        "battlefield_secured": False, "auto_looted_ids": [], "retreat_all": False,
        "preparation": {
            "budget": budget, "remaining": budget, "base_budget": base_budget,
            "race_bonus": defense_bonus, "gear_bonus": gear_bonus,
            "zone": map_data["preparation_zone"], "deployment_zone": map_data["deployment_zone"],
            "available": available, "placements": [],
        },
        "log": [
            f"Scouts give the guild time to prepare the Hedgerow Watch. Place defenses and deploy the party before the raiders arrive. Preparation budget: {budget}."
        ],
        "seed": seed, "action_count": 0,
    }


def create_contract_battle(state: dict, party_ids: list[str], seed: str, mission_id: str, defer_start: bool = False) -> dict:
    spec = TACTICAL_CONTRACTS[mission_id]
    mission = MISSION_TEMPLATES[mission_id]
    board = compile_generated_battle_map(f"contract_{spec['layout']}", seed)
    characters = {c["id"]: c for c in state["characters"]}
    units = {cid: _player_unit(state, characters[cid], tile["x"], tile["y"])
             for cid, tile in zip(party_ids, board["spawn_zones"]["player"])}
    tier = {"E":0,"D":0,"C":1,"B":2,"A":3,"S":4}[mission["rank"]]
    count = min(8, 3 + tier + (1 if tier else 0))
    rng = random.Random(f"contract:{seed}")
    race = spec["race"]
    racial = race_gameplay(race)
    used_names = set()
    for index, tile in enumerate(board["spawn_zones"]["enemy"][:count]):
        uid = f"contract_enemy_{index}"
        kind = "chieftain" if index == 0 else "archer" if index % 3 == 0 else "raider"
        if race in {"Goblin", "Hobgoblin"}:
            identity = _goblin_npc_identity(seed, uid, "scout" if kind == "archer" else "fighter")
            name = identity["name"]
        else:
            gender = rng.choice(("male", "female"))
            name = rng.choice(("Tarin","Nessa","Rovan","Mira","Kellan","Sera","Veyra","Darin")) + " " + rng.choice(("Hale","Voss","Carrow","Fen","Rook","Vale"))
            identity = choose_pool_portrait(portrait_pool_key(race,gender,"scout" if kind == "archer" else "fighter"),rng) or {}
            identity["gender"] = gender
        if name in used_names:
            name += " " + ("Ash","Reed","Iron","Thorn","Flint","Oak","Stone","Moss")[index]
        used_names.add(name)
        if race == "Hobgoblin":
            identity = {**choose_pool_portrait(portrait_pool_key(race,identity.get("gender","male"),"scout" if kind == "archer" else "fighter"),rng), "gender":identity.get("gender","male")}
        hp = max(8,round(((23 if index == 0 else 14) + tier * (5 if index == 0 else 3))*float(racial["hp_multiplier"]))+int(racial["hp_bonus"]))
        unit = _enemy(uid,name,kind,tile["x"],tile["y"],identity)
        unit.update({"race":race,"boss":index == 0,"hp":hp,"max_hp":hp,
            "armor":max(0,(2 if index == 0 else 0)+tier//2+int(racial["armor_bonus"])),"attack":(5 if index == 0 else 4)+tier,
            "move":3+int(racial["move_bonus"])+(1 if spec.get("mounted") else 0),
            "initiative":14+int(racial["initiative_bonus"])+index,
            "evasion":int(racial["evasion"]),"movement_type":racial["movement_type"],
            "racial_resistances":list(racial["resistances"]),"racial_weaknesses":list(racial["weaknesses"]),
            "weight":_race_weight(race),
            "weapon":"Short Bow" if kind == "archer" else "Chapel Blade" if race == "Undead" else "Raider Spear",
            "corpse_item":"short_bow" if kind == "archer" else "rusty_knife",
            "corpse_item_chance":35 if index == 0 else 25})
        units[uid] = unit
    commander = units["contract_enemy_0"]
    return_battle = {**board,"version":1,"encounter_id":f"contract:{mission_id}","name":mission["name"],
        "round":1,"turn_index":0,"turn_order":sorted(units,key=lambda uid:(-units[uid]["initiative"],uid)),
        "units":units,"objects":{},"primary_target_id":commander["id"],
        "leader_target":bool(spec.get("leader_target")),"capture_bonus":race != "Undead",
        "objectives":[{"id":"route","name":f"Defeat or subdue {commander['name']}" if spec.get("leader_target") else f"Break the {spec['faction']}","required":True,"complete":False},
                      {"id":"clean_extraction","name":mission["combat_critical_condition"],"required":False,"complete":False}],
        "status":"active","outcome":None,"reinforcements_spawned":False,
        "battle_won":False,"decision_pending":False,"victory_phase":None,
        "battlefield_secured":False,"auto_looted_ids":[],"retreat_all":False,
        "log":[f"{mission['description']} The {spec['faction']} hold the far approach. The guild can withdraw through the western approach."],
        "seed":seed,"action_count":0}
    if not defer_start:
        _advance_to_player(return_battle)
    return return_battle


def _check_contract_end(battle: dict) -> None:
    commander = battle["units"][battle["primary_target_id"]]
    # An escaped commander never counts as a defeated target.
    stopped = commander.get("condition") in {"dead","unconscious"}
    clear = not _living(battle,"enemy")
    objective = stopped if battle["leader_target"] else clear
    battle["objectives"][0]["complete"] = objective
    if objective:
        if clear:
            battle["battlefield_secured"] = True
            _secure_battlefield_loot(battle)
        party = [u for u in battle["units"].values() if u["team"] == "player"]
        captured = commander.get("condition") == "unconscious" and (clear or commander.get("extracted"))
        battle["objectives"][1]["complete"] = clear and all(u.get("alive") and u.get("conscious",True) for u in party) and (captured or not battle["capture_bonus"])
        battle["victory_title"] = "The contract objective is secured"
        battle["victory_description"] = "Leave with secured rewards, or continue to recover prisoners and defeat the remaining opposition."
        _trigger_battle_victory(battle,panic_enemies=battle["leader_target"])
    if not _living(battle,"player") and battle.get("status") == "active":
        escaped = any(u.get("extracted") for u in battle["units"].values() if u["team"] == "player")
        battle.update(status="complete",decision_pending=False,
                      outcome=_victory_outcome(battle) if objective and escaped else "failure" if escaped else "critical_failure")


def create_battle(state: dict, party_ids: list[str], seed: str, encounter_id: str, defer_start: bool = False) -> dict:
    if encounter_id.startswith("contract:"):
        return create_contract_battle(state, party_ids, seed, encounter_id.split(":", 1)[1], defer_start=defer_start)
    factories = {
        "goblin_warcamp": create_goblin_warcamp_battle,
        "goblin_captive_cart": create_captive_cart_battle,
        "goblin_smoke_signals": create_smoke_signals_battle,
        "frontier_watch_defense": create_frontier_watch_defense_battle,
    }
    if encounter_id not in factories:
        raise ValueError(f"Tactical encounter {encounter_id!r} is not implemented")
    return factories[encounter_id](state, party_ids, seed) if encounter_id == "frontier_watch_defense" else factories[encounter_id](state, party_ids, seed, defer_start=defer_start)


def _combat_active(unit: dict) -> bool:
    return bool(unit.get("alive") and unit.get("conscious", True) and not unit.get("extracted") and not unit.get("carried_by"))


def _living(battle: dict, team: str | None = None) -> list[dict]:
    return [unit for unit in battle["units"].values() if _combat_active(unit) and (team is None or unit["team"] == team)]


def _terrain_at(battle: dict, x: int, y: int) -> list[dict]:
    return [tile for tile in battle.get("terrain", []) if (x, y) in occupied_tiles(tile)]


def _distance_to_entity(unit: dict, entity: dict) -> int:
    return min(abs(int(unit["x"]) - x) + abs(int(unit["y"]) - y) for x, y in occupied_tiles(entity))


def _player_exit_tiles(battle: dict) -> set[tuple[int, int]]:
    """Every authored EXIT is valid for guild withdrawal and handoff."""
    return {
        (int(tile["x"]), int(tile["y"]))
        for route in (battle.get("extraction", {}), battle.get("enemy_extraction", {}))
        for tile in route.get("tiles", [])
    }


def _ground_at(battle: dict, x: int, y: int) -> tuple[str, dict]:
    tile = next((tile for tile in battle.get("ground_tiles", []) if tile["x"] == x and tile["y"] == y), None)
    material = tile.get("material", "grass") if tile else "grass"
    return material, battle.get("ground_materials", {}).get(material, {})


def _blocked(
    battle: dict, x: int, y: int, ignore_unit: str | None = None,
    movement_type: str | None = None,
) -> bool:
    if x < 0 or y < 0 or x >= battle["width"] or y >= battle["height"]:
        return True
    if any(
        tile.get("blocking") and not tile.get("destroyed")
        and not (tile.get("requires_flying") and movement_type == "flying")
        for tile in _terrain_at(battle, x, y)
    ):
        return True
    if movement_type != "flying" and any(tile["x"] == x and tile["y"] == y for tile in battle.get("void_tiles", [])):
        return True
    if any(
        (x, y) in occupied_tiles(obj) and obj.get("blocking", True)
        and not obj.get("carried_by") and obj.get("state") not in {"broken", "removed"}
        for obj in battle.get("objects", {}).values()
    ):
        return True
    if any(tile["x"] == x and tile["y"] == y and tile.get("impassable") for tile in battle.get("elevation", [])):
        return True
    return any(
        unit["id"] != ignore_unit and _combat_active(unit)
        and unit["x"] == x and unit["y"] == y
        for unit in battle["units"].values()
    )


def _movement_limit(unit: dict) -> int:
    penalty = int(unit.get("carried_payload_penalty", 2 if unit.get("carrying") else 0))
    return max(1, int(unit["move"]) - penalty)


def _carry_penalty(unit: dict, weight: int) -> int:
    capacity = max(1, int(unit.get("strength", 5)) // 3)
    return max(0, min(3, int(weight) - capacity + 1))


def _tile_height(battle: dict, x: int, y: int) -> int:
    tile = next((tile for tile in battle.get("elevation", []) if tile["x"] == x and tile["y"] == y), None)
    return int(tile.get("height", 0)) if tile else 0


def _can_step(battle: dict, x: int, y: int, nx: int, ny: int, unit: dict) -> bool:
    if _blocked(battle, nx, ny, unit["id"], unit.get("movement_type")):
        return False
    if unit.get("movement_type") == "flying":
        return True
    return abs(_tile_height(battle, nx, ny) - _tile_height(battle, x, y)) <= 2


def _step_cost(battle: dict, x: int, y: int, nx: int, ny: int, unit: dict) -> int:
    if unit.get("movement_type") == "flying":
        return 1
    climb = _tile_height(battle, nx, ny) - _tile_height(battle, x, y)
    elevation_cost = max(1, climb * 2)
    _, ground = _ground_at(battle, nx, ny)
    terrain_cost = max(
        [int(tile.get("movement_cost", 1)) for tile in _terrain_at(battle, nx, ny) if not tile.get("destroyed")]
        + [int(tile.get("destroyed_movement_cost", 1)) for tile in _terrain_at(battle, nx, ny) if tile.get("destroyed")]
        + [int(ground.get("movement_cost", 1))]
        + [1]
    )
    return elevation_cost + terrain_cost - 1


def _distance(a: dict, b: dict) -> int:
    return abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])


def _line_of_sight(battle: dict, attacker: dict, target: dict) -> bool:
    """Bresenham trace; blocking terrain stops ranged attacks."""
    x0, y0, x1, y1 = attacker["x"], attacker["y"], target["x"], target["y"]
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    error = dx + dy
    x, y = x0, y0
    while (x, y) != (x1, y1):
        twice = 2 * error
        if twice >= dy:
            error += dy; x += sx
        if twice <= dx:
            error += dx; y += sy
        if (x, y) == (x1, y1):
            return True
        if any(tile.get("blocks_sight", tile.get("blocking", False)) and not tile.get("destroyed") for tile in _terrain_at(battle, x, y)):
            return False
        if _tile_height(battle, x, y) >= max(_tile_height(battle, attacker["x"], attacker["y"]), _tile_height(battle, target["x"], target["y"])) + 2:
            return False
    return True


def _elevation_attack_modifier(battle: dict, attacker: dict, target: dict, rule: str) -> tuple[int, int]:
    """Return accuracy and damage modifiers; magic must select its rule explicitly."""
    if rule != "ballistic":
        return 0, 0
    difference = _tile_height(battle, attacker["x"], attacker["y"]) - _tile_height(battle, target["x"], target["y"])
    if difference > 0:
        return min(20, difference * 8), min(3, difference)
    if difference < 0:
        return -min(40, abs(difference) * 12), 0
    return 0, 0


def _attack_preview(battle: dict, attacker: dict, target: dict, rule: str) -> dict:
    accuracy, damage = _elevation_attack_modifier(battle, attacker, target, rule)
    base = 90 if rule == "ballistic" else 100
    target_evasion = int(target.get("evasion", 0))
    evasion_factor = 1.0 if rule == "ballistic" else .3 if rule == "ignore" else .6
    evasion_penalty = round(target_evasion * evasion_factor)
    return {
        "chance": max(5, min(100, base + accuracy - evasion_penalty + attacker.get('perk_modifiers',{}).get('accuracy',0))), "damage_bonus": damage,
        "target_evasion": target_evasion, "evasion_penalty": evasion_penalty,
        "attacker_height": _tile_height(battle, attacker["x"], attacker["y"]),
        "target_height": _tile_height(battle, target["x"], target["y"]), "elevation_rule": rule,
    }


def _attack_hits(battle: dict, attacker: dict, target: dict, rule: str) -> tuple[bool, dict, int]:
    preview = _attack_preview(battle, attacker, target, rule)
    counter = int(battle.get("roll_counter", 0))
    battle["roll_counter"] = counter + 1
    roll = random.Random(f"{battle.get('seed')}:{counter}:{attacker['id']}:{target['id']}").randint(1, 100)
    return roll <= preview["chance"], preview, roll


def _can_attack(battle: dict, attacker: dict, target: dict, attack_range: int | None = None) -> bool:
    reach = int(attack_range if attack_range is not None else attacker["attack_range"])
    return _distance(attacker, target) <= reach and (reach == 1 or _line_of_sight(battle, attacker, target))


def _reachable(battle: dict, unit: dict, limit: int) -> dict[tuple[int, int], int]:
    found = {(unit["x"], unit["y"]): 0}
    queue = [(0, unit["x"], unit["y"])]
    while queue:
        current_cost, x, y = heapq.heappop(queue)
        if current_cost != found[(x, y)]:
            continue
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if not _can_step(battle, x, y, nx, ny, unit):
                continue
            distance = current_cost + _step_cost(battle, x, y, nx, ny, unit)
            if distance > limit or distance >= found.get((nx, ny), limit + 1):
                continue
            found[(nx, ny)] = distance
            heapq.heappush(queue, (distance, nx, ny))
    return found


def _movement_tree(battle: dict, unit: dict) -> tuple[dict[tuple[int, int], int], dict[tuple[int, int], tuple[int, int] | None]]:
    origin = unit.get("movement_origin") or {"x": unit["x"], "y": unit["y"]}
    start = (int(origin["x"]), int(origin["y"]))
    found = {start: 0}
    parents: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    movement_limit = _movement_limit(unit)
    queue = [(0, start[0], start[1])]
    while queue:
        current_cost, x, y = heapq.heappop(queue)
        if current_cost != found[(x, y)]:
            continue
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if not _can_step(battle, x, y, nx, ny, unit):
                continue
            distance = current_cost + _step_cost(battle, x, y, nx, ny, unit)
            if distance > movement_limit or distance >= found.get((nx, ny), movement_limit + 1):
                continue
            found[(nx, ny)] = distance
            parents[(nx, ny)] = (x, y)
            heapq.heappush(queue, (distance, nx, ny))
    return found, parents


def _movement_path(parents: dict, costs: dict, destination: tuple[int, int]) -> list[dict]:
    path = []
    cursor = destination
    while parents.get(cursor) is not None:
        path.append({"x": cursor[0], "y": cursor[1], "cost": costs[cursor]})
        cursor = parents[cursor]
    path.reverse()
    return path


def _commit_player_movement(battle: dict, unit: dict) -> None:
    origin = unit.get("movement_origin")
    if origin and (int(origin["x"]), int(origin["y"])) != (unit["x"], unit["y"]):
        battle["log"].append(f"{unit['name']} takes position at {unit['x'] + 1},{unit['y'] + 1}.")
    unit.pop("movement_origin", None)
    unit.pop("movement_path", None)
    _apply_tile_entry(battle, unit)


def _apply_tile_entry(battle: dict, unit: dict) -> None:
    """Resolve immediate effects from the tile where a committed move ends."""
    tiles = _terrain_at(battle, unit["x"], unit["y"])
    material, _ = _ground_at(battle, unit["x"], unit["y"])
    if material == "water" or any(tile.get("kind") == "shallow_water" or "water" in tile.get("tags", []) for tile in tiles):
        statuses = unit.get("statuses", [])
        remaining = [status for status in statuses if status.get("id") != "burn"]
        if len(remaining) != len(statuses):
            unit["statuses"] = remaining
            battle["log"].append(f"{unit['name']} stamps out the flames in the shallow water.")
    if unit.get("team") != "enemy":
        return
    for tile in tiles:
        if tile.get("destroyed") or not tile.get("prepared_trap"):
            continue
        damage = int(tile.get("trap_damage", 0))
        unit["hp"] = max(0, int(unit.get("hp", 0)) - damage)
        tile["destroyed"] = True
        trap_name = tile.get("name", "prepared trap")
        if tile.get("trap_effect") == "snare":
            unit["snared_until_round"] = int(battle.get("round", 1)) + 1
            unit.setdefault("statuses", []).append({"id": "bind", "expires_round": unit["snared_until_round"]})
            battle["log"].append(f"{unit['name']} triggers {trap_name}, takes {damage} damage, and is pinned in place.")
        else:
            battle["log"].append(f"{unit['name']} triggers {trap_name} and takes {damage} damage.")
        if unit["hp"] <= 0:
            unit.update({"alive": False, "conscious": False, "condition": "dead", "defeat_weapon": trap_name})
            battle["log"].append(f"{unit['name']} is killed by the prepared defense.")


def _current_unit(battle: dict) -> dict | None:
    _ensure_battle_schema(battle)
    if battle["status"] != "active" or battle.get("decision_pending"):
        return None
    order = battle["turn_order"]
    while order:
        if battle["turn_index"] >= len(order):
            battle["turn_index"] = 0
            battle["round"] += 1
            for unit in _living(battle):
                unit["moved"] = False; unit["acted"] = False; unit["guarding"] = False
                healing=min(unit.get('perk_modifiers',{}).get('regeneration',0),unit['max_hp']-unit['hp'])
                if healing>0:
                    unit['hp']+=healing
                    battle['log'].append(f"{unit['name']} regenerates {healing} HP.")
            alarm = battle.get("objects", {}).get("alarm_horn")
            if battle.get("encounter_id") == "goblin_warcamp" and battle["round"] == 5 and alarm and alarm.get("state") == "active":
                _spawn_reinforcements(battle)
            if battle["round"] > 20:
                battle["status"] = "complete"; battle["outcome"] = "failure"
                battle["log"].append("After twenty rounds, the exhausted party can no longer hold its position and is forced to retreat.")
                return None
        unit = battle["units"].get(order[battle["turn_index"]])
        if unit and _combat_active(unit):
            return unit
        battle["turn_index"] += 1
    return None


def _spawn_reinforcements(battle: dict) -> None:
    if battle.get("reinforcements_spawned"):
        return
    first = _goblin_npc_identity(battle.get("seed", "battle"), "gob_reinforce_1")
    second = _goblin_npc_identity(battle.get("seed", "battle"), "gob_reinforce_2")
    spawned = [
        _enemy("gob_reinforce_1", first["name"], "reinforcement", 0, 1, first),
        _enemy("gob_reinforce_2", second["name"], "reinforcement", 7, 4, second),
    ]
    for unit in spawned:
        if not _blocked(battle, unit["x"], unit["y"]):
            battle["units"][unit["id"]] = unit
            battle["turn_order"].append(unit["id"])
    battle["reinforcements_spawned"] = True
    battle["log"].append("The alarm horn answers across the hills. Warhost reinforcements enter the camp.")


def _deal_damage(
    battle: dict, attacker: dict, target: dict, bonus: int = 0, armor_pierce: int = 0,
    intent: str = "lethal",
) -> int:
    armor = max(0, int(target.get("armor", 0)) - armor_pierce)
    damage = max(1, int(attacker["attack"]) + bonus - armor)
    perks=attacker.get('perk_modifiers',{})
    if target.get('race') in {'Goblin','Hobgoblin','Bugbear'}:damage+=perks.get('damage_goblin',0)
    if target.get('race') in {'Undead','Revenant','Banshee','Vampire'}:damage+=perks.get('damage_deathless',0)
    if attacker.get('attack_elevation_rule')=='melee':damage+=perks.get('melee_damage',0)
    if attacker.get('attack_elevation_rule')=='ignore':
        reduction=target.get('perk_modifiers',{}).get('magic_reduction',0)
        if 'magic' in target.get('racial_resistances',[]):reduction+=20
        if 'magic' in target.get('racial_weaknesses',[]):reduction-=20
        damage=max(1,round(damage*(1-min(60,reduction)/100)))
    if target.get("guarding"):
        damage = max(1, damage // 2)
        target["guarding"] = False
        _record_sound(battle, "shield_block", offset=185)
    target["hp"] = max(0, int(target["hp"]) - damage)
    target["statuses"] = [status for status in target.get("statuses", []) if status.get("id") != "sleep"]
    if target["hp"] <= 0:
        target["conscious"] = False
        target["guarding"] = False
        if intent == "nonlethal":
            target["alive"] = True; target["condition"] = "unconscious"
            battle["log"].append(f"{target['name']} is knocked unconscious.")
        else:
            target["alive"] = False; target["condition"] = "dead"
            battle["log"].append(f"{target['name']} is killed and leaves a recoverable corpse.")
        target["defeated_by"] = attacker.get("name", "")
        target["defeated_by_id"] = attacker.get("id", "")
        target["defeated_round"] = battle.get("round", 1)
        target["defeat_weapon"] = attacker.get("weapon", "")
        if target.get("carrying") in battle["units"]:
            carried = battle["units"][target["carrying"]]
            carried["carried_by"] = None
            target["carrying"] = None
            target.pop("carried_payload_penalty", None)
        if target.get("carrying_object") in battle.get("objects", {}):
            carried_object = battle["objects"][target["carrying_object"]]
            carried_object.update({"x": target["x"], "y": target["y"], "state": "ground", "carried_by": None})
            target["carrying_object"] = None
            target.pop("carried_payload_penalty", None)
    return damage


def _victory_outcome(battle: dict) -> str:
    optional = [objective for objective in battle.get("objectives", []) if not objective.get("required")]
    return "critical_success" if optional and all(objective.get("complete") for objective in optional) and not battle.get("reinforcements_spawned") else "success"


def _panic_unit(unit: dict) -> None:
    unit["panicked"] = True
    if not any(status.get("id") == "panic" for status in unit.get("statuses", [])):
        unit.setdefault("statuses", []).append({"id": "panic"})


def _trigger_battle_victory(battle: dict, panic_enemies: bool = False) -> None:
    if battle.get("battle_won"):
        return
    battle["battle_won"] = True
    battle["decision_pending"] = True
    battle["victory_phase"] = "decision"
    if panic_enemies:
        for enemy in _living(battle, "enemy"):
            _panic_unit(enemy)
    battle["log"].append(battle.get("victory_log", "The required objective is secured. The guild can withdraw or pursue the remaining opportunities."))


def _secure_battlefield_loot(battle: dict) -> None:
    if battle.get("loot_secured"):
        return
    recovered = {
        unit["id"] for unit in battle["units"].values()
        if unit["team"] == "enemy" and unit.get("condition") == "dead" and not unit.get("fled")
    }
    battle["auto_looted_ids"] = sorted(recovered)
    battle["auto_captured_ids"] = sorted(
        unit["id"] for unit in battle["units"].values()
        if unit["team"] == "enemy" and unit.get("condition") == "unconscious" and not unit.get("fled")
    )
    battle["loot_secured"] = True
    battle["log"].append(
        f"The victors strip usable gear and coin from {len(recovered)} fallen enem{'y' if len(recovered) == 1 else 'ies'} and secure every unconscious prisoner."
        if recovered else "The victors secure the camp, but there are no fallen enemies to strip."
    )


def _claim_victory(battle: dict) -> None:
    if not battle.get("battle_won"):
        raise ValueError("Victory has not been secured yet")
    if battle.get("battlefield_secured") or battle.get("encounter_id") == "goblin_warcamp":
        _secure_battlefield_loot(battle)
    battle["decision_pending"] = False
    battle["victory_phase"] = "complete"
    battle["status"] = "complete"
    battle["outcome"] = _victory_outcome(battle)
    battle["log"].append(battle.get("completion_log", "The guild ends the engagement and withdraws with its secured objectives."))


def _check_warcamp_end(battle: dict) -> None:
    chief = battle["units"].get("gob_chief")
    chief_name = chief.get("name", "the goblin chieftain") if chief else "The goblin chieftain"
    battle["objectives"][0]["complete"] = bool(chief and not _combat_active(chief))
    battle["objectives"][1]["complete"] = battle["objects"]["prisoner_pen"]["state"] == "opened"
    battle["objectives"][2]["complete"] = battle["objects"]["alarm_horn"]["state"] == "disabled"
    if chief and not _combat_active(chief):
        battle.setdefault("victory_title", f"{chief_name} has fallen. The warcamp is breaking.")
        battle.setdefault("victory_description", "End the battle and gather the fallen automatically, or pursue the panicked goblins to capture or defeat more before leaving.")
        battle.setdefault("claim_victory_label", "Secure Spoils & Leave")
        battle.setdefault("victory_log", f"{chief_name} falls. The remaining goblins panic. The guild can leave with the victory or pursue them.")
        battle.setdefault("completion_log", "The guild calls the pursuit and leaves the broken warcamp under its control.")
        _trigger_battle_victory(battle, panic_enemies=True)
        if not _living(battle, "enemy"):
            battle["battlefield_secured"] = True
    if not _living(battle, "player"):
        extracted = [unit for unit in battle["units"].values() if unit["team"] == "player" and unit.get("extracted")]
        battle["status"] = "complete"
        if battle.get("battle_won") and extracted:
            _secure_battlefield_loot(battle)
            battle["outcome"] = _victory_outcome(battle)
            battle["log"].append("The surviving party withdraws safely after breaking the warcamp.")
        else:
            battle["outcome"] = "failure" if extracted else "critical_failure"
            battle["log"].append("The surviving party escapes through the south approach. The warcamp remains standing." if extracted else "The last guild fighter falls. The surviving warcamp defenders hold the field.")


def _check_captive_cart_end(battle: dict) -> None:
    courier = battle["units"].get("captive_courier")
    cartmaster = battle["units"].get("cartmaster_vrak")
    courier_name = courier.get("name", "the captive courier") if courier else "The captive courier"
    cartmaster_name = cartmaster.get("name", "the cartmaster") if cartmaster else "the cartmaster"
    satchel = battle.get("objects", {}).get("dispatch_satchel")
    if not _living(battle, "enemy"):
        battle["battlefield_secured"] = True
        _secure_battlefield_loot(battle)
        if courier and courier.get("alive"):
            courier["extracted"] = True
            courier["secured_from_field"] = True
        if cartmaster and cartmaster.get("condition") == "unconscious":
            cartmaster["extracted"] = True
            cartmaster["secured_from_field"] = True
        if satchel and satchel.get("state") == "ground":
            satchel["state"] = "extracted"
            satchel["secured_from_field"] = True
    rescue_complete = bool(courier and courier.get("alive") and courier.get("extracted"))
    capture_complete = bool(
        cartmaster and cartmaster.get("alive") and cartmaster.get("condition") == "unconscious"
        and (cartmaster.get("extracted") or battle.get("battlefield_secured"))
    )
    satchel_complete = bool(satchel and satchel.get("state") == "extracted")
    battle["objectives"][0]["complete"] = rescue_complete
    battle["objectives"][1]["complete"] = capture_complete
    battle["objectives"][2]["complete"] = satchel_complete
    if courier and not courier.get("alive"):
        battle["status"] = "complete"
        battle["outcome"] = "critical_failure"
        battle["decision_pending"] = False
        battle["log"].append(f"{courier_name} dies before extraction. The rescue collapses into a disastrous retreat.")
        return
    if rescue_complete:
        battle.setdefault("victory_log", f"{courier_name} crosses the guild line alive. The rescue is secured; {cartmaster_name} and the dispatches remain optional prizes.")
        battle.setdefault("completion_log", f"The guild withdraws with {courier_name} alive and the Captive Cart operation broken.")
        _trigger_battle_victory(battle)
    if not _living(battle, "player") and battle.get("status") == "active":
        battle["status"] = "complete"
        if rescue_complete:
            _secure_battlefield_loot(battle)
            battle["outcome"] = _victory_outcome(battle)
            battle["log"].append("The last guild fighter clears the ambush line after securing the rescue.")
        else:
            battle["outcome"] = "failure"
            battle["log"].append(f"The guild withdraws without {courier_name}. The captive cart escapes down the warhost road.")


def _check_smoke_signals_end(battle: dict) -> None:
    captain = battle["units"].get("signal_captain")
    chart = battle.get("objects", {}).get("signal_chart", {})
    captain_stopped = bool(captain and not _combat_active(captain))
    battle["objectives"][0]["complete"] = captain_stopped
    battle["objectives"][1]["complete"] = chart.get("state") == "extracted"
    if not _living(battle, "enemy"):
        battle["battlefield_secured"] = True
        if chart.get("state") == "ground":
            chart["state"] = "extracted"
            chart["secured_from_field"] = True
            battle["objectives"][1]["complete"] = True
        _secure_battlefield_loot(battle)
    if captain_stopped:
        _trigger_battle_victory(battle, panic_enemies=True)
    if not _living(battle, "player") and battle.get("status") == "active":
        extracted = [unit for unit in battle["units"].values() if unit["team"] == "player" and unit.get("extracted")]
        battle["status"] = "complete"
        battle["outcome"] = "success" if captain_stopped and extracted else "failure" if extracted else "critical_failure"
        battle["decision_pending"] = False
        battle["log"].append(
            "The surviving investigators carry the warning back to Fortcamp."
            if extracted else "The signal crew destroys the evidence and holds the hedgerow."
        )


def _check_frontier_watch_end(battle: dict) -> None:
    keeper = battle.get("units", {}).get("watch_keeper")
    keeper_safe = bool(keeper and _combat_active(keeper))
    enemies_alive = bool(_living(battle, "enemy"))
    party_alive = any(
        _combat_active(unit) and not unit.get("defense_objective")
        for unit in battle.get("units", {}).values() if unit.get("team") == "player"
    )
    battle["objectives"][0]["complete"] = keeper_safe and not enemies_alive
    battle["objectives"][1]["complete"] = not enemies_alive
    if not keeper_safe:
        battle.update({"status": "complete", "outcome": "critical_failure", "decision_pending": False})
        battle["log"].append("The raiders reach Keeper Mara Fen. With the watch broken, the guild is forced off the road.")
    elif not enemies_alive:
        defenders = [
            unit for unit in battle.get("units", {}).values()
            if unit.get("team") == "player" and not unit.get("defense_objective")
        ]
        flawless = int(keeper.get("hp", 0)) == int(keeper.get("max_hp", 1)) and all(_combat_active(unit) for unit in defenders)
        battle.update({"status": "complete", "outcome": "critical_success" if flawless else "success", "battlefield_secured": True, "decision_pending": False})
        _secure_battlefield_loot(battle)
        battle["log"].append(
            "The line never breaks. Keeper Mara Fen keeps the signal burning while the guild collects the abandoned raider gear."
            if flawless else
            "The last attacker falls or flees. Keeper Mara Fen relights the watch signal while the guild searches the abandoned raider gear."
        )
    elif not party_alive:
        battle.update({"status": "complete", "outcome": "failure", "decision_pending": False})
        battle["log"].append("With the defenders down, Keeper Mara Fen abandons the signal post before the raiders surround it.")


def _check_end(battle: dict) -> None:
    if battle.get("encounter_id", "").startswith("contract:"):
        _check_contract_end(battle)
    elif battle.get("encounter_id") == "goblin_captive_cart":
        _check_captive_cart_end(battle)
    elif battle.get("encounter_id") == "goblin_smoke_signals":
        _check_smoke_signals_end(battle)
    elif battle.get("encounter_id") == "frontier_watch_defense":
        _check_frontier_watch_end(battle)
    else:
        _check_warcamp_end(battle)


def _finish_turn(battle: dict) -> None:
    order = battle.get("turn_order", [])
    index = int(battle.get("turn_index", 0))
    unit = battle["units"].get(order[index]) if index < len(order) else None
    if unit:
        unit.pop("movement_origin", None)
        unit.pop("movement_path", None)
        if _combat_active(unit):
            at_exit = (unit["x"], unit["y"]) in (
                {(int(tile["x"]), int(tile["y"])) for tile in battle.get("enemy_extraction", {}).get("tiles", [])}
                if unit.get("team") == "enemy" else _player_exit_tiles(battle)
            )
            unit["exit_ready"] = at_exit
    battle["turn_index"] += 1
    _check_end(battle)


def _record_movement(battle: dict, unit: dict, start: tuple[int, int], path: list[tuple[int, int]]) -> None:
    if not path:
        return
    battle.setdefault("animation_events", []).append({
        "type": "movement",
        "unit_id": unit["id"],
        "points": [{"x": start[0], "y": start[1]}] + [{"x": x, "y": y} for x, y in path],
        "extracted": False,
    })


def _record_sound(battle: dict, cue: str, offset: int = 0, duration: int = 0) -> None:
    battle.setdefault("animation_events", []).append({
        "type": "sound", "cues": [{"name": cue, "offset": offset}], "duration": duration,
    })


def _record_melee_animation(battle: dict, attacker: dict, target: dict, hit: bool, rule: str | None = None) -> None:
    rule = rule or attacker.get("attack_elevation_rule", "melee")
    if rule != "melee":
        ranged = rule == "ballistic"
        cues = [{"name": "bow_release" if ranged else "magic_cast", "offset": 45},
                {"name": ("arrow_hit" if ranged else "magic_hit") if hit else "attack_miss", "offset": 220}]
        if hit and target.get("condition") in {"dead", "unconscious"}:
            cues.append({"name": "unit_death" if target["condition"] == "dead" else "unit_unconscious", "offset": 350})
        battle.setdefault("animation_events", []).append({"type": "sound", "cues": cues, "duration": 490})
        return
    battle.setdefault("animation_events", []).append({
        "type": "melee_attack", "attacker_id": attacker["id"], "target_id": target["id"], "hit": bool(hit),
        "target_condition": target.get("condition", "active"),
    })


def _move_toward(battle: dict, unit: dict, target: dict) -> None:
    start = (unit["x"], unit["y"])
    goals = {
        (target["x"] + dx, target["y"] + dy)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
        if not _blocked(battle, target["x"] + dx, target["y"] + dy, unit["id"])
    }
    queue = [(0, start[0], start[1])]; parents = {start: None}; costs = {start: 0}; goal = None
    while queue:
        current_cost, x, y = heapq.heappop(queue)
        cell = (x, y)
        if current_cost != costs[cell]:
            continue
        if cell in goals:
            goal = cell; break
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        neighbors.sort(key=lambda point: (abs(point[0] - target["x"]) + abs(point[1] - target["y"]), point))
        for neighbor in neighbors:
            if not _can_step(battle, x, y, neighbor[0], neighbor[1], unit):
                continue
            candidate_cost = current_cost + _step_cost(battle, x, y, neighbor[0], neighbor[1], unit)
            if candidate_cost >= costs.get(neighbor, 10**9):
                continue
            costs[neighbor] = candidate_cost; parents[neighbor] = cell
            heapq.heappush(queue, (candidate_cost, neighbor[0], neighbor[1]))
    if goal is None:
        return
    path = []
    while goal != start:
        path.append(goal); goal = parents[goal]
    path.reverse()
    if path:
        reachable_path = [point for point in path if costs[point] <= _movement_limit(unit)]
        if reachable_path:
            x, y = reachable_path[-1]
            unit["exit_ready"] = False
            unit["x"], unit["y"], unit["moved"] = x, y, True
            _record_movement(battle, unit, start, reachable_path)
            if unit.get("carrying") in battle["units"]:
                carried = battle["units"][unit["carrying"]]
                carried["x"], carried["y"] = x, y
            _apply_tile_entry(battle, unit)


def _move_to_nearest_tile(battle: dict, unit: dict, destinations: list[dict]) -> None:
    start = (unit["x"], unit["y"])
    goals = {(int(tile["x"]), int(tile["y"])) for tile in destinations}
    if start in goals:
        return
    queue = [(0, start[0], start[1])]
    parents = {start: None}
    costs = {start: 0}
    goal = None
    while queue:
        current_cost, x, y = heapq.heappop(queue)
        cell = (x, y)
        if current_cost != costs[cell]:
            continue
        if cell in goals:
            goal = cell
            break
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if not _can_step(battle, x, y, nx, ny, unit):
                continue
            cost = current_cost + _step_cost(battle, x, y, nx, ny, unit)
            if cost >= costs.get((nx, ny), 10**9):
                continue
            costs[(nx, ny)] = cost
            parents[(nx, ny)] = cell
            heapq.heappush(queue, (cost, nx, ny))
    if goal is None:
        return
    path = []
    while goal != start:
        path.append(goal)
        goal = parents[goal]
    path.reverse()
    reachable = [point for point in path if costs[point] <= _movement_limit(unit)]
    if reachable:
        unit["exit_ready"] = False
        unit["x"], unit["y"] = reachable[-1]
        unit["moved"] = True
        _record_movement(battle, unit, start, reachable)
        if unit.get("carrying") in battle["units"]:
            carried = battle["units"][unit["carrying"]]
            carried["x"], carried["y"] = unit["x"], unit["y"]
        _apply_tile_entry(battle, unit)


def _extract_unit(battle: dict, unit: dict, fled: bool = False) -> None:
    unit["extracted"] = True
    unit["fled"] = fled
    unit["acted"] = True
    x, y = int(unit["x"]), int(unit["y"])
    if x == 0: outside = (-1, y)
    elif x == int(battle.get("width", 1)) - 1: outside = (x + 1, y)
    elif y == 0: outside = (x, -1)
    else: outside = (x, y + 1)
    battle.setdefault("animation_events", []).append({
        "type": "movement", "unit_id": unit["id"],
        "points": [{"x": x, "y": y}, {"x": outside[0], "y": outside[1]}], "extracted": True,
    })
    if unit.get("team") == "player":
        _record_sound(battle, "extraction")
    if not fled and unit.get("carrying") in battle["units"]:
        carried = battle["units"][unit["carrying"]]
        carried["extracted"] = True
        carried["extracted_with"] = unit["id"]
        battle["log"].append(f"{unit['name']} extracts {carried['name']} with them.")
    if unit.get("carrying_object") in battle.get("objects", {}):
        carried_object = battle["objects"][unit["carrying_object"]]
        if fled:
            carried_object.update({"x": unit["x"], "y": unit["y"], "state": "ground", "carried_by": None})
        else:
            carried_object.update({"state": "extracted", "carried_by": None, "extracted_with": unit["id"]})
            battle["log"].append(f"{unit['name']} carries {carried_object['name']} out of the battle.")
        unit["carrying_object"] = None
        unit.pop("carried_payload_penalty", None)
    if fled:
        battle["log"].append(f"{unit['name']} escapes the battlefield in a panic.")
    else:
        battle["log"].append(f"{unit['name']} leaves through an exit.")


def _flee_turn(battle: dict, unit: dict) -> None:
    extraction = battle["enemy_extraction"] if unit["team"] == "enemy" else {
        "name": "the nearest exit",
        "tiles": [{"x": x, "y": y} for x, y in sorted(_player_exit_tiles(battle))],
    }
    tiles = extraction.get("tiles", [])
    exits = {(tile["x"], tile["y"]) for tile in tiles}
    if (unit["x"], unit["y"]) in exits and unit.get("exit_ready"):
        _extract_unit(battle, unit, fled=unit["team"] == "enemy")
    else:
        _move_to_nearest_tile(battle, unit, tiles)
        if (unit["x"], unit["y"]) in exits:
            battle["log"].append(f"{unit['name']} reaches {extraction.get('name', 'an exit')} and prepares to withdraw.")
        else:
            battle["log"].append(f"{unit['name']} runs toward {extraction.get('name', 'an exit')}.")
    _finish_turn(battle)


def _should_party_panic(battle: dict, unit: dict) -> bool:
    if unit["team"] != "player" or unit.get("player_avatar") or int(unit.get("loyalty", 100)) >= 60:
        return False
    health_ratio = int(unit.get("hp", 0)) / max(1, int(unit.get("max_hp", 1)))
    return health_ratio <= .30 and len(_living(battle, "enemy")) > len(_living(battle, "player"))


def _enemy_turn(battle: dict, unit: dict) -> None:
    if unit.get("panicked"):
        _flee_turn(battle, unit)
        return
    targets = _living(battle, "player")
    if not targets:
        _check_end(battle); return
    target = min(targets, key=lambda candidate: (_distance(unit, candidate), candidate["hp"]))
    snared = int(unit.get("snared_until_round", 0)) >= int(battle.get("round", 1))
    if not _can_attack(battle, unit, target) and not snared:
        _move_toward(battle, unit, target)
        target = min(targets, key=lambda candidate: (_distance(unit, candidate), candidate["hp"]))
    if _can_attack(battle, unit, target):
        hit, preview, roll = _attack_hits(battle, unit, target, unit["attack_elevation_rule"])
        if hit:
            damage = _deal_damage(battle, unit, target, preview["damage_bonus"])
            battle["log"].append(f"{unit['name']} attacks {target['name']} with {unit['weapon']} for {damage} damage.")
        else:
            battle["log"].append(f"{unit['name']} misses {target['name']} ({roll} vs {preview['chance']}% accuracy).")
        _record_melee_animation(battle, unit, target, hit)
    elif snared:
        battle["log"].append(f"{unit['name']} struggles against the snare and cannot advance.")
    else:
        battle["log"].append(f"{unit['name']} advances through the warcamp.")
    unit["acted"] = True
    _finish_turn(battle)


def _advance_to_player(battle: dict) -> None:
    safety = 0
    while battle["status"] == "active" and safety < 100:
        unit = _current_unit(battle)
        if not unit:
            return
        if unit["team"] == "player":
            if battle.get("retreat_all") or _should_party_panic(battle, unit):
                if _should_party_panic(battle, unit) and not unit.get("panicked"):
                    _panic_unit(unit)
                    battle["log"].append(f"{unit['name']} loses their nerve and tries to escape.")
                _flee_turn(battle, unit)
                safety += 1
                continue
            return
        _enemy_turn(battle, unit)
        safety += 1


def _player_auto_turn(battle: dict, unit: dict, tactic: str) -> None:
    objective_runner = max(_living(battle, "player"), key=lambda candidate: (candidate["move"], candidate["initiative"], candidate["id"]))
    world_has_active_objects = any(obj["state"] in {"locked", "active"} for obj in battle["objects"].values())
    active_objects = [
        obj for obj in battle["objects"].values() if obj["state"] in {"locked", "active"}
    ] if tactic == "objective" and unit["id"] == objective_runner["id"] else []
    pursuing_objective = False
    if tactic == "objective" and active_objects:
        alarm = battle["objects"].get("alarm_horn")
        objective = (
            alarm if alarm and alarm.get("state") == "active" and battle["round"] < 5
            else min(active_objects, key=lambda obj: abs(unit["x"] - obj["x"]) + abs(unit["y"] - obj["y"]))
        )
        if abs(unit["x"] - objective["x"]) + abs(unit["y"] - objective["y"]) == 1:
            _interact(battle, unit, objective["id"])
            return
        _move_toward(battle, unit, objective)
        pursuing_objective = True
    targets = _living(battle, "enemy")
    if not targets:
        return
    if tactic == "objective" and world_has_active_objects:
        non_chiefs = [candidate for candidate in targets if candidate.get("kind") != "chieftain"]
        if non_chiefs:
            targets = non_chiefs
        else:
            unit["guarding"] = True; unit["acted"] = True
            _record_sound(battle, "guard")
            _record_sound(battle, "guard")
            chief_name = battle.get("units", {}).get("gob_chief", {}).get("name", "the goblin chieftain")
            battle["log"].append(f"{unit['name']} holds back from {chief_name} while the other objectives remain unfinished.")
            _finish_turn(battle)
            return
    in_range = [candidate for candidate in targets if _can_attack(battle, unit, candidate)]
    target_priority = lambda candidate: (
        0 if tactic == "objective" and candidate.get("capture_role") == "live_target" else 1,
        0 if candidate.get("kind") == "chieftain" else 1,
        candidate["hp"],
    )
    target = (
        min(in_range, key=target_priority)
        if in_range else
        min(targets, key=lambda candidate: (target_priority(candidate), _distance(unit, candidate)))
    )
    if not _can_attack(battle, unit, target) and not pursuing_objective:
        _move_toward(battle, unit, target)
    if _can_attack(battle, unit, target):
        nonlethal = tactic == "objective" and target.get("capture_role") == "live_target" and unit.get("nonlethal_capable")
        special = None if nonlethal else unit.get("special")
        bonus = 2 if special and not unit.get("special_used") else 0
        rule = special["elevation_rule"] if bonus else unit["attack_elevation_rule"]
        hit, preview, roll = _attack_hits(battle, unit, target, rule)
        damage = _deal_damage(
            battle, unit, target, bonus + preview["damage_bonus"] - (1 if nonlethal else 0),
            1 if special and special["id"] == "precision_shot" else 0,
            "nonlethal" if nonlethal else "lethal",
        ) if hit else 0
        _record_melee_animation(battle, unit, target, hit, rule)
        if bonus:
            unit["special_used"] = True
        attack_name = "a nonlethal takedown" if nonlethal else "their special attack" if bonus else unit["weapon"]
        battle["log"].append(f"{unit['name']} uses {attack_name} on {target['name']} for {damage} damage." if hit else f"{unit['name']} misses {target['name']} ({roll} vs {preview['chance']}% accuracy).")
    elif tactic == "defensive":
        unit["guarding"] = True
        _record_sound(battle, "guard")
        battle["log"].append(f"{unit['name']} takes a guarded stance.")
    unit["acted"] = True
    _finish_turn(battle)


def _interact(battle: dict, unit: dict, object_id: str) -> None:
    obj = battle["objects"].get(object_id)
    if not obj or _distance_to_entity(unit, obj) != 1:
        raise ValueError("Move next to that object before interacting")
    if object_id == "prisoner_pen" and obj["state"] == "locked":
        obj["state"] = "opened"
        obj.update({"handled_by": unit["name"], "handled_by_id": unit["id"], "handled_round": battle.get("round", 1)})
        battle["log"].append(f"{unit['name']} opens the prisoner pen and directs the captives toward safety.")
    elif object_id == "alarm_horn" and obj["state"] == "active":
        obj["state"] = "disabled"
        obj.update({"handled_by": unit["name"], "handled_by_id": unit["id"], "handled_round": battle.get("round", 1)})
        battle["log"].append(f"{unit['name']} disables the alarm horn before another signal can be sent.")
    else:
        raise ValueError("That object has already been handled")
    _record_sound(battle, "cage_open" if object_id == "prisoner_pen" else "objective_interact")
    unit["acted"] = True
    _finish_turn(battle)
    _check_end(battle)


def _carry_body(battle: dict, unit: dict, target_id: str) -> None:
    if unit.get("carrying") or unit.get("carrying_object"):
        raise ValueError("This unit is already carrying something")
    target = battle["units"].get(target_id)
    if not target or target.get("extracted") or target.get("carried_by"):
        raise ValueError("That body cannot be carried")
    if target.get("conscious", True) or target.get("condition") not in {"unconscious", "dead"}:
        raise ValueError("Only unconscious units or corpses can be carried")
    if _distance(unit, target) > 1:
        raise ValueError("Move onto or next to the body before carrying it")
    unit["carrying"] = target["id"]
    unit["carried_payload_penalty"] = _carry_penalty(unit, int(target.get("weight", 3)))
    target["carried_by"] = unit["id"]
    target["x"], target["y"] = unit["x"], unit["y"]
    battle["log"].append(f"{unit['name']} picks up {target['name']} (weight {target.get('weight', 3)}; movement penalty {unit['carried_payload_penalty']}).")


def _drop_body(battle: dict, unit: dict) -> None:
    target = battle["units"].get(unit.get("carrying"))
    if not target:
        raise ValueError("This unit is not carrying anyone")
    destinations = [
        (unit["x"] + dx, unit["y"] + dy)
        for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1))
        if _can_step(battle, unit["x"], unit["y"], unit["x"] + dx, unit["y"] + dy, unit)
    ]
    if not destinations:
        raise ValueError("There is no adjacent space to drop the body")
    target["x"], target["y"] = destinations[0]
    target["carried_by"] = None
    unit["carrying"] = None
    unit.pop("carried_payload_penalty", None)
    battle["log"].append(f"{unit['name']} puts {target['name']} down.")


def _pickup_object(battle: dict, unit: dict, target_id: str) -> None:
    if unit.get("carrying") or unit.get("carrying_object"):
        raise ValueError("This unit is already carrying something")
    obj = battle.get("objects", {}).get(target_id)
    if not obj or not obj.get("portable") or obj.get("state") != "ground" or obj.get("carried_by"):
        raise ValueError("That object cannot be picked up")
    if _distance_to_entity(unit, obj) != 1:
        raise ValueError("Move next to that object before picking it up")
    unit["carrying_object"] = obj["id"]
    unit["carried_payload_penalty"] = _carry_penalty(unit, int(obj.get("weight", 2)))
    obj["state"] = "carried"
    obj["carried_by"] = unit["id"]
    battle["log"].append(f"{unit['name']} picks up {obj['name']} (weight {obj.get('weight', 2)}).")


def _safe_landing_tile(battle: dict, thrower: dict, target: dict, ignore_unit: str | None = None) -> tuple[int, int] | None:
    dx = 0 if target["x"] == thrower["x"] else (1 if target["x"] > thrower["x"] else -1)
    dy = 0 if target["y"] == thrower["y"] else (1 if target["y"] > thrower["y"] else -1)
    candidates = [(target["x"] + dx, target["y"] + dy)] + [
        (target["x"] + ox, target["y"] + oy) for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1))
    ]
    for x, y in candidates:
        if not _blocked(battle, x, y, ignore_unit):
            return x, y
    return None


def _throw_profile(battle: dict, unit: dict) -> dict | None:
    payload = None
    payload_kind = None
    if unit.get("carrying") in battle["units"]:
        payload = battle["units"][unit["carrying"]]
        payload_kind = "body"
        weight = int(payload.get("weight", 3))
        impact = 2 + weight
    elif unit.get("carrying_object") in battle.get("objects", {}):
        payload = battle["objects"][unit["carrying_object"]]
        payload_kind = "object"
        weight = int(payload.get("weight", 2))
        impact = int(payload.get("impact_damage", 2))
    if not payload:
        return None
    strength = int(unit.get("strength", 5))
    throw_range = max(1, min(5, 1 + strength // 4 - max(0, weight - 2)))
    damage = max(1, impact + strength // 3 + weight // 2)
    return {
        "payload_id": payload["id"], "payload_name": payload["name"], "payload_kind": payload_kind,
        "weight": weight, "strength": strength, "range": throw_range, "damage": damage,
    }


def _drop_object(battle: dict, unit: dict) -> None:
    obj = battle.get("objects", {}).get(unit.get("carrying_object"))
    if not obj:
        raise ValueError("This unit is not carrying an object")
    landing = _safe_landing_tile(battle, unit, unit)
    if not landing:
        raise ValueError("There is no adjacent space to put that object down")
    obj.update({"x": landing[0], "y": landing[1], "state": "ground", "carried_by": None})
    unit["carrying_object"] = None
    unit.pop("carried_payload_penalty", None)
    battle["log"].append(f"{unit['name']} puts {obj['name']} down.")


def _throw_payload(battle: dict, unit: dict, target: dict) -> None:
    profile = _throw_profile(battle, unit)
    if not profile:
        raise ValueError("Pick up an object or body before throwing")
    if not _can_attack(battle, unit, target, profile["range"]):
        raise ValueError("That target is outside this payload's throw range")
    landing = _safe_landing_tile(battle, unit, target, profile["payload_id"] if profile["payload_kind"] == "body" else None)
    if not landing:
        raise ValueError("There is no safe tile where the thrown payload can land")
    impact_source = {
        "id": unit["id"], "name": unit["name"], "attack": profile["damage"],
        "weapon": f"thrown {profile['payload_name'].lower()}",
    }
    damage = _deal_damage(battle, impact_source, target)
    cues = [{"name": "throw_release", "offset": 0}, {"name": "throw_hit", "offset": 220}]
    if target.get("condition") in {"dead", "unconscious"}:
        cues.append({"name": "unit_death" if target["condition"] == "dead" else "unit_unconscious", "offset": 350})
    battle.setdefault("animation_events", []).append({"type": "sound", "cues": cues, "duration": 490})
    if profile["payload_kind"] == "body":
        payload = battle["units"][profile["payload_id"]]
        if payload.get("condition") != "dead":
            _deal_damage(battle, {
                "id": unit["id"], "name": unit["name"], "attack": max(1, profile["damage"] // 2),
                "weapon": "the impact",
            }, payload)
        payload.update({"x": landing[0], "y": landing[1], "carried_by": None})
        unit["carrying"] = None
        unit.pop("carried_payload_penalty", None)
    else:
        payload = battle["objects"][profile["payload_id"]]
        payload.update({"x": landing[0], "y": landing[1], "carried_by": None})
        payload["state"] = "broken" if payload.get("breaks_on_throw") else "ground"
        unit["carrying_object"] = None
        unit.pop("carried_payload_penalty", None)
    battle["log"].append(
        f"{unit['name']} throws {profile['payload_name']} at {target['name']} for {damage} impact damage "
        f"(STR {profile['strength']} vs weight {profile['weight']}, range {profile['range']})."
    )


def _damage_terrain(battle: dict, unit: dict, target_id: str) -> None:
    tile = next((item for item in battle.get("terrain", []) if item.get("id") == target_id), None)
    if not tile or not tile.get("destructible") or tile.get("destroyed"):
        raise ValueError("That terrain cannot be damaged")
    damage = max(1, int(unit.get("attack", 1)) - int(tile.get("armor", 0)))
    tile["hp"] = max(0, int(tile.get("hp", tile.get("max_hp", 10))) - damage)
    battle["log"].append(f"{unit['name']} strikes {tile['name']} for {damage} damage.")
    if tile["hp"] <= 0:
        tile["destroyed"] = True
        tile["original_kind"] = tile.get("kind", "terrain")
        tile["kind"] = tile.get("destroyed_kind", "rubble")
        tile["blocking"] = False
        tile["movement_cost"] = int(tile.get("destroyed_movement_cost", 1))
        battle["log"].append(f"{tile['name']} collapses into {tile['kind'].replace('_', ' ')}.")
    rule = unit.get("attack_elevation_rule", "melee")
    release = "bow_release" if rule == "ballistic" else "melee_swing" if rule == "melee" else "magic_cast"
    battle.setdefault("animation_events", []).append({
        "type": "sound", "duration": 490,
        "cues": [{"name": release, "offset": 45}, {"name": "structure_hit", "offset": 185}]
                + ([{"name": "structure_break", "offset": 300}] if tile.get("destroyed") else []),
    })


def _context_actions(battle: dict, unit: dict) -> list[dict]:
    actions: list[dict] = []
    if not unit.get("acted"):
        for obj in battle.get("objects", {}).values():
            if _distance_to_entity(unit, obj) != 1:
                continue
            if obj["id"] == "prisoner_pen" and obj.get("state") == "locked":
                actions.append({
                    "id": "open_prisoner_pen", "label": "Open Prisoner Pen", "target": obj["name"],
                    "description": "Free the captives in the adjacent pen. Uses the main action and ends this activation.",
                    "cost": "Main action", "hotkey": "I", "command": {"action": "interact", "target_id": obj["id"]},
                })
            elif obj["id"] == "alarm_horn" and obj.get("state") == "active":
                actions.append({
                    "id": "disable_alarm_horn", "label": "Disable Alarm Horn", "target": obj["name"],
                    "description": "Prevent the camp from calling reinforcements. Uses the main action and ends this activation.",
                    "cost": "Main action", "hotkey": "I", "command": {"action": "interact", "target_id": obj["id"]},
                })
            elif obj.get("portable") and obj.get("state") == "ground" and not unit.get("carrying") and not unit.get("carrying_object"):
                profile_strength = int(unit.get("strength", 5))
                weight = int(obj.get("weight", 2))
                actions.append({
                    "id": f"pickup:{obj['id']}", "label": f"Pick Up {obj['name']}",
                    "target": f"Weight {weight}",
                    "description": f"Pick up this throwable object for free. Its throw range and impact use this character's STR {profile_strength} against weight {weight}.",
                    "cost": "Free action", "hotkey": "P", "command": {"action": "pickup_object", "target_id": obj["id"]},
                })
        for target in ([] if unit.get("carrying") or unit.get("carrying_object") else battle["units"].values()):
            if target.get("conscious", True) or target.get("condition") not in {"unconscious", "dead"}:
                continue
            if target.get("carried_by") or target.get("extracted") or _distance(unit, target) > 1:
                continue
            actions.append({
                "id": f"carry:{target['id']}", "label": f"Carry {target['name']}", "target": target["name"],
                "description": f"Pick up this {target['condition']} unit for free. STR {unit.get('strength', 5)} versus weight {target.get('weight', 3)} gives a movement penalty of {_carry_penalty(unit, int(target.get('weight', 3)))}.",
                "cost": "Free action", "hotkey": "C", "command": {"action": "carry", "target_id": target["id"]},
            })
        if unit.get("carrying") in battle["units"]:
            carried = battle["units"][unit["carrying"]]
            actions.append({
                "id": "drop_carried", "label": f"Drop {carried['name']}", "target": carried["name"],
                "description": "Place the carried unit in a safe adjacent tile. Uses the main action and ends this activation.",
                "cost": "Main action", "hotkey": "D", "command": {"action": "drop"},
            })
        if unit.get("carrying_object") in battle.get("objects", {}):
            carried_object = battle["objects"][unit["carrying_object"]]
            actions.append({
                "id": "drop_object", "label": f"Drop {carried_object['name']}", "target": carried_object["name"],
                "description": "Place the carried object in a safe adjacent tile. Uses the main action and ends this activation.",
                "cost": "Main action", "hotkey": "D", "command": {"action": "drop_object"},
            })
    extraction_tiles = _player_exit_tiles(battle)
    if unit.get("carrying") in battle["units"] and (unit["x"], unit["y"]) in extraction_tiles and unit.get("exit_ready"):
        carried = battle["units"][unit["carrying"]]
        actions.insert(0, {
            "id": "extract_carried", "label": f"Extract {carried['name']}", "target": carried["name"],
            "description": "Hand the carried unit over at the exit while remaining in battle. This is free.",
            "cost": "Free action", "hotkey": "X", "command": {"action": "extract_body"},
        })
    return actions


def battle_view(battle: dict) -> dict:
    view = deepcopy(battle)
    current = _current_unit(view)
    view["current_unit_id"] = current["id"] if current else None
    if current and current["team"] == "player":
        reachable, _ = _movement_tree(view, current)
        view["reachable"] = [
            {"x": x, "y": y} for x, y in reachable
        ]
        origin = current.get("movement_origin") or {"x": current["x"], "y": current["y"]}
        view["movement_origin"] = {"x": int(origin["x"]), "y": int(origin["y"])}
        view["movement_path"] = list(current.get("movement_path", []))
        extraction_tiles = _player_exit_tiles(view)
        view["can_extract"] = (current["x"], current["y"]) in extraction_tiles and bool(current.get("exit_ready"))
        view["can_extract_body"] = view["can_extract"] and bool(current.get("carrying"))
        view["can_subdue"] = bool(current.get("nonlethal_capable"))
        view["can_drop"] = bool(current.get("carrying") or current.get("carrying_object"))
        view["context_actions"] = _context_actions(view, current)
        view["carry_targets"] = [
            target["id"] for target in view["units"].values()
            if not target.get("conscious", True) and target.get("condition") in {"unconscious", "dead"}
            and not target.get("carried_by") and not target.get("extracted") and _distance(current, target) == 1
        ]
        view["attack_previews"] = {}
        for target in _living(view, "enemy"):
            standard_valid = not current.get("acted") and _can_attack(view, current, target)
            subdue_valid = (
                not current.get("acted") and current.get("nonlethal_capable")
                and _can_attack(view, current, target, 1)
            )
            skill = current.get("special")
            skill_valid = (
                not current.get("acted") and skill and not current.get("special_used")
                and _can_attack(view, current, target, int(skill["range"]))
            )
            view["attack_previews"][target["id"]] = {
                "attack": _attack_preview(view, current, target, current["attack_elevation_rule"]) if standard_valid else None,
                "subdue": _attack_preview(view, current, target, "melee") if subdue_valid else None,
                "skill": _attack_preview(view, current, target, skill["elevation_rule"]) if skill_valid else None,
            }
        view["terrain_targets"] = [
            tile["id"] for tile in view.get("terrain", [])
            if tile.get("destructible") and not tile.get("destroyed")
            and not current.get("acted") and _can_attack(view, current, tile)
        ]
        throw_profile = _throw_profile(view, current)
        if throw_profile:
            throw_profile["target_ids"] = [
                target["id"] for target in _living(view, "enemy")
                if not current.get("acted") and _can_attack(view, current, target, throw_profile["range"])
            ]
        view["throw_profile"] = throw_profile
    else:
        view["reachable"] = []
        view["movement_origin"] = None
        view["movement_path"] = []
        view["can_extract"] = False
        view["can_extract_body"] = False
        view["can_subdue"] = False
        view["can_drop"] = False
        view["context_actions"] = []
        view["carry_targets"] = []
        view["attack_previews"] = {}
        view["terrain_targets"] = []
        view["throw_profile"] = None
    view["status_definitions"] = STATUS_DEFINITIONS
    view["log"] = view["log"][-30:]
    return view


def _preparation_cell_set(preparation: dict, key: str) -> set[tuple[int, int]]:
    return {(int(tile["x"]), int(tile["y"])) for tile in preparation.get(key, [])}


def _placement_definition(preparation: dict, placement_id: str) -> dict:
    entry = next((entry for entry in preparation.get("available", []) if entry.get("id") == placement_id), None)
    if not entry:
        raise ValueError("That defense is not available to this party")
    return entry


def _place_prepared_defense(battle: dict, command: dict) -> None:
    preparation = battle["preparation"]
    placement_id = str(command.get("placement_id", ""))
    definition = _placement_definition(preparation, placement_id)
    x, y = int(command.get("x", -1)), int(command.get("y", -1))
    if (x, y) not in _preparation_cell_set(preparation, "zone"):
        raise ValueError("Choose a highlighted preparation tile")
    used = sum(1 for row in preparation.get("placements", []) if row.get("type") == placement_id)
    if used >= int(definition.get("limit", 99)):
        raise ValueError(f"The placement limit for {definition['name']} has been reached")
    cost = int(definition["cost"])
    if int(preparation.get("remaining", 0)) < cost:
        raise ValueError("There is not enough preparation budget left")
    if any(_combat_active(unit) and (unit["x"], unit["y"]) == (x, y) for unit in battle["units"].values()):
        raise ValueError("A unit is standing on that tile")
    if any((x, y) in occupied_tiles(tile) and not tile.get("destroyed") for tile in battle.get("terrain", [])):
        raise ValueError("That tile is already occupied")
    unique_id = f"prepared_{placement_id}_{len(preparation.get('placements', [])) + 1}"
    templates = {
        "barricade": {
            "name": "Wooden Barricade", "kind": "barricade", "sprite": "structure:wooden_barricade",
            "blocking": True, "blocks_sight": True, "destructible": True, "hp": 12, "max_hp": 12,
            "armor": 1, "destroyed_kind": "rubble", "destroyed_sprite": "structure:palisade_breached",
            "destroyed_movement_cost": 2,
        },
        "spike_trap": {
            "name": "Spike Trap", "kind": "prepared_trap", "sprite": "spike_trap", "blocking": False,
            "prepared_trap": True, "trap_damage": 4, "destroyed_sprite": "spike_trap", "destroyed_movement_cost": 1,
        },
        "snare_trap": {
            "name": "Iron-Jaw Snare", "kind": "prepared_trap", "sprite": "iron_jaw_trap", "blocking": False,
            "prepared_trap": True, "trap_damage": 2, "trap_effect": "snare", "destroyed_sprite": "iron_jaw_trap", "destroyed_movement_cost": 1,
        },
        "watch_platform": {
            "name": "Raised Watch Platform", "kind": "platform", "sprite": "structure:wooden_watch_platform",
            "blocking": False, "destructible": True, "hp": 14, "max_hp": 14, "armor": 1,
        },
    }
    tile = {"id": unique_id, "x": x, "y": y, **templates[placement_id]}
    battle.setdefault("terrain", []).append(tile)
    if placement_id == "watch_platform":
        battle.setdefault("elevation", []).append({"x": x, "y": y, "height": 2, "kind": "prepared_platform", "source_id": unique_id})
    preparation.setdefault("placements", []).append({
        "id": unique_id, "type": placement_id, "name": definition["name"], "x": x, "y": y, "cost": cost,
    })
    preparation["remaining"] = int(preparation["remaining"]) - cost
    battle["log"].append(f"The party places {definition['name']} at {x + 1},{y + 1}.")


def _remove_prepared_defense(battle: dict, command: dict) -> None:
    preparation = battle["preparation"]
    target_id = str(command.get("target_id", ""))
    placement = next((row for row in preparation.get("placements", []) if row.get("id") == target_id), None)
    if not placement:
        raise ValueError("Choose one of the defenses placed during preparation")
    preparation["placements"].remove(placement)
    preparation["remaining"] = int(preparation["remaining"]) + int(placement["cost"])
    battle["terrain"] = [tile for tile in battle.get("terrain", []) if tile.get("id") != target_id]
    battle["elevation"] = [tile for tile in battle.get("elevation", []) if tile.get("source_id") != target_id]
    battle["log"].append(f"The party removes {placement['name']} and recovers its preparation budget.")


def _deploy_prepared_unit(battle: dict, command: dict) -> None:
    preparation = battle["preparation"]
    unit = battle.get("units", {}).get(str(command.get("target_id", "")))
    if not unit or unit.get("team") != "player" or unit.get("defense_objective"):
        raise ValueError("Choose a guild character to deploy")
    x, y = int(command.get("x", -1)), int(command.get("y", -1))
    if (x, y) not in _preparation_cell_set(preparation, "deployment_zone"):
        raise ValueError("Choose a highlighted deployment tile")
    if any(other["id"] != unit["id"] and _combat_active(other) and (other["x"], other["y"]) == (x, y) for other in battle["units"].values()):
        raise ValueError("Another unit is already deployed there")
    if any(tile.get("blocking") and not tile.get("destroyed") and (x, y) in occupied_tiles(tile) for tile in battle.get("terrain", [])):
        raise ValueError("That deployment tile is blocked")
    unit["x"], unit["y"] = x, y
    battle["log"].append(f"{unit['name']} deploys at {x + 1},{y + 1}.")


def _apply_preparation_command(battle: dict, command: dict) -> dict:
    action = command.get("action")
    if action == "place_defense":
        _place_prepared_defense(battle, command)
    elif action == "remove_defense":
        _remove_prepared_defense(battle, command)
    elif action == "deploy_unit":
        _deploy_prepared_unit(battle, command)
    elif action == "start_battle":
        battle["status"] = "active"
        battle["turn_index"] = 0
        battle["log"].append("The warning horn sounds. The raiders enter the eastern road and the defense begins.")
        _advance_to_player(battle)
    else:
        raise ValueError("Finish preparation or start the defense before issuing combat orders")
    battle["action_count"] = int(battle.get("action_count", 0)) + 1
    return battle_view(battle)


def apply_player_command(battle: dict, command: dict) -> dict:
    battle["animation_events"] = []
    if battle.get("status") == "preparing":
        return _apply_preparation_command(battle, command)
    if battle.get("status") != "active":
        raise ValueError("This battle is already complete")
    action = command.get("action")
    if action == "claim_victory":
        _claim_victory(battle)
        battle["action_count"] += 1
        return battle_view(battle)
    if action == "continue_pursuit":
        if not battle.get("decision_pending"):
            raise ValueError("There is no victory decision waiting")
        battle["decision_pending"] = False
        battle["victory_phase"] = "pursuit"
        battle["log"].append(battle.get("continue_log", "The guild continues the pursuit while the surviving enemies scatter for the perimeter."))
        _advance_to_player(battle)
        return battle_view(battle)
    if action == "retreat_all":
        battle["decision_pending"] = False
        battle["retreat_all"] = True
        if battle.get("battle_won"):
            battle["victory_phase"] = "withdrawing"
        battle["log"].append("The party is ordered to withdraw. Every guild fighter heads for the nearest exit.")
        _advance_to_player(battle)
        battle["action_count"] += 1
        return battle_view(battle)
    unit = _current_unit(battle)
    if not unit or unit["team"] != "player":
        raise ValueError("It is not a player turn")
    if action == "move":
        if unit.get("acted"):
            raise ValueError("This unit already committed its action")
        x, y = int(command.get("x", -1)), int(command.get("y", -1))
        if not unit.get("movement_origin"):
            unit["movement_origin"] = {"x": unit["x"], "y": unit["y"]}
        reachable, parents = _movement_tree(battle, unit)
        if (x, y) not in reachable:
            raise ValueError("That tile is outside this unit's movement range")
        origin = unit["movement_origin"]
        if (x, y) != (unit["x"], unit["y"]):
            unit["exit_ready"] = False
        unit["x"], unit["y"] = x, y
        if unit.get("carrying") in battle["units"]:
            carried = battle["units"][unit["carrying"]]
            carried["x"], carried["y"] = x, y
        unit["moved"] = (x, y) != (int(origin["x"]), int(origin["y"]))
        unit["movement_path"] = _movement_path(parents, reachable, (x, y))
    elif action in {"attack", "skill", "subdue"}:
        if unit.get("acted"):
            raise ValueError("This unit already used its action")
        target_id = str(command.get("target_id", ""))
        terrain_target = next((
            tile for tile in battle.get("terrain", [])
            if tile.get("id") == target_id and tile.get("destructible") and not tile.get("destroyed")
        ), None)
        if terrain_target:
            if action != "attack":
                raise ValueError("Only a standard attack can target this terrain")
            if not _can_attack(battle, unit, terrain_target):
                raise ValueError("Terrain target is outside attack range")
            _commit_player_movement(battle, unit)
            _damage_terrain(battle, unit, target_id)
            unit["acted"] = True
        else:
            target = battle["units"].get(target_id)
            if not target or not _combat_active(target) or target["team"] != "enemy":
                raise ValueError("Choose a living enemy or destructible terrain target")
            if action == "subdue" and not unit.get("nonlethal_capable"):
                raise ValueError("This weapon cannot perform a nonlethal takedown")
            if action == "skill" and not unit.get("special"):
                raise ValueError("This unit has no equipped combat skill")
            attack_range = int(unit["special"]["range"] if action == "skill" else 1 if action == "subdue" else unit["attack_range"])
            if not _can_attack(battle, unit, target, attack_range):
                raise ValueError("Target is outside attack range")
            if action == "skill" and unit.get("special_used"):
                raise ValueError("This unit's special skill has already been used")
            _commit_player_movement(battle, unit)
            rule = unit["special"]["elevation_rule"] if action == "skill" else "melee" if action == "subdue" else unit["attack_elevation_rule"]
            hit, preview, roll = _attack_hits(battle, unit, target, rule)
            bonus = 3 if action == "skill" else -1 if action == "subdue" else 0
            pierce = 2 if action == "skill" and unit["special"]["id"] == "precision_shot" else 0
            damage = _deal_damage(battle, unit, target, bonus + preview["damage_bonus"], pierce, "nonlethal" if action == "subdue" else "lethal") if hit else 0
            _record_melee_animation(battle, unit, target, hit, rule)
            if action == "skill":
                unit["special_used"] = True
            action_name = unit["special"]["name"] if action == "skill" else "a nonlethal takedown" if action == "subdue" else unit["weapon"]
            battle["log"].append(f"{unit['name']} uses {action_name} on {target['name']} for {damage} damage." if hit else f"{unit['name']} misses {target['name']} ({roll} vs {preview['chance']}% accuracy).")
            unit["acted"] = True
    elif action == "carry":
        if unit.get("acted"):
            raise ValueError("This unit already used its action")
        _carry_body(battle, unit, str(command.get("target_id", "")))
        _record_sound(battle, "pickup")
    elif action == "pickup_object":
        if unit.get("acted"):
            raise ValueError("This unit already used its action")
        _pickup_object(battle, unit, str(command.get("target_id", "")))
        _record_sound(battle, "pickup")
    elif action == "drop":
        if unit.get("acted"):
            raise ValueError("This unit already used its action")
        _commit_player_movement(battle, unit)
        _drop_body(battle, unit)
        _record_sound(battle, "payload_drop")
        unit["acted"] = True
    elif action == "drop_object":
        if unit.get("acted"):
            raise ValueError("This unit already used its action")
        _commit_player_movement(battle, unit)
        _drop_object(battle, unit)
        _record_sound(battle, "payload_drop")
        unit["acted"] = True
    elif action == "throw":
        if unit.get("acted"):
            raise ValueError("This unit already used its action")
        target = battle["units"].get(str(command.get("target_id", "")))
        if not target or target["team"] != "enemy" or not _combat_active(target):
            raise ValueError("Choose a living enemy to receive the throw")
        _commit_player_movement(battle, unit)
        _throw_payload(battle, unit, target)
        unit["acted"] = True
    elif action == "extract_body":
        extraction_tiles = _player_exit_tiles(battle)
        if (unit["x"], unit["y"]) not in extraction_tiles:
            raise ValueError("Move onto an extraction tile before extracting a body")
        if not unit.get("exit_ready"):
            raise ValueError("Hold this exit until the unit's next activation before handing off a body")
        carried = battle["units"].get(unit.get("carrying"))
        if not carried:
            raise ValueError("This unit is not carrying anyone")
        carried["extracted"] = True
        carried["extracted_with"] = unit["id"]
        carried["carried_by"] = None
        _record_sound(battle, "extraction")
        unit["carrying"] = None
        unit.pop("carried_payload_penalty", None)
        battle["log"].append(f"{unit['name']} hands {carried['name']} over at the exit and remains in the battle.")
        _check_end(battle)
        return battle_view(battle)
    elif action == "guard":
        if unit.get("acted"):
            raise ValueError("This unit already used its action")
        _commit_player_movement(battle, unit)
        unit["guarding"] = True; unit["acted"] = True
        _record_sound(battle, "guard")
        battle["log"].append(f"{unit['name']} guards against the next attack.")
    elif action == "interact":
        if unit.get("acted"):
            raise ValueError("This unit already used its action")
        object_id = str(command.get("target_id", ""))
        obj = battle["objects"].get(object_id)
        if not obj or _distance_to_entity(unit, obj) != 1:
            raise ValueError("Move next to that object before interacting")
        _commit_player_movement(battle, unit)
        _interact(battle, unit, object_id)
        _advance_to_player(battle)
        battle["action_count"] += 1
        return battle_view(battle)
    elif action == "retreat":
        battle["status"] = "complete"; battle["outcome"] = "failure"
        battle["log"].append(f"{unit['name']} orders the party to withdraw from the warcamp.")
    elif action == "leave":
        extraction_tiles = _player_exit_tiles(battle)
        if (unit["x"], unit["y"]) not in extraction_tiles:
            raise ValueError("Move onto an extraction tile before leaving the map")
        if not unit.get("exit_ready"):
            raise ValueError("Hold this exit until the unit's next activation before leaving the map")
        _commit_player_movement(battle, unit)
        _extract_unit(battle, unit, fled=False)
        _finish_turn(battle)
    elif action != "end_turn":
        raise ValueError("Unknown battle action")

    if action == "end_turn":
        _commit_player_movement(battle, unit)
    if action == "end_turn" or action in {"attack", "skill", "subdue", "drop", "drop_object", "throw", "guard"}:
        _finish_turn(battle)
    _check_end(battle)
    _advance_to_player(battle)
    if action != "move":
        battle["action_count"] += 1
    return battle_view(battle)


def auto_step(battle: dict, tactic: str = "balanced") -> dict:
    battle["animation_events"] = []
    battle["animation_events"] = []
    if battle.get("status") == "preparing":
        battle["status"] = "active"
        battle["turn_index"] = 0
        battle["log"].append("The party accepts its current deployment and begins the defense.")
        _advance_to_player(battle)
    if battle.get("status") != "active":
        return battle_view(battle)
    if battle.get("decision_pending"):
        _claim_victory(battle)
        battle["action_count"] += 1
        return battle_view(battle)
    _advance_to_player(battle)
    unit = _current_unit(battle)
    if unit and unit["team"] == "player":
        _player_auto_turn(battle, unit, tactic if tactic in {"balanced", "objective", "defensive"} else "balanced")
    _check_end(battle)
    _advance_to_player(battle)
    battle["action_count"] += 1
    return battle_view(battle)


def auto_resolve(battle: dict, tactic: str = "balanced", max_steps: int = 200) -> dict:
    if battle.get("status") == "preparing":
        auto_step(battle, tactic)
    for _ in range(max_steps):
        if battle.get("status") != "active":
            break
        auto_step(battle, tactic)
    if battle.get("status") == "active":
        battle["status"] = "complete"; battle["outcome"] = "failure"
        battle["log"].append("The battle exceeded its action limit and the party withdrew.")
    return battle_view(battle)
