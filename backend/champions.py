"""Large authored Champion catalog kept separate from the mission definitions."""
from __future__ import annotations

from copy import deepcopy


ROLE_TEMPLATES = {
    "vanguard": {
        "specialty": "Vanguard", "traits": ["guard"],
        "stats": {"combat": 9, "scavenging": 3, "building": 3, "medicine": 2, "cooking": 2, "survival": 7, "magic": 3},
        "attributes": {"str": 9, "dex": 6, "agi": 6, "vit": 9, "int": 4, "luk": 5},
    },
    "duelist": {
        "specialty": "Duelist", "traits": ["swordsman"],
        "stats": {"combat": 9, "scavenging": 4, "building": 2, "medicine": 2, "cooking": 2, "survival": 7, "magic": 3},
        "attributes": {"str": 7, "dex": 9, "agi": 9, "vit": 6, "int": 5, "luk": 6},
    },
    "marksman": {
        "specialty": "Marksman", "traits": ["scout"],
        "stats": {"combat": 8, "scavenging": 7, "building": 2, "medicine": 2, "cooking": 2, "survival": 8, "magic": 2},
        "attributes": {"str": 4, "dex": 10, "agi": 8, "vit": 5, "int": 6, "luk": 7},
    },
    "mage": {
        "specialty": "Archmage", "traits": ["magic_resistance"],
        "stats": {"combat": 6, "scavenging": 4, "building": 2, "medicine": 4, "cooking": 3, "survival": 6, "magic": 10},
        "attributes": {"str": 3, "dex": 5, "agi": 6, "vit": 5, "int": 10, "luk": 8},
    },
    "healer": {
        "specialty": "Mystic Healer", "traits": ["medic"],
        "stats": {"combat": 5, "scavenging": 4, "building": 2, "medicine": 10, "cooking": 5, "survival": 7, "magic": 8},
        "attributes": {"str": 3, "dex": 7, "agi": 6, "vit": 6, "int": 10, "luk": 7},
    },
    "scout": {
        "specialty": "Elite Scout", "traits": ["scout", "tracker"],
        "stats": {"combat": 7, "scavenging": 9, "building": 3, "medicine": 3, "cooking": 3, "survival": 9, "magic": 2},
        "attributes": {"str": 5, "dex": 9, "agi": 10, "vit": 6, "int": 6, "luk": 8},
    },
    "strategist": {
        "specialty": "Strategist", "traits": ["pathfinder"],
        "stats": {"combat": 6, "scavenging": 7, "building": 6, "medicine": 5, "cooking": 3, "survival": 8, "magic": 6},
        "attributes": {"str": 4, "dex": 7, "agi": 6, "vit": 6, "int": 10, "luk": 8},
    },
    "support": {
        "specialty": "Field Support", "traits": ["scout"],
        "stats": {"combat": 5, "scavenging": 7, "building": 5, "medicine": 6, "cooking": 7, "survival": 7, "magic": 5},
        "attributes": {"str": 4, "dex": 7, "agi": 7, "vit": 6, "int": 8, "luk": 9},
    },
}

