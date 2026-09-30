# Fortcamp Champion Portrait Tracker

This file records every Champion portrait contact sheet, its exact cell order, review status, and import status. Keep the source sheet and its row/column order unchanged after approval so each crop can be assigned to the correct Champion ID.

## Status legend

- `Planned` — assigned to a batch but not generated.
- `Generated` — a contact sheet exists but has not been approved.
- `Approved` — every cell has been checked and accepted.
- `Imported` — individual full and thumbnail files have been created and connected to the Champion ID.
- `Redo` — the cell or batch must be regenerated.

## Art-style references

Upload these three files with every Champion batch:

1. `reference/portrait-art-reference.png` — primary painterly anime-fantasy finish, warm cinematic light, rich detail, and atmospheric background treatment.
2. `portraits/human_female_healer.png` — primary reference for soft facial rendering, luminous eyes, natural posture, warm bloom, and portrait framing.
3. `portraits/human_female_melee.png` — secondary reference for material detail, stronger contrast, equipment rendering, and role readability.

Use the references only for Fortcamp's shared visual language. Do not copy their faces, clothing, poses, or character identities. Each Champion must retain her recognizable canonical identity.

## Batch 001 — `champion_batch_001.png`

*Iconic heroines and fighters*

**Layout:** 4 columns × 4 rows  
**Filename:** `champion_batch_001.png`  
**Batch status:** Imported — `champions/champion_batch_001.png`

| Cell | Champion ID | Character | Series | Status | Notes |
|---|---|---|---|---|---|
| R1C1 | `frieren` | Frieren | Frieren: Beyond Journey's End | Imported | White-haired elf mage, calm expression |
| R1C2 | `fern` | Fern | Frieren: Beyond Journey's End | Imported | Long purple hair, composed human mage |
| R1C3 | `ubel` | Übel | Frieren: Beyond Journey's End | Imported | Green hair, distinctive eyes, confident mage |
| R1C4 | `maomao` | Maomao | The Apothecary Diaries | Imported | Green hair, freckles, practical apothecary identity |
| R2C1 | `yor_forger` | Yor Forger | SPY x FAMILY | Imported | Black hair, red eyes, elegant assassin identity |
| R2C2 | `makima` | Makima | Chainsaw Man | Imported | Red braided hair, ringed golden-red eyes, controlled expression |
| R2C3 | `power` | Power | Chainsaw Man | Imported | Long blonde hair, red horns, cross-pattern eyes |
| R2C4 | `reze` | Reze | Chainsaw Man | Imported | Dark hair, soft expression, subtle bomb-hybrid cues |
| R3C1 | `mitsuri_kanroji` | Mitsuri Kanroji | Demon Slayer | Imported | Pink-and-green hair, bright compassionate expression |
| R3C2 | `shinobu_kocho` | Shinobu Kocho | Demon Slayer | Imported | Butterfly hair ornament, dark purple hair, gentle unreadable smile |
| R3C3 | `nobara_kugisaki` | Nobara Kugisaki | Jujutsu Kaisen | Imported | Short auburn hair, confident expression, hammer-and-nail identity |
| R3C4 | `maki_zenin` | Maki Zenin | Jujutsu Kaisen | Imported | Dark green hair, glasses, athletic weapons specialist |
| R4C1 | `rukia_kuchiki` | Rukia Kuchiki | BLEACH | Imported | Short black hair, composed Soul Reaper identity |
| R4C2 | `yoruichi_shihoin` | Yoruichi Shihōin | BLEACH | Imported | Purple hair, golden eyes, confident martial identity |
| R4C3 | `nami` | Nami | One Piece | Imported | Orange hair, navigator and weather-staff identity |
| R4C4 | `nico_robin` | Nico Robin | One Piece | Imported | Long black hair, calm archaeologist identity |

### Batch 001 generation prompt

Upload the three files listed under **Art-style references**, then paste the following prompt:

