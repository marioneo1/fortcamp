# Combat zones and forms

October 6 update: [Mage rework](MAGE_REWORK_REVIEW.md) implements radius-two/three elemental areas, visible armed Freeze/Meteor warnings and painted Scorched ground. Scorched reuses committed-path entry/start triggers: three damage per actual entered tile, repeated entry/forced movement included, dangerous to everyone including allies/caster; overlapping fire-ground zones do not multiply damage. Entry refreshes a bounded separate ground Burn layer rather than generating unlimited stacks by walking. Spell Burn layers remain independent. The foundation description below is historical; regular Jobs and starter selection are now playable.

Implemented engine foundation in dev, October 4, 2026. This is dependency work,
not the release of Druid/Mage/Cleric Jobs. No existing item drops or starter kits
were changed. Subsequent dependency passes implement deployment resources and
regular loadouts; see COMBAT_DEPLOYMENTS.md and JOB_LOADOUTS.md. Full starter
creation/progression remains pending.

The existing versioned ability resolver accepts two additional ordered effects:
`zone` and `form`. Authored effects use fixed supported IDs, bounded numbers and
ordinary main-action/cooldown costs. There is no arbitrary skill scripting.
Pure zone skills can target empty ground with clipped area and combined approach
previews; see COMBAT_CONTROLS.md. Mixed attack/zone skills retain their unit target.

## Zones

Zones occupy one tile or a five-tile diamond. Bounds, wall sight, solid terrain,
blocking objects, water and pits clip the placement. Preflight rejects an entirely
invalid area before movement or ability costs commit. Zone creation itself does
not deal an immediate hit. A target-anchored setup has no damage/accuracy roll
or interception unless the same ability includes an actual attack effect.

Supported fixed rules:

| Zone | Affected side | Trigger | Result |
|---|---|---|---|
| Ember Patch | Hostile to owner | Committed entry or activation start | One-turn Burn; each burned tile entered on the committed route deals 3 damage |
| Binding Circle | Hostile to owner | Committed entry | One-turn Bind attempt; resistance/recovery apply |
| Thornbed | Hostile to owner | Committed entry | 3 damage per thorn tile entered, through the existing damage/Barrier/defeat path |
| Consecrated Ground | Friendly to owner | Activation start | Up to 3 HP restored; Burn prevents healing |

Entry means each crossed cell of a real committed route or displacement. Provisional
movement, route planning and polling never trigger a zone. Committed walking
routes check crossed cells, not only the final tile; a fatal hit stops the route.
Restraint applied during a committed walk restricts subsequent movement; this
pass does not add interrupt-and-replan movement midway through a nonlethal route.

Damaging ground uses `entry_per_cell`: every eligible crossed cell triggers, and
leaving then re-entering a cell counts again. Overlapping zones of the same kind
share one hit per entry across owners. Burning ground and thorns follow this rule.
Other zones retain their per-activation control/healing limits; failed resistance
attempts use that allowance. Activation-start effects remain separate from ground
entry damage. Discarded provisional routes are free: only the final route from
START is checked when the action commits. One owner can maintain one zone of each supported kind; recasting replaces
its area. Clocks and hit stamps persist in battle JSON and survive reloads.

Duration is 1-3 owner activations. A zone expires at the declared owner activation
start, before it affects that owner again. Owner death, unconsciousness, carrying
or extraction prevents further triggers and removes the zone when battle outcomes
are checked. Already-applied short statuses keep their own duration.

Zones use the existing hostility rules, including Charm/Berserk/hostile mercenaries.
Concealed owners and their zone details are filtered from public battle views.
The overlay sits beneath actors, preserves terrain readability and passes clicks
to the tile. Tile hover explains owner, effect and remaining owner activations.
Ability previews include the clipped affected area and rule description.

## Forms

Forms target the caster only. Prowler and Bulwark replace each other; `normal`
returns to the original combat profile. Duration is 1-3 owner activations, expiring
at activation start. Changing form commits movement and uses the main action.

Both use a bounded INT-based melee attack profile (3-12 attack, range one).
Prowler adds one movement; Bulwark adds three armor and 50 displacement resistance
while reducing movement by one (minimum one). These are trial values for the
later Job balance pass, not final progression scaling.

Forms preserve absolute HP/max HP, race, portrait, ground/flight traversal,
identity and equipment ownership. Entering, switching or expiring cannot heal.
Original profile fields are restored exactly, including absent optional fields;
repeated transformations cannot accumulate armor or movement bonuses.
Weapon-specific attack procs/elements/finishers are not copied into the form
basic attack. Permanent/racial traits remain; this is not a race replacement.

Equipment weapon attack techniques are unavailable in a form. Authored character
abilities remain eligible under their ordinary rules; gear support techniques are
not removed. Source ownership is explicit in ability data. Capture tools and
carried bodies/objects prevent transformation. This does not grant Captors a
free lethal form attack.

The battle status tooltip displays form, rules and duration. No portrait art
transformation or new generated assets were needed for this dependency pass.

## Remaining work

Owner-linked summoned units/devices and their shared budgets are next. Then
empty-ground placement/command UI, form-aware AI scoring, all regular loadouts,
Job progression and the twelve starters together. Current AI uses the existing
legal ability paths; it does not yet evaluate full zone/form build strategies.
The existing wall pathfinding stalls remain separately tracked.

Tests cover JSON reload, repeated previews, route entry, owner removal, clipping,
overlap limits, control recovery, invalid casts, no HP refill, exact restoration,
weapon/character ability ownership and no attack damage from a dead caster.
See history for final test counts and browser validation.

Deployment dependency update: owner-linked temporary units and resource/action budgets are now implemented in COMBAT_DEPLOYMENTS.md. Dedicated ground targeting, personality-aware scoring and the full Job rollout remain pending.

October 4 impact update: forced routes check crossed zone cells too. See
COMBAT_IMPACT.md for Ember entry damage, Burn ticks, collisions and presentation.
