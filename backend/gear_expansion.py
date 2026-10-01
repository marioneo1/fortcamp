"""Equipment with tactical identities, ordinary caches, and chain-only discoveries."""
from copy import deepcopy


def skill(name, reach, rule, pierce=0, bonus=1, nonlethal=False):
    return {"id": name.lower().replace(" ", "_"), "name": name, "range": reach,
            "elevation_rule": rule, "armor_pierce": pierce, "damage_bonus": bonus,
            "scaling": "int" if rule == "ignore" else "dex" if rule == "ballistic" else "str",
            "nonlethal": nonlethal,
            "description": f"Once per battle. Range {reach}; ignores {pierce} armor; damage {bonus:+d}."
            + (" Knocks out instead of killing." if nonlethal else "")}


def weapon(name, rarity, kind, power, description, **extra):
    scaling = "dex" if kind in {"bow", "crossbow"} else "int" if kind in {"staff", "wand", "grimoire"} else "str"
    return {"name": name, "slot": "weapon", "rarity": rarity, "weapon_type": kind,
            "weapon_scaling": scaling, "power": power, "bonuses": {}, "attribute_bonuses": {},
            "granted_perks": [], "tags": [], "description": description, **extra}


NEW_GEAR = {
    "watchmans_cudgel": weapon("Watchman's Cudgel", "common", "club", 1, "A plain arrest weapon. Supports ordinary nonlethal takedowns."),
    "apprentice_wand": weapon("Apprentice Wand", "common", "wand", 1, "A reliable first spell focus. Its attacks use INT and ignore elevation."),
    "hooked_spear": weapon("Hooked Spear", "uncommon", "spear", 2, "Trades some damage for a once-per-battle armor-piercing thrust.", combat_skill=skill("Hook Thrust", 1, "melee", 3, 0)),
    "weighted_sling": weapon("Weighted Sling", "uncommon", "bow", 1, "A short-range capture tool, rather than a longbow replacement.", attack_range=3, combat_skill=skill("Dazing Stone", 3, "ballistic", 0, -2, True)),
    "coalbrand_sabre": weapon("Coalbrand Sabre", "rare", "sword", 3, "Fire-enchanted steel. Successful lethal hits have a 25% chance to burn for two turns.", element="fire", on_hit={"id": "burn", "chance": 25, "turns": 2}),
    "venomthorn_bow": weapon("Venomthorn Bow", "rare", "bow", 2, "Lower direct damage; 30% chance to poison a living target for two turns.", on_hit={"id": "poison", "chance": 30, "turns": 2}),
    "stormglass_rod": weapon("Stormglass Rod", "epic", "wand", 3, "Lightning focus. Its long-range spell ignores elevation and pierces armor.", element="lightning", combat_skill=skill("Storm Lance", 5, "ignore", 3, 1)),
    "mercykeepers_maul": weapon("Mercykeeper's Maul", "legendary", "hammer", 4, "A powerful capture weapon; its finishing skill leaves the target alive.", combat_skill=skill("Mercy Strike", 1, "melee", 3, 2, True)),
    "goblin_notched_axe": weapon("Goblin Notched Axe", "common", "axe", 1, "A light, brutally practical raider's axe."),
    "goblin_net_bow": weapon("Goblin Net Bow", "uncommon", "crossbow", 1, "A close-range raiding weapon with a nonlethal capture shot.", attack_range=3, combat_skill=skill("Net Shot", 3, "ballistic", 0, -2, True)),
    "smokecaller_staff": weapon("Smokecaller Staff", "rare", "staff", 2, "Fire magic from the Warhost's camp braziers; 25% burn chance.", element="fire", on_hit={"id": "burn", "chance": 25, "turns": 2}),
    "gravekeepers_spade": weapon("Gravekeeper's Spade", "common", "axe", 1, "An ordinary burial tool pressed into service against the procession."),
    "mourning_censer": weapon("Mourning Censer", "uncommon", "mace", 1, "A blunt warding weapon. Its wielder deals extra damage to Deathless.", granted_perks=["exorcist"]),
    "pale_watch_lance": weapon("Pale Watch Lance", "rare", "spear", 3, "Holy-enchanted steel, with an armor-piercing thrust.", element="holy", combat_skill=skill("Vigil Thrust", 1, "melee", 2, 1)),
    "cracked_ley_wand": weapon("Cracked Ley Wand", "common", "wand", 1, "A damaged but usable arcane focus found around unstable ley lines."),
    "prism_tuning_fork": weapon("Prism Tuning Fork", "uncommon", "wand", 1, "A short-range lightning focus with one distant discharge.", element="lightning", attack_range=2, combat_skill=skill("Prism Discharge", 4, "ignore", 1, 1)),
    "winterglass_grimoire": weapon("Winterglass Grimoire", "rare", "grimoire", 2, "Ice-enchanted spells. The focused spell ignores elevation rather than borrowing bow rules.", element="ice", combat_skill=skill("Winter Ray", 4, "ignore", 2, 0)),
    "antler_hatchet": weapon("Antler Hatchet", "common", "axe", 1, "A scout's bone-handled tool recovered along the migration route."),
    "hunters_bola": weapon("Hunter's Bola", "uncommon", "bow", 1, "A short-range hunt weapon with a nonlethal finishing throw.", attack_range=2, combat_skill=skill("Bola Takedown", 3, "ballistic", 0, -1, True)),
    "razorvine_spear": weapon("Razorvine Spear", "rare", "spear", 3, "A barbed spear coated in plant venom; 25% chance to poison living targets.", on_hit={"id": "poison", "chance": 25, "turns": 2}),
    "meteor_iron_knife": weapon("Meteor-Iron Knife", "common", "dagger", 1, "Small impact fragments forged into an ordinary usable blade."),
    "skyfall_focus": weapon("Skyfall Focus", "uncommon", "wand", 1, "An alien energy focus. Its short normal range is balanced by a distant spell.", element="void", attack_range=2, combat_skill=skill("Distant Echo", 4, "ignore", 1, 0)),
    "voidglass_crossbow": weapon("Voidglass Crossbow", "rare", "crossbow", 2, "Alien-enchanted bolts still follow ballistic elevation rules.", element="void", combat_skill=skill("Glasspiercer", 5, "ballistic", 3, 0)),
    "empty_crowns_verdict": weapon("Empty Crown's Verdict", "mythic", "sword", 4, "The Empty Court's execution blade. Its verdict pierces heavy armor; wielding it also grants Guard.", tags=["mission_exclusive", "chain_relic"], granted_perks=["guard"], combat_skill=skill("Royal Verdict", 1, "melee", 5, 2)),
    "processional_last_light": weapon("Processional Last Light", "mythic", "staff", 3, "A holy focus found only at the end of the buried bell's procession. Grants Exorcist and a distant ward-breaking spell.", tags=["mission_exclusive", "chain_relic"], element="holy", granted_perks=["exorcist"], combat_skill=skill("Last Light", 5, "ignore", 4, 1)),
    "meridian_arc_driver": weapon("Meridian Arc Driver", "mythic", "crossbow", 3, "The engine's aiming assembly converted into a weapon. Its charged bolt follows ballistic rules and pierces armor.", tags=["mission_exclusive", "chain_relic"], element="lightning", granted_perks=["precision_core"], combat_skill=skill("Meridian Bolt", 6, "ballistic", 4, 1)),
    "shepherds_gentle_hand": weapon("Shepherd's Gentle Hand", "mythic", "hammer", 4, "A titan-sized restraint hammer. The wielder gains Beast Bond and can finish a target without killing it.", tags=["mission_exclusive", "chain_relic"], granted_perks=["beast_bond"], combat_skill=skill("Colossus Restraint", 1, "melee", 4, 2, True)),
    "starless_door_key": weapon("Starless Door Key", "mythic", "wand", 3, "A void focus recovered beyond the last signal. It trades normal reach for a powerful distant spell.", tags=["mission_exclusive", "chain_relic"], element="void", attack_range=2, combat_skill=skill("Threshold Ray", 6, "ignore", 5, 1)),
}

