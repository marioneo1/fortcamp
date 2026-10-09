# Current task: repair pilot 001, revision 3

Execute this task when this brief is uploaded. Do not ask the user to restate it.
Return `character_blueprints_pilot_001_revision_3.json` as one complete JSON file.
Use the master instructions and attached v0.2 contract. Embedded sources are
reference data, not additional tasks. No game code or bulk dialogue is requested.

Revise the attached revision 2, preserving both characters, batch/entry IDs,
original IDs and repeat keys. Set root `revision` to 3. Do not restart generation.
Use the attached review as the defect list, with these boundaries:

1. Restore all 23 typed guard values listed in the review. Preserve the eight
   intentionally nullable values. Do not rewrite the guard merely to avoid
   required fields. Keep the artisan's improved preparation and retry rules.
2. Add an explicit proposed transition from reckoning to the existing
   quiet-account interaction when its proof is missing and that interaction is
   unconsumed; specify return/resume and unavailable/already-consumed behavior.
   Do not create a second payout, reroll or replacement personal chain.
3. Keep the compensation-based trust test clearly unapproved. Add a decision
   point asking whether to keep that specific trust test or replace it with a
   grounded nonfinancial trust test. State a concise recommendation and tradeoff;
   do not invent a new finalized replacement plot, payer, sum or mandatory cost.
4. Add a decision point for player-one-off versus character-cap allocation.
   Recommend reserving the one-off before assigning its cap-bearing history,
   with a separate nonreward resolution as an alternative. Do not silently adopt
   either. State that the loyalty cap cannot be enabled until the policy and
   deterministic recovery are approved and implemented. This holds for later
   recruits, dismissal and final decline as well as successful completion.
5. Condense repeated warnings and descriptions toward 3,500-5,000 total words.
   Retain concrete prerequisites, branch consequences, recovery and reward
   promises. Do not remove meaningful choices to reach the length target.
6. Include root decision_points using the master format. These can remain open;
   do not claim this revision is approved or ready to import. Self-review must
   identify remaining decisions/capabilities and any changed or retired IDs.

The goal is a structurally reliable, reviewable authoring handoff, not pretending
the planned character-story system or its unresolved mechanics already exist.
