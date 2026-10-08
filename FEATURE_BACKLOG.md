# Fortcamp feature backlog

## October 7: Captor / Resolve

Implemented: eight-skill Captor, separate lethal Attack and Resolve Subdue, isolation forecasts, paired Abduct, uncapped earned Hold with 0.75x Resolve ticks, free release, Blitz, Disarm, unconscious recovery, migration and generated art/audio. See docs/design/CAPTOR_REWORK_REVIEW.md. Open: boss capture pacing, numerical/art/audio playtesting, personality-driven capture AI and coordinated isolation/drag planning.

## October 7: Summoner autonomous kit

Implemented: eight Job choices, Fire/Earth/Grass companion selection, atomic
three-Wisp placement, autonomous movement/attacks, persistent one/all commands,
Reclaim, Transposition, Projection, overlapping friendly-fire Sacrifice, Overload,
Life Pact, Rapid Conjuration and legacy loadout migration. New summons act after
the next owner activation, without manual turns or the legacy automatic damage
budget. Generated portrait/icon/effect atlas and six Summoner SFX; Battle Lab
uses the new catalogue. See docs/design/SUMMONER_REWORK_REVIEW.md.

Follow-up implemented: Grass inherits full INT/max HP and attacks with normal
INT-powered damage. Summon Orders is a numbered/reorderable innate skill-bar tile
with its command popup, costing no equipped slot. Defeated/dismissed summons retain
presentation bodies until their actual playback event, including birth and death
within one response; final server cleanup no longer hides them ahead of attacks.

Protect Ally is implemented for Bound Companions, including targeting their
Summoner. Grass heals the assigned ally and centers defensive bursts on them;
Earth/Fire stay near and prioritize threats. Follow is now Follow Summoner.
All-summons Protect affects only the Companion; unavailable targets fall back
to the Summoner. This remains best-effort support, without attack interception.

Open: live numerical/aesthetic playtesting; coordinated multi-summon planning;
personality-aware Summoner caster/enemy AI. Current owner auto-play is conservative
and does not plan sacrifice/overload/swap combinations. Creature commands are
best-effort goals, and creatures do not open doors. Engineer rework remains separate.

## October 7: Bard behavior and usability pass

Fixed recipient-timed lingering after stop/switch/source defeat, immediate NO LINGER
removal, persistent once-per-turn Quickening cooldown recovery, instant-Meteor return
exception, and wall-aware shared Song areas. Updated player descriptions and Stop
Playing cooldown presentation. Song of Peace retains the user-confirmed automatic
stop at the Bard's second following activation and never lingers.

Deferred: personality-aware Bard AI for performance choice, switching, stopping,
commands and provocation. Work on this separately alongside hidden personalities;
current behavior pass does not redesign AI. See docs/design/BARD_REWORK_REVIEW.md.

## October 6: Bard battlefield conductor implemented in dev

Added the eight-skill Bard kit with planted Songs, one-cell acquisition refresh,
activation-timed lingering, NO LINGER Accelerando/Song of Peace, movement lock,
Maestro switching, War Anthem damage support, Quickening cooldown ticks, Jeering
Verse forced-target AI/vulnerability, and Cue the Strike's two-stage ally/enemy
command. The existing status, action, targeting, cooldown, attack and animation
systems remain authoritative. Added a painted Bard icon atlas/crops and six short
ElevenLabs lute cues. Frontend now supports Cue target selection and an active Song
slot's Stop Playing action. Accelerando Meteor resolves immediately without a stale
armed event. Focused job tests and frontend build pass; numeric balance, advanced AI
song planning and multi-Bard playtesting remain open. No production rollout.

Follow-up hardening in dev: Cue the Strike keeps its selected ally across redraws
and submits an explicit ally ID; the mission and Battle Lab command schemas now
preserve that second target; dead or unconscious Bards immediately release
their performance and NO LINGER Song statuses; Maestro preserves ordinary War Anthem
and Quickening lingering windows when switching; Song of Peace explains and
enforces its automatic two-Bard-activation stop; active Songs refresh a settled
unit's buff through its next activation without tile polling; Bard status icons are
compact on both tokens and the tray. Focused Bard tests (28), frontend tests
(332), and the frontend build pass. No production rollout.

## October 6: Connecting-screen regression fixed (implemented in dev)

Added the missing inert createHotContext interface required by Vite's versioned CSS imports. Its absence prevented game initialization; reproduced on the actual running dev page. Full source startup reaches the expected environment sign-in guard with no JS exceptions; fixture preview now uses the same steady client. Regression coverage includes context methods, style injection and versioned CSS. Restart the running launcher to replace its cached client. No save/auth/production changes. Reference: docs/design/DEVELOPMENT_RUNNER.md.


## October 6: Restore source dev and prepare spell images before playback (implemented in dev)

Rolled back build-before-start/preview dev mode after reported loading regressions. Vite source serving retains no-store headers and API proxy; steady mode uses a CSS-only client without sockets/reload logic. Optional live edit restores stock Vite; production unaffected. Initial HTML hides inactive screens before CSS arrives. Mage battle entry warms equipped effect assets; manual/auto responses await required image load/decode before the shared impact timeline, retaining command lock and bounded failure timeout. Pending: user confirmation over the actual tunnel; no claim that every first-load delay is gone. Docs: docs/design/DEVELOPMENT_RUNNER.md and docs/art/MAGE_V1.md.


## October 6: Uninterrupted dev playtesting and calmer fire (implemented in dev)

Normal dev launcher builds browser files then serves preview on 5174 with API proxy to 8001, retaining real login/bot/debug/dev saves. Removes Vite's reload client and backend automatic reloader from default playtesting. Optional FORTCAMP_DEV_AUTO_RELOAD=true restores live editing, with Python watches limited to backend. Latest logs are timestamped and previous sessions archived; failed builds stop startup. Scorched loops slowed to 3.2?4.0 seconds. Available log showed no backend crash/restart for reported browser refresh; dev reload/reconnect is plausible, exact original cause unproven. Pending: user confirmation during long play sessions and further flame-frame refinement if shape motion still feels excessive. Reference: docs/design/DEVELOPMENT_RUNNER.md and docs/art/SCORCHED_V3.md.


## October 6: Percentage DoTs and Scorched V3 (implemented in dev)

Burn 2%, Poison 10%, Bleed 5% target maximum HP per stack; regular damage and one-stack decay at target turn end. Burn resistance reduces damage, never application. Fire entry adds Burn and triggers its full pool without decay; traps add Bleed without immediate damage. Ranger cashout/previews follow the new clock. Overlapping ground renders/triggers once; one sixteen-frame overhead fire per cell replaces mini fires. Meteor is another 50% larger, faces upper-left, and reveals new ground at landing. Fireball cooldown is three. Canonical rules/art: docs/design/COMBAT_DOTS.md and docs/art/SCORCHED_V3.md. Pending: percentage damage/boss balance, human animation review and split multi-source tick credit. No production deployment or save reset.


## October 6: Mage friendly fire and larger cinder beds (implemented in dev)

Meteor?s falling sprite is 80% larger. Scorched cells retain soot and add a same-envelope central cinder bed plus three to five seeded, independently phased small fires using the existing shared atlas/CSS animation. Flash Freeze, Singularity, Meteor and Fireball include allies and caster in resolution and forecasts; Scorched ground also burns everyone. Auto-battle rejects currently friendly-occupied areas. Dash hazard forecasts include friendly Scorched ground and deduplicate overlapping fire. No new particle runtime or asset download. Canonical rules/art: docs/design/MAGE_REWORK_REVIEW.md and docs/art/MAGE_SURFACES_V2.md. Pending: large-map/device performance and human aesthetic/numeric review; AI does not predict later friendly movement into delayed zones.

## October 6: Dedicated Frozen and Scorched presentation (implemented in dev)

Two complete 4×4 generated atlases: portrait ice spread/stable patterns/fracture/thaw, and flat soot/ash/top-down flame frames/embers/smoke. Ice fits the face circle and uses actual contact timing. Scorch forms one feathered connected region, with stable variations and sparse offset fire; removes repeated lava tiles and explosion stamps. Removed Freeze's old binding-tether flash. Actual Chrome fixtures cover real portrait geometry, grass/dirt/stone, loaded art and cleanup. No damage, status, sound, save or production changes. Docs/prompts: docs/art/MAGE_SURFACES_V2.md. Pending: human aesthetic feedback, a separate Meteor centre impact mark and reconstructing ice that applies/breaks within one returned multi-hit activation.

## October 6: Mage elemental rework (implemented in dev)

Eight-skill Mage pool, three starter actives, five-slot progression and saved-ID migration. Wet → Lightning / Fire → Blister, delayed breakable Freeze → Wet, grouped Singularity, interruptible two-activation Meteor, friendly-displacing Typhoon, player-chosen per-hit weapon enchantments and slotted Debuffer reuse current engine systems. Layered Burn and painted Scorched terrain use committed routes, repeated/forced entries and ally-safe ground; no infinite ground-stack multiplication. Forecasts retain movement/cast combination and shared damage/push/next-actor timing. One packed 16-asset atlas plus five locally synthesized sound clips; no extra cloud or Effekseer dependency. Request-local preview caches reduced the measured 8×8 five-skill fixture from ~85ms to ~24ms. Canonical rules: docs/design/MAGE_REWORK_REVIEW.md; art: docs/art/MAGE_V1.md.

Pending: live rank balance, human audio/aesthetic review and multi-turn elemental AI/channel protection. No production rollout, save reset or Champion redesign. Final validation is recorded in docs/history/MISSION_REFINEMENT_PHASE.md.

## October 6: Ranger Marksman and Poison rework (implemented in dev)

Eight Ranger skills now share the existing five-slot Job system: Mark Quarry, Longshot, Multi-Shot, Rapid Fire, Poison Attack, Pestilence Shot, Rupturing Blow and Sharpshooter. Mark is an owner-specific main-action setup; marked arrows cannot miss. Longshot uses distance power and a separate 20% double-damage critical roll. Rapid Fire is a target-selected Quick Action with a legal equipped-attack pool and Basic Attack fallback; the chosen attack's cooldown is not spent, walking is committed/locked and the main action remains.

Ranger Poison stacks snapshot 8% attack (minimum 1 HP) for two independent target-start ticks. Imbue gives one stack per damaging hit of the next successful attack. Pestilence reduces ATK by 25% and amplifies all incoming damage by 25%, including allied damage and DoTs; it adds to Monk direct-hit vulnerability. Rupture consumes every owner's Poison/Bleed for half their remaining base potential; Bleed assumes future exertion. Sharpshooter grants 10% damage and two range after a stationary activation; discarded previews are free, committed/forced movement cancels it. Walking approaches use the unboosted range.

Packed painted icons/projectiles/contacts use the existing 220 ms contact and serialized playback, with readable owner/stack/crit/cashout forecasts. Generic proc/flat-damage budgets are bounded per volley. Legacy loadouts preserve practice and order. Existing practice tiers unlock all eight in Battle Lab; choose Ranger, practice 16 or 20, and select a five-skill build. No production rollout or save reset. Numerical rank-by-rank playtesting remains open. Canonical rules: docs/design/RANGER_REWORK_REVIEW.md; assets: docs/art/RANGER_V1.md.

Validation: 235 combined backend regression tests, 36 final Ranger checks, all 297 frontend tests, frontend build and real Chrome checks for both builds/projectile cleanup. Existing bundle-size warning remains.

## October 6: Painted tactical props and Rogue API fixes (implemented in dev)

Replaced the temporary steel-vector Caltrops with three seeded, pure top-down painted scatter props. They keep transparent gutters, contact shading, a small footprint, and the established subtle pulse/glow above terrain/props. New equal 4x4 atlas also supplies anchored Scrap Turret ready/fire/recoil/destroyed frames and its north-oriented bolt. The existing stationary Engineer turret now renders as a prop, aims toward its target, animates firing/recoil, launches a bolt to the shared 220 ms contact, and uses wreckage when destroyed. HP/hover controls and automatic targeting remain. Heavy turret variants, tools, spare bolts and bear traps are imported for later use; no new equipment or deployment rules are implied.

Fixed both Battle Lab and normal combat API schemas dropping `knife_skill_id` and Caltrops `rotation`. Knife delivery now reaches the engine for Basic Attack, Cheap Shot and Exploit Weakness. Vertical strips remain vertical after confirmation. Caltrops immediately attempt one Bleed/Hobble stack on occupants of newly placed tiles (including allies); resistance and Trap Expert apply. This triggers only the new strip, marks the current tile, and does not charge an extra entry for standing still. Later committed movement and push/pull continue adding stacks per entered tile.

Validation: 70 focused backend/Battle Lab tests and all 293 frontend tests, frontend build, real Chrome UI checks for Knife confirmation/strip rotation, painted prop display, turret fire/recoil/bolt cleanup and destroyed art. Existing bundle-size warning remains. No production rollout or save reset. Restart the dev server and refresh the browser for the changed request schemas. Art source/import details: docs/art/TACTICAL_PROPS_V1.md via docs/INDEX.md.

## October 6: Rogue confirmation and trap visibility fixes (implemented in dev)

Rogue attack selection and Confirm/Cancel now appear in the centre of the visible map viewport. R rotation stays in the bottom action-preview area. A selected Caltrops strip stays fixed while confirming; pointer motion only moves the unconfirmed hover preview. Invalid placement cannot commit; cancelling is free. Knife attack selection refreshes the selected attack forecast.

Fixed Throwing Knife + Exploit Weakness: the command sender now preserves an explicit skill ID instead of replacing it with the selected Knife utility. The underlying selected main attack and Knife cooldown resolve together; the main attack still ends activation. Multiple Quick Actions remain allowed before it.

Caltrops now use three small opaque steel spike silhouettes per tile, with a subtle glow and scale pulse, above terrain and props. Combat feedback and interaction controls keep their own foreground layers. Reduced motion disables the pulse. Prior atlas imagery is retained; it is no longer the persistent trap visual.

Validation: 24 Rogue backend tests, all 291 frontend tests and frontend build pass (existing bundle-size warning). Actual Chrome UI fixture checks centred prompts, rotation/cancellation, and the confirmed Exploit/Knife command IDs. Screenshot review covers the confirmation panel and trap layer. No production deployment or player-save changes.

## October 5: Rogue implemented in dev

Eight-skill positional saboteur replaces the overlapping legacy kit. Multiple Quick Actions precede one activation-ending main attack; normal walking locks, legal mobility remains. Confirmed Shadowstep/Backflip/Caltrop/knife controls, three starter actives, five slots, retired-ID/order migration and whole pool at 16 successes in Battle Lab. Real committed and forced routes stack independently expiring Bleed/Hobble; fixed a duplicate forced-destination entry. Shared timeline serializes knife impact/death/enemy actions. One packed atlas and four short normalized ElevenLabs sounds are installed. Canonical rules/art: ROGUE_REWORK_REVIEW.md and ROGUE_V1.md via docs/INDEX.md. 211 focused backend tests and all 289 frontend tests pass, along with the build (existing bundle-size warning). Actual battle-UI fixture covers placement/rotation/cancellation/landing/knife controls without JavaScript exceptions; Warcamp view median 8.9 ms locally. Remaining: player balance/aesthetic review and coordinated AI trap/escape planning. No production rollout or save reset.

## October 5: Rogue review, including multiple Quick Actions

Reviewed current Rogue definitions, skill costs/automatic finish, reversible movement, Bleed/Hobbled refresh rules, per-cell zones, forced routes, prepared traps, leaps, targeting, deployment and loadout migration. Canonical proposal: docs/design/ROGUE_REWORK_REVIEW.md (via docs/INDEX.md). User clarified that multiple Quick Actions are allowed, Caltrops is Quick too, and Backflip is Quick. Latest user correction: Rogue main attacks MUST auto-end the activation; Quick Actions can chain before the main attack only. No post-attack escape window. Recommend a separate normal-walk lock while retaining one main action. Knife changes delivery; Cheap Shot/Exploit remain separate attacks. Stack Caltrop Bleed/Hobbled applications, preserve shared route deduplication and readable forecasts. No Rogue gameplay code, save changes, new art/audio or production changes in this review. Implementation and balance testing remain pending.

## October 5: Monk buffs and selective boss resistances

Implemented in dev: Rapid Palm builds up to 30% direct-damage exposure for three target turns; Crushing Fist rolls a 50% stun after successful combo advancement. Iron Reversal grants 25 evasion against the struck enemy until next Monk turn. Breaking Combination grants 3 HP per landed attack for the next three Monk turns, including punches/Dash victims. Dash grants brief 10% single-target physical parry; magic/AoE excluded. New statuses reuse existing skill artwork and contact feedback. Damage amplifiers add, hit healing does not multiply generic procs, and preview damage includes per-punch exposure.