> Generate a completely new image from scratch. Create one high-resolution square 4-column by 4-row contact sheet containing exactly 16 separate upper-torso character portraits for Fortcamp. Every cell must contain the specific character assigned below, in the exact row and column listed. Do not reorder, replace, duplicate, merge, or omit characters.
>
> **Reference hierarchy:** Use `portrait-art-reference.png` for the primary painterly anime-fantasy finish, warm cinematic rim light, rich hand-painted detail, and atmospheric medieval-fantasy backgrounds. Use `human_female_healer.png` for soft expressive facial rendering, luminous eyes, natural posture, warm bloom, and relaxed portrait framing. Use `human_female_melee.png` for detailed materials, stronger contrast, equipment rendering, and role readability. Use these references only for visual language and production quality. Do not copy their faces, hair, clothing, anatomy, or poses.
>
> **Exact cell assignment:**
> - Row 1, Column 1: Frieren from *Frieren: Beyond Journey's End*.
> - Row 1, Column 2: Fern from *Frieren: Beyond Journey's End*.
> - Row 1, Column 3: Übel from *Frieren: Beyond Journey's End*.
> - Row 1, Column 4: Maomao from *The Apothecary Diaries*.
> - Row 2, Column 1: Yor Forger from *SPY x FAMILY*.
> - Row 2, Column 2: Makima from *Chainsaw Man*.
> - Row 2, Column 3: Power from *Chainsaw Man*.
> - Row 2, Column 4: Reze from *Chainsaw Man*.
> - Row 3, Column 1: Mitsuri Kanroji from *Demon Slayer*.
> - Row 3, Column 2: Shinobu Kocho from *Demon Slayer*.
> - Row 3, Column 3: Nobara Kugisaki from *Jujutsu Kaisen*.
> - Row 3, Column 4: Maki Zenin from *Jujutsu Kaisen*.
> - Row 4, Column 1: Rukia Kuchiki from *BLEACH*.
> - Row 4, Column 2: Yoruichi Shihōin from *BLEACH*.
> - Row 4, Column 3: Nami from *One Piece*.
> - Row 4, Column 4: Nico Robin from *One Piece*.
>
> **Identity requirements:** Each character must be immediately recognizable from their canonical facial structure, hair shape and color, eyes, species traits, signature clothing language, and one restrained role cue or signature item when useful. Preserve canonical gender, skin tone, age group, and distinctive traits. Do not blend characters from the same series together. Do not give them the faces, clothes, or hairstyles from the uploaded Fortcamp references. Avoid same-face syndrome. Each cell must depict only its assigned character.
>
> **Fortcamp adaptation:** Render every character as a polished Fortcamp Champion portrait while preserving their identity. Use tasteful, practical, nonsexual presentation and their recognizable canonical costume or a faithful medieval-fantasy adaptation of it. Keep signature weapons, magical effects, or role props compact and entirely within the correct cell. Favor expressive natural presence over rigid identification-photo poses.
>
> **Layout:** Exactly 16 equal square cells in a clean 4×4 grid. Use consistent upper-torso framing and camera distance, with generous clearance around hair, ears, horns, weapons, and effects. Use thin clean separators. Nothing may cross a cell boundary. Most characters should look toward the viewer with small natural changes in shoulder angle, expression, hand placement, and head tilt.
>
> **Avoid:** swapped positions, missing characters, duplicates, hybridized identities, incorrect signature hair colors, same-face syndrome, generic substitute characters, elderly versions, chibi proportions, sexualized framing, photographic realism, 3D CGI, flat cel shading, text, names, labels, numbers, logos, watermarks, decorative outer frames, merged cells, or elements crossing cell boundaries.

### Batch 001 import manifest

The splitter should read cells from left to right and top to bottom:

```json
[
  "frieren", "fern", "ubel", "maomao",
  "yor_forger", "makima", "power", "reze",
  "mitsuri_kanroji", "shinobu_kocho", "nobara_kugisaki", "maki_zenin",
  "rukia_kuchiki", "yoruichi_shihoin", "nami", "nico_robin"
]
```

Do not mark this batch `Approved` until every cell has been visually checked against this table. A wrong cell should be recorded as `Redo`; never silently assign it to a different Champion merely because it resembles someone else.

## Planned batch lists

Use the Batch 001 prompt and replace only its **Exact cell assignment** section with the relevant list below. Keep the same three art-style references and save each result under the stated filename.

### Batch 002 — `champion_batch_002.png`

**Batch status:** Imported — `champions/champion_batch_002.png`

