import io
import random
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.champions import CATALOG, EXPANDED_CHAMPIONS
from backend.champions_lower_tiers import LOWER_TIER_CATALOG, LOWER_TIER_CHAMPIONS
from backend.celestials import CELESTIALS, CELESTIAL_CHAIN_STEPS
from backend.combat import STATUS_DEFINITIONS, _attack_preview, _movement_limit, apply_player_command, auto_resolve, battle_view, create_captive_cart_battle, create_goblin_warcamp_battle
from backend.content import CHAMPIONS, EVENT_REWARD_TABLES, ITEMS, MISSION_TEMPLATES, RECRUIT_PROFILES, STANDALONE_PERKS
from backend.db import Base
from backend.game import _award_reward_block, _make_procedural, _normalize_prisoners, _random_champion, analyze_mission, character_condition_met, effective_stat, manage_prisoner, new_game, normalize_state, prison_capacity, resolve_mission, train_perk
from backend.main import _resize_portrait
from backend.models import MissionInstance, PlayerState
from backend.races import BEASTKIN_RACES, RACE_CATALOG, RACE_GAMEPLAY, REGIONAL_RECRUIT_TABLES, SECRET_RECRUIT_EVENTS
import backend.portraits as portrait_module
import backend.appearance as appearance_module
from tools import champion_portrait_io
from backend.services import (
    _award_capture_loot, _battle_outcome_details, _rolled_pool_templates, _spawn_result_chains, active_pool_slot, available_chain_missions,
    claim_instance, choose_decision_instance, debug_resolve_now_instance, debug_start_battle, debug_start_goblin_battle, ensure_pool, force_pool_refresh, now_ts, pool_event,
    update_battle_instance,
)


def player_state(scavenging=1, traits=None):
    perk = "master" if scavenging >= 9 else "expert" if scavenging >= 7 else "skilled" if scavenging >= 5 else "basic" if scavenging >= 3 else "none"
    return new_game({
        "name": "Tester",
        "traits": traits or [],
        "stats": {"scavenging": scavenging},
        "perks": {"scavenging": perk},
        "attributes": {"dex": scavenging, "luk": scavenging},
    })


class CriticalSuccessRulesTests(unittest.TestCase):
    def test_special_critical_is_impossible_until_criterion_matches(self):
        mission = MISSION_TEMPLATES["roadside_store"]
        state = player_state(scavenging=1)
        analysis = analyze_mission(state, mission, ["player"])

        self.assertFalse(analysis["critical_success_available"])
        self.assertEqual(analysis["probabilities"]["critical_success"], 0)
        with self.assertRaisesRegex(ValueError, "special critical criterion"):
            resolve_mission(state, mission, ["player"], analysis, "locked", "critical_success")

    def test_matching_special_criterion_opens_critical_success(self):
        mission = MISSION_TEMPLATES["roadside_store"]
        state = player_state(scavenging=8)
        analysis = analyze_mission(state, mission, ["player"])

        self.assertTrue(analysis["critical_success_available"])
        self.assertGreater(analysis["probabilities"]["critical_success"], 0)

    def test_general_mission_uses_normal_stat_critical(self):
        mission = MISSION_TEMPLATES["fallen_orchard"]
        state = player_state(scavenging=10)
        analysis = analyze_mission(state, mission, ["player"])

        self.assertFalse(mission["critical_any"])
        self.assertTrue(analysis["critical_success_available"])
        self.assertGreater(analysis["probabilities"]["critical_success"], 0)


class MissionPoolRulesTests(unittest.TestCase):
    def test_optional_bodyguard_never_changes_investigation_odds(self):
        state = new_game({"name": "Tracker", "stats": {"survival": 7}, "attributes": {"dex": 7}})
        guard = deepcopy(state["characters"][0])
        guard.update({"id": "bodyguard", "name": "Shield", "is_player": False, "status": "idle"})
        state["characters"].append(guard)
        mission = MISSION_TEMPLATES["goblin_smoke_signals"]
        alone = analyze_mission(state, mission, ["player"])
        protected = analyze_mission(state, mission, ["player"], bodyguard_ids=["bodyguard"])
        self.assertTrue(protected["claimable"])
        self.assertEqual(protected["probabilities"], alone["probabilities"])
        self.assertEqual(protected["support_bonus"], alone["support_bonus"])
        self.assertFalse(analyze_mission(state, mission, ["player"], bodyguard_ids=["player"])["claimable"])

    def test_rank_floors_and_s_is_rare_and_capped(self):
        s_counts = []
        for slot in range(1000):
            ids = _rolled_pool_templates("pool-test", slot, 1)
            ranks = [MISSION_TEMPLATES[mission_id].get("rank", "E") for mission_id in ids]
            self.assertEqual(ranks.count("E"), 16)
            self.assertEqual(ranks.count("D"), 8)
            self.assertLessEqual(ranks.count("C"), 5)
            self.assertLessEqual(ranks.count("B"), 3)
            self.assertLessEqual(ranks.count("A"), 2)
            self.assertLessEqual(ranks.count("S"), 3)
            s_counts.append(ranks.count("S"))

        self.assertIn(0, s_counts)
        self.assertTrue(any(count > 0 for count in s_counts))

    def test_every_event_has_a_broad_exclusive_catalog(self):
        for event_id in ("goblin_warhost", "ashen_procession", "arcane_convergence", "great_beast_tide", "starfall_omen"):
            themed = [mission for mission in MISSION_TEMPLATES.values() if mission.get("event") == event_id]
            self.assertGreaterEqual(len(themed), 12)
            self.assertTrue({"E", "D", "C", "B", "A", "S"}.issubset({mission["rank"] for mission in themed}))

    def test_general_refresh_never_uses_event_only_contracts(self):
        slot = next(slot for slot in range(10000) if pool_event("general-test", slot)["id"] == "general")
        ids = _rolled_pool_templates("general-test", slot, 8)
        self.assertTrue(all(not MISSION_TEMPLATES[mission_id].get("event") for mission_id in ids))

    def test_triggered_consequences_never_enter_random_pool(self):
        for slot in range(100):
            ids = _rolled_pool_templates("consequence-audit", slot, 4)
            self.assertTrue(all(not MISSION_TEMPLATES[mission_id].get("trigger_only") for mission_id in ids))

    def test_every_non_chain_mission_belongs_to_the_world_and_has_varied_prose(self):
        for mission in MISSION_TEMPLATES.values():
            if mission.get("chain_only"):
                continue
            self.assertTrue(mission.get("story_thread_name"), mission["name"])
            self.assertTrue(mission.get("world_context"), mission["name"])
            narrative = mission.get("narrative", {})
            self.assertTrue(narrative.get("approach"), mission["name"])
            for outcome in ("failure", "success", "critical_failure", "critical_success"):
                self.assertTrue(narrative.get(outcome), f"{mission['name']} / {outcome}")

    def test_every_mission_has_completed_design_audit_metadata(self):
        valid_forms = {"recovery", "rescue", "escort", "defense", "hunt", "containment", "investigation", "infiltration", "operation", "diplomacy"}
        for mission in MISSION_TEMPLATES.values():
            self.assertTrue(mission.get("audited"), mission["name"])
            self.assertIn(mission.get("mission_form"), valid_forms, mission["name"])
            self.assertTrue(mission.get("objective"), mission["name"])
            self.assertIsInstance(mission.get("reward_rolls"), list, mission["name"])
            self.assertIn(mission.get("resolution_mode"), {"roll", "tactical", "choices", "choices → tactical"}, mission["name"])
            self.assertIn(mission.get("encounter_plan", {}).get("mode"), {"roll", "dialogue", "branching", "tactical", "adventure"}, mission["name"])
            self.assertIn(mission.get("encounter_plan", {}).get("combat"), {"expected", "possible", "unknown"}, mission["name"])

    def test_hedgerow_private_chain_moves_from_diplomacy_to_prepared_defense(self):
        investigation = MISSION_TEMPLATES["goblin_smoke_signals"]
        terms = MISSION_TEMPLATES[investigation["chain_next"]]
        defense = MISSION_TEMPLATES[terms["chain_next"]]
        self.assertEqual((terms["mission_form"], terms["resolution_mode"]), ("diplomacy", "choices"))
        self.assertEqual((defense["mission_form"], defense["resolution_mode"]), ("defense", "tactical"))
        self.assertTrue(terms["chain_only"] and defense["chain_only"])
        self.assertEqual((terms["chain_step"], defense["chain_step"], defense["chain_total"]), (1, 2, 2))
        self.assertEqual(defense["combat_encounter"]["id"], "frontier_watch_defense")
        self.assertEqual({roll["reward"]["item"] for roll in defense["reward_rolls"]}, {"trappers_roll", "hedgerow_engineers_kit"})

    def test_success_can_set_a_world_consequence_in_motion(self):
        mission = deepcopy(MISSION_TEMPLATES["highway_ambush"])
        mission["board_followups"][0]["chance"] = 100
        state = player_state(scavenging=10)

        result = resolve_mission(
            state, mission, ["player"], analyze_mission(state, mission, ["player"]),
            "certain-consequence", "success",
        )

        self.assertEqual(result["board_followups"][0]["template_id"], "black_banner_ledger")
        self.assertIn("follow-up contracts for your party", result["story"][-1])

    def test_story_finale_guarantees_world_outcome_but_rolls_relic_and_perk(self):
        mission = MISSION_TEMPLATES["meridian_engine"]
        relic_results = set()
        perk_results = set()
        for seed in range(40):
            state = player_state(scavenging=10)
            result = resolve_mission(
                state, mission, ["player"], analyze_mission(state, mission, ["player"]),
                f"meridian-finale-{seed}", "success",
            )
            relic_results.add(any(item["item_id"] == "meridian_heart" for item in state["inventory"]))
            perk_results.add("meridian_attunement" in state["characters"][0]["traits"])
            self.assertTrue(state["flags"]["mastered_meridian_engine"])
            self.assertEqual(result["rewards"]["world_flags"][0]["name"], "Mastered the Meridian Engine")
        self.assertEqual(relic_results, {False, True})
        self.assertEqual(perk_results, {False, True})

    def test_starless_critical_rolls_for_a_voidsent(self):
        mission = MISSION_TEMPLATES["door_between_dead_stars"]
        outcomes = set()
        for seed in range(40):
            state = player_state(scavenging=10)
            result = resolve_mission(
                state, mission, ["player"], analyze_mission(state, mission, ["player"]),
                f"starless-finale-{seed}", "critical_success",
            )
            outcomes.add(any(recruit.get("profile") == "voidsent" for recruit in result["rewards"]["recruits"]))
            self.assertTrue(any(roll["source"] == "critical recruit" for roll in result["rewards"]["loot_rolls"]))
            self.assertTrue(any(roll["source"] == "story relic" for roll in result["rewards"]["loot_rolls"]))
        self.assertEqual(outcomes, {False, True})

    def test_event_champion_pool_awards_an_unowned_champion(self):
        state = player_state()
        awarded = {"materials": {}, "items": [], "blueprints": [], "recruits": []}
        block = {"champion_pool": [{"champion": "goblin_slayer", "weight": 70}, {"champion": "sword_maiden", "weight": 30}]}

        _award_reward_block(state, block, awarded, random.Random(4))

        self.assertEqual(len(awarded["recruits"]), 1)
        self.assertEqual(awarded["recruits"][0]["kind"], "champion")
        self.assertIn(awarded["recruits"][0]["profile"], {"goblin_slayer", "sword_maiden"})

    def test_debug_refresh_forces_selected_event_and_new_slot(self):
        first = force_pool_refresh("debug-test", "goblin_warhost")
        second = force_pool_refresh("debug-test", "starfall_omen")

        self.assertNotEqual(first, second)
        self.assertEqual(active_pool_slot("debug-test"), second)
        self.assertEqual(pool_event("debug-test", second)["id"], "starfall_omen")
        self.assertTrue(pool_event("debug-test", second)["debug_forced"])