Boss unit inspection now shows selective innate status resistances, the separate one-turn control limit and temporary recovery lock. Shared chance rules cover abilities, weapon procs, collision stuns and zones; racial poison immunity remains. Chiefs can resist stun while remaining susceptible to poison/burn. Authored profiles support other boss weaknesses without a blanket resistance. 191 focused backend tests pass; frontend tests/build pass with the existing bundle warning. Tests cover caps, durations, enemy-specific evasion, hit healing, parry exclusions, stun/recovery and visible profiles. Final gameplay balance remains pending; start a fresh test battle to use updated snapshots. No production rollout.

## October 5: accepted Monk kit implemented in dev

Replaced the six overlapping Monk skills with eight sequence/mobility choices; full three-active starter, five equipped slots, unlocks at 2/5/9/12/16 successful contracts. Added deterministic owner-clock stages, budgeted multi-hit damage/procs, source-clock Open Guard, Iron Reversal, Footwork, short enemy-crossing dash with committed hazard forecast and stage-aware AI. Retired-ID migration preserves earned progress/order and leaves existing battle snapshots intact. Fighter/Barbarian rules and production saves were preserved.

One packed 4?4 atlas supplies square skill icons and physical contact/defensive/finisher sprites. Contact/audio/defeat share the existing serialized playback timeline. Browser fixture checked five icons, all combo stages and completion without runtime errors. Full Monk Goblin Warcamp preview measured ~19?23 ms locally. 121 focused backend tests and all 280 frontend tests pass, along with the build; the existing bundle-size warning remains. See MONK_REWORK_REVIEW.md and MONK_V1.md through docs/INDEX.md for behavior/media. Automated coverage includes budgets, gates, source expiry, hazards, concealment, migration and auto selection.

Remaining: manual Fighter/Barbarian/Monk comparison with equal gear/enemies; tune initial numbers and review the final effects in real battles. No production rollout in this pass. New cloud tagging, advanced Jobs, additional gear restrictions and a Ki resource were not introduced.

## October 5: Monk review and map-status spacing

Implemented in dev: map-status column gap reduced from 6px to 3px; wrapping rows fit actual badge widths instead of leaving unused 36px grid tracks around smaller passive icons. Row gap remains 6px. Browser spacing/dock checks, 21 targeted UI tests and frontend build pass; existing bundle-size warning remains.

Pending proposal: docs/design/MONK_REWORK_REVIEW.md records eight Monk skills, complete starter combo, five-slot choices, two-turn readiness windows, source-owned Open Guard, technique-budget multi-hit damage/procs and enemy-crossing dash. No Monk combat code, live saves, art/audio or production changes in this review. Next pass must implement/migrate and validate the agreed kit, including AI and animation timing; numerical balance remains untested.

## October 5: passive slots and combat skill arrangement (implemented in dev)

Layout refinement: card ? Traits ? skills ? commands share the desktop row, buffs below all four. Passive readiness map badges are 75% of their previous size. Narrow screens wrap rather than squeeze controls.

Slotted Job passives now appear alongside actives with automatic/passive tooltips. Drag-to-swap saves order without changing loadouts or spending actions; Arrange exposes every page together. Roster-character order persists in the authenticated player save; Lab testers remain local and isolated. Traits beside the horizontal acting card lists only innate/racial/equipment effects. Passive cooldown/once-use/reaction readiness has actual skill icons on map buffs, including cooldown counts and spent state. Open battle dialogs survive rerender/swap. Bloodthirst now heals 20% maximum HP per kill; three-turn cooldown and same-turn multi-kills remain. Details: docs/design/COMBAT_CONTROLS.md.

## October 5: Fighter additions and Barbarian Fury (implemented in dev)

Fighter adds Brace, Second Wind and Victory Strike. Barbarian now has innate five-segment Fury and eight authored choices, including direct-hit Bloodfury, health-based attack, death defiance, multi-kill healing and automatic one-status cleansing. Five shared active/passive slots remain. Existing learned/equipped Barbarian IDs migrate; earned practice unlocks additions. Existing battle snapshots and production stay unchanged.

Two 4?4 painted atlases supply square skill/status icons and transparent effect phases. Eight physical SFX are installed, with contact synchronization and no generic magic overlay on Fighter self-care. Battle Lab tiers extend through 20 successes. Canonical rules: docs/design/MARTIAL_JOBS_REWORK.md; media: docs/art/MARTIAL_JOBS_V1.md.

Still open: live balance/listening approval, deeper Fury-planning AI, authoring enemy Job kits, other Job presentation passes. No speculative universal skill scripting system or new runtime dependency.

## October 5: nonlethal restraint damage and armor-aware contacts (implemented in dev)

Subdue now has modest balanced restraint power. One outcome roll selects capture, landed-but-escaped, or miss. Landed attempts deal real damage through armor/Guard/Barrier; damage stops at 1 HP so a boss still needs its capture check. Successful captures add no fabricated damage credit. The preview shows contact/capture chance and HP damage; numbers, rope cinching and sounds share the 320ms contact marker. Escaped catches cinch then slip; misses cause no damage. Capture weapons still only use Subdue as their basic attack.

Six new flesh-contact sounds and one compact eight-sprite atlas distinguish organic light/unarmored targets from chain/plate and Automatons. Slash, axe, hammer and stabbing organic contacts use blood accents; clubs and fists remain bloodless. Numerical armor is not treated as metal. Existing hard impacts remain available. The haze trial was alpha-corrected before import; originals are retained.

Validation: 117 related backend tests, 247 frontend tests, build and browser playback of flesh, metal, Automaton, capture/escape/miss. Details: docs/art/FLESH_CONTACT_V1.md and docs/design/CAPTURE_AND_STARTING_ROLES.md. Listening approval remains pending; no production/live-save changes.

## October 5: weapon-aware melee, capture nets and Battle Lab equipment (implemented in dev)

Six basic-melee families now have distinct token poses, painted contact/fade art and paired swing/hit SFX. Driving Strike remains a blunt push; other authored Fighter skills keep their delivery. Contact stays at 185 ms and structure impacts remain distinct. Net capture opens/spins in flight and cinches or slips at the 320 ms result marker, with Subdued/Escaped feedback and three matching sounds. Capture remains nonlethal.

Battle Lab temporary Job testers each have a weapon dropdown: actual catalogue equipment, starter default or unarmed. Weapon stats, capture rules and gear abilities apply without modifying roster saves. Restart preserves the selection. See docs/art/MELEE_WEAPON_PRESENTATION_V1.md for art/import rules, audio previews and limits. Validation: 79 related backend tests, 244 frontend tests, build and isolated browser cases. Subjective audio approval remains pending; ranged redesign is deferred. Dev only.

## October 5: melee attacks against structures (implemented in dev)

Standard melee attacks against weapon racks, walls, gates and other destructible
terrain now emit a real melee swing, sharing its contact packet with structure
hit/break sounds. The renderer can animate an attacker whose target is terrain,
including terrain destroyed by that hit; it no longer requires a character token
for the target. Magical structure attacks also emit their existing projectile.

Validation: 120 related backend tests, 220 frontend tests and build pass; the 46-test
location/wall/Fighter/audio subset also passes. An isolated browser test checks
the rack lunge at the 185 ms contact marker and the playback input lock. Tests
cover surviving and destroyed racks. Existing bundle-size warning remains.
Dev only; no production or live saves changed.

The screenshot-only pathing report near the lower corner/door was not reproduced
by the player or in fresh-map checks. Deferred to the planned map/pathing rebuild
at the player's request. No speculative collision changes or snapshot tool added.
Walking is unchanged in this pass: free movement and attack-sequence walking use
a 5 px midpoint hop, 2 degree tilt and 2.5% scale change; their keyframe phase is
not identical. Forced movement remains a slide. Preserve these approved amounts
and disclose future changes to their presentation.


## October 5: lethal knockback and movement origin (implemented in dev)

Driving Strike and Earthbreaker retain their displacement when the impact kills
the target. A body can strike a solid object or living bystander; the surviving
bystander takes half the original impact damage and collision stun, subject to
existing immunity/resistance. Earthbreaker now declares collision stun as well.
Open-ground pushes do not stun. Corpse HP is not damaged a second time and no new
status is applied to a corpse. Bodies do not trigger ground damage/traps on their
forced route; lethal pits make pushed bodies unrecoverable. Death facts use the
final forced-movement cell, and presentation completes push/rebound before
collapse. Enemy playback continues afterward. Misses do not displace targets.

The provisional movement origin remains marked with a gold outline and START
label, including after choosing another destination. It resets when the movement
is committed or a new activation starts. Attack-sequence walking again has the
small 5 px hop, 2 degree tilt and scale change already used for free positioning;
forced movement remains a slide. This preserves the endpoint/rubberband repairs.

Validation: 114 related backend tests and 220 frontend tests pass. Isolated browser
checks confirm both lethal Fighter collisions finish motion before collapse,
restore the corpse marker, stun the living bystander without stunning the corpse,
and render the origin label. Tests cover open-ground lethal push, walls, a killed
bystander and stun immunity. Build passes with the existing bundle-size warning.
Use a new battle for the updated Earthbreaker skill definition; existing battles
retain skill snapshots. No production or live saves changed.


## October 5: attack rubberband and area forecast audit (implemented in dev)

Walking segments now end at their own path destination, rather than the final
position of the entire response. A unit can walk, attack, react and walk again
without jumping between the later saved tile and the attack tile. An attack
interrupting an unfinished player preview first settles the short visible path.
Hit reactions start neutral instead of showing recoil before contact.

The resolving-turn notice is positioned outside layout flow: it no longer
resizes a fitted map halfway through pixel-based motion. Earthbreaker's complete
650 ms landing effect and every victim push, rebound and collapse finish before
the next unit begins movement. Per-victim wave contacts remain distance-based;
floating damage labels can linger without delaying the next turn. One composed
transform animation per token is retained, not a separate rules engine.

Unit stats follow the lower right of the cursor, clamped to the screen, and hide
immediately when the pointer leaves the unit. Cards do not intercept the pointer.
Ground previews show compact labels at each affected visible unit. Earthbreaker
forecasts include damage after armor/guard/barrier, accuracy, push and resistance;
zone labels distinguish future entry damage/control or activation healing from
an immediate hit. Adjacent labels stagger with connector lines. Forecasts do not
consume statuses, shields, RNG or mutate the battle. Hidden enemies are excluded.
Collision damage, reactions and random on-hit bonuses remain conditional, not
included in the direct-hit estimate. Large crowds and extreme zoom still warrant
manual visual review; this is not a claim of exhaustive visual verification.

Validation: 110 related backend tests, 218 frontend tests and build pass. Isolated
browser tests verify walk/attack/later-walk poses at four timeline samples, no
premature shift in Driving Strike/Earthbreaker, rejected commands during playback,
unlock afterward, collision feedback, cursor following/immediate hide, and two
nonoverlapping area forecasts. A two-enemy fixture averaged about 10 ms per
battle_view call over ten runs; this is not a large-map benchmark. Existing bundle
size warning remains. No live saves or production changed.


## October 5: map-first combat workspace (implemented in dev)

Moved commands beside skills (3x2), removed the inspector rail, added readable
hover/focus unit stats and direct-hit forecasts using the actual damage rules.
Supplies/passives/history/options use centered dialogs; retained both auto modes
and exit confirmation. Wheel/pan plus one crosshair fit button replace zoom clutter.
Validated 109 backend / 211 frontend tests, build and desktop/narrow browser UI.
Ground AOE forecasts are implemented in the later motion audit.

## October 5: push-before-contact regression repair (implemented in dev)

Composed per-token motion prevents later enemy movement from overriding the
pre-hit pose. Player map commands, hotkeys and auto wait until attack/enemy
playback finishes; ordinary movement previews stay responsive. Validated 210
frontend tests, build and real-UI push-then-enemy-turn browser cases.

## October 5: Fighter power and wave contact (implemented in dev)

Driving Strike: 150% attack power, solid collision stun on both surviving people.
Chain Snare: two-activation, nonstacking 30% armor reduction alongside pull/slow.
Earthbreaker: 200% attack power; per-target wave contact after landing, with
separate collision timing. Existing cooldowns and resistance rules retained.
See docs/design/FIGHTER_COMBAT_REVIEW.md for rules and proposed future tradeoffs.
Validated 107 backend / 205 frontend tests and build; fresh battles required.


## October 5: battle readability follow-up (implemented in dev)

Moved primary actions to the right, enlarged skills/acting portrait/turn order,
and added a readable fixed Action Preview below commands. Enlarged sidebar text;
sidebar scrolling respects actual available height. Existing auto/targeting
controls retained. Frontend build/tests and browser checks passed.

## October 5: Layout A and Fighter disruption (implemented in dev)

Installed real Layout A with painted action icons/keycaps, End Turn art, field
inspector, bottom command dock and both auto options. Refined Fighter into
Chain Snare, Earthbreaker and nearby-allies Fear rally; retained stable loadouts.
Added bounded area/leap resolution, Hobbled, ring previews, automatic-play
choices, synchronized leap/landing/chain effects and a compact six-cell art pack.
Validated 105 related backend / 205 frontend tests, build and isolated browser
checks. Player visual/balance review and the broader Mage ground/Barrier pass
remain pending. See docs/design/FIGHTER_COMBAT_REVIEW.md.


## Next: Combat presentation polish (proposal)

Current effects are not approved final art. Align visible contact with damage/
sound; add collision bounce and bystander recoil. Validate basic melee, Driving
Palm, Ember Ground and Shelter as a complete scene before scaling. Generate
consistent painted skill icons with function accents, a translucent forcefield
and proper ground-zone art in planned uniform packs. Audit every Job/gear skill
after the representative scene is approved. Custom damage fonts remain deferred.
See docs/design/COMBAT_PRESENTATION_PLAN.md. This pass documents the plan only.

## October 4: Combat impact and damage feedback (dev)

Implemented half-hit solid/person collision damage, including friendly fire and
Barrier absorption. Ember crossings now deal 3 damage once per activation;
Scorch remains a targeted Burn effect. Added typed floating actual-damage/heal/
status numbers, absorbed damage labels, shield capacity/halo and distinct Guard
outline. Knockback begins at impact; following enemies wait through the action.
Four generated impact sounds share the visual timeline and Battle volume.
88 backend / 197 frontend tests and build pass; isolated browser review confirms
feedback/shields. See docs/design/COMBAT_IMPACT.md. Production and saves untouched.
Skill-specific artwork and further VFX variety remain future work.

## October 4: Combat controls, targeting and animation timing (dev)

Fixed provisional movement returning to its origin. Unused End Turn now grants
Guard; Guard reduces the next direct hit by 25%. Added map skill hotbar with
1-9/0 keys and unrestricted overflow pages, right-drag panning and viewport
status cards. Pure zone skills can target empty ground with exact clipped areas.
Allied and ground casts now support combined movement with path/destination
previews; offensive movement-and-cast remains. Self casts highlight the caster.
Projectile/death animations reserve time before following enemy animations.
78 backend and 192 frontend tests, build and isolated browser checks pass.
Canonical: docs/design/COMBAT_CONTROLS.md. No save resets or production changes.
Further area shapes, deliberate summon placement and authored skill artwork remain
pending; this does not add arbitrary ground damage or new attack effects.

## October 4: Job testing in Battle Lab (dev)

Added temporary parties of up to four starting Jobs, matching starter equipment,
practice presets (0/2/5/9) and selectable learned skills with the regular five-slot
limit. Roster-copy mode and mission/approach/seed controls remain. Helper defaults
off; restart retains the request. Backend snapshot/isolation validation and
isolated browser controls/payload checks pass; frontend build passes. No production
or player-save changes. Canonical: docs/design/BATTLE_LAB.md. Broader balance,
personality-aware skill AI and dedicated summon commands remain pending.

## October 4: Twelve starting Jobs and first unlocks (dev)

Published all twelve Jobs together in character creation with matching Common
poor-quality kits. Removed Medic and independent work-proficiency selection;
legacy medicine characters retain Field Care. Three starting skills are equipped
and three more unlock at 2/5/9 successful contracts: 72 executable skills total.
Five character slots remain shared by actives/passives; gear abilities are uncapped
and consume no character slots. Unlocks never automatically equip or grow stats.

Vendor stock includes all starter equipment, using existing art pending a coherent
icon pack. Improved regeneration targeting and commanded-unit auto attacks. Fixed
closed-door pursuit stalls and creature objectives inheriting chieftain capture
resistance. Captor Binding Line now allows a follow-up capture attempt and Sure
Grip adds four capture points. Solo Captor combat is still harder; advanced kit
AI, unique conditional passives, full draft catalogues and device art are pending.

Validation: 124 related backend tests, 189 frontend tests and frontend build pass.
Isolated browser checks cover twelve creator choices, starter previews, six-skill
progression cards and five-slot swaps. All twelve solo Storehouse smoke encounters
finish without stalling; not all builds win automatically. Existing large bundle
warning remains. Canonical: docs/design/JOB_LOADOUTS.md.

