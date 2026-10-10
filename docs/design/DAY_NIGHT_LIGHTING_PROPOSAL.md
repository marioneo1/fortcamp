# Day/night lighting

Status: October 9 arrival lighting and visual tester implemented. Presentation
only: no combat modifiers. User approved saved arrival phase plus gentle elapsed
light movement, including time spent away from a quest.

Rollout/consolidation: lighting is active on ordinary combat maps, not just test
maps. Battle Lab's Lighting toolbar button provides presets, scrubber, fast
preview and comparison toggles. There is no separate Lighting Lab launcher in
Developer Tools. Leaving test mode hides its controls, stops fast playback and
restores default shadows/glows plus saved mission arrival lighting.

Regression correction: the single-cell pseudo-art conversion described below
was reverted after the crater report. Unpositioned terrain could anchor the
new absolute art layer to the whole map. Original single-cell background art is
preserved; single-cell palisades receive grading without generated drop shadows,
excluding their HP label from that shadow. Badge box shadows remain removed.
Multi-cell art-only filters are retained. Browser QA checks Warcamp background
art/no extra layer, consolidated toolbar, no separate launcher and ordinary-map
lighting/override reset. 444 frontend tests, 10 backend checks and build pass.

## Arrival and return timing

Warcamp label-shadow correction: its palisades use single-cell background art,
not the multi-cell pseudo-element path. Single-cell painted terrain now also
places artwork on its own pseudo-element, preserving background scale/position
while excluding HP labels from silhouette filters. Painted terrain HP badges
have no separate box shadow. Actual Warcamp browser assertions verify wall art
remains graded, parent filter is absent and label shadow is absent.

Follow-up: rotating/mirroring multi-cell art now counter-transforms the shadow
offset, keeping the cast direction aligned with world sunlight rather than the
sprite's local axes. Painted palisades omit the extra generic contact halo;
eligible outdoor fences retain a softer directional silhouette shadow. Closed
roofed rooms retain contact lighting, since direct sunlight does not enter through
a roof; an open yard can legitimately receive an inward shadow from its sunward
wall and an outward shadow from its opposite wall. Physical wall/roof occlusion
is not simulated. Living mounted boars cast a directional shadow through a
nonrotating artwork wrapper; dismounted circular portraits have no added animal
shadow. This changes no combat rules or portrait grading.

October 9 stability refinement: painted wooden palisades no longer retain the
legacy rectangular tile shadow/inset highlight beneath their sprites. Multi-cell
props such as prison carts apply the scenery filter to their artwork rather than
the entire element, so HP labels do not cast stray shadows. Camera sizing supplies
the final cell size for shadow offsets, avoiding temporary jumps during movement
preview redraws; equivalent cloned views preserve the client clock baseline.
Browser QA covers the actual Promise Proven open training yard, cart label
exclusion and three redraws plus a lighting tick with unchanged shadow offsets.
All 444 frontend tests and the build pass. Inward sun shadows are reasonable in
an open courtyard; roofed rooms use small stationary contact shadows. This is
stylized presentation, not physical roof/window occlusion.

New battles save a server timestamp, arrival minute and phase. The global hour
provides 30-minute day/night windows: day 0-28, dusk 28-30, night 30-58, dawn 58-60.
Once inside a mission, its arrival phase stays fixed. Color and shadow direction
advance using real elapsed seconds, then settle at that phase's end; ordinary
missions never cross from day into dusk or night. Combat turns do not move the sun.
Leaving/rejoining or refreshing does not restart its light. Each server response
provides a fresh time sample; the client uses elapsed monotonic time between
responses rather than trusting the browser's wall clock. Lab cached map responses
refresh their clock separately, preserving the existing presentation cache.

Older saved mission battles derive their initial light from the mission's stable
claimed timestamp. The next saved command retains that metadata. Optional authored
`lighting_phase` (day/dusk/night/dawn) overrides arrival; no title-based guesses.
Auditing story-specific time overrides remains deferred. Full phase progression
for future long/open maps is not enabled.

## Rendering

Terrain and scenery use one shared SVG color matrix; blue night grading retains
sprite alpha and covers oversized tree/prop artwork outside the map rectangle.
There is no rectangle overlay clipping the colored foliage. Day gently warms,
dusk blends through violet into evening blue, night shifts in cool moonlight,
dawn warms toward morning. Portraits, names, status badges and HUD are not graded;
targeting remains functional and readable. No new map art or map rebuild required.