# id, display name, series, role, Champion rank, race, signature perk
CATALOG = [
    ("frieren", "Frieren", "Frieren: Beyond Journey's End", "mage", "S", "Elf", "millennia_of_magic"),
    ("fern", "Fern", "Frieren: Beyond Journey's End", "mage", "A", "Human", "zoltraak_precision"),
    ("ubel", "Übel", "Frieren: Beyond Journey's End", "duelist", "A", "Human", "cleaving_imagination"),
    ("maomao", "Maomao", "The Apothecary Diaries", "healer", "A", "Human", "poison_savant"),
    ("momo_ayase", "Momo Ayase", "DAN DA DAN", "mage", "A", "Human", "psychokinesis"),
    ("aira_shiratori", "Aira Shiratori", "DAN DA DAN", "duelist", "B", "Human", "acrobatic_silky"),
    ("marin_kitagawa", "Marin Kitagawa", "My Dress-Up Darling", "support", "C", "Human", "cosplay_heart"),
    ("yor_forger", "Yor Forger", "SPY x FAMILY", "duelist", "S", "Human", "thorn_princess"),
    ("anya_forger", "Anya Forger", "SPY x FAMILY", "strategist", "C", "Human", "telepathy"),
    ("makima", "Makima", "Chainsaw Man", "strategist", "S", "Devil", "control_devils_contract"),
    ("power", "Power", "Chainsaw Man", "vanguard", "A", "Fiend", "blood_weapons"),
    ("reze", "Reze", "Chainsaw Man", "duelist", "A", "Hybrid", "bomb_heart"),
    ("kobeni_higashiyama", "Kobeni Higashiyama", "Chainsaw Man", "scout", "B", "Human", "survival_panic"),
    ("mitsuri_kanroji", "Mitsuri Kanroji", "Demon Slayer", "vanguard", "A", "Human", "love_breathing"),
    ("shinobu_kocho", "Shinobu Kocho", "Demon Slayer", "healer", "A", "Human", "insect_breathing"),
    ("nezuko_kamado", "Nezuko Kamado", "Demon Slayer", "vanguard", "A", "Demon", "exploding_blood"),
    ("kanao_tsuyuri", "Kanao Tsuyuri", "Demon Slayer", "duelist", "B", "Human", "flower_breathing"),
    ("nobara_kugisaki", "Nobara Kugisaki", "Jujutsu Kaisen", "marksman", "A", "Human", "resonance"),
    ("maki_zenin", "Maki Zenin", "Jujutsu Kaisen", "vanguard", "S", "Human", "heavenly_restriction"),
    ("yuki_tsukumo", "Yuki Tsukumo", "Jujutsu Kaisen", "vanguard", "S", "Human", "star_rage"),
    ("rukia_kuchiki", "Rukia Kuchiki", "BLEACH", "duelist", "A", "Soul", "sode_no_shirayuki"),
    ("orihime_inoue", "Orihime Inoue", "BLEACH", "healer", "A", "Human", "phenomenon_rejection"),
    ("yoruichi_shihoin", "Yoruichi Shihōin", "BLEACH", "scout", "S", "Soul", "flash_goddess"),
    ("nami", "Nami", "One Piece", "strategist", "A", "Human", "weather_navigation"),
    ("nico_robin", "Nico Robin", "One Piece", "strategist", "A", "Human", "flower_flower_fruit"),
    ("boa_hancock", "Boa Hancock", "One Piece", "mage", "S", "Human", "love_love_fruit"),
    ("yamato", "Yamato", "One Piece", "vanguard", "S", "Oni", "guardian_wolf"),
    ("nefertari_vivi", "Nefertari Vivi", "One Piece", "support", "C", "Human", "desert_diplomacy"),
    ("hinata_hyuga", "Hinata Hyūga", "Naruto", "duelist", "A", "Human", "byakugan"),
    ("tsunade", "Tsunade", "Naruto", "healer", "S", "Human", "hundred_healings"),
    ("temari", "Temari", "Naruto", "marksman", "A", "Human", "wind_scythe"),
    ("mikasa_ackerman", "Mikasa Ackerman", "Attack on Titan", "duelist", "S", "Human", "ackerman_instinct"),
    ("annie_leonhart", "Annie Leonhart", "Attack on Titan", "vanguard", "A", "Titan Shifter", "female_titan"),
    ("historia_reiss", "Historia Reiss", "Attack on Titan", "support", "C", "Human", "true_queen"),
    ("ochaco_uraraka", "Ochaco Uraraka", "My Hero Academia", "support", "B", "Human", "zero_gravity"),
    ("momo_yaoyorozu", "Momo Yaoyorozu", "My Hero Academia", "strategist", "B", "Human", "creation"),
    ("mirko", "Mirko", "My Hero Academia", "vanguard", "S", "Human", "rabbit_hero"),
    ("faye_valentine", "Faye Valentine", "Cowboy Bebop", "marksman", "B", "Human", "red_tail_gambit"),
    ("motoko_kusanagi", "Motoko Kusanagi", "Ghost in the Shell", "strategist", "S", "Cyborg", "ghost_hacking"),
    ("revy", "Revy", "Black Lagoon", "marksman", "A", "Human", "two_hands"),
    ("erza_scarlet", "Erza Scarlet", "Fairy Tail", "vanguard", "S", "Human", "the_knight_requip"),
    ("lucy_heartfilia", "Lucy Heartfilia", "Fairy Tail", "mage", "A", "Human", "celestial_spirits"),
    ("rias_gremory", "Rias Gremory", "High School DxD", "mage", "S", "Devil", "power_of_destruction"),
    ("akeno_himejima", "Akeno Himejima", "High School DxD", "mage", "A", "Fallen Angel", "holy_lightning"),
    ("rem", "Rem", "Re:ZERO", "vanguard", "A", "Oni", "morning_star_mastery"),
    ("emilia", "Emilia", "Re:ZERO", "mage", "S", "Half-Elf", "spirit_arts"),
    ("echidna", "Echidna", "Re:ZERO", "strategist", "S", "Witch", "witch_of_greed"),
    ("asuna_yuuki", "Asuna Yuuki", "Sword Art Online", "duelist", "S", "Human", "lightning_flash"),
    ("sinon", "Sinon", "Sword Art Online", "marksman", "A", "Human", "hawkeye_sniper"),
    ("alice_zuberg", "Alice Zuberg", "Sword Art Online", "vanguard", "A", "Human", "fragrant_olive_sword"),
    ("kurisu_makise", "Kurisu Makise", "Steins;Gate", "strategist", "B", "Human", "future_gadget_genius"),
    ("holo", "Holo", "Spice and Wolf", "strategist", "S", "Wolf Deity", "wisewolf_harvest"),
    ("violet_evergarden", "Violet Evergarden", "Violet Evergarden", "support", "B", "Human", "memory_doll"),
    ("chisato_nishikigi", "Chisato Nishikigi", "Lycoris Recoil", "marksman", "S", "Human", "bullet_sight"),
    ("takina_inoue", "Takina Inoue", "Lycoris Recoil", "marksman", "B", "Human", "lycoris_precision"),
    ("vladilena_milize", "Vladilena Milizé", "86 EIGHTY-SIX", "strategist", "B", "Human", "bloody_regina"),
    ("zero_two", "Zero Two", "DARLING in the FRANXX", "vanguard", "S", "Klaxosaur Hybrid", "strelizia_partner"),
    ("ryuko_matoi", "Ryūko Matoi", "KILL la KILL", "vanguard", "S", "Human", "senketsu_sync"),
    ("satsuki_kiryuin", "Satsuki Kiryūin", "KILL la KILL", "strategist", "S", "Human", "junketsu_command"),
    ("yoko_littner", "Yoko Littner", "Gurren Lagann", "marksman", "A", "Human", "spiral_sniper"),
    ("cc", "C.C.", "Code Geass", "strategist", "S", "Immortal", "geass_code"),
    ("kallen_kozuki", "Kallen Kōzuki", "Code Geass", "vanguard", "A", "Human", "guren_pilot"),
    ("rin_tohsaka", "Rin Tohsaka", "Fate/stay night", "mage", "S", "Human", "jewel_magecraft"),
    ("sakura_matou", "Sakura Matou", "Fate/stay night", "mage", "S", "Human", "imaginary_numbers"),
    ("jeanne_darc", "Jeanne d'Arc", "Fate/Apocrypha", "vanguard", "S", "Human", "luminosite_eternelle"),
    ("kaguya_shinomiya", "Kaguya Shinomiya", "Kaguya-sama: Love Is War", "strategist", "B", "Human", "ice_cold_planning"),
    ("chika_fujiwara", "Chika Fujiwara", "Kaguya-sama: Love Is War", "support", "C", "Human", "chaos_secretary"),
    ("ai_hayasaka", "Ai Hayasaka", "Kaguya-sama: Love Is War", "scout", "B", "Human", "perfect_attendant"),
    ("kana_arima", "Kana Arima", "OSHI NO KO", "support", "B", "Human", "star_performer"),
    ("akane_kurokawa", "Akane Kurokawa", "OSHI NO KO", "strategist", "B", "Human", "method_profiling"),
    ("ruby_hoshino", "Ruby Hoshino", "OSHI NO KO", "support", "C", "Human", "idol_radiance"),
    ("mai_sakurajima", "Mai Sakurajima", "Rascal Does Not Dream", "support", "B", "Human", "adolescence_syndrome"),
    ("hitagi_senjougahara", "Hitagi Senjougahara", "Monogatari", "strategist", "B", "Human", "weightless_crab"),
    ("roxy_migurdia", "Roxy Migurdia", "Mushoku Tensei", "mage", "A", "Demon", "water_saint_magic"),
    ("sylphiette", "Sylphiette", "Mushoku Tensei", "healer", "A", "Elf", "silent_spellcasting"),
    ("marcille_donato", "Marcille Donato", "Delicious in Dungeon", "mage", "A", "Half-Elf", "dungeon_magic"),
    ("falin_touden", "Falin Touden", "Delicious in Dungeon", "healer", "A", "Human", "resurrection_magic"),
    ("riza_hawkeye", "Riza Hawkeye", "Fullmetal Alchemist", "marksman", "B", "Human", "hawkeyes_aim"),
    ("winry_rockbell", "Winry Rockbell", "Fullmetal Alchemist", "support", "C", "Human", "automail_engineer"),
    ("android_18", "Android 18", "Dragon Ball", "vanguard", "S", "Android", "infinite_energy"),
    ("bulma", "Bulma", "Dragon Ball", "strategist", "B", "Human", "capsule_engineering"),
    ("usagi_tsukino", "Usagi Tsukino", "Sailor Moon", "mage", "S", "Human", "silver_crystal"),
    ("rei_ayanami", "Rei Ayanami", "Neon Genesis Evangelion", "vanguard", "A", "Human", "eva_unit_zero"),
    ("asuka_langley", "Asuka Langley", "Neon Genesis Evangelion", "vanguard", "A", "Human", "eva_unit_two"),
    ("homura_akemi", "Homura Akemi", "Puella Magi Madoka Magica", "strategist", "S", "Human", "time_stop"),
    ("cha_haein", "Cha Hae-In", "Solo Leveling", "duelist", "S", "Human", "mana_scent"),
    ("han_sooyoung", "Han Sooyoung", "Omniscient Reader's Viewpoint", "strategist", "S", "Human", "avatar_author"),
    ("endorsi_jahad", "Endorsi Jahad", "Tower of God", "vanguard", "A", "Human", "princess_of_jahad"),
    ("sung_jinwoo", "Sung Jinwoo", "Solo Leveling", "vanguard", "S", "Human", "shadow_monarch"),
    ("kim_dokja", "Kim Dokja", "Omniscient Reader's Viewpoint", "strategist", "S", "Human", "omniscient_reader"),
    ("satoru_gojo", "Satoru Gojo", "Jujutsu Kaisen", "mage", "S", "Human", "limitless_six_eyes"),
    ("levi_ackerman", "Levi Ackerman", "Attack on Titan", "duelist", "S", "Human", "humanitys_strongest"),
    ("loid_forger", "Loid Forger", "SPY x FAMILY", "strategist", "A", "Human", "twilight"),
    ("himmel", "Himmel", "Frieren: Beyond Journey's End", "duelist", "S", "Human", "heroes_legacy"),
    ("jinshi", "Jinshi", "The Apothecary Diaries", "strategist", "B", "Human", "imperial_grace"),
    ("roronoa_zoro", "Roronoa Zoro", "One Piece", "duelist", "S", "Human", "three_sword_style"),
    ("kakashi_hatake", "Kakashi Hatake", "Naruto", "strategist", "S", "Human", "copy_ninja"),
    ("guts", "Guts", "Berserk", "vanguard", "S", "Human", "dragonslayer"),
    ("twenty_fifth_bam", "Twenty-Fifth Bam", "Tower of God", "mage", "S", "Irregular", "shinsu_mastery"),
    ("yoo_joonghyuk", "Yoo Joonghyuk", "Omniscient Reader's Viewpoint", "vanguard", "S", "Human", "regressors_resolve"),
]