At the user's request reset only Grimm and Local Tester in data/fortcamp-dev.db,
with SQLite backups and Discord registrations preserved. Cleared their 59 owned
contracts and associated result notices. Shared board and production untouched.
The reset tool supports --keep-registration; no credentials or media were pushed.

October 4 deployment foundation (dev): seven trial profiles, owner-linked clocks, finite Components/capacity, shared automatic output, commanded movement/attacks, manual turret operation and dismissal implemented. No extra initiative turns, immediate deployment shots, corpse loot or prisoners. Context controls/resources and tooltips installed; no starter Jobs released. Next: dedicated ground placement/command UI, repairs/reclaim/release skills and full Job loadouts/AI/catalogues. Canonical: docs/design/COMBAT_DEPLOYMENTS.md.

October 4 spaces foundation (dev): four bounded zone rules, real committed-route entry, overlap/expiry/owner checks, and two reversible form profiles implemented. No HP refill, race rewrite or new starter kits. Zone/form overlays and tooltips installed. Canonical: docs/design/COMBAT_SPACES.md. Next: owner-linked summons/devices, ground-target/command UI and Job loadouts; all twelve Jobs still launch together.

October 4 tactical dependency pass: finite Barrier, owned Mark, status expiry/recovery, shared bounded interception/counters, straight displacement and authored pit outcomes implemented in dev. Tower Shield, Duelist Gloves, Precision Shot, Hook Thrust and Titan Thrust are pilots. Next: zones/forms/summon economy, then loadouts/UI/AI and all twelve Jobs together. Canonical: docs/design/COMBAT_ABILITIES.md. Production untouched.

October 4 ability foundation: versioned snapshots, per-technique cooldown/charges and ordered effects/conditions implemented. Precision Shot/Arc Bolt cooldown 2; Field Care 3; other gear has individual one-use limits. No two-gear-active cap. New battles have no twenty-round defeat; bounded auto pauses. Old saved battles retain legacy rules. Dev only. Canonical: docs/design/COMBAT_ABILITIES.md. Next: status ownership/expiry, Barrier/Mark, displacement and bounded reactions, then summons/forms/loadouts and all twelve starters.

Follow-up: boundary-aware auto approach/pathfinding for Locked Tool Shed and former-command prison encounter. Existing wall stalls previously ended in forced timeout defeats; now they pause without a fabricated outcome.

October 4 Job design draft (NOT IMPLEMENTED): agreed starting roster is Fighter,
Barbarian, Rogue, Ranger, Mage, Cleric, Monk, Bard, Druid, Engineer, Summoner and
Captor; replace Paladin proposal with Summoner and remove Medic/proficiency
selection from future character creation. Five regular character slots; no
two-gear-active limit. All equipped gear abilities remain accessible. Champion
kits deferred; popularity rank must not dictate combat power. Draft proposes
96 skills and matching starter equipment, bounded summon/device/form mechanics,
distinct restraint versus Subdue, pit types and encounter-specific pressure
instead of twenty-round loss. Canonical: docs/design/STARTING_JOBS_AND_SKILLS_V1.md.
Next: review individual skills and budgets, then implement dependencies and
test all twelve starters before publishing them together. Starting role roster unchanged; the foundation above is live in new dev battles.

October 4 chair spacing: implemented Table spacing for supported seats, 60% tuck
through 60% outward gap, retaining table/side and saving the preference per seat.
Tight prop picking and post-save inspector editing fixed. 182 frontend tests,
25 backend tests, build and browser spacing/save checks pass. Dev only;
canonical: docs/design/BASE_CONSTRUCTION.md.

Pending: full active-map audit using the calibrated construction/prop toolkit.
Review all locations and variations for prop scale, placement, clutter,
perspective, wall connections, objectives and traversable routes. Reuse shared
assets and geometry, with visual and gameplay review for each layout.
Automatic base-to-map export remains separate future work.

October 4 prop audit: 142 construction props now use calibrated, centered visible
art sizes instead of one generic PNG box. Placement-only boxes/toggle, red invalid
preview, Standard size for old footprints, full half-cell positioning, and 24 new
overhead furniture/training sprites installed. Eight chairs/three stools/bench
use existing table docking; six training images replaced with overhead versions.
Character/combat collision unchanged. 181 frontend tests, 24 backend tests, build
and isolated browser checks pass. Production untouched. Canonical: BASE_CONSTRUCTION
and docs/art/CONSTRUCTION_PROP_SIZE_AUDIT.md. Further irregular-silhouette collision
and additional style refinements remain deferred.

October 4 furniture placement: props can share cells when visible bounds fit;
unrelated silhouette overlaps are blocked on preview/save, untouched older
layouts preserved. Supported seats dock beside tables with S snapping, permit
a small tuck, and render behind the tabletop. 178 frontend/18 backend tests,
build and isolated browser docking/save/order checks pass. Additional pairing
rules and pixel-perfect collision deferred. Dev only; see
docs/design/BASE_CONSTRUCTION.md.

October 4 wall/prop sharing: visible sprite bounds replace transparent viewport
collision padding; footprint, rotation and offsets match rendering on client and
server. Edge walls leave usable interior space, actual wall crossings remain
blocked. New H walls default top, V walls left, corners center; saved positions
retained. 175 frontend/16 backend tests and build pass. Dev only. Measurement
tool and limitations: docs/design/BASE_CONSTRUCTION.md.

October 4 construction drag QoL: exact rotated snapped-corner commit, rectangular
floor fill and single row/column wall runs with matching native art. Remove [Del]
preserves floors; Shift+Remove previews a floor rectangle preserving objects.
Hover highlights/enlarges the target; all drags commit on inside release only,
outside drops cancel, and undo restores each drag. 173 frontend tests, build and
isolated browser checks pass. No production or real save changes. Repeated prop
placement remains deferred. Canonical: docs/design/BASE_CONSTRUCTION.md.

October 4 construction finishing pass: Delete selects Erase; F/P/W/V switch tools;
wheel zoom stays under the cursor with Shift+wheel scrolling; optional S snapping
persists in the browser. Corners choose connected facing/anchor automatically;
R keeps existing joins and skips invalid orientations. Six nine-original material
kits added to the read-only Wall Kit Lab: rough stone, castle, church, metal,
goblin camp and raider camp. Existing wood/combat art preserved. Future materials
share the same ports/installer. Permanent painted base selection and open/broken
art remain deferred. 168 frontend tests, 18 construction/extraction tests, build
and browser checks pass; room captures inspected. Dev only. See
docs/art/CONSTRUCTION_MATERIAL_KITS.md and docs/design/BASE_CONSTRUCTION.md.

October 3 Aasimar female healer 011?015: trimmed next-row/separator contamination from uncropped originals only; visually verified clean. Tags, standalone tagging data, square/thumb bytes and framing unchanged. Backups retained; image URL versions refreshed. See docs/art/PORTRAIT_FRAMING.md.

October 3 local portrait tagger built in sibling `character-tagger`: pinned WD EVA02-Large v3, own Windows venv/CUDA runtime, immutable raw scores, editable taxonomy/thresholds, SQLite audit history, JSON/CSV exports, resume/remap, local review and structured/phrase search. All 2,072 portraits tagged; assigned race/gender imported. Nine Champion and twelve original samples visually checked; five separate corrections. Eighteen tests, browser QA, CPU/GPU inference and setup launcher passed. Cloud option paused; no API key needed. **Existing game metadata stays unchanged.** Next: reviewed-only integration preserving manual character descriptions; optional VLM comparison for difficult visual attributes. Canonical: docs/art/LOCAL_PORTRAIT_TAGGER.md.

October 3 final male batch consumed: 200 portraits/600 full-thumb-original files installed and verified. Female Troll regular/shaman/chieftain 4×4 sheets installed (16 active each); regular IDs replaced safely, four old IDs retained as compatibility copies excluded from new rolls. Source/pool/metadata/framing backup retained. Fifteen focused tests passed, regular source-crop validation has no problems, eight generated female Troll bosses verified against special pool. Lab now 2,072 active portraits. Appearance metadata tagging remains pending for new male/Troll sheets; stale regular Troll library tags cleared. Existing personal identity/overrides and production unchanged.

October 3 male rollout final generation: ten remaining male sheets (200 portraits) staged with exact prompts under staging-portraits/MALE_BATCH_004.md. No generation targets remain in this plan; batch 004 awaits import. Banshee/Dryad excluded at user request and now female-only for new recruit/combat generation. Approved Aasimar male healer installed (20 portraits/60 files); Lab now 1,844. Fourteen focused race-gender/framing/importer tests passed; new sheets decode at 1254×1254 with 5×4 grid evidence recorded. Female quality review remains deferred. Existing identities and production unchanged.

October 3 male batches 002/003 consumed after user approval: sixteen pools, 320 portraits, 960 full/thumb/original files verified. Exact and alternate-role matching checked; installed montage inspected; Portrait Lab now 1,824 portraits. Existing assignments and production unchanged. Twelve male generation targets and staged Aasimar installation remain. New deferred request: review female pool quality and plan selective fresh generations using approved style; preserve legacy sources and IDs. Canonical: docs/art/MALE_PORTRAIT_ROLLOUT.md.

October 3 male batch 003: eight new sheets staged with exact prompts, 160 portraits (Revenant/Vampire/Ogre/Troll melee, Alien ranged, Undead/Manaforged/Dreamkin magic). All decode at 1254×1254; grid evidence and visual-review concerns recorded. Not imported. Twelve generic generation targets remain plus the approved staged Aasimar installation; batches 002/003 await pool installation. See docs/art/MALE_PORTRAIT_ROLLOUT.md.

October 3 male batch 002: eight beast-race sheets staged with exact prompts and review index, 160 portraits (Bugbear/Lizardfolk/Minotaur/Dragonkin melee; Harpy/Centaur/Faun/Catfolk ranged). File decoding and 5×4 boundary evidence checked; horn clearance, Harpy wing anatomy and Centaur framing remain review concerns. Not imported. Twenty generic generation targets remain, plus the approved staged Aasimar installation. Canonical progress: docs/art/MALE_PORTRAIT_ROLLOUT.md.

October 3 male batch 001 installed after approval: 160 portraits across eight male pools; all 480 full/thumb/original assets verified, matching-role and alternate-role fallback verified, and installed montage reviewed. Portrait Lab lists 1,504 images. Remaining 28 generic male generation targets are unchanged; existing portrait assignments and production saves/assets are untouched.

October 3 male portrait batch 001: eight sheets (Half-Orc/Orc/Hobgoblin melee, Wood Elf/Halfling ranged, Tiefling/High Elf magic, Gnome worker), 160 portraits generated and staged with exact prompts. Halfling redrawn from scratch for stronger adult features. Review/import remains pending; remaining 28 generic male generation targets and staged Aasimar installation are tracked in docs/art/MALE_PORTRAIT_ROLLOUT.md.

October 3 male Goblin portraits: approved ranged and prior approved melee sheets installed in dev, twenty portraits per role with stable IDs, square previews and uncropped originals. Both pools verified against runtime role selection and Portrait Lab. Further male races remain pending.

October 3 safe framing reset: Reset to default previews the appropriate character/shared default and requires Save framing; Cancel performs no write. Browser-tested both paths. One male Goblin ranged 5×4 generation is staged for visual review, with its exact prompt; further male batches remain deferred until review.

October 3 portrait borders follow-up: verified Aasimar healer 013/014/015/019/020 square files contain artwork to their edges and their default circles stay inside bounds. Added file-versioned pool URLs to roster normalization, battle views and Portrait Lab so old padded image caches are replaced. Reapply circle positioning after retained DOM patches so combat updates cannot discard portrait geometry.

October 3 portrait follow-up: restored square full/thumb previews, recovered separate uncropped originals for all 1,080 generic portraits, and added an image-source switch to framing editors. Portrait Lab opens the uncropped image by default. Saved manual frames remember which source they use; automatic square frames stay inside image bounds to avoid black borders. Existing portrait IDs and character assignments remain unchanged.

October 3 portrait framing: implemented per-character circle editor and dev-only Portrait Lab with search/set filters, sixty previews per page and persistent shared image defaults. First automatic audit covers 1,304 portraits; visually inspect uncertain nonhuman faces in the Lab. Manual library corrections survive re-audits; source images and identity order remain unchanged. Updated twenty Aasimar female healer images in place. See docs/art/PORTRAIT_FRAMING.md. Future work: review remaining detector estimates and reimport sources whose heads were already clipped.

October 3 road rollout: Highway Ambush now has four authored road/bank/flank layouts with stolen-supply pull-offs and verified Battle Lab seeds. Existing enemies, objectives and rewards retained. Next road review: Boar-Rider Patrol and The Tithe Convoy; other generic road, tunnel and later facility maps remain pending. See docs/design/AUTHORED_BATTLE_LOCATIONS.md.

October 3 environment variations: all four gardens and all four training yards now use distinct footprint-aware arrangements. Kit reused in farm clearings, well yards, provision/supply sites and full command/redoubt/vanguard camps (36 authored variants across nine settings). Visual dressing only; save layouts, mission rewards and mechanics retained.

October 3 garden clutter follow-up: new overhead garden prop kit installed in reviewed layout 1. Crop edging overlays planting without blocking movement; potting, watering, drying and rest areas now have sized clutter. Training layout 1 gets a small equipment/rest addition. Other variants and interactive fence/gardening mechanics remain deferred.

October 3 environment follow-up: implemented one herb-garden and one training-yard composition (layout 1) with a new overhead terrain-only atlas, coherent multi-cell ground patches, paths, activity areas and edge-offset equipment. Other three variants await visual review; harvesting/training mechanics are unchanged. See docs/art/ENVIRONMENT_DRESSING_V1.md.

October 3 follow-up: rejected supplied gardening kit retired from runtime and source staging; earlier herb props restored. Saved battle art has approved replacement aliases. Proposed next pass: overhead ground vegetation, paths/scuffed training ground, purposeful work/rest clusters and sub-cell visual placement. Review one garden and one training yard before expanding variants.

## October 3: Earlier prop sizing audit (garden import superseded above)

Audited all 138 registered non-modular prop/state sprites across 249 encounters; shared alpha-calibrated presentation and new-object footprint defaults now distinguish small clutter, ordinary furniture and multi-cell objects. New wells/wagons/cages/tents/ballistas use 2x2 defaults; carts and long furniture use two cells. Existing saved occupancy is retained; walls preserve material join calibration. Captive Cart courier moved outside the enlarged logical wagon footprint.

Imported all 32 supplied garden objects as complete proportional silhouettes. Four herb-garden variants now use three/four large planting beds, potting/watering corner, compost and tools with clear aisles. No farming/harvest mechanics added. Archived 34 obsolete replaced runtime PNGs; active artwork, style references and prepared assets retained. Canonical: docs/art/PROP_SIZE_STANDARDS.md, PROP_SIZE_AUDIT.md and PROP_CLEANUP_20261003.json. Map rollout paused for this refinement. Next map work remains convoy/highway/watch; siege operation and additional prop interactions stay proposed.

Validation: 140 distinct backend tests, 37 frontend tests, build, all-location route checks and 249-preview/19,603-reference art coverage pass. Real renderer checks include all four gardens and cart/well 2-column footprints. Imported garden perspective is not pure overhead; replacement art may be considered later if this mismatch remains distracting.

## October 3: Beginner maps and full-camp clutter completed

Seven compact settings each have four named layouts: provision stores, farm paddocks, herb gardens, purse roads, well yards, supply stops and occupied training yards (all prisoner-proof ranks). Existing encounter counts, mission paths and rewards retained. Full command compounds/redoubts/vanguard camps now contain training/archery props, bedding, cooking and supplies, with reserved deployment/door lanes and complete furniture footprints.

New separate 32-sprite prop atlas includes all seven requested beds, reed mat, training equipment, camp supplies, well/herbs/purse and siege states. Camp extraction preserves whole silhouettes and previous assets. Stored ballista is scenery/obstacle; ballista operation and gate-mounted oil hazards remain WIP, as do training interactions and additional dedicated sleeping quarters. The original small Goblin Warcamp map has not been changed. Canonical: docs/design/AUTHORED_BATTLE_LOCATIONS.md and docs/art/CAMP_PROP_PACK.md.

Current coverage: 43 authored, 18 generic encounter IDs. Next: convoy/highway/watch sites, then tunnels and origin-specific story encounters. No production or player data changes.

Validation: 43 focused backend tests, 48 actual-renderer layout checks, frontend build and 249-preview/19,555-reference asset coverage pass. Final camp dressing additionally checked across 400 current map seeds for escape routes.

## October 3: Roadblocks and command camps completed

First reviewed batch implemented for all ranks of Break the Rival Warband and End the Old Command, plus Chieftain's Redoubt and The Ironcap Vanguard. Five settings each have four named layouts; early old-command posts are compact, full camps use nested defenses, and roadblocks have actual gates/flank routes. Approved assets cover this batch; no new art generation. Alarm bell remains scenery. Enemy budgets, rewards and existing battles retained.

