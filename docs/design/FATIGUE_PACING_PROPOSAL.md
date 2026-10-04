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

## Earlier rotation-first recommendation (superseded)

The earlier rotation-first suggestion was capacity 100 and recovery 100 over 30
minutes, retain borrowing, and test E1 / D3 / C5 / **B20** / A50 / S100. This leaves
solo E/D play cheap and raises B's cost so the C-to-B change matters. A's original
fivefold jump from B10 to A50 would otherwise bear most of the rotation pressure.
That profile allows rested bursts and makes borrowing a deliberate reserve-party
choice. The user can instead retain 200 recovery for a more generous steady rate,
accepting the additional rested S burst. Both profiles remain proposals.

## Revised recovery and reward recommendation — October 3

The user's goal is to recover fully after an S mission by the following pool,
including repayment of borrowed points. Prefer the user's 200 recovery per 30
minutes as the starting proposal. At that rate, 0 -> 100 takes 15 minutes and
-99 -> 100 takes 29 minutes 51 seconds. Recovery starts when deployment spends
points, not when a shared pool resets. A late-pool deployment cannot guarantee
full stamina at the next boundary without an instant refill, which is not the
proposed system. Further deployments also extend recovery. Accept the rested
three-S burst described above; scarcity, actual combat time and crew availability
still constrain play. No fixed per-rank completion quota is proposed.

The earlier B20 cost has not been justified by current rewards. For normal
success, current rank scaling in backend/content.py is:

| Rank | Base gold when the mission pays gold | Extra loot rolls | Chance per roll | Expected extra items |
| --- | --- | --- | --- | --- |
| E | 4–7 | 1 | 28% | 0.28 |
| D | 8–13 | 1 | 35% | 0.35 |
| C | 15–23 | 2 | 42% | 0.84 |
| B | 28–40 | 2 | 50% | 1.00 |

This compares only ordinary success base payouts and independent extra cache
rolls. It excludes authored drops, gold from missed caches, corpse loot, event
rewards, recruits, critical bonuses, exclusive discoveries and failure risk.
Not every mission pays gold. Rarity weights are renormalized to eligible tiers;
do not present nominal rank rarity weights as exact universal drop rates.

At C5/B20, one B costs four C deployments per character. Their normal base gold
averages are 34 versus 76 and extra cache expectations are 1 versus 3.36 items.
Higher-tier access adds value, but these generic payouts alone do not establish
that B is worth four C missions, especially when B also needs a larger crew.
Four B completions are not an implemented allowance: capacity 100 at B20 covers
five full-price deployments before recovery or borrowing.

Keep B10 as the initial cost candidate; consider B12–15 only after reviewing
specific B contracts and actual outcomes. B20 would need a paired reward pass.
Assess whole-party stamina, mission duration, win chance, gold/claim cost, gear
rarity and useful build-changing effects together. B should offer meaningful
access to better equipment, faction progress and chain opportunities; it need
not beat E/D/C in every farming metric. Preserve lower-rank exclusive drops and
cheap gathering routes so earlier content stays worthwhile. These are proposals,
not deployed economy changes.

### Earn recovery through play, not just construction costs

Suggested optional progression, not existing content:

- A healer/herbalist Private Contract chain unlocks a camp recovery improvement
  worth +10% of the base recovery rate. Its recipe or blueprint is the achievement;
  resources finish construction rather than being the only unlock requirement.
- An exploration chain can uncover a restorative camp relic, adding another
  +10% of base recovery. Install it at camp instead of consuming a combat gear
  slot. A low-rank exclusive discovery can start this chain to keep those ranks
  relevant; provide an earned route rather than making basic recovery depend on
  one exceptionally rare roll.
- A character's personal agreement can improve that individual's recovery or
  unlock an optional preferred meal benefit. Keep food a bonus, not mandatory
  feeding upkeep or a punishment for missing a session.
- Scarce restorative consumables can provide an emergency partial recovery.
  They should not become cheap repeatable full refills that erase party rotation.

Start with at most +20% combined passive recovery, additive rather than
multiplicative: 200 -> 240 per 30 minutes. This shortens 0 -> 100 to 12 minutes
30 seconds and -99 -> 100 to 24 minutes 52.5 seconds. This is a tuning target,
not a promised permanent ceiling. Unique unlocks do not stack via duplicate
items; meal/individual boosts need explicit combined limits before implementation.
Recovery progression should make returning to characters feel better without
making a large roster or constant consumable farming compulsory.

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
