# Fortcamp portrait batch generation

October 3 installation follow-up: batches 002 and 003 approved and consumed into dev, sixteen pools/320 portraits with stable IDs and separate square/original assets. Staged sheets and exact prompts retained. Twelve male generation targets remain; selective female quality review is deferred and tracked in docs/art/MALE_PORTRAIT_ROLLOUT.md.

October 3 batch 003: eight additional male sheets staged (Revenant/Vampire/Ogre/Troll melee, Alien ranged, Undead/Manaforged/Dreamkin magic), with exact expanded prompts in staging-portraits/MALE_BATCH_003.md. Same full production male approach and style/presentation reference roles; no female counterpart generation references. Not imported. Current and legacy prompts remain intact.

October 3 batch 002: eight additional male sheets staged for review (Bugbear/Lizardfolk/Minotaur/Dragonkin melee; Harpy/Centaur/Faun/Catfolk ranged). Images and exact expanded prompts are in staging-portraits/MALE_BATCH_002.md. Used the same full production male template and reference roles as approved batch 001, with species-specific anatomy. Not imported yet. Production and legacy prompts below remain intact.

October 3 batch 001: eight male sheets generated with the full production male prompt and per-race biology blocks, approved by the user and installed in dev. See `staging-portraits/MALE_BATCH_001.md` for images and exact expanded prompts, and `docs/art/MALE_PORTRAIT_ROLLOUT.md` for remaining targets. Canonical source sheets are in portraits/. Final Halfling is a fresh second generation; v1 is retained only for comparison. Current production prompts and legacy sections below remain intact.

October 3 male restart: the user approved `staging-portraits/goblin_male_ranged.png`, generated using the production male prompt, authoritative art reference and male Human presentation reference only. Exact expanded prompt is beside it in `goblin_male_ranged.prompt.md`. Installed twenty ranged portraits and twenty melee portraits from the earlier approved `goblin_male_melee_style_test_v2.png`. Canonical source copies are `portraits/goblin_male_ranged.png` and `portraits/goblin_male_melee.png`. Each pool has square full/thumb assets and separate uncropped originals. Existing approved male/female prompts and legacy sections remain unchanged.

Generate one contact sheet per portrait set, then use the importer to split it into twenty full portraits and twenty roster thumbnails. Keep one consistent visual style across every batch.

## Current production prompts

Use these gender-specific prompts for new portrait sheets. Append a substantial race-specific biology block after the selected prompt. Do not shorten the prompt when generating several races, and do not use an opposite-gender race sheet as a biological reference.

### Production female portrait prompt

Upload:

1. `reference/portrait-art-reference.png` — authoritative painterly-anime visual style.
2. `reference/human_female_healer.png` — female facial construction, natural presentation, and softer portrait finish.
3. `reference/human_female_melee.png` — material detail, contrast, and role readability only.

Copy and replace every bracketed value:

> Generate a completely new image from scratch. Do not edit, revise, transform, or preserve any previously generated portrait sheet.
>
> Create one square 5-column by 4-row contact sheet containing exactly 20 original adult female **[RACE] [ROLE]** characters for Fortcamp. Set name: **[SET NAME]**. Every cell must contain one unmistakable member of the requested race.
>
> **Authoritative art style:** `portrait-art-reference.png` controls the visual style. Match its painterly anime fantasy illustration: clearly anime-designed faces and proportions rendered as polished 2D digital paintings; smooth idealized facial planes; large expressive readable eyes; elegant simplified noses and mouths; carefully grouped hair or race-appropriate biological shapes; soft blended modeling; luminous warm amber rim light; deep but clean painted shadows; richly hand-painted materials; atmospheric medieval backgrounds; delicate highlights; and little or no visible hard line art. Preserve its balance between anime stylization and painterly detail. Never become photographic.
>
> Do not copy the reference character, body, animal ears, tail, clothes, pose, or scene. Use `human_female_healer.png` only for adult female facial construction, natural relaxed presentation, luminous eyes, consistent camera distance, and portrait finish. Use `human_female_melee.png` only for detailed materials, stronger contrast, and readable role design. Do not copy either sheet's identities, human biology, clothing, equipment, or repeated poses. The requested race's biology overrides every reference.
>
> **Style exclusions:** No photorealism, skin pores, harsh realistic anatomy, gritty Western RPG concept art, generic tabletop-monster art, grotesque realism, 3D CGI, character-creator rendering, desaturated grimdark painting, comic ink outlines, flat cel shading, or generic AI headshots. Do not make every face conventionally human, identical, rigid, snarling, or glamorous in the same way.
>
> **Race authority:** Every subject must visibly satisfy the appended **[RACE BIOLOGY BLOCK]**. Race anatomy is real biology rather than makeup, costume pieces, prosthetics, or a human with recolored skin. Do not automatically add human hair, ears, skin, hands, clothes, armor, or body structure where they do not belong. Adapt all equipment and modest coverage to the race's actual body. No humans or neighboring fantasy races may appear unless the requested race is Human.
>
> **Identity diversity:** All 20 characters must look unrelated. Vary underlying facial or equivalent identity-bearing anatomy rather than disguising one design with different colors, hair, markings, or equipment. Vary face or head silhouette, brow, eyes, nose or muzzle, cheeks, mouth, jaw, chin, ears, horns, crests, surface pattern, material, expression, build, pose, and race-appropriate coloration. Use scars, freckles, chips, bubbles, inclusions, tattoos, weathering, and unmarked surfaces selectively. Avoid sibling-like repetition.
>
> **Age:** All subjects are clearly adult women approximately **[AGE RANGE, DEFAULT 21–40]**. No children, teenagers, elderly characters, frailty, deep age wrinkles, or hair whitened by age. Naturally pale fantasy coloration is allowed on an otherwise age-appropriate adult.
>
> **Role:** Express twenty varied **[ROLE]** identities through stance, anatomy, markings, magic, carried objects, clothing, or equipment only where appropriate. Equipment is optional. When present, it is practical, worn, grounded in fantasy, fitted to the requested anatomy, and kept away from faces and cell boundaries. Use **[ROLE-SPECIFIC DETAILS]**.
>
> **Layout:** Exactly 5 columns and 4 rows, exactly 20 equal cells, one different upper-torso character centered in each cell, clean thin straight separators, consistent camera distance, and generous clearance around every head or identifying silhouette. No missing cells, extra figures, merged cells, uneven rows, decorative frames, text, labels, numbers, logos, watermarks, UI, or anything crossing a cell boundary.
>
> **Natural viewer engagement:** Every subject looks toward the viewer. At least 12 are nearly frontal; the rest use only subtle natural turns while maintaining eye contact. Add variety through relaxed shoulders, slight weight shifts, small head tilts, role props, and expression. No profiles, averted eyes, raised chins, dramatic tilts, repeated side poses, or twenty identical passport-photo poses.
>
> Before completing the image, verify every cell independently contains an adult female **[RACE]**, follows the race biology block, remains in painterly anime fantasy style, has a distinct underlying identity, and stays fully inside its cell.

### Production male portrait prompt

Upload:

1. `reference/portrait-art-reference.png` — authoritative painterly-anime visual style.
2. `reference/human_male_magic.png` — male construction, pose, and contact-sheet presentation only.
3. For male Dwarves only, optionally add `reference/dwarf_male_melee.png` for Dwarf build, armor, and material treatment. Do not use it as a universal male reference.

Copy and replace every bracketed value:

> Generate a completely new image from scratch. Do not edit, revise, transform, or preserve any previously generated portrait sheet.
>
> Create one square 5-column by 4-row contact sheet containing exactly 20 original adult male **[RACE] [ROLE]** characters for Fortcamp. Set name: **[SET NAME]**. Every cell must contain one unmistakable member of the requested race.
>
> **Authoritative art style:** `portrait-art-reference.png` controls the visual style. Match its painterly anime fantasy illustration: clearly anime-designed faces and proportions rendered as polished 2D digital paintings; smooth idealized facial planes; large expressive readable eyes; elegant simplified noses and mouths; carefully grouped hair or race-appropriate biological shapes; soft blended modeling; luminous warm amber rim light; deep but clean painted shadows; richly hand-painted materials; atmospheric medieval backgrounds; delicate highlights; and little or no visible hard line art. Preserve its balance between anime stylization and painterly detail. The result must feel illustrated and stylized, never photographic.
>
> Do not copy the reference woman, body, animal ears, tail, clothes, pose, or scene. Use `human_male_magic.png` only for adult masculine presentation, upper-torso framing, relaxed poses, consistent camera distance, and contact-sheet organization. Do not copy its faces, hairstyles, elderly subjects, costumes, magic objects, realism level, or human biology. The male reference must never override the painterly-anime style or the requested race.
>
> **Style exclusions:** No photorealism, realistic skin pores, harsh anatomical planes, gritty Western RPG concept art, generic tabletop-monster art, grotesque realism, 3D CGI, character-creator screenshots, desaturated grimdark painting, hypermasculine bodybuilder anatomy, comic ink outlines, flat cel shading, or generic AI headshots. Do not make all faces conventionally human, identical, rigid, snarling, gnarled, scarred, ugly, or sinister.
>
> **Race authority:** Every subject must visibly satisfy the appended **[RACE BIOLOGY BLOCK]**. Race anatomy is real biology rather than makeup, costume pieces, prosthetics, or a human with recolored skin. Do not automatically add human hair, ears, skin, hands, clothes, armor, or body structure where they do not belong. Adapt all equipment and modest coverage to the race's actual body. No humans or neighboring fantasy races may appear unless the requested race is Human.
>
> **Identity diversity:** All 20 characters must look unrelated. Deliberately vary the underlying face, head, or core silhouette and every race-defining feature. Vary brows, eyes, nose or muzzle, cheeks, mouth, jaw, chin, ears, horns, crests, hair or equivalent biological shapes, surface pattern, material, expression, build, pose, and race-appropriate coloration. Do not reuse one handsome anime face or one monster face and disguise it through recoloring, hair, facial hair, scars, or equipment. Avoid sibling-like repetition.
>
> **Age:** All subjects are clearly adult men approximately **[AGE RANGE, DEFAULT 21–40]**. No children, teenagers, elderly characters, frailty, deep age wrinkles, or hair whitened by age. Naturally pale fantasy coloration is allowed on an otherwise age-appropriate adult.
>
> **Role:** Express twenty varied **[ROLE]** identities through stance, anatomy, markings, magic, carried objects, clothing, or equipment only where appropriate. Equipment is optional. When present, it is practical, worn, grounded in fantasy, fitted to the requested anatomy, and kept away from faces and cell boundaries. Use **[ROLE-SPECIFIC DETAILS]**.
>
> **Layout:** Exactly 5 columns and 4 rows, exactly 20 equal cells, one different upper-torso character centered in each cell, clean thin straight separators, consistent camera distance, and generous clearance around every head or identifying silhouette. No missing cells, extra figures, merged cells, uneven rows, decorative frames, text, labels, numbers, logos, watermarks, UI, or anything crossing a cell boundary.
>
> **Natural viewer engagement:** Every subject looks toward the viewer. At least 12 are nearly frontal; the rest use only subtle natural turns while maintaining eye contact. Add variety through relaxed shoulders, slight weight shifts, small head tilts, role props, and expression. No profiles, averted eyes, raised chins, dramatic tilts, repeated side poses, or twenty identical passport-photo poses.
>
> Before completing the image, verify every cell independently contains an adult male **[RACE]**, follows the race biology block, remains in painterly anime fantasy style, has a distinct underlying identity, and stays fully inside its cell.

## Legacy reusable GPT image prompt

This short prompt is retained for comparison and old workflows. Do not use it for the production race batches. It does not give the generator enough protection against humanizing nonhuman races or copying the sex, anatomy, and poses in the reference images. Use **Natural viewer-facing generation for ChatGPT** below.

Replace the bracketed values and attach one previously approved Fortcamp portrait as a style reference after the first batch.

> Create a square 5-column by 4-row contact sheet containing exactly 20 distinct fantasy character portraits for Fortcamp. Set: **[SET NAME]**. Every cell contains one different **[RACE, GENDER, ROLE]** character, shown from the upper chest upward, facing generally toward the viewer. Dark grounded fantasy style, painterly semi-realistic game portrait, readable silhouette, expressive face, practical worn equipment, subdued natural colors, soft directional lighting, simple atmospheric background. Keep the character centered with generous space around the head. Make every cell equal size and perfectly aligned. No character may cross into another cell. No text, labels, numbers, logos, frames, borders, UI, watermarks, famous characters, or recognizable copyrighted designs. Vary faces, skin tones or coloration, hairstyles, equipment, age, and expression while keeping the requested race, gender, role, rendering style, camera distance, and lighting consistent. Output one high-resolution square image only.