39 focused backend tests, 20 actual-renderer layout checks and art coverage of 201 previews/14,615 references pass. Current coverage: 31 authored encounter IDs, 30 generic. Next: compact beginner sites/reclaimed training yards, then convoy/watch routes. Details in docs/design/AUTHORED_BATTLE_LOCATIONS.md; remaining proposals in docs/maps/GENERIC_CONTRACT_LOCATION_REVIEW.md.

## October 3: Remaining generic locations reviewed (proposal)

Reviewed all 29 distinct generic mission titles (44 encounter IDs with prison-rank copies) against runtime premises and faction openings. Proposed map descriptions, existing-asset reuse, specialized art gaps and implementation order are in docs/maps/GENERIC_CONTRACT_LOCATION_REVIEW.md. First recommended batch: road blockade, old-command camp, layered chieftain redoubt and disciplined vanguard camp. No maps changed in this review.

Corrections to earlier proposals: Knight without a Grave belongs on the royal road in its own quest, with origin-specific chapel/crypt maps for reused story encounters; the Missing Governor is a pump component at a guarded salvage yard; prisoner proof is a real reclamation fight. Follow-up authored-map fixes: bridge under the titan-road toll gate and exterior staging for Chapel Patrol.

## October 3: Obsolete map art cleared from dev

Archived 54 obsolete map-art/cache targets outside dev after automatic approval review rejected permanent deletion. Archive uses NTFS compression; exact paths and space measurements are in docs/art/MAP_ART_CLEANUP_20261003.json. Approved sources, current map templates, latest screenshots and required legacy pilot prop source retained. Fixed the legacy building installer to recognize current source versions. All 171 registered runtime assets remain byte-for-byte unchanged; 145-encounter/7,877-reference asset audit passes. No game data or production changes.

## October 3: Mission building rollout completed; remaining maps audited

Approved material kits now serve chapel patrol/gate, five toll/watch contracts, raider cache/outpost, Goblin Armory and Salvage Court encounters. Each building setting has four named layouts; all building locations have four deterministic dressing choices. Armory replaces its two legacy enclosures with four metal-magazine plans. Small twin-building patrols use both buildings. Mission modes, objectives, budgets, rewards and active saved maps are retained. See docs/design/AUTHORED_BATTLE_LOCATIONS.md for exact mapping and limitations.

Remaining work is inventoried in docs/maps/BATTLE_LOCATION_AUDIT.md: fortified command camps/roadblocks; compact beginner sites/training yards; tunnels/crypts/royal halls; convoy and flooded-bell sites; named variants for the separate warcamp/cart/investigation/defense scenarios. These are proposed follow-up batches, not implemented. Roll-only missions do not need a battle map unless their encounter routing changes deliberately.

Validation: 35 focused backend tests, 20 actual-renderer browser layouts and 145 encounter art coverage previews pass (7,877 references). Routes, spawn validity and saved-game isolation are covered. Tactical pacing still needs play feedback.

## October 3: Side T trial reverted

Restored map detail 2's previous side-facing T art and its shared orientation rule. Part 17 is inactive again; part 20 inward corners and all other wall work are retained. Assets reinstalled with a fresh cache version. See docs/art/MODULAR_WALL_GENERATION_GUIDE.md.

## October 3: Polished side T refinement completed

Map detail 2's side-facing interior T now uses user-authored part 17 with calibrated rotation/anchor; this rule applies throughout the polished kit. Part 20 remains the inward-corner source for map detail 3. Other T orientations and perimeter joints retain their original parts. Four furnished browser checks, 32 wall-rendering tests and frontend build pass; reviewed the refreshed enlarged map 2 image. Live seam review remains available in Battle Lab. See docs/art/MODULAR_WALL_GENERATION_GUIDE.md.

## October 3: Authored part 20 for inward polished joins

The user supplied part_20.png and clarified the requested inward corner was in map detail 3, then accepted the shared pass. Replaced the previously adjusted inward-corner artwork with the supplied silhouette at the kit?s common scale, remeasured its horizontal/vertical anchors and fitted its surviving vertical arm. All four mirrored inward-corner facings derive from this source. Side-facing interior Ts also use its corner-shaped arm plus the existing part-19 upright upper continuation, preserving all three connections. These shared rules apply throughout the polished kit, not by mission-specific exceptions. Source overrides are recorded in installed.json and restored on reimport; the original source file is not modified.

Reviewed enlarged map details 2 and 3; four furnished browser renders and asset loading checks pass. Doors, map footprints, collision and logical connection ports remain unchanged. Other material profiles, rough-stone assets, production and saves unchanged. Canonical installer: tools/install_polished_building_kit.py. Artwork still requires normal subjective live review.


## October 3: Apply sample placement rules to every polished-stone map

Used the user?s `staging-terrain/building-toolset-v10-polished/SAMPLE-detail3.png` as a placement/painted-face reference. Polished convex corners (including damaged corners) now use reflected facings instead of quarter-turning horizontal paint into vertical paint: native NE, vertical reflection SE, both reflections SW, horizontal reflection NW. Each facing carries its measured reflected anchor; displayed artwork rotation is separate from the unchanged logical wall rotation. Lower T pieces use a vertical reflection of the native T; crosses preserve the original horizontal/upright painted faces in every orientation.

Concave corners preserve the existing L-shaped collision and arm geometry. Their horizontal and vertical arm faces are reflected locally and remeasured so they meet the outside-facing wall runs around a courtyard; the original joint stays in place. Part 1 horizontal / part 19 upright straight rules remain. The installer exports these variants from existing art and records them in the shared polished geometry profile; renderer selects by piece/orientation and inward-corner offset. There are no map-3-specific placement overrides: every dev map using this polished kit follows the same rules. Door/gate placements, furniture, layouts, interaction edges and movement/sight rules remain unchanged. Rough stone, timber, metal, production and saves unchanged.

Reviewed the four complete furnished layouts, particularly the annex?s inset join and outer corners. Small painted seams remain subject to live review. Browser checks confirm current assets load; rendering tests verify reflected art does not alter connection ports or logical rotation. Canonical implementation: tools/install_polished_building_kit.py and frontend/src/building-joins.js.


## October 2: Original joints restored; part 19 supplies matching upright runs

Disabled the part 17/18 overrides and restored original part 2 corners, part 3 interior Ts and part 15 perimeter Ts. Part 1 remains the horizontal straight wall. The alpha silhouette of part 19 is installed as a dedicated upright straight: its thickness uses the same scale as native vertical arms, its length fits one full wall span, and it is counter-rotated on export so existing whole-building rotation and face-mirroring rules still work. The renderer selects it for vertical straight runs; collision, movement edges, IDs and connection ports are unchanged. This addresses the painted-face mismatch when joining the vertical arms of parts 2, 3, 4, 14 and 15. The original damaged corner's surviving stem is also fitted to its neighboring run without filling the broken area.

Installer records only the active part 19 override; parts 17/18 remain as inactive source files. Reviewed all four furnished layouts and checked asset loading. Wall rendering tests cover all four orientations and verify unchanged face/port rules. Source and screenshots: staging-terrain/building-toolset-v10-polished. Rough stone, timber, metal, production and saves remain unchanged. Painted joins are still subject to live visual review.


## October 2: User-authored polished T and corner replacements

Installed `staging-terrain/building-toolset-v10-polished/part_17.png` for both centered and perimeter T walls, and `part_18.png` for intact corners. Original atlas remains unchanged. The dedicated polished installer reapplies these overrides, records filenames in installed.json, measures the new horizontal/vertical anchors and fits their stems to the adjoining tile. Existing straight-wall boundary offset is preserved; rotations carry calibrated anchors to each corner and T orientation. Native artwork is retained, without assembled corner overlays. Damaged corner, cross, doors and other pieces remain from the existing kit. Asset cache version changed so refreshed clients load the replacement sprites.

Reviewed enlarged browser captures of all four furnished polished buildings; browser loading/native-junction checks pass. Rough stone, timber, metal, production and saves unchanged. Small painted seams remain subject to live visual review.


## October 2: Complete painted polished-stone kit installed

The active dev `limestone` family now uses one 4x4, 16-piece atlas in `staging-terrain/building-toolset-v10-polished`. References: successful timber/metal sheets, the user?s `question/better style.png`, and a visible diagram of sixteen equal square cells. Full walls, half ends, native corner/T/cross/perimeter-T joints, window, breach, matching open/closed doors and gates, pillar, stairs, damaged corner and brace were generated together. Exact prompt, original atlas, crop bounds and in-game screenshots are preserved beside the source.

`tools/install_polished_building_kit.py` extracts complete alpha components at one shared scale. Door/gate states retain fixed jamb anchors; joint arms are calibrated to the tile axes. Only the straight longitudinal stems beyond corner/T joints are fitted to their adjoining tile boundary; wall thickness and the authored joint are retained. The renderer displays native polished junction art directly rather than assembling overlapping straight-wall bands. This is a painted, partly overhead camera matching existing timber/metal, not the rejected flat plan-view style.

Battle Lab ? Building material tests ? **Polished stone building kit** has four furnished layouts: gatehouse, divided hall, breached annex and twin stores (`material-layout-1` through `material-layout-4`). All sixteen parts occur across the layouts. Doors, gates and collision retain normal interactions. Checked actual browser renders at enlarged scale; automated checks cover asset loading, native joints, reproducible layouts, reachable exits and save isolation. Remaining tiny painted seams and subjective style should be reviewed live; this is not a claim of mathematically seamless artwork.

Retired the unused polished plan-view and boxed-trial selectors, geometry, registry entries and their installation/preview tools. Obsolete polished assets/trials are archived outside the project at `E:/Other Games/Fortcamp/fortcamp-art-archive/polished-trials-20261002` after bulk deletion was rejected by automatic approval review. Historical entries below document retired experiments, not current options. The preferred v4 style source remains available as reference. The general material importer delegates polished installation to the current dedicated installer, and the overhead importer handles rough stone only. Rough stone (including its overhead variant), timber, metal, production, credentials and saves are unchanged. Generated media remain local and excluded from Git.


## October 2: Fit candidate stone corners and lengths to actual building boundaries

Restored the template's edge-wall collision convention. Candidate perimeter bands now sit 0.38 tile from cell centre; the generated corner's bend sits at the rotated boundary intersection rather than the tile centre. Concave joins retain their template seating. Full bands span one unit, half bands half a unit; corner arms and perimeter T stems extend 0.88 units to meet the neighbouring boundary/divider ports. Centre T/cross arms reach half-unit ports. Dedicated authored corner/T/cross centres remain intact. Only outer arms use uncapped cropped sections of the matching straight/vertical material from the SAME generation; sections repeat at unchanged pixel scale. No image stretching, foreign wall art, centre patches, synthetic overlapping junction bands or extra posts. Added a separate perimeter-T export. Sprites use shared 1024px canvases and port-based anchors.

Reinstallation now calls tools/fit_boxed_wall_ports.py automatically from tools/install_boxed_wall_trial.py; raw recovery is internal, so reimport does not undo calibration. The frontend's native connection ports use these exact arm lengths. Cache stamp updated. Timber/metal and all old stone profiles remain unchanged. Review screenshots of all four complete buildings show boundary corners and continuous wall runs; subtle texture/stone-course transitions still exist and visual approval is not claimed. Verification: four backend material tests, 31 frontend wall tests including corner-to-band/perimeter-T coincidence, frontend build, and four actual-renderer browser maps with loading assets and no procedural junction connectors. The browser screenshots are in staging-terrain/building-toolset-v9-boxed-reference/in-game-1..4.png. Production unchanged.

## October 2: Replace isolated wall displays with full building comparisons

User rejected the candidate's isolated pieces/rotated sample rows as insufficient. The same dev material now rebuilds the four established furnished building plans: gatehouse, divided hall, breached annex and twin stores, using material-layout-1 through material-layout-4. Former boxed-walls-1..4 seeds remain aliases. Stone shells, partitions and authored junctions use the new generated six-piece art at one shared scale; all room floors and original furniture remain. Doors/gates deliberately use working timber leaves, because no matching door art was generated; broken sections use traversable gaps with common stone-debris props. Removed unsupported pillar/stair/brace sample decorations rather than pretending they came from the new atlas. Native masonry occupies its cell; enemy spawn candidates are recalculated to avoid occupied walls. No old stone wall textures are mixed into the new shell.

Verified four complete-building renders and reviewed screenshots of every layout; four backend material tests pass, including full-plan/floor/furniture preservation, working gate pairs, reachable exits and save/owner isolation. Generated thickness/span inconsistencies remain visible and are not called solved. Screenshots: staging-terrain/building-toolset-v9-boxed-reference/in-game-1..4.png. Production and normal mission defaults unchanged. This supersedes the previous individual-piece Battle Lab layouts.

## October 2: Boxed six-piece kit available in dev Battle Lab

Installed the v9 candidate additively as **Polished stone (Boxed six-piece trial)** in Building material tests. Four seeds: boxed-walls-1 (individual pieces), boxed-walls-2 (connected runs), boxed-walls-3 (90-degree connected runs), boxed-walls-4 (180-degree connected runs). Six source silhouettes are exported on shared 640px canvases at unchanged scale; measured intersection anchors seat them on the grid. Removed broad soft-alpha background halos using silhouette ownership with a two-pixel fringe. No texture stretching or independent piece rescaling. The new native_pieces profile draws generated corner/T/cross directly, without procedural connectors, cap overlays or face mirroring. Old material profiles/default maps remain unchanged.

This is an in-game comparison, not an even or seamless kit: generated full/T/cross spans are 397/443/412px, and half width is 218px. Gates, breaches and other parts were not generated and are not substituted from another kit. The dedicated test maps use ordinary destructible blocking walls, owner-scoped temporary Battle Lab parties and reachable exits. Verification: three material tests (all seven material families), 30 wall-renderer tests, frontend build and all four isolated browser renders with every candidate asset loading and zero procedural connector elements. Connected-run screenshot inspected; joins remain subject to visual review. Rebuild tool: tools/install_boxed_wall_trial.py. Browser check: tools/boxed_wall_browser_qa.mjs. Media excluded from Git; stored locally in structures/building-v9-boxed and staging-terrain/building-toolset-v9-boxed-reference.

## October 2: Explicit boxed generation reference

Added a visible 3x2 diagram of six equal 512px square cells, with labels, dimensioned full/half silhouettes and matching axes. Saved under staging-terrain/building-toolset-v9-boxed-reference/six_equal_cells_reference.png. Generated all six matching parts together using that guide and the painted style reference. The generator still varied bar spans and added soft alpha halos; source/report preserved, not installed or approved. Future generation references must show clear equal cell boundaries and declared piece dimensions, rather than relying on invisible cell positions. Even boxes do not alone prove compatible asset geometry.

## October 2: Complete material kits must be generated together

Generate each material's straight bands and authored junctions in the SAME atlas generation. Do not generate only junctions and later generate their straight walls separately: this omits essential parts and risks different style/stone scale. Minimum matched trial: full horizontal, half horizontal, full vertical, corner, T and cross. Measure before installation; sharing a generation does not guarantee compatible lengths.

Saved six-piece one-generation limestone candidate in staging-terrain/building-toolset-v8-matched-walls, with exact prompt, geometry reference, intact atlas and complete region crops at unchanged scale. Full horizontal/T solid widths 446/448px; cross 397px; half 235px. Not approved or installed; modular fit and generated shadow alpha need correction/review. Prior materials retained.

## October 2: Rejected wall overlap prototype; generated junction candidates pending

The user rejected the v6 procedural corner/T/cross preview. It is not completed or approved art. Generated two dedicated three-piece junction candidates using measured geometry and existing painted wall references; complete silhouettes extracted to staging-terrain/building-toolset-v7-junctions. Both still fail modular geometry checks and remain uninstalled. Pending: correctly matched authored junctions/straight bands, connection review, then additive game integration. Canonical direction: docs/art/MODULAR_WALL_GENERATION_GUIDE.md. No runtime or production changes.

## Rejected October 2: Fixed-unit corner/T/cross assembly prototype

Added an isolated interactive preview of actual corner, T and cross assembly using the v6 painted material. Includes all four quarter turns, four surface variants, optional grid and actual map paving. Exact arm spans, common top width and union-based side-face projection; browser validation/export passes for 16 configurations. Source: tools/build_gridfit_join_preview.py; page/images: staging-terrain/building-toolset-v6-gridfit. Inspected all four comparison images; mortar transitions remain visibly assembled. Existing game materials, combat renderer, saves and production unchanged. Next: user art comparison; guided dedicated junction art remains a valid option; no automatic rollout. Canonical reference: docs/art/MODULAR_WALL_GENERATION_GUIDE.md.

## October 2: Correct wall source strategy - painted style and exact construction units