| Cell | Champion ID | Character | Series |
|---|---|---|---|
| R1C1 | `saber` | Saber | Fate/stay night |
| R1C2 | `momo_ayase` | Momo Ayase | DAN DA DAN |
| R1C3 | `aira_shiratori` | Aira Shiratori | DAN DA DAN |
| R1C4 | `marin_kitagawa` | Marin Kitagawa | My Dress-Up Darling |
| R2C1 | `kobeni_higashiyama` | Kobeni Higashiyama | Chainsaw Man |
| R2C2 | `nezuko_kamado` | Nezuko Kamado | Demon Slayer |
| R2C3 | `kanao_tsuyuri` | Kanao Tsuyuri | Demon Slayer |
| R2C4 | `yuki_tsukumo` | Yuki Tsukumo | Jujutsu Kaisen |
| R3C1 | `orihime_inoue` | Orihime Inoue | BLEACH |
| R3C2 | `boa_hancock` | Boa Hancock | One Piece |
| R3C3 | `yamato` | Yamato | One Piece |
| R3C4 | `nefertari_vivi` | Nefertari Vivi | One Piece |
| R4C1 | `hinata_hyuga` | Hinata Hyūga | Naruto |
| R4C2 | `tsunade` | Tsunade | Naruto |
| R4C3 | `temari` | Temari | Naruto |
| R4C4 | `mikasa_ackerman` | Mikasa Ackerman | Attack on Titan |

### Batch 003 — `champion_batch_003.png`

**Batch status:** Imported — `champions/champion_batch_003.png`

| Cell | Champion ID | Character | Series |
|---|---|---|---|
| R1C1 | `annie_leonhart` | Annie Leonhart | Attack on Titan |
| R1C2 | `historia_reiss` | Historia Reiss | Attack on Titan |
| R1C3 | `ochaco_uraraka` | Ochaco Uraraka | My Hero Academia |
| R1C4 | `momo_yaoyorozu` | Momo Yaoyorozu | My Hero Academia |
| R2C1 | `mirko` | Mirko | My Hero Academia |
| R2C2 | `faye_valentine` | Faye Valentine | Cowboy Bebop |
| R2C3 | `motoko_kusanagi` | Motoko Kusanagi | Ghost in the Shell |
| R2C4 | `revy` | Revy | Black Lagoon |
| R3C1 | `erza_scarlet` | Erza Scarlet | Fairy Tail |
| R3C2 | `lucy_heartfilia` | Lucy Heartfilia | Fairy Tail |
| R3C3 | `rias_gremory` | Rias Gremory | High School DxD |
| R3C4 | `akeno_himejima` | Akeno Himejima | High School DxD |
| R4C1 | `rem` | Rem | Re:ZERO |
| R4C2 | `emilia` | Emilia | Re:ZERO |
| R4C3 | `echidna` | Echidna | Re:ZERO |
| R4C4 | `asuna_yuuki` | Asuna Yuuki | Sword Art Online |

### Batch 004 — `champion_batch_004.png`

**Batch status:** Imported — `champions/champion_batch_004.png`

| Cell | Champion ID | Character | Series |
|---|---|---|---|
| R1C1 | `sinon` | Sinon | Sword Art Online |
| R1C2 | `alice_zuberg` | Alice Zuberg | Sword Art Online |
| R1C3 | `kurisu_makise` | Kurisu Makise | Steins;Gate |
| R1C4 | `holo` | Holo | Spice and Wolf |
| R2C1 | `violet_evergarden` | Violet Evergarden | Violet Evergarden |
| R2C2 | `chisato_nishikigi` | Chisato Nishikigi | Lycoris Recoil |
| R2C3 | `takina_inoue` | Takina Inoue | Lycoris Recoil |
| R2C4 | `vladilena_milize` | Vladilena Milizé | 86 EIGHTY-SIX |
| R3C1 | `zero_two` | Zero Two | DARLING in the FRANXX |
| R3C2 | `ryuko_matoi` | Ryūko Matoi | KILL la KILL |
| R3C3 | `satsuki_kiryuin` | Satsuki Kiryūin | KILL la KILL |
| R3C4 | `yoko_littner` | Yoko Littner | Gurren Lagann |
| R4C1 | `cc` | C.C. | Code Geass |
| R4C2 | `kallen_kozuki` | Kallen Kōzuki | Code Geass |
| R4C3 | `rin_tohsaka` | Rin Tohsaka | Fate/stay night |
| R4C4 | `sakura_matou` | Sakura Matou | Fate/stay night |

