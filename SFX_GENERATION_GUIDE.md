# Fortcamp Sound Effects Guide

## Captor foley, October 7

Four ElevenLabs clips use tools/generate_captor_sfx.py, with original MP3s/reports in staging-sfx/captor-v1 and runtime WAVs in frontend/public/assets/sfx. See docs/art/CAPTOR_V1.md. Existing net Subdue sound is reused.

## Combat impact pack

> Modern painted-fantasy tactical RPG, warm soft low-mid texture, compact readable one-shot, gentle at low volume, no piercing highs, no music, no voices, no ambience, no trailer boom.

| Filename | Length | Prompt after the palette sentence |
|---|---:|---|
| `burn_tick.wav` | 0.7 s | A tiny close puff of magical fire scorching cloth, soft short ember crackle and rounded airy heat release. No roaring flame, no alarm. |
| `poison_tick.wav` | 0.7 s | A muted viscous magical poison pulse, one soft liquid bubble with a low organic tap, subtle and ominous. No cartoon gulp, no squeak. |
| `barrier_absorb.wav` | 0.8 s | A magical protective shell absorbs a hit, soft glassy thump and brief warm shimmering decay. Gentle rounded tone, no ringing high bell. |
| `collision_hit.wav` | 0.8 s | A combatant bumps hard into a wooden obstacle, compact padded body thud and small dry wood rattle. Weighty but restrained, no voice, no gore. |

Generate with `tools/generate_sfx_pack.py --pack combat-impact-v1`. Originals and
technical checks stay in staging-sfx/combat-impact-v1. Playback uses the Battle
channel at restrained gain; separate poison/fire cues avoid sounding like sword
hits. Technical checks cannot certify how an effect sounds; listening remains
part of the review.

## Sonic identity

Current direction: warm, melodic fantasy MMORPG feedback, with Ragnarok Online and Tree of Savior as broad mood references. Use round bell and celesta tones, soft harp plucks, restrained strings, friendly readable motifs, and modern clean audio. Keep combat tactile but slightly stylized; keep UI soft and magical. Critical outcomes should be recognizable through melody and arrangement, not simply louder playback. Future action/UI passes should follow this direction too.

The dry dark-fantasy direction below is legacy. Its existing action sounds remain the first audition set; the mission cues have a dedicated modern replacement pack.

Fortcamp should sound like a grounded dark-fantasy tabletop campaign brought to life: close, tactile, slightly stylized, and readable at low volume. Reuse this palette sentence in every ElevenLabs prompt:

> Grounded dark-fantasy tactical RPG game audio, close-miked dry foley, warm low-mid tone, leather wood and iron textures, restrained impact, clean isolated one-shot, no music, no voices, no ambience, no long reverb, no cinematic trailer boom.

Generate each effect separately. In ElevenLabs Sound Effects, use non-looping output, WAV 48 kHz, and roughly 45–60% prompt influence. Generate four variations, keep the quietest clean version that remains readable, and avoid variations with musical tones or background ambience.

Put unedited downloads in `staging-sfx`. The selected final files go in `frontend/public/assets/sfx` with the exact filenames below.

## First production pack

| Filename | Length | Prompt after the palette sentence |
|---|---:|---|
| `ui_click.wav` | 0.5 s | Subtle game menu selection: a soft leather tap with a tiny dry wooden tick, quiet and unobtrusive. |
| `ui_confirm.wav` | 0.6 s | Positive game menu confirmation: compact wooden clack with a restrained warm metal accent, confident but quiet. |
| `ui_cancel.wav` | 0.5 s | Game menu cancel: short muted wooden knock with a soft downward cloth movement, neutral rather than alarming. |
| `melee_swing.wav` | 0.5 s | Fast handheld weapon swing through air, compact cloth-and-metal whoosh, no impact. |
| `melee_hit_light.wav` | 0.6 s | Light melee strike against leather armor, dense body impact with a small equipment rattle, no gore. |
| `melee_hit_heavy.wav` | 0.8 s | Heavy melee strike against armored target, weighty body impact, wood and iron rattle, controlled low end, no gore. |
| `subdue_hit.wav` | 0.7 s | Nonlethal blunt takedown, padded body thump with brief armor rattle, forceful but not graphic. |
| `unit_death.wav` | 0.9 s | Defeated fantasy combatant collapses onto packed earth, armor and equipment settling, no voice and no gore. |
| `unit_unconscious.wav` | 0.8 s | Unconscious armored combatant drops onto packed earth, softer body fall and equipment settle, no voice. |
| `guard.wav` | 0.6 s | Defensive stance: shield and weapon brace together with a compact leather-and-iron clack. |
| `mission_success.wav` | 1.2 s | Short restrained dark-fantasy success stinger, two warm hammered-metal notes with a subtle wooden resonance, no orchestra. |
| `mission_failure.wav` | 1.2 s | Short restrained dark-fantasy failure stinger, low muted iron resonance and a soft wooden fall, no horror sting. |

## Modern melodic mission pack

> Modern fantasy MMORPG audio. Warm rounded celesta, soft bells, harp and gentle strings. Smooth treble, clean full-fidelity mix, subtle reverb. No voices, chiptune, harsh buzz or alarms.