# These ranks describe real-world recognition within the intended audience,
# rather than how powerful a character is in her source material. Keeping the
# correction separate preserves the authored catalog rows and makes later
# popularity passes easy to review.
POPULARITY_RANK_OVERRIDES = {
    "maomao": "S",
    "marin_kitagawa": "S",
    "power": "S",
    "aira_shiratori": "C",
    "shinobu_kocho": "S",
    "nezuko_kamado": "S",
    "nobara_kugisaki": "S",
    "maki_zenin": "A",
    "yuki_tsukumo": "C",
    "rukia_kuchiki": "S",
    "nami": "S",
    "nico_robin": "S",
    "nefertari_vivi": "B",
    "hinata_hyuga": "S",
    "tsunade": "A",
    "temari": "B",
    "historia_reiss": "B",
    "ochaco_uraraka": "A",
    "mirko": "B",
    "faye_valentine": "A",
    "motoko_kusanagi": "A",
    "erza_scarlet": "S",
    "rem": "S",
    "echidna": "A",
    "alice_zuberg": "B",
    "kurisu_makise": "S",
    "violet_evergarden": "S",
    "takina_inoue": "B",
    "ryuko_matoi": "A",
    "satsuki_kiryuin": "A",
    "kallen_kozuki": "B",
    "kaguya_shinomiya": "S",
    "chika_fujiwara": "A",
    "ai_hayasaka": "A",
    "kana_arima": "A",
    "ruby_hoshino": "A",
    "mai_sakurajima": "S",
    "hitagi_senjougahara": "S",
    "sylphiette": "B",
    "falin_touden": "B",
    "riza_hawkeye": "A",
    "winry_rockbell": "A",
    "rei_ayanami": "S",
    "asuka_langley": "S",
    "cha_haein": "A",
    "han_sooyoung": "A",
    "endorsi_jahad": "B",
}


