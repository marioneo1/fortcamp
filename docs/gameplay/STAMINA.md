# Expedition stamina

Implemented in dev, October 4. Production has not been updated by this pass.
The player-facing term is **stamina**: high points mean rested. Fatigue is the
pacing system, not a second meter. Earlier discussion remains in
[the proposal](../design/FATIGUE_PACING_PROPOSAL.md).

## Rules

Every roster character starts with 100 points, maximum 100. Restore one point
every 18 seconds (100 over 30 minutes), including offline, during missions and
while injured. A pool refresh does not refill points or remove debt. Time spent
already full cannot bank future recovery. Stamina is independent of HP and injury.

| Contract rank | Cost per participant |
| --- | --- |
| E | 1 |
| D | 3 |
| C | 5 |
| B | 10 |
| A | 50 |
| S | 100 |

Starting requires at least one whole point, even if the contract costs more.
Borrow the difference: an S contract started at 1 leaves -99. Recover to 1 before
another departure. At zero, eligibility returns in 18 seconds; at -99, in 30
minutes. Fully recovering from zero takes 30 minutes, from -99 takes 59 minutes
42 seconds. Fractional recovery is preserved but cannot bypass the one-point rule.

Spend once when the private contract actually starts, not when reserving it from
the public board. Bodyguards and hired mercenaries pay the same rank cost; saved
mercenary offers retain debt between hires and permanent recruitment. The fee is
not refunded for defeat, retreat or abandoning an operation after departure.
Decision scenes and subsequent battles inside that contract do not charge again.
A separate follow-up contract charges again. Existing injury/deployment rules
still apply. There are no stamina penalties to stats, rolls or combat actions.
Base work, equipping and conversation do not cost stamina or require positive
stamina. The meter applies to the player's character as well as companions.

Existing saves initialize missing meters at full. Already-running contracts are
not retroactively charged. Battle Lab and forced debug completion do not spend
real stamina; resolving an already-deployed contract does not refund its cost.

## Interface

Roster cards/details, assignment candidates/slots and hiring cards show points
and time until full (or until eligible when below 1). Assignment hides tired
characters and team suggestions exclude them. A tired character becomes a
candidate when recovery reaches 1 without reopening the planner. Deployment
analysis shows cost and resulting points for each participant, with explicit
borrowing and insufficient-stamina text. Server validation remains authoritative.

## Persistence and performance

backend/stamina.py stores balance and timestamp in each character's JSON save.
Read recovery from elapsed time, without writing a recovered balance during
polling. Missing fields are initialized once by state normalization. Deployment
uses the existing player lock and conditional mission update; rejected or repeated
starts do not charge points again. Mercenary copies mirror spending to the saved
offer. No schema migration, dependencies, per-character jobs or timers were added.

The existing shared UI clock updates visible text only. The planner rebuilds
candidates when the next eligibility boundary is reached, rather than sorting
the roster every clock tick. Values use the existing browser clock convention;
an inaccurate local clock can make the display disagree with server validation.

## Validation and deferred tuning

Tests cover offline/fractional recovery, negative debt, no banked time, clock
rollback, initialization without repeated recovery writes, atomic group checks,
bodyguards, persistent hired debt, real SQLite deployment/retry/rejection, and
frontend filtering. Isolated browser QA checks suggestions, recovery eligibility
and desktop/mobile readout layout. Runtime and build regression results are
recorded in the history log.

Recovery/capacity quest unlocks, meals and restoration consumables remain
proposals. Do not imply existing buildings grant stamina recovery. B10 remains
the initial pacing choice; later costs must be evaluated against whole-party
effort, contract duration, success risk and mission-specific loot. No reward
tables or mission difficulty were changed in this pass.
