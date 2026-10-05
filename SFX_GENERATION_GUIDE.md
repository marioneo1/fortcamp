# Fortcamp Sound Effects Guide

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