class RewardAndRecoveryTests(unittest.TestCase):
    def test_starfall_success_rolls_themed_keepsake_and_scaled_caches(self):
        mission = MISSION_TEMPLATES["starfall_crater"]
        outcomes = set()
        for seed in range(40):
            state = player_state(scavenging=10)
            result = resolve_mission(state, mission, ["player"], analyze_mission(state, mission, ["player"]), f"starfall-rewards-{seed}", "success")
            outcomes.add("starfall_shard" in result["rewards"]["items"])
            self.assertEqual(len(result["rewards"]["loot_rolls"]), 6)  # keepsake, three caches, event recruit, Champion
        self.assertEqual(outcomes, {False, True})

    def test_first_successful_high_rank_event_cache_is_event_gear(self):
        mission = MISSION_TEMPLATES["starfall_crater"]
        won_item = None
        for seed in range(30):
            state = player_state(scavenging=10)
            result = resolve_mission(state, mission, ["player"], analyze_mission(state, mission, ["player"]), f"star-gear-{seed}", "success")
            first_cache = next(roll for roll in result["rewards"]["loot_rolls"] if roll["source"] == "event cache")
            if first_cache["item"]:
                won_item = first_cache["item"]
                break
        from backend.content import EVENT_REWARD_TABLES, MISSION_RANKS
        eligible = {iid for iid, minimum_rank, _ in EVENT_REWARD_TABLES['starfall_omen']['loot'] if MISSION_RANKS.index(minimum_rank) <= MISSION_RANKS.index('A')}
        self.assertIn(won_item, eligible)

    def test_only_paid_contracts_award_gold(self):
        paid_state = player_state(scavenging=10)
        paid = MISSION_TEMPLATES["highway_ambush"]
        paid_result = resolve_mission(paid_state, paid, ["player"], analyze_mission(paid_state, paid, ["player"]), "paid", "success")
        unpaid_state = player_state(scavenging=10)
        unpaid = MISSION_TEMPLATES["creekside_scrap"]
        unpaid_result = resolve_mission(unpaid_state, unpaid, ["player"], analyze_mission(unpaid_state, unpaid, ["player"]), "unpaid", "success")

        self.assertGreater(paid_result["rewards"]["gold"], 0)
        self.assertEqual(unpaid_result["rewards"]["gold"], 0)

    def test_critical_failure_incapacitates_one_character_in_tent(self):
        state = player_state(scavenging=1)
        mission = {**MISSION_TEMPLATES["fallen_orchard"], "rank": "D"}
        analysis = analyze_mission(state, mission, ["player"])

        result = resolve_mission(state, mission, ["player"], analysis, "injury", "critical_failure")
        character = state["characters"][0]

        self.assertEqual(character["status"], "incapacitated")
        self.assertEqual(character["recovery_location"], "Tent")
        self.assertEqual(len(result["rewards"]["injuries"]), 1)
        self.assertEqual(result["rewards"]["materials"], {})
        self.assertEqual(result["rewards"]["items"], [])

    def test_infirmary_shortens_recovery_and_expired_injury_normalizes(self):
        state = player_state(scavenging=1)
        state["buildings"].append({"id": "clinic", "type": "infirmary", "x": 7, "y": 1, "assigned": []})
        mission = {**MISSION_TEMPLATES["fallen_orchard"], "rank": "D"}
        result = resolve_mission(state, mission, ["player"], analyze_mission(state, mission, ["player"]), "clinic-injury", "critical_failure")
        injury = result["rewards"]["injuries"][0]

        self.assertEqual(injury["location"], "Infirmary")
        self.assertLessEqual(injury["recovers_at"] - result["timestamp"], 30 * 60)
        state["characters"][0]["recovers_at"] = 0
        normalize_state(state)
        self.assertEqual(state["characters"][0]["status"], "idle")

    def test_every_event_has_multiple_exclusive_recruit_races(self):
        for event in EVENT_REWARD_TABLES.values():
            profiles = [profile for profile, _, _ in event.get("recruits", [])]
            self.assertGreaterEqual(len(profiles), 4)
            self.assertTrue(all(profile in RECRUIT_PROFILES for profile in profiles))
            self.assertGreaterEqual(len({RECRUIT_PROFILES[profile]["race"] for profile in profiles}), 4)

    def test_event_recruit_can_join_from_a_high_rank_mission(self):
        mission = MISSION_TEMPLATES["starfall_second_sun"]
        recruited = None
        for seed in range(100):
            state = player_state(scavenging=10)
            result = resolve_mission(state, mission, ["player"], analyze_mission(state, mission, ["player"]), f"star-recruit-{seed}", "success")
            event_recruits = [entry for entry in result["rewards"]["recruits"] if entry["kind"] == "event"]
            if event_recruits:
                recruited = event_recruits[0]
                break
        self.assertIsNotNone(recruited)
        starfall_profiles = {profile for profile, _, _ in EVENT_REWARD_TABLES["starfall_omen"]["recruits"]}
        self.assertIn(recruited["race"], {RECRUIT_PROFILES[profile]["race"] for profile in starfall_profiles})

    def test_general_missions_can_find_nonhuman_survivors(self):
        mission = MISSION_TEMPLATES["deep_expedition"]
        recruited = None
        for seed in range(150):
            state = player_state(scavenging=10)
            result = resolve_mission(state, mission, ["player"], analyze_mission(state, mission, ["player"]), f"general-recruit-{seed}", "success")
            encounters = [entry for entry in result["rewards"]["recruits"] if entry["kind"] == "survivor"]
            if encounters and encounters[0]["race"] != "Human":
                recruited = encounters[0]
                break
        self.assertIsNotNone(recruited)
        deepwood_profiles = {profile for profile, _, _ in REGIONAL_RECRUIT_TABLES["deepwood"]}
        self.assertIn(recruited["race"], {RECRUIT_PROFILES[profile]["race"] for profile in deepwood_profiles})

    def test_equipped_mythic_item_grants_active_mission_perks(self):
        state = player_state()
        state["inventory"].append({"instance_id": "core", "item_id": "starfall_core"})
        character = state["characters"][0]
        character["equipment"]["accessory"] = "core"

        self.assertTrue(character_condition_met(state, character, {"kind": "trait", "value": "stellar_aegis"}))
        self.assertGreaterEqual(ITEMS["starfall_core"]["bonuses"]["magic"], 7)
        self.assertGreaterEqual(len(ITEMS["starfall_core"]["granted_perks"]), 3)


class RaceDiscoveryTests(unittest.TestCase):
    def test_every_race_has_a_strong_gameplay_identity(self):
        self.assertEqual(set(RACE_GAMEPLAY), set(RACE_CATALOG))
        for race, profile in RACE_GAMEPLAY.items():
            self.assertTrue(profile["summary"], race)
            self.assertGreater(profile["hp_multiplier"], 0, race)
            self.assertIn(profile["movement_type"], {"ground", "flying", "amphibious", "amorphous"}, race)

    def test_goblin_is_fragile_fast_and_evasive_in_combat(self):
        human_state = new_game({"name": "Human", "race": "Human", "attributes": {"agi": 8, "vit": 8}})
        goblin_state = new_game({"name": "Goblin", "race": "Goblin", "attributes": {"agi": 8, "vit": 8}})
        human = create_goblin_warcamp_battle(human_state, ["player"], "human-race-test")["units"]["player"]
        goblin = create_goblin_warcamp_battle(goblin_state, ["player"], "goblin-race-test")["units"]["player"]
        self.assertLess(goblin["max_hp"], human["max_hp"])
        self.assertGreater(goblin["move"], human["move"])
        self.assertGreater(goblin["evasion"], human["evasion"])

    def test_every_procedural_race_is_documented(self):
        procedural_races = {profile["race"] for profile in RECRUIT_PROFILES.values()}
        self.assertTrue(procedural_races.issubset(RACE_CATALOG))
        self.assertIn("Werewolf", RACE_CATALOG)
        self.assertEqual(len(RACE_CATALOG), 42)
        self.assertNotIn("Beastkin", RACE_CATALOG)
        self.assertTrue({"Catfolk", "Foxkin", "Harpy", "Centaur", "Minotaur"}.issubset(BEASTKIN_RACES))

    def test_regional_pools_only_reference_real_profiles_and_weight_rare_races_lower(self):
        for table in REGIONAL_RECRUIT_TABLES.values():
            self.assertTrue(all(profile in RECRUIT_PROFILES for profile, _, _ in table))
        deepwood = {profile: weight for profile, _, weight in REGIONAL_RECRUIT_TABLES["deepwood"]}
        mountains = {profile: weight for profile, _, weight in REGIONAL_RECRUIT_TABLES["mountains"]}
        self.assertLess(deepwood["fairy"], deepwood["wood_elf"])
        self.assertLess(mountains["troll"], mountains["dwarf"])
        self.assertLess(mountains["dragonkin"], mountains["dwarf"])

    def test_qualifying_lineup_gets_only_a_secret_possibility_signal(self):
        state = player_state()
        state["characters"][0]["race"] = "Gnome"
        state["characters"][0]["traits"] = ["engineer"]
        constructed = _make_procedural("manaforged", random.Random(1))
        companion = _make_procedural("survivor", random.Random(2))
        state["characters"].extend([constructed, companion])
        mission = MISSION_TEMPLATES["haunted_foundry"]
        party_ids = ["player", constructed["id"], companion["id"]]

        analysis = analyze_mission(state, mission, party_ids)

        self.assertTrue(analysis["secret_event_possible"])
        self.assertNotIn("secret", " ".join(mission.get("visible_hints", [])).lower())

    def test_secret_event_can_award_its_contextual_recruit(self):
        state = player_state()
        state["characters"][0]["race"] = "Gnome"
        state["characters"][0]["traits"] = ["engineer"]
        constructed = _make_procedural("manaforged", random.Random(3))
        companion = _make_procedural("survivor", random.Random(4))
        state["characters"].extend([constructed, companion])
        mission = deepcopy(MISSION_TEMPLATES["haunted_foundry"])
        mission["secret_events"][0]["chance"] = 100
        party_ids = ["player", constructed["id"], companion["id"]]
        analysis = analyze_mission(state, mission, party_ids)

        result = resolve_mission(state, mission, party_ids, analysis, "secret-race", "success")

        self.assertEqual(result["rewards"]["secret_events"][0]["id"], "the_sleeping_shift")
        self.assertTrue(any(recruit["profile"] == "automaton" for recruit in result["rewards"]["recruits"]))

    def test_authored_secret_encounters_stay_low_chance(self):
        chances = [event["chance"] for events in SECRET_RECRUIT_EVENTS.values() for event in events]
        self.assertGreaterEqual(len(chances), 6)
        self.assertTrue(all(1 <= chance <= 7 for chance in chances))

    def test_retired_races_and_perks_migrate_without_promoting_old_celestines(self):
        replacements = {
            "Ashborn": ("Undead", "undead"),
            "Dhampir": ("Vampire", "vampire"),
            "Graveborn": ("Undead", "undead"),
            "Cometkin": ("Alien", "alien"),
            "Voidborn": ("Voidsent", "voidsent"),
            "Starforged": ("Automaton", "automaton"),
            "Celestine": ("Aasimar", "aasimar"),
        }
        for old_race, (new_race, new_profile) in replacements.items():
            state = player_state()
            state["version"] = 6
            state["characters"][0].update({
                "race": old_race, "generation_profile": old_race.lower(),
                "traits": ["ash_body", "living_constellation"],
            })

            normalize_state(state)

            character = state["characters"][0]
            self.assertEqual(character["race"], new_race)
            self.assertEqual(character["generation_profile"], new_profile)
            self.assertEqual(character["traits"], ["deathless", "radiant_soul"])
        self.assertEqual(state["version"], 10)


