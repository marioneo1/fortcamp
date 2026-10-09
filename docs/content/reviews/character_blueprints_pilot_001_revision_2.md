# Pilot 001 revision 2 review

Reviewed October 8, 2026. **Targeted corrections required; not approved or live.**
Source: [untouched revision 2](../drafts/character_blueprints_pilot_001_revision_2.json).
Compared against the original submission, [revision request](character_blueprints_pilot_001_revision_prompt.md), v0.2 authoring contract and character-story design proposal.

This is a useful revision, not a finished implementation specification. Keep the
submission in drafts. No story, loyalty, reward or runtime changes were made by
this review. New gameplay/story choices need user review before approval.

## What improved

- All 101 original `id` values remain; revision 2 contains 112 distinct IDs.
- Both major arcs now propose player-scoped one-offs, retaining their original
  repeat keys; introductions remain character-scoped.
- Guard evidence/trust and artisan review/ledger have explicit incoming routes.
  Every routing-table `to` points to a defined ID or `end`.
- The artisan inspection is one committed narrative preparation choice followed
  by actual ordinary mission success and a debrief. Failure/retreat preserves
  preparation and requires a subsequent eligible successful mission.
- Anti-Orc specialization is again a legitimate proposed reward, with defensive
  training as an alternative. Reconciliation does not invent hidden stat bonuses.
- Unsupported mechanics and reward grants remain proposals rather than claims
  of existing engine support. Optional devotion is separate from core closure.

## Required data corrections

JSON parses, but 23 guard fields that had concrete values in the original are
now `null`. These are not intentional unapproved reward IDs. Restore the typed
values below in a separate corrected revision, preserving this submission.

All paths below are relative to `entries[0]`:

| Path | Required value | Count |
| --- | --- | --- |
| `facets[0..7].starts_revealed` | In order: `true, true, false, true, true, false, false, false` | 8 |
| `introduction.eligibility.all[3].value` | `true` (`speaker.conscious`) | 1 |
| `introduction.prospective_loyalty_cap.value` | `80`, matching its prose; still an unapproved mechanic | 1 |
| `introduction.prospective_loyalty_cap.review_required` | `true` | 1 |
| `introduction.repeat_policy.max_offers` | `1` | 1 |
| `personal_arcs[0].repeat_policy.max_offers` | `1` | 1 |
| `personal_arcs[0].entry_conditions.registered_predicates.all[2].value` | `true` (`speaker.conscious`) | 1 |
| `reward_contracts[0..2].review_required` | `true` for each | 3 |
| `capability_requests[0..5].review_required` | `true` for each | 6 |

The other eight nulls already existed: six unapproved reward implementation IDs,
the artisan's proposed history-tag registration and the artisan's absent loyalty
cap. Do not replace those merely to eliminate nulls.

## Required behavior clarification

### Character-specific cap versus player-specific quest

The introduction can assign this individual an Orc-player loyalty cap, but the
major resolving story can only run once per player. The revision does not
explicitly prevent a second recruit from receiving that cap after the story key
has been consumed by another character.

Before approval, choose an allocation policy: reserve the available one-off for
the eligible character before assigning its cap-bearing history, or provide a
separate nonreward resolution for later characters. Recommendation: reserve the
one-off before assigning this particular cap-bearing blueprint; reusable voice
facets can still belong to other characters. This is a recommendation, not an
approved rule or a change made by this review. Abandonment, dismissal and final
decline also need explicit reservation/completion handling.

### Quiet-account recovery needs an explicit transition

The combat path can reach `milestone_reckoning` without
`state_costly_truthful_report`, which reconciliation requires. Its insufficient-
proof row goes to `end`; its prose says to offer `node_quiet_account`, while
the generic resume rule returns to the source milestone. Specify an explicit
choice/transition to the existing quiet-account interaction, with same-instance
state and return behavior. Destination existence alone does not prove the
conditional reconciliation path is usable.

## Story proposal requiring user choice

The new quiet-account path offers a disputed compensation claim that unfairly
blames unrelated Orcs. Waiving that real optional claim and recording truthful
limited responsibility proves trust. This makes the earlier vague promise
concrete and avoids random encounter farming, but adds a specific financial
story beat and a private-contract capability.

The revision request allowed a private-contract fallback; it did not approve
this particular plot or payment mechanic. A credible payer, entitlement, amount,
actual opportunity cost and irrevocable claim outcome must be defined if chosen.
Do not manufacture compensation just to demand the player surrender it. Ask the
user whether this is the desired trust test before developing or implementing it.
If it is rejected, propose a small alternative rather than silently substituting
a different plot. The draft correctly says not to activate the loyalty cap until
its deterministic recovery exists.

## Editorial and validation limits

The file is approximately 7,600 whitespace-separated words, above the requested
3,500–5,000. This is secondary to correctness, but repeated warnings and state
explanations can be condensed after the story decisions are settled.

Checks performed: JSON parsing, recursive comparison of null fields and original
ID preservation, distinct ID counts, routing destination existence and manual
review of conditional flow/repeat policies. This is not executable JSON Schema
validation or a gameplay simulation. Valid IDs do not establish that proposed
events, rewards or predicates are implemented. No importer exists.

Recommended next step: locally repair the mechanical data defects in a separate
revision, then resolve the cap allocation, trust-test choice and explicit recovery
route with the user before approving the two blueprints or commissioning dialogue.
