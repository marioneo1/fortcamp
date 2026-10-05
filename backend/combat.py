"""Deterministic tactical combat engine for Fortcamp's first battle encounter."""
from __future__ import annotations

import random
from .relationships import ensure_character, independence_check, independent_chance, personality_profile
import heapq
from copy import deepcopy

from .battle_maps import compile_battle_map, compile_generated_battle_map, occupied_tiles
from .content import ITEMS, RECRUIT_PROFILES, MISSION_TEMPLATES
from .tactical_contracts import TACTICAL_CONTRACTS
from .location_maps import MISSION_LOCATIONS
from .wall_boundaries import crossed_walls, can_operate_gate
from .portraits import choose_pool_portrait, portrait_pool_key
from .races import race_gameplay, generated_genders
from .perk_effects import modifiers
from .equipment_rules import collect_rules,equipped_skills
from .combat_pacing import enemy_budget
from .combat_supplies import sync_supplies, remaining_uses
from . import combat_conditions as conditions
from . import concealment
from . import combat_abilities as abilities
from . import combat_tactics as tactics
from . import combat_spaces as spaces
from . import combat_entities as entities


STATUS_DEFINITIONS = {
    "lifeline_ready":{"name":"Survival safeguard","icon":"✧","description":"Equipped gear can prevent one lethal defeat this battle, leaving this unit at 1 HP. Does not prevent a nonlethal capture."},
    "lifeline_spent":{"name":"Safeguard spent","icon":"◇","description":"This unit's once-per-battle survival safeguard has been used. The next lethal hit can defeat them."},
    "stun": {"name": "Stun", "icon": "✦", "description": "Cannot act during the next activation."},
    "sleep": {"name": "Sleep", "icon": "Zz", "description": "Cannot act. Taking direct damage wakes the unit."},
    "ambush_sleep": {"name": "Sleeping camp", "icon": "Zz", "description": "Cannot move or act for the opening three rounds. Attacking any enemy wakes the whole camp, even if the attack misses."},
    "poison": {"name": "Poison", "icon": "☠", "description": "Takes damage at activation start; armor does not reduce it."},
    "bleed": {"name": "Bleed", "icon": "◆", "description": "Takes physical damage after moving or using a physical action."},
    "charm": {"name": "Charm", "icon": "♥", "description": "Treats the charmer's faction as friendly and former allies as hostile."},
    "confuse": {"name": "Confuse", "icon": "?", "description": "Offensive actions may redirect to another valid nearby target."},
    "berserk": {"name": "Berserk", "icon": "‼", "description": "Must attack if possible and treats every nearby unit as hostile."},
    "freeze": {"name": "Freeze", "icon": "❄", "description": "Cannot move. Direct hits deal 25% more damage; fire removes it."},
    "burn": {"name": "Burn", "icon": "♨", "description": "Takes damage at activation start. Suppresses status Regeneration."},
    "blind": {"name": "Blind", "icon": "◉", "description": "Attack accuracy loses 35 percentage points for ranged/magic attacks and 15 for melee."},
    "bind": {"name": "Bind", "icon": "⌁", "description": "Cannot move until the bind is broken, removed, or expires."},
    "slow": {"name": "Slow", "icon": "◷", "description": "Reduces movement by 2, with a minimum of 1."},
    "paralyze": {"name": "Paralyze", "icon": "ϟ", "description": "30% chance to miss the activation. Otherwise cannot move but can act."},
    "mute": {"name": "Mute", "icon": "◇", "description": "Cannot use magical basic attacks or spells. Physical actions and supplies remain available."},
    "fear": {"name": "Fear", "icon": "!", "description": "Cannot willingly move closer to the source. Attack accuracy is reduced by 15 percentage points."},
    "vulnerable": {"name": "Vulnerable", "icon": "▽", "description": "The next direct damaging hit ignores 3 armor."},
    "regeneration": {"name": "Regeneration", "icon": "+", "description": "Restores health at activation start; fire can suppress it."},
    "panic": {"name": "Panic", "icon": "↯", "description": "Control is lost. The unit will run toward the nearest valid escape tile."},
    "barrier": {"name":"Barrier","icon":"◈","description":"Absorbs damage before HP is lost. One finite shield; casting another does not add their amounts."},
    "mark": {"name":"Mark","icon":"◎","description":"The owner gains accuracy on their first successful hit each activation against this target. Allies do not inherit this benefit."},
    "braced": {"name":"Braced","icon":"▣","description":"Adds 50 percentage points of resistance to forced movement. Does not prevent normal walking."},
    "pit_trapped": {"name":"In a deep pit","icon":"⇧","description":"Cannot walk out. Use Climb Out to reach an adjacent safe cell; this uses the main action."},
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
    modern=any(u.get('ability_version') for u in battle.get('units',{}).values())
    for unit in battle.get("units", {}).values():
        if modern:unit.setdefault('status_version',1)
        # Existing saves cannot retain the obsolete blunt/unarmed Subdue permission.
        if unit.get('team') == 'player' and 'capture_weapon' not in unit:
            weapon = next((item for item in ITEMS.values() if item.get('name') == unit.get('weapon')), {})
            if unit.get('weapon') == "Watchman's Cudgel": weapon = ITEMS['watchmans_cudgel']
            profile = deepcopy(weapon.get('capture_weapon'))
            unit.update(capture_weapon=profile, nonlethal_capable=bool(profile), knockout_finisher=weapon.get('knockout_finisher',0))
            if profile:
                unit.update(attack=0, attack_range=profile['range'], attack_elevation_rule=profile['elevation_rule'])
                unit['skills'] = [skill for skill in unit.get('skills',[]) if not skill.get('nonlethal') and skill.get('id') not in {'precision_shot','arc_bolt'}]
                unit['special'] = unit['skills'][0] if unit['skills'] else None
            else:
                for skill in unit.get('skills',[]): skill['nonlethal'] = False
                if unit.get('special'): unit['special']['nonlethal'] = False
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
    equipped_ids = set(character.get("equipment", {}).values())
    basic_special=deepcopy(special)
    equipped = [ITEMS.get(instance["item_id"], {}) for instance in state.get("inventory", []) if instance["instance_id"] in equipped_ids]
    skill_item = weapon if weapon.get("combat_skill") else next((item for item in equipped if item.get("combat_skill")), {})
    granted_skill = skill_item.get("combat_skill")
    if granted_skill:
        special = deepcopy(granted_skill)
        special["attack"] = 5 + _effective_attribute(state, character, special["scaling"]) // 2 + int(skill_item.get("power", 2))
        special.setdefault("element", skill_item.get("element"))
        special.setdefault("on_hit", deepcopy(skill_item.get("on_hit")))
    capture_weapon = deepcopy(weapon.get('capture_weapon'))
    if capture_weapon:
        basic_special = None
        special = None
        granted_skill = None
    attack_range = int(weapon.get("attack_range", attack_range))
    vit = _effective_attribute(state, character, "vit")
    agi = _effective_attribute(state, character, "agi")
    scaling_value = _effective_attribute(state, character, scaling)
    strength = _effective_attribute(state, character, "str")
    combat_training = {"none": 0, "basic": 1, "skilled": 2, "expert": 3, "master": 4}.get(character.get("perks", {}).get("combat", "none"), 0)
    if granted_skill:
        special["attack"] += combat_training
    skills=equipped_skills(equipped,lambda key:_effective_attribute(state,character,key),combat_training,
                           fallback=basic_special,weapon=weapon)
    from .perk_effects import character_perks
    if 'medic' in character_perks(state, character, ITEMS) or character.get('perks', {}).get('medicine', 'none') != 'none':
        if not any(s['id'] == 'field_care' for s in skills):
            skills.append({'id': 'field_care', 'name': 'Field Care', 'target': 'ally', 'effect': 'support',
                           'range': 1, 'heal': 8, 'cleanses': ['bleed'], 'scaling': 'int',
                           'elevation_rule': 'physical_care', 'description': 'One shared technique use per battle. Range 1: restore 8 + half INT HP and stop Bleed. Physical treatment works while muted; cannot revive.'})
    skills = abilities.snapshot(skills, _effective_attribute(state, character, 'int'))
    special = skills[0] if skills else None
    rules=collect_rules(equipped)
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
        "racial_resistances": sorted(set(racial["resistances"])|set(rules['resistances'])), "racial_weaknesses": list(racial["weaknesses"]),
        "gear_rules":rules,
        "race": race, "race_summary": racial["summary"],
        "strength": strength, "intelligence": _effective_attribute(state, character, 'int'), "weight": _race_weight(character.get("race", "human")),
        "attack": 0 if capture_weapon else 5 + scaling_value // 2 + int(weapon.get("power", 0)) + combat_training,
        "capture_weapon": capture_weapon,
        "capture_attributes": {key:_effective_attribute(state, character, key) for key in ("str", "dex", "int")},
        "knockout_finisher": int(weapon.get("knockout_finisher", 0)),
        "attack_elevation_rule": capture_weapon["elevation_rule"] if capture_weapon else "ballistic" if ranged else "ignore" if magical else "melee",
        "nonlethal_capable": bool(capture_weapon),
        "weapon": weapon.get("name", "Unarmed"), "scaling": scaling,
        "element": weapon.get("element"), "on_hit": deepcopy(weapon.get("on_hit")),
        "portrait": (character.get('portrait') if character.get('portrait_source')=='override' and not character.get('portrait_thumbnail_uncropped')
                     else character.get("portrait_thumbnail") or character.get("portrait", "")),
        "portrait_full": character.get("portrait", ""),
        "portrait_frame": deepcopy(character.get('portrait_frame', {})),
        "portrait_frame_source": character.get('portrait_frame_source'),
        "portrait_frame_key": character.get('portrait_frame_key'),
        "special": special, "skills":skills, "special_used": False, "ability_version": 1,
        "ability_activation": 0, "ability_state": {}, "guarding": rules.get('opening_guard',False),
        "reactions": [deepcopy(item['combat_reaction']) for item in equipped if item.get('combat_reaction')],
        "moved": False, "acted": False, "alive": True, "conscious": True, "condition": "active",
        "statuses": ([{'id':'lifeline_ready'}] if rules.get('lifeline') else []), "carrying": None, "carrying_object": None, "carried_by": None, "panicked": False, "fled": False,
        "loyalty": ensure_character(character)["loyalty"],
        "personality_id": character["personality_id"],
        "personality_override": deepcopy(character.get("personality_override", {})),
        "combat_record": {"kills":0,"subdues":0,"times_defeated":0,"total_damage":0,"combat_turns":0,"highest_turn_damage":0},
        "turn_damage": 0,
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
    # Authored D-rank boss encounter; fixed stats, never scaled to the player's roster.
    warcamp_stats = {
        "chieftain": (72, 3, 12), "raider": (28, 2, 8),
        "archer": (24, 1, 7), "horncaller": (24, 1, 7),
    }
    for enemy in enemies:
        hp, armor, attack = warcamp_stats[enemy["kind"]]
        enemy.update(hp=hp, max_hp=hp, armor=armor, attack=attack)
        if enemy["kind"] == "chieftain":
            enemy.update(boss=True, move=4, strength=14)
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
            "alarm_horn": {"id": "alarm_horn", "name": "Alarm Bell", "x": 7, "y": 1, "state": "active"},
            "supply_crate": {"id": "supply_crate", "name": "Loose Supply Crate", "x": 0, "y": 6, "state": "ground", "portable": True, "blocking": False, "weight": 4, "impact_damage": 5, "carry_penalty": 1, "breaks_on_throw": True, "icon": "📦"},
            "loose_stone": {"id": "loose_stone", "name": "Loose Camp Stone", "x": 3, "y": 6, "state": "ground", "portable": True, "blocking": False, "weight": 1, "impact_damage": 2, "carry_penalty": 0, "breaks_on_throw": False, "icon": "●"},
        },
        "objectives": [
            {"id": "chieftain", "name": f"Defeat {chief_name}", "required": True, "complete": False},
            {"id": "captives", "name": "Free the captives", "required": False, "complete": False},
            {"id": "alarm", "name": "Disable the alarm bell", "required": False, "complete": False},
        ],
        "status": "active", "outcome": None, "reinforcements_spawned": False,
        "battle_won": False, "decision_pending": False, "victory_phase": None,
        "battlefield_secured": False, "auto_looted_ids": [], "retreat_all": False,
        "log": [f"The party enters through the south approach. {chief_name} is inside the palisade. The captives and alarm bell are on opposite sides of the camp."],
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
    courier = _enemy("captive_courier", courier_name, "archer", 7, 4, courier_identity)
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
            "dispatch_satchel": {"id": "dispatch_satchel", "name": "Stolen Dispatch Satchel", "sprite": "dispatch_satchel", "x": 7, "y": 5, "state": "ground", "portable": True, "blocking": False, "weight": 1, "impact_damage": 1, "carry_penalty": 0, "breaks_on_throw": False, "objective_item": True, "icon": "▣"},
            "loose_wheel": {"id": "loose_wheel", "name": "Loose Wagon Wheel", "sprite": "wagon_wheel", "x": 5, "y": 2, "state": "ground", "portable": True, "blocking": False, "weight": 3, "impact_damage": 4, "carry_penalty": 1, "breaks_on_throw": False, "icon": "◉"},
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
            "signal_chart": {"id": "signal_chart", "name": "Marked Farm Chart", "sprite": "marked_farm_chart", "x": chart_x, "y": chart_y,
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


def create_contract_battle(state: dict, party_ids: list[str], seed: str, mission_id: str, defer_start: bool = False, race_override: str | None = None) -> dict:
    spec = TACTICAL_CONTRACTS[mission_id]
    mission = MISSION_TEMPLATES[mission_id]
    location = MISSION_LOCATIONS.get(mission_id)
    board = compile_generated_battle_map(f"location_{location}" if location else f"contract_{spec['layout']}", seed)
    characters = {c["id"]: c for c in state["characters"]}
    units = {cid: _player_unit(state, characters[cid], tile["x"], tile["y"])
             for cid, tile in zip(party_ids, board["spawn_zones"]["player"])}
    tier = {"E":0,"D":0,"C":1,"B":2,"A":3,"S":4}[mission["rank"]]
    count = min(8, spec.get('enemy_count',3 + tier + (1 if tier else 0)))
    rng = random.Random(f"contract:{seed}")
    race = race_override or spec["race"]
    racial = race_gameplay(race)
    used_names = set()
    for index, tile in enumerate(board["spawn_zones"]["enemy"][:count]):
        uid = f"contract_enemy_{index}"
        kind = "chieftain" if index == 0 else "archer" if index % 3 == 0 else "raider"
        if race in {"Goblin", "Hobgoblin"}:
            identity = _goblin_npc_identity(seed, uid, "scout" if kind == "archer" else "fighter")
            name = identity["name"]
        else:
            gender = rng.choice(generated_genders(race))
            name = rng.choice(("Tarin","Nessa","Rovan","Mira","Kellan","Sera","Veyra","Darin")) + " " + rng.choice(("Hale","Voss","Carrow","Fen","Rook","Vale"))
            identity = choose_pool_portrait(portrait_pool_key(race,gender,"scout" if kind == "archer" else "fighter", special=index == 0),rng) or {}
            identity["gender"] = gender
        if name in used_names:
            name += " " + ("Ash","Reed","Iron","Thorn","Flint","Oak","Stone","Moss")[index]
        used_names.add(name)
        if race == "Hobgoblin":
            identity = {**choose_pool_portrait(portrait_pool_key(race,identity.get("gender","male"),"scout" if kind == "archer" else "fighter"),rng), "gender":identity.get("gender","male")}
        budget = enemy_budget(mission['rank'], index == 0, racial)
        hp = budget['hp']
        unit = _enemy(uid,name,kind,tile["x"],tile["y"],identity)
        unit.update({"race":race,"boss":index == 0,"hp":hp,"max_hp":hp,
            "armor":budget['armor'],"attack":budget['attack'],
            "move":3+int(racial["move_bonus"])+(1 if spec.get("mounted") else 0),
            "initiative":14+int(racial["initiative_bonus"])+index,
            "evasion":int(racial["evasion"]),"movement_type":racial["movement_type"],
            "racial_resistances":list(racial["resistances"]),"racial_weaknesses":list(racial["weaknesses"]),
            "weight":_race_weight(race),
            "weapon":"Short Bow" if kind == "archer" else "Chapel Blade" if race == "Undead" else "Raider Spear",
            "corpse_item":"short_bow" if kind == "archer" else "rusty_knife",
            "corpse_item_chance":35 if index == 0 else 25})
        if mission_id == "goblin_chieftain":
            # The B-rank Redoubt is a trained warband, not a D-rank camp patrol.
            hp = 112 if index == 0 else 40
            unit.update(hp=hp, max_hp=hp, armor=4 if index == 0 else 2,
                        attack=17 if index == 0 else 10)
        rank_index = ['E', 'D', 'C', 'B', 'A', 'S'].index(mission['rank'])
        if not spec.get('rookie') and not spec.get('creature'):
            unit['corpse_gold'] = ((4 + rank_index * 3, 8 + rank_index * 5) if index == 0
                                   else (rank_index, 2 + rank_index * 2))
            if rank_index >= 2:
                unit['on_hit'] = {'id': 'mute' if race == 'Undead' else 'blind' if kind == 'archer' else 'bleed',
                                  'chance': 15 if index == 0 else 10, 'turns': 1 if index == 0 else 2}
            if spec.get('caster') and index == count - 1:
                unit.update(weapon='Static Discharge', attack_range=3, attack_elevation_rule='ignore',
                            element='lightning', on_hit={'id':'paralyze','chance':12,'turns':1})
        if spec.get('rookie'):
            unit.update(hp=10 if index==0 else 7,max_hp=10 if index==0 else 7,armor=0,attack=3,initiative=8+index,move=3)
        if spec.get('creature'):
            unit.update(name=f"{spec['creature']} {index+1}",portrait='',weapon='Bite',corpse_item=None,corpse_item_chance=0,boss=False,creature=True)
            unit['corpse_gold']=(0,0)
        if index in board.get('ambush_enemy_indices', []):
            unit['bush_ambusher'] = True
        units[uid] = unit
    commander = units["contract_enemy_0"]
    return_battle = {**board,"version":1,"encounter_id":f"contract:{mission_id}","name":mission["name"],
        "round":1,"turn_index":0,"turn_order":sorted(units,key=lambda uid:(-units[uid]["initiative"],uid)),
        "units":units,"objects":{},"primary_target_id":commander["id"],
        "leader_target":bool(spec.get("leader_target")),"capture_bonus":race != "Undead" and not spec.get('rookie') and not spec.get('creature'),
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
        battle = create_contract_battle(state, party_ids, seed, encounter_id.split(":", 1)[1], defer_start=defer_start)
        sync_supplies(battle, state)
        return battle
    factories = {
        "goblin_warcamp": create_goblin_warcamp_battle,
        "goblin_captive_cart": create_captive_cart_battle,
        "goblin_smoke_signals": create_smoke_signals_battle,
        "frontier_watch_defense": create_frontier_watch_defense_battle,
    }
    if encounter_id not in factories:
        raise ValueError(f"Tactical encounter {encounter_id!r} is not implemented")
    battle = factories[encounter_id](state, party_ids, seed) if encounter_id == "frontier_watch_defense" else factories[encounter_id](state, party_ids, seed, defer_start=defer_start)
    sync_supplies(battle, state)
    return battle


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
        tile.get("blocking") and not tile.get("destroyed") and not tile.get('edge_wall')
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
        and not (battle.get('units', {}).get(ignore_unit, {}).get('team') == 'player' and concealment.unseen(unit))
        and unit["x"] == x and unit["y"] == y
        for unit in battle["units"].values()
    )


def _movement_limit(unit: dict) -> int:
    if unit.get('stationary'):return 0
    if conditions.has(unit, 'freeze') or conditions.has(unit, 'bind') or conditions.has(unit,'pit_trapped') or unit.get('paralyzed_move'):
        return 0
    penalty = int(unit.get("carried_payload_penalty", 2 if unit.get("carrying") else 0))
    return max(1, int(unit["move"]) - penalty - (2 if conditions.has(unit, 'slow') else 0))


def _carry_penalty(unit: dict, weight: int) -> int:
    capacity = max(1, (int(unit.get("strength", 5))+unit.get('gear_rules',{}).get('carry_strength',0)) // 3)
    return max(0, min(3, int(weight) - capacity + 1))


def _tile_height(battle: dict, x: int, y: int) -> int:
    tile = next((tile for tile in battle.get("elevation", []) if tile["x"] == x and tile["y"] == y), None)
    return int(tile.get("height", 0)) if tile else 0


def _can_step(battle: dict, x: int, y: int, nx: int, ny: int, unit: dict) -> bool:
    fear = next((s for s in unit.get('statuses', []) if s.get('id') == 'fear'), None)
    source = battle['units'].get(fear.get('source_id')) if fear else None
    if source and abs(nx-source['x'])+abs(ny-source['y']) < abs(x-source['x'])+abs(y-source['y']):
        return False
    if _blocked(battle, nx, ny, unit["id"], unit.get("movement_type")):
        return False
    if crossed_walls(battle, (x, y), (nx, ny)):
        return False
    if unit.get("movement_type") == "flying":
        return True
    return abs(_tile_height(battle, nx, ny) - _tile_height(battle, x, y)) <= 2


def _step_cost(battle: dict, x: int, y: int, nx: int, ny: int, unit: dict) -> int:
    if unit.get("movement_type") == "flying":
        return 1
    climb = _tile_height(battle, nx, ny) - _tile_height(battle, x, y)
    elevation_cost = max(1, climb * 2)
    material, ground = _ground_at(battle, nx, ny)
    terrain_cost = max(
        [int(tile.get("movement_cost", 1)) for tile in _terrain_at(battle, nx, ny) if not tile.get("destroyed")]
        + [int(tile.get("destroyed_movement_cost", 1)) for tile in _terrain_at(battle, nx, ny) if tile.get("destroyed")]
        + [int(ground.get("movement_cost", 1))]
        + [1]
    )
    rules=unit.get('gear_rules',{})
    kinds={tile.get('kind') for tile in _terrain_at(battle,nx,ny)}
    water=bool(kinds.intersection({'shallow_water','water'})) or material.startswith('water')
    rubble='rubble' in kinds or 'rubble' in material or any(tile.get('destroyed') for tile in _terrain_at(battle,nx,ny))
    if water and rules.get('water_walk') or rubble and rules.get('rubble_walk'):terrain_cost=1
    return elevation_cost + terrain_cost - 1


def _distance(a: dict, b: dict) -> int:
    return abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])