| Filename | Length | Prompt after the palette sentence |
|---|---:|---|
| `mission_critical_success.wav` | 3.5 s | Exceptional quest triumph: joyful rising three-note celesta melody, graceful harp flourish, luminous major chord with soft strings. Richer than ordinary success, delightful and gentle. Start promptly, fully resolve, allow a natural fading tail. |
| `mission_success.wav` | 2.5 s | Ordinary quest success: friendly ascending three-note celesta melody, small harp accent, warm resolved major chord. Light, satisfying, pleasantly memorable, modest celebration. Start promptly, end with soft natural decay. |
| `mission_failure.wav` | 2.5 s | Ordinary quest setback: gentle descending three-note celesta melody, wistful minor harmony, soft harp support. Reflective and reassuring, pleasant to hear repeatedly. Start promptly, resolve to a small low chord with natural decay. |
| `mission_critical_failure.wav` | 3.5 s | Serious quest setback: slow descending three-note lower-register celesta melody, restrained sorrowful strings, one soft harp pluck, deeper resolved minor chord. Consequential but calm and tuneful. Start promptly, end with natural decay. |
| `ui_click.wav` | 0.5 s | One very short quiet menu selection: soft rounded wooden tick blended with a tiny warm bell pluck. Crisp immediate onset, brief smooth decay. Tactile and slightly magical, comfortable when clicked repeatedly. No melody or strings. |
| `ui_confirm.wav` | 0.7 s | Menu confirmation: two soft rising celesta notes and a delicate harp pluck, warm and friendly with a tiny magical shimmer. Compact, smooth, immediate, reassuring. Quiet UI feedback, no orchestral swell. |
| `ui_cancel.wav` | 0.5 s | Menu back or cancel: two short soft descending bell plucks, rounded low-mid tone, gentle wooden undertone. Calm neutral feedback, never alarming. Immediate and brief with a clean fading tail. No strings. |

Generate these four outcomes and three UI replacements using `.venv\Scripts\python.exe tools\generate_sfx_pack.py --pack mission-melodic-v2`. Originals and reports are saved in `staging-sfx/mission-melodic-v2`; replaced WAVs are backed up there. Final cues preserve stereo at 48 kHz, target -22 dBFS RMS (UI -24) with a -3 dBFS peak ceiling, and retain softer reverb tails. Listen for timbre, melodic clarity, and a smooth ending before approving the pack. Combined prompts stay within the API's 450-character limit.

## Distinct mission outcomes v3

The v2 mission jingles were rejected because too many sounded like rewards. V3 separates mood as well as register: major-key rising reward cues versus falling minor-key loss cues. Failures use muted piano, woodwind, and cello instead of sparkling bell/harp flourishes. Instruments remain soft and polished. Generation cannot guarantee exact melody or emotional interpretation; listening approval remains required.

> One short modern fantasy RPG outcome jingle. Original melody, smooth full-fidelity instruments, soft attack, balanced treble, modest reverb, complete ending. No voices, chiptune, harsh buzz or ambient noise.

| Filename | Length | Prompt after the palette sentence |
|---|---:|---|
| `mission_critical_success_v3.wav` | 3.5 s | GREAT VICTORY reward. Joyful brisk ascending celesta arpeggio in C major, warm strings swell into a triumphant full major chord. Bright uplifting celebration and a tiny final bell flourish. Clearly happy and earned, gentle natural fade. |
| `mission_success_v3.wav` | 2.5 s | QUEST SUCCESS reward. Cheerful rising bell melody, C-E-G, supported by warm harp and light strings. Resolve confidently on a consonant major chord. An unmistakably positive small victory, no descending or sad phrases. Natural fade. |
| `mission_failure_v3.wav` | 2.5 s | QUEST FAILED. Muted piano and low woodwind play a falling A-G-F-E phrase in A minor. Sparse hesitant rhythm, low minor chord fading away. Unsuccessful and downcast. No bells, sparkle, harp, uplifting resolution or flourish. |
| `mission_critical_failure_v3.wav` | 3.5 s | DEFEAT, serious loss. Low cello and felt piano, slow descending A-F-D in D minor, then a mournful low minor chord and silence. Sorrow, unmistakable failure. No bells, harp, sparkle, rising phrase, celebratory flourish, horror blast or boom. |

Run `.venv\Scripts\python.exe tools\generate_sfx_pack.py --pack mission-outcomes-v3`. This generates only four new cues, saves the v2 files, and installs versioned filenames to avoid stale cached audio. Audition at `/assets/sfx/preview-mission-outcomes-v3.html`. Prompt influence is 0.8 to prioritize the requested emotional distinction. The v2 UI pack remains installed.

## Action expansion pack

> Modern stylized fantasy RPG one-shot. Warm rounded tone, clear tactile detail, soft treble, compact clean tail. No voices, music, harsh noise, retro effects or background ambience.