Add one of these role notes:

- **Melee:** visible practical melee weapon or shield, armor ranging from light to heavy, confident or guarded posture.
- **Ranged:** bow, crossbow, sling, or throwing gear visible, alert eyes, mobile armor.
- **Worker:** builder or salvager tools, durable work clothing, soot, dust, or repair equipment.
- **Healer:** medicine pouch, bandages, herbs, practical field-clinic clothing; avoid modern hospital uniforms.
- **Magic:** focus, staff, charm, spellbook, or subtle magical light; keep effects away from cell edges.
- **Special:** leader, boss, shaman, veteran, or elite visual language with more distinctive equipment and presence, while remaining usable as an original Fortcamp character.

For goblins, add:

> Original fantasy goblins with varied green, olive, moss, and gray-green skin, large expressive ears, compact facial proportions, and scavenged practical equipment. They can look rough or dangerous without becoming identical monsters.

For werewolves, add:

> Original humanoid werewolves with readable individual faces, controlled bestial features, varied fur colors, and varied practical fantasy equipment. Avoid quadrupedal poses. This is a general werewolf set; do not constrain it to a combat role.

## Required image sets

Generate these first. Each sheet produces 20 usable portraits.

### Humans

- `human_male_melee`
- `human_female_melee`
- `human_male_ranged`
- `human_female_ranged`
- `human_male_worker`
- `human_female_worker`
- `human_male_healer`
- `human_female_healer`
- `human_male_magic`
- `human_female_magic`

### Goblins

- `goblin_male_melee`
- `goblin_female_melee`
- `goblin_male_ranged`
- `goblin_female_ranged`
- `goblin_male_special`
- `goblin_female_special`

### Werewolves

- `werewolf_male`
- `werewolf_female`

Werewolves use one pool per gender regardless of their role, equipment, or how they acquired the transformation.

Slimefolk likewise use one general pool per gender (`slimefolk_female` or `slimefolk_male`). Their mutable bodies do not require separate visual classes even though an individual can still have a healer, magic, worker, melee, or ranged gameplay specialty. When a race lacks the requested role art, Fortcamp first tries a role-neutral pool and then another available role for the same race and gender.

### Event recruit races

Event-exclusive races can join without portrait art and will display initials until their matching pool is added. Their pool names follow `<race_slug>_<gender>_<role>` using the same melee, ranged, worker, healer, and magic roles as Humans.

- **General survivors:** `dwarf`, `wood_elf`, `half_orc`, `halfling`, `tiefling`

- **Green Warhost:** `hobgoblin`, `bugbear`, `kobold`, `orc`
- **Ashen Procession:** `revenant`, `dhampir`, `ashborn`, `graveborn`
- **Arcane Convergence:** `high_elf`, `gnome`, `manaforged`, `homunculus`, `dreamkin`
- **Great Beast Tide:** `lizardfolk`, `harpy`, `minotaur`, `beastkin`, `centaur`
- **Starfall Omen:** `astral_elf`, `voidborn`, `starforged`, `celestine`, `cometkin`

For example, a female Harpy Scout reads from `harpy_female_ranged`, while a male Starforged Fighter reads from `starforged_male_melee`. Missing folders are safe and do not prevent recruitment.

## Importing a finished sheet

For normal batch imports on Windows, double-click `run_portrait_pool_importer_windows.bat`. Choose the folder containing the sheets (the UI starts in `portraits/`) and use **Import Safe New Pools**. It imports only canonical filenames that target empty pools. To add a revised sheet to an existing pool, select it and use **Append Selected Revisions**.

The importer never overwrites or renumbers existing portraits. It appends new row-major IDs after the highest existing number. It also hashes the decoded image dimensions and RGB pixels, so the same image with different PNG metadata or compression is recognized as an exact duplicate. A visually similar image with any changed pixel is treated as a revision and is not rejected automatically.

Save the generated sheet anywhere, then run this from the project directory:

```powershell
.\.venv\Scripts\python.exe tools\import_portrait_sheet.py "C:\path\goblin_female_melee.png" goblin_female_melee
```

The default assumes a 5×4 sheet. For another layout:

```powershell
.\.venv\Scripts\python.exe tools\import_portrait_sheet.py "C:\path\sheet.png" goblin_female_melee --columns 4 --rows 5
```

Inspect the resulting files in `data/portrait_pools/<set>/full`. If the generator added thick gutters, raise `--inset` slightly, for example `--inset 0.05`, and re-import after removing the unwanted output files.

Fortcamp selects one image automatically when a matching generic recruit joins and permanently stores that selection with the character. Adding images or restarting the game does not reroll an assigned portrait. A manual upload can still override the pool choice and remains available for every character.















## Legacy combined natural viewer-facing prompt

This older combined prompt is retained intact for comparison and reproducibility. It produced the more natural `dwarf_female_melee_natural_v4` and `dwarf_male_melee_natural_v4` tests, but new generations should use the separate production female or male prompt above.

### Files to upload

Always upload `reference/portrait-art-reference.png` as the overall finish reference. Then use references matching the requested gender:

1. `reference/portrait-art-reference.png` — authoritative visual-style reference. Its style is **painterly anime fantasy illustration**: anime-designed faces and proportions rendered as a polished 2D digital painting, with smooth idealized facial planes, large readable eyes, finely shaped hair, soft blended modeling, warm cinematic rim light, detailed materials, and very little visible line art. Detail must not turn into photographic skin, harsh realistic anatomy, or Western grimdark concept art.
2. For **female** sets, use `reference/human_female_healer.png` as the primary presentation reference and `reference/human_female_melee.png` as the secondary material/role reference.
3. For **male** sets, use `reference/human_male_magic.png` only as the gender, pose, and contact-sheet presentation reference. It supplies masculine facial and body construction without requiring the generator to translate female faces into men. It must not override the painterly anime style established by `portrait-art-reference.png`.
4. Use `reference/dwarf_male_melee.png` only for male Dwarves or when a sturdy armored male build is specifically desired. Do not use it as a universal reference for Goblins, Elves, animal folk, spectral races, constructs, or other unrelated anatomy; its broad faces, beards, armor, and Dwarf proportions can bleed into the result.

Do not upload a rejected generation as another reference. It can reinforce the exact face or pose problem being corrected. Do not use the female counterpart sheet as a race reference for a male set. Describe the requested biology in the prompt and use a gender-matched presentation reference. Image references influence anatomy and identity even when the prompt says they are for style only.

The full prompt below, followed by a substantial race-specific biology block, is the production workflow used for the successful multi-race female pass. Do not replace it with a shortened shared prompt when mass-generating several races. The race block is mandatory for every visibly nonhuman race; one sentence appended to a generic human-oriented prompt is insufficient.

For a male set, replace the female-reference names in the **Reference hierarchy** and **Style lock** paragraphs below with `human_male_magic.png`. Omit `human_female_healer.png` and `human_female_melee.png`. For a male Dwarf set only, add `dwarf_male_melee.png` as the secondary build, equipment, and material reference.

### Authoritative style wording

Use **painterly anime fantasy illustration** as the style name. Describe it as anime facial design rendered with soft, sophisticated 2D digital painting: smooth idealized skin or race-appropriate surfaces, simplified graceful facial planes, large expressive readable eyes, carefully grouped hair or biological shapes, soft blended shadows, warm amber rim light, rich painted materials, atmospheric depth, and little or no hard outline. Do not use `semi-realistic` by itself; generators often interpret it as realistic Western RPG concept art. Avoid photorealistic pores, harsh anatomical rendering, gritty desaturated concept art, grotesque realism, excessively gnarled faces, and generic tabletop-monster art unless a specific creature truly requires them.

### Copy-paste prompt

Replace every bracketed value. Keep the reference filenames in the prompt so ChatGPT knows the purpose of each upload.

