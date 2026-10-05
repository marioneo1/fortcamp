# Combat presentation V2

Implemented in development October 4, 2026. Production is unchanged.
Subsequent user review rejected the AOE/barrier visual direction. See
../design/FIGHTER_COMBAT_REVIEW.md for corrections and proposed replacements.

## Assets and usage

Three new uniform 6 × 4 sheets supply all 72 current Job skills, including
passives. The icons appear in the battle hotbar, passive panel and character
loadout UI. Their small category borders/badges distinguish damage, damage over
time, control, self enhancement, ally support, restoration and deployment.
Hotkeys, names, cooldowns and descriptions remain live UI text.

Gear skills remain unlimited by this presentation pass and use matching visual
families where they lack individual art. Unique equipment skill icons and
Champion kits are later work; these are not 72 unique animated skill effects.

A transparent 4 × 4 effects atlas supplies a forcefield shell, shield hit/break,
poison cloud, burning ground/flame/motes/smoke, binding circle/tether,
sanctuary/restoration, thorn ground/growth and physical/magical hit components.
The face remains visible through the shield. Ground regions clip to real affected
cells and show only their outer boundary; idle animation is restrained.

Source sheets: `staging-ui/combat-presentation-v2/job-icons-01.png` through
`job-icons-03.png`, plus `effects-atlas.png`. Runtime assets:
`frontend/public/assets/combat-presentation-v2/icons/` and `effects/`.
The staging `asset-manifest.json` records every source cell and actual crop box.
[Exact generation prompts](COMBAT_PRESENTATION_V2_PROMPTS.md) preserve the art recipe.

Run `.venv\Scripts\python.exe tools/import_combat_presentation.py` to rebuild
these same named assets from their sheets. It uses actual image dimensions:
1536 × 1024 for icons and 1254 × 1254 for effects. Icons are 128-pixel squares;
effects are 256-pixel squares with original alpha. Sources are never modified.
Generated media follows the existing Git exclusion policy and must accompany a
prepared release through the release builder.

## Contact and defeat

The melee peak, number, sound and target recoil share the 185 ms contact marker.
Moving collisions reach the obstacle at 220 ms after the original contact, then
bounce back by 320 ms. A target blocked immediately uses an 80 ms contact and
220 ms bounce. A struck bystander recoils at collision contact without changing
occupancy. Collision damage still comes from server resolution, not animation.

Defeated units keep a temporary living portrait through impact/travel/recoil,
then collapse over 440 ms before their corpse/unconscious marker appears.
Knockout has a gentler tilt and no blood burst. Defeat audio follows the collapse;
earlier attack sound cues are suppressed to prevent playing it twice.

Guard, cleanse, mark, form change and deployment now emit resolved feedback too.
Cleanse only reports effects actually removed. Zone placement uses its painted
area and cast sound. Existing attacks, statuses, reactions and damage ticks use
the shared hit families. There is no invented HP loss in these cosmetic events.

## Verification and remaining review

91 related backend tests and 202 frontend tests pass; the frontend builds with
its existing large-bundle warning. Added checks cover contact markers, moving
and stationary collisions, collapse ordering, shield break facts, support
feedback, all 72 icon asset paths and irregular ground clipping.

An isolated browser fixture reviewed the four ground families, readable portraits,
forcefield capacity, hotbar icons, both damage labels at collision, a hidden final
corpse during travel and its reveal after collapse. No player saves were used.
This also found/fixed legacy portrait span selectors overriding shield layers.

Reduced motion keeps feedback while omitting particle/zone motion and replacing
collapse with a fade. Custom damage typography is deferred. Full manual play of
every skill, subjective audio/art approval, mobile density review and bespoke
signature effects remain follow-up work; shared family coverage is implemented.