User rejected the pure-overhead polished style and irregular generated lengths; strict overhead is no longer the priority. Preserve current six material profiles while returning to the existing painted-map style. Generated a measured-layout source trial using the current wall/paving references; rejected its inaccurate half/join/door geometry. Prepared twelve crop-only material parts with exact 256px full / 128px half lengths, common cross-section and compact 48px joints, without long L arms or independent rescaling. Verified dimensions and checked the two-full/two-half paving preview. Source/prompts/report: staging-terrain/building-toolset-v6-gridfit. Canonical rules: docs/art/MODULAR_WALL_GENERATION_GUIDE.md. Remaining: validate style with user, prototype grid-defined connection ports and doors/gates, then test an additive material before changing defaults. Current game art/registry/geometry and production unchanged.

## Completed October 2: Additive overhead stone material tests

Installed both overhead candidates as additional materials (limestone_plan/fieldstone_plan), preserving every existing registry/geometry entry and all old art. Battle Lab now has six material entries and 24 comparable layouts. Separate top-down calibration, gate/door state anchors and no painted-face flips/extra columns; normal interactions, collision, damage and save isolation retained. Additive installer is tools/install_topdown_stone_toolsets.py; canonical controls: docs/design/BATTLE_LAB.md. Verified 132 frontend tests, build, eight targeted backend checks and all 24 material-layout browser checks. Remaining: user visual comparison and deciding whether any mission defaults should change. Production untouched.

## October 2: Generated pure overhead stone trial; integration pending

Created separate polished/rough stone plan-view 4x4 candidates, preserved active packs and wood/metal. Rejected an initial limestone draft with frontal doors; revised doors/gates use narrow overhead leaves. Staging: staging-terrain/building-toolset-v5-topdown contains exact prompts, original sheets, 32 complete alpha-extracted pieces, extraction.json and preview.html. Checked camera and representative extracted corner/door/gate silhouettes. No runtime replacement or gameplay changes. Next: subjective review, separate optional stone profile calibration and actual-map comparison before choosing a default. Canonical reference: docs/art/MODULAR_WALL_GENERATION_GUIDE.md.

## Completed October 2: Limestone face matching and corner seating

Corrected the supplied directional limestone corners' outward-face convention across perimeter bands, Ts and exposed posts. Matching straight bands extend into each existing built-in column; clipped foreground columns hide unequal source arm tips. Rejected a sideways inset after it visibly stepped the joins. No separate strategic pillars or image warping. Reviewed enlarged renders in all four directions and full limestone layouts; 131 frontend tests, build, seven targeted backend checks and enlarged/16-layout browser checks pass. Canonical rules: docs/design/WALL_BOUNDARIES.md and docs/art/MODULAR_WALL_GENERATION_GUIDE.md. Production unchanged; subjective approval pending. Remaining art limitation: legacy damaged limestone corner faces.

## Completed October 2: Revert connector pillars and try user-authored limestone corners

Removed the strategic pillar rule after visual rejection. Limestone corners now use the four supplied directional images with independent measured alignment; earlier face/layer/end-post/T fixes remain. Preserved files from disposable frontend/dist into source assets and a staging backup. Installer keeps/calibrates optional directional sets; rough stone retains prior assembly. Canonical reference: docs/design/WALL_BOUNDARIES.md and docs/art/MODULAR_WALL_GENERATION_GUIDE.md. Validation: 128 frontend tests, build, seven targeted backend tests and all 16 Battle Lab layouts pass. Production untouched; subjective review pending.

## Completed October 2: Foreground end posts

Fixed the exposed stone branch post below the divided-hall gate: cap sprites draw in front of wall bands and mirror to match their attached face at opposite endpoints. Terminal posts follow the same rule, in combat and defense preparation. Canonical rules retained in docs/art/MODULAR_WALL_GENERATION_GUIDE.md and docs/design/WALL_BOUNDARIES.md. Validation: 127 frontend tests, build, seven targeted backend tests and all 16 Battle Lab layouts; browser assertions cover foreground layering and mirrored posts. Also made horizontal bands cover vertical bands at corners and branches, and selected the calibrated dedicated v4 stone T for the left-facing join above the gate. Other orientations retain face-correct assembly. Production untouched.

## Completed October 2: Consistent T/cross branch faces

Matched rotated centered T/cross arms to neighboring divider faces; perimeter Ts keep their inward-facing boundary bar while their stem matches the interior wall. Half-turned centered runs/terminal bands use the same face convention. This addresses the upper T/gate, lower T and cross seams in the latest polished/rough-stone screenshots without altering placement or collision. Validation: 124 frontend tests, build and all 16 material-layout browser checks pass. Canonical reference: docs/design/WALL_BOUNDARIES.md. Production untouched; final visual review remains pending.

## Completed October 2: Corner-consistent wall faces and metal corner joins

Updated stone screenshots exposed opposite perimeter bands facing outward. Boundary-aware texture mirroring now matches the inward-facing corner arms across all building rotations; centered dividers retain their orientation, translated concave arms reverse their face, and breach calibration follows mirroring. Metal corner rims meet at a diagonal seam rather than overlap. No source art regeneration, save migration or gameplay changes. Canonical references: docs/design/WALL_BOUNDARIES.md and docs/art/MODULAR_WALL_GENERATION_GUIDE.md. Validation: 122 frontend tests, build, seven targeted backend boundary/showcase tests, four-material/four-rotation enlarged checks and all 16 Battle Lab layouts pass. Remaining: user visual review and previously documented door camera/stair work. Production untouched.

## Completed October 2: Regenerated stone and neighbor-aware wall columns

Generated new rough/polished stone v4 kits with uncapped connecting bands and separate caps. Metal now uses its post-free middle texture at connected joins, preserving terminal columns at exposed ends. Matching rotated endpoints handles corners/branches, parallel walls, door states and destroyed neighbors; caps are visual only. New stone half ends have explicit half-cell length. Original packs preserved; timber unchanged. Canonical guidance: docs/art/MODULAR_WALL_GENERATION_GUIDE.md and docs/design/WALL_BOUNDARIES.md. Validation: 325 backend tests, 117 frontend tests, build, enlarged/16-layout browser checks and 99-preview art audit pass. Remaining: subjective live approval and stricter overhead door/gate art; stair gameplay remains deferred. Production untouched.

## Completed October 2: Connection geometry from all eight user snips

Replaced unreliable whole corner/T/cross silhouette placement with exact clipped matching straight-wall assembly; preserved painted thickness/proportions, rotation, inward corners and gameplay. Fixed directional short-end attachment and separately calibrated damaged corners without filling their broken center. Enlarged review tool now covers six connection types in all rotations. Canonical reference: docs/design/WALL_BOUNDARIES.md. Validation: 109 frontend tests, build, seven targeted backend tests, four-material enlarged browser checks and all 16 Battle Lab layouts pass. No new art generation or production changes. Remaining: live subjective review, future structural styles and functional stairs.

## Completed October 2: New rough stone and complete material test layouts

Regenerated rough-stone structures as a continuous-masonry v3 kit, preserved legacy packs, and aligned timber breaches by surviving beam ends rather than rubble center. Short supporting pieces retain appropriate scale. Added four distinct Battle Lab layouts per material (16 total), covering all 16 parts across each material's four layouts, with exact piece lists in the toolbar. Source filter: Building material tests. Canonical instructions: docs/design/BATTLE_LAB.md, BUILDING_TEMPLATES.md and WALL_BOUNDARIES.md. Validation: 325 backend tests, 107 frontend tests, build and all 16 layout browser checks pass; 99-preview art audit finds no missing files across 3,465 references. Remaining: subjective review of other material packs and actual stair/floor transitions. Production and saves untouched.

## Completed October 2: Short T stems and forge corner alignment

Fixed in dev: independent corner-axis alignment and matching clipped wall sleeves beneath short corner/T connection ends, including rotation and destruction cleanup. No stretched images, new collision or regenerated art. Added an enlarged four-material comparison tool and browser check. Canonical references: docs/design/WALL_BOUNDARIES.md and BUILDING_TEMPLATES.md. Validation: 106 frontend tests, build, all authored-map browser checks and enlarged four-material previews pass. Production untouched.

## Completed October 2: Wall boundaries and material-specific building kits

Implemented in dev: walkable interior floor beside edge walls/corners, blocked crossing/sight, full-tile centered dividers, real divider-to-shell T joins and boundary-aware gate/pursuit/escape behavior. Generated four complete 16-piece atlases, one per material, with matching walls, doors and gates; installed versioned art and preserved legacy sources/IDs. Canonical references: docs/design/WALL_BOUNDARIES.md and BUILDING_TEMPLATES.md. Validation: 323 backend tests, 103 frontend tests, build/browser checks and 83-encounter art audit pass. Remaining: more material-specific buildings, stair interactions and live balance/visual review. Production untouched.

## Completed October 2: First authored-location pass

Six maps rebuilt around their quests: Locked Tool Shed, Intruders at the Workshop, Bone Collectors, Bone Patrol, Timber Across the Creek and Narrow Bridge Gang. Added reusable enclosure/work-bay/grave-row/river-crossing pieces, two seeded dressing variants, working attackable gates and separate twelve-prop/eight-structure art packs; reused existing terrain. Original generic layouts and assets preserved. Reference: docs/design/AUTHORED_BATTLE_LOCATIONS.md. Validation: 314 backend tests, browser checks of six maps, 65-map art coverage audit and frontend build/tests passed. Remaining: chapel/gatehouse, toll ford/watch dispute, fortified command/blockade, tunnels/armory, submerged bell, cache and reclaimed training yard. Subjective visual approval and map balance follow-up remain open. Production untouched.

## Completed October 2: Battle Lab and prison wagon size

Implemented a dev-only Battle Lab with 73 current mission templates, rank/source/search filters, authored approach/outcome selection, seed controls, roster copies, optional temporary companion and restart/return controls. Tests use ephemeral server/player-scoped sessions without rewards or save changes; production profiles reject access. Captive Cart prison wagon/wreck artwork is doubled with preserved proportions and legacy CSS wheel cleanup. Reference: docs/design/BATTLE_LAB.md. Validation: 309 backend tests, 103 frontend tests, frontend build and desktop/mobile browser checks passed. Remaining: live visual feedback and subsequent scaling/balance review. Production untouched.

## Completed October 2: Remaining active mission props

Added twelve overhead sprites and wired missing dispatch satchel, loose wagon wheel and marked farm chart. Prison wagon now has dedicated intact/wrecked art; prepared traps have armed/spent variants and generic contract walls use the existing overhead stone-wall sprite. Shared state resolver supports older saved encounters without changing gameplay. Current registry: 55 sprites. Audit: 65 encounter setups, 888 references, no missing prop assignments/files. Validation: 301 backend and 103 frontend tests, browser encounter checks and frontend build passed. No production deployment. Remaining: subjective live review, unused legacy-library objects and future props needed by new mission forms.

## Completed October 2: Expanded overhead props installed

Generated three additional twelve-sprite packs and installed 43 selected overhead assets across nature, defenses and containers. The left pine, lower-right bramble and alarm bell now render in the actual Warcamp; bell active/disabled art and human-readable labels match. Stable IDs and old saves remain compatible, gameplay unchanged, original art preserved. Sources/prompts/gallery/screenshots: staging-terrain/overhead-props-v2. Manifest and reproducible import procedure: docs/art/MAP_ASSET_LAYERING.md. Remaining: subjective live review, unmapped specialist props and further camera refinement where tall structures still show frontal surfaces. Validation: 301 backend tests, frontend build and actual-browser asset/state checks passed. Production not deployed.

## Completed October 2: Prop grounding and camera pilot

Live painted props now preserve aspect ratio when enlarged and use short silhouette shadows. Generated and safely extracted a twelve-object overhead study with terrain comparisons and actual Warcamp old/new toggle; existing runtime art remains intact. See docs/art/MAP_ASSET_LAYERING.md and staging-terrain/overhead-props-v1/PROMPT.md. Two catalogue crop tests, production build and browser study/Warcamp checks passed. Remaining: user visual review, steeper overhead palisades and coherent open/closed pairs before expanding or replacing the full prop pack. Do not describe the pilot as a completed art replacement.

## Completed October 2: vendor, hire pricing and social workspaces

Implemented: always-available starter gear for gold; contact-grade hiring fees multiplied by actual contract rank; compact prisoner selection/details with warden readiness and explicit full-cell swaps; portrait-based conversation workspace with eight session exchanges, readable topics, meal quantities/preferences/cooldown and duplicate-click protection. Canonical rules: docs/design/FACTIONS_AND_ROTATING_TRADE.md, MERCENARIES.md, PRISON_RECRUITMENT.md and CHARACTER_RELATIONSHIPS.md. Validation: 301 backend tests, 101 frontend tests, production build and isolated mercenary/social/trade browser checks passed. No production deployment. Remaining: real multiplayer price feedback, more authored conversation/Champion voices, and persistent conversation history if later requested. Current dialogue remains curated, not an LLM service.

Use this file for pending work and GAMEPLAY_VISION.md for standing design rules. Update statuses when implementing a feature; record validation in docs/history/MISSION_REFINEMENT_PHASE.md. Requests here do not authorize paid generation or publication beyond the user's current instructions.

## October 2 ? capture weapons and starter roles

- Implemented in dev: Fighter, Ranger, Mage, Captor, Medic and Engineer starting roles with matching poor-quality gear, one perk and Basic proficiency. Starting roles do not restrict later builds; existing characters keep their gear.
- Implemented: dedicated capture weapons replace Attack with Subdue, including the A hotkey, target menu and previews. The server rejects Attack for these weapons. Repeatable STR/DEX/INT probability checks drive Subdue. Failed attempts do no damage; success leaves a living captive. Manual/automatic/personality combat, previews, boss resistance, control setup and legacy battles use the new rules.
- Implemented: nine capture weapons with rank-gated general/event sources and two rare mission exclusives; existing restraint tools converted. Ordinary blunt/unarmed capture and the glove loophole retired. Blackwatch Cudgel gets its own 5% killing-blow knockout effect.
- Deferred/design recorded: levels, persistent XP, bounded specialization choices and fixed enemy levels; no automatic attribute inflation or player-scaled encounters. Respecialization and dedicated starter/capture art still need a pass.
- Canonical reference: docs/design/CAPTURE_AND_STARTING_ROLES.md. Existing gear art reused; no new image generation or production deployment.


## Current pass — September 30, 2026

- Goblin flames now emit continuously instead of ending together between bursts. Added a 24-second soft wood-fire loop with gentle context fades and Master/Ambient controls. Sources and listening previews are preserved; user listening approval remains pending. See docs/audio/WOOD_FIRE_AMBIENCE.md.

- Goblin fire composition revised after user feedback: large overlapping flames originate below the camera, with only broad tongues rising from the bottom. The effect itself keeps its upper flames wide and bright; smoke/embers emerge from the same unseen blaze. No buildings or random visible campfire bases. Independent timing and scale changes avoid a uniform fire border. Desktop/mobile browser previews, reduced motion and allocation checks passed; live visual review remains open.

- Implemented: accepting a choice-driven contract includes its first decision in the acceptance response. Open immediately, scroll to the top, allow closing, and resume saved choices. Background completions must not replace an open mission screen.
- Implemented: aftermath places readable story beside recovered rewards; expedition checks and loot rolls are expandable.
- Implemented: device-local Master, Music, Interface & Mission Sounds, and Battle Effects volume settings, mute, reset, and sound previews. Existing effects retain their individual mix levels inside those channels. Music playback now rotates approved guild tracks and switches to base/general/goblin themes with fades.
- All four guild tracks approved; three base/combat themes and eight distinct Mureka tracks installed (two each for investigation, defense, undead, and bosses). Originals are preserved; the listening library contains 15 tracks. docs/audio/MUSIC_GENERATION_GUIDE.md records the shared palette and four arrangements. ELEVENLABS_MUSIC_IMAGE_KEY remains server/tool-only.

## Next priorities

- Browser play implemented: Discord OAuth, server picker restricted to user membership and this instance's installed bot, registration gating, server switching and sign-out. Website/Activity share server-scoped saves. Dev/release sessions bind to environment/application/database; cookies and caches are separated. Alpha signing secret is independent. Launchers block conflicting simultaneous bot application IDs; release preparation preserves production credentials rather than copying dev env. Portal redirects and a separate dev Discord application remain manual setup; pinned release unchanged. See docs/WEB_PLAY.md.

- October 1 gear/content pass implemented: 180 items total, 56 additions across all eight slots, 18 new mission-exclusive/capture/event discoveries, and six existing utility upgrades. Low-rank exclusives remain relevant; new long-chain pieces and Starfall relic retain independent drop rates. Equipment techniques are selectable with one shared battle use. Carrying, throwing, breaching, guarding, terrain mobility, elemental protection and survival rules are bounded and shown in gear descriptions. See docs/gameplay/ITEM_CATALOGUE_AUDIT.md and GEAR_LOOT_DESIGN.md. All 180 local icons installed; new sheets append existing assignments.
- Follow-up item design: actual player drop-rate/progression feedback, additional authored branch rewards, party support/healing skills and consumable actions. Do not label unimplemented granted-perk effects as working mechanics. Loadouts/shared armory and deeper gear comparison remain separate UX work.

