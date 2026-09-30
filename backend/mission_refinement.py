"""Final data pass for mission identity, story structure, and reward intent.

This module deliberately contains no imports from ``content``.  It receives the
finished mission table and annotates it after event, chain, and world-thread data
have all been assembled.
"""

from __future__ import annotations

from typing import Any


FORM_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("rescue", ("captive", "missing", "clinic", "quarantine", "rescue")),
    ("escort", ("convoy", "cart", "caravan", "migration", "procession")),
    ("defense", ("ambush", "checkpoint", "outpost", "siege", "vanguard", "stampede")),
    ("hunt", ("hunt", "alpha", "roost", "den", "spoor", "nest", "razorwing", "white fang", "world eater")),
    ("containment", ("breach", "squall", "storm", "zero hour", "second sun", "leyline", "gravity scar")),
    ("investigation", ("signal", "observatory", "trace", "ledger", "whispering", "mirror", "library", "tunnel map", "silent farm")),
    ("infiltration", ("fortress", "citadel", "crypt", "necropolis", "cathedral", "court", "warren", "redoubt", "tomb")),
    ("recovery", ("store", "scrap", "cache", "orchard", "workshop", "yard", "armory", "meadow", "crater", "glasswood")),
)


FORM_STORY: dict[str, dict[str, list[str]]] = {
    "recovery": {
        "success": [
            "The first haul was already packed when part of the site shifted. {lead} called everyone clear, found a second way in, and finished the search without leaving anyone beneath the wreckage.",
            "The obvious cache had been picked over. {party} followed the signs left by the last occupants and found what they had hidden before they fled.",
        ],
        "failure": [
            "The site began to give way before the useful stores could be freed. {lead} abandoned the haul and brought the party out ahead of the collapse.",
        ],
    },
    "rescue": {
        "success": [
            "Voices answered from beyond the last obstruction. {party} opened a route, covered the withdrawal, and did not leave until the people trapped there were moving toward Fortcamp.",
            "The rescue route closed almost as soon as it opened. {lead} held it long enough for the last survivor to cross, then followed with the danger close behind.",
        ],
        "failure": [
            "The party reached the trapped survivors, but every safe route out had closed. They withdrew to keep the disaster from claiming another group and returned with a plan for a second attempt.",
        ],
    },
    "escort": {
        "success": [
            "The route changed twice before the destination came into sight. {lead} kept the column moving while the others cleared each obstruction before it could become an ambush.",
            "Someone tested the convoy near the narrowest part of the road. {party} closed around it, broke the attack, and delivered what had been placed in their care.",
        ],
        "failure": [
            "The road ahead became indefensible. The party saved the people who could still move, but the cargo and the original route were lost.",
        ],
    },
    "defense": {
        "success": [
            "The attack came from the side the contract had called secure. {party} turned in time, held the crossing, and forced the enemy to leave its stolen supplies behind.",
            "The defenders tried to draw the party into a prepared lane. {lead} recognized the trap, shifted the pressure elsewhere, and broke the position from its weakest edge.",
        ],
        "failure": [
            "Holding the position would have trapped the party with it. {lead} ordered the retreat before the enemy closed the road and carried warning of the threat back to Fortcamp.",
        ],
    },
    "hunt": {
        "success": [
            "The trail doubled back where the ground concealed it best. {party} waited instead of chasing, caught the quarry on its return, and ended the threat away from the settled road.",
            "The creature chose the ground for the final encounter. {lead} drew it away from its advantage while the rest of the party closed the only escape it had left.",
        ],
        "failure": [
            "The tracks led into ground where pursuit would have cost lives. The party marked the trail, warned the nearest settlements, and returned without pretending the hunt was finished.",
        ],
    },
    "containment": {
        "success": [
            "The disturbance changed shape while the party worked. {lead} recognized the new pattern, moved the final anchor, and closed the danger before it could spread beyond the site.",
            "For a few moments the breach pushed back against every safeguard. {party} held the line, completed the seal, and watched the surrounding ground settle into silence.",
        ],
        "failure": [
            "The disturbance grew faster than the party could contain it. They broke off before the escape route vanished and returned with measurements for a stronger attempt.",
        ],
    },
    "investigation": {
        "success": [
            "The first answer was meant to end the search. {lead} noticed what had been removed from the evidence, followed the omission, and found the part someone had tried to hide.",
            "Nothing at the site matched the story that had reached Fortcamp. {party} reconstructed what happened from what remained and returned with a lead that pointed farther down the same road.",
        ],
        "failure": [
            "The evidence began disappearing while the party was still reading it. They preserved what they could, but the person or force behind the site stayed ahead of them.",
        ],
    },
    "infiltration": {
        "success": [
            "The outer route ended at a door that should not have been guarded. {lead} changed the approach, brought the party through the neglected side, and reached the objective before the whole stronghold could respond.",
            "The alarm began in a distant wing. {party} used the confusion, crossed the defended interior, and left with the objective before the garrison understood where the real breach had happened.",
        ],
        "failure": [
            "The stronghold sealed itself section by section. The party escaped the last closing passage, but the objective remained behind the defenses.",
        ],
    },
    "operation": {
        "success": [
            "The contract changed as soon as the party reached the site. {lead} set a new order of work, and {party} solved the immediate danger before it could spread to the road home.",
            "A second problem surfaced behind the one named on the board. {party} divided the work, kept both from getting worse, and returned with the objective secure.",
        ],
        "failure": [
            "The situation had moved beyond the contract before the party arrived. They prevented a worse loss, but the original objective slipped out of reach.",
        ],
    },
    "diplomacy": {
        "success": [
            "The first offer failed because it answered the wrong concern. {lead} listened to what the other side kept returning to, changed the terms, and found an agreement both parties could defend afterward.",
            "The meeting nearly ended when an old grievance surfaced. {party} stayed long enough to separate that dispute from the present request and left with a workable promise instead of another enemy.",
        ],
        "failure": [
            "Neither side trusted the terms enough to commit. The party left without an agreement, but with a clearer understanding of what the faction will demand next time.",
        ],
    },
}


