# Character stamina / fatigue pacing proposal

**Proposal only. No stamina costs, recovery or mission restrictions are implemented.**
User discussion: 100 starting points, gradual recovery totaling 200 per pool,
rank costs E1 / D3 / C5 / B10 / A50 / S100; a character may start a mission with
at least one point and borrow the rest, entering negative points. These are
remaining stamina points (high means rested), rather than accumulated fatigue.

## Current timing and the borrowing math

Current mission pool period: 1,800 seconds / 30 minutes (`backend/services.py`).
Interpretation for comparison: capacity 100, integer eligibility at least 1,
continuous recovery with no pool-boundary refill. Negative balances recover at
the same rate and are not cleared by resets. Treating eligibility as a positive
fraction would let players borrow again almost instantly, so use at least 1 whole
point. Expensive mission borrowing can reach -99, but cannot accumulate beyond
that if the next mission also requires at least 1.

With recovery of 200 per 30 minutes, gain 1 every 9 seconds. Ignoring combat
length and other existing availability restrictions, a rested character can
start S missions at 0 seconds (100 -> 0), 9 seconds (1 -> -99), and 909 seconds
(1 -> -99). That is three starts in the first pool. Sustained spending later is
about two S missions per 30 minutes. This is a resource rate, not a hard quota;
alignment to the shared reset and combat duration also affect the count.

With recovery of 100 per 30 minutes, gain 1 every 18 seconds. A rested character
can start two S missions in the first pool, then sustained spending is about one
S mission per 30 minutes. It does not replenish instantly on reset. Offline time
counts, recovery caps at 100, and unused time cannot bank recovery beyond the cap.

Do not claim both a strict two-S maximum and a sustained two-S rate with the
200-per-pool recovery plus this borrowing rule; that would need a separate quota
or changed borrowing eligibility. A strict quota is not recommended for this pass.

## Balance recommendation for discussion

If rotation is the priority, start with capacity 100 and recovery 100 over 30
minutes, retain borrowing, and test E1 / D3 / C5 / **B20** / A50 / S100. This leaves
solo E/D play cheap and raises B's cost so the C-to-B change matters. A's original
fivefold jump from B10 to A50 would otherwise bear most of the rotation pressure.
This profile allows rested bursts and makes borrowing a deliberate reserve-party
choice. The user can instead retain 200 recovery for a more generous steady rate,
accepting the additional rested S burst. Both profiles remain proposals.

At 200 recovery and B10, the sustained resource rate permits 20 B missions per
character per pool before existing mission/claim/party constraints. At B20 it is
10. At 100 recovery and B20 it is 5. Fatigue never replaces actual rank-specific
combat difficulty or mission scarcity. It encourages rotating individuals, but
varied builds need useful role, race, gear and enemy/terrain differences as well.

No stat penalties are recommended: negative stamina blocks the *next* deployment
until recovered; it does not suddenly weaken a crew inside its current mission.
Party costs apply per participating character, not once to a shared account pool.
Bodyguards and mercenary treatment need an explicit follow-up decision so hiring
cannot become a stamina bypass. Ordinary base work should not share these mission
costs in the first pass; early solo progression must stay usable.

## Eventual implementation and performance

Charge when deploying into a private contract, after validation; claiming a
public contract is not deployment and costs no stamina. Validate every selected
character on the server, then atomically deduct once. Existing deployed/injured
availability checks continue to apply. Invalid submissions and repeated network
requests must not double-charge. Cancel/refund policy before any mission action,
mercenary costs and multi-stage chain costs remain decisions before implementation.
Suggested chain policy: charge once for the accepted contract, not for each
roll/dialogue/battle stage inside it; another follow-up contract has its own cost.

Store a balance and timestamp per character. Derive recovery from elapsed real
time only when read or used, cap it, and preserve fractional time/tick remainders.
No per-character background jobs, per-second database writes or per-character
JS intervals. Reuse one shared display clock for visible UI, update text only,
and avoid sorting/re-rendering a 100-character roster each second. Offline
recovery falls out of timestamps. Debug Battle Lab remains isolated from real
character stamina. Persistent storage / transactional reads protect against
refresh, reconnect or dev/prod save leakage.

Before tuning, measure actual successful deployments by rank per active player,
minutes per combat, early roster size, costs compared with rewards, and negative
stamina downtime. Adjust the recovery/cost config from those measurements instead
of assuming infinite instant mission completions are normal play.