FACTION_STARTERS = {
    "goblin_warhost": ["goblin_notched_axe", "goblin_net_bow", "smokecaller_staff"],
    "ashen_procession": ["gravekeepers_spade", "mourning_censer", "pale_watch_lance"],
    "arcane_convergence": ["cracked_ley_wand", "prism_tuning_fork", "winterglass_grimoire"],
    "great_beast_tide": ["antler_hatchet", "hunters_bola", "razorvine_spear"],
    "starfall_omen": ["meteor_iron_knife", "skyfall_focus", "voidglass_crossbow"],
}
CHAIN_RELICS = {
    "black_banner_court": "empty_crowns_verdict",
    "processions_empty_hearse": "processional_last_light",
    "meridian_engine": "meridian_arc_driver",
    "shepherd_of_titans": "shepherds_gentle_hand",
    "door_between_dead_stars": "starless_door_key",
}


def apply_gear_expansion(items, missions, general, events):
    items.update(deepcopy(NEW_GEAR))
    for iid, rank, weight in [
        ("rusty_knife", "E", 14), ("worn_jacket", "E", 12), ("work_boots", "E", 12),
        ("watchmans_cudgel", "E", 12), ("apprentice_wand", "E", 12),
        ("hooked_spear", "D", 9), ("weighted_sling", "D", 9),
        ("coalbrand_sabre", "C", 6), ("venomthorn_bow", "C", 6),
        ("stormglass_rod", "B", 3), ("mercykeepers_maul", "A", 1),
    ]:
        general.append((iid, rank, weight))
    for event_id, ids in FACTION_STARTERS.items():
        events[event_id]["loot"][:0] = [(iid, rank, weight) for iid, rank, weight in zip(ids, ["E", "D", "C"], [12, 10, 6])]
    mission_caches = {
        "goblin_warcamp": [("goblin_notched_axe", "E", 12), ("goblin_net_bow", "D", 8), ("ironcap_buckler", "C", 6), ("warhost_banner", "B", 3), ("warlords_cleaver", "S", 1)],
        "goblin_captive_cart": [("goblin_notched_axe", "E", 10), ("goblin_net_bow", "D", 12), ("cartmaster_route_book", "C", 4), ("ironcap_buckler", "C", 6)],
        "goblin_smoke_signals": [("goblin_notched_axe", "E", 10), ("goblin_net_bow", "D", 8), ("smokecaller_staff", "C", 10), ("crooked_shaman_staff", "A", 3)],
        "black_banner_ledger": [("watchmans_cudgel", "E", 10), ("hooked_spear", "D", 10), ("reinforced_vest", "D", 8), ("ranger_cloak", "C", 6)],
        "black_banner_court": [("watchmans_cudgel", "E", 8), ("hooked_spear", "D", 9), ("coalbrand_sabre", "C", 6), ("tower_shield", "B", 4), ("mercykeepers_maul", "A", 1)],
        "processions_empty_hearse": list(events["ashen_procession"]["loot"]),
        "meridian_engine": list(events["arcane_convergence"]["loot"]),
        "shepherd_of_titans": list(events["great_beast_tide"]["loot"]),
        "door_between_dead_stars": list(events["starfall_omen"]["loot"]),
    }
    for mid, pool in mission_caches.items():
        if mid in missions:
            missions[mid]["loot_pool"] = pool
    for mid, iid in CHAIN_RELICS.items():
        missions[mid].setdefault("reward_rolls", []).append({
            "source": "chain relic discovery", "chance": 14, "critical_bonus": 8,
            "requires_chain_parent": True, "reward": {"item": iid},
        })
        missions[mid].setdefault("reward_preview", []).append(f"Chain relic: {items[iid]['name']} (14%; 22% on critical success)")
    # Existing high-tier gear gains an action identity too; saved instances remain compatible.
    upgrades = {
        "ember_staff": {"element": "fire", "on_hit": {"id": "burn", "chance": 20, "turns": 2}},
        "warlords_cleaver": {"combat_skill": skill("Warhost Cleave", 1, "melee", 3, 2)},
        "mourning_blade": {"element": "holy", "combat_skill": skill("Grave Sever", 1, "melee", 3, 1)},
        "bottled_storm": {"combat_skill": skill("Storm Release", 4, "ignore", 3, 1)},
        "titanbone_spear": {"combat_skill": skill("Titan Thrust", 1, "melee", 4, 1)},
        "comet_string_bow": {"element": "void", "combat_skill": skill("Comet Pierce", 6, "ballistic", 3, 1)},
        "star_metal_blade": {"element": "void", "combat_skill": skill("Impact Cut", 1, "melee", 2, 1)},
    }
    for iid, fields in upgrades.items():
        items[iid].update(fields)
