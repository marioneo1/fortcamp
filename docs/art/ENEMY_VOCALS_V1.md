# Wordless humanoid combat vocals
October 9, 2026; installed in dev after user approval. Not pushed/released.

## Installed scope

Future-generation direction, accepted October9: user finds some Human male
attacks resemble pain or coughing, but accepts the current pack for now. Do not
regenerate or replace them solely on that feedback. Future attack vocals across
new voice identities should follow the approved female attack approach: proactive
projected martial exertion, immediate committed onset, strong voiced short finish.
Avoid pain gasps, coughing, hesitation, cheering, weak/wavering endings and moans.
Use the installed approved female attacks as listening references, adapting pitch
and timbre to race/gender/personality rather than copying female audio into male
slots. Audition a small set before expanding; pain/death remain distinct events.

144 wordless clips: Human/Goblin ? male/female ? Guardian/Strategist/Opportunist/
Survivor ? three attack/hurt/death variations. Audited humanoid encounters opt in;
recruits preserve the identity key. No additional races/personality packs added.

48 approved female revisions live in assets/sfx/enemy-vocals-female-v2:
12 Human female attacks, 12 Goblin female attacks and 24 Goblin female hurt/death.
Goblin hurt/death reuse the six reviewed Guardian variants across all four female
personalities; attack variants remain personality-specific. Guardian Death3 uses
its existing first0.70s with short edge fades; trailing breath removed as requested.
The other96 male/Human female pain/death clips stay in enemy-vocals-v1 unchanged.

SFX uses shared timbre prompts, not voice cloning. All new installed revisions
were approved by the user; no unreviewed pain/death variants generated in cleanup.

## Runtime

Identity assignment: backend/combat_vocals.py, called only by the authored
encounter profiles. combat_voice_key is copied to battle units from recruits.
frontend/src/enemy-vocals.js registers the files and schedules cues through the
same impact timeline as weapon sounds. Weapon contacts are retained; voices
are quieter. Misses can produce effort; no damage means no hurt. Direct physical,
elemental, collision, fall and Resolve hits can produce pain; status applications,
healing and ongoing DoT ticks do not create repeated hurt vocals. Unconsciousness
uses hurt, not death. Death follows its actual resolved event, never final state.
Duplicate packets and closely spaced multi-hits are suppressed (900ms effort,
500ms pain per unit). Death bypasses those rate limits.

Only the current battle's voice keys warm their nine clips, in the background.
Decoded audio is reused in memory; no global 144-clip preload and no awaited
voice fetch during map loading. Cold-cache/failed downloads can still delay or
omit a first vocal; gameplay is never blocked waiting for voice audio.

## Tester, sources and restoration

Follow-up tester bug fixed: headings formerly hardcoded "female", including
male rows. Labels and now-playing gender now follow the parsed filename identity.
Audio paths and combat routing were correct; all144 source hashes verified,
all72 male/female audio pairs differ. Browser regression checks all144 rendered
identities and playback URLs for male/female Human/Goblin Survivor Death3.

One tester: assets/sfx/voice-tester/preview.html. All144 installed clips, race/
gender/personality/event filters, single and sequence playback, volume, local
Keep/Redo/Clear ratings, notes, copy filename summary and JSON export. Ratings
never change combat automatically. Browser storage/clipboard fallbacks supported.

Exact approved WAVs, original MP3s and source metadata preserved together in
staging-sfx/enemy-vocals-approved. manifest.json records selected versions and
SHA256 checksums. tools/rebuild_enemy_vocals.py restores exact approved WAVs and
rebuilds the tester offline; no credentials or generation/API calls required.
Historical failed auditions, original requests and generation scripts are archived
in staging-sfx/archive/female-vocal-review-20261009.zip (verified ZIP integrity).
Superseded public preview folders, overridden old runtime WAVs, decoded intermediates
and old QA directories moved out of active folders. Do not reinstate failed revisions from the archive.

## Validation

Ten vocal tests pass, covering valid144 WAVs, revision routing, ranged/melee/net,
misses, killing-event timing, unconsciousness, multi-hit rate limits and unchanged
animal/default routing. All installed files are mono48kHz, nonempty, unclipped;
exact approved hashes retained. Tester browser QA checks playback, filters,
ratings persistence, filename feedback, stop/sequence and mobile fit.
No production saves, credentials or processes changed.

Cleanup note: automatic approval review blocked bulk deletion with no more specific
reason than "blocked by policy". Obsolete files were instead moved safely into
staging-sfx/archive/superseded-files-20261009, outside active runtime/tools/QA
paths; originals and historical feedback pages remain recoverable there.
Final build passes with the existing chunk-size warning. No restart or push.