def _line_of_sight(battle: dict, attacker: dict, target: dict) -> bool:
    """Bresenham trace; blocking terrain stops ranged attacks."""
    x0, y0, x1, y1 = attacker["x"], attacker["y"], target["x"], target["y"]
    if any(wall.get('id') != target.get('id') for wall in crossed_walls(battle, (x0, y0), (x1, y1), sight=True)):
        return False
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
        if any(tile.get("blocks_sight", tile.get("blocking", False)) and not tile.get("destroyed") and not tile.get('edge_wall') for tile in _terrain_at(battle, x, y)):
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
    mark_accuracy=conditions.mark_bonus(attacker,target)
    accuracy+=mark_accuracy
    base = 90 if rule == "ballistic" else 100
    target_evasion = int(target.get("evasion", 0))
    evasion_factor = 1.0 if rule == "ballistic" else .3 if rule == "ignore" else .6
    evasion_penalty = round(target_evasion * evasion_factor)
    if conditions.has(attacker, 'blind'):
        accuracy -= 35 if rule in {'ballistic', 'ignore'} else 15
    if conditions.has(attacker, 'fear'):
        accuracy -= 15
    if conditions.has(attacker, 'berserk'):
        accuracy -= 10
    return {
        "chance": max(5, min(100, base + accuracy - evasion_penalty + attacker.get('perk_modifiers',{}).get('accuracy',0))), "damage_bonus": damage,
        "target_evasion": target_evasion, "evasion_penalty": evasion_penalty,
        "mark_accuracy":mark_accuracy,
        "attacker_height": _tile_height(battle, attacker["x"], attacker["y"]),
        "target_height": _tile_height(battle, target["x"], target["y"]), "elevation_rule": rule,
    }


def _attack_hits(battle: dict, attacker: dict, target: dict, rule: str) -> tuple[bool, dict, int]:
    concealment.reveal(battle, attacker)
    _wake_ambush(battle, target)
    preview = _attack_preview(battle, attacker, target, rule)
    counter = int(battle.get("roll_counter", 0))
    battle["roll_counter"] = counter + 1
    roll = random.Random(f"{battle.get('seed')}:{counter}:{attacker['id']}:{target['id']}").randint(1, 100)
    if roll<=preview['chance'] and preview.get('mark_accuracy'):
        owner=battle['units'].get(attacker['id'],attacker)
        owner['mark_hit_activation']=deepcopy(owner.get('status_activation'))
    return roll <= preview["chance"], preview, roll


def _can_attack(battle: dict, attacker: dict, target: dict, attack_range: int | None = None) -> bool:
    if attacker.get('team') == 'player' and concealment.unseen(target):
        return False
    reach = int(attack_range if attack_range is not None else attacker["attack_range"])
    return (_distance(attacker, target) <= reach
            and not any(wall.get('id') != target.get('id') for wall in crossed_walls(battle, (attacker['x'], attacker['y']), (target['x'], target['y']), sight=True))
            and (reach == 1 or _line_of_sight(battle, attacker, target)))


def _interceptor(battle,attacker,target,reach):
    candidates=[u for u in battle['units'].values() if u['id']!=target['id'] and u['team']==target['team']
        and u['team']!=attacker['team'] and tactics.reaction_available(u) and not conditions.has(u,'bind')
        and any(r.get('id')=='intercept' for r in u.get('reactions',[]))
        and _distance(u,target)==1 and _distance(attacker,u)<=reach+1
        and _line_of_sight(battle,u,target) and _line_of_sight(battle,attacker,u)]
    return min(candidates,key=lambda u:(-u['hp']/max(1,u['max_hp']),u['id'])) if candidates else target