> Generate a completely new image from scratch. Do not edit, revise, transform, or preserve any previously generated portrait sheet. Do not use a previous generated sheet as the starting canvas.
>
> Create one square 5-column by 4-row contact sheet containing exactly 20 original adult **[GENDER] [RACE] [ROLE]** characters for Fortcamp. Set name: **[SET NAME]**.
>
> **Reference hierarchy:** Use `human_female_healer.png` as the primary portrait-style reference. Match its softly painterly anime/semi-realistic facial readability, luminous expressive eyes, fine surface detail, warm amber bloom, gentle modeling, atmospheric medieval backgrounds, natural relaxed posture, and polished illustration finish. Use `human_female_melee.png` only for high-detail material rendering, dark-fantasy contrast, and clear role presentation. Its armor, fabric, weapons, and human anatomy are examples rather than universal requirements. Do not copy its repeated raised-chin or side-facing composition. Use `portrait-art-reference.png` to reinforce the luxurious painterly anime-fantasy finish, warm cinematic rim light, rich texture, and detailed medieval atmosphere. Do not copy its character, face, body, animal ears, tail, clothing, pose, or location. Use all references only for visual language and production quality. The requested race's biology overrides every reference-image costume or body detail. Create entirely original characters.
>
> **Style lock:** The result must look like the same portrait collection as `human_female_healer.png` and `human_female_melee.png`: high-end illustrated anime fantasy with painterly semi-realistic rendering, soft but precise readable features, expressive detailed eyes where applicable, finely painted race-appropriate surfaces, warm modeling, rich amber edge light, deep brown shadows, intricate hand-painted material detail, and subtle atmospheric depth. Render skin, hair, fur, feathers, scales, bark, chitin, slime, spectral matter, stone, metal, or constructed plating according to the requested race. Avoid photographic realism, Western RPG character-creator rendering, 3D CGI, hard hyperreal pores, comic ink outlines, flat cel shading, and generic AI headshots.
>
> **Biology, equipment, and coverage:** Treat **[RACE]** biology as authoritative. Do not automatically give a nonhuman race human clothes, armor, hair, skin, hands, or body structure just because the references contain them. Clothing and manufactured equipment are optional and appear only when they make sense for the race, culture, and role. A character may instead be naturally and modestly covered by fur, feathers, scales, chitin, bark, stone, mist, flame, shadow, spectral matter, slime shaped into garment-like layers, or built-in constructed plating. Natural coverage should feel intentional and visually readable rather than censored or humanized. Do not expose explicit anatomy. When equipment is appropriate, adapt its straps, grips, openings, and silhouette to the race's actual body.
>
> **Layout:** Output one high-resolution square image with exactly 5 columns and 4 rows, exactly 20 equal square cells, and one different upper-torso character centered in every cell. Use a consistent camera distance, generous clearance around every head or primary identifying silhouette, and thin clean separators. Race-appropriate limbs, natural body features, tools, focuses, shields, books, or weapon handles may appear when useful but must remain inside their own cells. No subject, body feature, or prop may cross a cell boundary.
>
> **Natural viewer engagement:** Every character makes eye contact with the viewer or, for races without conventional eyes, visibly directs its attention toward the viewer. At least 12 of the 20 faces or primary identifying fronts are essentially frontal, within roughly 0-7 degrees of the camera. The remaining subjects may turn subtly no more than roughly 15 degrees left or right while continuing to engage the viewer. Add natural variety through small shoulder or body-silhouette angles, relaxed weight shifts, slight head tilts under 5 degrees, limb placement, natural features, role props, and expression. Keep heads or equivalent focal features near level. Do not use profiles, strong three-quarter views, side shots, averted attention, raised chins, upward gazes, downward gazes, dramatic tilts, identical passport-photo symmetry, or rigid repeated posture.
>
> **Identity diversity is mandatory:** All 20 characters must look unrelated. For humanoid races, vary underlying facial anatomy rather than only changing hair or color: distribute different face silhouettes, foreheads, brows, eye shapes and spacing, noses, cheekbones, cheeks, mouths, lips, jaws, chins, ears, complexions, and hair textures. For nonhuman races, vary the equivalent identity-bearing anatomy: head or core silhouette, eye count/shape/placement, muzzle or mandible, ears or horns, crests, tendrils, fluid contours, surface opacity, fur pattern, feather arrangement, scale structure, bark growth, cracks, inclusions, glow, markings, and asymmetry. Vary race-appropriate colors and material qualities without using recoloring as the only difference. Use scars, freckles, tattoos, chips, bubbles, embedded objects, weathering, and unmarked surfaces selectively where they make biological sense. Do not reuse one underlying design and disguise it with different hair, facial hair, colors, clothing, equipment, or markings. Avoid sibling-like repetition.
>
> **Age:** All characters are clearly adults approximately **[AGE RANGE]**. Do not include children or elderly characters. No seniors, deeply aged faces, frailty, deep age wrinkles, or hair whitened by age. Naturally pale fantasy hair is allowed only on an otherwise age-appropriate adult.
>
> **Race and role:** Give every character unmistakable **[RACE]** biology and cultural traits while maintaining twenty separate identities. Express visibly different **[ROLE]** specializations through stance, natural anatomy, body shaping, markings, carried objects, magic, equipment, or clothing only where each choice makes sense. Equipment is not mandatory. Any equipment that appears must be practical, worn, adapted to the character's body, and appropriate to a grounded dark-fantasy setting. Expressions or equivalent body-language cues should vary naturally while retaining viewer engagement: warm, stern, amused, guarded, skeptical, proud, impatient, focused, calm, fierce, tired, and quietly confident.
>
> **Avoid:** same-face or same-body syndrome, sibling-like repetition, one design with recolored hair, fur, slime, scales, or surface material, repeated exact silhouettes, automatically dressing every race like a human, human anatomy imposed on incompatible races, repeated armor, repeated raised-chin poses, rigid lineup posture, photographic realism, generic Western fantasy portraits, elderly characters, famous or copyrighted characters, text, labels, numbers, logos, UI, watermarks, decorative outer frames, merged cells, or subjects crossing boundaries.

