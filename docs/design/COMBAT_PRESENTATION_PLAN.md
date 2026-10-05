# Combat presentation polish plan

Planned October 4, 2026. The first rollout is now implemented in development.
See ../art/COMBAT_PRESENTATION_V2.md for delivered art/timing, validation and limits.
The wider per-skill manual audit and custom typography remain deferred.

## First acceptance scene

Use Battle Lab to test basic melee, Monk Driving Palm, Mage Ember Ground and
Cleric Shelter. Include a free push, solid obstacle collision, person collision,
fully absorbed hit, and a unit crossing a ground effect. Review at normal playing
zoom, with several units and overlapping effects. Expand the rest of the skill
catalogue only after this scene passes visual review.

## Timing and collision

Current scheduling uses a 185 ms melee feedback marker, but the lunge's peak is
at 52% of a 420 ms animation and the target's recoil has its own later peak.
Sharing timestamps alone has not aligned visible contact. Replace separately
tuned peaks with explicit wind-up/contact/recovery markers shared by token
movement, hit flash, sound, numbers, shield response and death.

On collision, travel toward the actual obstruction, visibly compress/recoil and
bounce back a short distance to the final legal position. A struck person recoils
too. Collision damage numbers and sound appear at contact, not at the original
attack or after the whole bounce. Visual overshoot never changes occupancy,
crosses a wall, or moves the struck bystander into another tile. Lethal impact
must finish before the collapse. Reduced motion keeps the impact readable.

## Art direction and asset packs

Use the painted map/prop artwork as visual references: readable silhouettes,
painted materials, restrained warm fantasy accents. Portrait style is not the
reference for effects. Make icons legible at their actual hotbar size.

Generate compact packs with uniform adjacent square cells and a manifest that
maps cells to IDs. Do not bake numbers, letters, cooldowns or labels into images.
Every cell has a planned use; spare cells can provide useful elemental or status
variants. Preserve source sheets. Check extracted alpha edges and sizes.

AI supplies cohesive painted components. Animation is authored from those
components; do not rely on independently generated animation frames staying
perfectly consistent. A genuinely frame-based effect can receive a dedicated
sheet when needed. This is not a requirement to use Effekseer for every effect.

## Ability icons

Create an inventory of the 72 Job skills, their passives and existing gear
abilities before planning atlas cells. Each skill gets a recognizable symbol;
shared visual motifs communicate related skills without giving every skill the
same generic glyph. Passives retain the same art language with a passive badge.

Suggested function accents:

| Function | Accent | Extra cue |
|---|---|---|
| Direct damage | Vermilion | Strike motif |
| Damage over time | Amber | Repeated tick mark |
| Control / displacement | Violet | Bind or directional motif |
| Self enhancement | Gold | Self badge |
| Ally protection / enhancement | Blue | Ally badge |
| Healing / restoration | Green | Restoration motif |
| Summon / device | Teal | Entity badge |

Function appears in the frame or small badge; the illustration can still use
elemental colors. A fire skill should still look fiery. Mixed skills use their
primary function plus a secondary badge. Text/tooltips remain authoritative;
color is not the only indication. Disabled/cooldown states must preserve identity.

## Barriers and zones

Replace the outline with a translucent forcefield enveloping the entire portrait
token and frame. Split rear shell and front rim/highlights to create volume while
keeping the face visible. Include application, idle shimmer, directional impact,
absorption and break/fade. Keep capacity/HP readable. Guard stays visually distinct.

Ground zones need painted textures, animated accents and coherent boundaries:
embers/scorched ground with low flame licks; runic binding with restrained moving
tethers; thorn growth integrated into the floor; sanctuary with flowing warm
light. Clip effects to actual legal cells. Connected cells read as one region,
not a collection of labeled boxes. Separate targeting preview, cast appearance,
idle zone, triggered hit and expiry. Units/terrain/doors remain readable.

## Rollout order

1. Repair contact timing and collision recoil; review slow-motion and normal speed.
2. Build the representative barrier/ground/impact art and a small icon sample in
   planned image packs; integrate and review the complete acceptance scene.
3. Generate the remaining icon packs using the approved art direction.
4. Apply shared presentation families to every current Job and equipment skill,
   including passives, deployment, forms, support, control and reactions.
5. Audit all skills in Battle Lab for targeting, readable cause/effect, audio,
   cleanup, zoom behavior and performance with multiple effects.

Maintain a per-skill presentation checklist. Shared effects are desirable;
signature mechanics need their own recognizable cues. Prevent repeated effects
on menu changes/polls. Keep cosmetic randomness separate from combat resolution.

## Damage typography

Defer a custom damage font/glyph atlas. Start with one properly licensed readable
font and distinguish damage families through color, symbols, weight and animation.
Review hierarchy for ordinary hits, critical hits, DoT ticks, healing and shield
absorption. Generating separate fonts per damage type risks inconsistent digits,
poor small-size readability and unnecessary asset maintenance.

The rollout has generated and integrated icons and shared effect families in dev.
Production deployment is separate. Final aesthetic approval and the wider manual
per-skill audit remain pending user review.