- October 1 onboarding: catalogue-backed race dropdown with racial effect preview, clearly separated starting Perk and Basic Proficiency, optional background/portrait settings. Exactly one roster character grants +10 Contract Points per pool in free-for-all only; waves remain five points and spent points do not reset when roster size changes. Camp hiring removed from UI and API; keep mission recruitment and author future prisoner recruitment/trader acquisition separately.
- Building functionality audit: see docs/design/BUILDING_FUNCTIONAL_AUDIT.md. Watchpost has no implemented defense effect; Barracks beds do not enforce housing capacity; Campfire staff has no working bonus. Decide whether to retire/defer those construction offers or give them meaningful systems. Do not silently delete placed buildings or existing recruits. Correct stale claims about equipment repair and inventory capacity.
- Loyalty remains partial: combat reads it and low-loyalty endangered allies may panic; missing values default to 100. Recruit starting values, loyalty gains/losses, visible obedience chances and independent commands remain unimplemented. Preserve the proposed curve in COMBAT_DESIGN.md for a dedicated gameplay pass.
- Catalogue art crop repair: 43 items and 41 race emblems recovered from complete source silhouettes, good crops preserved, importer upgraded to prevent nominal-grid cuts, backups/report under data/catalogue-crop-audit. No new artwork generated.

- October 1 friend-trial pass: explicit per-server `/register` and `/unregister` participation; unregister preserves saves. Pinned local releases and separate stable/dev databases and ports; see docs/FRIEND_TRIAL.md. Base workshop/search/management cleanup, immediate contract mutation updates, live phase countdown and deadline refresh. Broader Base artwork and real multiplayer balance/soak testing remain future work.

1. **Music pilot:** 25 tracks are installed with context playlists, three-second crossfades, brief-popup protection, and resuming prior background tracks. All five regional events now have two Mureka tracks each. Seven occasional ambience clips are installed with a separate Ambient Sounds channel; subjective listening refinement remains open. Keep one musical identity across arrangements. Verify actual loop boundaries and perceived loudness, not just file peaks.
2. **Selection responsiveness — first pass implemented October 1:** battle/preparation updates retain map cells, tokens and decoded portraits; interrupted walking continues from its actual displayed position. Rapid movement input keeps only the latest pending destination for the same activation. Hidden Base/Roster panels defer polling redraws; visible roster cards, base cells and resource counters retain their elements. Local software-rendered browser profiling removed the observed 128 ms long task and reduced the maximum sampled frame gap from 217 to 67 ms. Actual Discord/device profiling, large parties/maps and selection performance remain follow-ups; this does not eliminate network latency.
3. **Equipment and inventory UX — first pass implemented:** paged/searchable item stacks, slot/rarity filters, equipped ownership, transfers, injured-character equip/unequip and remembered hide-equipped preference. Granted effects now show bounded utility rules; battle exposes all equipped techniques. Shared armory, loadouts and deeper comparisons remain pending.
4. **Mission-board visual direction — catalogued, deferred:** consider consistent generated icons, restrained backgrounds and event VFX. Preserve readability, navigation, rank grouping, private leads, and reduced-motion behavior; decorative work must not worsen performance.
5. **Aftermath follow-up:** review the new format with real long stories, prisoners, discoveries, and large reward lists. Prefer story and consequence over a wall of mechanical recap; expose checks on demand.

## Gameplay and content pipeline

- Economy/building discussion (not implemented): starter production, Stone replacing Cloth as a general construction resource, expanded E-rank content, public wave/free-for-all allowances, and base expansion. See docs/design/RESOURCE_PROGRESSION_PROPOSAL.md; numerical proposals and tentative buildings require validation.
- Faction trade: gold purchases increasingly varied/rare/faction-specific goods as relationships improve. Visiting merchants can offer rare or merchant-exclusive stock; persist offers and avoid reload rerolls or compulsory frequent checking. Preserve mission-exclusive acquisition rules.
- Food/cooking proposal: simple foraging and passive farm production, hunting/provision missions and trade fallback; optional batch-cooked meals. Defer detailed crop simulation and avoid offline starvation or collection-size upkeep penalties.
- Confirmed starting constraint: player begins SOLO. Withdraw starter-helper proposal; production, basic cooking, construction, recovery and early contracts must work without recruited staff. Workers improve these systems later. See the resource progression draft for proposed idle Camp Work and recovery safeguards.
- Faction diplomacy and trust that open relevant Private Contracts.
- Decision scenes continuing after combat, with route-specific endings.
- Broader authored decision coverage: optional setbacks, mission loss, ordinary fights, exceptional bosses; pure-roll missions remain plentiful.
- Defense preparation and readable objective placement; traps/Engineer constructions develop in stages.
- Adventure floors, transitions, rescue/escort objectives, and scenario-specific maps. Reuse docs/art/BATTLE_MAP_AUTHORING.md and docs/art/MAP_ASSET_LAYERING.md; add props only for meaningful interactions.
- Full stealth/detection and night/sleep approaches; larger squads only after scaling and deployment UI support them.
- Individually authored Champion acquisition chains and signature perk mechanics; maintain uniqueness and lore-relevant discovery.
- Continue perk/race balancing and show only implemented effects. Do not claim the entire perk catalogue is finished.
- Prison foundation already supports capture storage, selling, secured/stockade swaps, and a one-hour stockade budget preserved per prisoner. Recruitment, exchanges, and meaningful warden mechanics remain deferred until resumed explicitly.
- Remaining male portrait pass: deferred. Preserve current female/male generation guides and legacy prompts.

## Development workflow

Use local Git for code, tests, documentation, and build configuration. Keep secrets, player databases, generated art/audio, and build outputs outside the baseline. Asset source folders need their own backups; Git exclusions do not delete files. The origin remote is https://github.com/marioneo1/fortcamp.git; the user authorized public code publication. Generated media and player data are excluded.

## Regional audio follow-up

All ten regional uploads are installed, bringing the listening library to 25 tracks. Seven sparse ambience accents are generated and installed. Review their listening comfort in real play; do not add a continuous bed or more clips until the current mix has been heard. Ambient volume is separate from music and battle feedback.

## Mission Board art proposal and guild ambience

The user approved the board proposal; the first art/layout pass is implemented. docs/design/MISSION_BOARD_UI_PLAN.md preserves the plan and docs/art/MISSION_BOARD_ASSETS.md records extraction and browser verification. Guild chatter is installed now as an eighth ambience clip, restricted to the ordinary Mission Board and governed by the existing Ambient Sounds slider.

Regional visual effects now include actual full-board backgrounds behind public/private cards, alongside the event emblem scene. Motion is bounded and suspended when hidden or outside the board. Further tuning should follow real Discord play rather than adding more layers blindly.

The board backgrounds now use PixiJS Particle Emitter with the generated painted effects pack: layered windblown leaves, sparks that fade/burn out, expanding smoke/mist, ash and magical motes. Shared lazy loading preserves stable asset names. Rain/snow presets are implemented and available in the local effects preview; actual battle weather and skill integrations remain deferred. See docs/art/ENVIRONMENT_VFX_ASSETS.md.

Visual follow-up replaces repeated painted smoke curls with new procedural density textures, large arcane glyphs with deforming viewport currents/glimmers, and the slowly dragged Starfall image with a fast head and tapered trail. More visible particle layers and restrained panel transparency let the atmosphere read across the board. The old emblem-only CSS scene is suppressed; original art assets remain preserved.

Implemented the next visual review: Starfall uses tiny procedural starlight, falling cosmic dust, darker nebula and two deforming gravity trails alongside sparse fast shooting stars. Goblin atmosphere favors smoke, fewer green sparks and three intermittent flame sources. Arcane keeps its flowing currents and restores the two counter-rotating circles on the far right of the banner, separate from the emblem. Original art remains preserved. Effekseer is now integrated for Goblin fire; authored spells/portals/impacts remain future work.

Starfall follow-up: meteor showers use staggered 6-10-meteor clusters, four concurrent flights maximum, varied paths/scales and quiet gaps. Mission Board rank crops use the cleaned full-height row with stable filenames and a cache revision. Goblin fire now has an enabled Effekseer trial replacing the rejected Pixi flames; live Discord visual approval remains pending. See docs/art/EFFEKSEER_FIRE_TRIAL.md.

Effekseer Goblin fire is authored, compiled and browser-tested using the real WASM engine on the shared board canvas. Other regional effects remain Pixi. Allocation caps, reduced-motion freeze and cleanup are implemented; source, provenance, license and rebuild instructions are recorded. Further fire art/tuning should follow the user's live visual review.

## Equipment, loot and burning scene - September 30, 2026

- Implemented: three larger burning sources spread across desktop backgrounds, two on narrow screens. Smoke and sparks use the same source positions as actual Effekseer fire; restart as each effect finishes. Reduced motion, hidden-tab suspension and allocation caps remain. Further visual tuning follows live play.
- Implemented: 28 new items, bringing the catalogue to 108. Ordinary capture weapons, elemental weapons, armor-piercing abilities and five chain-exclusive relic weapons. Gear skills work in manual and auto combat, use explicit STR/DEX/INT scaling and explicit elevation rules, and consume one action once per battle.
- Implemented: Fire, Ice, Lightning, Holy and Void enchantments check matching racial affinities. Existing Burn/Freeze/Radiant affinities map to Fire/Ice/Holy. Burn and Poison weapon procs tick once per activation, expire, do not stack, and cannot be applied by nonlethal attacks. Poison-resistant Deathless/constructs are immune; other status mechanics remain separate backlog work.
- Implemented: Common and Uncommon additions for all five event caches; nine authored mission cache pools mix with ordinary gear. Rarity rolls remain gated by rank, after a separate chance to obtain any loot. Mission-exclusive relics never enter random caches. Five chain-final relic checks require follow-up provenance: 14% success / 22% critical success; failure yields none. No guaranteed relic or automatic pity reward.
- Implemented: 108 generated item icons (three 6x6 sheets) and 42 race emblems (one 7x6 sheet), installed with stable item/race filenames. Item icons appear in equipment and aftermath; race emblems appear in roster racial identity. Original sheets are preserved under staging-ui/equipment-icons-v1. Manifest assignments append rather than reorder; extractor refuses overwrites and preserves aspect ratio. Generated media remains excluded from public Git.
- Implemented: tiered Basic to Master tracks are called **Proficiencies** in roster/training. Distinctive traits remain **Perks**. Saved field/API names remain compatible; existing progress is unchanged.
- Next balancing pass: mission loot across all 118 templates, branch/capture-specific rewards, skill diversity beyond a single equipped action, elemental enemy variety, rare non-weapon active gear and crafting/consumable uses for keepsakes. Do not display unimplemented skills as functional.
- Next UI pass: full shared inventory view and loadouts; existing roster Equipment browser is functional now. Broader combat-status mechanics, stealth, dungeon floors, prisoner recruitment and male portraits retain their previous scope.

See docs/gameplay/GEAR_LOOT_DESIGN.md and docs/art/EQUIPMENT_ICON_PIPELINE.md for the rules and asset workflow.

- October 1 responsiveness follow-up: valid movement clicks now immediately redirect local walking using server-validated routes, without waiting for network replies. Older replies cannot undo newer input; failed moves restore the authoritative position. Tested with 400 ms simulated latency. Continue actual Discord/device review.


## October 1 relationship / combat-effects foundation

Implemented: loyalty-based independent-turn chance, stable personalities (12 tropes / seven shared policies), individual meal tastes, roster conversations and service records, eight factual memories, prepared-meal gifts with six-hour cooldown, Effekseer death splash and magic projectile. docs/INDEX.md and AGENTS.md upkeep rules added. Durable completion notices with reconnect retry; Dev still needs `/fortcamp_setup` in its own channel.

Deferred: deeper debriefs and Champion voices, item/trinket gifts and crafter recipes, relationship events/rivalries, adult SFW family/relationship design, award ceremonies and in-game handbook. See docs/design/CHARACTER_RELATIONSHIPS.md. No free-form conversational AI or retrospective statistics.

## Completed: contract, equipment and map QoL (2026-10-01)

- Click outside the contract dialog to close it without abandoning a saved mission.
- Equipped gear effects; spare item effects visible by default; independently saved Hide gear details setting.
- Viewport-clamped perk/attribute formula help; Service Record moved out of Conversation.
- Fit map camera for combat and preparation; preserve proportions and manual scrolling at larger zooms.
- Hidden unique rewards no longer advertised by name or numerical drop chance unless the briefing discloses them.
- Validation: 226 backend tests, 94 frontend tests, production build; isolated real-browser checks for fit, zoom, gear preferences, tooltips, record placement and outside dismissal. No release/save changes.

### Completed follow-up: equipped effects and victory banner

- Equipped slot effects are permanently visible; spare-card detail preference remains separate.
- Camera buttons share one row with equal widths.
- Centered wide objective-secured banner minimizes after Continue for optional objectives and can be reopened through Finish operation.
- Validation: 94 frontend tests, production build, isolated browser checks of camera layout at three sizes, always-visible equipped effects and victory minimize/reopen. Gameplay rules and release saves unchanged.

### Precise zoom and prison planning (2026-10-01)

Implemented smooth pointer-anchored map wheel zoom, retaining modified-wheel scrolling, camera buttons and middle-click behavior. Proposed prison recruitment design documented in docs/design/PRISON_RECRUITMENT_PROPOSAL.md: warden attention, resistance versus loyalty, individual concerns and allegiance contracts for exceptional captives. Recruitment/warden effects remain pending; no prisoner data altered.

## Completed: first playable prisoner allegiance loop (2026-10-01)

Stable capture terms and recruit profiles; eight initial concerns; shared INT-based warden negotiation; story-backed gold/wood/medicine/item sinks; 24 owner-only tactical allegiance templates; explicit one-time recruit conversion and starting loyalty. B/A/S officers with payments also require proof. Roster prisoner conversations and Private Contracts now connect. See docs/design/PRISON_RECRUITMENT.md for live rules, migration and limitations. Temporary faction politics, deeper authored chains, security incidents and personal loyalty follow-ups remain pending.

### Completed October 1: prisoner UI standardization
- Replaced native browser confirmations with a shared in-game dialog for agreement payments, prisoner sales and contract abandonment.
- Organized prisoner cards into conversation/terms, recruit profile, warden resistance, and separate custody actions. Payment costs and follow-up requirements are explicit; tabs remain selected across refreshes.

### October 1: friend trial.2 release preparation
- Prepare an independent production clone from current tested main, preserving production credentials, database and media; force debug/auth bypass off in release env and launcher.
- Alpha and production still share a Discord application ID: simultaneous local dev is supported; concurrent Discord dev requires separate application credentials.
- Host startup and friend-server installation remain operator steps documented in docs/FRIEND_TRIAL.md.

### Completed October 1: camp, roster and inventory navigation (dev only)
- Base task sections: Settlement, Supplies, Development, Kitchen and Prisoners; facility list/inspector and construction sidebar; explicit staffing controls alongside drag/drop.
- Prisoners have their own Base workspace with Roster shortcut, search and secure/stockade filters. Collections are a separate Roster view.
- Party Inventory separates manuals/materials from wearable equipment and allows confirmed quantity sales of unequipped copies; server prevents equipped/duplicate/missing sales and publishes resale quotes.
- See docs/design/CAMP_INTERFACE.md. Existing production trial.2 is unchanged; further sale-price tuning, buyback and material use remain future work.
## Mercenary and early pacing pass — October 2, 2026

Implemented in alpha/dev: four persistent player-specific mercenary contacts; private-contract hiring after assigning an own crew member; multiple hires/bodyguards, rank-scaled fees, −1 check penalty per hire (maximum −4), shared betrayal encounter with occasional loyal holdout, trust discounts and permanent recruitment. Original contracts resume after surviving turncoats. Low-frequency outdoor corpse/friendly/hostile encounters, a central notice, hostile victory gating, and removal of dead contacts are implemented. Missing contacts refill on opening the hiring board. Starter perk kits and quieter natural regional events are included. See docs/design/MERCENARIES.md for numbers and validation.

Follow-ups: real multiplayer balance/soak testing; broader racial/named mercenary content; full pre-contract injury/consumable carryover into adventure encounters; dedicated worn starter-gear art if useful. Permanent companions remain the better long-term option. No release deployment in this pass.

## October 2 production workflow

Implemented fixed sibling `fortcamp-dev` and `fortcamp-prod` folders, a one-step `update_prod_windows.bat`, production-only launch guards, credential-preserving updates with database backups and failed-build rollback. `fortcamp-release-data` remains the production store for every installed server; registrations persist. Separate Discord dev application and actual multiplayer soak testing remain follow-ups. See docs/FRIEND_TRIAL.md.


