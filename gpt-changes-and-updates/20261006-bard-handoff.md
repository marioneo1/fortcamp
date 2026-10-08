# Fortcamp Bard / LinkAPI Handoff

Date: 2026-10-06

This handoff covers work performed after the Bard request. It intentionally omits the earlier Mage and general combat work that predated the Bard request.

## Bard implementation covered

- Added/integrated Bard job skills: Jeering Verse, Cue the Strike, Accelerando, Quickening Chorus, Battle Musician, War Anthem, Song of Peace, and Maestro.
- Added Bard song state, performance locking, song switching, lingering/no-linger handling, cooldown interaction, damage modifiers, Song of Peace attack blocking, Jeering Verse targeting, Cue the Strike, and AI support behavior.
- Added Bard status definitions and Bard ability artwork/audio mappings.
- Added performance-space presentation zones and animated floating musical-note treatment.
- Added Bard song audio event mappings (`bard_jeering_verse`, `bard_cue_strike`, `bard_accelerando`, `bard_quickening_chorus`, `bard_war_anthem`, and `bard_song_of_peace`).

Primary implementation files include:

- `backend/combat_bard.py`
- `backend/combat.py`
- `backend/combat_abilities.py`
- `backend/job_loadouts.py`
- `frontend/src/main.js`
- `frontend/src/combat-hotbar.js`
- `frontend/src/combat-spaces-ui.js`
- `frontend/src/combat-painted-effects.css`
- `frontend/src/combat-audio.js`
- `frontend/src/ability-icons.js`
- Bard-related status/audio/icon assets and tests

## Critical Cue the Strike API fix

The browser was correctly sending:

```json
{
  "action": "skill",
  "skill_id": "job:bard:cue_the_strike",
  "ally_id": "...",
  "target_id": "..."
}
```

Both backend Pydantic command schemas omitted `ally_id`:

- `backend/main.py` → `CombatCommandRequest`
- `backend/battle_lab.py` → `CommandRequest`

Pydantic silently ignored the unknown field, so combat received no performer ID and raised `Choose a conscious allied performer`.

Fix applied:

```python
ally_id: str | None = None
```

added to both request models. A regression test verifies both schemas preserve the field. This was an API contract omission, not an intentional frontend/backend disagreement.

## Status icon sizing normalization

The shared status renderer already had separate context standards:

- Map token statuses: `36×36`
- Bottom combat status tray: `48×48`
- Inspection/status detail: `36×36`

Bard-specific CSS had overridden those dimensions to `20px`, `30px`, and `24px`, which caused the inconsistent Bard icon sizes. Those exceptions were removed. The separate passive-readiness map shrink was also removed so map statuses use one consistent size.

The Bard-specific markup class used only for those size overrides was removed as well. No universal 48px resize was made; map and tray retain their distinct layout-appropriate standards.

## Latest Song range and indicator work

The requested Song radius is now **one cell** (Chebyshev distance, including diagonals) for all Songs.

Updated:

- `backend/combat_bard.py` (`SONG_RADIUS = 1`)
- Bard skill effects and descriptions in `backend/job_loadouts.py`
- Song performance overlays
- Song targeting preview data

The Song targeting preview now uses the same map-cell highlighting path as other area/support previews (the `spell-area`/AoE forecast presentation), and Bard Songs are treated as self-targeted preview skills in `frontend/src/combat-hotbar.js`.

The purple artwork was identified: Bard zones were falling through to the existing `binding_tether` accent artwork used by binding zones. That was not intended as a Bard effect. Bard zones now skip that fallback and retain the dedicated performance wash and dancing musical notes.

No dedicated Bard sprite-sheet/image pack has been generated yet. The current notes are CSS/SVG text-style effects. A full Bard effect pack can be generated later if we agree on the visual language first.

## Validation completed

- Backend Bard + starter tests: **39 passed**
- Frontend focused tests (hotbar, spaces, status presentation): **17 passed**
- Frontend production build: passed

The live browser still needs a visual check for the one-cell Song preview after restarting/reloading the development server.

## Remaining follow-up

1. Restart/reload the dev client and visually verify each Song highlights exactly the one-cell performance space before activation.
2. Verify Song of Peace and the other Songs show the same preview treatment as Fighter Hold Together.
3. Confirm there is no remaining purple binding artwork in active Bard zones.
4. Decide whether to commission a generated Bard performance sprite/effect pack; none has been silently substituted.
5. Preserve the unrelated pre-existing dirty worktree changes. No production push or commit was made.

## QA profile note

Historical QA used `E:\fortcamp-faction-qa-profile`. The October 7 cleanup moved it into `fortcamp-dev\data\browser-qa\archived-profiles`. Future isolated Chrome profiles belong in `fortcamp-dev\data\browser-qa\profile`, ignored by Git. Browser QA scripts connect to Chrome DevTools on port `9229` and load local preview fixtures from `127.0.0.1:8766`; profiles are not game source code or production data.