| Filename | Length | Prompt after the palette sentence |
|---|---:|---|
| `step_earth.wav` | 0.5 s | One boot footstep on soft grass and packed earth. Gentle low leather thud, tiny dry grass rustle. Quiet and immediately readable, not a sequence of steps. |
| `step_stone.wav` | 0.5 s | One boot footstep on a stone dungeon floor. Soft sole tap with a restrained stone clack. Quiet and rounded, no metallic ringing. |
| `step_water.wav` | 0.5 s | One boot footstep through shallow water. Small warm splash and watery slosh, quiet, no large wave or repeated walking. |
| `bow_release.wav` | 0.5 s | A fantasy bow releases one arrow. Quick taut string twang and short arrow whoosh, clean and rounded, satisfying but not musical. |
| `arrow_hit.wav` | 0.5 s | One arrow strikes leather armor: compact dull puncture thunk with a tiny wood rattle. Readable soft impact, no gore, no voice. |
| `magic_cast.wav` | 0.7 s | One neutral arcane spell release. A soft rising airy pulse, round glass resonance, tiny magical shimmer. One brief cast, gentle and clean, no melody. |
| `magic_hit.wav` | 0.7 s | One neutral arcane spell impact. Rounded magical puff and soft crystalline crackle, tactile and compact. Distinct from metal or physical hits, no melody. |
| `attack_miss.wav` | 0.5 s | A failed attack glances harmlessly past: quick soft air flick and small cloth swish. Brief empty gesture, no impact or musical notes. |
| `shield_block.wav` | 0.6 s | A shield absorbs one attack. Restrained rounded iron-on-wood clonk with leather tension. Solid protective block, short decay, no piercing metal ring. |
| `throw_release.wav` | 0.5 s | Throwing a heavy handheld object: compact effort-free cloth movement and low air whoosh. One release, no vocal grunt, no impact. |
| `throw_hit.wav` | 0.6 s | Heavy thrown object hits armor: solid rounded thump, short wood and equipment rattle. Weighty but comfortable, no gore or bass boom. |
| `structure_hit.wav` | 0.6 s | One weapon blow into a wooden palisade: firm wood knock with a small splinter crunch. Clear damage feedback, no collapse yet. |
| `structure_break.wav` | 1.0 s | A small wooden barricade breaks apart: short cracking wood, falling chunks, soft debris settling. Clear compact destruction, no explosion or huge crash. |
| `cage_open.wav` | 0.8 s | Opening one small iron cage door: latch clicks, short gentle metal hinge creak, soft final clack. No long squeal, no door slam. |
| `pickup.wav` | 0.5 s | Picking up equipment or lifting a body: short cloth and leather gather with a small strap creak. Soft tactile handling, no voice or gore. |
| `payload_drop.wav` | 0.5 s | Gently setting a carried object or body onto the ground: one muted padded thud and soft cloth settle. Quiet, no voice or gore. |
| `extraction.wav` | 0.7 s | Small fantasy safe-exit confirmation: soft wooden latch then two rounded low bell tones. Calm closure, understated rather than a victory fanfare. |
| `objective_interact.wav` | 0.6 s | Handling a battlefield mechanism: a dry small wooden click, leather rustle, soft final latch. Brief tactile interaction, no music or reward flourish. |

Run `.venv\Scripts\python.exe tools\generate_sfx_pack.py --pack action-expansion-v1`. Eighteen originals and their generation report are kept separately in `staging-sfx/action-expansion-v1`. Movement plays quiet individual steps along the animation; ranged and arcane attacks, misses, blocks, throws, destruction, object handling, and exits use confirmed backend events. No sound is inferred from prose. Full battle auto-resolve skips detailed action audio.

## Action expansion pack

> Modern stylized fantasy RPG one-shot. Warm rounded tone, clear tactile detail, soft treble, compact clean tail. No voices, music, harsh noise, retro effects or background ambience.

| Filename | Length | Prompt after the palette sentence |
|---|---:|---|
| `step_earth.wav` | 0.5 s | One boot footstep on soft grass and packed earth. Gentle low leather thud, tiny dry grass rustle. Quiet and immediately readable, not a sequence of steps. |
| `step_stone.wav` | 0.5 s | One boot footstep on a stone dungeon floor. Soft sole tap with a restrained stone clack. Quiet and rounded, no metallic ringing. |
| `step_water.wav` | 0.5 s | One boot footstep through shallow water. Small warm splash and watery slosh, quiet, no large wave or repeated walking. |
| `bow_release.wav` | 0.5 s | A fantasy bow releases one arrow. Quick taut string twang and short arrow whoosh, clean and rounded, satisfying but not musical. |
| `arrow_hit.wav` | 0.5 s | One arrow strikes leather armor: compact dull puncture thunk with a tiny wood rattle. Readable soft impact, no gore, no voice. |
| `magic_cast.wav` | 0.7 s | One neutral arcane spell release. A soft rising airy pulse, round glass resonance, tiny magical shimmer. One brief cast, gentle and clean, no melody. |
| `magic_hit.wav` | 0.7 s | One neutral arcane spell impact. Rounded magical puff and soft crystalline crackle, tactile and compact. Distinct from metal or physical hits, no melody. |
| `attack_miss.wav` | 0.5 s | A failed attack glances harmlessly past: quick soft air flick and small cloth swish. Brief empty gesture, no impact or musical notes. |
| `shield_block.wav` | 0.6 s | A shield absorbs one attack. Restrained rounded iron-on-wood clonk with leather tension. Solid protective block, short decay, no piercing metal ring. |
| `throw_release.wav` | 0.5 s | Throwing a heavy handheld object: compact effort-free cloth movement and low air whoosh. One release, no vocal grunt, no impact. |
| `throw_hit.wav` | 0.6 s | Heavy thrown object hits armor: solid rounded thump, short wood and equipment rattle. Weighty but comfortable, no gore or bass boom. |
| `structure_hit.wav` | 0.6 s | One weapon blow into a wooden palisade: firm wood knock with a small splinter crunch. Clear damage feedback, no collapse yet. |
| `structure_break.wav` | 1.0 s | A small wooden barricade breaks apart: short cracking wood, falling chunks, soft debris settling. Clear compact destruction, no explosion or huge crash. |
| `cage_open.wav` | 0.8 s | Opening one small iron cage door: latch clicks, short gentle metal hinge creak, soft final clack. No long squeal, no door slam. |
| `pickup.wav` | 0.5 s | Picking up equipment or lifting a body: short cloth and leather gather with a small strap creak. Soft tactile handling, no voice or gore. |
| `payload_drop.wav` | 0.5 s | Gently setting a carried object or body onto the ground: one muted padded thud and soft cloth settle. Quiet, no voice or gore. |
| `extraction.wav` | 0.7 s | Small fantasy safe-exit confirmation: soft wooden latch then two rounded low bell tones. Calm closure, understated rather than a victory fanfare. |
| `objective_interact.wav` | 0.6 s | Handling a battlefield mechanism: a dry small wooden click, leather rustle, soft final latch. Brief tactile interaction, no music or reward flourish. |

