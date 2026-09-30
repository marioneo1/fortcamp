# Fortcamp music direction — proposal, not generated

## Listening goal

Comfortable, memorable fantasy adventure music that survives repeated listening while reading contracts. Use Ragnarok Online / Tree of Savior only as broad mood references, not tunes to copy. The user specifically dislikes piercing high pitches. Favor warmth, a small memorable melodic motif, gentle rhythmic motion, and soft transients instead of brightness or loudness. Instrumental only; no voices, spoken words, or choir.

Shared palette: felt piano, softly plucked strings, mid-register flute or clarinet, warm low strings, rounded bass, and small restrained acoustic percussion. Keep leads in the middle register. Avoid shrill piccolo, sparkling bell leads, aggressive cymbals, exaggerated treble, hard EDM drops, and trailer-style constant crescendos. Not chiptune or deliberately retro.

## First four tracks

| Track | Job | Direction | Suggested initial source |
| --- | --- | --- | --- |
| Guild board | Public board, private contracts, roster, ordinary dialogue choices | Light forward motion, a memorable short melody, subtle variation; inviting rather than frantic | 100–120 seconds, approximately 88–96 BPM |
| Hearth & camp | Base management | A related melodic motif with fewer notes and lighter percussion, warm and settled | 100–120 seconds, approximately 76–84 BPM |
| Road encounter | Battles without dedicated music | Moderate strings and hand drums; tactical momentum without drowning out hits or exhausting the listener | 90–120 seconds, approximately 108–116 BPM |
| Goblin warcamp | Goblin camps and goblinoid skirmishes | Low woodwind rhythmic figures and rough but rounded drums, mischievous danger; related harmony and instrument treatment | 90–120 seconds, approximately 112–120 BPM |

Start with the guild-board pilot. Review the melody, treble comfort, repetition fatigue, and loop before generating the rest. Numbers are creative targets, not guaranteed output measurements.

## Guild-board pilot prompt

Original instrumental background music for a modern fantasy guild management RPG. Warm, inviting, quietly adventurous and pleasant for long reading sessions. Around 92 BPM with a steady gentle groove, felt piano, softly plucked acoustic strings, mid-register clarinet or mellow flute, warm low strings and rounded bass. A short memorable melody returns with small variations; leave generous space between phrases. Soft restrained hand percussion, smooth dynamics, controlled warm treble, no piercing high notes, no bright bell lead, no shrill piccolo, no harsh cymbals, no chiptune, no EDM drops, no vocals, speech or choir. Maintain a coherent repeating arrangement rather than a dramatic song arc. Start already inside the groove; avoid a long intro, breakdown or final cadence. End on a compatible phrase that can return to the opening. Approximately two minutes. Original composition, not an imitation of any existing soundtrack.

## Generation and installation workflow

Use the official ElevenLabs Music API, with `force_instrumental: true` in prompt mode and an explicit `music_length_ms`. Current compose documentation: https://elevenlabs.io/docs/api-reference/music/compose/. Read ELEVENLABS_MUSIC_IMAGE_KEY only from local environment/.env in the generation tool, never frontend code or a committed file. The key has not been used for paid music generation in this pass.

Save immutable source, exact prompt, model, duration, and non-secret request metadata under staging-music/<pack>. Avoid automatically retrying an uncertain paid request. Keep approved runtime assets under frontend/public/assets/music, with a manifest linking context, source, loop boundaries, and gain. Never silently replace an approved version.

A loop request is not proof of a seamless loop. Find musically matching boundaries, trim at phrase/bar boundaries, and use a small crossfade only when needed. Preserve the original. Check loudness, clipping, abrupt transients, silence, and the seam across several repetitions. Match perceived volume between tracks; peak normalization alone is insufficient. Human listening remains necessary for style and fatigue.

## Runtime design, after tracks are approved

- Browser playback unlocks after a user gesture; load only the selected context, not the whole library.
- Music is selected by location first, then battle scenario/faction; bosses can override where authored. Do not change track on every turn, click, or dialogue selection.
- Crossfade approximately 1–2 seconds between board/base/battle; preserve the current track on ordinary UI redraws.
- Music follows Master × Music. Clicks and success/failure stingers share Master × Interface & Mission Sounds. Combat effects follow Master × Battle Effects. A stinger can briefly duck music without changing the saved volume.
- Keep music softer than important action feedback, while allowing the user to reverse that balance. Controls persist on the device and include mute.
- Future packs: undead dread, ruins/mystery, defense siege, major boss, and rare-event variants. Generate only when enough playable content justifies a separate theme.