### Batch 005 — `champion_batch_005.png`

**Batch status:** Imported — `champions/champion_batch_005.png`

| Cell | Champion ID | Character | Series |
|---|---|---|---|
| R1C1 | `jeanne_darc` | Jeanne d'Arc | Fate/Apocrypha |
| R1C2 | `kaguya_shinomiya` | Kaguya Shinomiya | Kaguya-sama: Love Is War |
| R1C3 | `chika_fujiwara` | Chika Fujiwara | Kaguya-sama: Love Is War |
| R1C4 | `ai_hayasaka` | Ai Hayasaka | Kaguya-sama: Love Is War |
| R2C1 | `kana_arima` | Kana Arima | OSHI NO KO |
| R2C2 | `akane_kurokawa` | Akane Kurokawa | OSHI NO KO |
| R2C3 | `ruby_hoshino` | Ruby Hoshino | OSHI NO KO |
| R2C4 | `mai_sakurajima` | Mai Sakurajima | Rascal Does Not Dream |
| R3C1 | `hitagi_senjougahara` | Hitagi Senjougahara | Monogatari |
| R3C2 | `roxy_migurdia` | Roxy Migurdia | Mushoku Tensei |
| R3C3 | `sylphiette` | Sylphiette | Mushoku Tensei |
| R3C4 | `marcille_donato` | Marcille Donato | Delicious in Dungeon |
| R4C1 | `falin_touden` | Falin Touden | Delicious in Dungeon |
| R4C2 | `riza_hawkeye` | Riza Hawkeye | Fullmetal Alchemist |
| R4C3 | `winry_rockbell` | Winry Rockbell | Fullmetal Alchemist |
| R4C4 | `android_18` | Android 18 | Dragon Ball |

## Remaining Champion batches

Batches 006–014 cover every Champion not already assigned to Batches 001–005. Batches 006–013 contain women; Batch 014 closes the remaining women and the male Champion catalog. Use the same neutral Batch 001 generation instructions and the exact cell order below.

### Batch 006 — `champion_batch_006.png`

**Batch status:** Imported — `champions/champion_batch_006.png`

| Cell | Champion ID | Character | Series |
|---|---|---|---|
| R1C1 | `sword_maiden` | Sword Maiden | Goblin Slayer |
| R1C2 | `seraphine_vale` | Seraphine Vale | Original |
| R1C3 | `anya_forger` | Anya Forger | SPY x FAMILY |
| R1C4 | `bulma` | Bulma | Dragon Ball |
| R2C1 | `usagi_tsukino` | Usagi Tsukino | Sailor Moon |
| R2C2 | `rei_ayanami` | Rei Ayanami | Neon Genesis Evangelion |
| R2C3 | `asuka_langley` | Asuka Langley | Neon Genesis Evangelion |
| R2C4 | `homura_akemi` | Homura Akemi | Puella Magi Madoka Magica |
| R3C1 | `cha_haein` | Cha Hae-In | Solo Leveling |
| R3C2 | `han_sooyoung` | Han Sooyoung | Omniscient Reader's Viewpoint |
| R3C3 | `endorsi_jahad` | Endorsi Jahad | Tower of God |
| R3C4 | `megumin` | Megumin | KonoSuba |
| R4C1 | `mikoto_misaka` | Mikoto Misaka | A Certain Scientific Railgun |
| R4C2 | `kurumi_tokisaki` | Kurumi Tokisaki | Date A Live |
| R4C3 | `miku_nakano` | Miku Nakano | The Quintessential Quintuplets |
| R4C4 | `hitori_gotoh` | Hitori Gotoh | Bocchi the Rock! |

### Batch 007 — `champion_batch_007.png`

**Batch status:** Imported — `champions/champion_batch_007.png`