CRITICAL_ENDINGS = [
    "With the immediate danger gone, the party had time to search the part of the site everyone else had missed. What they found made the return worth more than the original contract promised.",
    "The clean finish opened one last opportunity. {lead} took it, and the party returned with evidence and salvage that a hurried withdrawal would have left behind.",
]

CRITICAL_FAILURE_ENDINGS = [
    "The danger reached the withdrawal route first. The party escaped through rough ground, but someone came home hurt and the unfinished threat was left stronger than before.",
    "One bad decision became three emergencies at once. {lead} kept the group together long enough to escape, though the objective and most of their equipment had to be abandoned.",
]


FORM_OBJECTIVES = {
    "recovery": "Recover the useful stores and leave the site stable enough for the route home.",
    "rescue": "Reach the trapped people and bring them out alive.",
    "escort": "Move the protected people or cargo through the threatened route.",
    "defense": "Break the hostile position before it can close the surrounding roads.",
    "hunt": "Find the source of the attacks and stop it away from settled ground.",
    "containment": "Control the spreading hazard before it reaches another site.",
    "investigation": "Learn what happened and preserve evidence that can lead to the next cause.",
    "infiltration": "Cross the defended site, secure the objective, and leave before the whole force responds.",
    "operation": "Resolve the contract's central danger and return with proof of the result.",
    "diplomacy": "Reach an agreement, learn what the other side wants, and decide what Fortcamp is willing to promise.",
}


ENCOUNTER_PLANS = {
    "recovery": {"mode": "adventure", "combat": "expected", "bodyguards": 0, "description": "Explore a generated site across connected rooms or floors, recover what matters, and decide when to leave."},
    "rescue": {"mode": "branching", "combat": "possible", "bodyguards": 1, "description": "Locate the missing people through rolls or choices; extraction may become a tactical encounter."},
    "escort": {"mode": "tactical", "combat": "expected", "bodyguards": 0, "description": "Protect moving people or cargo while the route and opposition create changing objectives."},
    "defense": {"mode": "tactical", "combat": "expected", "bodyguards": 0, "description": "Position the force and protect a person, object, structure, or boundary until the threat ends."},
    "hunt": {"mode": "branching", "combat": "expected", "bodyguards": 0, "description": "Use rolls to track and shape the encounter, then confront, capture, drive off, or kill the quarry."},
    "containment": {"mode": "branching", "combat": "possible", "bodyguards": 1, "description": "Use expertise to control the hazard; failure, delay, or certain choices can create combat."},
    "investigation": {"mode": "roll", "combat": "unknown", "bodyguards": 1, "description": "Resolve clues and choices primarily through rolls. Some discoveries can become encounters without advance warning."},
    "infiltration": {"mode": "tactical", "combat": "expected", "bodyguards": 0, "description": "Cross a guarded map while managing detection; stealth rules will determine how and when combat begins."},
    "operation": {"mode": "branching", "combat": "possible", "bodyguards": 1, "description": "Combine rolls, choices, and encounters according to the contract's changing objective."},
    "diplomacy": {"mode": "dialogue", "combat": "unknown", "bodyguards": 1, "description": "Negotiate through informed choices and social rolls; agreements can unlock Private Contracts."},
}


