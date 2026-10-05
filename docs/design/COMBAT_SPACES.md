# Combat zones and forms

Implemented engine foundation in dev, October 4, 2026. This is dependency work,
not the release of Druid/Mage/Cleric Jobs. No existing item drops or starter kits
were changed. The twelve Jobs, loadouts and summon/device economy remain pending.

The existing versioned ability resolver accepts two additional ordered effects:
`zone` and `form`. Authored effects use fixed supported IDs, bounded numbers and
ordinary main-action/cooldown costs. There is no arbitrary skill scripting.
Current zone targeting is anchored to a selected conscious enemy/ally. Arbitrary
empty-tile casting and expanded area-target UI are still future work.

## Zones

Zones occupy one tile or a five-tile diamond. Bounds, wall sight, solid terrain,
blocking objects, water and pits clip the placement. Preflight rejects an entirely
invalid area before movement or ability costs commit. Zone creation itself does
not deal an immediate hit. A target-anchored setup has no damage/accuracy roll
or interception unless the same ability includes an actual attack effect.

Supported fixed rules:

| Zone | Affected side | Trigger | Result |
|---|---|---|---|
| Ember Patch | Hostile to owner | Committed entry or activation start | One-turn Burn |
| Binding Circle | Hostile to owner | Committed entry | One-turn Bind attempt; resistance/recovery apply |
| Thornbed | Hostile to owner | Committed entry | 3 damage through the existing damage/Barrier/defeat path |
| Consecrated Ground | Friendly to owner | Activation start | Up to 3 HP restored; Burn prevents healing |

Entry means a real committed route or displacement destination. Provisional
movement, route planning and polling never trigger a zone. Committed walking
routes check crossed cells, not only the final tile; a fatal hit stops the route.
Restraint applied during a committed walk restricts subsequent movement; this
pass does not add interrupt-and-replan movement midway through a nonlethal route.

The same zone kind triggers at most once per affected unit activation across all
owners and entry/start events. Failed resistance attempts also use that allowance.
Overlapping identical zones cannot multiply damage/healing or repeated control
checks. One owner can maintain one zone of each supported kind; recasting replaces
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