Run `.venv\Scripts\python.exe tools\generate_sfx_pack.py --pack action-expansion-v1`. Eighteen originals and their generation report are kept separately in `staging-sfx/action-expansion-v1`. Movement plays quiet individual steps along the animation; ranged and arcane attacks, misses, blocks, throws, destruction, object handling, and exits use confirmed backend events. No sound is inferred from prose. Full battle auto-resolve skips detailed action audio.

## Installed API pack (2026-09-30)

The first 12 effects are now installed in `frontend/public/assets/sfx`. Open `/assets/sfx/preview.html` on the running game server to audition them together. Listening approval is pending; technical checks cannot establish whether an effect has the right character or contains unwanted content.

Original MP3 downloads and decoded WAVs are preserved in `staging-sfx/first-pack`. The generation report records each prompt, billed character-cost header, duration, levels, and clipping measurements. Final assets are mono 48 kHz, trimmed and balanced with a -3 dBFS peak ceiling; UI sounds target a quieter level than combat sounds. One heavy-hit source contained a single full-scale sample, recorded in the report; all processed files have zero clipped samples.

Run `.venv\Scripts\python.exe tools\generate_sfx_pack.py` to rebuild the current melodic pack from its saved downloads. `--pack first-pack` deliberately restores the legacy 12-effect pack, replacing current UI and ordinary outcome cues. Existing downloads are reused without another generation request; missing downloads require the local `ELEVENLABS_API_KEY`. The key stays outside the client and generated reports.

## Future expansion

After the first pack sounds coherent in game, generate ranged release, arrow impact, magic cast families, fire/freeze/status applications, footsteps by terrain, doors, chests, barricade damage, wall collapse, prisoner handling, and event ambience. Do not generate all of these before approving the first pack; the chosen first pack becomes the audible reference for later prompts.

## Bard Song pack

> Modern fantasy MMORPG lute performance, short readable fantasy game cue, warm wooden lute and soft hand percussion, clear melodic identity, restrained reverb, no voices, no lyrics, no battle impacts, no ambience, no long loop.

| Filename | Length | Prompt |
|---|---:|---|
| `bard_jeering_verse.wav` | 1.8 s | A sly descending lute phrase with one playful dissonant pluck and a quick mocking cadence, mischievous battlefield provocation. Ends cleanly and immediately. |
| `bard_cue_strike.wav` | 1.2 s | A crisp conductor cue: two bright lute plucks and a short rising hand-drum pickup, decisive and encouraging, like ordering an ally to strike now. |
| `bard_accelerando.wav` | 2.4 s | A quickening lute ostinato that accelerates into a bright clean flourish, agile and energizing, suggesting channeling time collapsing into an instant. |
| `bard_quickening_chorus.wav` | 2.4 s | A precise repeating lute rhythm with clocklike hand percussion and a light upward turn, suggesting abilities returning faster. Clearly rhythmic, controlled, and cleanly resolved. |
| `bard_war_anthem.wav` | 2.8 s | A bold rising lute-and-frame-drum war anthem, compact heroic melody with warm strings tucked behind it, encouraging allied offense without becoming a full orchestral fanfare. |
| `bard_song_of_peace.wav` | 2.8 s | A gentle suspended lute melody with soft breathy flute and a calm final chord, disarming and serene, clearly signaling a temporary no-attack sanctuary. |

## Selection rules

- UI sounds must remain quiet enough to tolerate rapid clicking.
- Swing and impact must be separate files so animation timing stays precise.
- Death and unconscious sounds must be distinct without using voices.
- Avoid huge bass, long tails, orchestral layers, modern firearms, and glossy mobile-game sparkle.
- Keep one primary sound per action initially. Add two or three alternates only after the primary mix works.
- Trim leading silence. Leave a few milliseconds at the start to prevent clicks.
- Normalize related sounds together rather than maximizing every file individually.

ElevenLabs currently supports individual sound generation, four variations per generation in its web interface, non-looping WAV downloads, fixed or automatic durations, and prompt influence. Its documentation recommends generating separate effects and combining or timing them in the game instead of requesting complex sequences.


## Regional ambience v1