def _react_after_attack(battle,attacker,target,hit,rule):
    if rule!='melee' or not _combat_active(attacker) or not _combat_active(target):return
    if not tactics.reaction_available(target) or target.get('capture_weapon') or target.get('attack_elevation_rule')!='melee':return
    wanted='riposte' if hit else 'returning_hand'
    if not any(r.get('id')==wanted for r in target.get('reactions',[])) or not _can_attack(battle,target,attacker,1):return
    target['reaction_ready']=False
    battle['log'].append(f"{target['name']} counters {attacker['name']}.")
    counter={**target,'attack':max(1,target['attack']//2),'reaction_attack':True,'element':None,'on_hit':None,'knockout_finisher':0}
    _perform_attack(battle,counter,attacker,'melee',reaction=True)


def _perform_attack(battle,attacker,target,rule,bonus=0,pierce=0,intent='lethal',ability=None,reaction=False,defer_reaction=False):
    original=target
    if not reaction and intent=='lethal':
        target=_interceptor(battle,attacker,target,int((ability or {}).get('range',attacker.get('attack_range',1))))
        if target is not original:
            target['reaction_ready']=False
            concealment.reveal(battle,target)
            battle['log'].append(f"{target['name']} intercepts the attack on {original['name']}.")
    hit,preview,roll=_attack_hits(battle,attacker,target,rule)
    damage=_deal_damage(battle,attacker,target,bonus+preview['damage_bonus'],pierce,intent,ability=ability) if hit else 0
    _record_melee_animation(battle,attacker,target,hit,rule)
    if not reaction and not defer_reaction and intent=='lethal':_react_after_attack(battle,attacker,target,hit,rule)
    return target,hit,damage,preview,roll


def _strike_preview(battle,actor,target,rule,reach,skill=None):
    direct = not skill or any(e['type']=='attack' for e in skill.get('effects',[]))
    recipient=_interceptor(battle,actor,target,reach) if direct else target
    preview=_attack_preview(battle,actor,recipient,rule)
    preview['barrier']=max((s.get('amount',0) for s in recipient.get('statuses',[]) if s['id']=='barrier'),default=0)
    if recipient is not target:preview['intercepted_by']=recipient['name']
    preview['tactics']=[{'type':e['mode'],**_displacement_preview(battle,actor,recipient,e)}
        for e in (skill or {}).get('effects',[]) if e['type']=='displace']
    preview['zones']=[{'kind':e['zone'],'name':spaces.ZONES[e['zone']]['name'],
        'description':spaces.ZONES[e['zone']]['description'],'cells':_zone_cells(battle,recipient,e),
        'turns':e['turns']} for e in (skill or {}).get('effects',[]) if e['type']=='zone']
    if not direct:preview.update(chance=100,damage_bonus=0,setup_only=True)
    return preview


def _displacement_preview(battle,actor,target,effect):
    path=[];blocked=None;pit=None
    x,y=target['x'],target['y']
    for nx,ny in tactics.displacement_path(actor,target,effect['distance'],effect['mode']):
        hazard=tactics.pit_at(battle,nx,ny)
        flying=target.get('movement_type')=='flying'
        if crossed_walls(battle,(x,y),(nx,ny)) or _blocked(battle,nx,ny,target['id'],'flying' if hazard else target.get('movement_type')):
            blocked='Wall, object, occupied cell or map edge';break
        if not flying and abs(_tile_height(battle,nx,ny)-_tile_height(battle,x,y))>2:
            blocked='Impassable elevation';break
        if hazard and not flying:
            kind=tactics.pit_kind(hazard)
            if kind not in {'shallow','deep','lethal'}:
                blocked='This gap has no authored fall rule';break
            pit=kind
        path.append({'x':nx,'y':ny});x,y=nx,ny
        if pit:break
    return {'path':path,'destination':{'x':x,'y':y},'blocked':blocked,'pit':pit,
        'resistance':tactics.displacement_resistance(target),'collision_damage':effect.get('collision_damage',0) if blocked else 0}


def _apply_displacement(battle,actor,target,effect):
    preview=_displacement_preview(battle,actor,target,effect)
    counter=battle.get('displacement_counter',0);battle['displacement_counter']=counter+1
    if random.Random(f"{battle.get('seed')}:displace:{counter}:{actor['id']}:{target['id']}").randint(1,100)<=preview['resistance']:
        battle['log'].append(f"{target['name']} resists the forced movement.");return
    start=(target['x'],target['y']);path=[]
    for point in preview['path']:
        hidden=next((u for u in battle['units'].values() if u['id']!=target['id'] and _combat_active(u) and (u['x'],u['y'])==(point['x'],point['y'])),None)
        if hidden:
            if target['team']=='player':concealment.reveal(battle,hidden,'contact')
            break
        target.update(point);path.append((point['x'],point['y']))
        if target.get('carrying') in battle['units']:battle['units'][target['carrying']].update(point)
    if path:
        _commit_player_movement(battle,target)
        target['exit_ready']=False
        _record_movement(battle,target,start,path)
        battle['animation_events'][-1]['forced']=True
        battle['log'].append(f"{target['name']} is {'pushed' if effect['mode']=='push' else 'pulled'} {len(path)} cell{'s' if len(path)!=1 else ''}.")
        hazard=tactics.pit_at(battle,target['x'],target['y'])
        if hazard and target.get('movement_type')!='flying':
            kind=tactics.pit_kind(hazard)
            if kind=='lethal':
                carried_id=target.get('carrying');object_id=target.get('carrying_object')
                source={**actor,'attack':target['max_hp']*100,'status_tick':True,'environmental_fall':True,'element':None,'on_hit':None,'weapon':'a lethal fall'}
                _deal_damage(battle,source,target)
                target['lost_in_pit']=True
                if carried_id in battle['units']:
                    cargo=battle['units'][carried_id]
                    _deal_damage(battle,{**source,'attack':cargo['max_hp']*100},cargo)
                    cargo['lost_in_pit']=True
                if object_id in battle.get('objects',{}):battle['objects'][object_id].update(state='removed',lost_in_pit=True)
                battle['log'].append(f"{target['name']} falls beyond reach. Their body and equipment cannot be recovered.")
            elif kind in {'shallow','deep'}:
                source={'id':actor['id'],'name':actor['name'],'attack':max(2,round(target['max_hp']*.12)),'status_tick':True,'weapon':'a fall'}
                _deal_damage(battle,source,target,armor_pierce=target.get('armor',0))
                if _combat_active(target):
                    if kind=='deep':target['statuses'].append({'id':'pit_trapped'})
                    else:conditions.apply(target,'slow',1,actor)
                battle['log'].append(f"{target['name']} falls into a {kind} pit.")
            else:_apply_tile_entry(battle,target)
        else:_apply_tile_entry(battle,target)
    if preview['collision_damage'] and _combat_active(target):
        _deal_damage(battle,{**actor,'attack':preview['collision_damage'],'status_tick':True,'element':None,'on_hit':None,'weapon':'a collision'},target,armor_pierce=target.get('armor',0))
    concealment.refresh(battle)


def _pit_exits(battle,unit):
    if not conditions.has(unit,'pit_trapped') or unit.get('forced_skip') or unit.get('paralyzed_move') or any(conditions.has(unit,s) for s in ('bind','freeze','stun','sleep','ambush_sleep')):return []
    return [(unit['x']+dx,unit['y']+dy) for dx,dy in ((0,-1),(1,0),(0,1),(-1,0))
        if not tactics.pit_at(battle,unit['x']+dx,unit['y']+dy) and _can_step(battle,unit['x'],unit['y'],unit['x']+dx,unit['y']+dy,unit)]


def _climb_out(battle,unit,destination):
    if unit.get('acted') or destination not in _pit_exits(battle,unit):raise ValueError('Choose an adjacent safe cell to climb out')
    start=(unit['x'],unit['y']);_commit_player_movement(battle,unit)
    conditions.remove(unit,'pit_trapped');unit.update(x=destination[0],y=destination[1],acted=True,exit_ready=False)
    if unit.get('carrying') in battle['units']:battle['units'][unit['carrying']].update(x=destination[0],y=destination[1])
    _record_movement(battle,unit,start,[destination]);_apply_tile_entry(battle,unit)
    battle['log'].append(f"{unit['name']} climbs out of the pit.")


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
    if origin and unit.get('movement_path'):
        _apply_zone_route(battle,unit,[(p['x'],p['y']) for p in unit['movement_path']])
    unit.pop("movement_origin", None)
    unit.pop("movement_path", None)
    _apply_tile_entry(battle, unit)


def _attack_position(battle, unit, target, attack_range, reachable, parents):
    """Choose the cheapest legal firing position under this turn's movement budget."""
    if _can_attack(battle, unit, target, attack_range):
        return unit, None
    candidates = []
    for (x, y), cost in reachable.items():
        actor = {**unit, 'x': x, 'y': y}
        if _can_attack(battle, actor, target, attack_range):
            candidates.append((cost, _distance(unit, actor), y, x, actor))
    if not candidates:
        return None, None
    cost, _, y, x, actor = min(candidates, key=lambda row: row[:4])
    return actor, {'move_to': {'x': x, 'y': y}, 'movement_cost': cost,
                   'path': _movement_path(parents, reachable, (x, y))}


def _apply_attack_approach(battle, unit, target, attack_range, command):
    destination = command.get('move_to')
    if destination is None:
        return
    if not isinstance(destination, dict):
        raise ValueError('Choose a valid approach tile')
    x, y = int(destination.get('x', -1)), int(destination.get('y', -1))
    costs, parents = _movement_tree(battle, unit)
    actor = {**unit, 'x': x, 'y': y}
    if (x, y) not in costs or not _can_attack(battle, actor, target, attack_range):
        raise ValueError('That approach cannot reach the target within this turn')
    desired = (x, y)
    path = _movement_path(parents, costs, (x, y))
    origin = unit.get('movement_origin') or {'x': unit['x'], 'y': unit['y']}
    points = [{'x': unit['x'], 'y': unit['y']}]
    current_index = next((i for i, point in enumerate(path) if (point['x'], point['y']) == (unit['x'], unit['y'])), None)
    if current_index is not None:
        points.extend(path[current_index + 1:])
    else:
        points.extend(reversed(unit.get('movement_path', [])[:-1]))
        if (points[-1]['x'], points[-1]['y']) != (origin['x'], origin['y']):
            points.append(origin)
        points.extend(path)
    route = _scout_path(battle, unit, [(p['x'],p['y']) for p in points[1:]])
    if route:
        x, y = route[-1]
    else:
        x, y = unit['x'], unit['y']
    points = [points[0]] + [{'x':px,'y':py} for px,py in route]
    if (unit['x'], unit['y']) != (x, y):
        unit['exit_ready'] = False
        battle.setdefault('animation_events', []).append({'type': 'movement', 'unit_id': unit['id'], 'points': points})
    unit['movement_origin'] = origin
    unit['movement_path'] = _movement_path(parents, costs, (x, y))
    unit['x'], unit['y'] = x, y
    unit['moved'] = (x, y) != (origin['x'], origin['y'])
    if unit.get('carrying') in battle['units']:
        battle['units'][unit['carrying']].update(x=x, y=y)
    return (x, y) != desired


def _zone_cells(battle, target, effect):
    def allowed(x,y):
        tiles=_terrain_at(battle,x,y)
        if tactics.pit_at(battle,x,y) or any(t.get('blocking') and not t.get('edge_wall') and not t.get('destroyed') for t in tiles):return False
        material,_=_ground_at(battle,x,y)
        if material=='water' or any(t.get('kind')=='shallow_water' for t in tiles):return False
        if any(o.get('blocking') and (x,y) in occupied_tiles(o) for o in battle.get('objects',{}).values()):return False
        return _line_of_sight(battle,target,{'x':x,'y':y})
    return spaces.zone_cells(battle,target,effect['radius'],allowed)


def _trigger_zones(battle, unit, event):
    def apply_status(owner,target,sid):
        if sid=='poison' and sid in target.get('racial_resistances',[]):return
        chance=50 if sid in target.get('racial_resistances',[]) else 100
        roll=random.Random(f"{battle.get('seed')}:zone:{sid}:{target['id']}:{target.get('status_activation')}").randint(1,100)
        if roll<=chance and conditions.apply(target,sid,1,owner):
            battle['log'].append(f"{target['name']} suffers {sid} from {owner['name']}'s zone.")
    def damage(owner,target,amount,name):
        source={'id':owner['id'],'name':owner['name'],'attack':amount,'weapon':name,'status_tick':True}
        dealt=_deal_damage(battle,source,target,armor_pierce=target.get('armor',0))
        battle['log'].append(f"{target['name']} takes {dealt} damage from {name}.")
    spaces.trigger_zones(battle,unit,event,_combat_active,
        lambda target,owner:target['id'] in {u['id'] for u in conditions.hostile_units(battle,owner,_living(battle))},
        apply_status,damage)


def _apply_zone_route(battle,unit,path):
    """Consequences run only after a real route commits, never during preview."""
    if not battle.get('zones'):return
    destination=(unit['x'],unit['y'])
    for x,y in path:
        if unit.get('zone_location')==[x,y]:continue
        unit.update(x=x,y=y,zone_location=[x,y])
        _trigger_zones(battle,unit,'entry')
        if not _combat_active(unit):return
    unit['x'],unit['y']=destination


def _apply_tile_entry(battle: dict, unit: dict) -> None:
    """Resolve immediate effects from the tile where a committed move ends."""
    if battle.get('zones'):
        position=[unit['x'],unit['y']]
        old=unit.get('zone_location')
        unit['zone_location']=position
        if old is not None and old!=position:_trigger_zones(battle,unit,'entry')
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


def _current_unit(battle: dict, activate: bool = True) -> dict | None:
    _ensure_battle_schema(battle)
    if battle["status"] != "active" or battle.get("decision_pending"):
        return None
    order = battle["turn_order"]
    if not activate:
        index = battle.get('turn_index',0)
        unit = battle['units'].get(order[index]) if 0 <= index < len(order) else None
        return unit if unit and _combat_active(unit) else None
    while order:
        if battle["turn_index"] >= len(order):
            battle["turn_index"] = 0
            battle["round"] += 1
            if battle.get("ambush_sleep_until_round") and battle["round"] >= battle["ambush_sleep_until_round"]:
                _wake_ambush(battle)
            for unit in _living(battle):
                unit["moved"] = False; unit["acted"] = False; unit["guarding"] = False
                healing=min(unit.get('perk_modifiers',{}).get('regeneration',0),unit['max_hp']-unit['hp'])
                if healing>0:
                    unit['hp']+=healing
                    battle['log'].append(f"{unit['name']} regenerates {healing} HP.")
            alarm = battle.get("objects", {}).get("alarm_horn")
            if battle.get("encounter_id") == "goblin_warcamp" and battle["round"] == 5 and alarm and alarm.get("state") == "active":
                _spawn_reinforcements(battle)
            if battle["round"] > 20 and not any(u.get('ability_version') for u in battle['units'].values()):
                battle["status"] = "complete"; battle["outcome"] = "failure"
                battle["log"].append("After twenty rounds, the exhausted party can no longer hold its position and is forced to retreat.")
                return None
        unit = battle["units"].get(order[battle["turn_index"]])
        if unit and _combat_active(unit):
            stamp = [battle["round"], battle["turn_index"]]
            if unit.get("status_activation") != stamp:
                unit["status_activation"] = stamp
                if unit.get('ability_version'):
                    abilities.start_activation(unit, stamp)
                    unit['entity_budget_spent']=0
                spaces.expire_form(unit)
                if battle.get('zones'):
                    spaces.expire_zones(battle,unit)
                    unit['zone_location']=[unit['x'],unit['y']]
                    _trigger_zones(battle,unit,'start')
                conditions.start_activation(battle, unit)
                if unit.get("team")=="player":
                    facts=unit.setdefault("combat_record",{})
                    facts["combat_turns"]=facts.get("combat_turns",0)+1
                    unit["turn_damage"]=0
                if any(s.get("id") in {"burn", "poison"} and "turns" in s for s in unit.get("statuses", [])):
                    _tick_gear_statuses(battle, unit)
                    _check_end(battle)
                if _combat_active(unit):_start_entities(battle,unit)
                if battle["status"] != "active" or battle.get("decision_pending"):
                    return None
                if not _combat_active(unit):
                    battle["turn_index"] += 1
                    continue
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
    battle["log"].append("The alarm bell answers across the hills. Warhost reinforcements enter the camp.")


def _wake_ambush(battle: dict, target: dict | None = None) -> None:
    """Only the opening ambush sleep shares an alarm; ordinary Sleep is local."""
    if not battle.get("ambush_sleep_until_round") or (target is not None and target.get("team") != "enemy"):
        return
    battle.pop("ambush_sleep_until_round", None)
    for unit in battle["units"].values():
        unit["statuses"] = [s for s in unit.get("statuses", []) if s.get("id") != "ambush_sleep"]
    battle["log"].append("The attack wakes the whole camp." if target is not None else "The camp wakes. The ambush preparation window has ended.")


def _deal_damage(
    battle: dict, attacker: dict, target: dict, bonus: int = 0, armor_pierce: int = 0,
    intent: str = "lethal", ability: dict | None = None,
) -> int:
    source_unit=battle.get('units',{}).get(attacker.get('id'))
    if not attacker.get('status_tick') and source_unit and not _combat_active(source_unit):return 0
    if not attacker.get("status_tick"):
        _wake_ambush(battle, target)
    if ability:
        finisher = attacker.get('knockout_finisher',0) if ability.get('source_name', attacker.get('weapon')) == attacker.get('weapon') else 0
        attacker = {**attacker, 'knockout_finisher':finisher, "attack": ability.get("attack", attacker["attack"]),
                    "attack_elevation_rule": ability["elevation_rule"],
                    "element": ability.get("element", attacker.get("element")),
                    "on_hit": ability.get("on_hit", attacker.get("on_hit")),"weapon":ability.get('source_name',attacker.get('weapon',''))}
    armor = max(0, int(target.get("armor", 0)) - armor_pierce)
    if conditions.has(target, 'vulnerable') and not attacker.get('status_tick'):
        armor = max(0, armor - 3)
        conditions.remove(target, 'vulnerable')
    damage = max(1, int(attacker["attack"]) + bonus - armor)
    if conditions.has(attacker, 'berserk') and not attacker.get('status_tick'):
        damage += 3
    if conditions.has(target, 'freeze') and not attacker.get('status_tick'):
        damage = max(1, round(damage * 1.25))
        if attacker.get('element') == 'fire':
            conditions.remove(target, 'freeze')
    if not attacker.get('status_tick'):
        rules=attacker.get('gear_rules',{})
        if target['hp']<=target.get('max_hp',target['hp'])*.5:damage+=rules.get('wounded_damage',0)
        if target.get('boss') or target.get('kind') in {'chieftain','boss'}:damage+=rules.get('boss_damage',0)
    perks=attacker.get('perk_modifiers',{})
    if target.get('race') in {'Goblin','Hobgoblin','Bugbear'}:damage+=perks.get('damage_goblin',0)
    if target.get('race') in {'Undead','Revenant','Banshee','Vampire'}:damage+=perks.get('damage_deathless',0)
    if attacker.get('attack_elevation_rule')=='melee':damage+=perks.get('melee_damage',0)
    if attacker.get('attack_elevation_rule')=='ignore':
        reduction=target.get('perk_modifiers',{}).get('magic_reduction',0)
        if 'magic' in target.get('racial_resistances',[]):reduction+=20
        if 'magic' in target.get('racial_weaknesses',[]):reduction-=20
        damage=max(1,round(damage*(1-min(60,reduction)/100)))
    element = attacker.get("element")
    if element and intent != "nonlethal":
        affinity = {"fire": "burn", "ice": "freeze", "holy": "radiant"}.get(element, element)
        factor = 1.0
        if {element, affinity}.intersection(target.get("racial_resistances", [])):
            factor -= .25
        if {element, affinity}.intersection(target.get("racial_weaknesses", [])):
            factor += .25
        damage = max(1, round(damage * factor))
    if target.get("guarding") and not attacker.get("status_tick") and not attacker.get('environmental_fall'):
        damage = max(1, damage // 2)
        target["guarding"] = False
        _record_sound(battle, "shield_block", offset=185)
    if not attacker.get('capture_only') and not attacker.get('environmental_fall'):
        damage,absorbed=conditions.absorb(target,damage)
        if absorbed:
            battle['log'].append(f"{target['name']}'s Barrier absorbs {absorbed} damage.")
            _record_sound(battle,'shield_block',offset=185)
    previous_hp = int(target["hp"])
    if intent == 'lethal' and not attacker.get('status_tick') and damage >= previous_hp and attacker.get('knockout_finisher'):
        counter = int(battle.get('finisher_counter', 0))
        battle['finisher_counter'] = counter + 1
        roll = random.Random(f"{battle.get('seed')}:finisher:{counter}:{attacker.get('id')}:{target['id']}").randint(1,100)
        if roll <= attacker['knockout_finisher']:
            intent = 'nonlethal'
            battle['log'].append(f"{attacker['weapon']} leaves {target['name']} unconscious instead of killing them.")
    target["hp"] = max(0, previous_hp - damage)
    if target['hp']==0 and intent!='nonlethal' and not attacker.get('environmental_fall') and target.get('gear_rules',{}).get('lifeline') and not target.get('lifeline_used'):
        target['hp']=1;target['lifeline_used']=True
        target['statuses']=[s for s in target.get('statuses',[]) if s.get('id')!='lifeline_ready']+[{'id':'lifeline_spent'}]
        battle['log'].append(f"{target['name']}'s survival safeguard leaves them at 1 HP. It is spent for this battle.")
    if not attacker.get("status_tick") and damage>0:
        target["statuses"] = [status for status in target.get("statuses", []) if status.get("id") != "sleep"]
    proc = attacker.get("on_hit")
    if target["hp"] > 0 and intent != "nonlethal" and proc:
        sid = proc["id"]
        immune = sid == "poison" and (sid in target.get("racial_resistances", []) or target.get("race") in {"Undead", "Revenant", "Banshee", "Golem", "Automaton"})
        counter = int(battle.get("proc_counter", 0))
        battle["proc_counter"] = counter + 1
        roll = random.Random(f"{battle.get('seed')}:proc:{counter}:{attacker.get('id')}:{target['id']}").randint(1, 100)
        proc_chance = int(proc["chance"])
        if sid in target.get("racial_resistances", []):
            proc_chance //= 2
        if sid in target.get("racial_weaknesses", []):
            proc_chance = min(95, proc_chance + 15)
        if not immune and roll <= proc_chance:
            if conditions.apply(target, sid, int(proc['turns']), attacker):
                battle["log"].append(f"{target['name']} suffers {sid}.")
    if target["hp"] <= 0:
        target["conscious"] = False
        target["guarding"] = False
        if target.get('temporary'):
            target.update(alive=False,extracted=True,condition='dismissed')
            battle['log'].append(f"{target['name']} is destroyed. It leaves no prisoner or loot.")
        elif intent == "nonlethal":
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
    source=battle.get("units",{}).get(attacker.get("id"))
    if source and source.get('temporary'):source=battle['units'].get(source['owner_id'])
    if source and source.get("team")=="player" and not target.get('temporary'):
        facts=source.setdefault("combat_record",{})
        actual=0 if attacker.get("capture_only") else max(0,previous_hp-int(target["hp"]))
        facts["total_damage"]=facts.get("total_damage",0)+actual
        source["turn_damage"]=source.get("turn_damage",0)+actual
        facts["highest_turn_damage"]=max(facts.get("highest_turn_damage",0),source["turn_damage"])
        if previous_hp>0 and target.get("condition") in {"dead","unconscious"}:
            key="kills" if target["condition"]=="dead" else "subdues"
            facts[key]=facts.get(key,0)+1
    if previous_hp>0 and target.get("condition") in {"dead","unconscious"}:
        facts=target.setdefault("combat_record",{})
        facts["times_defeated"]=facts.get("times_defeated",0)+1
        if target["condition"]=="dead":
            battle.setdefault("animation_events",[]).append({"type":"death_burst","unit_id":target["id"],"x":target["x"],"y":target["y"],"race":target.get("race","Human")})
    return damage


def _capture_attempt(battle: dict, actor: dict, target: dict) -> None:
    if not _combat_active(actor):return
    if target.get('temporary'):raise ValueError('Temporary deployments cannot become prisoners')
    if not actor.get('capture_weapon'):
        raise ValueError('Equip a capture weapon to attempt Subdue')
    if not _combat_active(target) or not _can_attack(battle, actor, target):
        raise ValueError('Choose an active target within capture range')
    concealment.reveal(battle, actor)
    preview = _capture_preview(battle, actor, target)
    counter = int(battle.get('roll_counter', 0))
    battle['roll_counter'] = counter + 1
    roll = random.Random(f"{battle.get('seed')}:{counter}:{actor['id']}:{target['id']}").randint(1,100)
    # The first attempt wakes the camp even when it fails; preview includes the initial sleep advantage.
    _wake_ambush(battle, target)
    success = roll <= preview['chance']
    if success:
        restrained = {**actor, 'attack': target['max_hp']*100 + target.get('armor',0),
                      'status_tick': True, 'capture_only': True, 'element': None, 'on_hit': None}
        _deal_damage(battle, restrained, target, intent='nonlethal')
    battle['log'].append(f"{actor['name']} attempts to capture {target['name']}: {'successful' if success else 'failed'} ({roll} vs {preview['chance']}% capture chance).")
    _record_melee_animation(battle, actor, target, success, actor['attack_elevation_rule'])


def _capture_preview(battle: dict, actor: dict, target: dict) -> dict:
    from .capture_weapons import capture_preview
    result = capture_preview(actor, target)
    accuracy, _ = _elevation_attack_modifier(battle, actor, target, actor['attack_elevation_rule'])
    if conditions.has(actor, 'blind'): accuracy -= 35 if actor['attack_elevation_rule'] != 'melee' else 15
    if conditions.has(actor, 'fear'): accuracy -= 15
    result['chance'] = max(2, min(60 if target.get('boss') or target.get('kind') == 'chieftain' else 95, result['chance']+accuracy))
    return result


def _tick_gear_statuses(battle: dict, unit: dict) -> None:
    """Only duration-bearing gear effects tick; repeated views never tick again."""
    for status in list(unit.get("statuses", [])):
        if status.get("id") not in {"burn", "poison"} or "turns" not in status:
            continue
        damage = max(2, min(5, round(unit["max_hp"] * .04)))
        source = {"id": status.get("source_id"), "name": status.get("source_name") or status["id"].title(),
                  "weapon": status.get("source_weapon", ""), "attack": damage, "status_tick": True}
        dealt = _deal_damage(battle, source, unit, armor_pierce=int(unit.get("armor", 0)))
        battle["log"].append(f"{unit['name']} takes {dealt} damage from {status['id']}.")
        status["turns"] -= 1
        if status["turns"] <= 0:
            unit["statuses"] = [s for s in unit["statuses"] if s is not status]
        if not _combat_active(unit):
            _record_sound(battle, "unit_death")
            break


def _tick_bleed(battle: dict, unit: dict) -> None:
    status = next((s for s in unit.get('statuses', []) if s.get('id') == 'bleed'), None)
    if not status or not _combat_active(unit) or not (unit.get('moved') or unit.get('physical_action')):
        return
    source = {'id': status.get('source_id'), 'name': status.get('source_name', 'Bleeding'),
              'weapon': 'bleeding', 'attack': max(2, min(4, round(unit['max_hp'] * .04))), 'status_tick': True}
    dealt = _deal_damage(battle, source, unit, armor_pierce=int(unit.get('armor', 0)))
    battle['log'].append(f"{unit['name']} takes {dealt} bleeding damage after exertion.")


def _victory_outcome(battle: dict) -> str:
    optional = [objective for objective in battle.get("objectives", []) if not objective.get("required")]
    return "critical_success" if optional and all(objective.get("complete") for objective in optional) and not battle.get("reinforcements_spawned") else "success"


def _panic_unit(unit: dict) -> None:
    unit["panicked"] = True
    if not any(status.get("id") == "panic" for status in unit.get("statuses", [])):
        unit.setdefault("statuses", []).append({"id": "panic"})


def _trigger_battle_victory(battle: dict, panic_enemies: bool = False) -> None:
    if any(u.get('mercenary_hostile') and _combat_active(u) for u in battle['units'].values()):
        return
    if battle.get("battle_won"):
        return
    battle["battle_won"] = True
    battle["decision_pending"] = True
    battle["victory_phase"] = "decision"
    if panic_enemies:
        for enemy in _living(battle, "enemy"):
            if not enemy.get("mercenary_hostile"):_panic_unit(enemy)
    battle["log"].append(battle.get("victory_log", "The required objective is secured. The guild can withdraw or pursue the remaining opportunities."))


def _secure_battlefield_loot(battle: dict) -> None:
    if battle.get("loot_secured"):
        return
    recovered = {
        unit["id"] for unit in battle["units"].values()
        if unit["team"] == "enemy" and unit.get("condition") == "dead" and not unit.get("fled") and not unit.get('lost_in_pit') and not unit.get('temporary')
    }
    battle["auto_looted_ids"] = sorted(recovered)
    battle["auto_captured_ids"] = sorted(
        unit["id"] for unit in battle["units"].values()
        if unit["team"] == "enemy" and unit.get("condition") == "unconscious" and not unit.get("fled") and not unit.get('lost_in_pit') and not unit.get('temporary')
    )
    battle["loot_secured"] = True
    battle["log"].append(
        f"The victors strip usable gear and coin from {len(recovered)} fallen enem{'y' if len(recovered) == 1 else 'ies'} and secure every unconscious prisoner."
        if recovered else "The victors secure the camp, but there are no fallen enemies to strip."
    )


def _claim_victory(battle: dict) -> None:
    if any(u.get('mercenary_hostile') and _combat_active(u) for u in battle['units'].values()):
        raise ValueError('Stop the hostile mercenary before claiming victory')
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
    entities.cleanup(battle,_combat_active)
    spaces.cleanup_zones(battle,_combat_active)
    if battle.get('mercenary_interlude') or battle.get("encounter_id", "").startswith("contract:"):
        _check_contract_end(battle)
    elif battle.get("encounter_id") == "goblin_captive_cart":
        _check_captive_cart_end(battle)
    elif battle.get("encounter_id") == "goblin_smoke_signals":
        _check_smoke_signals_end(battle)
    elif battle.get("encounter_id") == "frontier_watch_defense":
        _check_frontier_watch_end(battle)
    else:
        _check_warcamp_end(battle)
    hostile = any(u.get('mercenary_hostile') and u.get('condition') not in ('dead','unconscious') for u in battle['units'].values())
    for objective in battle.get('objectives',[]):
        if objective.get('id')=='mercenary_threat':objective['complete']=not hostile
    crew = [u for u in battle['units'].values() if u['team']=='player' and not u.get('mercenary_guest') and not u.get('temporary')]
    if hostile and not battle.get('mercenary_interlude'):
        if any(u.get('mercenary_hostile') and u.get('fled') for u in battle['units'].values()):
            battle.update(status='complete',outcome='failure',battle_won=False,decision_pending=False)
            return
        battle.update(battle_won=False, decision_pending=False)
        if not any(_combat_active(u) for u in crew):
            battle.update(status='complete',outcome='failure' if any(u.get('extracted') for u in crew) else 'critical_failure')
        elif battle.get('status')=='complete' and battle.get('outcome') in ('success','critical_success'):
            battle.update(status='active',outcome=None)


def _finish_turn(battle: dict) -> None:
    order = battle.get("turn_order", [])
    index = int(battle.get("turn_index", 0))
    unit = battle["units"].get(order[index]) if index < len(order) else None
    if unit:
        _tick_bleed(battle, unit)
        _finish_entities(battle,unit)
        conditions.finish_activation(unit)
        unit.pop('physical_action', None)
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


def _scout_path(battle, unit, path):
    """Stop provisional guild movement when new opposition is discovered."""
    if not concealment.cover_cells(battle):
        return path
    accepted = []
    original = (unit['x'], unit['y'])
    try:
        for x, y in path:
            occupant = next((other for other in battle['units'].values()
                             if _combat_active(other) and other['id'] != unit['id']
                             and (other['x'],other['y']) == (x,y)), None)
            if occupant:
                if unit.get('team') == 'player':
                    concealment.reveal(battle, occupant, reason='contact')
                break
            unit['x'], unit['y'] = x, y
            accepted.append((x, y))
            spotted = concealment.refresh(battle)
            if spotted and unit.get('team') == 'player':
                break
    finally:
        unit['x'], unit['y'] = original
    return accepted


def _visible_enemies(battle):
    return [u for u in _living(battle, 'enemy') if not concealment.unseen(u)]


def _search_brush(battle, unit):
    covers = concealment.cover_cells(battle)
    searched = {tuple(p) for p in battle.get('searched_bushes', [])}
    choices = [{'x':x, 'y':y} for x,y in sorted(covers-searched)
               if not _blocked(battle,x,y,unit['id'],unit.get('movement_type'))]
    if choices:
        _move_to_nearest_tile(battle, unit, choices)
    _guard(battle, unit)
    _finish_turn(battle)


def _record_movement(battle: dict, unit: dict, start: tuple[int, int], path: list[tuple[int, int]]) -> None:
    if not path:
        return
    battle.setdefault("animation_events", []).append({
        "type": "movement",
        "unit_id": unit["id"],
        "points": [{"x": start[0], "y": start[1]}] + [{"x": x, "y": y} for x, y in path],
        "extracted": False,
        "concealed": concealment.unseen(unit),
    })


def _record_sound(battle: dict, cue: str, offset: int = 0, duration: int = 0) -> None:
    battle.setdefault("animation_events", []).append({
        "type": "sound", "cues": [{"name": cue, "offset": offset}], "duration": duration,
    })


def _record_melee_animation(battle: dict, attacker: dict, target: dict, hit: bool, rule: str | None = None) -> None:
    if (rule or attacker.get('attack_elevation_rule')) in {'melee', 'ballistic'}:
        attacker['physical_action'] = True
    rule = rule or attacker.get("attack_elevation_rule", "melee")
    if rule != "melee":
        ranged = rule == "ballistic"
        cues = [{"name": "bow_release" if ranged else "magic_cast", "offset": 45},
                {"name": ("arrow_hit" if ranged else "magic_hit") if hit else "attack_miss", "offset": 220}]
        if hit and target.get("condition") in {"dead", "unconscious"}:
            cues.append({"name": "unit_death" if target["condition"] == "dead" else "unit_unconscious", "offset": 350})
        if not ranged:
            battle.setdefault("animation_events", []).append({"type":"magic_projectile", "attacker_id":attacker["id"],"target_id":target["id"],"from":{"x":attacker["x"],"y":attacker["y"]},"to":{"x":target["x"],"y":target["y"]},"hit":hit})
        battle.setdefault("animation_events", []).append({"type":"sound", "cues":cues, "duration":490})
        return
    battle.setdefault("animation_events", []).append({
        "type": "melee_attack", "attacker_id": attacker["id"], "target_id": target["id"], "hit": bool(hit),
        "target_condition": target.get("condition", "active"),
    })


def _route_with_gates(battle, unit, goals):
    """Compare walking detours with routes that spend an activation opening a door."""
    if not goals:return [],{},{}
    gates = {cell: tile for tile in battle.get('terrain', [])
             if tile.get('kind') == 'gate' and not tile.get('destroyed') and tile.get('state') != 'opened'
             and not tile.get('edge_wall')
             for cell in occupied_tiles(tile)}
    planning = {**battle, 'terrain': [{**t, 'blocking':False} if t.get('kind') == 'gate' and not t.get('destroyed') else t
                                     for t in battle.get('terrain', [])]}
    start=(unit['x'],unit['y']);queue=[(0,*start)];parents={start:None};costs={start:0};goal=None
    while queue:
        cost,x,y=heapq.heappop(queue);cell=(x,y)
        if cost != costs[cell]:continue
        if cell in goals:goal=cell;break
        for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if not _can_step(planning,x,y,nx,ny,unit):continue
            crossing = any(t.get('kind') == 'gate' for t in crossed_walls(battle, (x,y), (nx,ny)))
            candidate=cost+_step_cost(planning,x,y,nx,ny,unit)+(max(1,_movement_limit(unit)) if (nx,ny) in gates or crossing else 0)
            if candidate>=costs.get((nx,ny),10**9):continue
            costs[(nx,ny)]=candidate;parents[(nx,ny)]=cell;heapq.heappush(queue,(candidate,nx,ny))
    if goal is None:return [],costs,gates
    path=[]
    while goal!=start:path.append(goal);goal=parents[goal]
    path=list(reversed(path))
    previous=start; route_gates={}
    for cell in path:
        doors=[t for t in crossed_walls(battle, previous, cell) if t.get('kind')=='gate']
        if cell in gates:route_gates[cell]=gates[cell]
        elif doors:route_gates[cell]=doors[0]
        previous=cell
    return path,costs,route_gates


def _pursuit_goals(battle, unit, target):
    gate_cells={cell for t in battle.get('terrain',[]) if t.get('kind')=='gate' and not t.get('destroyed') for cell in occupied_tiles(t)}
    return {(target['x']+dx,target['y']+dy) for dx,dy in ((1,0),(-1,0),(0,1),(0,-1))
            if (not _blocked(battle,target['x']+dx,target['y']+dy,unit['id'],unit.get('movement_type'))
                or (target['x']+dx,target['y']+dy) in gate_cells)
            and not any(t.get('kind') != 'gate' for t in crossed_walls(battle,
                         (target['x']+dx,target['y']+dy),(target['x'],target['y']),sight=True))}


def _move_toward(battle: dict, unit: dict, target: dict) -> None:
    start = (unit["x"], unit["y"])
    path, costs, gates = _route_with_gates(battle,unit,_pursuit_goals(battle,unit,target))
    # Stop beside the first closed gate; the next activation can operate it.
    first_gate=next((i for i,p in enumerate(path) if p in gates),len(path))
    path=path[:first_gate]
    if path:
        reachable_path = _scout_path(battle, unit, [point for point in path if costs[point] <= _movement_limit(unit)])
        if reachable_path:
            x,y=reachable_path[-1];unit['exit_ready']=False
            unit['x'],unit['y'],unit['moved']=x,y,True
            _record_movement(battle,unit,start,reachable_path)
            if unit.get('carrying') in battle['units']:
                carried=battle['units'][unit['carrying']];carried['x'],carried['y']=x,y
            _apply_zone_route(battle,unit,reachable_path)
            _apply_tile_entry(battle,unit)


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
    reachable = _scout_path(battle, unit, [point for point in path if costs[point] <= _movement_limit(unit)])
    if reachable:
        unit["exit_ready"] = False
        unit["x"], unit["y"] = reachable[-1]
        unit["moved"] = True
        _record_movement(battle, unit, start, reachable)
        if unit.get("carrying") in battle["units"]:
            carried = battle["units"][unit["carrying"]]
            carried["x"], carried["y"] = unit["x"], unit["y"]
        _apply_zone_route(battle,unit,reachable)
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
        path,_,gates=_route_with_gates(battle,unit,exits)
        gate_index=next((i for i,p in enumerate(path) if p in gates),None)
        if gate_index==0:
            _interact(battle,unit,gates[path[0]]['id'])
            return
        if gate_index is not None:
            x,y=path[gate_index-1]
            tiles=[{'x':x,'y':y}]
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


def _ambush_target(battle, unit, targets):
    """Wait for a real strike through the lane; abandon the plan before it stalls."""
    # Once the rest of the opposition is beaten, hidden survivors actively hunt.
    visible_allies = [u for u in _living(battle, 'enemy') if not concealment.unseen(u)]
    if not visible_allies or unit.get('ambush_waits', 0) >= 2:
        unit['ambush_plan'] = 'pursue'
        return min(targets, key=lambda t: (_distance(unit,t),t['hp']))
    lane = {tuple(p) for p in battle.get('ambush_lane', [])}
    reach = unit['attack_range']
    costs, parents = _movement_tree(battle, unit)
    opportunities = []
    for target in targets:
        # A clear shot from concealment needs no speculative move or bonus action.
        direct = _can_attack(battle, unit, target)
        if not direct and lane and (target['x'],target['y']) not in lane:
            continue
        actor, approach = _attack_position(battle, unit, target, reach, costs, parents)
        if direct or actor:
            nearby_allies = sum(_distance(target, other) <= 2 for other in targets if other['id'] != target['id'])
            opportunities.append((not direct, nearby_allies, target['hp']/max(1,target['max_hp']),
                                  _distance(unit,target), target['id'], target))
    if opportunities:
        unit['ambush_plan'] = 'strike'
        return min(opportunities, key=lambda entry: entry[:-1])[-1]
    return None


def _enemy_turn(battle: dict, unit: dict) -> None:
    concealment.refresh(battle)
    if _pit_exits(battle,unit):
        _climb_out(battle,unit,_pit_exits(battle,unit)[0]);_finish_turn(battle);return
    if any(s.get("id") == "ambush_sleep" for s in unit.get("statuses", [])):
        battle["log"].append(f"{unit['name']} is still asleep.")
        _finish_turn(battle)
        return
    if unit.get('forced_skip'):
        battle['log'].append(f"{unit['name']} cannot act this turn.")
        _finish_turn(battle)
        return
    if unit.get("panicked"):
        _flee_turn(battle, unit)
        return
    if conditions.has(unit, 'mute') and unit.get('attack_elevation_rule') in {'ignore','line_of_effect'}:
        _guard(battle, unit)
        _finish_turn(battle)
        return
    if unit.get('mercenary_hostile_all'):
        targets = [u for u in _living(battle) if u['id']!=unit['id'] and u.get('team') in ('player','enemy')]
    elif unit.get('mercenary_guest') and unit['team']=='player':
        crew = [u for u in _living(battle,'player') if not u.get('mercenary_guest')]
        if not crew:
            unit.update(extracted=True,alive=False)
            _finish_turn(battle)
            return
        targets = _living(battle,'enemy')
    else:
        targets = _living(battle,'player') + [u for u in _living(battle,'enemy') if u.get('mercenary_hostile_all') and u['id']!=unit['id']]
    targets = conditions.hostile_units(battle, unit, _living(battle))
    if not targets:
        _finish_turn(battle); return
    targets = [target for target in targets if unit.get('team') != 'player' or not concealment.unseen(target)]
    if not targets:
        _search_brush(battle, unit)
        return
    target = min(targets, key=lambda candidate: (_distance(unit, candidate), candidate["hp"]))
    if unit.get('bush_ambusher') and concealment.unseen(unit) and not battle.get('ambush_sprung'):
        target = _ambush_target(battle, unit, targets)
        if target is None:
            unit['ambush_waits'] = int(unit.get('ambush_waits', 0)) + 1
            _guard(battle, unit)
            _finish_turn(battle)
            return
        battle['ambush_sprung'] = True
    if _auto_open_gate(battle, unit, target):
        return
    snared = int(unit.get("snared_until_round", 0)) >= int(battle.get("round", 1))
    if not _can_attack(battle, unit, target) and not snared:
        _move_toward(battle, unit, target)
        if unit.get('ambush_plan') != 'strike' or not _can_attack(battle, unit, target):
            target = min(targets, key=lambda candidate: (_distance(unit, candidate), candidate["hp"]))
    if _can_attack(battle, unit, target):
        target = conditions.confused_target(battle, unit, target, lambda u: _can_attack(battle, unit, u))
        if unit.get('capture_weapon'):
            _capture_attempt(battle, unit, target)
        else:
            target,hit,damage,preview,roll=_perform_attack(battle,unit,target,unit["attack_elevation_rule"])
            if hit:
                battle["log"].append(f"{unit['name']} attacks {target['name']} with {unit['weapon']} for {damage} damage.")
            else:
                battle["log"].append(f"{unit['name']} misses {target['name']} ({roll} vs {preview['chance']}% accuracy).")
    elif snared:
        battle["log"].append(f"{unit['name']} struggles against the snare and cannot advance.")
    else:
        battle["log"].append(f"{unit['name']} advances through the warcamp.")
    unit["acted"] = True
    _finish_turn(battle)


def _advance_to_player(battle: dict) -> None:
    concealment.refresh(battle)
    safety = 0
    while battle["status"] == "active" and safety < 100:
        concealment.refresh(battle)
        unit = _current_unit(battle)
        if not unit:
            return
        if unit.get('forced_skip'):
            battle['log'].append(f"{unit['name']} cannot act this turn.")
            _finish_turn(battle)
            safety += 1
            continue
        if unit['team'] == 'player' and (conditions.has(unit, 'charm') or conditions.has(unit, 'berserk')):
            _enemy_turn(battle, unit)
            safety += 1
            continue
        if unit.get('mercenary_guest') and unit['team']=='player':
            _enemy_turn(battle,unit)
            safety += 1
            continue
        if unit["team"] == "player":
            if battle.get("retreat_all") or _should_party_panic(battle, unit):
                if _should_party_panic(battle, unit) and not unit.get("panicked"):
                    _panic_unit(unit)
                    battle["log"].append(f"{unit['name']} loses their nerve and tries to escape.")
                _flee_turn(battle, unit)
                safety += 1
                continue
            if independence_check(battle,unit):
                _independent_turn(battle,unit)
                safety += 1
                continue
            return
        _enemy_turn(battle, unit)
        safety += 1


def _independent_turn(battle: dict,unit: dict) -> None:
    profile=personality_profile(unit)
    behavior=profile[2]
    battle["log"].append(f"{unit['name']} acts independently ({unit.get('loyalty',100)} loyalty; {profile[0]}).")
    unit["independent_actions"]=unit.get("independent_actions",0)+1
    if behavior=="coward" or (behavior=="survival" and unit["hp"]<=unit["max_hp"]*.35):
        _flee_turn(battle,unit)
        return
    if behavior in {"guardian","survival"}:
        allies=[u for u in _living(battle,"player") if u["id"]!=unit["id"]]
        enemies=_visible_enemies(battle)
        reachable=_reachable(battle,unit,unit["move"])
        if reachable:
            if behavior=="guardian" and allies:
                ally=min(allies,key=lambda u:(u["hp"]/u["max_hp"],_distance(unit,u)))
                point=min(reachable,key=lambda p:(abs(p[0]-ally["x"])+abs(p[1]-ally["y"]),reachable[p]))
            else:
                point=max(reachable,key=lambda p:(min((abs(p[0]-e["x"])+abs(p[1]-e["y"]) for e in enemies),default=0),_tile_height(battle,*p),-reachable[p]))
            _move_to_nearest_tile(battle,unit,[{"x":point[0],"y":point[1]}])
        _guard(battle,unit);unit["acted"]=True;_finish_turn(battle)
        return
    if behavior=="merciful":
        enemies=_visible_enemies(battle)
        if enemies and unit.get("nonlethal_capable"):
            target=min(enemies,key=lambda u:(_distance(unit,u),u["hp"]))
            if not _can_attack(battle,unit,target,unit["attack_range"]):_move_toward(battle,unit,target)
            if _can_attack(battle,unit,target,unit["attack_range"]):
                _capture_attempt(battle,unit,target)
            else:_guard(battle,unit)
        else:_guard(battle,unit)
        unit["acted"]=True;_finish_turn(battle)
        return
    unit["independent_style"]=behavior
    _player_auto_turn(battle,unit,"objective" if behavior=="objective" else "balanced")
    unit.pop("independent_style",None)


def _guard(battle: dict,unit: dict) -> None:
    unit['guarding']=True
    heal=min(unit.get('gear_rules',{}).get('guard_heal',0),unit['max_hp']-unit['hp'])
    if heal>0:
        unit['hp']+=heal
        battle['log'].append(f"{unit['name']} recovers {heal} HP while guarding.")


def _support_eligible(battle, actor, target, effect):
    if not target or target.get('team') != actor.get('team') or not _combat_active(target):
        return False
    if _distance(actor, target) > int(effect.get('range', 1)) or not _line_of_sight(battle, actor, target):
        return False
    return ((effect.get('deployment') and target['id']==actor['id'] and entities.available(battle,actor,effect['deployment']))
            or (effect.get('form_change') and target['id']==actor['id'] and not actor.get('capture_weapon') and not actor.get('carrying') and not actor.get('carrying_object'))
            or effect.get('zone_setup')
            or (effect.get('heal', 0) > 0 and target['hp'] < target['max_hp'])
            or (effect.get('barrier',0)>max((s.get('amount',0) for s in target.get('statuses',[]) if s['id']=='barrier'),default=0))
            or (effect.get('guard_ally') and not target.get('guarding'))
            or any(s.get('id') in effect.get('cleanses', []) for s in target.get('statuses', [])))


def _apply_support(battle, actor, target, effect):
    if not _support_eligible(battle, actor, target, effect):
        raise ValueError('Choose a conscious ally in range who needs healing or treatment')
    _commit_player_movement(battle, actor)
    healing = min(target['max_hp'] - target['hp'], int(effect.get('heal', 0)))
    target['hp'] += healing
    conditions.remove(target, *effect.get('cleanses', []))
    if effect.get('guard_ally'):
        target['guarding'] = True
    if not (conditions.has(target, 'stun') or conditions.has(target, 'sleep') or conditions.has(target, 'paralyze')):
        target.pop('forced_skip', None)
    if not conditions.has(target, 'paralyze'):
        target.pop('paralyzed_move', None)
    actor['acted'] = True
    battle['log'].append(f"{actor['name']} uses {effect['name']} on {target['name']}: {healing} HP restored" + (', harmful effects treated.' if effect.get('cleanses') else '.'))
    _record_sound(battle, 'magic_cast' if effect.get('elevation_rule') == 'line_of_effect' else 'guard')


def _support_effect(skill, actor):
    effect = dict(skill)
    if skill.get('ability_version'):
        effect['heal']=sum(e['amount'] for e in skill['effects'] if e['type']=='heal')
        effect['cleanses']=[s for e in skill['effects'] if e['type']=='cleanse' for s in e['statuses']]
        effect['guard_ally']=any(e['type']=='guard' for e in skill['effects'])
        effect['barrier']=max((e['amount'] for e in skill['effects'] if e['type']=='barrier'),default=0)
        effect['form_change']=any(e['type']=='form' for e in skill['effects'])
        effect['zone_setup']=any(e['type']=='zone' for e in skill['effects'])
        effect['deployment']=next((e['entity'] for e in skill['effects'] if e['type']=='deploy'),None)
        return effect
    if effect.get('heal'):
        effect['heal'] += int(actor.get('intelligence', 4)) // 2
    return effect


def _deployment_positions(battle,owner,kind):
    profile=entities.PROFILES[kind]
    candidates=[]
    for dx,dy in ((0,-1),(1,0),(0,1),(-1,0)):
        x,y=owner['x']+dx,owner['y']+dy
        probe={**owner,'movement_type':'flying' if profile.get('flying') else 'ground'}
        material,_=_ground_at(battle,x,y)
        if (not _blocked(battle,x,y,None,probe['movement_type']) and material!='water'
            and not tactics.pit_at(battle,x,y) and _can_step(battle,owner['x'],owner['y'],x,y,probe)):
            candidates.append((x,y))
    count=profile.get('count',1)
    if len(candidates)<count:raise ValueError('Not enough open adjacent ground for deployment')
    return candidates[:count]


def _start_entities(battle,owner):
    if not entities.owned(battle,owner):return
    def start(unit):
        conditions.start_activation(battle,unit)
        unit['zone_location']=[unit['x'],unit['y']]
        _trigger_zones(battle,unit,'start')
        if _combat_active(unit):_tick_gear_statuses(battle,unit)
    entities.start_owner(battle,owner,start)
    entities.cleanup(battle,_combat_active)


def _entity_targets(battle,entity):
    owner=battle['units'].get(entity['owner_id'])
    if not owner:return []
    # The entity adopts owner allegiance; it never reads concealed enemies.
    targets=conditions.hostile_units(battle,owner,_living(battle))
    return [u for u in targets if not concealment.unseen(u)]


def _entity_attack(battle,owner,entity,target,power):
    source={**entity,'attack':power,'credit_owner_id':owner['id']}
    _,hit,damage,_,_=_perform_attack(battle,source,target,entity['attack_elevation_rule'])
    battle['log'].append(f"{entity['name']} hits {target['name']} for {damage} damage." if hit else f"{entity['name']} misses {target['name']}.")
    entity['acted']=True
    entity['fired_at']=owner.get('ability_activation',0)


def _finish_entities(battle,owner):
    crew=entities.owned(battle,owner)
    if not crew:return
    stamp=owner.get('ability_stamp')
    if owner.get('entities_finished_stamp')==stamp:return
    owner['entities_finished_stamp']=deepcopy(stamp)
    if not _combat_active(owner) or owner.get('forced_skip'):
        for unit in crew:conditions.finish_activation(unit)
        return
    ready=[u for u in crew if u['deployed_at']<owner.get('ability_activation',0)
           and u['policy']=='automatic' and not u.get('forced_skip') and not u.get('panicked')
           and not (u['resource_pool']=='capacity' and conditions.has(owner,'mute'))
           and not u.get('acted') and u.get('fired_at')!=owner.get('ability_activation',0)]
    remaining=max(0,entities.budget(owner)-owner.get('entity_budget_spent',0))
    for i,unit in enumerate(ready):
        share=min(unit['entity_output'],remaining//max(1,len(ready)-i))
        if share<1:continue
        profile=entities.PROFILES[unit['entity_kind']]
        if profile.get('heal'):
            hostile_ids={u['id'] for u in _entity_targets(battle,unit)}
            friends=[u for u in _living(battle) if u['id'] not in hostile_ids and not u.get('temporary') and u['hp']<u['max_hp'] and not conditions.has(u,'burn')]
            target=min(friends,key=lambda u:(u['hp']/u['max_hp'],u['id'])) if friends else None
        else:
            targets=_entity_targets(battle,unit)
            target=min(targets,key=lambda u:(not _can_attack(battle,unit,u,unit['attack_range']),_distance(unit,u),u['id'])) if targets else None
        if not target:continue
        if not unit.get('stationary') and not _can_attack(battle,unit,target,unit['attack_range']):_move_toward(battle,unit,target)
        if not _combat_active(unit) or not _can_attack(battle,unit,target,unit['attack_range']):continue
        # Budget is spent for an attempted shot, including misses and absorption.
        remaining-=share;owner['entity_budget_spent']=owner.get('entity_budget_spent',0)+share
        if profile.get('heal'):
            amount=min(share,target['max_hp']-target['hp']);target['hp']+=amount
            unit['acted']=True;unit['fired_at']=owner.get('ability_activation',0)
            battle['log'].append(f"{unit['name']} restores {amount} HP to {target['name']}.")
        else:_entity_attack(battle,owner,unit,target,share)
    for unit in crew:
        if unit.get('movement_origin'):_commit_player_movement(battle,unit)
        conditions.finish_activation(unit)


def _entity_command(battle,owner,command):
    unit=battle['units'].get(command.get('entity_id'))
    if not entities.can_command(battle,owner,unit):raise ValueError('Choose an owned deployment ready this activation')
    action=command['action']
    if action=='dismiss_summon':
        _commit_player_movement(battle,owner);entities.dismiss(battle,owner,unit);owner['acted']=True;return
    if unit['resource_pool']=='capacity' and conditions.has(owner,'mute'):raise ValueError('Mute interrupts magical summon commands')
    if unit['policy']!='commanded' and action!='operate_turret':raise ValueError('This entity follows its automatic policy')
    if action=='summon_move':
        x,y=int(command.get('x',-1)),int(command.get('y',-1))
        costs,parents=_movement_tree(battle,unit)
        if (x,y) not in costs:raise ValueError('Destination is outside this deployment movement budget')
        start=(unit['x'],unit['y']);origin=unit.get('movement_origin') or {'x':start[0],'y':start[1]}
        unit.update(x=x,y=y,movement_origin=origin,movement_path=_movement_path(parents,costs,(x,y)),moved=(x,y)!=(origin['x'],origin['y']))
        _record_movement(battle,unit,start,[(x,y)])
        return
    if action=='operate_turret' and (not unit.get('stationary') or _distance(owner,unit)>1):raise ValueError('Stand beside an owned turret to operate it')
    target=battle['units'].get(command.get('target_id'))
    if not target or target not in _entity_targets(battle,unit) or not _can_attack(battle,unit,target,unit['attack_range']):raise ValueError('Choose a visible hostile target in deployment range and sight')
    if unit.get('acted') or unit.get('fired_at')==owner.get('ability_activation',0):raise ValueError('This deployment has already acted')
    power=unit['attack']
    if action=='operate_turret':
        power=min(power,max(0,entities.budget(owner)-owner.get('entity_budget_spent',0)))
        if power<1:raise ValueError('Automatic output budget is spent')
    _commit_player_movement(battle,owner);_commit_player_movement(battle,unit)
    if not _combat_active(owner) or not _combat_active(unit):return
    if action=='operate_turret':owner['entity_budget_spent']=owner.get('entity_budget_spent',0)+power
    _entity_attack(battle,owner,unit,target,power);owner['acted']=True


def _resolve_ability(battle, actor, target, skill):
    """Apply a snapshotted ordered ability through the existing combat primitives."""
    if not abilities.availability(actor,skill)['available']:
        raise ValueError(abilities.availability(actor,skill)['reason'])
    abilities.validate(skill)
    if actor.get('capture_weapon') and any(e['type']=='attack' for e in skill['effects']):
        raise ValueError('Capture weapons cannot perform damaging techniques')
    for effect in skill['effects']:
        if effect['type']=='deploy':
            if target['id']!=actor['id'] or not entities.available(battle,actor,effect['entity']):raise ValueError('Choose self with available deployment resources')
            _deployment_positions(battle,actor,effect['entity'])
        if effect['type']=='form' and (target['id']!=actor['id'] or actor.get('capture_weapon') or actor.get('carrying') or actor.get('carrying_object')):
            raise ValueError('Forms require self targeting without a payload or capture weapon')
        if effect['type']=='zone' and not _zone_cells(battle,target,effect):
            raise ValueError('No legal ground for this zone')
    _commit_player_movement(battle, actor)
    if not _combat_active(actor):return {'interrupted':True}
    def attack(effect):
        nonlocal target
        target,hit,damage,preview,roll=_perform_attack(battle,actor,target,skill['elevation_rule'],
            effect.get('damage_bonus',0),effect.get('armor_pierce',0),ability=skill,defer_reaction=True)
        battle['log'].append(f"{actor['name']} uses {skill['name']} on {target['name']} for {damage} damage." if hit else
                             f"{actor['name']} misses {target['name']} ({roll} vs {preview['chance']}% accuracy).")
        return {'hit':hit,'damage':damage,'target':target,'attacked':True}
    def heal(effect):
        amount=min(target['max_hp']-target['hp'],effect['amount'])
        target['hp']+=amount
        return {'healing':amount}
    def cleanse(effect):
        conditions.remove(target,*effect['statuses'])
        if not any(conditions.has(target,s) for s in ('stun','sleep','paralyze')):target.pop('forced_skip',None)
        if not conditions.has(target,'paralyze'):target.pop('paralyzed_move',None)
    def guard(effect):target['guarding']=True
    def barrier(effect):conditions.barrier(target,effect['amount'],effect['turns'],actor)
    def mark(effect):conditions.mark(battle,actor,target,effect['turns'],effect.get('accuracy',10))
    def displace(effect):_apply_displacement(battle,actor,target,effect)
    def zone(effect):spaces.place_zone(battle,actor,effect,_zone_cells(battle,target,effect))
    def form(effect):
        spaces.change_form(actor,effect)
        battle['log'].append(f"{actor['name']} returns to normal form." if effect['form']=='normal' else f"{actor['name']} takes {spaces.FORMS[effect['form']]['name']} form.")
    def deploy(effect):entities.deploy(battle,actor,effect['entity'],_deployment_positions(battle,actor,effect['entity']))
    def status(effect):
        sid=effect['status']
        if sid=='poison' and ('poison' in target.get('racial_resistances',[]) or target.get('race') in {'Undead','Revenant','Banshee','Golem','Automaton'}):return
        chance=effect.get('chance',100)
        if sid in target.get('racial_resistances',[]):chance//=2
        if sid in target.get('racial_weaknesses',[]):chance=min(95,chance+15)
        counter=battle.get('proc_counter',0);battle['proc_counter']=counter+1
        roll=random.Random(f"{battle.get('seed')}:ability-status:{counter}:{actor['id']}:{target['id']}").randint(1,100)
        if roll<=chance and conditions.apply(target,sid,effect['turns'],actor):
            battle['log'].append(f"{target['name']} suffers {sid}.")
    result=abilities.resolve(skill,target,{'attack':attack,'heal':heal,'cleanse':cleanse,'guard':guard,'status':status,
        'barrier':barrier,'mark':mark,'displace':displace,'zone':zone,'form':form,'deploy':deploy})
    abilities.spend(actor,skill)
    if result.get('attacked'):_react_after_attack(battle,actor,target,result['hit'],skill['elevation_rule'])
    if skill['target']=='ally':
        details=[f"{result.get('healing',0)} HP restored"] if result.get('healing') else []
        if skill.get('cleanses'):details.append('harmful effects treated')
        if any(e['type']=='barrier' for e in skill['effects']):details.append('Barrier applied')
        if any(e['type']=='guard' for e in skill['effects']):details.append('Guard granted')
        battle['log'].append(f"{actor['name']} uses {skill['name']} on {target['name']}"+(': '+', '.join(details) if details else '')+'.')
        _record_sound(battle,'magic_cast' if skill['elevation_rule']=='line_of_effect' else 'guard')
    actor['acted']=True
    return result


def _auto_support(battle, unit):
    for skill in unit.get('skills', []):
        if not abilities.availability(unit,skill)['available'] or skill.get('target') != 'ally' or (conditions.has(unit, 'mute') and skill['elevation_rule'] == 'line_of_effect'):
            continue
        effect = _support_effect(skill, unit)
        targets = [u for u in _living(battle, unit['team']) if _support_eligible(battle, unit, u, effect)
                   and (u['hp'] <= u['max_hp'] * .65 or any(s['id'] in effect.get('cleanses', []) for s in u['statuses'])
                        or (effect.get('barrier') and any(_distance(u,e)<=4 for e in _living(battle,'enemy'))))]
        if targets:
            target = min(targets, key=lambda u: u['hp'] / u['max_hp'])
            if skill.get('ability_version'):_resolve_ability(battle,unit,target,skill)
            else:
                _apply_support(battle, unit, target, effect)
                abilities.spend(unit,skill)
            _finish_turn(battle)
            return True
    return False


def _player_auto_turn(battle: dict, unit: dict, tactic: str) -> None:
    if not unit.get('forced_skip') and _pit_exits(battle,unit):
        _climb_out(battle,unit,_pit_exits(battle,unit)[0]);_finish_turn(battle);return
    enemies = _visible_enemies(battle)
    if enemies and _auto_open_gate(battle, unit, min(enemies, key=lambda u: _distance(unit, u))):
        return
    if battle.get('ambush_sleep_until_round'):
        target = next((u for u in _visible_enemies(battle) if u.get('boss') or u.get('kind') == 'chieftain'), None)
        if target:
            # Reach an open firing/assault position rather than waking the camp from the entry.
            destinations = [{'x': x, 'y': y} for x in range(battle['width']) for y in range(battle['height'])
                            if not _blocked(battle, x, y, unit['id'], unit.get('movement_type'))
                            and abs(x-target['x']) + abs(y-target['y']) <= (2 if unit['attack_range'] > 1 else 1)
                            and _line_of_sight(battle, {**unit, 'x': x, 'y': y}, target)]
            _move_to_nearest_tile(battle, unit, destinations)
        _guard(battle, unit)
        _finish_turn(battle)
        return
    if _auto_support(battle, unit):
        return
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
    targets = _visible_enemies(battle)
    if not targets:
        _search_brush(battle, unit)
        return
    if tactic == "objective" and world_has_active_objects:
        non_chiefs = [candidate for candidate in targets if candidate.get("kind") != "chieftain"]
        if non_chiefs:
            targets = non_chiefs
        else:
            _guard(battle,unit); unit["acted"] = True
            _record_sound(battle, "guard")
            chief_name = battle.get("units", {}).get("gob_chief", {}).get("name", "the goblin chieftain")
            battle["log"].append(f"{unit['name']} holds back from {chief_name} while the other objectives remain unfinished.")
            _finish_turn(battle)
            return
    available_skills=[s for s in (unit.get('skills') or ([unit['special']] if unit.get('special') else []))
                      if abilities.availability(unit,s)['available'] and s.get('target') != 'ally' and not (conditions.has(unit, 'mute') and s['elevation_rule'] in {'ignore', 'line_of_effect'})]
    if conditions.has(unit, 'mute') and unit['attack_elevation_rule'] in {'ignore','line_of_effect'} and not available_skills:
        _guard(battle, unit)
        unit['acted'] = True
        _finish_turn(battle)
        return
    if unit.get('capture_weapon'): available_skills = []  # Auto preserves the live-capture role.
    auto_range = max([unit['attack_range']]+[s['range'] for s in available_skills])
    in_range = [candidate for candidate in targets if _can_attack(battle, unit, candidate, auto_range)]
    target_priority = lambda candidate: (
        0 if unit.get("independent_style")=="duelist" or (tactic == "objective" and candidate.get("capture_role") == "live_target") else 1,
        0 if unit.get("independent_style")=="duelist" or candidate.get("kind") == "chieftain" else 1,
        -candidate["max_hp"] if unit.get("independent_style")=="duelist" else candidate["hp"],
    )
    target = (
        min(in_range, key=target_priority)
        if in_range else
        min(targets, key=lambda candidate: (target_priority(candidate), _distance(unit, candidate)))
    )
    capturing=tactic=='objective' and target.get('capture_role')=='live_target'
    if capturing:
        safe_ranges=([unit['attack_range']] if unit.get('nonlethal_capable') else [])+[s['range'] for s in available_skills if s.get('nonlethal')]
        if not safe_ranges:
            _guard(battle,unit);unit['acted']=True
            battle['log'].append(f"{unit['name']} holds fire rather than killing the capture target.")
            _finish_turn(battle)
            return
        auto_range=max(safe_ranges)
    if not _can_attack(battle, unit, target, auto_range) and not pursuing_objective:
        _move_toward(battle, unit, target)
    if _can_attack(battle, unit, target, auto_range):
        if unit.get('capture_weapon'):
            _capture_attempt(battle, unit, target)
        else:
            nonlethal = tactic == "objective" and target.get("capture_role") == "live_target" and unit.get("nonlethal_capable") and _can_attack(battle,unit,target,1)
            choices=[s for s in available_skills if _can_attack(battle,unit,target,s['range']) and (not capturing or s.get('nonlethal'))]
            special=max(choices,key=lambda s:(s.get('armor_pierce',0)+s.get('damage_bonus',0),s.get('attack',unit['attack']))) if choices and not nonlethal else None
            if special:unit['special']=special
            use_skill = bool(special and abilities.availability(unit,special)['available'] and _can_attack(battle, unit, target, special["range"]))
            if not use_skill and not _can_attack(battle, unit, target, 1 if nonlethal else unit["attack_range"]):
                unit["acted"] = True
                _finish_turn(battle)
                return
            bonus = int(special.get("damage_bonus", 2)) if use_skill else 0
            rule = special["elevation_rule"] if use_skill else unit["attack_elevation_rule"]
            skill_nonlethal = use_skill and special.get("nonlethal", False)
            target = conditions.confused_target(battle, unit, target, lambda u: _can_attack(battle, unit, u, special['range'] if use_skill else unit['attack_range']))
            if use_skill and special.get('ability_version'):
                _resolve_ability(battle,unit,target,special)
                _finish_turn(battle)
                return
            target,hit,damage,preview,roll=_perform_attack(battle,unit,target,rule,
                bonus-(1 if nonlethal else 0),
                int(special.get("armor_pierce",2 if special["id"]=="precision_shot" else 0)) if use_skill else 0,
                "nonlethal" if nonlethal or skill_nonlethal else "lethal",ability=special if use_skill else None)
            if use_skill:
                unit["special_used"] = True
            attack_name = "a nonlethal takedown" if nonlethal else special["name"] if use_skill else unit["weapon"]
            battle["log"].append(f"{unit['name']} uses {attack_name} on {target['name']} for {damage} damage." if hit else f"{unit['name']} misses {target['name']} ({roll} vs {preview['chance']}% accuracy).")
    elif tactic == "defensive":
        _guard(battle,unit)
        _record_sound(battle, "guard")
        battle["log"].append(f"{unit['name']} takes a guarded stance.")
    unit["acted"] = True
    _finish_turn(battle)


def _auto_open_gate(battle, unit, target):
    if _can_attack(battle,unit,target):return False
    if not any(t.get('kind')=='gate' and not t.get('destroyed') and t.get('state')!='opened'
               and can_operate_gate(unit,t) for t in battle.get('terrain',[])):
        return False
    path,_,gates=_route_with_gates(battle,unit,_pursuit_goals(battle,unit,target))
    if path and path[0] in gates:
        _interact(battle,unit,gates[path[0]]['id'])
        return True
    return False


def _interact(battle: dict, unit: dict, object_id: str) -> None:
    gate = next((t for t in battle.get('terrain', []) if t.get('id') == object_id and t.get('kind') == 'gate' and not t.get('destroyed')), None)
    if gate:
        if not can_operate_gate(unit, gate):
            raise ValueError('Move next to the gate before operating it')
        closing = gate.get('state') == 'opened'
        if closing and not gate.get('edge_wall') and any(u.get('conscious', True) and not u.get('extracted') and not u.get('carried_by')
                           and (u['x'], u['y']) in occupied_tiles(gate) for u in battle['units'].values()):
            raise ValueError('Someone is standing in the gate')
        gate.update(state='closed' if closing else 'opened', blocking=closing, blocks_sight=closing,
                    sprite=gate['closed_sprite'] if closing else gate['open_sprite'])
        battle['log'].append(f"{unit['name']} {'closes' if closing else 'opens'} {gate['name']}.")
        _record_sound(battle, 'cage_open')
        unit['acted'] = True
        _finish_turn(battle)
        return
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
        battle["log"].append(f"{unit['name']} disables the alarm bell before another signal can be sent.")
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
    if not target or target.get("extracted") or target.get("carried_by") or target.get('lost_in_pit') or target.get('temporary'):
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
    throw_range = max(1, min(5, 1 + strength // 4 - max(0, weight - 2)+unit.get('gear_rules',{}).get('throw_range',0)))
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
    damage = max(1, int(unit.get("attack", 1)) - int(tile.get("armor", 0))+unit.get('gear_rules',{}).get('breach_damage',0))
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
        for entity in entities.owned(battle,unit):
            if not entities.can_command(battle,unit,entity):continue
            actions.append({'id':f"dismiss:{entity['id']}",'label':f"Dismiss {entity['name']}",'target':entity['name'],
                'description':'Remove this deployment. Releases capacity, but never refunds Components or refreshes an ability.',
                'cost':'Main action','command':{'action':'dismiss_summon','entity_id':entity['id']}})
            magical_block=entity['resource_pool']=='capacity' and conditions.has(unit,'mute')
            if magical_block:continue
            if entity['policy']=='commanded':
                costs,_=_movement_tree(battle,entity)
                for dx,dy in ((0,-1),(1,0),(0,1),(-1,0)):
                    x,y=entity['x']+dx,entity['y']+dy
                    if (x,y) in costs:actions.append({'id':f"entity_move:{entity['id']}:{x}:{y}",
                        'label':f"Move {entity['name']} to {x+1}, {y+1}",'target':entity['name'],
                        'description':'Reposition within its own movement budget. Does not grant an extra attack.',
                        'cost':'Deployment movement','command':{'action':'summon_move','entity_id':entity['id'],'x':x,'y':y}})
            operating=entity.get('stationary') and _distance(unit,entity)<=1
            if entity['policy']=='commanded' or operating:
                for target in _entity_targets(battle,entity):
                    if not _can_attack(battle,entity,target,entity['attack_range']):continue
                    action='operate_turret' if operating else 'summon_attack'
                    actions.append({'id':f"entity_attack:{entity['id']}:{target['id']}",
                        'label':f"{entity['name']}: attack {target['name']}",'target':target['name'],
                        'description':'Uses your main action. Operating a turret replaces its automatic firing opportunity.',
                        'cost':'Owner main action','command':{'action':action,'entity_id':entity['id'],'target_id':target['id']}})
        for x,y in _pit_exits(battle,unit):
            actions.append({'id':f'climb:{x}:{y}','label':f'Climb Out ({x+1}, {y+1})','target':'Safe ground',
                'description':'Climb into this adjacent safe cell. Uses the main action.','cost':'Main action',
                'command':{'action':'climb_out','x':x,'y':y}})
        for gate in battle.get('terrain', []):
            if gate.get('kind') != 'gate' or gate.get('destroyed') or not can_operate_gate(unit, gate):
                continue
            verb = 'Close' if gate.get('state') == 'opened' else 'Open'
            actions.append({'id': f"gate:{gate['id']}", 'label': f"{verb} {gate['name']}", 'target': gate['name'],
                            'description': f'{verb} the passage. Uses the main action and ends this activation. Gates can also be attacked.',
                            'cost': 'Main action', 'hotkey': 'I', 'command': {'action':'interact','target_id':gate['id']}})
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
                    "id": "disable_alarm_horn", "label": "Disable Alarm Bell", "target": obj["name"],
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
            if target.get("carried_by") or target.get("extracted") or target.get('lost_in_pit') or _distance(unit, target) > 1:
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
    # First sightings are persistent. Presentation must not start an activation,
    # but must keep a revealed enemy visible after it returns to cover.
    concealment.refresh(battle)
    view = deepcopy(battle)
    _ensure_battle_schema(view)
    view['zones']=spaces.presentation(view)
    for unit in view['units'].values():
        if unit.get('form'):
            rule=spaces.FORMS[unit['form']['id']]
            unit['statuses'].append({'id':'wild_form','name':rule['name'],'description':rule['description'],
                'turns':max(0,unit['form']['expires_at']-unit.get('ability_activation',0))})
    hidden = {uid for uid, unit in view['units'].items() if concealment.unseen(unit)}
    hidden_names = [view['units'][uid]['name'] for uid in hidden]
    view['log'] = [line for line in view.get('log', []) if not any(name in line for name in hidden_names)]
    view['units'] = {uid:unit for uid,unit in view['units'].items() if uid not in hidden}
    view['entity_rules']='Deployments have no extra initiative turn. Commands spend the owner action; automatic entities share output. Newly deployed entities act from the next owner activation.'
    view['zones']=[z for z in view['zones'] if z['owner_id'] not in hidden]
    if 'spawn_zones' in view:
        view['spawn_zones'].pop('enemy', None)
    # Filter initiative without advancing a hidden enemy activation in the view copy.
    current_id = view['turn_order'][view['turn_index'] % len(view['turn_order'])] if view['turn_order'] else None
    view['turn_order'] = [uid for uid in view['turn_order'] if uid not in hidden]
    view['turn_index'] = view['turn_order'].index(current_id) if current_id in view['turn_order'] else 0
    view['animation_events'] = [event for event in view.get('animation_events', [])
                                if event.get('unit_id') not in hidden and event.get('target_id') not in hidden
                                and not event.get('concealed')]
    view['concealment_help'] = concealment.HELP if concealment.cover_cells(view) else None
    view.pop('searched_bushes', None)
    view.pop('ambush_enemy_indices', None)
    view.pop('ambush_lane', None)
    view['concealment_warning'] = ('The fight is not over. Check the brush or end your turn to let the enemy act.'
                                   if hidden and not _visible_enemies(battle) and battle.get('status') == 'active'
                                   else None)
    from .portrait_framing import resolve_frame
    from .portraits import version_pool_url
    for unit in view.get('units',{}).values():
        for field in ('portrait','portrait_full','portrait_thumbnail'):
            if unit.get(field):unit[field] = version_pool_url(unit[field])
        unit['portrait_frame'] = resolve_frame(unit)
    # Keep the existing object ID and alarm rules compatible with saved battles.
    if 'alarm_horn' in view.get('objects', {}):
        view['objects']['alarm_horn']['name'] = 'Alarm Bell'
    for objective in view.get('objectives', []):
        if objective.get('id') == 'alarm':
            objective['name'] = 'Disable the alarm bell'
    current = _current_unit(view, activate=False)
    if current and (entities.owned(view,current) or any(e['type']=='deploy' for s in current.get('skills',[]) for e in s.get('effects',[]))):
        view['deployment_resources']={'components':current.get('components',3),'capacity_used':entities.usage(view,current),
            'capacity':current.get('summon_capacity',2),'automatic_budget':entities.budget(current),
            'automatic_spent':current.get('entity_budget_spent',0)}
    for unit in view['units'].values():
        if unit.get('temporary'):
            owner=view['units'].get(unit['owner_id'],{})
            unit['statuses'].append({'id':'deployment','owner_name':owner.get('name','Owner'),
                'policy':unit['policy'],'ready':unit['deployed_at']<owner.get('ability_activation',0),
                'stationary':unit.get('stationary',False)})
        for choice in unit.get('skills',[]):
            choice['availability']=abilities.availability(unit,choice)
        if unit.get('special'):
            unit['special']['availability']=abilities.availability(unit,unit['special'])
    for unit in view["units"].values():
        resistance=tactics.displacement_resistance(unit)
        if resistance:unit['statuses'].append({'id':'footing','resistance':resistance})
        if unit.get('reactions'):
            unit['statuses'].append({'id':'reaction','ready':bool(tactics.reaction_available(unit)),
                'reactions':[r['name'] for r in unit['reactions']]})
        for status in unit.get("statuses", []):
            if status.get("id") == "ambush_sleep":
                status["rounds"] = max(0, int(view.get("ambush_sleep_until_round", view["round"])) - view["round"])
    view["current_unit_id"] = current["id"] if current else None
    view['supply_uses_remaining'] = remaining_uses(view)
    view['supply_targets'] = [u['id'] for u in _living(view, 'player') if current
                             and _distance(current, u) <= 1 and _line_of_sight(view, current, u)]
    if current and current["team"] == "player":
        reachable, parents = _movement_tree(view, current)
        view["reachable"] = [
            {"x": x, "y": y} for x, y in reachable
        ]
        # One parent per reachable tile, rather than a full path for every tile.
        # The client can preview only server-validated routes immediately.
        view["movement_tree"] = [
            {"x": x, "y": y, "cost": reachable[(x, y)],
             "parent": list(parent) if parent is not None else None}
            for (x, y), parent in parents.items()
        ]
        origin = current.get("movement_origin") or {"x": current["x"], "y": current["y"]}
        view["movement_origin"] = {"x": int(origin["x"]), "y": int(origin["y"])}
        view["movement_path"] = list(current.get("movement_path", []))
        extraction_tiles = _player_exit_tiles(view)
        view["can_extract"] = (current["x"], current["y"]) in extraction_tiles and bool(current.get("exit_ready"))
        view["can_extract_body"] = view["can_extract"] and bool(current.get("carrying"))
        view["can_subdue"] = bool(current.get("capture_weapon"))
        view["can_drop"] = bool(current.get("carrying") or current.get("carrying_object"))
        view["context_actions"] = _context_actions(view, current)
        view["carry_targets"] = [
            target["id"] for target in view["units"].values()
            if not target.get("conscious", True) and target.get("condition") in {"unconscious", "dead"}
            and not target.get('lost_in_pit')
            and not target.get("carried_by") and not target.get("extracted") and _distance(current, target) == 1
        ]
        view["attack_previews"] = {}
        skill = current.get('special')
        options = {
            'attack': (current['attack_range'], current['attack_elevation_rule'], not current.get('capture_weapon') and not current.get('acted') and not (conditions.has(current, 'mute') and current['attack_elevation_rule'] in {'ignore','line_of_effect'})),
            'subdue': (current['attack_range'], current['attack_elevation_rule'], not current.get('acted') and current.get('capture_weapon') and not (conditions.has(current,'mute') and current['attack_elevation_rule']=='line_of_effect')),
            'skill': (skill['range'], skill['elevation_rule'], skill.get('target') != 'ally' and abilities.availability(current,skill)['available'] and not (conditions.has(current, 'mute') and skill['elevation_rule'] in {'ignore', 'line_of_effect'})) if skill else (0, 'melee', False),
        }
        for target in _living(view, 'enemy'):
            previews = {}
            for action, (reach, rule, available) in options.items():
                actor, approach = _attack_position(view, current, target, reach, reachable, parents) if available else (None, None)
                previews[action] = {**(_capture_preview(view, actor, target) if current.get('capture_weapon') and action in {'attack','subdue'} else _strike_preview(view, actor, target, rule,reach,skill if action=='skill' else None)), **(approach or {})} if actor else None
            view['attack_previews'][target['id']] = previews
        view['skill_previews']={}
        for choice in current.get('skills',[]):
            entries={}
            if choice.get('target') == 'ally':
                for target in _living(view, 'player'):
                    view['attack_previews'].setdefault(target['id'], {})
                    allowed = abilities.availability(current,choice)['available'] and not (conditions.has(current, 'mute') and choice['elevation_rule'] == 'line_of_effect')
                    effect = _support_effect(choice, current)
                    entries[target['id']] = {'chance': 100, 'support': True, 'heal': effect.get('heal', 0)} if allowed and _support_eligible(view, current, target, effect) else None
                    if choice['id'] == (skill or {}).get('id'):
                        view['attack_previews'][target['id']]['skill'] = entries[target['id']]
                view['skill_previews'][choice['id']] = entries
                continue
            for target in _living(view,'enemy'):
                allowed = abilities.availability(current,choice)['available'] and not (conditions.has(current, 'mute') and choice['elevation_rule'] in {'ignore', 'line_of_effect'})
                actor,approach=_attack_position(view,current,target,choice['range'],reachable,parents) if allowed else (None,None)
                entries[target['id']]={**_strike_preview(view,actor,target,choice['elevation_rule'],choice['range'],choice),**(approach or {})} if actor else None
            view['skill_previews'][choice['id']]=entries
        view['terrain_attack_previews'] = {}
        for tile in view.get('terrain', []):
            if current.get('capture_weapon') or not tile.get('destructible') or tile.get('destroyed') or current.get('acted') or (conditions.has(current, 'mute') and current['attack_elevation_rule'] == 'ignore'):
                continue
            actor, approach = _attack_position(view, current, tile, current['attack_range'], reachable, parents)
            if actor:
                view['terrain_attack_previews'][tile['id']] = approach or {}
        view['terrain_targets'] = list(view['terrain_attack_previews'])
        throw_profile = _throw_profile(view, current)
        if throw_profile:
            throw_profile["target_ids"] = [
                target["id"] for target in _living(view, "enemy")
                if not current.get("acted") and _can_attack(view, current, target, throw_profile["range"])
            ]
        view["throw_profile"] = throw_profile
    else:
        view["reachable"] = []
        view["movement_tree"] = []
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
        view["terrain_attack_previews"] = {}
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
            "prepared_trap": True, "trap_damage": 4, "destroyed_sprite": "spike_trap_spent", "destroyed_movement_cost": 1,
        },
        "snare_trap": {
            "name": "Iron-Jaw Snare", "kind": "prepared_trap", "sprite": "iron_jaw_trap", "blocking": False,
            "prepared_trap": True, "trap_damage": 2, "trap_effect": "snare", "destroyed_sprite": "iron_jaw_trap_spent", "destroyed_movement_cost": 1,
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
    _ensure_battle_schema(battle)
    concealment.refresh(battle)
    battle["animation_events"] = []
    if battle.get("status") == "preparing":
        return _apply_preparation_command(battle, command)
    if battle.get("status") != "active":
        raise ValueError("This battle is already complete")
    action = command.get("action")
    battle.pop('auto_pause_reason',None)
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
    if unit.get('forced_skip'):
        raise ValueError('This unit cannot act during this activation')
    if independence_check(battle,unit):
        _independent_turn(battle,unit)
        _advance_to_player(battle)
        battle["action_count"]+=1
        return battle_view(battle)
    selected_skill=next((s for s in unit.get('skills',[]) if s['id']==command.get('skill_id',(unit.get('special') or {}).get('id'))),None) if action=='skill' else None
    if action in {'summon_move','summon_attack','operate_turret','dismiss_summon'}:
        _entity_command(battle,unit,command)
    elif selected_skill and selected_skill.get('ability_version'):
        abilities.validate(selected_skill)
        availability=abilities.availability(unit,selected_skill)
        if not availability['available']:raise ValueError(availability['reason'])
        rule=selected_skill['elevation_rule']
        if conditions.has(unit,'mute') and rule in {'ignore','line_of_effect'}:
            raise ValueError('Mute prevents this spell')
        target=battle['units'].get(command.get('target_id'))
        if selected_skill['target']=='ally':
            if not _support_eligible(battle,unit,target,_support_effect(selected_skill,unit)):
                raise ValueError('Choose a conscious ally in range who needs this technique')
        else:
            if not target or not _combat_active(target) or target['team']!='enemy' or concealment.unseen(target):
                raise ValueError('Choose a visible living enemy')
            if unit.get('capture_weapon') and any(e['type']=='attack' for e in selected_skill['effects']):
                raise ValueError('Capture weapons cannot perform damaging techniques')
            if _apply_attack_approach(battle,unit,target,selected_skill['range'],command):return battle_view(battle)
            if not _can_attack(battle,unit,target,selected_skill['range']):raise ValueError('Target is outside technique range')
            target=conditions.confused_target(battle,unit,target,lambda u:_can_attack(battle,unit,u,selected_skill['range']))
        unit['special']=selected_skill
        _resolve_ability(battle,unit,target,selected_skill)
    elif action == "move":
        if unit.get("acted"):
            raise ValueError("This unit already committed its action")
        x, y = int(command.get("x", -1)), int(command.get("y", -1))
        if not unit.get("movement_origin"):
            unit["movement_origin"] = {"x": unit["x"], "y": unit["y"]}
        reachable, parents = _movement_tree(battle, unit)
        if (x, y) not in reachable:
            raise ValueError("That tile is outside this unit's movement range")
        path = _movement_path(parents, reachable, (x, y))
        route = _scout_path(battle, unit, [(p['x'],p['y']) for p in path])
        if route:
            x, y = route[-1]
        else:
            x, y = unit['x'], unit['y']
        origin = unit["movement_origin"]
        if (x, y) != (unit["x"], unit["y"]):
            unit["exit_ready"] = False
        unit["x"], unit["y"] = x, y
        if unit.get("carrying") in battle["units"]:
            carried = battle["units"][unit["carrying"]]
            carried["x"], carried["y"] = x, y
        unit["moved"] = (x, y) != (int(origin["x"]), int(origin["y"]))
        unit["movement_path"] = _movement_path(parents, reachable, (x, y))
    elif action == 'use_item':
        if unit.get('acted') or remaining_uses(battle) < 1:
            raise ValueError('No supply action is available this battle')
        supply = next((s for s in battle.get('supplies', []) if s['instance_id'] == command.get('item_id')), None)
        if not supply:
            raise ValueError('This supply is no longer available')
        _apply_support(battle, unit, battle['units'].get(command.get('target_id')), {**supply, 'range': 1})
        battle['supplies_used'].append(supply['instance_id'])
        battle['supplies'].remove(supply)
    elif action == 'skill' and next((s for s in unit.get('skills', []) if s['id'] == command.get('skill_id', (unit.get('special') or {}).get('id'))), {}).get('target') == 'ally':
        if unit.get('acted') or unit.get('special_used'):
            raise ValueError('This unit has already used its action or technique')
        skill = next(s for s in unit['skills'] if s['id'] == command.get('skill_id', (unit.get('special') or {}).get('id')))
        if conditions.has(unit, 'mute') and skill['elevation_rule'] == 'line_of_effect':
            raise ValueError('Mute prevents this spell')
        _apply_support(battle, unit, battle['units'].get(command.get('target_id')), _support_effect(skill, unit))
        unit['special'] = skill
        unit['special_used'] = True
    elif action in {"attack", "skill", "subdue"}:
        if unit.get("acted"):
            raise ValueError("This unit already used its action")
        if action=='skill' and command.get('skill_id'):
            choice=next((s for s in unit.get('skills',[]) if s['id']==command['skill_id']),None)
            if not choice:raise ValueError('That skill is not granted by the equipped gear')
            unit['special']=choice
        target_id = str(command.get("target_id", ""))
        terrain_target = next((
            tile for tile in battle.get("terrain", [])
            if tile.get("id") == target_id and tile.get("destructible") and not tile.get("destroyed")
        ), None)
        if terrain_target:
            if unit.get("capture_weapon"):
                raise ValueError("Capture weapons cannot damage structures")
            if action != "attack":
                raise ValueError("Only a standard attack can target this terrain")
            if conditions.has(unit, 'mute') and unit['attack_elevation_rule'] == 'ignore':
                raise ValueError('Mute prevents this spell')
            if _apply_attack_approach(battle, unit, terrain_target, unit["attack_range"], command):
                return battle_view(battle)
            if not _can_attack(battle, unit, terrain_target):
                raise ValueError("Terrain target is outside attack range")
            _commit_player_movement(battle, unit)
            _damage_terrain(battle, unit, target_id)
            unit["acted"] = True
        else:
            target = battle["units"].get(target_id)
            if not target or not _combat_active(target) or target["team"] != "enemy" or concealment.unseen(target):
                raise ValueError("Choose a living enemy or destructible terrain target")
            if action == "attack" and unit.get("capture_weapon"):
                raise ValueError("Capture weapons can only use Subdue instead of Attack")
            if action == "subdue" and not unit.get("capture_weapon"):
                raise ValueError("Equip a capture weapon to attempt Subdue")
            if action == "skill" and not unit.get("special"):
                raise ValueError("This unit has no equipped combat skill")
            attack_range = int(unit["special"]["range"] if action == "skill" else unit["attack_range"])
            if action == "skill" and unit.get("special_used"):
                raise ValueError("This unit's special skill has already been used")
            if _apply_attack_approach(battle, unit, target, attack_range, command):
                return battle_view(battle)
            if not _can_attack(battle, unit, target, attack_range):
                raise ValueError("Target is outside attack range")
            _commit_player_movement(battle, unit)
            rule = unit["special"]["elevation_rule"] if action == "skill" else unit["attack_elevation_rule"]
            if conditions.has(unit, 'mute') and rule in {'ignore', 'line_of_effect'}:
                raise ValueError('Mute prevents this spell')
            target = conditions.confused_target(battle, unit, target, lambda u: _can_attack(battle, unit, u, attack_range))
            if unit.get('capture_weapon') and action != 'skill':
                _capture_attempt(battle, unit, target)
            else:
                bonus = int(unit["special"].get("damage_bonus", 3)) if action == "skill" else -1 if action == "subdue" else 0
                pierce = int(unit["special"].get("armor_pierce", 2 if unit["special"]["id"] == "precision_shot" else 0)) if action == "skill" else 0
                nonlethal = action == "subdue" or (action == "skill" and unit["special"].get("nonlethal", False))
                target,hit,damage,preview,roll=_perform_attack(battle,unit,target,rule,bonus,pierce,
                    "nonlethal" if nonlethal else "lethal",ability=unit["special"] if action=="skill" else None)
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
    elif action == "climb_out":
        _climb_out(battle,unit,(int(command.get('x',-1)),int(command.get('y',-1))))
    elif action == "guard":
        if unit.get("acted"):
            raise ValueError("This unit already used its action")
        _commit_player_movement(battle, unit)
        _guard(battle,unit); unit["acted"] = True
        _record_sound(battle, "guard")
        battle["log"].append(f"{unit['name']} guards against the next attack.")
    elif action == "interact":
        if unit.get("acted"):
            raise ValueError("This unit already used its action")
        object_id = str(command.get("target_id", ""))
        obj = battle["objects"].get(object_id) or next((t for t in battle.get('terrain', []) if t.get('id') == object_id and t.get('kind') == 'gate'), None)
        if not obj or (not can_operate_gate(unit, obj) if obj.get('kind') == 'gate' else _distance_to_entity(unit, obj) != 1):
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
    if action == "end_turn" or action in {"attack", "skill", "subdue", "drop", "drop_object", "throw", "guard", "use_item", "climb_out",'summon_attack','operate_turret','dismiss_summon'}:
        _finish_turn(battle)
    concealment.refresh(battle)
    _check_end(battle)
    _advance_to_player(battle)
    if action != "move":
        battle["action_count"] += 1
    return battle_view(battle)


def auto_step(battle: dict, tactic: str = "balanced") -> dict:
    battle.pop('auto_pause_reason',None)
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
        if any(u.get('ability_version') for u in battle['units'].values()):
            battle['auto_pause_reason']='Auto-battle paused after its step limit. Continue manually or run auto-battle again.'
        else:
            battle["status"] = "complete"; battle["outcome"] = "failure"
            battle["log"].append("The battle exceeded its action limit and the party withdrew.")
    return battle_view(battle)