### October 2: ambush opening and goblin boss pacing ? implemented in dev
- Successful scouting: every initial enemy sleeps for three rounds; first attack against any enemy wakes all, even on a miss. Positioning remains safe. Status hover shows the shared rule and rounds remaining.
- Authored, roster-independent Goblin Warcamp chief and escort stats; stronger B-rank Redoubt commander. Existing saved battles retain their old values.
- Follow-up implemented below: quiet automatic opening positioning and generated-contract rank budgets. Coordinated formations and live friend-server balance review remain pending.
- Superseded by the following pass: the Story milestone label and five personal faction consequences are now implemented. These flags still do not alter server events.


## October 2: combat tools, authored branches and rotating faction trade ? dev

- Implemented fixed E?S enemy budgets for generated contract battles, preserving special rookie fights and authored Warcamp/Redoubt stats. No player-roster scaling. C+ enemies add restrained status threats; auto-battle positions quietly during ambush preparation.
- Implemented selectable ally healing/cleansing/Guard techniques, one shared technique use per character, three shared consumable uses per battle, three owned supplies and immediate durable inventory spending with stale-state rejection. Auto does not spend consumables. Status activation stamps prevent polling/repositioning from repeating effects; condition rules and boss control recovery are documented.
- Implemented nine relationship-gated private faction agreements plus five earned finale consequences. A contact request immediately opens the planner. Private ownership, rank gates, active-copy deduplication and completed-job protection are authoritative.
- Implemented four ordinary safe/risky investigation graphs and three beginner combat handovers. Winning a fight can return to an optional evidence choice; failed optional checks preserve victory, and final rewards/records/notices are issued only once at handover.
- Implemented one rotating faction trader per camp, 48-hour saved visits and stock, relationship discounts, permanent basic/treatment supplies, and the separate player-specific roaming merchant. Adding additional factions remains a later content pass.
- Implemented fourteen mission-exclusive agreement keepsakes with distinct support/defensive actions and independent drop rates. Existing loot exclusivity and low-rank discoveries remain. Initial icons reuse installed art; unique art is deferred rather than blocking play.
- Renamed aftermath World outcome to Story milestone. Five existing flags now unlock personal faction work, not server-wide event changes.
- Validation: 280 backend tests, 100 frontend tests, frontend production build; isolated actual-browser Trade and battle supply checks, responsive widths 1440/800/430, immediate planner opening, correct item command. Preview files are local only; tools never access game databases. Production was not deployed and player data was not wiped.
- Remaining: multiplayer balance/soak testing, more factions and merchant goods, more authored branches/long arcs and lore-based Champion acquisition, more explicit sources for the full status catalogue, formation AI, dungeon floors/stealth, adventure injury/supply carryover, and optional dedicated keepsake art. Existing relationship/portrait/handbook backlog remains.

Canonical references: docs/gameplay/COMBAT_TOOLS_AND_PACING.md and docs/design/FACTIONS_AND_ROTATING_TRADE.md. Local UI fixture: tools/build_faction_combat_preview.py; run with the existing tools/serve_board_preview.mjs and tools/faction_combat_browser_qa.mjs. These are developer QA tools, not new game launchers.


## October 2: unified launcher cleanup

Implemented one authenticated dev launcher for both website and Discord Activity, preserving debug tools and dev saves. Removed the duplicate Discord shortcut and obsolete title-based stop shortcut; Ctrl+C stops the owned process group. Release checkout filtering removes dev-only shortcuts without changing pinned production source, credentials, builds or saves, and persists in future release builds. Existing production received launcher filtering only, with no gameplay deployment or restart. README, WINDOWS_TOOLS, browser play and friend trial instructions updated. Validation: ten run-profile/release tests, including a real temporary Git checkout proving filtering preserves HEAD, source, generated runtime files and clean production status. Separate Discord application credentials remain necessary for concurrent authenticated dev/prod bots.
# October 2 follow-up — authored building plans (dev)

Implemented door-aware pursuit and panic escape; one-third lantern artwork; perimeter wall/door/broken-wall edge alignment; three workshop plans, two mirrored shed plans, two connected-house armory plans and two bridge positions with wood/stone decking. Preserved original map snapshots and separate terrain/prop packs. Rules and validation: docs/design/AUTHORED_BATTLE_LOCATIONS.md. Chapel/bell art is prepared; chapel/bell maps, further fortified/tunnel/training layouts and balance playtesting remain pending. Production unchanged.
# October 2 — visible wall alignment and Battle Lab layout presets

Fixed global CSS overriding perimeter offsets; browser QA now checks actual sprite placement. Battle Lab has named layouts and verified seeds per selected encounter, retains launched choices and shows the template in the battle toolbar. Custom seeds still work.

Proposed, awaiting user direction: replace overlapping corpse/unconscious tokens on a tile with one small body marker and a count badge. Clicking opens a per-body name/state/action list; living occupants stay prominent. Do not confuse this proposal with implemented rendering.
# October 2 — coordinated building parts and independent building plans

Implemented four distinct tool-shed and four workshop buildings, separate from map placement; union footprints, shared-wall removal, inward corners, anchor/quarter-turn transforms and spawn/furniture transforms. New 40-piece structural library supplies matching walls/corners/breaches/door/gate pairs across four families; workshop mixed stone art replaced. Battle Lab lists all eight plans with verified seeds. Canonical docs: docs/design/BUILDING_TEMPLATES.md. Stairs and castle/prison pieces are prepared assets; stair gameplay, further location/map variation and friend-server balance review remain pending. Earlier flipped layouts preserved in snapshots. Dev only.


## October 3: production update packaging

Release updates now include shared portrait framing defaults alongside portrait assets, exclude the obsolete macOS/Linux dev shortcut, and require clean tracked source while leaving unrelated untracked notes alone. Production launch continues to force debug and authentication bypass off; production credentials, player saves and uploads stay separate. The standalone portrait tagging tool remains separate from game runtime metadata.

Validation: 142 frontend checks passed. Full backend run passed 355/356; the remaining special-Goblin portrait test depended on an optional uninstalled male art pool. Isolated that test with both special pools supplied explicitly; production fallback behavior remains unchanged.


## October 3: bush concealment and roadside ambushes

Implemented persistent first sightings for enemies in walkable bush cover. Spot within two tiles with clear sight, or reveal on leaving cover/attacking; bodies are visible. Server views omit unseen units, initiative, targets and animations; direct targeting is rejected. Provisional movement pauses on discovery without spending the main action. Auto/independent party AI uses spotted enemies and searches brush. Two Highway Ambush presets put two escorts in brush with waiting AI; other two presets and rank budgets stay intact. No new art or dependencies. Production remains unchanged. Full stealth, friendly concealment and re-hiding remain deferred. Canonical: docs/design/BUSH_CONCEALMENT.md.


## Bush ambush refinement

Supersedes the two-tile proximity reveal: nearby enemies remain concealed until attacking, leaving cover or physical contact with their occupied cell. Names remain absent from initiative. Authored road kill zones, actual reachable attacks, isolated/wounded target preference and a shared spring signal govern ambushers. Two waiting activations maximum, then normal pursuit; hidden last survivors pursue immediately. An unfinished-fight hint covers the case with no visible targets. No extra damage or free attacks. Fatigue is a separate pacing proposal, not implemented. See docs/design/BUSH_CONCEALMENT.md and docs/design/FATIGUE_PACING_PROPOSAL.md.


## October 3: stamina recovery and reward pacing review

Proposal only: retain the user's 200-point recovery per 30-minute pool as the initial candidate so borrowed S-rank stamina can recover in approximately one pool. Recovery is elapsed-time based, not a reset refill; late deployments cannot guarantee full points at the next boundary. Current ordinary E?B reward scaling does not justify the earlier B20 suggestion on generic payouts alone. Keep B10 as the initial candidate and review whole-party cost, risk, rarity, unique effects and mission-specific rewards before increasing it. Optional healer/exploration/personal-contract recovery unlocks and modest additive improvements are documented, not implemented. Canonical: docs/design/FATIGUE_PACING_PROPOSAL.md. Validation: compared backend/content.py scaling and backend/services.py pool timing; calculated expected independent loot rolls and recovery durations. No runtime, save, drop-table or production changes.


## October 4: expedition stamina (dev)

Implemented 100 maximum stamina, 100 recovery per 30 minutes, E1/D3/C5/B10/A50/S100 deployment costs, and borrowing from at least 1 whole point. Bodyguards and mercenaries pay; saved hiring contacts retain debt. Recovery is computed from timestamps, including offline, without per-character timers or recovery writes. Reservation, base work, Battle Lab and forced debug completion do not spend points; scene/battle transitions within a contract do not recharge. Existing saves start full. Assignment and roster/hiring UI show points, recovery times and borrowing; suggestions omit tired candidates and eligibility returns without reopening the planner. Capacity/recovery quest upgrades remain deferred. Production and live player saves were not touched. Canonical: docs/gameplay/STAMINA.md.

Validation: nine stamina backend tests plus mercenary/private-contract regressions (27 total) passed; 144 frontend checks and build passed. Isolated browser QA passed candidate filtering, suggestions, recovery boundary and desktop/mobile readout sizing. Another 38 backend checks covering stamina, economy, solo onboarding, Battle Lab save isolation and notifications passed. Python compilation and diff whitespace checks passed.


## October 4: square roster and prisoner portrait containers

Fixed rectangular prisoner list/detail and roster Conversation header frames, plus the Conversation companion card at desktop/tablet/mobile sizes. Portrait flex items cannot shrink under long names. The existing framing renderer now receives square containers so image proportions remain intact; original images, square thumbnails, tags and personal framing are untouched. Dev only. Validation: isolated browser measurements at 1440/800/430px verified five affected contexts remain square and a non-square source retains its original aspect ratio; all 144 frontend checks and production build passed.


## October 4: player base construction foundation (dev)

Implemented Base ? Settlement ? Floors, props & walls: searchable installed terrain/prop catalogue, drag floor painting, adjustable/multi-cell/rotatable props, center/edge-snapped wall arms with corners/T/cross/half/gates, automatic exposed posts, broken/open placeholders, selection/moving, undo/redo, zoom, saved layout display and JSON layout export. Authenticated player/server ownership, server validation and revision/CAS conflicts protect persistence. Existing facilities and economy stay functional; decoration is currently free and grants no loot, capacity or defense. Generic geometry/render modules are reusable for a later dev map editor; import, combat adapters, costs/unlocks, functional camp gates/raids and painted wall art remain deferred. Canonical: docs/design/BASE_CONSTRUCTION.md. Validation: 25 backend construction/economy/onboarding checks, all 148 frontend checks, actual browser placement/joins/undo/save/reopen and 1440/800/430px bounds, visually inspected desktop capture, production build. Production and real player saves unchanged by validation.


## October 4: construction interaction and wall asset refinement (dev)

Implemented drag previews with drop-to-commit and outside/Escape/focus-loss
cancellation, reliable R outside text entry, arrow-key prop offsets (Shift fine)
and directional wall anchors, Home centering, full-cell corner arms, and named
horizontal/vertical/post/corner/T/cross/gate assets. Opposite facings have their
own IDs for later painted artwork. Post choice is part of the asset; the separate
post dropdown and half-arm pieces are removed from the library. Legacy saved
walls retain their geometry and can be replaced explicitly. Construction preview
updates use a separate SVG layer, animation-frame coalescing and unchanged-preview
skips; selected-object nudges replace only that SVG, avoiding whole-map rebuilds.
Art generation and functional construction economy/collision remain deferred.
Canonical: docs/design/BASE_CONSTRUCTION.md. Validation: 26 backend regressions,
151 frontend checks, build, actual browser drag/cancel/hotkey/move/undo/save flows,
1440/800/430px bounds, stable scene during 80 pointer updates, stable ground during
selected prop adjustment, and visually reviewed capture. Dev only; no real save
or production changes.


## October 4: simplify player construction wall kit (dev)

Removed T and + junctions from the construction palette and wall-asset selector;
half walls were already absent. Saved junctions retain render/save compatibility
through separate legacy definitions, with rotation disabled. Future agreed kit:
24 selectable variants / 9 generated originals per material, with permitted
mirrors and separately generated horizontal/vertical art. Full-cell corners
remain. Rectangle fill and Remove / Remove floors, mirrored artwork and limiting
straight-wall rotation to its orientation family remain pending. Canonical:
docs/design/BASE_CONSTRUCTION.md. Production and player saves untouched.

Validation: 9 backend construction checks (including old/native retired junction
save/reload and active catalogue filtering), 8 frontend geometry/render checks,
production build and whitespace checks passed.


## October 4: plain-wood atlas and isolated Wall Kit Lab (dev)

Generated one matched 3x3 nine-original timber kit using active painted map art
and an equal-cell diagram; refined the short vertical plain wall in the same
atlas. Extracted relative equal cells, measured alpha/thickness/ports, retained
ends/posts/corner joint while fitting middle grain bands, and installed nine
normalized transparent sprites. All 24 variants use native H/V originals plus
mirrors; bitmap quarter-turns are never used. R stays within straight/gate
orientation families. No half, T or + assets. Added Mission Board debug Wall Kit
Lab with all variants and a connected room, a whole-layout kit dropdown, and no
save writes. Backend access denies production, debug-off and non-admin without
bypass; normal base construction has no trial picker. Combat kits and production
remain untouched. Canonical: docs/art/CONSTRUCTION_PLAIN_WOOD_KIT.md.

Validation: 27 backend construction/economy/onboarding checks, 155 frontend
checks and build; actual browser verifies 44 sample/room walls load nine sprites,
whole-layout switching, mirrored preview, no PUT/save, normal UI separation and
1440/800/430px bounds. Full/100%-zoom room captures visually inspected. Permanent
player wall art, open/broken sprites, rectangle fill/repeated placement and
separate Remove / Remove floors tools remain pending.


## October 4: construction palette and rotation QoL (dev)

Removed opposite-facing duplicate icons/options and collapsed rotated corners
to one Full-length corner entry. Kept direct horizontal/vertical choices and
explicit post positions. R now cycles four orientations H -> V -> opposite H
-> opposite V, selecting separately authored art plus mirrors without rotating
bitmap images. Post positions follow the turn and four turns restore the original.
Added Center [Home] beside Rotate: resets prop offsets or wall anchor to center.
Existing Home key remains. No art, player saves or production changes.


October 4 construction follow-up: 11 wall-library entries cover all 24 orientations;
R changes native H/V artwork and rotates edge anchors; Center [Home] resets position.
World-segment duplicate detection prevents two neighboring cells owning the same
wall span while allowing perpendicular/end connections. Prop collision respects
actual offsets and wall thickness, in preview, selected edits and server saves.
Untouched old conflicts remain saveable. Shared movement helpers distinguish
edge crossing from blocked interior cells; base character walking is still deferred.
Validation: 161 frontend tests, 15 construction backend tests, build and browser
rotation/collision checks pass. Dev only; production and player saves untouched.
See docs/design/BASE_CONSTRUCTION.md for implemented rules and limitations.
# October 4 — Job loadout dependency pass

Implemented: Roster Skills tab; deliberate regular-character Job selection;
twelve initial toolboxes with two supported actives and one passive each; learned
versus equipped IDs; five shared active/passive slots; idle-only validated save;
persisted battle snapshots; grouped unrestricted gear techniques and passive
inspection; basic auto support for deployments/forms. See
[JOB_LOADOUTS.md](docs/design/JOB_LOADOUTS.md).

Next: publish all twelve starting Jobs in creation together with matching poor
equipment; remove Medic/proficiency starter selection while preserving existing
work training. Then implement later unlocks and differentiated builds. Champion
authoring remains deferred. This pass does not implement the proposed 96 skills.

## October 4 ? Combat presentation V2 delivered in dev

- 72 painted square Job icons in hotbar/passives/loadouts; function accents and gear-family fallback.
- Painted forcefields, shield hit/break response and four connected ground families.
- Contact-aligned melee numbers/sounds; collision bounce and bystander recoil; delayed corpse/knockout reveal after collapse.
- Support/form/deployment feedback and old shield/portrait CSS conflict repaired.
- Remaining: full per-skill manual playthrough, mobile density review, unique gear/Champion signatures, custom damage typography.
- Validation: 91 backend / 202 frontend checks, build and isolated browser review. Production untouched.

## October 4 ? Fighter-first correction and UI review

- Implemented: damage/hit overlay above moving tokens; separated overlapping numbers; full-art 64px skill buttons; C/Escape cancel; precise corpse handoff; stronger rebound and body collision sound; Intercept/Counter/Resisted cues.
- All six Fighter skills audited. Break Formation self-collision confirmed; needs an explicit redesign, not a silent rule exception.
- Proposed: tactical workspace A with bottom dock/one inspector (recommended), floating layout B. Interactive local comparison in staging-ui/combat-fighter-review/proposals.html.
- Rejected/pending replacement: stretched AOE imagery and static bubble protection. Fighter protection and ground cast/state/trigger proposals in docs/design/FIGHTER_COMBAT_REVIEW.md.
- Validation: 96 backend / 203 frontend tests, build and browser checks. Subjective audio review pending. No production changes.