Use `tools/generate_event_ambience.py` for the seven authored environmental accents. This is a separate pack from the action/mission cues above. Exact prompts, source MP3s, API-reported cost, and technical checks are preserved under `staging-sfx/event-ambience-v1`. The original generation made seven requests (64 seconds requested total); receipt reports 640 credits. Existing source audio is reused; pending/uncertain requests block automatic paid retries. `--process-only` prevents generation. No new batch launcher is needed.

The shared palette is distant fantasy environmental detail with softened treble, no music or instruments, no intelligible speech, no screams or jump scares. Goblin chatter/camp activity, dragging undead procession, arcane disturbance, beast call/passage, and damaged Starfall machinery play sparsely; runtime does not continuously loop them. Preview at `staging-sfx/event-ambience-v1/LISTEN.html` or the Sound settings ambience link. The Ambient Sounds slider is independent of the other channels.

API reference: https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert

## Fighter contact pack

> Modern painted-fantasy tactical RPG Foley, warm rounded transient, no voices, no music, no metallic chime, dry close sound, no long reverb.

| File | Duration | Prompt |
|---|---|---|
| `body_collision.wav` | 1.0 s | One heavy padded body slams into a timber barrier: immediate low chesty flesh thud, short wood creak and scrape, then a tiny rebound scuff. Firm weight, no gore, no grunt, no explosion. Impact at the start, single hit. |

## Fighter weight pack

> Modern fantasy tactical RPG Foley. Warm low-mid weight, softened treble, close dry sound, no music, no voices, no gore, no UI chimes.

| File | Duration | Prompt |
|---|---|---|
| `earthbreaker_launch.wav` | 0.5 s | One powerful armored fighter launches into a jump: short boot push-off and dense air rush, a single rising whoosh. No footsteps, no landing, no rattling metal. Immediate start. |
| `earthbreaker_land.wav` | 1.2 s | One enormous boot-and-body slam into solid earth, instantaneous deep punchy impact, cracking dirt and stone, followed by a short expanding bass shockwave and settling grit. Powerful grounded weight, no footsteps, no repeated hits, no explosion. |
| `body_into_body.wav` | 0.7 s | One heavy clothed human body collides with another human body: immediate muffled chesty flesh thump, compressed fabric and a tiny rebound shuffle. Dense soft-body impact, no wood, no stone, no punch swish, no vocal grunt. |
| `body_into_wall.wav` | 0.8 s | One heavy clothed human body slams against a rigid wall: immediate dull flesh thud layered with a short hard masonry knock, gritty scrape and tiny rebound. Heavier rigid contact than body-to-body, no shattering, no explosion, no voices. |


Fighter weight pack playback revision (October 5): the importer preserves the
initial Earthbreaker landing impact, fades its existing tail from 0.28 seconds,
and ends it at 0.52 seconds. This is applied from the retained original on each
run, so rebuilding cannot accumulate edits. Wall collision gain is set in the
combat audio schedule at 0.63, versus body collision 0.50 (about +2 dB).
No regeneration/purchase was needed for these adjustments.


Superseding landing edit: Earthbreaker dry v3 (October 5) keeps only 0.22 seconds,
uses two 1 kHz low-pass stages and a 12 ms anti-click edge. The earlier long fade
is removed completely. This edit is reproducible from the original MP3. No new
paid generation. The game landing URL version is `20261005-landing-dry-v3`.

## Fighter crater boom pack

> Modern fantasy tactical RPG physical impact. Dark warm bass, softened treble, close grounded weight, no music, no voice, no magic, no pitched note or ringing metal.

| File | Duration | Prompt |
|---|---|---|
| `earthbreaker_crater.wav` | 0.8 s | Single crater impact: immediate deep bass BOOM, dense low earth cracking, short soft grit falloff. Dry physical weight beneath a boot slam. No whistle, rising tone, shrill accent, bells, sparkle or repeated hits. |


## Melee weapon families pack

> Modern painted fantasy RPG combat Foley. One isolated dry close sound, immediate onset, warm low mids, softened treble, tiny natural tail. No music, voice, scream, ringing tone or long reverb. SFW stylized impact.

| File | Length | Prompt |
|---|---|---|
| `melee_slash_swing.wav` | 0.5 s | One fast light steel sword slicing through air, smooth narrow silky swoosh, no contact sound. |
| `melee_slash_hit.wav` | 0.6 s | One crisp sword cut impact: brief soft leather slice layered with a compact fleshy thud. Clean fast cutting contact, subtle damp detail, no gore or splash. |
| `melee_hack_swing.wav` | 0.5 s | One weighty axe swing through air, broader lower rushed whoosh with slight haft movement. No impact. |
| `melee_hack_hit.wav` | 0.6 s | One heavy chopping axe contact: dense damp leather chop and short wooden crunch under a solid low thud. Weighty bite, clean bounded impact, no splatter. |
| `melee_crush_swing.wav` | 0.5 s | One heavy warhammer sweeping through air, low broad weighty whoosh, no clang or impact. |
| `melee_crush_hit.wav` | 0.6 s | One massive blunt hammer contact: compressed low body thump with brief gritty brittle crack and a tiny dull debris tail. Heavy crushing weight, no metallic ringing. |
| `melee_blunt_swing.wav` | 0.5 s | One quick wooden quarterstaff strike through air, dry mid-low swish with slight wood movement. No impact. |
| `melee_blunt_hit.wav` | 0.6 s | One wooden staff striking a padded body: rounded firm hollow wood knock over warm deep leather thud. Clearly a shove-like staff hit, no crunch, no ringing. |
| `melee_fist_swing.wav` | 0.5 s | One very short barehand boxing jab through air: tight cloth rustle and quick compact swish. No impact, no voice. |
| `melee_fist_hit.wav` | 0.6 s | One sharp fast fist contacting a padded body: punchy close leather smack and compact low thump. Snappy restrained boxing impact, no crack or metal. |
| `melee_stab_swing.wav` | 0.5 s | One fast spear or dagger thrust through air: narrow straight short air zip with dry grip movement. No impact, no high pitched whistle. |
| `melee_stab_hit.wav` | 0.6 s | One tight spear or dagger contact: short pointed leather puncture tick layered with a small damp low thud. Focused precise piercing hit, no ripping or gore. |

