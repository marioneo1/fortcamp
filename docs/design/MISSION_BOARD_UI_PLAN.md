# Mission Board visual and usability pass ? proposed

Implementation status: the user approved this proposal, and the first board pass is implemented. See ../art/MISSION_BOARD_ASSETS.md for the approved asset pack and preview tools. The proposals below preserve the original plan; broader follow-up remains in the root backlog. Existing mission logic, drops, disclosure rules, locked-rank concealment, assignment mechanics, and party selection remain authoritative.

## Direction

A polished working guild board: painted wood, aged bronze and iron, dark readable surfaces, and controlled magical light. Use the existing painted prop master and combat UI icon/frame art as style references. Character portraits do not determine this UI style. Avoid large photorealistic backdrops, noisy parchment under text, oversized ornaments, and a uniformly glowing interface.

## Usability first

- Clear top-level access to Public Board, Private Contracts, and Your Expeditions, with useful counts and a visible next-refresh time. Resolve navigation across these existing areas as one contract workflow without losing saved mission decisions.
- Search/filter controls stay reachable while browsing long lists. Keep rank, form, availability, and sort; add compact active-filter chips and a clear reset. Preserve focus, scroll, selected filters, and expanded ranks during background refreshes.
- Rank groups stay collapsible. Locked ranks disclose counts only and start collapsed. Use compact headers and a consistent seal, not massive empty decorative boards.
- Each mission card prioritizes name, mission form / disclosed encounter, duration, party size, and a short premise. Separate reward possibilities from party requirements. Do not imply guaranteed drops or reveal secret routes.
- Show a few useful reward previews rather than a wall of equal-weight chips. Keep stack counts visible and offer a clear Inspect / Assign affordance. Full story, requirements and detailed rewards belong in the existing mission planning view.
- Private follow-ups should stand out through ownership, story connection and expiry. Running expeditions need a distinct Resume / Choices / Battle / Claim state.
- Responsive layout: roughly two or three comfortably readable card columns depending on width; one column on narrow screens. Keep text and action targets usable inside Discord rather than relying on browser zoom.

## One initial generated asset sheet

Generate 24 reusable painted icons in a strict 6-column by 4-row atlas, target 1536 x 1024 (256 x 256 nominal cells). Extract using the actual decoded width and height rather than assuming the generator obeys the requested resolution. Each object stays centered inside its own cell, consistent visual scale, with roughly 15% breathing room. No separator lines, captions or generated text. Transparent background; no object or glow may cross a cell boundary. Inspect the atlas before extraction and keep stable filenames/manifests.

- Six rank seals: E, D, C, B, A, S metal treatments; letters rendered by the app, not baked into the art.
- Eight mission-form icons: recovery, rescue, defense, hunt, containment, investigation, infiltration, operation.
- Five regional emblems: Green Warhost, Ashen Procession, Arcane Convergence, Great Beast Tide, Starfall Omen.
- Five utility icons: public contract scroll, private key/seal, reward chest, duration clock, party/group.

Use CSS/code for scalable card frames and actual text. This avoids stretching raster borders, squashing icons, and treating a complete generated screenshot as an interface. Build a real board preview from these assets rather than another standalone illustration.

## Animated visual effects

Generated emblems provide the art; browser animation provides the motion. Begin with one restrained effect in the event header and subtle card hover/focus feedback:

- Green Warhost: occasional ember/dust flecks and a low green edge glow.
- Ashen Procession: slow drifting ash, muted violet-gray light.
- Arcane Convergence: a gentle rune-like orbit or intermittent light pulse.
- Great Beast Tide: drifting leaf silhouettes and warm amber movement.
- Starfall Omen: faint drifting particles and irregular alien light, conveying danger.

Do not animate every card or put moving effects behind body text. Keep effects noninteractive, low contrast, capped in count, paused when hidden and disabled under reduced motion. Sound remains sparse and independently adjustable.

## Delivery and checks

1. Generate and review the single shared icon atlas.
2. Build a representative board preview with ordinary, event, locked-rank, stacked, private-follow-up and active-expedition examples.
3. Integrate readable card hierarchy and stable navigation, preserving interactions during refresh.
4. Add restrained event animation and verify Discord sizing, keyboard focus, narrow layout, locked information, and refresh behavior.
5. Review the actual game before expanding the art pack. New equipment/inventory art and full application-wide redesign remain separate work.

Guild chatter is implemented separately now: one 16-second quiet room-murmur clip, occasional soft table/paper sounds, no intelligible dialogue. It uses the existing sparse ambience scheduler and Ambient Sounds slider, only on the ordinary Mission Board. Regional events and battle contexts take precedence.


## First implemented pass

Generated one transparent 24-icon atlas, extracted stable runtime files, and rebuilt public/private cards with clearer hierarchy and explicit Inspect actions. Added a shared contract navigation bar and an expedition shortcut. Search/filter chips, keyboard focus, collapsed ranks, hidden locked content, independent countdowns, and unchanged DOM during polling are preserved. Event headers use generated emblems, controlled animation, and regional colors. The old full-screen dotted effect is retired.

Validation: 33 frontend tests, production build, and browser checks at 1440 and 390 pixels. Browser checks cover hidden rank details, card/input focus and collapse persistence, navigation, inspection, reduced motion, icon loading, and horizontal overflow. Live Discord responsiveness still needs real-session observation; the local preview does not claim server/network performance was profiled.