Trees and larger structure props receive a subtle directional sprite silhouette
shadow; changing light direction moves that shadow. This is a stylized drop shadow,
not a 3D height/occlusion simulation. No per-prop authored heights required. Ground
edging, wall connectors and destroyed scenery are excluded from the large-shadow
pass. Lit campfire glow is bounded to sixteen sources; spell fire remains separate.
Selected raised props (crates, barrels, chests, racks, tables, workbenches, anvils,
carts, cages/stocks and boulders) get a shorter directional shadow. Plants, flat
ground dressing and debris do not. Roofed building footprints determine indoor
placement: a prop must fit wholly inside the covered cells. Indoor props use a
soft stationary contact shadow, unaffected by sun direction. Open yards are not
classified from floor texture. Roof flags currently cover tool/chapel/armory/cache
families, road relay house and enclosed workshop rooms; mixed/open compounds
remain outdoors until individual roof regions are authored. Explicit
`lighting_indoor_cells` supports those regions; rotated footprints retain alignment.
Indoor color grading still follows the outdoor phase; actual room lighting remains
a separate deferred pass.

Prison-cart border/shadow fix: old CSS wagon fallback retained a rectangular inset
box shadow under the painted multi-cell sprite. Removed that box shadow and border
for painted wagons. Artwork/crop unchanged; contour shadow now follows sprite alpha.
Updates run every two seconds without rerendering the battle or rebuilding tokens;
hidden pages/maps skip painting and catch up from elapsed time on return.

## Implemented tester

Open Developer Tools > Lighting Lab, choose a Battle Lab map, then use Day, Dusk,
Night or Dawn. Scrub the hour or play a 30-second preview of the full cycle.
The compact panel is draggable; closing it restores the map's saved arrival lighting.
Apply lighting toggles a direct comparison. Campfire glow is optional and bounded
to sixteen detected lit fires. Directional shadows have a comparison toggle.
Settings remain only for this page session. Preview overrides apply only to Battle
Lab; regular missions use their saved arrival phase. This is an initial visual
pass, with native Safari profiling and final art tuning still pending.

Developer Tools consolidates Battle Lab, Portrait Lab, Wall Kit Lab and Lighting
Lab behind existing dev/debug/admin restrictions. Existing lab behavior is retained;
Portrait Lab can still save framing changes. In a test battle, Developer Tools
is also available in the Battle Lab toolbar. Production does not expose it.

Offline visual fixture: `tools/build_lighting_preview.py`; serve with the existing
`tools/serve_board_preview.mjs`, then open
`http://127.0.0.1:8766/staging-ui/lighting-v1/preview.html`.
Real outdoor camp/tool-shed maps, no live saves or backend requests.
Browser QA checks presets, unchanged portrait filters, tinted overflowing art,
changing shadow direction, neutral/shadow toggles, single launcher after rerenders,
close/restore, forced radiant popup and mobile panel width. Backend/frontend timing
checks cover save/reopen, time away, phase boundaries and fresh cached lab clocks.
Desktop screenshots reviewed; native iPhone Safari profiling remains pending.
Interior-aware illumination, moving spell lights and final visual tuning remain
deferred; indoor floors currently receive the same grade as outdoor scenery.
Browser QA also checks indoor shadows remain stationary and painted prison carts
have no box shadow/border. Room-versus-yard/rotation and prop selection checks pass.

Original global clock direction: server-synchronized repeating 60-minute cycle, split into
30-minute day/night windows. Reload/reconnect must restore the current phase;
mission refresh timing remains independent. Dawn/dusk blends occupy the edges of
those windows (roughly 1-2 minutes), not extra periods extending the hour.

Combat map uses DOM terrain/props/tokens with effect layers; the Pixi
renderer is primarily board atmosphere. No ENB or new engine required. Use
selective terrain/prop color adjustments,
and a small number of warm lights at actual campfires/lamps/scorched sources.
Keep UI outside the illumination pass. Portraits stay recognizable, HP/names,
status icons and targeting colors remain readable. Night is cool moonlit blue,
not a black transparent rectangle; dusk is warm with gradual color/intensity change.
Interior lighting needs authored room/building data to prevent outdoor light
washing through every room. Do not promise real 3D cast shadows from this renderer.

Visual rollout: preview one outdoor and one building map, day/dusk/night controls
in Battle Lab, then inspect real spell fire and mobile Safari performance. Keep
lighting sources bounded; avoid a renderer/emitter per tile or arbitrary dynamic
shadows. Use simple composited glows/masks first; profile before heavier rendering.
Existing effects must remain visible above appropriate terrain illumination.

Mission-authored fixed time (night ambush, underground scene, etc.) should override
world lighting explicitly when story accuracy requires it. Proposed UI: tiny sun/
moon indication beside battle heading, optionally time to next phase; no large HUD
panel. No automatic stat, evasion, AI, spawn/reward or mission-pool changes in this
initial visual feature. Those would require separate design work/authorization.

Parked: mission resource reward comparison proposal still awaits UI discussion.