One shared contact time (185 ms). Swing and hit are separate clips so misses never play a flesh hit. Softened treble and controlled loudness keep repeated combat comfortable. Original MP3s and exact prompts remain in staging-sfx/melee-families-v1; normalized WAVs install under frontend/public/assets/sfx. Listening quality still needs human review.


## Capture net pack

> Modern painted fantasy RPG Foley, one dry close action, immediate onset, warm low mids and softened treble, short natural tail. No music, voice, scream, metal ringing or dramatic tone.

| File | Length | Prompt |
|---|---|---|
| `capture_net_cast.wav` | 0.6 s | One folded coarse rope net thrown open through air: quick cloth and rope unfurling swish, a few very soft dull bronze weight clicks, short decisive cast. No body impact. |
| `capture_net_cinch.wav` | 0.6 s | One coarse rope net landing and pulling tight around padded cloth: compact soft weighted thud, braided rope sliding under tension then tightening creak. Nonviolent restraint, no crunch or punch. |
| `capture_net_slip.wav` | 0.6 s | One thrown rope net slipping off padded cloth and dropping loose: brief dry rope scrape, soft loose fabric flutter and tiny dull weight taps. Failed catch, no impact hit. |

Landed contact tightens the net with real Squeeze damage at 320 ms. A successful capture displays Subdued; a failed capture displays Escaped and loosens with a quiet slip at 450 ms. Missed throws only slip, with no damage. Originals and technical report remain in staging-sfx/capture-net-v1. Listening approval remains a human review.


## Flesh contact pack

> Modern fantasy RPG close combat Foley. One isolated immediate contact, warm low mids, softened treble, short dry tail. No music, voices, screams, metal clang, ringing or long reverb.

| File | Length | Prompt |
|---|---|---|
| `melee_slash_flesh.wav` | 0.6 s | One fast sword slicing a lightly clothed flesh target: crisp moist slicing snap over a soft dense body thud, brief damp contact detail, tight immediate onset. No repeated cuts. |
| `melee_hack_flesh.wav` | 0.6 s | One heavy axe chopping a flesh target: deep wet meaty chop, short brittle bone crunch beneath a dense low body impact. Weighty single contact with very short damp splash, no prolonged squelching. |
| `melee_crush_flesh.wav` | 0.6 s | One heavy hammer striking an unarmored body: massive compressed fleshy thump with a short low brittle bone crack and brief wet impact detail. Deep crushing weight, no metal or wood collision. |
| `melee_stab_flesh.wav` | 0.6 s | One spear or dagger puncturing a lightly clothed flesh target: tight moist puncture snap and compact deep body thud, brief damp penetration detail. Single quick focused contact, no tearing tail. |
| `melee_blunt_flesh.wav` | 0.6 s | One wooden staff hitting a cloth covered body: firm rounded fleshy thud with short fabric compression. Dry bloodless impact, no crack, wet splash or metallic sound. |
| `melee_fist_flesh.wav` | 0.6 s | One fast bare fist striking a lightly clothed body: tight sharp skin smack with compact chesty bass and tiny cloth rustle. Dry bloodless boxing impact, no crack or wet splash. |

Selected from target material, not armor points. Cutting, piercing and crushing organic hits use stylized crimson art; fist/blunt remain bloodless. Original family impacts remain the metal/rigid-target variant. Sources and listening previews stay separate. Capture-net damage uses rope tightening and never flesh/blood effects.

## Martial Jobs pack

> Cohesive modern painterly fantasy RPG combat SFX, dry close impacts, warm low mids, restrained treble, no music, no speech, no metallic ringing tail, no shrill magic chime.