class PrisonerManagementTests(unittest.TestCase):
    @staticmethod
    def prisoner(prisoner_id, holding="prison_cell", **extra):
        return {
            "id": prisoner_id, "name": prisoner_id.title(), "race": "Goblin",
            "kind": "raider", "boss": False, "holding": holding, "status": "held",
        } | extra

    def test_cell_capacity_and_stockade_timer_survive_swaps(self):
        state = new_game({"name": "Warden"})
        state["buildings"].append({
            "id": "prison_test", "type": "prison_cell", "x": 7, "y": 4, "assigned": [],
        })
        state["prisoners"] = [
            self.prisoner("a", "temporary_stockade", stockade_remaining_seconds=200, stockade_expires_at=1200),
            *(self.prisoner(letter) for letter in ("b", "c", "d", "e")),
        ]
        self.assertEqual(prison_capacity(state), 4)

        first = manage_prisoner(state, "a", "secure", "b", now=1000)
        self.assertEqual(first["displaced"]["id"], "b")
        self.assertEqual(next(p for p in state["prisoners"] if p["id"] == "a")["stockade_remaining_seconds"], 200)
        self.assertEqual(next(p for p in state["prisoners"] if p["id"] == "b")["stockade_expires_at"], 4600)

        manage_prisoner(state, "b", "secure", "a", now=1100)
        prisoner_a = next(p for p in state["prisoners"] if p["id"] == "a")
        prisoner_b = next(p for p in state["prisoners"] if p["id"] == "b")
        self.assertEqual(prisoner_a["stockade_expires_at"], 1300)
        self.assertEqual(prisoner_b["stockade_remaining_seconds"], 3500)

        _normalize_prisoners(state, now=1301)
        self.assertNotIn("a", [p["id"] for p in state["prisoners"]])
        self.assertIn("b", [p["id"] for p in state["prisoners"]])

    def test_any_prisoner_can_be_sold_for_gold(self):
        state = new_game({"name": "Warden"})
        state["prisoners"] = [self.prisoner("chief", "temporary_stockade", boss=True, kind="chieftain")]
        before = state["resources"]["gold"]
        result = manage_prisoner(state, "chief", "sell", now=1000)
        self.assertEqual(result["gold"], 40)
        self.assertEqual(state["resources"]["gold"], before + 40)
        self.assertEqual(state["prisoners"], [])


class CelestialChainTests(unittest.TestCase):
    def test_celestials_are_separate_unique_recruits(self):
        self.assertEqual(len(CELESTIALS), 8)
        self.assertTrue(all(profile["race"] == "Celestial" for profile in CELESTIALS.values()))
        state = player_state()
        awarded = {
            "materials": {}, "items": [], "blueprints": [], "recruits": [],
            "perks": [], "transformations": [],
        }

        _award_reward_block(state, {"celestial": "athena"}, awarded, random.Random(1))
        _award_reward_block(state, {"celestial": "athena"}, awarded, random.Random(2))

        self.assertEqual(sum(c.get("source_id") == "celestial:athena" for c in state["characters"]), 1)
        self.assertEqual([entry["kind"] for entry in awarded["recruits"]], ["celestial"])

    def test_chains_have_three_escalating_chapters_and_never_enter_random_pool(self):
        self.assertEqual(len(CELESTIAL_CHAIN_STEPS), 12)
        for chain_id in {mission["chain_id"] for mission in CELESTIAL_CHAIN_STEPS.values()}:
            chapters = sorted(
                (mission for mission in CELESTIAL_CHAIN_STEPS.values() if mission["chain_id"] == chain_id),
                key=lambda mission: mission["chain_step"],
            )
            self.assertEqual([mission["chain_step"] for mission in chapters], [1, 2, 3])
            totals = [sum(mission["rewards"].get("materials", {}).values()) for mission in chapters]
            self.assertEqual(totals, sorted(totals))
            self.assertEqual(len(set(totals)), 3)
            self.assertIsNotNone(chapters[-1]["celestial_reward"])
        for slot in range(100):
            self.assertTrue(all(not MISSION_TEMPLATES[mid].get("chain_only") for mid in _rolled_pool_templates("chain-audit", slot, 2)))

    def test_authored_aftermath_varies_between_replays(self):
        mission = MISSION_TEMPLATES["owl_of_bronze_1"]
        stories = set()
        for seed in range(8):
            state = player_state(scavenging=10)
            analysis = analyze_mission(state, mission, ["player"])
            result = resolve_mission(state, mission, ["player"], analysis, f"story-{seed}", "success")
            stories.add("\n".join(result["story"]))
            self.assertGreaterEqual(len(result["story"]), 3)
        self.assertGreaterEqual(len(stories), 2)


class PrivateChainDatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def test_unlocked_chapter_is_private_and_expires_after_one_day(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        timestamp = 1_000_000
        async with sessions() as session:
            async with session.begin():
                session.add_all([
                    PlayerState(guild_id="chain-db", user_id="owner", display_name="Owner", state=player_state(), updated_at=timestamp),
                    PlayerState(guild_id="chain-db", user_id="other", display_name="Other", state=player_state(), updated_at=timestamp),
                ])
                parent = MissionInstance(
                    id="parent", guild_id="chain-db", template_id="tomb_beyond_sky",
                    pool_slot=1, position=0, spawned_at=timestamp - 10, expires_at=timestamp + 10,
                    duration_seconds=1, status="completed", claimed_by_user_id="owner",
                )
                session.add(parent)
                await session.flush()
                result = {"outcome": "success", "rewards": {"chain_starts": ["owl_of_bronze_1"]}}
                spawned = await _spawn_result_chains(session, parent, "owner", result, timestamp)

            owner_missions = await available_chain_missions(session, "chain-db", "owner", timestamp)
            other_missions = await available_chain_missions(session, "chain-db", "other", timestamp)

        self.assertEqual(len(spawned), 1)
        self.assertEqual(spawned[0].expires_at, timestamp + 24 * 60 * 60)
        self.assertEqual([mission.id for mission in owner_missions], [spawned[0].id])
        self.assertEqual(other_missions, [])
        self.assertEqual(result["chain_unlocked"][0]["mission_id"], spawned[0].id)
        await engine.dispose()


class TacticalCombatTests(unittest.TestCase):
    def test_capture_items_use_visible_seeded_drop_rates(self):
        wins = 0
        misses = 0
        for seed in range(100):
            state = new_game({"name": "Captor", "attributes": {"str": 8, "vit": 8}})
            battle = create_goblin_warcamp_battle(state, ["player"], f"capture-drop-{seed}")
            battle["units"]["gob_chief"].update({
                "alive": True, "conscious": False, "condition": "unconscious", "extracted": True,
            })
            result = {"rewards": {"loot_rolls": []}}
            rewards = _award_capture_loot(state, battle, result)
            roll = result["rewards"]["loot_rolls"][0]
            self.assertEqual(roll["chance"], 20)
            self.assertEqual(roll["possible_item"], "chieftain_command_horn")
            if rewards:
                wins += 1
                self.assertEqual(roll["item"], "chieftain_command_horn")
            else:
                misses += 1
                self.assertIsNone(roll["item"])
        self.assertGreater(wins, 0)
        self.assertGreater(misses, 0)

    def test_captive_cart_generates_stable_unique_mission_characters(self):
        state = new_game({"name": "Reporter", "attributes": {"str": 8, "vit": 8}})
        first = create_captive_cart_battle(state, ["player"], "named-cart")
        repeated = create_captive_cart_battle(state, ["player"], "named-cart")
        another = create_captive_cart_battle(state, ["player"], "another-cart")
        first_names = (
            first["units"]["captive_courier"]["name"],
            first["units"]["cartmaster_vrak"]["name"],
        )
        self.assertEqual(first_names, (
            repeated["units"]["captive_courier"]["name"],
            repeated["units"]["cartmaster_vrak"]["name"],
        ))
        self.assertNotEqual(first_names, (
            another["units"]["captive_courier"]["name"],
            another["units"]["cartmaster_vrak"]["name"],
        ))
        self.assertNotIn("Courier Lysa", first_names)
        self.assertNotIn("Cartmaster Vrak", first_names)

    def test_warcamp_aftermath_names_chief_and_describes_mixed_capture(self):
        state = new_game({"name": "Reporter", "attributes": {"str": 8, "vit": 8}})
        battle = create_goblin_warcamp_battle(state, ["player"], "aftermath-mixed")
        battle["units"]["gob_chief"].update({"alive": False, "conscious": False, "condition": "dead"})
        battle["units"]["gob_archer"].update({"alive": False, "conscious": False, "condition": "dead"})
        for unit_id in ("gob_guard", "gob_horn"):
            battle["units"][unit_id].update({"alive": True, "conscious": False, "condition": "unconscious"})
        battle["auto_captured_ids"] = ["gob_guard", "gob_horn"]
        battle["battlefield_secured"] = True
        details = _battle_outcome_details(battle)
        chief_name = battle["units"]["gob_chief"]["name"]
        self.assertEqual(details["primary_target"], {"id": "gob_chief", "name": chief_name, "resolution": "killed"})
        captured_names = [battle["units"][unit_id]["name"] for unit_id in ("gob_guard", "gob_horn")]
        self.assertEqual(details["enemy_outcome"]["captured"], captured_names)
        story = " ".join(details["aftermath"])
        self.assertIn(chief_name, story)
        for captured_name in captured_names:
            self.assertIn(captured_name, story)
        self.assertTrue(details["recap"])
        self.assertIn(f"{chief_name}: killed.", details["recap"])
        self.assertNotIn(f"{chief_name}: killed.", story)

    def test_warcamp_generates_a_stable_chieftain_from_the_special_portrait_pool(self):
        state = new_game({"name": "Reporter", "attributes": {"str": 8, "vit": 8}})
        first = create_goblin_warcamp_battle(state, ["player"], "named-chief")
        repeated = create_goblin_warcamp_battle(state, ["player"], "named-chief")
        another = create_goblin_warcamp_battle(state, ["player"], "different-chief")
        chief = first["units"]["gob_chief"]
        self.assertEqual(chief["name"], repeated["units"]["gob_chief"]["name"])
        self.assertEqual(chief["portrait"], repeated["units"]["gob_chief"]["portrait"])
        self.assertIn(chief["name"], first["objectives"][0]["name"])
        self.assertIn(chief["name"], first["log"][0])
        self.assertIn(chief["portrait_pool"], {"goblin_male_special", "goblin_female_special"})
        self.assertTrue(chief["portrait"])
        self.assertNotEqual(
            (chief["name"], chief["portrait"]),
            (another["units"]["gob_chief"]["name"], another["units"]["gob_chief"]["portrait"]),
        )

    def test_saved_placeholder_chieftain_is_upgraded_when_battle_is_opened(self):
        state = new_game({"name": "Reporter", "attributes": {"str": 8, "vit": 8}})
        battle = create_goblin_warcamp_battle(state, ["player"], "legacy-chief")
        chief = battle["units"]["gob_chief"]
        chief.update({"name": "Rattle-Crown", "portrait": "", "portrait_full": "", "portrait_pool": ""})
        battle["objectives"][0]["name"] = "Defeat Rattle-Crown"
        battle["log"][0] = "Rattle-Crown is inside the palisade."

        view = battle_view(battle)

        upgraded = view["units"]["gob_chief"]
        self.assertNotEqual(upgraded["name"], "Rattle-Crown")
        self.assertTrue(upgraded["portrait"])
        self.assertIn(upgraded["name"], view["objectives"][0]["name"])
        self.assertIn(upgraded["name"], view["log"][0])

    def battle_party(self):
        state = new_game({
            "name": "Vanguard", "attributes": {"str": 9, "dex": 7, "agi": 8, "vit": 9, "int": 5, "luk": 4},
            "perks": {"combat": "skilled"},
        })
        ally = _make_procedural("goblin_boss", random.Random(4))
        # This fixture tests commanded tactics; disobedience has its own tests.
        ally["loyalty"] = 100
        ally["attributes"].update({"str": 9, "agi": 7, "vit": 9})
        ally["equipment"] = {}
        state["characters"].append(ally)
        return state, ["player", ally["id"]]

    def test_battle_uses_roster_tokens_and_manual_commands(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "manual-battle")
        view = battle_view(battle)
        current = view["units"][view["current_unit_id"]]

        self.assertEqual((view["width"], view["height"]), (8, 8))
        self.assertEqual(current["team"], "player")
        self.assertEqual(current["portrait"], state["characters"][party_ids.index(current["id"])].get("portrait_thumbnail", ""))
        destination = next(tile for tile in view["reachable"] if (tile["x"], tile["y"]) != (current["x"], current["y"]))
        moved = apply_player_command(battle, {"action": "move", **destination})
        self.assertEqual((moved["units"][current["id"]]["x"], moved["units"][current["id"]]["y"]), (destination["x"], destination["y"]))
        self.assertTrue(moved["units"][current["id"]]["moved"])
        alternatives = [tile for tile in moved["reachable"] if (tile["x"], tile["y"]) != (destination["x"], destination["y"])]
        repositioned = apply_player_command(battle, {"action": "move", **alternatives[-1]})
        self.assertEqual(
            (repositioned["units"][current["id"]]["x"], repositioned["units"][current["id"]]["y"]),
            (alternatives[-1]["x"], alternatives[-1]["y"]),
        )
        self.assertEqual(
            (repositioned["movement_path"][-1]["x"], repositioned["movement_path"][-1]["y"]),
            (alternatives[-1]["x"], alternatives[-1]["y"]),
        )
        self.assertEqual(battle["action_count"], 0)
        apply_player_command(battle, {"action": "guard"})
        self.assertNotIn("movement_origin", battle["units"][current["id"]])
        self.assertNotIn("movement_path", battle["units"][current["id"]])
        self.assertEqual(battle["action_count"], 1)

    def test_battle_view_marks_only_actionable_targets(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "target-preview")
        current_id = battle_view(battle)["current_unit_id"]
        current = battle["units"][current_id]
        target = battle["units"]["gob_guard"]
        current.update({"x": 0, "y": 7, "attack_range": 1, "nonlethal_capable": True})
        target.update({"x": 6, "y": 1})
        distant = battle_view(battle)["attack_previews"][target["id"]]
        self.assertIsNone(distant["attack"])
        self.assertIsNone(distant["subdue"])
        target.update({"x": 0, "y": 6})
        adjacent = battle_view(battle)["attack_previews"][target["id"]]
        self.assertIsNotNone(adjacent["attack"])
        self.assertIsNotNone(adjacent["subdue"])

    def test_objective_auto_battle_completes_both_optional_objectives(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "objective-battle")

        auto_resolve(battle, "objective")

        self.assertEqual(battle["status"], "complete")
        self.assertEqual(battle["outcome"], "success")
        self.assertTrue(all(objective["complete"] for objective in battle["objectives"][1:]))

    def test_units_leave_individually_through_map_extraction_tiles(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "extraction-battle")
        current_id = battle_view(battle)["current_unit_id"]
        current = battle["units"][current_id]
        current.update({"x": 1, "y": 7, "exit_ready": True})
        escaped = apply_player_command(battle, {"action": "leave"})
        self.assertTrue(battle["units"][current_id]["extracted"])
        self.assertNotEqual(escaped["current_unit_id"], current_id)

    def test_guild_units_can_leave_through_any_exit(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "shared-exit-battle")
        current_id = battle_view(battle)["current_unit_id"]
        current = battle["units"][current_id]
        current.update({"x": 7, "y": 5, "exit_ready": True})
        self.assertTrue(battle_view(battle)["can_extract"])
        apply_player_command(battle, {"action": "leave"})
        self.assertTrue(current["extracted"])

    def test_reaching_an_exit_requires_holding_until_the_next_activation(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "hold-exit-battle")
        current_id = battle_view(battle)["current_unit_id"]
        current = battle["units"][current_id]
        current.update({"x": 1, "y": 7, "exit_ready": False, "hp": 999, "max_hp": 999})

        self.assertFalse(battle_view(battle)["can_extract"])
        with self.assertRaisesRegex(ValueError, "next activation"):
            apply_player_command(battle, {"action": "leave"})

        apply_player_command(battle, {"action": "end_turn"})
        self.assertTrue(current["exit_ready"])
        battle["turn_index"] = battle["turn_order"].index(current_id)
        current["acted"] = False
        self.assertTrue(battle_view(battle)["can_extract"])

    def test_corpses_do_not_block_reachable_tiles(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "corpse-step-battle")
        current_id = battle_view(battle)["current_unit_id"]
        current = battle["units"][current_id]
        corpse = battle["units"]["gob_guard"]
        current["x"], current["y"] = 1, 7
        corpse.update({"x": 1, "y": 6, "alive": False, "conscious": False, "condition": "dead"})
        self.assertIn({"x": 1, "y": 6}, battle_view(battle)["reachable"])

    def test_nonlethal_takedown_creates_an_unconscious_unit(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "subdue-battle")
        current_id = battle_view(battle)["current_unit_id"]
        current = battle["units"][current_id]
        target = battle["units"]["gob_guard"]
        current.update({"x": 3, "y": 1, "attack": 100, "nonlethal_capable": True})
        target.update({"x": 3, "y": 2, "hp": 1, "evasion": 0})

        apply_player_command(battle, {"action": "subdue", "target_id": target["id"]})

        self.assertTrue(target["alive"])
        self.assertFalse(target["conscious"])
        self.assertEqual(target["condition"], "unconscious")
        self.assertEqual(battle["animation_events"][0]["type"], "melee_attack")

    def test_boss_defeat_opens_victory_choice_and_panics_survivors(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "victory-choice")
        current_id = battle_view(battle)["current_unit_id"]
        current = battle["units"][current_id]
        chief = battle["units"]["gob_chief"]
        current.update({"x": 3, "y": 1, "attack": 100})
        chief.update({"x": 4, "y": 1, "hp": 1, "evasion": 0})

        view = apply_player_command(battle, {"action": "attack", "target_id": chief["id"]})

        self.assertEqual(view["status"], "active")
        self.assertTrue(view["battle_won"])
        self.assertTrue(view["decision_pending"])
        self.assertIsNone(view["current_unit_id"])
        survivors = [unit for unit in view["units"].values() if unit["team"] == "enemy" and unit["id"] != chief["id"]]
        self.assertTrue(all(unit["panicked"] for unit in survivors))

        pursued = apply_player_command(battle, {"action": "continue_pursuit"})
        self.assertEqual(pursued["victory_phase"], "pursuit")
        self.assertFalse(pursued["decision_pending"])
        self.assertTrue(pursued["animation_events"])
        self.assertTrue(all(event["points"] for event in pursued["animation_events"]))
        self.assertTrue(any(event["unit_id"] in {unit["id"] for unit in survivors} for event in pursued["animation_events"]))

    def test_claiming_victory_auto_recovers_corpses(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "auto-loot")
        chief = battle["units"]["gob_chief"]
        guard = battle["units"]["gob_guard"]
        for unit in (chief, guard):
            unit.update({"hp": 0, "alive": False, "conscious": False, "condition": "dead"})
        battle["decision_pending"] = False
        battle["battle_won"] = True

        completed = apply_player_command(battle, {"action": "claim_victory"})

        self.assertEqual(completed["status"], "complete")
        self.assertEqual(set(completed["auto_looted_ids"]), {chief["id"], guard["id"]})

    def test_unconscious_units_can_be_carried_and_extracted(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "carry-battle")
        current_id = battle_view(battle)["current_unit_id"]
        carrier = battle["units"][current_id]
        body = battle["units"]["gob_guard"]
        carrier.update({"x": 1, "y": 7, "hp": 999, "max_hp": 999})
        body.update({"x": 1, "y": 6, "hp": 0, "conscious": False, "condition": "unconscious"})

        apply_player_command(battle, {"action": "carry", "target_id": body["id"]})

        self.assertEqual(carrier["carrying"], body["id"])
        self.assertEqual(body["carried_by"], carrier["id"])
        self.assertFalse(carrier["acted"])
        self.assertEqual(battle_view(battle)["current_unit_id"], current_id)
        self.assertEqual(_movement_limit(carrier), max(1, carrier["move"] - carrier["carried_payload_penalty"]))

        battle["turn_index"] = battle["turn_order"].index(current_id)
        carrier["acted"] = False
        carrier.update({"x": 1, "y": 7, "exit_ready": True})
        action_count = battle["action_count"]
        extracted_body = apply_player_command(battle, {"action": "extract_body"})
        self.assertTrue(extracted_body["units"][body["id"]]["extracted"])
        self.assertFalse(extracted_body["units"][carrier["id"]].get("extracted", False))
        self.assertEqual(extracted_body["current_unit_id"], current_id)
        self.assertEqual(battle["action_count"], action_count)

        body.update({"extracted": False, "extracted_with": None, "carried_by": carrier["id"], "x": 1, "y": 7})
        carrier["carrying"] = body["id"]

        battle["turn_index"] = battle["turn_order"].index(current_id)
        carrier["acted"] = False
        dropped = apply_player_command(battle, {"action": "drop"})
        self.assertIsNone(dropped["units"][carrier["id"]]["carrying"])
        self.assertIsNone(dropped["units"][body["id"]]["carried_by"])

        battle["turn_index"] = battle["turn_order"].index(current_id)
        carrier["acted"] = False
        carrier.update({"x": 1, "y": 7, "exit_ready": True})
        body["x"], body["y"] = 1, 6
        apply_player_command(battle, {"action": "carry", "target_id": body["id"]})
        battle["turn_index"] = battle["turn_order"].index(current_id)
        carrier["acted"] = False
        escaped = apply_player_command(battle, {"action": "leave"})
        self.assertTrue(escaped["units"][carrier["id"]]["extracted"])
        self.assertTrue(escaped["units"][body["id"]]["extracted"])
        self.assertEqual(escaped["units"][body["id"]]["extracted_with"], carrier["id"])

    def test_portable_object_can_be_picked_up_and_thrown_at_an_enemy(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "throw-crate")
        current_id = battle_view(battle)["current_unit_id"]
        thrower = battle["units"][current_id]
        other = battle["units"][next(unit_id for unit_id in party_ids if unit_id != current_id)]
        thrower.update({"x": 0, "y": 7, "hp": 999, "max_hp": 999, "strength": 9})
        other.update({"x": 2, "y": 7})

        actions = {entry["id"]: entry for entry in battle_view(battle)["context_actions"]}
        self.assertIn("pickup:supply_crate", actions)
        self.assertIn({"x": 0, "y": 6}, battle_view(battle)["reachable"])
        picked_up = apply_player_command(battle, actions["pickup:supply_crate"]["command"])
        self.assertEqual(thrower["carrying_object"], "supply_crate")
        self.assertEqual(thrower["carried_payload_penalty"], 2)
        self.assertEqual(_movement_limit(thrower), max(1, thrower["move"] - 2))
        self.assertFalse(thrower["acted"])
        self.assertEqual(picked_up["current_unit_id"], current_id)

        battle["turn_index"] = battle["turn_order"].index(current_id)
        thrower.update({"acted": False, "x": 1, "y": 5})
        target = battle["units"]["gob_guard"]
        target.update({"x": 1, "y": 4, "hp": 18, "max_hp": 18})
        profile = battle_view(battle)["throw_profile"]
        self.assertEqual((profile["strength"], profile["weight"], profile["range"]), (9, 4, 1))
        self.assertIn(target["id"], profile["target_ids"])

        apply_player_command(battle, {"action": "throw", "target_id": target["id"]})
        crate = battle["objects"]["supply_crate"]
        self.assertIsNone(thrower["carrying_object"])
        self.assertEqual(crate["state"], "broken")
        self.assertLess(target["hp"], 18)

    def test_body_throw_range_and_impact_scale_with_strength_and_weight(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "throw-body")
        current_id = battle_view(battle)["current_unit_id"]
        thrower = battle["units"][current_id]
        body = battle["units"]["gob_archer"]
        target = battle["units"]["gob_horn"]
        thrower.update({"x": 3, "y": 4, "hp": 999, "max_hp": 999, "carrying": body["id"], "strength": 5})
        body.update({"x": 3, "y": 4, "hp": 6, "alive": True, "conscious": False, "condition": "unconscious", "carried_by": current_id, "weight": 2})
        target.update({"x": 6, "y": 4, "hp": 15, "max_hp": 15})

        weak_profile = battle_view(battle)["throw_profile"]
        thrower["strength"] = 13
        strong_profile = battle_view(battle)["throw_profile"]
        self.assertGreater(strong_profile["range"], weak_profile["range"])
        self.assertGreater(strong_profile["damage"], weak_profile["damage"])
        self.assertEqual(strong_profile["weight"], body["weight"])
        self.assertIn(target["id"], strong_profile["target_ids"])

        apply_player_command(battle, {"action": "throw", "target_id": target["id"]})
        self.assertIsNone(thrower["carrying"])
        self.assertIsNone(body["carried_by"])
        self.assertEqual((body["x"], body["y"]), (7, 4))
        self.assertLess(target["hp"], 15)
        self.assertLess(body["hp"], 6)

    def test_captive_cart_rescue_triggers_extraction_victory_choice(self):
        state, party_ids = self.battle_party()
        battle = create_captive_cart_battle(state, party_ids, "rescue-courier")
        current_id = battle_view(battle)["current_unit_id"]
        carrier = battle["units"][current_id]
        courier = battle["units"]["captive_courier"]
        carrier.update({"x": 0, "y": 4, "carrying": courier["id"], "carried_payload_penalty": 1, "exit_ready": True})
        courier.update({"x": 0, "y": 4, "carried_by": current_id})

        view = apply_player_command(battle, {"action": "extract_body"})

        self.assertTrue(courier["extracted"])
        self.assertTrue(view["objectives"][0]["complete"])
        self.assertTrue(view["battle_won"])
        self.assertTrue(view["decision_pending"])
        self.assertEqual(view["victory_title"], f"{courier['name']} is safe.")

        completed = apply_player_command(battle, {"action": "claim_victory"})
        self.assertEqual(completed["outcome"], "success")

    def test_captive_cart_complete_recovery_is_critical_success(self):
        state, party_ids = self.battle_party()
        battle = create_captive_cart_battle(state, party_ids, "complete-capture")
        current_id = battle_view(battle)["current_unit_id"]
        battle["units"]["captive_courier"].update({"extracted": True})
        battle["units"]["cartmaster_vrak"].update({
            "hp": 0, "alive": True, "conscious": False, "condition": "unconscious", "extracted": True,
        })
        battle["objects"]["dispatch_satchel"]["state"] = "extracted"
        battle["turn_index"] = battle["turn_order"].index(current_id)

        view = apply_player_command(battle, {"action": "end_turn"})
        self.assertTrue(all(objective["complete"] for objective in view["objectives"]))
        self.assertTrue(view["decision_pending"])

        completed = apply_player_command(battle, {"action": "claim_victory"})
        self.assertEqual(completed["outcome"], "critical_success")

    def test_securing_captive_cart_field_recovers_rescue_capture_and_satchel(self):
        state, party_ids = self.battle_party()
        battle = create_captive_cart_battle(state, party_ids, "secure-cart-field")
        current_id = battle_view(battle)["current_unit_id"]
        for unit in battle["units"].values():
            if unit.get("team") != "enemy":
                continue
            unit.update({"hp": 0, "conscious": False})
            if unit["id"] == "cartmaster_vrak":
                unit.update({"alive": True, "condition": "unconscious"})
            else:
                unit.update({"alive": False, "condition": "dead"})
        battle["turn_index"] = battle["turn_order"].index(current_id)

        view = apply_player_command(battle, {"action": "end_turn"})

        self.assertTrue(view["battlefield_secured"])
        self.assertTrue(view["units"]["captive_courier"]["extracted"])
        self.assertTrue(view["units"]["cartmaster_vrak"]["extracted"])
        self.assertEqual(view["objects"]["dispatch_satchel"]["state"], "extracted")
        self.assertTrue(all(objective["complete"] for objective in view["objectives"]))

    def test_captive_cart_courier_death_is_critical_failure(self):
        state, party_ids = self.battle_party()
        battle = create_captive_cart_battle(state, party_ids, "lost-courier")
        current_id = battle_view(battle)["current_unit_id"]
        battle["units"]["captive_courier"].update({
            "hp": 0, "alive": False, "conscious": False, "condition": "dead",
        })
        battle["turn_index"] = battle["turn_order"].index(current_id)

        view = apply_player_command(battle, {"action": "end_turn"})

        self.assertEqual(view["status"], "complete")
        self.assertEqual(view["outcome"], "critical_failure")
        self.assertFalse(view["decision_pending"])

    def test_retreat_all_paths_every_party_member_to_an_exit(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "retreat-all")

        escaped = apply_player_command(battle, {"action": "retreat_all"})

        self.assertEqual(escaped["status"], "complete")
        self.assertEqual(escaped["outcome"], "failure")
        self.assertTrue(all(battle["units"][unit_id]["extracted"] for unit_id in party_ids))

    def test_plain_melee_has_no_power_strike_skill(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "no-power-strike")
        self.assertIsNone(battle["units"]["player"]["special"])

    def test_context_actions_describe_available_objects_and_body_handling(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "context-actions")
        current_id = battle_view(battle)["current_unit_id"]
        current = battle["units"][current_id]
        body = battle["units"]["gob_guard"]
        current.update({"x": 4, "y": 5})
        body.update({"x": 4, "y": 4, "hp": 0, "alive": True, "conscious": False, "condition": "unconscious"})

        view = battle_view(battle)
        actions = {entry["id"]: entry for entry in view["context_actions"]}
        self.assertIn("open_prisoner_pen", actions)
        self.assertIn(f"carry:{body['id']}", actions)
        self.assertEqual(actions[f"carry:{body['id']}"]["cost"], "Free action")
        self.assertTrue(all(entry.get("description") and entry.get("command") for entry in actions.values()))

        current.update({"x": 1, "y": 7, "carrying": body["id"], "exit_ready": True})
        body.update({"x": 1, "y": 7, "carried_by": current_id})
        exit_actions = {entry["id"]: entry for entry in battle_view(battle)["context_actions"]}
        self.assertEqual(exit_actions["extract_carried"]["cost"], "Free action")
        self.assertIn("drop_carried", exit_actions)

    def test_enemy_and_corpse_on_same_tile_expose_both_attack_and_body_actions(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "stacked-body-actions")
        current_id = battle_view(battle)["current_unit_id"]
        current = battle["units"][current_id]
        enemy = battle["units"]["gob_guard"]
        corpse = battle["units"]["gob_archer"]
        current.update({"x": 3, "y": 4, "attack_range": 1})
        enemy.update({"x": 4, "y": 4, "hp": 18, "alive": True, "conscious": True, "condition": "active"})
        corpse.update({"x": 4, "y": 4, "hp": 0, "alive": False, "conscious": False, "condition": "dead"})

        view = battle_view(battle)
        self.assertIsNotNone(view["attack_previews"][enemy["id"]]["attack"])
        self.assertIn(f"carry:{corpse['id']}", {entry["id"] for entry in view["context_actions"]})

    def test_low_loyalty_wounded_outnumbered_ally_panics_toward_exit(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "party-panic")
        ally_id = party_ids[1]
        ally = battle["units"][ally_id]
        ally.update({"loyalty": 20, "hp": 1, "player_avatar": False, "x": 2, "y": 5})
        battle["turn_order"] = ["player", ally_id, "gob_chief", "gob_guard", "gob_archer", "gob_horn"]
        battle["turn_index"] = 0

        apply_player_command(battle, {"action": "end_turn"})

        self.assertTrue(ally["panicked"])
        self.assertTrue(ally.get("extracted") or ally["y"] > 5)

    def test_elevation_changes_ballistic_attacks_but_not_explicit_magic(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "elevation-battle")
        attacker = battle["units"][party_ids[0]]
        target = battle["units"]["gob_chief"]
        attacker["x"], attacker["y"] = 3, 1
        target["x"], target["y"] = 4, 1
        uphill = _attack_preview(battle, attacker, target, "ballistic")
        downhill = _attack_preview(battle, target, attacker, "ballistic")
        magic = _attack_preview(battle, attacker, target, "ignore")
        self.assertEqual((uphill["chance"], uphill["damage_bonus"]), (63, 0))
        self.assertEqual((downhill["chance"], downhill["damage_bonus"]), (98, 1))
        self.assertEqual((magic["chance"], magic["damage_bonus"]), (96, 0))
        self.assertEqual(uphill["target_evasion"], 15)

    def test_elevation_climbing_uses_weighted_cost_and_two_level_steps(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "climb-battle")
        current_id = battle_view(battle)["current_unit_id"]
        unit = battle["units"][current_id]
        unit["x"], unit["y"], unit["move"] = 0, 1, 8
        first_climb = apply_player_command(battle, {"action": "move", "x": 0, "y": 0})
        self.assertEqual(first_climb["movement_path"][-1]["cost"], 4)
        summit = apply_player_command(battle, {"action": "move", "x": 1, "y": 0})
        self.assertEqual(summit["movement_path"][-1]["cost"], 8)

        blocked = create_goblin_warcamp_battle(state, party_ids, "steep-climb-battle")
        current_id = battle_view(blocked)["current_unit_id"]
        unit = blocked["units"][current_id]
        unit["x"], unit["y"], unit["move"] = 0, 1, 8
        next(tile for tile in blocked["elevation"] if tile["x"] == 0 and tile["y"] == 0)["height"] = 3
        self.assertNotIn({"x": 0, "y": 0}, battle_view(blocked)["reachable"])

    def test_void_tiles_are_data_driven_and_never_reachable(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "void-map")
        current_id = battle_view(battle)["current_unit_id"]
        unit = battle["units"][current_id]
        unit["x"], unit["y"], unit["move"] = 1, 6, 4
        battle["void_tiles"] = [{"x": 1, "y": 5}, {"x": 2, "y": 5}]

        view = battle_view(battle)

        self.assertEqual((view["width"], view["height"]), (8, 8))
        self.assertNotIn({"x": 1, "y": 5}, view["reachable"])
        self.assertNotIn({"x": 2, "y": 5}, view["reachable"])

    def test_water_costs_extra_movement_and_extinguishes_burn_on_commit(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "water-rules")
        current_id = battle_view(battle)["current_unit_id"]
        unit = battle["units"][current_id]
        other = battle["units"][next(unit_id for unit_id in party_ids if unit_id != current_id)]
        unit.update({"x": 3, "y": 7, "move": 4, "statuses": [{"id": "burn", "duration": 2}]})
        other.update({"x": 0, "y": 6})

        moved = apply_player_command(battle, {"action": "move", "x": 4, "y": 7})
        self.assertEqual(moved["movement_path"][-1]["cost"], 2)
        self.assertTrue(any(status["id"] == "burn" for status in unit["statuses"]))

        apply_player_command(battle, {"action": "end_turn"})
        self.assertFalse(any(status["id"] == "burn" for status in unit["statuses"]))
        self.assertTrue(any("shallow water" in line for line in battle["log"]))

    def test_pits_require_flight(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "pit-rules")
        current_id = battle_view(battle)["current_unit_id"]
        unit = battle["units"][current_id]
        other = battle["units"][next(unit_id for unit_id in party_ids if unit_id != current_id)]
        unit.update({"x": 6, "y": 6, "move": 3})
        other.update({"x": 0, "y": 6})

        self.assertNotIn({"x": 7, "y": 6}, battle_view(battle)["reachable"])
        unit["movement_type"] = "flying"
        self.assertIn({"x": 7, "y": 6}, battle_view(battle)["reachable"])

    def test_palisade_is_a_normal_attack_target_and_becomes_traversable_rubble(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "break-palisade")
        current_id = battle_view(battle)["current_unit_id"]
        unit = battle["units"][current_id]
        unit.update({"x": 0, "y": 4, "attack": 30})
        palisade = next(tile for tile in battle["terrain"] if tile["id"] == "palisade_0")

        view = battle_view(battle)
        self.assertIn("palisade_0", view["terrain_targets"])
        self.assertFalse(any(entry["id"].startswith("break:") for entry in view["context_actions"]))
        apply_player_command(battle, {"action": "attack", "target_id": "palisade_0"})

        self.assertTrue(palisade["destroyed"])
        self.assertEqual(palisade["kind"], "rubble")
        self.assertFalse(palisade["blocking"])
        self.assertEqual(palisade["movement_cost"], 2)

    def test_ranged_weapons_can_attack_destructible_terrain_at_weapon_range(self):
        state, party_ids = self.battle_party()
        battle = create_goblin_warcamp_battle(state, party_ids, "ranged-palisade")
        current_id = battle_view(battle)["current_unit_id"]
        unit = battle["units"][current_id]
        unit.update({"x": 0, "y": 7, "attack": 30, "attack_range": 4, "attack_elevation_rule": "ballistic"})
        other = battle["units"][next(unit_id for unit_id in party_ids if unit_id != current_id)]
        other.update({"x": 2, "y": 7})

        self.assertIn("palisade_0", battle_view(battle)["terrain_targets"])
        apply_player_command(battle, {"action": "attack", "target_id": "palisade_0"})
        self.assertTrue(next(tile for tile in battle["terrain"] if tile["id"] == "palisade_0")["destroyed"])

    def test_status_catalog_is_presentable_and_extensible(self):
        expected = {"stun", "sleep", "poison", "bleed", "charm", "confuse", "berserk", "freeze", "burn", "blind", "bind", "slow", "paralyze", "mute"}
        self.assertTrue(expected.issubset(STATUS_DEFINITIONS))
        self.assertTrue(all(entry.get("icon") and entry.get("description") for entry in STATUS_DEFINITIONS.values()))

    def test_balanced_and_objective_tactics_make_different_tradeoffs(self):
        state, party_ids = self.battle_party()
        balanced = create_goblin_warcamp_battle(state, party_ids, "same-seed")
        objective = deepcopy(balanced)

        auto_resolve(balanced, "balanced")
        auto_resolve(objective, "objective")

        self.assertFalse(any(item["complete"] for item in balanced["objectives"][1:]))
        self.assertTrue(all(item["complete"] for item in objective["objectives"][1:]))


class TacticalCombatDatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def test_debug_resolve_now_uses_the_normal_timed_mission_roll(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        state = new_game({"name": "Timer Tester", "attributes": {"agi": 8, "luk": 6}})
        async with sessions() as session:
            async with session.begin():
                session.add(PlayerState(guild_id="timer-db", user_id="tester", display_name="Tester", state=state, updated_at=now_ts()))
                session.add(MissionInstance(
                    id="timer-mission", guild_id="timer-db", template_id="fallen_orchard",
                    pool_slot=1, position=0, spawned_at=now_ts(), expires_at=now_ts() + 1000,
                    duration_seconds=600, status="available",
                ))
            async with session.begin():
                claimed = await claim_instance(session, "timer-db", "tester", "Tester", "timer-mission", ["player"])
            self.assertEqual(claimed.status, "claimed")
            self.assertLessEqual(claimed.completes_at, now_ts())
            async with session.begin():
                completed = await debug_resolve_now_instance(session, "timer-db", "tester", "timer-mission")
            saved = await session.get(PlayerState, {"guild_id": "timer-db", "user_id": "tester"})
        self.assertEqual(completed.status, "completed")
        self.assertIn(completed.result["outcome"], {"critical_failure", "failure", "success", "critical_success"})
        self.assertFalse(completed.result.get("debug_forced", False))
        self.assertEqual(saved.state["characters"][0]["status"], "idle")
        await engine.dispose()

    async def test_investigation_branch_deploys_bodyguard_without_adding_to_roll(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        state = new_game({"name": "Investigator", "stats": {"survival": 8}, "attributes": {"dex": 8}})
        guard = deepcopy(state["characters"][0])
        guard.update({"id": "guard", "name": "Bodyguard", "is_player": False, "status": "idle"})
        state["characters"].append(guard)
        branch = MISSION_TEMPLATES["goblin_smoke_signals"]["branching_encounter"]
        old_chance = branch["trigger_chance"]
        branch["trigger_chance"] = 100
        scene_seed=next(f'branch-mission-{i}' for i in range(100) if 1<random.Random(f'branch-mission-{i}:scene:signals:0:follow').randint(1,20)<6)
        try:
            async with sessions() as session:
                async with session.begin():
                    session.add(PlayerState(guild_id="branch-db", user_id="scout", display_name="Scout", state=state, updated_at=now_ts()))
                    session.add(MissionInstance(
                        id=scene_seed, guild_id="branch-db", template_id="goblin_smoke_signals",
                        pool_slot=1, position=0, spawned_at=now_ts(), expires_at=now_ts() + 1000,
                        duration_seconds=60, status="available",
                    ))
                async with session.begin():
                    mission = await claim_instance(
                        session, "branch-db", "scout", "Scout", scene_seed, ["player"], None, ["guard"],
                    )
                self.assertEqual(mission.status, 'decision')
                async with session.begin():
                    await choose_decision_instance(session,'branch-db','scout',mission.id,'signals',0,'follow')
                self.assertEqual(mission.status, "battle")
                self.assertEqual(mission.analysis["support_bonus"], 0)
                self.assertEqual(mission.analysis["mission_party_ids"], ["player"])
                self.assertEqual(mission.analysis["bodyguard_ids"], ["guard"])
                self.assertEqual(set(mission.analysis["battle"]["units"]), {"player", "guard", "signal_captain", "signal_runner", "hedgerow_knife"})
                async with session.begin():
                    metadata = deepcopy(mission.analysis)
                    for unit in metadata["battle"]["units"].values():
                        if unit["team"] == "enemy":
                            unit.update({"hp": 0, "alive": False, "conscious": False, "condition": "dead"})
                    mission.analysis = metadata
                async with session.begin():
                    await update_battle_instance(session, "branch-db", "scout", mission.id, command={"action": "end_turn"})
                async with session.begin():
                    _, result = await update_battle_instance(session, "branch-db", "scout", mission.id, command={"action": "claim_victory"})
                saved = await session.get(PlayerState, {"guild_id": "branch-db", "user_id": "scout"})
                statuses = {character["id"]: character["status"] for character in saved.state["characters"]}
            self.assertEqual(result["outcome"], "critical_success")
            self.assertEqual(statuses, {"player": "idle", "guard": "idle"})
            self.assertIn("marked farm chart", " ".join(result["story"]).lower())
        finally:
            branch["trigger_chance"] = old_chance
            await engine.dispose()

    async def test_captive_cart_debug_battle_resolves_rescue_capture_and_recovery_report(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        state = new_game({"name": "Rescue Tester", "attributes": {"str": 10, "vit": 9}})
        async with sessions() as session:
            async with session.begin():
                session.add(PlayerState(
                    guild_id="rescue-combat", user_id="tester", display_name="Tester",
                    state=state, updated_at=now_ts(),
                ))
            async with session.begin():
                mission = await debug_start_battle(
                    session, "rescue-combat", "tester", "Tester", "goblin_captive_cart",
                )
                metadata = deepcopy(mission.analysis)
                battle = metadata["battle"]
                courier_name = battle["units"]["captive_courier"]["name"]
                cartmaster_name = battle["units"]["cartmaster_vrak"]["name"]
                battle["units"]["captive_courier"]["extracted"] = True
                battle["units"]["cartmaster_vrak"].update({
                    "hp": 0, "alive": True, "conscious": False, "condition": "unconscious", "extracted": True,
                })
                battle["objects"]["dispatch_satchel"]["state"] = "extracted"
                mission.analysis = metadata
            async with session.begin():
                await update_battle_instance(
                    session, "rescue-combat", "tester", mission.id, command={"action": "end_turn"},
                )
            async with session.begin():
                _, result = await update_battle_instance(
                    session, "rescue-combat", "tester", mission.id, command={"action": "claim_victory"},
                )
            async with session.begin():
                saved_player = (await session.execute(select(PlayerState).where(
                    PlayerState.guild_id == "rescue-combat", PlayerState.user_id == "tester",
                ))).scalar_one()
                saved_state = deepcopy(saved_player.state)

        self.assertEqual(result["outcome"], "critical_success")
        self.assertEqual(result["battle_report"]["rescued"], [courier_name])
        self.assertEqual(result["battle_report"]["captured"], [cartmaster_name])
        self.assertEqual(result["battle_report"]["recovered_objects"], ["Stolen Dispatch Satchel"])
        self.assertEqual(result["battle_report"]["new_prisoners"], [cartmaster_name])
        capture_roll = next(
            roll for roll in result["rewards"]["loot_rolls"]
            if roll.get("possible_item") == "cartmaster_route_book"
        )
        self.assertEqual(capture_roll["chance"], 55)
        self.assertEqual(capture_roll["source"], f"Captured {cartmaster_name} alive")
        self.assertEqual(saved_state["prisoners"][0]["name"], cartmaster_name)
        self.assertEqual(saved_state["prisoners"][0]["holding"], "temporary_stockade")
        inventory_ids = [item["item_id"] for item in saved_state["inventory"]]
        self.assertEqual("cartmaster_route_book" in inventory_ids, bool(capture_roll["item"]))
        await engine.dispose()

    async def test_secured_corpses_award_body_scaled_loot_without_materials(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        state = new_game({"name": "Loot Tester", "attributes": {"str": 9, "vit": 9}})
        async with sessions() as session:
            async with session.begin():
                session.add(PlayerState(
                    guild_id="loot-combat", user_id="tester", display_name="Tester",
                    state=state, updated_at=now_ts(),
                ))
            async with session.begin():
                mission = await debug_start_goblin_battle(session, "loot-combat", "tester", "Tester")
                metadata = deepcopy(mission.analysis)
                battle = metadata["battle"]
                for unit_id in ("gob_chief", "gob_guard"):
                    battle["units"][unit_id].update({
                        "hp": 0, "alive": False, "conscious": False, "condition": "dead",
                    })
                battle.update({"battle_won": True, "decision_pending": False})
                mission.analysis = metadata
            async with session.begin():
                _, result = await update_battle_instance(
                    session, "loot-combat", "tester", mission.id,
                    command={"action": "claim_victory"},
                )

        self.assertEqual(result["rewards"]["materials"], {})
        self.assertEqual(len(result["battle_report"]["corpse_loot"]), 2)
        self.assertGreaterEqual(result["rewards"]["gold"], 6)
        await engine.dispose()

    async def test_debug_launcher_builds_and_cleans_up_a_temporary_party(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        state = new_game({"name": "Solo Tester", "attributes": {"str": 8, "vit": 8}})
        async with sessions() as session:
            async with session.begin():
                session.add(PlayerState(
                    guild_id="debug-combat", user_id="tester", display_name="Tester",
                    state=state, updated_at=now_ts(),
                ))
            async with session.begin():
                mission = await debug_start_goblin_battle(
                    session, "debug-combat", "tester", "Tester",
                )
                resumed = await debug_start_goblin_battle(
                    session, "debug-combat", "tester", "Tester",
                )
            self.assertEqual(resumed.id, mission.id)
            self.assertEqual(len(mission.party_ids), 2)
            self.assertTrue((mission.analysis or {}).get("debug_battle"))
            self.assertEqual(len((mission.analysis or {}).get("debug_temporary_character_ids", [])), 1)
            async with session.begin():
                await update_battle_instance(
                    session, "debug-combat", "tester", mission.id,
                    auto="balanced", resolve_all=True,
                )
            player = await session.get(PlayerState, {"guild_id": "debug-combat", "user_id": "tester"})
        self.assertFalse(any(char.get("source_kind") == "debug" for char in player.state["characters"]))
        await engine.dispose()

    async def test_claim_pauses_timer_and_auto_battle_resolves_normal_rewards(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        state = new_game({
            "name": "Vanguard", "attributes": {"str": 9, "dex": 7, "agi": 8, "vit": 9, "int": 5, "luk": 4},
            "perks": {"combat": "skilled"},
        })
        ally = _make_procedural("goblin_boss", random.Random(8))
        ally["attributes"].update({"str": 9, "agi": 7, "vit": 9})
        ally["equipment"] = {}
        state["characters"].append(ally)
        state["mission_rank"] = "D"
        party_ids = ["player", ally["id"]]
        async with sessions() as session:
            async with session.begin():
                session.add(PlayerState(guild_id="combat-db", user_id="fighter", display_name="Fighter", state=state, updated_at=now_ts()))
                session.add(MissionInstance(
                    id="combat-mission", guild_id="combat-db", template_id="goblin_warcamp",
                    pool_slot=1, position=0, spawned_at=now_ts(), expires_at=now_ts() + 1000,
                    duration_seconds=300, status="available",
                ))
            async with session.begin():
                claimed = await claim_instance(
                    session, "combat-db", "fighter", "Fighter", "combat-mission", party_ids,
                    {"tank": "player", "dps": ally["id"]},
                )
            self.assertEqual(claimed.status, 'decision')
            async with session.begin():
                await choose_decision_instance(session,'combat-db','fighter','combat-mission','approach',0,'direct')
            self.assertEqual(claimed.status, "battle")
            self.assertIsNone(claimed.completes_at)
            async with session.begin():
                battle, result = await update_battle_instance(
                    session, "combat-db", "fighter", "combat-mission",
                    auto="balanced", resolve_all=True,
                )
            player = await session.get(PlayerState, {"guild_id": "combat-db", "user_id": "fighter"})
            mission = await session.get(MissionInstance, "combat-mission")

        self.assertEqual(battle["status"], "complete")
        self.assertEqual(mission.status, "completed")
        self.assertIn(result["outcome"], {"success", "critical_success"})
        self.assertIn("battle_report", result)
        self.assertTrue(all(character["status"] == "idle" for character in player.state["characters"]))
        await engine.dispose()


class ExpandedChampionTests(unittest.TestCase):
    def test_catalog_contains_exactly_one_hundred_unique_champions(self):
        self.assertEqual(len(CATALOG), 100)
        self.assertEqual(len(EXPANDED_CHAMPIONS), 100)
        self.assertEqual(len({entry[0] for entry in CATALOG}), 100)
        self.assertEqual(sum(profile["gender"] == "female" for profile in EXPANDED_CHAMPIONS.values()), 88)
        self.assertTrue(all(profile["traits"][-1] in STANDALONE_PERKS for profile in EXPANDED_CHAMPIONS.values()))

    def test_lower_tier_catalog_has_one_hundred_twenty_unique_women(self):
        self.assertEqual(len(LOWER_TIER_CATALOG), 120)
        self.assertEqual(len(LOWER_TIER_CHAMPIONS), 120)
        self.assertEqual(len({entry[0] for entry in LOWER_TIER_CATALOG}), 120)
        self.assertTrue(all(profile["gender"] == "female" for profile in LOWER_TIER_CHAMPIONS.values()))
        self.assertGreaterEqual(sum(profile["champion_rank"] in {"C", "D", "E"} for profile in LOWER_TIER_CHAMPIONS.values()), 50)
        self.assertEqual(LOWER_TIER_CHAMPIONS["hana_inuzuka"]["champion_rank"], "E")
        self.assertTrue(all(profile["traits"][-1] in STANDALONE_PERKS for profile in LOWER_TIER_CHAMPIONS.values()))

    def test_collection_rank_is_popularity_based(self):
        self.assertEqual(EXPANDED_CHAMPIONS["marin_kitagawa"]["champion_rank"], "S")
        self.assertEqual(EXPANDED_CHAMPIONS["yuki_tsukumo"]["champion_rank"], "C")

    def test_s_rank_role_template_is_stronger_than_lower_rank_version(self):
        lower = EXPANDED_CHAMPIONS["aira_shiratori"]
        upper = EXPANDED_CHAMPIONS["levi_ackerman"]
        self.assertEqual(lower["specialty"], upper["specialty"])
        self.assertGreater(sum(upper["attributes"].values()), sum(lower["attributes"].values()))

    def test_owned_champions_are_removed_from_random_pool(self):
        state = player_state()
        state["characters"].extend({"source_id": champion_id} for champion_id in CHAMPIONS if champion_id != "frieren")
        self.assertEqual(_random_champion(state, "S", random.Random(4)), "frieren")

    def test_s_rank_missions_can_find_a_champion(self):
        mission = MISSION_TEMPLATES["deep_expedition"]
        found = None
        for seed in range(200):
            state = player_state(scavenging=10)
            result = resolve_mission(state, mission, ["player"], analyze_mission(state, mission, ["player"]), f"champion-{seed}", "success")
            champions = [entry for entry in result["rewards"]["recruits"] if entry["kind"] == "champion"]
            if champions:
                found = champions[0]
                break
        self.assertIsNotNone(found)
        self.assertIn(found["profile"], CHAMPIONS)


class ForcedPoolDatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def test_forced_pool_instances_are_immediately_available(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            async with session.begin():
                session.add(PlayerState(guild_id="forced-db", user_id="player", display_name="Tester", state=player_state(), updated_at=now_ts()))
            slot = force_pool_refresh("forced-db", "ashen_procession")
            async with session.begin():
                missions, created = await ensure_pool(session, "forced-db")

        self.assertTrue(created)
        self.assertTrue(missions)
        self.assertTrue(all(mission.pool_slot == slot for mission in missions))
        self.assertTrue(all(mission.expires_at > now_ts() for mission in missions))
        self.assertEqual(pool_event("forced-db", slot)["id"], "ashen_procession")
        await engine.dispose()

    async def test_completed_mission_delivers_private_consequence_without_board_refresh(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        refresh = 1_000_800
        async with sessions() as session:
            async with session.begin():
                session.add(PlayerState(
                    guild_id="world-db", user_id="scout", display_name="Mara",
                    state=player_state(), updated_at=refresh - 100,
                ))
                session.add(MissionInstance(
                    id="world-source", guild_id="world-db", template_id="highway_ambush",
                    pool_slot=refresh - 1800, position=0, spawned_at=refresh - 1800,
                    expires_at=refresh - 900, duration_seconds=1, status="completed",
                    claimed_by_user_id="scout", claimed_by_name="Mara", resolved_at=refresh - 100,
                    result={"mission": "Highway Ambush", "board_followups": [{"template_id": "black_banner_ledger"}]},
                ))
            async with session.begin():
                missions, _ = await ensure_pool(session, "world-db", refresh + 1)
                private = await available_chain_missions(session, "world-db", "scout", refresh + 1)
                repeated = await available_chain_missions(session, "world-db", "scout", refresh + 2)
                strangers = await available_chain_missions(session, "world-db", "someone-else", refresh + 2)

        self.assertFalse(any(row.template_id == "black_banner_ledger" for row in missions))
        self.assertEqual(len(private), 1)
        self.assertEqual([row.id for row in private], [row.id for row in repeated])
        self.assertEqual(strangers, [])
        consequence = private[0]
        self.assertEqual(consequence.template_id, "black_banner_ledger")
        self.assertEqual(consequence.analysis["world_trigger_source_id"], "world-source")
        self.assertEqual(consequence.analysis["world_triggered_by_name"], "Mara")
        self.assertEqual(consequence.expires_at, refresh - 100 + 86400)
        await engine.dispose()


class PerkTrainingTests(unittest.TestCase):
    def test_basic_uses_local_instructor_and_skilled_uses_teacher_and_manual(self):
        state = player_state()
        state["buildings"].append({"id": "training", "type": "training_ground", "x": 8, "y": 1, "assigned": []})

        state["resources"]["gold"] = 8
        basic = train_perk(state, "player", "combat")
        self.assertEqual(state["resources"]["gold"],0)
        teacher=deepcopy(state["characters"][0]);teacher.update(id="teacher",name="Teacher",is_player=False,status="idle");teacher["perks"]["combat"]="skilled";state["characters"].append(teacher)
        self.assertEqual(basic["level"], "basic")
        with self.assertRaisesRegex(ValueError, "Training Manual"):
            train_perk(state, "player", "combat")
        state["inventory"].append({"instance_id": "manual_1", "item_id": "training_manual"})
        skilled = train_perk(state, "player", "combat")
        self.assertEqual(skilled["level"], "skilled")
        self.assertFalse(any(item["item_id"] == "training_manual" for item in state["inventory"]))

    def test_legacy_numeric_skill_does_not_add_to_capability(self):
        state = new_game({"name": "No Perk", "stats": {"combat": 10}, "attributes": {"str": 2, "dex": 2}})
        character = state["characters"][0]

        self.assertEqual(character["perks"]["combat"], "none")
        self.assertLess(effective_stat(state, character, "combat"), 10)

    def test_mission_reward_can_grant_standalone_perk_and_transform_race(self):
        state = player_state()
        awarded = {"materials": {}, "items": [], "blueprints": [], "recruits": [], "perks": [], "transformations": []}

        _award_reward_block(state, {"standalone_perk": "moon_sense"}, awarded, random.Random(1), "player")
        _award_reward_block(state, {"transform": {"race": "Werewolf", "standalone_perks": ["lycanthrope"]}}, awarded, random.Random(1), "player")

        self.assertIn("moon_sense", state["characters"][0]["traits"])
        self.assertIn("lycanthrope", state["characters"][0]["traits"])
        self.assertEqual(state["characters"][0]["race"], "Werewolf")


class PortraitPipelineTests(unittest.TestCase):
    def test_upload_resize_creates_bounded_full_image_and_square_thumbnail(self):
        source = Image.new("RGB", (1800, 1400), (80, 120, 90))
        raw = io.BytesIO()
        source.save(raw, "PNG")

        full_bytes, thumb_bytes = _resize_portrait(raw.getvalue())
        with Image.open(io.BytesIO(full_bytes)) as full, Image.open(io.BytesIO(thumb_bytes)) as thumb:
            self.assertLessEqual(max(full.size), 1200)
            self.assertEqual(thumb.size, (192, 192))
            self.assertEqual(full.format, "WEBP")
            self.assertEqual(thumb.format, "WEBP")

    def test_pool_returns_matching_full_and_thumbnail_urls(self):
        original_root = portrait_module.PORTRAIT_POOL_ROOT
        with tempfile.TemporaryDirectory() as temp:
            portrait_module.PORTRAIT_POOL_ROOT = Path(temp)
            full = Path(temp) / "goblin_female_melee" / "full"
            thumb = Path(temp) / "goblin_female_melee" / "thumb"
            full.mkdir(parents=True); thumb.mkdir(parents=True)
            (full / "goblin_female_melee_001.webp").write_bytes(b"full")
            (thumb / "goblin_female_melee_001.webp").write_bytes(b"thumb")
            portrait = portrait_module.choose_pool_portrait("goblin_female_melee", random.Random(1))
        portrait_module.PORTRAIT_POOL_ROOT = original_root

        self.assertIn("/full/goblin_female_melee_001.webp", portrait["portrait"])
        self.assertIn("/thumb/goblin_female_melee_001.webp", portrait["portrait_thumbnail"])

    def test_pool_portrait_inherits_stable_appearance_metadata(self):
        original_root = portrait_module.PORTRAIT_POOL_ROOT
        original_metadata = appearance_module.PORTRAIT_METADATA_PATH
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            portrait_module.PORTRAIT_POOL_ROOT = root / "pools"
            appearance_module.PORTRAIT_METADATA_PATH = portrait_module.PORTRAIT_POOL_ROOT / "portrait_metadata.json"
            full = portrait_module.PORTRAIT_POOL_ROOT / "goblin_female_melee" / "full"
            full.mkdir(parents=True)
            (full / "goblin_female_melee_001.webp").write_bytes(b"full")
            appearance_module.write_portrait_metadata({
                "goblin_female_melee/goblin_female_melee_001.webp": {
                    "hair_color": "black", "eye_color": "gold",
                    "distinctive_features": "a chipped right tusk",
                },
            })
            portrait = portrait_module.choose_pool_portrait("goblin_female_melee", random.Random(1))
        portrait_module.PORTRAIT_POOL_ROOT = original_root
        appearance_module.PORTRAIT_METADATA_PATH = original_metadata

        self.assertEqual(portrait["appearance_source"], "portrait")
        self.assertEqual(portrait["appearance"]["eye_color"], "gold")

    def test_pool_falls_back_to_roleless_then_another_role(self):
        original_root = portrait_module.PORTRAIT_POOL_ROOT
        with tempfile.TemporaryDirectory() as temp:
            portrait_module.PORTRAIT_POOL_ROOT = Path(temp)
            roleless = Path(temp) / "slimefolk_female" / "full"
            roleless.mkdir(parents=True)
            (roleless / "slimefolk_female_001.webp").write_bytes(b"full")
            portrait = portrait_module.choose_pool_portrait("slimefolk_female_healer", random.Random(1))
            self.assertEqual(portrait["portrait_pool"], "slimefolk_female")

            roleless.rename(Path(temp) / "slimefolk_female_removed")
            ranged = Path(temp) / "slimefolk_female_ranged" / "full"
            ranged.mkdir(parents=True)
            (ranged / "slimefolk_female_ranged_001.webp").write_bytes(b"full")
            portrait = portrait_module.choose_pool_portrait("slimefolk_female_melee", random.Random(1))
            self.assertEqual(portrait["portrait_pool"], "slimefolk_female_ranged")
        portrait_module.PORTRAIT_POOL_ROOT = original_root

    def test_beastkin_family_condition_keeps_concrete_race(self):
        state = player_state()
        character = state["characters"][0]
        character["race"] = "Catfolk"
        self.assertTrue(character_condition_met(state, character, {"kind": "race_family", "value": "Beastkin"}))
        self.assertEqual(character["race"], "Catfolk")

    def test_race_families_support_deathless_and_overlapping_groups(self):
        state = player_state()
        character = state["characters"][0]
        character["race"] = "Banshee"
        self.assertTrue(character_condition_met(state, character, {"kind": "race_family", "value": "Deathless"}))
        character["race"] = "Minotaur"
        self.assertTrue(character_condition_met(state, character, {"kind": "race_family", "value": "Beastkin"}))
        self.assertTrue(character_condition_met(state, character, {"kind": "race_family", "value": "Giantkin"}))

    def test_appearance_is_not_forced_into_mission_story(self):
        state = player_state()
        state["characters"][0]["appearance"] = {
            "hair_color": "silver", "hair_length": "long", "eye_color": "amber",
            "skin_tone": "", "build": "", "distinctive_features": "", "summary": "",
        }
        mission = deepcopy(MISSION_TEMPLATES["roadside_store"])
        analysis = analyze_mission(state, mission, ["player"])
        result = resolve_mission(state, mission, ["player"], analysis, "appearance-story", forced_outcome="success")
        self.assertFalse(any("silver hair" in paragraph or "amber eyes" in paragraph for paragraph in result["story"]))
        state["characters"][0]["gender"] = "female"
        state["characters"][0]["race"] = "Human"
        state["characters"][0]["appearance"]["summary"] = "A female human with long brown hair and a sword in her hand."
        natural = resolve_mission(
            state, mission, ["player"], analyze_mission(state, mission, ["player"]),
            "appearance-summary", forced_outcome="success",
        )
        self.assertFalse(any("long brown hair" in paragraph or "sword in her hand" in paragraph for paragraph in natural["story"]))

    def test_internal_trigger_labels_never_leak_into_story(self):
        state = player_state()
        mission = deepcopy(MISSION_TEMPLATES["roadside_store"])
        analysis = analyze_mission(state, mission, ["player"])
        analysis["triggered"] = [{"label": "Event race or relic affinity", "bonus": 3}]
        result = resolve_mission(
            state, mission, ["player"], analysis, "internal-trigger-label", forced_outcome="success",
        )
        story = " ".join(result["story"]).lower()
        self.assertNotIn("event race or relic affinity", story)
        self.assertNotIn("the turning point was", story)
        self.assertGreaterEqual(len(result["story"]), 3)

    def test_champion_expression_uses_variant_and_falls_back_to_default(self):
        original_root = portrait_module.CHAMPION_PORTRAIT_ROOT
        with tempfile.TemporaryDirectory() as temp:
            portrait_module.CHAMPION_PORTRAIT_ROOT = Path(temp)
            default = Path(temp) / "raviel_ivansia" / "default"
            default.mkdir(parents=True)
            (default / "full.webp").write_bytes(b"default full")
            (default / "thumb.webp").write_bytes(b"default thumb")

            fallback = portrait_module.champion_portrait("raviel_ivansia", "angry")
            expression = Path(temp) / "raviel_ivansia" / "expressions" / "angry"
            expression.mkdir(parents=True)
            (expression / "full.webp").write_bytes(b"angry full")
            (expression / "thumb.webp").write_bytes(b"angry thumb")
            angry = portrait_module.champion_portrait("raviel_ivansia", "angry")
        portrait_module.CHAMPION_PORTRAIT_ROOT = original_root

        self.assertEqual(fallback["portrait_variant"], "default")
        self.assertIn("/raviel_ivansia/default/full.webp", fallback["portrait"])
        self.assertEqual(angry["portrait_variant"], "angry")
        self.assertIn("/raviel_ivansia/expressions/angry/full.webp", angry["portrait"])

    def test_champion_variant_tools_create_manifest_and_delete_one_variant(self):
        original_root = champion_portrait_io.CHAMPION_ROOT
        original_manifest = champion_portrait_io.MANIFEST_PATH
        with tempfile.TemporaryDirectory() as temp:
            champion_portrait_io.CHAMPION_ROOT = Path(temp)
            champion_portrait_io.MANIFEST_PATH = Path(temp) / "manifest.json"
            source = Image.new("RGB", (320, 480), "purple")
            champion_portrait_io.save_variant(source, "raviel_ivansia", "angry")
            manifest = champion_portrait_io.read_manifest()
            champion_portrait_io.record_variant(manifest, "raviel_ivansia", "angry")
            champion_portrait_io.write_manifest(manifest)

            self.assertEqual(champion_portrait_io.available_variants("raviel_ivansia"), ["angry"])
            self.assertTrue(champion_portrait_io.remove_variant("raviel_ivansia", "angry"))
            self.assertEqual(champion_portrait_io.available_variants("raviel_ivansia"), [])
            self.assertEqual(
                champion_portrait_io.read_manifest()["champions"]["raviel_ivansia"]["variants"], []
            )
        champion_portrait_io.CHAMPION_ROOT = original_root
        champion_portrait_io.MANIFEST_PATH = original_manifest

    def test_goblin_boss_uses_only_special_gender_pool(self):
        recruit = _make_procedural("goblin_boss", random.Random(2))

        self.assertIn(recruit["portrait_pool"], {"goblin_male_special", "goblin_female_special"})
        self.assertIn(recruit["gender"], {"male", "female"})

    def test_werewolf_pool_does_not_depend_on_role_or_special_status(self):
        self.assertEqual(
            portrait_module.portrait_pool_key("Werewolf", "female", "fighter", True),
            "werewolf_female",
        )
        self.assertEqual(
            portrait_module.portrait_pool_key("Werewolf", "male", "adept", False),
            "werewolf_male",
        )

    def test_slimefolk_pool_is_role_neutral(self):
        self.assertEqual(
            portrait_module.portrait_pool_key("Slimefolk", "female", "medic", False),
            "slimefolk_female",
        )
        self.assertEqual(
            portrait_module.portrait_pool_key("Slimefolk", "female", "adept", True),
            "slimefolk_female",
        )

    def test_assigned_pool_portrait_does_not_change_when_pool_grows(self):
        original_root = portrait_module.PORTRAIT_POOL_ROOT
        with tempfile.TemporaryDirectory() as temp:
            portrait_module.PORTRAIT_POOL_ROOT = Path(temp)
            full = Path(temp) / "human_female_melee" / "full"
            thumb = Path(temp) / "human_female_melee" / "thumb"
            full.mkdir(parents=True); thumb.mkdir(parents=True)
            (full / "human_female_melee_001.webp").write_bytes(b"full")
            (thumb / "human_female_melee_001.webp").write_bytes(b"thumb")
            state = player_state()
            state["characters"].append({
                "id": "locked-recruit", "source_kind": "generic", "race": "Human", "gender": "female",
                "archetype_id": "fighter", "specialty": "Fighter", "traits": [], "portrait": "",
                "portrait_source": "none", "status": "idle", "equipment": {},
            })
            normalize_state(state)
            assigned = state["characters"][-1]["portrait"]
            (full / "human_female_melee_002.webp").write_bytes(b"new full")
            (thumb / "human_female_melee_002.webp").write_bytes(b"new thumb")
            normalize_state(state)
        portrait_module.PORTRAIT_POOL_ROOT = original_root

        self.assertTrue(state["characters"][-1]["portrait_locked"])
        self.assertEqual(state["characters"][-1]["portrait"], assigned)


if __name__ == "__main__":
    unittest.main()
