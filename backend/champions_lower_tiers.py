"""Popularity-tiered women added to the Champion collection.

Champion rank describes recognition and discovery rarity, not combat power.  A
dangerous character can therefore be D/E rank when she is a deep-cut side
character, while an iconic noncombatant can be S rank.
"""
from __future__ import annotations

from copy import deepcopy

from .champions import ROLE_TEMPLATES


# id, display name, series, role, popularity rank, race
LOWER_TIER_CATALOG = [
    # Broadly iconic favorites.
    ("megumin", "Megumin", "KonoSuba", "mage", "S", "Human"),
    ("mikoto_misaka", "Mikoto Misaka", "A Certain Scientific Railgun", "mage", "S", "Esper"),
    ("kurumi_tokisaki", "Kurumi Tokisaki", "Date A Live", "marksman", "S", "Spirit"),
    ("miku_nakano", "Miku Nakano", "The Quintessential Quintuplets", "support", "S", "Human"),
    ("hitori_gotoh", "Hitori Gotoh", "Bocchi the Rock!", "support", "S", "Human"),

    # Famous leads and enduring fan favorites.
    ("aqua", "Aqua", "KonoSuba", "healer", "A", "Goddess"),
    ("darkness", "Darkness", "KonoSuba", "vanguard", "A", "Human"),
    ("esdeath", "Esdeath", "Akame ga Kill!", "vanguard", "A", "Human"),
    ("raphtalia", "Raphtalia", "The Rising of the Shield Hero", "duelist", "A", "Raccoon Demi-Human"),
    ("albedo", "Albedo", "Overlord", "vanguard", "A", "Succubus"),
    ("yukino_yukinoshita", "Yukino Yukinoshita", "My Teen Romantic Comedy SNAFU", "strategist", "A", "Human"),
    ("shoko_komi", "Shoko Komi", "Komi Can't Communicate", "support", "A", "Human"),
    ("taiga_aisaka", "Taiga Aisaka", "Toradora!", "duelist", "A", "Human"),
    ("tohru", "Tohru", "Miss Kobayashi's Dragon Maid", "vanguard", "A", "Dragon"),
    ("hestia", "Hestia", "Is It Wrong to Try to Pick Up Girls in a Dungeon?", "support", "A", "Goddess"),
    ("chizuru_mizuhara", "Chizuru Mizuhara", "Rent-A-Girlfriend", "support", "A", "Human"),
    ("tohka_yatogami", "Tohka Yatogami", "Date A Live", "vanguard", "A", "Spirit"),
    ("anna_yamada", "Anna Yamada", "The Dangers in My Heart", "support", "A", "Human"),
    ("asa_mitaka", "Asa Mitaka", "Chainsaw Man", "strategist", "A", "Human"),
    ("yoru_war_devil", "Yoru", "Chainsaw Man", "vanguard", "A", "Devil"),
    ("roxana_agriche", "Roxana Agriche", "Roxana", "strategist", "A", "Human"),
    ("navier_trovi", "Navier Ellie Trovi", "The Remarried Empress", "strategist", "A", "Human"),
    ("medea_solon", "Medea Solon", "Your Throne", "strategist", "A", "Human"),
    ("penelope_eckart", "Penelope Eckart", "Villains Are Destined to Die", "strategist", "A", "Human"),
    ("jiyoung_yoo", "Jiyoung Yoo", "Eleceed", "mage", "A", "Awakened Human"),

    # Well-known characters whose fandom reach is narrower than the A tier.
    ("nino_nakano", "Nino Nakano", "The Quintessential Quintuplets", "support", "B", "Human"),
    ("yunyun", "Yunyun", "KonoSuba", "mage", "B", "Human"),
    ("wiz", "Wiz", "KonoSuba", "mage", "B", "Lich"),
    ("shalltear_bloodfallen", "Shalltear Bloodfallen", "Overlord", "vanguard", "B", "Vampire"),
    ("shion", "Shion", "That Time I Got Reincarnated as a Slime", "vanguard", "B", "Oni"),
    ("shuna", "Shuna", "That Time I Got Reincarnated as a Slime", "healer", "B", "Oni"),
    ("milim_nava", "Milim Nava", "That Time I Got Reincarnated as a Slime", "vanguard", "B", "Dragonoid"),
    ("ais_wallenstein", "Ais Wallenstein", "Is It Wrong to Try to Pick Up Girls in a Dungeon?", "duelist", "B", "Human"),
    ("ryuu_lion", "Ryuu Lion", "Is It Wrong to Try to Pick Up Girls in a Dungeon?", "duelist", "B", "Elf"),
    ("kotori_itsuka", "Kotori Itsuka", "Date A Live", "strategist", "B", "Spirit"),
    ("origami_tobiichi", "Origami Tobiichi", "Date A Live", "marksman", "B", "Human"),
    ("ichika_nakano", "Ichika Nakano", "The Quintessential Quintuplets", "support", "B", "Human"),
    ("yotsuba_nakano", "Yotsuba Nakano", "The Quintessential Quintuplets", "scout", "B", "Human"),
    ("itsuki_nakano", "Itsuki Nakano", "The Quintessential Quintuplets", "support", "B", "Human"),
    ("yui_yuigahama", "Yui Yuigahama", "My Teen Romantic Comedy SNAFU", "support", "B", "Human"),
    ("iroha_isshiki", "Iroha Isshiki", "My Teen Romantic Comedy SNAFU", "support", "B", "Human"),
    ("rikka_takanashi", "Rikka Takanashi", "Love, Chunibyo & Other Delusions!", "mage", "B", "Human"),
    ("nijika_ijichi", "Nijika Ijichi", "Bocchi the Rock!", "support", "B", "Human"),
    ("ikuyo_kita", "Ikuyo Kita", "Bocchi the Rock!", "support", "B", "Human"),
    ("seiko_ayase", "Seiko Ayase", "DAN DA DAN", "mage", "B", "Human"),
    ("himiko_toga", "Himiko Toga", "My Hero Academia", "scout", "B", "Human"),
    ("ino_yamanaka", "Ino Yamanaka", "Naruto", "healer", "B", "Human"),
    ("perona", "Perona", "One Piece", "mage", "B", "Human"),
    ("jewelry_bonney", "Jewelry Bonney", "One Piece", "vanguard", "B", "Human"),
    ("pieck_finger", "Pieck Finger", "Attack on Titan", "strategist", "B", "Titan Shifter"),
    ("hwa_ryun", "Hwa Ryun", "Tower of God", "strategist", "B", "Red Witch"),
    ("yuri_jahad", "Yuri Jahad", "Tower of God", "vanguard", "B", "Princess of Jahad"),
    ("ihwa", "Ihwa", "Hero Killer", "duelist", "B", "Gifted Human"),
    ("raviel_ivansia", "Raviel Ivansia", "SSS-Class Revival Hunter", "strategist", "B", "Human"),
    ("psyche_callista", "Psyche Callista", "Your Throne", "healer", "B", "Human"),
    ("maximilian_calypse", "Maximilian Calypse", "Under the Oak Tree", "mage", "B", "Human"),
    ("juvelian_floyen", "Juvelian Floyen", "Father, I Don't Want This Marriage", "support", "B", "Human"),
    ("cayena_hill", "Cayena Hill", "The Villainess Is a Marionette", "strategist", "B", "Human"),
    ("shuri_von_neuschwanstein", "Shuri von Neuschwanstein", "A Stepmother's Märchen", "strategist", "B", "Human"),
    ("eris_miserian", "Eris Miserian", "Kill the Villainess", "duelist", "B", "Human"),
    ("deborah_seymour", "Deborah Seymour", "The Perks of Being a Villainess", "strategist", "B", "Human"),
    ("florentia_lombardi", "Florentia Lombardi", "I Shall Master This Family", "strategist", "B", "Human"),

    # Recognizable supporting cast and cult favorites.
    ("ryo_yamada", "Ryo Yamada", "Bocchi the Rock!", "strategist", "C", "Human"),
    ("kanna_kamui", "Kanna Kamui", "Miss Kobayashi's Dragon Maid", "mage", "C", "Dragon"),
    ("elma", "Elma", "Miss Kobayashi's Dragon Maid", "vanguard", "C", "Dragon"),
    ("ruka_sarashina", "Ruka Sarashina", "Rent-A-Girlfriend", "scout", "C", "Human"),
    ("sumi_sakurasawa", "Sumi Sakurasawa", "Rent-A-Girlfriend", "support", "C", "Human"),
    ("mami_nanami", "Mami Nanami", "Rent-A-Girlfriend", "strategist", "C", "Human"),
    ("rumiko_manbagi", "Rumiko Manbagi", "Komi Can't Communicate", "support", "C", "Human"),
    ("shizuka_hiratsuka", "Shizuka Hiratsuka", "My Teen Romantic Comedy SNAFU", "vanguard", "C", "Human"),
    ("saki_kawasaki", "Saki Kawasaki", "My Teen Romantic Comedy SNAFU", "support", "C", "Human"),
    ("minori_kushieda", "Minori Kushieda", "Toradora!", "scout", "C", "Human"),
    ("ami_kawashima", "Ami Kawashima", "Toradora!", "strategist", "C", "Human"),
    ("yuki_nagato", "Yuki Nagato", "The Melancholy of Haruhi Suzumiya", "strategist", "C", "Humanoid Interface"),
    ("mikuru_asahina", "Mikuru Asahina", "The Melancholy of Haruhi Suzumiya", "support", "C", "Human"),
    ("tsuyu_asui", "Tsuyu Asui", "My Hero Academia", "scout", "C", "Human"),
    ("kyoka_jiro", "Kyoka Jiro", "My Hero Academia", "scout", "C", "Human"),
    ("mina_ashido", "Mina Ashido", "My Hero Academia", "duelist", "C", "Human"),
    ("mei_hatsume", "Mei Hatsume", "My Hero Academia", "strategist", "C", "Human"),
    ("kurenai_yuhi", "Kurenai Yuhi", "Naruto", "mage", "C", "Human"),
    ("anko_mitarashi", "Anko Mitarashi", "Naruto", "scout", "C", "Human"),
    ("shizune", "Shizune", "Naruto", "healer", "C", "Human"),
    ("tenten", "Tenten", "Naruto", "marksman", "C", "Human"),
    ("karin_uzumaki", "Karin Uzumaki", "Naruto", "healer", "C", "Human"),
    ("tashigi", "Tashigi", "One Piece", "duelist", "C", "Human"),
    ("carrot", "Carrot", "One Piece", "scout", "C", "Mink"),
    ("vinsmoke_reiju", "Vinsmoke Reiju", "One Piece", "healer", "C", "Modified Human"),
    ("ulti", "Ulti", "One Piece", "vanguard", "C", "Human"),
    ("kozuki_hiyori", "Kozuki Hiyori", "One Piece", "support", "C", "Human"),
    ("soi_fon", "Soi Fon", "BLEACH", "scout", "C", "Soul"),
    ("retsu_unohana", "Retsu Unohana", "BLEACH", "healer", "C", "Soul"),
    ("nelliel_tu_oderschvank", "Nelliel Tu Odelschwanck", "BLEACH", "vanguard", "C", "Arrancar"),
    ("riruka_dokugamine", "Riruka Dokugamine", "BLEACH", "mage", "C", "Human"),
    ("shoko_ieiri", "Shoko Ieiri", "Jujutsu Kaisen", "healer", "C", "Human"),
    ("utahime_iori", "Utahime Iori", "Jujutsu Kaisen", "support", "C", "Human"),
    ("kasumi_miwa", "Kasumi Miwa", "Jujutsu Kaisen", "duelist", "C", "Human"),
    ("aoi_kanzaki", "Aoi Kanzaki", "Demon Slayer", "healer", "C", "Human"),
    ("rachel_tower", "Rachel", "Tower of God", "strategist", "C", "Human"),
    ("melissa_podebrat", "Melissa Podebrat", "Beware the Villainess!", "duelist", "C", "Human"),
    ("latte_ectrie", "Latte Ectrie", "Miss Not-So Sidekick", "support", "C", "Human"),

    # Minor recurring characters.
    ("hanabi_hyuga", "Hanabi Hyuga", "Naruto", "duelist", "D", "Human"),
    ("isane_kotetsu", "Isane Kotetsu", "BLEACH", "healer", "D", "Soul"),
    ("lisa_yadomaru", "Lisa Yadomaru", "BLEACH", "duelist", "D", "Visored"),
    ("kukaku_shiba", "Kukaku Shiba", "BLEACH", "mage", "D", "Soul"),
    ("makino", "Makino", "One Piece", "support", "D", "Human"),
    ("marguerite", "Marguerite", "One Piece", "marksman", "D", "Human"),
    ("petra_ral", "Petra Ral", "Attack on Titan", "duelist", "D", "Human"),

    # Deep-cut side characters: familiar to committed fans, obscure elsewhere.
    ("hana_inuzuka", "Hana Inuzuka", "Naruto", "healer", "E", "Human"),
    ("ayame_ichiraku", "Ayame", "Naruto", "support", "E", "Human"),
    ("tsume_inuzuka", "Tsume Inuzuka", "Naruto", "scout", "E", "Human"),
    ("samui", "Samui", "Naruto", "vanguard", "E", "Human"),
    ("karui", "Karui", "Naruto", "duelist", "E", "Human"),
    ("mabui", "Mabui", "Naruto", "support", "E", "Human"),
    ("yugao_uzuki", "Yugao Uzuki", "Naruto", "duelist", "E", "Human"),
    ("kaya", "Kaya", "One Piece", "healer", "E", "Human"),
    ("nojiko", "Nojiko", "One Piece", "support", "E", "Human"),
    ("conis", "Conis", "One Piece", "support", "E", "Skypiean"),
    ("rico_brzenska", "Rico Brzenska", "Attack on Titan", "strategist", "E", "Human"),
    ("nifa", "Nifa", "Attack on Titan", "scout", "E", "Human"),
    ("mina_carolina", "Mina Carolina", "Attack on Titan", "duelist", "E", "Human"),
]