### Race-specific biology and coverage add-ons

Add one concise race block after the general prompt. These examples override the human clothing and anatomy visible in the reference sheets.

For Slimefolk:

> Every character is one continuous living mass of magical semi-translucent ooze rather than human skin. Everything belonging to the character is slime: face, head, neck, torso, arms or pseudopods, modest coverage, decorative shapes, and magic. Do not render separate clothing, armor, fabric, leather, fur garments, mail, belts, seams, buckles, jewelry, books, staffs, bottles, charms, tools, weapons, flowers, or other carried or worn physical objects. Any rune, focus, ornament, or magical effect must be suspended inside the slime or formed from slime and visibly connected to the body.
>
> Do not render hair. No individual strands, wisps, bangs, braids, curls, locks, ponytails, hairlines, or human hairstyles. Use smooth slime caps, thick blunt fluid lobes, rounded pseudopod crests, large bubble clusters, wave shapes, or a simple flowing ooze mass. Any tendril must be thick, rounded, translucent, and gelatinous rather than thin or fibrous. Do not render human ears, pointed ears, animal ears, fin ears, gills, side fins, horns, or ear-shaped protrusions; keep the sides of the head smooth.
>
> Give every Slimefolk exactly one clearly visible internal slime core suspended at the same position inside the upper torso. Treat it as a consistent species organ rather than another identity feature. Every core has the same circular biological-cell design: one round translucent teal outer membrane, one round deep-red central nucleus, and optionally one small darker-red nucleolus inside the nucleus. Keep approximately the same diameter and sternum placement in all 20 portraits. The core must be visible through the translucent body, softly illuminate the surrounding slime, and must not resemble jewelry or a held object. Do not turn it into a flower, lotus, heart, star, moon, sun, crystal, gemstone, diamond, rune, sigil, vortex, galaxy, flame, eye, clock, mechanical part, or irregular silhouette. Do not vary its colors or create multiple cores.
>
> Maintain modest nonsexual coverage through thicker opaque slime anatomy, layered fluid folds, mantle-like body mass, shoulder waves, and smooth sculptural ooze. These are body structures rather than garments and must join continuously into the neck and torso through shared bubbles, uninterrupted gradients, and flowing surfaces. Express magic only through the body and core: orbiting slime droplets, bubbles, internal light, glowing fluid veins, pseudopods, suspended motes, ripples, refraction, and core pulses. Keep the core identical while making the characters different. Deliberately vary underlying face width and length, eye size and spacing, brow-like ridges, nose-like contour, cheek structure, mouth width and shape, jawline, chin, expression, head silhouette, viscosity, opacity, inclusions, asymmetry, internal flow, and body color. Do not reuse one anime face and disguise it through recoloring.