| Cell | Champion ID | Character | Series |
|---|---|---|---|
| R1C1 | `aqua` | Aqua | KonoSuba |
| R1C2 | `darkness` | Darkness | KonoSuba |
| R1C3 | `esdeath` | Esdeath | Akame ga Kill! |
| R1C4 | `raphtalia` | Raphtalia | The Rising of the Shield Hero |
| R2C1 | `albedo` | Albedo | Overlord |
| R2C2 | `yukino_yukinoshita` | Yukino Yukinoshita | My Teen Romantic Comedy SNAFU |
| R2C3 | `shoko_komi` | Shoko Komi | Komi Can't Communicate |
| R2C4 | `taiga_aisaka` | Taiga Aisaka | Toradora! |
| R3C1 | `tohru` | Tohru | Miss Kobayashi's Dragon Maid |
| R3C2 | `hestia` | Hestia | Is It Wrong to Try to Pick Up Girls in a Dungeon? |
| R3C3 | `chizuru_mizuhara` | Chizuru Mizuhara | Rent-A-Girlfriend |
| R3C4 | `tohka_yatogami` | Tohka Yatogami | Date A Live |
| R4C1 | `anna_yamada` | Anna Yamada | The Dangers in My Heart |
| R4C2 | `asa_mitaka` | Asa Mitaka | Chainsaw Man |
| R4C3 | `yoru_war_devil` | Yoru | Chainsaw Man |
| R4C4 | `roxana_agriche` | Roxana Agriche | Roxana |

### Batch 008 — `champion_batch_008.png`

**Batch status:** Imported — `champions/champion_batch_008.png`

| Cell | Champion ID | Character | Series |
|---|---|---|---|
| R1C1 | `navier_trovi` | Navier Ellie Trovi | The Remarried Empress |
| R1C2 | `medea_solon` | Medea Solon | Your Throne |
| R1C3 | `penelope_eckart` | Penelope Eckart | Villains Are Destined to Die |
| R1C4 | `jiyoung_yoo` | Jiyoung Yoo | Eleceed |
| R2C1 | `nino_nakano` | Nino Nakano | The Quintessential Quintuplets |
| R2C2 | `yunyun` | Yunyun | KonoSuba |
| R2C3 | `wiz` | Wiz | KonoSuba |
| R2C4 | `shalltear_bloodfallen` | Shalltear Bloodfallen | Overlord |
| R3C1 | `shion` | Shion | That Time I Got Reincarnated as a Slime |
| R3C2 | `shuna` | Shuna | That Time I Got Reincarnated as a Slime |
| R3C3 | `milim_nava` | Milim Nava | That Time I Got Reincarnated as a Slime |
| R3C4 | `ais_wallenstein` | Ais Wallenstein | Is It Wrong to Try to Pick Up Girls in a Dungeon? |
| R4C1 | `ryuu_lion` | Ryuu Lion | Is It Wrong to Try to Pick Up Girls in a Dungeon? |
| R4C2 | `kotori_itsuka` | Kotori Itsuka | Date A Live |
| R4C3 | `origami_tobiichi` | Origami Tobiichi | Date A Live |
| R4C4 | `ichika_nakano` | Ichika Nakano | The Quintessential Quintuplets |

### Batch 009 — `champion_batch_009.png`

**Batch status:** Imported — `champions/champion_batch_009.png`

| Cell | Champion ID | Character | Series |
|---|---|---|---|
| R1C1 | `yotsuba_nakano` | Yotsuba Nakano | The Quintessential Quintuplets |
| R1C2 | `itsuki_nakano` | Itsuki Nakano | The Quintessential Quintuplets |
| R1C3 | `yui_yuigahama` | Yui Yuigahama | My Teen Romantic Comedy SNAFU |
| R1C4 | `iroha_isshiki` | Iroha Isshiki | My Teen Romantic Comedy SNAFU |
| R2C1 | `rikka_takanashi` | Rikka Takanashi | Love, Chunibyo & Other Delusions! |
| R2C2 | `nijika_ijichi` | Nijika Ijichi | Bocchi the Rock! |
| R2C3 | `ikuyo_kita` | Ikuyo Kita | Bocchi the Rock! |
| R2C4 | `seiko_ayase` | Seiko Ayase | DAN DA DAN |
| R3C1 | `himiko_toga` | Himiko Toga | My Hero Academia |
| R3C2 | `ino_yamanaka` | Ino Yamanaka | Naruto |
| R3C3 | `perona` | Perona | One Piece |
| R3C4 | `jewelry_bonney` | Jewelry Bonney | One Piece |
| R4C1 | `pieck_finger` | Pieck Finger | Attack on Titan |
| R4C2 | `hwa_ryun` | Hwa Ryun | Tower of God |
| R4C3 | `yuri_jahad` | Yuri Jahad | Tower of God |
| R4C4 | `ihwa` | Ihwa | Hero Killer |