| File | Duration | Prompt |
|---|---|---|
| `martial_brace.wav` | 0.6 s | A warrior firmly braces a shield: short leather creak, dull armor settling, grounded low thump. Confident defensive weight, no sword ring. |
| `martial_second_wind.wav` | 0.8 s | A quiet rush of restorative breath, soft cloth flutter and gentle warm air lifting. Calm physical recovery, no voice, no sparkling magic. |
| `martial_victory.wav` | 0.6 s | Brief heavy victorious strike accent, low wooden thud opening into a warm airy release. Clean punchy payoff, no fanfare or musical notes. |
| `barbarian_reckless.wav` | 0.6 s | Powerful furious weapon acceleration: restrained deep whoosh with rough leather strain and a short bass punch. No shout, no metallic ringing. |
| `barbarian_skullbreaker.wav` | 0.5 s | One dense crushing impact against a padded steel helmet, low solid body thump and short gritty crunch. Heavy stun hit, no gore, no ring. |
| `barbarian_groundbreaker.wav` | 0.8 s | Huge physical ground strike: immediate bass-heavy thump, stone cracking outward and gravel scattering, short dry dust decay. No magic, no high-pitched tail. |
| `barbarian_defiance.wav` | 0.7 s | Defiant survival pulse: two deep heartbeat-like impacts beneath rough armor creak and a restrained rising warm rumble. No speech or musical tone. |
| `barbarian_unstoppable.wav` | 0.5 s | Iron restraints snapping apart: tight chain strain, decisive low crack, short falling metal pieces. Crisp liberation accent, no ringing or sharp whistle. |

## Rogue action pack

> Modern painterly fantasy RPG tactile effects; soft restrained transients, no music, no voices, no metallic ringing or shrill magical chimes. Short dry close perspective, controlled volume.

| File | Duration | Prompt |
| --- | --- | --- |
| `rogue_shadowstep.wav` | 0.7 s | A leather-clad figure vanishes into soft smoky cloth vapour and reappears. Two muted airy swishes. |
| `rogue_backflip.wav` | 0.7 s | Quick leather-cloth backflip whoosh followed by soft boots landing on packed dirt. Light agile movement. |
| `rogue_caltrops.wav` | 0.7 s | A handful of small steel caltrops scatter onto dirt with three quiet dry taps and tiny gritty scrapes. |
| `rogue_knife_throw.wav` | 0.5 s | A small throwing knife flicked quickly through air. Brief restrained cloth and air swish, no impact. |

## Druid nature pack

> Fantasy tactical game sound effect, dry close recording, no music, no speech, no metallic chime, no shrill tail.

| File | Duration | Prompt |
| --- | --- | --- |
| `druid_prowler.wav` | 1.0 s | Air rush and leaves spiraling into a brief restrained panther growl. Agile transformation, soft start, decisive organic finish. |
| `druid_bulwark.wav` | 1.2 s | Deep woody creak and swirling leaves settle into one short bear growl, heavy earthy transformation with a low thump. |
| `druid_rat.wav` | 0.7 s | Quick dry rustle of leaves contracting with tiny paws skittering, subtle short rat squeak, light evasive transformation. |
| `druid_growth.wav` | 1.2 s | Living roots growing rapidly, branches creaking softly and leaves unfurling, warm organic restorative magic, no tonal ringing. |
| `druid_vine_lash.wav` | 0.6 s | Thorny vine whips through air then slaps flesh with a dry leafy snap, short powerful organic lash, hit louder than swing. |

## Summoner spirit pack

> Cohesive painterly fantasy RPG effects, warm low mids, short restrained treble, no music, no speech, no shrill ringing tail. Clear close impact with a soft natural decay.

| File | Duration | Prompt |
| --- | --- | --- |
| `summoner_conjure.wav` | 1.0 s | A spirit gathers into a small creature: soft airy spiral, rounded resonant pulse and compact warm arrival thump. Magical yet tactile, no bells. |
| `summoner_transposition.wav` | 0.7 s | Two short spatial folds swap places: quick soft vacuum pulls followed by paired low airy pops. Clean teleport, no sizzling high frequencies. |
| `summoner_projection.wav` | 0.8 s | A concentrated spirit bolt rushing forward and striking with a dense warm magical pulse, quiet launch and stronger rounded hit. |
| `summoner_sacrifice.wav` | 0.9 s | A bound spirit collapses then explodes: tiny intake, weighty bass impact, scattered airy energy with a short dry tail. No glass, no whistle. |
| `summoner_overload.wav` | 0.9 s | A creature is flooded with unstable power: rising low electric rumble, tight pulsating pressure and one decisive deep surge. No sharp zap. |
| `summoner_life_pact.wav` | 0.8 s | Living energy transfers between two beings: soft heartbeat, warm flowing breath and a gentle restorative pulse. No voices or musical notes. |


## Engineer machinery pack

> Grounded hand-built wood and iron mechanisms, warm low mids, dry tactile attacks, restrained treble. No music, speech, magical chimes or shrill ringing tail. Powerful impact louder than preparation.

| File | Duration | Prompt |
| --- | --- | --- |
| `engineer_assembly.wav` | 0.9 s | Quick wooden brace settling, two muted iron ratchet clicks, final solid locking clunk. A small ballista has finished assembly. |
| `engineer_overclock.wav` | 0.9 s | Heavy mechanical crank accelerating, low unstable motor strain with tight iron vibration. Short weighty surge, no alarm or high pitch whine. |
| `engineer_explosion.wav` | 1.0 s | Compact ground-level black powder explosion, deep punch and crunchy wood iron debris, short dry rumbling decay. No whistle or ringing. |
| `engineer_mine.wav` | 0.6 s | Pressure pin clicks then a sharp concussive low explosion with dull earth scatter. Close grounded stun charge; no electrical or magical sound. |

## Engineer explosive bolt refinement

`tools/generate_engineer_impact_sfx.py` generates one retained ElevenLabs clip, `engineer_bolt_explosion.wav`: wooden bolt contact followed by a low black-powder boom and short debris decay, no music, voices, whistle, ringing or magic. Prompt, originals and technical metrics live in `staging-sfx/engineer-impact-v2`; reused on subsequent runs. Heavy contact anchors this cue and the cross explosion.