def _build_champion(entry: tuple[str, str, str, str, str, str, str]) -> tuple[str, dict]:
    champion_id, name, series, role, rank, race, signature = entry
    rank = POPULARITY_RANK_OVERRIDES.get(champion_id, rank)
    profile = deepcopy(ROLE_TEMPLATES[role])
    rank_adjustment = {"C": -1, "B": 0, "A": 1, "S": 2}[rank]
    profile["stats"] = {key: max(1, min(10, value + rank_adjustment)) for key, value in profile["stats"].items()}
    profile["attributes"] = {key: max(1, min(12, value + rank_adjustment)) for key, value in profile["attributes"].items()}
    profile.update({
        "name": name, "race": race, "gender": "female" if CATALOG.index(entry) < 88 else "male",
        "series": series, "source_kind": "champion", "champion_rank": rank,
        "traits": list(dict.fromkeys(profile["traits"] + [signature])), "portrait": "",
    })
    return champion_id, profile


EXPANDED_CHAMPIONS = dict(_build_champion(entry) for entry in CATALOG)
CHAMPION_PERKS = {
    signature: {
        "name": signature.replace("_", " ").title(),
        "description": f"{name}'s defining talent from {series}.",
        "effect": "A Champion signature perk that can unlock matching special mission routes.",
    }
    for _, name, series, _, _, _, signature in CATALOG
}

assert len(CATALOG) == 100
assert len(EXPANDED_CHAMPIONS) == 100
