"""Unique, one-copy divine characters and their private mission chains."""
from __future__ import annotations

from copy import deepcopy

from .champions import ROLE_TEMPLATES


# These are a separate collection from crossover Champions. Only the first four
# currently have acquisition chains; the others are ready for later stories.
_CELESTIAL_CATALOG = [
    ("athena", "Athena", "Greek", "strategist", "female", ["owl_wisdom", "divine_magic", "guard"]),
    ("hecate", "Hecate", "Greek", "mage", "female", ["crossroads_magic", "divine_magic", "ley_touched"]),
    ("diana", "Diana", "Roman", "marksman", "female", ["silver_hunt", "divine_magic", "tracker"]),
    ("bellona", "Bellona", "Roman", "vanguard", "female", ["war_goddess", "divine_magic", "guard"]),
    ("isis", "Isis", "Egyptian", "healer", "female", ["throne_magic", "divine_magic", "soul_anchor"]),
    ("anubis", "Anubis", "Egyptian", "strategist", "male", ["weigher_of_hearts", "divine_magic", "undead_hunter"]),
    ("freyja", "Freyja", "Norse", "mage", "female", ["golden_seidr", "divine_magic", "war_leader"]),
    ("odin", "Odin", "Norse", "strategist", "male", ["rune_wisdom", "divine_magic", "pathfinder"]),
]


def _build_celestial(entry: tuple[str, str, str, str, str, list[str]]) -> tuple[str, dict]:
    celestial_id, name, pantheon, role, gender, traits = entry
    profile = deepcopy(ROLE_TEMPLATES[role])
    profile["stats"] = {key: min(10, value + 2) for key, value in profile["stats"].items()}
    profile["attributes"] = {key: min(12, value + 2) for key, value in profile["attributes"].items()}
    profile.update({
        "name": name, "race": "Celestial", "gender": gender, "series": f"{pantheon} Pantheon",
        "pantheon": pantheon, "source_kind": "celestial", "limited": True,
        "traits": list(dict.fromkeys(profile["traits"] + traits)), "portrait": "",
    })
    return celestial_id, profile


CELESTIALS = dict(_build_celestial(entry) for entry in _CELESTIAL_CATALOG)
CELESTIAL_PERKS = {
    "owl_wisdom": {"name": "Owl Wisdom", "description": "Athena reads a battlefield as if its choices were already written.", "effect": "Unlocks divine strategy and guardian paths."},
    "crossroads_magic": {"name": "Crossroads Magic", "description": "Hecate commands thresholds, torchlight, spirits, and divided roads.", "effect": "Unlocks planar and crossroads paths."},
    "silver_hunt": {"name": "Silver Hunt", "description": "Diana never loses a chosen trail beneath the moon.", "effect": "Unlocks divine hunt and wilderness paths."},
    "war_goddess": {"name": "War Goddess", "description": "Bellona turns discipline and fury into one decisive advance.", "effect": "Unlocks divine warfare paths."},
    "throne_magic": {"name": "Throne Magic", "description": "Isis binds healing, protection, and rightful authority together.", "effect": "Unlocks divine restoration and royal paths."},
    "weigher_of_hearts": {"name": "Weigher of Hearts", "description": "Anubis recognizes the true weight carried by every soul.", "effect": "Unlocks judgment, burial, and spirit paths."},
    "golden_seidr": {"name": "Golden Seidr", "description": "Freyja sees desire, fate, death, and battle as threads of one craft.", "effect": "Unlocks fate-weaving and Vanir paths."},
    "rune_wisdom": {"name": "Rune Wisdom", "description": "Odin traded comfort and certainty for knowledge without end.", "effect": "Unlocks runic, sacrificial, and hidden-knowledge paths."},
}


def _stage(
    chain_id: str, step: int, total: int, name: str, description: str, stat: str,
    difficulty: int, party_size: int, rewards: dict, critical_rewards: dict,
    approaches: list[str], successes: list[str], criticals: list[str],
    next_id: str | None = None, celestial: str | None = None,
) -> dict:
    return {
        "name": name, "description": description, "rank": "S", "stat": stat,
        "difficulty": difficulty, "party_size": party_size,
        "durations": [[1800, 3600], [3600, 7200], [7200, 14400]][step - 1],
        "pool_weight": 0, "chain_only": True, "chain_id": chain_id,
        "chain_step": step, "chain_total": total, "chain_next": next_id,
        "claim_requirements": [], "visible_hints": ["This is a private chained mission.", "Its reward grows with every completed chapter."],
        "modifiers": [], "critical_any": [], "special_events": [], "roles": [],
        "rewards": rewards, "critical_rewards": critical_rewards,
        "reward_preview": [f"Chain chapter {step}/{total}", "Escalating rewards"] + (["Unique Celestial"] if celestial else []),
        "celestial_reward": celestial,
        "narrative": {
            "approach": approaches,
            "critical_failure": [
                "The sign failed at the worst moment. {party} escaped the collapsing path, but the chapter closed without yielding its answer.",
                "Whatever intelligence shaped the trial rejected the approach violently. {lead} got everyone home, though the trail went cold behind them.",
            ],
            "failure": [
                "The party reached the heart of the trial but could not force its final answer. They withdrew with the path still open and the lesson painfully clear.",
                "Progress came at too high a cost to continue. {lead} called the retreat before the trial could turn a setback into a burial.",
            ],
            "success": successes,
            "critical_success": criticals,
        },
    }


