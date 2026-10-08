# Druid rework — implemented in dev, October 7, 2026

Druid uses the existing Job/loadout catalogue, shared character HP, activation
clock, damage/status pipeline, displacement resolver, terrain obstacles and
combat playback. There is no separate animal unit or disposable animal HP bar.
Start a new Battle Lab battle after restarting dev to test the new snapshots.
The 16-success practice tier exposes all eight choices; five equipped slots
still include passives.

## Skills and progression

| Skill | Unlock | Implemented behavior |
| --- | --- | --- |
| Prowler Form | Starter | Quick, no cooldown. Movement +2; damage dealt +20%, received +20%. A successful hit gives a fresh target 1 global Bleed; otherwise doubles its existing global Bleed. |
| Rejuvenation | Starter | Range 3, self/ally. Heals 10% target maximum HP at each of the next three target turn starts; no instant heal. Cooldown 5. |
| Bramble Wall | Starter | Range 3; every segment must be in reach and clear sight. Confirm a horizontal/vertical three-cell strip on empty legal ground. Lasts four caster turns. Main action, cooldown 5. |
| Bulwark Form | 2 successes | Quick, no cooldown. Movement 1, direct incoming damage -25%, outgoing damage +25%. Landed attacks have 75% chance to push one tile, then normal displacement resistance applies. |
| Living Armor | 5 | Range 3, self/ally. Incoming damage -25%; heals 5% maximum HP at each of three upcoming target turn starts. Protection ends at the end of the final such activation. Cooldown 5. |
| Rat Form | 9 | Quick, no cooldown. Movement +1; ordinary aimed attacks have 10% hit chance. AoE and guaranteed hits bypass this evasion. Any actual HP damage kills, including DoT, hazards and nonlethal damage. Direct attacks deal fixed 1 damage before Barrier absorption. |
| Nature's Persistence | 12 | Wall HP/lash become 50% owner maximum HP/ATK; direct attackers gain 1 Bleed. Armor heals 7% over four target starts and retaliates with 1 Bleed once per direct attack action, rather than per hit. |
| Wild Instinct | 16 | Prowler outgoing bonus +25%; first successful hit per enemy per battle adds one extra Bleed, making 2 on a fresh target. Bulwark outgoing +50%, push chance 85%. Rat hits have 75% chance to apply existing Pestilence (-25% ATK, +25% incoming damage) for two target turns; refreshes without permanent stacking. |

Animal forms persist until changed. Select the current form's button, renamed
**Humanoid Form**, to return. Every change, including returning, consumes the
one-change allowance for that activation. Switching never restores HP. Nature
spells require humanoid form; ordinary weapon techniques retain the existing
animal-form restriction. Animals retain race and ground-traversal rules.

Prowler/Bulwark attack power uses the greater of original weapon attack and INT; Rat uses fixed 1 damage, without
changing maximum HP or inheriting the retired form's flat armor/resistance
bonuses. Prowler uses slash delivery, Bulwark blunt, Rat stabbing/bite delivery;
returning restores the original weapon presentation. Their portraits replace
only battle presentation; saved character identity and portrait stay untouched.

## Movement across a form change

Changing form commits the currently selected walking route, including its
hazards, in the **old** form. Already legal travel remains valid. The new origin
is the committed position; remaining normal movement is the new form's effective
budget minus the movement already committed this activation, floored at zero.
It does not refill the budget or return the actor to its original tile.

For example, Prowler can walk five cells then become Bulwark and attack from
there, with zero walking left. A humanoid who walks one cell then becomes Prowler
has four cells left on an ordinary three-movement base profile. Rat must survive
the committed route before it can change; transformation does not evade damage
from flames it already crossed.

## Living terrain

The three wall segments reference one shared HP pool: 20% caster maximum HP,
or 50% with Persistence. Damage to any segment synchronizes all three. Zero HP
destroys the entire wall; it also withers at the caster's fourth following
activation start or when the caster becomes inactive. It blocks normal walking
without creating a unit, initiative turn, capture target or separate inventory.
It does not block sight. An adjacent enemy can attack it through existing terrain
attack controls; ordinary collision and pathfinding recognize its occupied cells.

When an enemy's committed movement **ends cardinally adjacent**, the wall lashes
once for that movement event, regardless of how many segments are adjacent.
Damage is based on 20% caster ATK, or 50% with Persistence, through existing
damage mitigation. Bind has a 50% application chance before normal resistance
and selective control resistance. Provisional walking, discarded previews, view polling and
repeated checks at the same position do not trigger lashes. A different completed
move can trigger another. This intentionally uses the settled-movement hook,
not every traversed tile. Forced movement and teleports use the same landing hook.

