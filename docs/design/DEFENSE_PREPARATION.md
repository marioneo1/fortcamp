# Defense preparation

Implemented in dev October 9, 2026. Current rules supersede the older spike-trap,
snare and watch-platform preparation menu; existing version-1 battles retain
their saved rules for compatibility. Start a fresh defense to use version 2.

## Hedgerow allotment

Base points: **12 + 4 per defender** (20 for the intended two-person party).
Existing racial defense bonuses remain capped at +3 for the party. Defense tools /
Field Fortifier add +2; trapping tools / Trapper add +1; Fast Builder adds +1
per qualifying defender. Matching equipment and its granted perk do not count twice.

## Point-funded defenses

| Defense | Cost | Rule |
| --- | --- | --- |
| Barricade | 1 | 12 HP; blocks walking, allows firing through it. |
| Palisade | 1 | 18 HP; blocks walking and sight. |
| Stone Wall | 1 | 18 HP, 2 Armor; blocks walking and sight. |
| Trap Pit | 2 | Ground enemies entering take base 25% max HP fall damage and lose remaining movement/attacks; Climb Out spends the next main action to reach a legal adjacent cell. |
| Proximity Dynamite | 3, or 2 with an Engineer | Anyone approaching within one cell triggers explosive damage and one-cell knockback in a one-cell blast radius; allies can trigger and be hit. |

Walls, palisades, barricades and point-funded traps have **no separate placement
count cap**. Available points and legal map cells are the constraints. Pit damage
uses the normal environmental pipeline with armor bypass; applicable defensive
effects can still modify damage. Flying and Trap Expert avoid pit triggering;
allies can cross these enemy-facing trap pits. Pits remain after use. If every
escape tile is blocked, the trapped unit must wait for a legal exit.

Proximity Dynamite uses the existing 2× placer attack explosive packet, displacement
resistance, collision and hazard interactions. It stops the current route when
it explodes; it does not add the timed Engineer Dynamite's Stun/Hobble rider.
Trap Expert avoids triggering explosives, but does not grant explosion immunity.
Known explosives warn in route previews; previews never detonate them.

## Equipped Job deployments: free

Only real party Engineers/Rogues and **equipped skills** qualify, as confirmed by
the user. Learned-but-unequipped abilities and equipment perk names do not unlock
these entries. Each option displays its owner. No main action, charge use or
cooldown is spent during preparation.

- Engineer Sentry Turret: already built; three active per Engineer, sharing normal
  combat deployment slots.
- Engineer Heavy Emplacement: already built; one active per Engineer, sharing its
  normal slot. Both machines use their normal autonomous firing/mounting rules.
- Engineer Proximity Charge: one active mine per Engineer in this defense, also
  enforced when placing another during combat. Other encounters keep their normal
  two-mine limit. It uses ordinary mine disruption, not the proximity bomb's damage.
- Engineer timed Dynamite: free; survives the Engineer's first activation and
  explodes at their following activation. It keeps normal timed Dynamite effects.
- Rogue Caltrops: free rotatable 1×3 strips; no added preparation count cap. Each
  strip lasts through two Rogue activations and uses normal Bleed/Hobble, ally and
  forced-movement rules. Multiple prepared strips coexist; overlapping entries
  still follow the existing deduplication rules. NPC Tripline does not unlock Caltrops.

Placement requires the whole footprint in the preparation zone, unoccupied solid
ground, and no existing prepared defense on those cells. Armed mines/bombs cannot
be placed touching an enemy. **R** or Rotate changes caltrop orientation. The UI
previews footprint and explosive trigger radius. Click any prepared placement
to remove it: points are refunded, machines/zones/explosives are removed and
deployment slots restored. Prepared machines cannot be moved through party deployment.

Existing turret, caltrop, pit, dynamite and explosion art/audio are reused. No new
paid asset generation or live-save migration. Manual visual review remains open.

Validation: 232 backend regression checks, 427 frontend checks and browser build
passed; 81 focused checks also pass after the eligibility fix. Four prepared
Engineer/Fighter fights complete across all four layouts without errors/stalls.
These are smoke checks, not extensive solo-support balance work.
New tests cover equipment eligibility, shared caps, unlimited barriers,
rotation/whole-footprint legality, removal/refunds, monotonic placement IDs,
walk/forced pit entry without duplicate damage, escape cost, timed fuse, explosive
knockback and read-only route warnings. Follow-up fix restricts Caltrops eligibility
to the real equipped skill ID, rather than NPC Tripline's shared implementation tag.

## Proposal, not implemented

Alarm tripwire: a non-damaging reveal trap for concealed enemies. Consider only
after playing the rebuilt menu; no additional trap effects are silently added.

Sources: `backend/combat_defense.py`, `backend/combat_engineer.py`, existing pit
resolution in `backend/combat.py`, and `frontend/src/defense-preparation.js`.