CELESTIAL_CHAIN_STEPS = {
    "owl_of_bronze_1": _stage(
        "owl_of_bronze", 1, 3, "The Owl Above the Ruins", "A bronze owl waits over an impossible road of moonlit marble.",
        "survival", 20, 3, {"materials": {"scrap": 45, "cloth": 25, "medicine": 12}}, {"item": "warding_token"},
        [
            "The bronze owl never looked back, yet every time {party} slowed it was waiting on the next broken column. {lead} realized the road existed only while they followed.",
            "Moonlit stairs assembled themselves over empty air beneath {party}. Far below, the ordinary ruins looked small enough to fit inside a map case.",
        ],
        ["At the road's end, the party recovered a bronze tablet covered in moving battle lines. The owl carried its other half toward a storm-wrapped acropolis."],
        ["{lead} anticipated every shift in the false road. The owl bowed once and surrendered both halves of the tablet before opening the next gate."],
        "owl_of_bronze_2",
    ),
    "owl_of_bronze_2": _stage(
        "owl_of_bronze", 2, 3, "The Siege That Never Happened", "Ghostly armies repeat a battle whose winning move was erased from history.",
        "combat", 22, 4, {"materials": {"scrap": 90, "wood": 70, "medicine": 24}}, {"items": ["tower_shield", "specialist_tome"]},
        [
            "Two phantom armies formed around {party}, each convinced the newcomers were its missing command. {lead} had moments to decide which history deserved to survive.",
            "The acropolis rang with bronze and shouted orders, though every soldier was dust inside empty armor. The battle reset whenever anyone repeated an old mistake.",
        ],
        ["The party found the unwritten maneuver and broke the loop. When the armies faded, a living doorway remained beneath the acropolis."],
        ["{party} ended the battle without feeding either army another death. The approving owl opened a path directly into the hall of judgment."],
        "owl_of_bronze_3",
    ),
    "owl_of_bronze_3": _stage(
        "owl_of_bronze", 3, 3, "Audience at the Aegis Hall", "The goddess of strategy will join only a camp capable of defending wisdom without worshiping war.",
        "magic", 24, 5, {"materials": {"scrap": 160, "medicine": 55, "cloth": 85}}, {"items": ["archmage_grimoire", "mastery_codex"]},
        [
            "Athena waited beneath a stone aegis, neither prisoner nor prize. She asked {party} to defend three impossible choices and offered no hint which answer she favored.",
            "The final hall contained no enemy—only a city represented in bronze, already burning along a hundred possible futures. Athena handed command to {lead}.",
        ],
        ["The plan saved what could be saved and named the cost honestly. Athena accepted the camp as a place where counsel might still matter."],
        ["The party discovered a path the trial had not anticipated: victory without vanity. Athena laughed, lifted her spear, and chose to accompany them."],
        celestial="athena",
    ),

    "silent_scale_1": _stage(
        "silent_scale", 1, 3, "Footprints of the Black Jackal", "A trail visible only in grave dust crosses places the dead refuse to enter.",
        "survival", 20, 3, {"materials": {"medicine": 35, "cloth": 35, "scrap": 35}}, {"item": "ashen_reliquary"},
        ["The black jackal's prints appeared one at a time before {party}, each mark cooling the ground around it. {lead} noticed that the dead watched from everywhere except the path."],
        ["The trail ended at a sealed embalmer's gate. The party opened it without disturbing the names sleeping in its lintel."],
        ["Every restless spirit along the road fell silent as the party passed. The gate opened from within, and a voice invited them to continue."],
        "silent_scale_2",
    ),
    "silent_scale_2": _stage(
        "silent_scale", 2, 3, "The Hall of Unfinished Names", "Lost names circle a scale that cannot settle while their stories remain false.",
        "medicine", 22, 4, {"materials": {"medicine": 80, "cloth": 75, "scrap": 60}}, {"items": ["saints_censer", "specialist_tome"]},
        ["Names whispered from thousands of clay jars as {party} entered. Each demanded remembrance; several lied about who they had been."],
        ["The party restored enough true names for the scale to balance. A hidden stair descended toward the judge who had been waiting below."],
        ["{lead} found the one lie holding every other name in place. When it broke, the dead spoke together in relief and opened the final chamber."],
        "silent_scale_3",
    ),
    "silent_scale_3": _stage(
        "silent_scale", 3, 3, "The Weight of a Living Heart", "Anubis asks the party to judge someone whose guilt and sacrifice cannot be separated.",
        "magic", 24, 5, {"materials": {"medicine": 150, "cloth": 110, "scrap": 120}}, {"items": ["mourning_blade", "mastery_codex"]},
        ["Anubis stood beside a scale large enough to weigh a lifetime. He did not ask {party} for obedience; he asked them to make the judgment he refused to simplify."],
        ["The judgment acknowledged both harm and sacrifice. Anubis accepted that the camp understood justice as work rather than certainty."],
        ["The party found a merciful truth without hiding from consequence. Anubis left the scale balanced and joined them as its witness."],
        celestial="anubis",
    ),

    "silver_hunt_1": _stage(
        "silver_hunt", 1, 3, "Tracks Under the Second Moon", "A second moon reveals the spoor of a beast that exists only while pursued.",
        "survival", 20, 3, {"materials": {"food": 60, "wood": 50, "medicine": 18}}, {"item": "ranger_cloak"},
        ["A pale second moon rose as {party} crossed the tree line. Beneath it, tracks appeared ahead of the creature making them."],
        ["The party kept the impossible trail alive until it reached a silver boundary stone. Beyond it waited a forest no local map contained."],
        ["{lead} predicted the beast's future trail and arrived first. A silver bowstring sounded somewhere deeper in the hidden forest."],
        "silver_hunt_2",
    ),
    "silver_hunt_2": _stage(
        "silver_hunt", 2, 3, "The Forest Without Footprints", "The hunt enters a sacred forest where violence erases the hunter instead of the prey.",
        "scavenging", 22, 4, {"materials": {"food": 100, "wood": 100, "medicine": 35}}, {"items": ["moonwood_longbow", "specialist_tome"]},
        ["No footprint remained behind {party}. The forest took every careless mark, forcing the hunters to navigate by memory, breath, and the movement of stars."],
        ["The quarry was cornered without breaking the forest's law. It shed a silver antler and opened a road toward its mistress."],
        ["The party understood that the quarry was testing pursuit, not demanding death. It led them willingly to the final moonlit clearing."],
        "silver_hunt_3",
    ),
    "silver_hunt_3": _stage(
        "silver_hunt", 3, 3, "The Last Arrow of Diana", "Diana offers one arrow and asks the party to choose what deserves to be hunted.",
        "combat", 24, 5, {"materials": {"food": 180, "wood": 150, "medicine": 60}}, {"items": ["titanbone_spear", "mastery_codex"]},
        ["Diana waited in a clearing lit by two moons. At her feet lay one silver arrow; around her moved visions of predators, tyrants, curses, and frightened beasts."],
        ["The chosen target fell, and the reasons survived Diana's scrutiny. She agreed to hunt beside a camp that understood restraint."],
        ["The party loosed the arrow at the hidden hand arranging every false choice. Diana smiled at the answer and followed them home."],
        celestial="diana",
    ),

    "golden_seidr_1": _stage(
        "golden_seidr", 1, 3, "The Thread North of Time", "A golden thread leads through moments that have not happened in the right order.",
        "magic", 20, 3, {"materials": {"cloth": 55, "medicine": 20, "scrap": 45}}, {"item": "gravity_boots"},
        ["The golden thread pulled {party} through yesterday's rain and tomorrow's ashes. {lead} kept hold even when the camp appeared ahead of them, old and abandoned."],
        ["The party tied the broken hours back into sequence and found a golden spindle waiting at the thread's northern end."],
        ["{party} returned every stolen second to its proper owner. The spindle began turning by itself and spun a road into the snow."],
        "golden_seidr_2",
    ),
    "golden_seidr_2": _stage(
        "golden_seidr", 2, 3, "The Price of the Brísingamen", "Four smith-shadows demand four different prices for a necklace that remembers every bargain.",
        "alchemy", 22, 4, {"materials": {"cloth": 95, "scrap": 100, "medicine": 35}}, {"items": ["engineers_bracers", "specialist_tome"]},
        ["Four furnaces burned beneath the snow. Their smiths spoke in one voice and named prices no sensible merchant would put on a ledger."],
        ["The bargain held without surrendering what the party could not replace. The necklace lit a path toward a hall full of waiting cats."],
        ["{lead} offered the smiths a fifth bargain and made them compete for it. Their laughter shook gold from the rafters and opened the last road."],
        "golden_seidr_3",
    ),
    "golden_seidr_3": _stage(
        "golden_seidr", 3, 3, "Freyja's Share of the Fallen", "Freyja asks the party to recover warriors claimed by neither life nor death.",
        "medicine", 24, 5, {"materials": {"cloth": 170, "medicine": 100, "scrap": 130}}, {"items": ["celestial_halo", "mastery_codex"]},
        ["Freyja met {party} at the edge of a battlefield frozen between its final heartbeat and silence. Half the fallen waited for someone to remember why they fought."],
        ["The stranded warriors reached the hall appointed to them. Freyja chose to visit the mortal camp whose people had carried strangers through death."],
        ["The party recovered every name and left no soul to wander. Freyja fastened the golden thread to her cloak and followed it back with them."],
        celestial="freyja",
    ),
}


assert len(CELESTIALS) == 8
assert len(CELESTIAL_CHAIN_STEPS) == 12