SIGNATURE_NAMES = {
    "megumin": "Explosion Magic",
    "mikoto_misaka": "Railgun",
    "kurumi_tokisaki": "Zafkiel",
    "miku_nakano": "Sengoku Devotion",
    "hitori_gotoh": "Guitar Hero",
    "aqua": "Sacred Turn Undead",
    "hana_inuzuka": "Haimaru Veterinary Ninjutsu",
}


def _build_champion(entry: tuple[str, str, str, str, str, str]) -> tuple[str, dict]:
    champion_id, name, series, role, rank, race = entry
    profile = deepcopy(ROLE_TEMPLATES[role])
    # Popularity rank only adds a modest collection bonus; the role remains the
    # main source of stats, allowing obscure but formidable characters to work.
    rank_adjustment = {"E": -2, "D": -1, "C": 0, "B": 1, "A": 2, "S": 3}[rank]
    profile["stats"] = {
        key: max(1, min(10, value + rank_adjustment))
        for key, value in profile["stats"].items()
    }
    profile["attributes"] = {
        key: max(1, min(12, value + rank_adjustment))
        for key, value in profile["attributes"].items()
    }
    signature = f"{champion_id}_signature"
    profile.update({
        "name": name,
        "race": race,
        "gender": "female",
        "series": series,
        "source_kind": "champion",
        "champion_rank": rank,
        "traits": list(dict.fromkeys(profile["traits"] + [signature])),
        "portrait": "",
    })
    return champion_id, profile


LOWER_TIER_CHAMPIONS = dict(_build_champion(entry) for entry in LOWER_TIER_CATALOG)
LOWER_TIER_PERKS = {
    f"{champion_id}_signature": {
        "name": SIGNATURE_NAMES.get(champion_id, f"{name}'s Signature"),
        "description": f"{name}'s defining talent from {series}.",
        "effect": "A Champion signature perk that can unlock matching special mission routes.",
    }
    for champion_id, name, series, _, _, _ in LOWER_TIER_CATALOG
}

assert len(LOWER_TIER_CATALOG) == 120
assert len(LOWER_TIER_CHAMPIONS) == len(LOWER_TIER_CATALOG)
assert len({entry[0] for entry in LOWER_TIER_CATALOG}) == len(LOWER_TIER_CATALOG)
