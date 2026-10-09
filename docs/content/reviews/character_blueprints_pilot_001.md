# Pilot 001 review

Status: **reviewed, revisions required**. October 8, 2026.
Source: [original GPT batch](../drafts/character_blueprints_pilot_001.json).
The source was moved without changing its contents; it is not approved or live.
Use [the focused revision prompt](character_blueprints_pilot_001_revision_prompt.md)
with that source. Preserve original IDs and return a separate revision file.

## Assessment

Good character-design foundation. The Watchful Caravan Guard retains a reserved
strategist identity across endings; The Workshop Ledger gives an engineer a
mundane professional concern with appropriately ordinary rewards. Both distinguish
known history from optional development and preserve post-story personality.
Early prospective cap disclosure and capture/kill distinction are understood.

Do not restart the whole batch. Revise the transitions, concrete objectives and
reward options before commissioning dialogue or implementing these arcs.

This is a prose blueprint format, not a complete executable quest definition.
Valid JSON and IDs do not demonstrate reachability or gameplay support. Some
overly defensive/repetitive writing reflects the original prompt's emphasis on
unsupported claims; refine the authoring guidance as well as the returned content.

## Static checks

- JSON parses; batch/schema/type and two root entry structures match the draft.
- Two entries, each with eight facets, four intro-revealed facets, five
  conversation nodes and one four-milestone personal arc.
- No duplicate object IDs or unresolved blueprint-local ID references.
- Existing race/Job/personality IDs and non-null facet tags use the draft registry;
  new artisan history is correctly left as a proposal rather than a live tag.
- Reward implementation IDs remain null and capability requests are marked for
  review. These are correct boundaries, not evidence of executable rewards.

## Required revisions

### 1. Make the conversation and milestone flow explicit

Guard milestone_encounter goes directly to milestone_reckoning; node_evidence
has only a textual eligibility condition and no explicit incoming transition.
node_trust likewise has no explicit transition from the reconciliation ending.
Artisan milestone_field goes directly to milestone_account, while node_review
and node_ledger are described but not explicitly entered by the graph.

IDs all resolve, but a consumer following only next fields would skip these
conversations. Add a small routing table that names the entry, selected-choice
edges, event wait/resume edges, branch outcome edges and terminal states. Make
selected choice.next authoritative; a generic node.next must not auto-advance
through a defer/decline choice. Account for post-resolution optional pledge
without reopening the chain or issuing a second reward. These routing fields
are an authoring clarification, not a new runtime capability already delivered.

### 2. Give the trust bridge a real cause and a scored path

The guard requires a costly prior fair-treatment commitment, but there is no
fully defined commitment node/action, success condition or failure branch.
Current reconciliation text can become an impossible gate rather than an earned
outcome. Name the promise, when the player accepts it, what event proves it,
and how the player learns its requirements before acting.

The decline choice promises a separate ordinary-talk/nonviolent closure route,
but later trust needs the verified encounter. Either define that alternative
with explicit transitions or remove the promise. An Orc player should not be
silently stranded at 80 by an unavailable personal target. Defer and informed
final acceptance of an unresolved cap can exist; those are different choices.
Do not lift the cap merely because Orc enemies died or grant instant 100 loyalty.

### 3. Make target availability practical

The guard requires independently verified membership in the exact warband.
That protects lore, but current ordinary missions do not establish that personal
membership. Define the reviewed generation/binding integration: a compatible
unnamed procedural enemy can receive saved story affiliation before exposure,
within the normal encounter budget. Never rewrite named lore or invent past
recognition after the enemy has already been encountered. Alternatively propose
an ordinary Private Contract follow-up with reviewed support.

Do not require repeated random missions indefinitely as the only route to
resolving an early loyalty conflict. The source's no-proof closure honestly
leaves the cap in place; it is not a substitute for a viable resolution route.

### 4. Simplify the artisan's actual gameplay

The shared inspection is treated as requiring a separate observation/scoring
mechanic, while text says selecting a dialogue option cannot count as doing it.
That is unnecessarily restrictive for a conversation-led quest. An eligible,
committed narrative choice such as inspecting gear together can legitimately
perform the inspection and record a result. Opening/replaying prose cannot.

Use one explicit saved preparation action, ordinary mission participation and a
debrief. No new inventory inspection minigame is needed unless deliberately
requested. State one exact failure policy: current wording says a failed mission
may require another check, leaving scoring ambiguous. Avoid padding the path
with repetitive agreement/check/account conversations that offer no real decision.

### 5. Preserve enemy-type reward options and branch value

The guard reward explicitly says it is not an anti-Orc modifier. That exclusion
is not a user requirement; an appropriate enemy-type specialization perk is a
valid candidate. Keep defensive training as one option, but do not silently
remove the requested hunter/specialist direction. Any numbers remain balance
proposals and rewards need implementation review.

For a non-Orc player, removing an Orc-player cap provides no benefit. An optional
platonic bond currently has no defined mechanical effect. Explain the meaningful
payoff of reconciliation for that player; narrative closure can be enough if
honestly promised, or offer a suitable reviewed reward. Do not invent a hidden
bond buff. Distinct endings need deliberate value, not identical stats.

Do not describe ordinary training supplies as equivalent to a promised permanent
perk without revising the promise before acceptance. The artisan's modest gold/
ordinary-loot options are otherwise appropriate for its professional theme.

## Design decisions to make explicit

- Both arcs currently use character-scoped repeat keys: a new roster member
  could repeat the same quest. This is not a malformed field, but differs from
  a once-per-player one-off. Recommend player scope for these first major pilot
  stories; keep their reusable personality/voice profiles separate. Future
  character-scoped motifs remain possible when deliberately authorized.
- Core closure and unresolved conflict are separate. Final opt-out can close
  activity while preserving distrust; the player must see that consequence.
- Outcome alternatives that were not chosen remain inactive. Optional developed
  facets are not missing compulsory personality components.
- The source is about 90 KB/8,360 whitespace-delimited words for two blueprints.
  Keep the detail needed to play/score the stories, but consolidate repeated
  review/save-load warnings. A shorter revision should be easier to implement
  and reason about, not merely have shorter sentence fragments.

## Next step

Request one focused revision retaining both characters and all existing IDs.
Review its routing/outcomes and reward promises before approving permanent tags,
building the runtime foundation, or generating stage-specific dialogue. No new
mechanics, catalogue approvals or save migrations were performed in this review.