### Batch 010 — `champion_batch_010.png`

**Batch status:** Imported — `champions/champion_batch_010.png`

| Cell | Champion ID | Character | Series |
|---|---|---|---|
| R1C1 | `raviel_ivansia` | Raviel Ivansia | SSS-Class Revival Hunter |
| R1C2 | `psyche_callista` | Psyche Callista | Your Throne |
| R1C3 | `maximilian_calypse` | Maximilian Calypse | Under the Oak Tree |
| R1C4 | `juvelian_floyen` | Juvelian Floyen | Father, I Don't Want This Marriage |
| R2C1 | `cayena_hill` | Cayena Hill | The Villainess Is a Marionette |
| R2C2 | `shuri_von_neuschwanstein` | Shuri von Neuschwanstein | A Stepmother's Märchen |
| R2C3 | `eris_miserian` | Eris Miserian | Kill the Villainess |
| R2C4 | `deborah_seymour` | Deborah Seymour | The Perks of Being a Villainess |
| R3C1 | `florentia_lombardi` | Florentia Lombardi | I Shall Master This Family |
| R3C2 | `ryo_yamada` | Ryo Yamada | Bocchi the Rock! |
| R3C3 | `kanna_kamui` | Kanna Kamui | Miss Kobayashi's Dragon Maid |
| R3C4 | `elma` | Elma | Miss Kobayashi's Dragon Maid |
| R4C1 | `ruka_sarashina` | Ruka Sarashina | Rent-A-Girlfriend |
| R4C2 | `sumi_sakurasawa` | Sumi Sakurasawa | Rent-A-Girlfriend |
| R4C3 | `mami_nanami` | Mami Nanami | Rent-A-Girlfriend |
| R4C4 | `rumiko_manbagi` | Rumiko Manbagi | Komi Can't Communicate |

### Batch 011 — `champion_batch_011.png`

**Batch status:** Imported — `champions/champion_batch_011.png`

| Cell | Champion ID | Character | Series |
|---|---|---|---|
| R1C1 | `shizuka_hiratsuka` | Shizuka Hiratsuka | My Teen Romantic Comedy SNAFU |
| R1C2 | `saki_kawasaki` | Saki Kawasaki | My Teen Romantic Comedy SNAFU |
| R1C3 | `minori_kushieda` | Minori Kushieda | Toradora! |
| R1C4 | `ami_kawashima` | Ami Kawashima | Toradora! |
| R2C1 | `yuki_nagato` | Yuki Nagato | The Melancholy of Haruhi Suzumiya |
| R2C2 | `mikuru_asahina` | Mikuru Asahina | The Melancholy of Haruhi Suzumiya |
| R2C3 | `tsuyu_asui` | Tsuyu Asui | My Hero Academia |
| R2C4 | `kyoka_jiro` | Kyoka Jiro | My Hero Academia |
| R3C1 | `mina_ashido` | Mina Ashido | My Hero Academia |
| R3C2 | `mei_hatsume` | Mei Hatsume | My Hero Academia |
| R3C3 | `kurenai_yuhi` | Kurenai Yuhi | Naruto |
| R3C4 | `anko_mitarashi` | Anko Mitarashi | Naruto |
| R4C1 | `shizune` | Shizune | Naruto |
| R4C2 | `tenten` | Tenten | Naruto |
| R4C3 | `karin_uzumaki` | Karin Uzumaki | Naruto |
| R4C4 | `tashigi` | Tashigi | One Piece |

### Batch 012 — `champion_batch_012.png`

**Batch status:** Imported — `champions/champion_batch_012.png`