### Completed October 5 - Fighter support and impact contact
- Hold Together: self-cast area Fear removal, next-hit -25%, next-attack +25%;
  independent consumption, no stacking, clear targeting/hover text.
- Same-cell edge-wall melee lunge; nearest-cell multi-cell structure contact.
- Corpse/friendly cursor cleanup; four synchronized launch/landing/collision
  sounds; ring reaches radius then fades. Walking animation retained.
- Tested 124 backend / 224 frontend plus build and isolated browser checks.
- Remaining: player listening/visual balance review of this pack; broader Mage
  ground/Barrier redesign and deferred intermittent pathing/rebuild review.


### Completed October 5 - Fighter tuning follow-up
- Hold Together radius 1 / cooldown 4; independent 25% bonuses unchanged.
- Large cooldown counters over faded art; removed Ready badge; 18 px action help.
- Shortened/faded existing Earthbreaker audio tail; wall collision +2 dB.
- 58 related backend tests / 226 frontend tests, build and browser sizing check.
- Player listening review remains; new skill definitions require fresh battles.


### Completed October 5 - Readable statuses and Stun
- Grouped Buffs/Debuffs/Other strip; painted square icons, useful counts,
  status-specific hover/focus and complete grouped unit inspection.
- Map prioritizes two effects plus overflow; no active badges on defeated units.
- Persistent Stun star orbit with contact onset, recovery removal and reduced
  motion. Poison retained. Earthbreaker late audio tail discarded entirely.
- 232 frontend tests, build, audio checks and isolated browser review passed.
- Pending: player quality review; Burn/Freeze/Barrier passes; distinct status
  artwork for conditions currently sharing existing ability icons.

## October 5: painted commands and attached Chain Snare (implemented in dev)

Completed in dev: larger status icons above portraits, wider commands,
matching ranged/magic/pointer/loading/unavailable/hook art, attached Chain Snare
through pull/rebound, endpoint/collision forecasts and removal of Earthbreaker's
accidental magic cast. A new low crater boom layers beneath the landing.
112 related backend tests, 236 frontend tests, build and isolated browser checks
pass. No production or save changes.

Remaining: distinct status-icon art, richer Barrier/Burn/Freeze presentation,
player sound review and optional chain sparks. Effekseer is unnecessary for the
hook's resolved movement. See `docs/design/FIGHTER_COMBAT_REVIEW.md` and
`docs/art/COMBAT_CONTROLS_V2_PROMPT.md` for implementation and asset provenance.

## October 5: cursor, hover and collision follow-up (implemented in dev)

Moved attached status rows just inside the NPC upper-left, wrapping downward.
Enlarged every weapon targeting cursor 50%, aligned them upper-left and made
skill targeting choose bow/magic/hook/support art from its own mechanics.
Widened unit inspection with compact abbreviated stats and responsive columns.
Added collision hit-stop, clearer bystander recoil and complete recovery before
an immediately following enemy attack. No paid generation or production changes.

238 frontend tests, build and isolated full-command browser checks pass.
Canonical details: `docs/design/COMBAT_CONTROLS.md`,
`docs/design/COMBAT_IMPACT.md`, `docs/design/COMBAT_STATUS_PRESENTATION.md`.
Further status artwork and Barrier/ground-effect presentation remain pending.

- Implemented October 5: direct legal provisional repositioning instead of returning through START; same routing for combined approaches, visible effective movement use, original turn budget retained. See COMBAT_CONTROLS.md. Adjacent empty destinations can still exceed the turn range; richer blocked-cell explanations remain deferred.


Implemented October 5: persistent damaging ground counts each committed crossed tile/re-entry, discarded previews free; same-kind overlaps deduplicate per entry. Burn/Thorns numbers show each crossing; recorded movement schedules them at the matching step. See COMBAT_SPACES.md and COMBAT_IMPACT.md.

## October 5: battle input responsiveness (implemented in dev)

Fixed Guard/other actions silently dropped during an in-flight movement request. One committed action follows the latest queued destination; repeated presses cannot affect the next actor. Local movement previews and authoritative server validation remain. 252 frontend tests and build pass; actual network latency remains unmeasured. See docs/design/COMBAT_CONTROLS.md.

## October 5: combined input and flesh slash refinement (implemented in dev)

Movement clicks coalesce locally for 100ms; immediate actions include final position
in one validated command. An already pending scouting check retains one action,
without an extra final-movement round trip. Scouting interruptions cancel queued
actions. Committed requests and enemy/forced-movement playback lock inputs.
Cleaned four flesh effect crops; retained flesh sword sound alone and softened
slash fade. 255 frontend tests, related backend tests and build; live-network
latency and subjective feel still need player testing.

Melee mix follow-up: family/chain/structure swing gain reduced to .12; contacts raised to .55, misses .32. Flesh sword contact remains unlayered. These are playback gains, not a claim of equal measured loudness between clips. 256 frontend tests, 83 backend tests and build pass.

## October 5: persistent move destination and entrance navigation (dev implemented)

Separated chosen destination from pending request work; Guard no longer loses the
position after debounce consumption. Fixed one-point mid-step reversal animation.
Older acknowledgements preserve newer destinations; scouting still interrupts.
Floor clicks can approach the nearest route through entrances, preferring open
entrances at equal walking cost, and stop within the START movement budget.
Closed-door shortcuts get a hand-icon Open Door prompt; no automatic opening.
260 frontend / 94 backend tests, build and isolated delayed-response browser QA
pass. Live player feel still needs testing. Axe/bludgeon sound refinement deferred
at the player's request; this pass makes no audio changes.

## October 5: doorway blocking and navigation spam hardening (dev)

Fixed final-position fields dropped by both API models; actual Lab-handler test
now covers combined movement plus Guard. NPCs do not hide entrance intent, but
remain physical movement blockers. Suppressed unchanged repeated clicks, reused
validated Lab navigation responses and removed duplicate view construction.
Launcher preserves output and fails visibly when an owned child exits.
Past unrecorded server-window closure remains unconfirmed; saved logs now allow
diagnosis if it recurs. Production and player saves unchanged.

Validation for this pass: 263 frontend tests, 99 backend tests (including all Battle Lab catalogue starts, API/persistence and runner isolation tests), and Vite build pass. Existing bundle-size warning remains. No new browser animation benchmark in this pass.

Completed in dev: reduced initial Command Post navigation CPU from 238ms to 32ms
with transient routing lookups. See docs/design/COMBAT_CONTROLS.md for benchmark
and regression coverage. Network latency and any future process-exit diagnosis
remain separate concerns; production unchanged.

Completed in dev: permanent, small Open/Close doorway controls on both sides.
Far clicks approach; adjacent clicks operate without crossing. Existing action
costs and enemy-animation locks retained. General non-door object buttons and
full map/structure audit remain deferred. See docs/design/COMBAT_CONTROLS.md.

Completed in dev: doubled persistent doorway buttons to 44px and spaced the
pair apart. Original Job/build design catalogue remains available in
docs/design/STARTING_JOBS_AND_SKILLS_V1.md; distinguish it from implemented kits.


- Completed October 6: right-click targeting cancel/Move with right-drag preserved; occupied AoE attack cursors; explicit red self/ally forecasts; contact-timed status application badges/hover details. Intermediate status expiration/decay events and synchronized HP HUD remain separate future presentation work.

- Completed October 6: final-path entry-hazard preview (damage, stack attempts, delayed Bleed/Poison wording, hazardous-cell outline); painted open/close doors, retreat markers, pan and interaction cursors; consistent map cursor fallbacks. Delayed zone impacts and reactive survival-passive forecasting remain outside the entry-hazard warning.

- Completed October 6: solo Mage versus one-turn Frozen boss now visibly freezes and thaws even when both changes resolve in a single response; no gameplay duration increase. Removed the unused global recent-freeze visual cache.


October 7 housekeeping: nine obsolete Chrome QA profiles moved out of E-drive root
into ignored dev data/browser-qa/archived-profiles. Future QA profile location is
now documented and required by AGENTS.md. No game saves or production changes.

October 7 ? Cleric rework completed in dev: eight-skill pool, finite healing charges, continuous vulnerable Rest, placed Sanctuary, mixed-damage Smite, Exorcist, cross-shaped Holy Light, and Battle Priest self-only transformations. Matching native-generated icon atlas and browser QA added. See docs/design/CLERIC_REWORK_REVIEW.md.

Deferred: personality-aware Job AI (including Bard performance decisions and Cleric Sanctuary/Rest planning); Bard visual/audio polish requested for a later pass; Cleric dedicated audio/Sanctuary polish and balance playtesting.

October 7 balance refinement completed: Holy Light uses the smallest five-cell cross; Smite lasts the casting turn plus two following turns; Heal restores 40% maximum HP in both builds; Battle Priest reduces all incoming damage by 15%. Barbarian Skullbreaker and Groundbreaker have no cooldown, retaining 2/4 Fury and main-action costs.

October 7 Druid rework completed in dev: eight-skill pool, persistent once-per-
activation quick forms, movement-preserving transitions, global Bleed amplification,
Rat lethal-damage rules, Rejuvenation, Living Armor, shared-health Bramble terrain
and specialization passives. Native art includes circular animal portraits,
ability icons, transformation/restoration effects and reactive vine frames;
five ElevenLabs sounds are installed. See docs/design/DRUID_REWORK_REVIEW.md and
docs/art/DRUID_V1.md. Validation: 363 backend tests, 341 frontend tests, build and
isolated browser QA passed. No production deployment.

Deferred Druid work: personality-aware form selection and wall-placement planning,
encounter balance testing of uncapped global Bleed doubling, and human listening
review of the generated sound pack. Basic healing/form/protection/wall-attack
heuristics are implemented; this is not complete tactical Druid AI.

Druid follow-up: fixed missing-form/missing-metadata equality that renamed other
Jobs' skills to Humanoid Form; fixed ally/self preview selection for Rejuvenation
and Living Armor. Rat direct attacks/forecasts now deal fixed 1 before Barriers;
Bramble lasts four caster turns. Added cross-Job naming and support-casting
regressions and browser command checks. Future AI request recorded: Rat should
normally have lowest target priority unless a guaranteed hit/AoE can punish it.


### October 7 combat inspection / Druid polish completed

- Rat evasion reduced to 90%; form/return targeting explicitly marks SELF.
- Bramble corpses fade next battlefield round and disappear the following round, independent of caster survival.
- Blanket control recovery removed; selective resistances and boss short durations remain. Resistance display consolidated under one buff.
- Right-click ally/enemy draggable inspection with actual armor math and stat explanations implemented. Right-drag pan and empty-map cancel preserved.
- Deferred: personality-aware AI resistance/control planning and Rat low target priority except guaranteed/area threats. No change to Fighter/Barbarian kits or production.

### October 7 follow-up completed

Bounded horizontal hover summary, compact independently scrollable effects and right-click hint implemented. Full descriptions stay in the inspector. Corrupt question-mark separators/multipliers corrected. Poison duration stacks now cause constant 10% max-HP base ticks; cashout, previews, help and tests updated. Burn/Bleed damage stacking unchanged.


## October 7: Unit details readability and effect inspection (implemented)

Replaced the persistent inspector's unequal stats/effect columns with full-width stats above bounded, scrollable effect cards. Audited compact status summaries/clock labels and element-specific enchantment help; individual map badge hover retains full explanations. Added one independent draggable effect inspector, reused on subsequent right-clicks without replacing Unit details. Preserved independent close, stat explanations, scroll position and right-drag map pan.

Validation: 351 frontend tests, build and isolated Chrome checks for fourteen effects, full hover text, singleton replacement, independent drag/close, narrow layout and existing Druid interactions passed. No production changes or live save edits. Deferred: distinct status icon art, map badge crowding and personality-aware AI remain separate work.


### October 7: repeated loading/performance follow-up

Fixed confirmed unnecessary inspector innerHTML replacement on unchanged battle redraws. Browser regression checks retain both inspectors' DOM, refresh changed effects and confirm History sends no API request. Local fixture timings improved; all 351 frontend tests, build and inspector browser checks pass. Dev startup/source mode, cache headers and playback timing remain unchanged. Still open: reproduce/profile the user's repeated live map, History and general element-loading delay; local fixture results do not prove that broader issue resolved.


### October 7: hover-card responsiveness (implemented)

Coalesced map/unit and status-dock hover to one update per frame. Removed per-mousemove status serialization and repeated geometry reads; cached unchanged hover content survives control redraws. Pending hover cancels on exit/rebind, and new presentation status snapshots still refresh. Browser regression checks verify 100 unchanged pointer moves cause zero hover layout reads/content replacements, plus fast-exit cancellation, current effects, scrolling and pinned details. All 353 frontend tests and build pass. Loading, combat playback and production remain unchanged.


### October 7: cross-unit hover and command tiles (implemented)

Added bounded reusable unit-card DOM caching and 90ms intent only for switching inspected units in Move mode. Attack forecasts, keyboard focus and right-click remain immediate; old cards hide during switches and pending display cancels on exit/inspection. Commands now match 88px skill squares, with larger painted icons and consistent states/hotkey labels. 356 frontend tests, build and isolated hover/details browser checks pass. Open playtest item: assess switch-delay feel and shorten/remove the single tuning value if needed. Live runner, saves and production untouched.


### October 7: simplify cursor-following hover (implemented)

Removed stat calculation tooltips/focus targets/native abbreviation titles from the transient unit summary; kept calculations in pinned right-click details. Removed the 90ms switch timer rather than replacing it with 20ms. Hover effects now show at most three compact rows and an overflow count; full scrollable lists remain in Unit details. 356 frontend tests, build and both hover/details browser checks pass, including plain summary stats, pinned stat help, three-unit frame-only switching and fourteen-effects overflow. Live hover smoothness remains a user playtest item; the observed tooltip behavior is fixed without claiming it was the only performance cause.


### October 7: Engineer machinery rework (implemented)

Eight active Job choices; timed construction, active deployment slots, independent
Sentry/Heavy firing cycles, Quick mounting/exit, Overclock's four-shot payoff,
Scuttle/ejection, interrupting friendly-fire mines and delayed Dynamite. Generated
packed turret ready/fire/recoil/wreck art, operator seat portraits, icons/props and
four ElevenLabs clips. Confirmed placement and known-mine path warnings. Old Job
IDs migrate without save reset. Advanced placement/mine/mount AI and personality,
Heavy friendly-fire targeting and subjective sound mix review remain deferred.
See docs/design/ENGINEER_REWORK_REVIEW.md and docs/art/ENGINEER_V1.md. Relevant
backend/UI checks pass; the broad map reachability suite's native process exit
remains a separate unresolved validation limitation. No production changes.

### October 7: hover movement rendering follow-up (implemented)

Replaced left/top movement of transient cards with contained transform positioning. Removed display hiding during next-frame unit switches and made transient cards pointer-transparent, preventing accidental pointer interception. Removed obsolete crossing-grace handlers; actual units/badges remain right-click inspectable. 356 frontend tests, build and hover/details browser checks pass. New isolated positioning benchmark reports 89 layouts for 90 left/top updates versus zero for transforms. Full unit switches still require content layout, and live stutter resolution remains unconfirmed. No added delay or gameplay/loading changes.

### October 7: Engineer/Summoner placement refinement

Implemented: blocking/attackable unfinished machines with preserved HP, destroyed-build cancellation/slot refund; direct combat targeting and remote Scuttle; enemy-clear mine trigger placement and AoE mine detonation; delayed wreck/mine playback and two-round wreck cleanup; draggable remembered placement windows/E keycaps; concise Engineer/Summoner battle copy; eight generated Engineer icons, unfinished props, explosive bolt/cross blast, dedicated ElevenLabs bolt impact.

Pending: confirm live appearance after the Bard SELF-label fix; user sound/art review; broad skill-description audit and future reference menu. Personality-aware AI remains deferred. Validation recorded in the mission history.

October 7 follow-up: Rapid Assembly now has an activation effect, dedicated generated mechanical sound, ready text and visible preparation buff. Dynamite now requires one recovery turn after its explosion; existing fuse and blast remain unchanged. Listening/playtest feedback remains open.

October 7 Dynamite visibility follow-up implemented: portrait hurl, arcing prop toss and landing-to-explosion hazard playback, including solo battles resolving throw and explosion in one response. Validated in an isolated browser; further feel feedback remains open.

October 7 Captor follow-up: fixed Resolve label covering portraits and legacy Attack-to-Subdue remapping; Abduct now uses the styled, draggable Summoner placement panel. Every successful Resolve attack checks capture at zero Resolve, including the threshold hit; captured targets skip further control/pull processing. Existing HP badges retained; expanded HP/Resolve presentation deferred. Validated actual browser input/commands and focused capture regressions.

October 7 release preparation: removed dev-save/upload seeding from new production storage; production working copies exclude QA/test launchers and fixtures. Authorized launch wipe is backed up separately. See docs/design/RELEASE_PREPARATION.md.
