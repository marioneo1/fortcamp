# Pilot 001 revision 3 review

Reviewed October 8, 2026. **Structural checks passed; design decisions pending;
not approved or live.**

Source: [untouched revision 3](../drafts/character_blueprints_pilot_001_revision_3.json).
Compared with revision 2, its review and the packaged revision 3 request.

## Confirmed corrections

- Offline checker reports zero structural errors against revision 2.
- All 23 unexpectedly null guard values are restored. Eight intentionally
  nullable values remain: six proposed reward implementation IDs, the artisan's
  unregistered history tag and its absent loyalty cap.
- All 112 revision-2 IDs remain; two decision IDs are added. Original repeat keys
  remain unchanged. Major arcs are player-scoped and introductions character-scoped.
- Reckoning explicitly routes to the original pending, unconsumed quiet-account
  offer when proof is missing. Publish/claim returns to reckoning; waiting resumes
  the quiet offer. Consumed or unavailable claims cannot be rerolled.
- Cap activation is expressly blocked until allocation, deterministic trust
  recovery and supporting mechanics are approved and implemented.
- Artisan preparation, ordinary mission participation, failure/retreat retry and
  debrief remain clear. Opening a conversation does not count as inspection.
- At approximately 4,992 whitespace-separated words, the submission meets the
  requested 3,500-5,000 word target.

## Remaining user decisions

1. **Trust test:** keep the disputed-compensation waiver or use a grounded
   nonfinancial test? Recommendation: develop the nonfinancial option unless
   this character's premise already supports a credible entitlement and payer.
   Forgoing an invented payment risks feeling like paying to unlock loyalty.
   A replacement still needs a concrete action, evidence, consequence and
   deterministic availability; no alternate plot is approved by this review.
2. **One-off allocation:** reserve the personal story before assigning its
   cap-bearing history, or support later recruits with a distinct nonreward
   resolution? Recommendation for the pilot: reserve before assignment. Reusable
   traits can remain common; this particular story package belongs to one
   character per player. Define reservation on first eligible introduction,
   release before recruitment/commitment and consumption on accepted story or
   final outcome as part of the eventual reviewed policy, not an assumed rule.

The draft correctly records both choices as approval-blocking decision_points.
Its recommendations do not establish project rules.

## Human review notes and implementation limits

The new recovery route fixes the identified connection gap; it does not make an
unapproved private contract real. The chosen trust test needs its own approved
scenario before dialogue is commissioned.

Specialization, taking the disputed claim and final uncertainty intentionally
do not resolve distrust. Their possible permanent cap consequence must remain
visible at choice time. Reservation alone does not decide whether a player who
deliberately closes the trust path can later repair the relationship; settle that
with the cap policy. Do not promise unconditional recovery in player-facing copy
while simultaneously making all recovery choices final and exclusive.

Permanent specialization balance, ordinary supplies/gold sources and amounts,
history assignment, outcome events and runtime persistence remain unimplemented
dependencies. These need ordinary implementation design after the premise is
approved; another authoring revision cannot prove engine support.

Manual review covered conversation choices, guard conditional recovery and
exclusive endings, artisan preparation/success/retry/debrief, reward promises,
cap/one-off caveats and the two decision points. Structural checks are not a
formal conditional-flow proof or gameplay simulation. Neither blueprint has
been imported, and the submitted JSON is unchanged.

## Process result and next step

The strengthened single-file request produced the requested repairs, concise
output and explicit pending choices. This is evidence of improvement on this
submission, not a guarantee that future GPT files need no checking.

Do not ask the user for another GPT correction round now. Resolve the two design
choices, then Codex can prepare the next bounded authoring request or a separate
local revision as appropriate. The existing upload brief is the completed
revision-3 request, not instructions to generate revision 4.
