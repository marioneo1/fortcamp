# Bard rework

Bard is a planted battlefield conductor. The eight-skill kit extends the existing
combat actions, statuses, cooldown clocks and targeting. No new combat loop.

## Current kit and performance rules

Starter skills: Jeering Verse, Cue the Strike and Battle Musician. Unlocks:
Accelerando, Quickening Chorus, War Anthem, Song of Peace and Maestro.

All Songs cover one cell around the Bard, including diagonals, with clear sight.
Previews, active overlays and actual acquisition use the same wall-filtered area.
A unit acquires effects at a committed resting position; simply traversing the
area does not grant a buff. Remaining inside refreshes the effect.

Starting and stopping use a normal action. Performing locks normal movement.
Battle Musician permits normal weapon attacks while performing, without ending
it or granting free attacks. Maestro allows replacing a Song with one normal
action; otherwise stop first, then start the replacement on a later turn.

War Anthem gives settled allies +20% direct damage (not damage over time).
Quickening Chorus gives allies one extra cooldown tick at activation start,
once per activation. Recovered cooldown progress is permanent, not a temporary
availability discount. The performing Bard does not benefit from either Song.
Their acquired buffs persist through the recipient's current and next activation,
then expire unless refreshed. This also holds when the source stops, switches,
becomes unconscious or is defeated. No duplicate copies of a Song stack; another
performing Bard may refresh the same buff. Different Songs can coexist.

Accelerando removes Channeling delays while properly inside its live area, without
removing normal action/cooldown costs. Meteor resolves immediately without a stale
channel or delayed event. Accelerando has NO LINGER.

Song of Peace has NO LINGER and automatically stops when the Bard starts their
second following activation, as explicitly confirmed by the user. Every unit inside,
including the Bard, cannot initiate basic attacks or damaging skills. Movement,
Guard and non-attack utility remain available. Attacks initiated outside may hit
into the area or move the attacker inside as part of resolution. Ordinary walking
into the area before attacking does not bypass the restriction. Leaving or ending
the performance removes the restriction immediately. Restart cooldown: five turns.

Jeering Verse is non-resistable: the enemy must deliberately target the Bard for
two target activations. Both receive +20% direct incoming damage vulnerability.
Cue the Strike is a Quick Action: select an ally and legal enemy for an immediate
Basic Attack, respecting the ally's weapon range and sight with no free movement.
It does not consume the ally's upcoming activation. Use it before the Bard's main
action; starting a Song ends that activation, while an already performing Bard
may use Cue on a later activation.

## Usability and validation, October 7, 2026

Descriptions now explain actual range, acquisition, expiry, costs and NO LINGER.
Stop Playing does not display the Song restart cooldown as a stop restriction.
Ordinary Song forecast labels appear only on eligible allies; Peace includes
both teams and the caster. Dedicated note overlays contain no binding artwork.

Automated coverage includes lingering through the next recipient turn after stopping,
NO LINGER exit/stop, Peace expiry, Maestro switching, source defeat, duplicate Bard
refresh, route traversal without acquisition, wall-filtered coverage, persistent
cooldown recovery and Accelerando Meteor. Browser fixture: tools/bard_browser_qa.mjs
with tools/build_mage_preview.py and tools/serve_board_preview.mjs; no live saves/API.

## Deferred work

Personality-aware Bard AI is a separate task: choose, stop and switch performances
based on hidden personality, allied cooldowns/channels, threats and objectives.
Current AI can start Songs; it does not plan those decisions well. Do not broaden
this behavior pass into an AI redesign. Numeric balance and multi-Bard encounter
playtesting remain open. A dedicated generated performance effect sheet is deferred;
current visuals use performance washes and animated musical notes.

## October 7 self-target visual correction

SELF target labels now bypass generic portrait styling: no circular clip, portrait-sized empty background, or displaced empty face beside the Bard. Browser checks cover all four Songs and verify rectangular label size/clipping; a full-command backend regression verifies Accelerando and Quickening Chorus create no new units. Live confirmation of the reported blank circle remains open. Song rules, durations and AI are unchanged.