FORM_OVERRIDES = {
    "goblin_smoke_signals": "investigation",
    "goblin_bridge_trappers": "defense",
    "goblin_boar_riders": "hunt",
    "goblin_captive_cart": "rescue",
    "goblin_powder_mill": "infiltration",
    "goblin_tunnel_map": "investigation",
    "goblin_shaman_circle": "containment",
    "hobgoblin_vanguard": "defense",
    "goblin_siege_line": "defense",
    "goblin_emerald_throne": "infiltration",
    "undead_whispering_well": "investigation",
    "undead_bone_collectors": "hunt",
    "undead_corpse_lanterns": "investigation",
    "undead_chapel_bell": "containment",
    "undead_plague_ossuary": "recovery",
    "undead_drowned_choir": "containment",
    "undead_black_hearse": "hunt",
    "undead_death_knight": "hunt",
    "undead_hollow_cathedral": "infiltration",
    "undead_last_funeral": "containment",
    "arcane_crystal_rain": "recovery",
    "arcane_runaway_golem": "containment",
    "arcane_spellglass_field": "investigation",
    "arcane_bottled_storm": "containment",
    "arcane_time_lost_caravan": "rescue",
    "arcane_living_library": "infiltration",
    "arcane_gravity_well": "rescue",
    "arcane_dream_market": "diplomacy",
    "arcane_prism_tower": "containment",
    "arcane_zero_hour": "rescue",
    "beast_giant_spoor": "investigation",
    "beast_razorboar_nest": "hunt",
    "beast_webbed_caravan": "rescue",
    "beast_horned_stampede": "defense",
    "beast_razorwing_cliffs": "infiltration",
    "beast_breeding_hollow": "investigation",
    "beast_white_fang": "hunt",
    "beast_thunderherd": "recovery",
    "beast_leviathan_crossing": "defense",
    "beast_world_eater_wake": "hunt",
    "starfall_fallen_sparks": "recovery",
    "starfall_metal_thieves": "defense",
    "starfall_silent_farm": "rescue",
    "starfall_compass_storm": "investigation",
    "starfall_glasswood": "recovery",
    "starfall_hollow_signal": "investigation",
    "starfall_void_pilgrims": "investigation",
    "starfall_gravity_scar": "rescue",
    "starfall_black_observatory": "infiltration",
    "starfall_second_sun": "containment",
}


def _mission_form(mission_id: str, mission: dict[str, Any]) -> str:
    if mission.get("mission_form") in ENCOUNTER_PLANS:
        return mission["mission_form"]
    if mission_id in FORM_OVERRIDES:
        return FORM_OVERRIDES[mission_id]
    haystack = f"{mission_id} {mission.get('name', '')} {mission.get('description', '')}".lower()
    for form, needles in FORM_RULES:
        if any(needle in haystack for needle in needles):
            return form
    return "operation"


def _is_generic_narrative(narrative: dict[str, Any]) -> bool:
    joined = " ".join(
        value if isinstance(value, str) else " ".join(value or [])
        for value in narrative.values()
    )
    return (
        "with {lead} directing the approach" in joined
        or "The objective was secured after the party adjusted" in joined
        or "The operation landed cleanly enough" in joined
    )


def _audited_narrative(mission: dict[str, Any], form: str) -> dict[str, Any]:
    name = mission["name"]
    description = mission["description"]
    form_story = FORM_STORY[form]
    return {
        "approach": [
            f"The notice for {name} gave the facts in a few lines: {description} {{party}} reached the area quietly while {{lead}} studied what the notice had left out.",
            f"By the time {{party}} reached {name}, the situation had already started to change. {description} {{lead}} stopped the group outside the danger and chose the first move from there.",
        ],
        "critical_failure": CRITICAL_FAILURE_ENDINGS,
        "failure": form_story["failure"],
        "success": form_story["success"],
        "critical_success": form_story["success"] + CRITICAL_ENDINGS,
    }