Rapid Assembly: `engineer_rapid_assembly.wav`, 0.9-second mechanical ratchet/tool/latch ready cue with no magic or ringing; original and metrics under `staging-sfx/engineer-preparation-v1`. Existing generator retains originals to prevent repeated billing.


## Animal combat pack

> Isolated organic animal game sound, dry close microphone, no music, no speech, no metal, no reverb tail. Immediate onset, one short event, clean quiet ending.

| File | Duration | Prompt |
|---|---|---|
| `rat_attack_1.wav` | 0.7 s | Brown rat aggressive short chitter and breathy squeak before a bite, restrained pitch. |
| `rat_attack_2.wav` | 0.7 s | Brown rat quick raspy defensive chirrup and snort, compact attack effort. |
| `rat_attack_3.wav` | 0.7 s | Brown rat low coarse chatter with one short squeak, lunging attack effort. |
| `rat_bite_1.wav` | 0.7 s | Small incisors sink into flesh, soft wet puncture and tiny jaw snap, no crunching metal. |
| `rat_bite_2.wav` | 0.7 s | Small rat bite contact, damp sharp nip and brief skin tear, not a sword. |
| `rat_bite_3.wav` | 0.7 s | Rat incisors biting, short fleshy pinch and subtle jaw crunch, compact impact. |
| `rat_hurt_1.wav` | 0.7 s | Brown rat clipped startled squeak on being struck, no prolonged shrill whistle. |
| `rat_hurt_2.wav` | 0.7 s | Brown rat rough short pain chitter and gasp. |
| `rat_hurt_3.wav` | 0.7 s | Brown rat brief breathy distressed squeal on impact, subdued high end. |
| `rat_death_1.wav` | 1.2 s | Brown rat soft fading squeak and final exhale, short natural death vocal. |
| `rat_death_2.wav` | 1.2 s | Brown rat low rasping dying chitter tapering to silence. |
| `rat_death_3.wav` | 1.2 s | Brown rat last broken squeak and breath release, no melodrama. |
| `rat_swarm_1.wav` | 1.2 s | Three rats scurrying together, tiny claws and layered low rat chitters, quick gathering. |
| `rat_swarm_2.wav` | 1.2 s | Three rats regroup, close quick claw patter and overlapping short squeaks. |
| `rat_swarm_3.wav` | 1.2 s | Small rat group clusters, fur rustle, tiny footsteps and coarse social chatter. |
| `wolf_attack_1.wav` | 0.7 s | Wolf short throaty growl and explosive breathy snarl before biting, no lion roar. |
| `wolf_attack_2.wav` | 0.7 s | Wolf compact low rumble into a sharp attack bark, realistic canine. |
| `wolf_attack_3.wav` | 0.7 s | Wolf aggressive short raspy snarl with forceful exhale, no long howl. |
| `wolf_bite_1.wav` | 0.7 s | Wolf jaws clamp into flesh, deep damp puncture and brief heavy jaw snap, no metal. |
| `wolf_bite_2.wav` | 0.7 s | Wolf bite impact, short wet tearing contact and muted flesh compression. |
| `wolf_bite_3.wav` | 0.7 s | Canine fangs bite flesh, heavy fleshy thud with subtle puncture crack. |
| `wolf_hurt_1.wav` | 0.7 s | Wolf short startled pain yelp and breath, natural canine. |
| `wolf_hurt_2.wav` | 0.7 s | Wolf clipped rough whine and low grunt when struck. |
| `wolf_hurt_3.wav` | 0.7 s | Wolf sudden hoarse yip on impact, quick natural decay. |
| `wolf_death_1.wav` | 1.2 s | Wolf low broken whimper and final breath, subdued short dying vocal. |
| `wolf_death_2.wav` | 1.2 s | Wolf short fading canine groan and exhale, no theatrical howl. |
| `wolf_death_3.wav` | 1.2 s | Wolf quiet breathy yelp fading into a last low whine. |


## Bear combat pack

> Isolated natural brown bear game vocal, dry close sound, no music, no human voice, no metal, no long reverb. Immediate onset, one short event, clean quiet ending.

| File | Duration | Prompt |
|---|---|---|
| `bear_attack_1.wav` | 0.8 s | Short forceful bear huff and low growl as it swipes with a paw. |
| `bear_attack_2.wav` | 0.8 s | Bear compact raspy attacking grunt and heavy exhale, not a lion roar. |
| `bear_attack_3.wav` | 0.8 s | Brown bear brief chesty snarl and breathy effort on a claw swipe. |
| `bear_hurt_1.wav` | 0.8 s | Brown bear abrupt low pain grunt and snort when struck. |
| `bear_hurt_2.wav` | 0.8 s | Bear clipped rough groan on impact, no theatrical roar. |
| `bear_hurt_3.wav` | 0.8 s | Bear short breathy distressed growl from being hit. |
| `bear_death_1.wav` | 1.2 s | Brown bear last low broken groan and breath fading out. |
| `bear_death_2.wav` | 1.2 s | Bear short dying rumble into a final soft exhale. |
| `bear_death_3.wav` | 1.2 s | Brown bear subdued last grunt and weakening breath, no long howl. |