For Werewolves:

> Every character is an upright intelligent Werewolf with a distinct lupine face, muzzle, ears, fur pattern, mane, and sturdy humanoid posture. Their own fur provides natural modest coverage; do not add human shirts, dresses, or trousers merely because the references contain them. Optional belts, harnesses, cloaks, packs, jewelry, light armor pieces, or role equipment may appear only where practical, fitted around the body rather than replacing its fur identity. Vary muzzle length, ear shape, facial ruff, mane, fur texture, markings, scars, and coloration so no two Werewolves share the same underlying design.

For other nonhuman races, replace the coverage material with the biology that fits: feathers for avian peoples, scales for reptilian peoples, bark and leaves for plant folk, chitin for insectoid peoples, spectral matter for incorporeal undead, and integrated plating for constructs.

### Dwarf melee add-on

Append the relevant block to the prompt above.

For female Dwarf melee sets:

> All 20 are adult female Dwarf melee fighters approximately 21-40, with sturdy compact proportions and broad capable builds. No elders. No mustaches, beards, chin hair, facial-hair braids, or masculine facial hair. Preserve Dwarf identity without giving everyone the same broad face. Include distinct axe fighters, hammer guards, sword duelists, shield bearers, tunnel fighters, pick warriors, clan sentinels, armored veterans, and lightly armored skirmishers. Clothing and armor are practical, attractive, modest, and fully cover the chest.

For male Dwarf melee sets:

> All 20 are adult male Dwarf melee fighters approximately 21-40, with sturdy compact proportions and broad capable builds. No elders. Facial hair cannot serve as the primary identity difference: at least seven characters are clean-shaven or have only light stubble. Distribute the others among visibly different moustaches, short beards, trimmed beards, forked beards, curly beards, and braided beards. Do not repeat the same large beard. Make the facial anatomy beneath the facial hair clearly different. Include distinct axe fighters, hammer guards, sword duelists, shield bearers, tunnel fighters, pick warriors, clan sentinels, armored veterans, and lightly armored skirmishers.

If ChatGPT starts editing the most recent image instead of generating a new one, begin a new message with the first sentence of the prompt again: **“Generate a completely new image from scratch.”** Keep the rejected image unattached.

## Appearance metadata for portrait sheets

Fortcamp keeps visual descriptions in `data/portrait_pools/portrait_metadata.json`, keyed to the stable split portrait filename. The data is deliberately separate from PNG/WebP metadata, so recompression does not erase it and replacing an unrelated image cannot silently inherit it.

To attach descriptions while importing a sheet, place a companion file beside it with the same base name and `.metadata.json` as its ending. For example:

- `banshee_female_magic.png`
- `banshee_female_magic.metadata.json`

The companion contains exactly one entry per cell in the same row-major order used by the importer: left to right across the first row, then the next row. A 5×4 sheet therefore needs exactly 20 entries.

```json
{
  "portraits": [
    {
      "hair_color": "silver",
      "hair_length": "waist-length",
      "eye_color": "pale blue",
      "skin_tone": "translucent pearl",
      "build": "slender",
      "distinctive_features": "a torn spectral veil and a faint scar over her left brow",
      "summary": "a slender spectral woman with waist-length silver hair, pale blue eyes, and a torn translucent veil"
    }
  ]
}
```

Use empty strings for traits that do not apply. Slimefolk, constructs, harpies, and other nonhuman races should describe their visible surface, silhouette, core, feathers, plating, markings, or other identifying anatomy instead of inventing human hair or skin. `summary` is the natural phrase mission prose uses first; if it is empty, Fortcamp assembles a phrase from the structured fields.

The in-game Appearance editor can override these fields for any character, including a character with a user-uploaded portrait. The **Fill from portrait tags** action appears when the currently assigned pool portrait has a registry entry. Uploading an override clears portrait-derived fields so the old image cannot describe the new one; a manual description is preserved.

Image colors and anatomy should be tagged by a vision-capable model or reviewed by a person. Ordinary pixel sampling cannot reliably distinguish hair, eyes, skin, clothing, fur, feathers, slime, and background lighting, so the importer does not guess those labels from color alone.