def apply_mission_refinement(missions: dict[str, dict[str, Any]]) -> None:
    """Annotate and refine every finished mission template in place."""
    for mission_id, mission in missions.items():
        form = _mission_form(mission_id, mission)
        mission["mission_form"] = form
        mission["objective"] = FORM_OBJECTIVES[form]
        mission["audited"] = True
        mission.setdefault("reward_rolls", [])
        plan = ENCOUNTER_PLANS[form]
        mission["resolution_mode"] = "tactical" if mission.get("combat_encounter") else "roll"
        mission["encounter_plan"] = dict(plan)
        mission["bodyguard_slots"] = 0 if mission.get("combat_encounter") else int(plan["bodyguards"])

        # Celestial chapters already have fully authored multi-part scenes.
        if mission.get("chain_only"):
            continue
        if _is_generic_narrative(mission.get("narrative", {})):
            mission["narrative"] = _audited_narrative(mission, form)

    # First playable roll-to-battle investigation. The public mission card does
    # not reveal the trigger chance; its optional bodyguard is excluded from
    # every investigation roll and only deploys if the scouts catch the party.
    smoke_signals = missions["goblin_smoke_signals"]
    smoke_signals["bodyguard_slots"] = 1
    smoke_signals["branching_encounter"] = {
        "id": "goblin_smoke_signals", "trigger_chance": 45,
        "map_scenario": "hedgerow_signal_site",
        "trigger_text": "The signal crew spots the investigators and closes the road before the evidence can be carried home.",
    }

    # Story conclusions always change the world, but their trophy equipment and
    # permanent personal perks remain discoveries with explicit chances.
    finale_rewards = {
        "black_banner_court": ("empty_crown_standard", "bannerbreaker", 65),
        "processions_empty_hearse": ("bell_of_last_rites", "keeper_of_last_rites", 65),
        "meridian_engine": ("meridian_heart", "meridian_attunement", 60),
        "shepherd_of_titans": ("titan_shepherds_horn", "titan_speaker", 60),
        "door_between_dead_stars": ("starless_gate_sigil", "riftwalker", 55),
    }
    for mission_id, (item_id, perk_id, chance) in finale_rewards.items():
        mission = missions[mission_id]
        rewards = mission["rewards"]
        rewards.pop("guaranteed_items", None)
        rewards.pop("standalone_perk", None)
        mission["reward_rolls"].extend([
            {"source": "story relic", "chance": chance, "critical_bonus": 20, "reward": {"item": item_id}},
            {"source": "story boon", "chance": max(25, chance - 20), "critical_bonus": 15, "reward": {"standalone_perk": perk_id}},
        ])
        mission["reward_preview"] = [
            entry.replace("Guaranteed story relic", "Story relic chance").replace("Exclusive story perk", "Exclusive perk chance")
            for entry in mission.get("reward_preview", [])
        ]

    chapter_rewards = {
        "black_banner_ledger": ("black_banner_cipher", 70),
        "bell_beneath_mud": ("mudbound_clapper", 65),
        "brass_foreman": ("brass_foreman_key", 65),
        "wounded_colossus": ("colossus_heartblood", 60),
        "signal_knows_name": ("echoing_starstone", 55),
    }
    for mission_id, (item_id, chance) in chapter_rewards.items():
        mission = missions[mission_id]
        mission["rewards"].pop("guaranteed_items", None)
        mission["reward_rolls"].append({
            "source": "story discovery", "chance": chance, "critical_bonus": 20,
            "reward": {"item": item_id},
        })
        mission["reward_preview"] = [
            entry.replace("Guaranteed story relic", "Story discovery chance")
            for entry in mission.get("reward_preview", [])
        ]

    # Breaking the Tithe Convoy can teach the lead character how the Black
    # Banner fights, but one victory does not guarantee that permanent perk.
    convoy = missions["black_banner_convoy"]
    convoy["rewards"].pop("standalone_perk", None)
    convoy["reward_rolls"].append({
        "source": "captured Banner doctrine", "chance": 40, "critical_bonus": 20,
        "reward": {"standalone_perk": "bannerbreaker"},
    })