| Cell | Champion ID | Character | Series |
|---|---|---|---|
| R1C1 | `carrot` | Carrot | One Piece |
| R1C2 | `vinsmoke_reiju` | Vinsmoke Reiju | One Piece |
| R1C3 | `ulti` | Ulti | One Piece |
| R1C4 | `kozuki_hiyori` | Kozuki Hiyori | One Piece |
| R2C1 | `soi_fon` | Soi Fon | BLEACH |
| R2C2 | `retsu_unohana` | Retsu Unohana | BLEACH |
| R2C3 | `nelliel_tu_oderschvank` | Nelliel Tu Odelschwanck | BLEACH |
| R2C4 | `riruka_dokugamine` | Riruka Dokugamine | BLEACH |
| R3C1 | `shoko_ieiri` | Shoko Ieiri | Jujutsu Kaisen |
| R3C2 | `utahime_iori` | Utahime Iori | Jujutsu Kaisen |
| R3C3 | `kasumi_miwa` | Kasumi Miwa | Jujutsu Kaisen |
| R3C4 | `aoi_kanzaki` | Aoi Kanzaki | Demon Slayer |
| R4C1 | `rachel_tower` | Rachel | Tower of God |
| R4C2 | `melissa_podebrat` | Melissa Podebrat | Beware the Villainess! |
| R4C3 | `latte_ectrie` | Latte Ectrie | Miss Not-So Sidekick |
| R4C4 | `hanabi_hyuga` | Hanabi Hyuga | Naruto |

### Batch 013 — `champion_batch_013.png`

**Batch status:** Imported — `champions/champion_batch_013.png`

| Cell | Champion ID | Character | Series |
|---|---|---|---|
| R1C1 | `isane_kotetsu` | Isane Kotetsu | BLEACH |
| R1C2 | `lisa_yadomaru` | Lisa Yadomaru | BLEACH |
| R1C3 | `kukaku_shiba` | Kukaku Shiba | BLEACH |
| R1C4 | `makino` | Makino | One Piece |
| R2C1 | `marguerite` | Marguerite | One Piece |
| R2C2 | `petra_ral` | Petra Ral | Attack on Titan |
| R2C3 | `hana_inuzuka` | Hana Inuzuka | Naruto |
| R2C4 | `ayame_ichiraku` | Ayame | Naruto |
| R3C1 | `tsume_inuzuka` | Tsume Inuzuka | Naruto |
| R3C2 | `samui` | Samui | Naruto |
| R3C3 | `karui` | Karui | Naruto |
| R3C4 | `mabui` | Mabui | Naruto |
| R4C1 | `yugao_uzuki` | Yugao Uzuki | Naruto |
| R4C2 | `kaya` | Kaya | One Piece |
| R4C3 | `nojiko` | Nojiko | One Piece |
| R4C4 | `conis` | Conis | One Piece |

### Batch 014 — `champion_batch_014.png`

**Batch status:** Imported — `champions/champion_batch_014.png`

| Cell | Champion ID | Character | Series |
|---|---|---|---|
| R1C1 | `rico_brzenska` | Rico Brzenska | Attack on Titan |
| R1C2 | `nifa` | Nifa | Attack on Titan |
| R1C3 | `mina_carolina` | Mina Carolina | Attack on Titan |
| R1C4 | `goblin_slayer` | Goblin Slayer | Goblin Slayer |
| R2C1 | `sung_jinwoo` | Sung Jinwoo | Solo Leveling |
| R2C2 | `kim_dokja` | Kim Dokja | Omniscient Reader's Viewpoint |
| R2C3 | `satoru_gojo` | Satoru Gojo | Jujutsu Kaisen |
| R2C4 | `levi_ackerman` | Levi Ackerman | Attack on Titan |
| R3C1 | `loid_forger` | Loid Forger | SPY x FAMILY |
| R3C2 | `himmel` | Himmel | Frieren: Beyond Journey's End |
| R3C3 | `jinshi` | Jinshi | The Apothecary Diaries |
| R3C4 | `roronoa_zoro` | Roronoa Zoro | One Piece |
| R4C1 | `kakashi_hatake` | Kakashi Hatake | Naruto |
| R4C2 | `guts` | Guts | Berserk |
| R4C3 | `twenty_fifth_bam` | Twenty-Fifth Bam | Tower of God |
| R4C4 | `yoo_joonghyuk` | Yoo Joonghyuk | Omniscient Reader's Viewpoint |