Wall lash extension, contact damage, Bind feedback and sound share a playback
packet. Enemy actions wait for the lash to finish. Transformation and growing
protection also share their visual/sound timing. Art is preloaded when a Druid
enters battle; reduced-motion users get fades rather than stretching vines.

## Damage, balance and migration

Living Armor and Bulwark use normal sequential percentage mitigation, rather
than adding reductions into immunity. Together their direct-damage factor is
0.75 × 0.75 before other ordinary modifiers/rounding. Bulwark alone does not reduce
DoT damage. A fully absorbing Barrier causes no HP loss and therefore does not
kill Rat; actual HP damage bypasses survival/lifeline and nonlethal safeguards.
Strike forecasts explicitly label damaging hits on Rat as lethal.

Global Bleed doubling remains uncapped. With current 5%-max-HP-per-stack Bleed,
20 stacks can be lethal at turn end before mitigation. Wild Instinct adds its
one-time extra stack **after** normal doubling when Bleed already exists:
3 becomes 7 on that first enhanced hit, then 14. This preserves both the global
synergy and a clear one-time opener. Encounter balance testing remains required;
no speculative cap or private Druid-only Bleed status was introduced.

Legacy learned/equipped/order IDs map once: thorns → bramble_wall,
rooted → natures_persistence, sprite → rejuvenation, bark → living_armor.
Practice and choices remain intact; newly available starter skills are learned,
not silently substituted into equipped slots. Existing saved battles retain
their snapshots. No database schema migration is needed.

## AI and validation

Basic auto heuristics return to humanoid for a wounded nearby ally, use
Rejuvenation, apply Living Armor to a nearby threatened ally, choose Prowler or
low-HP Bulwark from humanoid, avoid proactively selecting Rat, and attack an
adjacent hostile wall when no enemy can be attacked. Personality-aware form
planning, deliberate wall placement, choke-point evaluation and sophisticated
Rat tactics remain deferred. These are not claims of complete tactical Druid AI.

Future Rat AI preference: ordinarily lowest target priority, except when enemies
have a guaranteed hit or can reliably catch it with an area attack. This preference
is recorded for the later personality-aware AI pass, not implemented yet.

Behavior tests cover once-per-activation transformations, shared HP, movement
before/after switching, restoration of weapons, spell restrictions, global and
one-time Bleed effects, resistance-aware displacement, Rat accuracy/AoE/death,
barriers, exact regeneration ticks, mitigation, multihit retaliation, shared
wall damage/expiration/owner loss, invalid placement without spending, and
free previews versus committed wall reactions. Frontend tests cover legal
placement/confirmation, icons and contact-linked lash sound/damage. Isolated
browser QA checks portraits, return controls, spell disabling, three segments,
confirmation payloads, lash/growth rendering and transient cleanup.

Final pass: 363 backend checks and all 341 frontend tests passed; Vite build and
isolated browser QA passed. The build retains its existing bundle-size advisory.

### Follow-up naming/targeting regression fix

The original form-button check compared missing `druid_kind` to a missing form,
so ordinary skills were incorrectly presented as Humanoid Form. Presentation now
requires an actual persistent animal form and renames only its matching form
button, including the selected skill. Tests preserve names/descriptions and
original state across all starting Jobs. There is no character/save reset.

Druid support previews now seed ally/self target entries even when a different
skill is initially selected. The shared frontend skill selector also merges
new target IDs, rather than only replacing entries in the old offensive target
list. Rejuvenation/Living Armor self and ally casting are covered in behavioral
tests, with actual browser selection/command checks. Rat direct damage and its
forecasts now remain 1 despite attack bonuses, vulnerabilities or pre-resolved
damage; Barriers may absorb it. Bramble expiry increased from three to four
caster activations. Start a new battle for updated skill snapshot descriptions.

Follow-up validation: 366 backend tests, 342 frontend tests, isolated browser QA
and the Vite build passed.


## October 7 polish

Rat now has 90% evasion: ordinary aimed attacks have 10% contact chance; area and guaranteed attacks bypass it. Fixed 1 direct damage and lethal received HP damage remain. Form and Humanoid return selection visibly outlines the Druid with a SELF label; click the Druid to commit.

Destroyed/expired Bramble remains are nonblocking immediately. They remain fully visible for the destruction round, start fading at the next battlefield round, and are removed on the following round. This battlefield clock works even if the caster is dead and cannot take further activations. Repeated cleanup never restarts the decay timer.

Control recovery immunity is retired; see COMBAT_CONTROLS.md. Rat AI target-priority/personality planning is still deferred.
