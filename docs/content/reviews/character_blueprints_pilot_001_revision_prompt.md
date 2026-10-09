# Focused GPT revision request - pilot 001

Attach the original draft JSON, the current single-file GPT brief and this file.
Say: "Revise the attached pilot using this focused review request; do not execute
the original generation request again." Return the revised JSON separately.

```text
Revise character_blueprints_pilot_001, preserving its two characters, original
entry/node/facet/arc/reward IDs and core identities. This is authoring, not live
gameplay. Keep schema_version=0.2, content_type=character_blueprint and batch_id
unchanged, and add revision=2 at the root. Do not recycle IDs, rename entries,
generate unrelated blueprints, write engine code or produce bulk dialogue.

Use the existing nested v0.2 format. Add review-required local routing metadata
where needed; these additions are design clarification, not executable runtime
features. New local IDs must be namespaced under the relevant existing entry.

1. Add a compact routing table per entry: from ID, trigger or selected choice,
   prerequisite, to ID and state effect. Every intended conversation/milestone/
   ending needs a reachable path. Selected choice.next overrides generic
   node.next. Explain event waits and resume points, defer versus final decline,
   and once-only post-resolution conversations. Do not auto-advance past choices.
   Guard node_evidence/node_trust and artisan node_review/node_ledger currently
   have no explicit incoming routing; connect or deliberately remove them with
   a clear retirement note. Preserve existing IDs whenever the beat survives.

2. Define the guard's actual trust promise and evidence. Specify exactly which
   prior choice arms it, what player-observable event proves it, how it can fail,
   and which final branch it enables. A costly truthful choice cannot remain
   vague prose. No automatic trust from Orc kills. Do not require a specific
   class/loadout's capture ability as the only path to resolving the loyalty cap.

3. The guard's decline choice promises a nonviolent ordinary-talk closure that
   is not actually modeled. Supply a credible explicitly routed alternative
   for reconciliation, or amend the promise and provide a practical recovery
   path. Differentiate stopping the hunt with unresolved distrust from resolving
   the distrust. Display that consequence. Never silently strand an Orc player
   at 80 because no compatible random enemy appeared; removal of the cap does
   not automatically grant loyalty points.

4. Define target availability. An existing unnamed procedural enemy can be
   assigned compatible saved warband/story affiliation BEFORE being encountered
   through a reviewed generation hook, within the normal mission budget. This
   is a capability proposal, not current support. Do not reinterpret a named
   lore enemy, respawn a dead rival or call an arbitrary visible Orc a perpetrator.
   A reviewed ordinary private-contract follow-up is another possible recovery.
   The core path must not depend on endless chance farming.

5. Simplify the artisan inspection: one explicit eligible narrative preparation
   choice can perform the two-person inspection and commit its result. Merely
   opening or replaying a conversation cannot. Do not demand an unnecessary
   physical inspection minigame. Follow with real ordinary mission participation
   and a useful debrief. Replace 'may require another mission' with one exact
   success/failure/retry policy. Keep the ordinary gold/loot reward theme.

6. Restore enemy-type specialization as a valid guard reward proposal: the user
   explicitly allows relevant anti-Orc damage perks or techniques. Do not exclude
   them categorically. You may recommend defensive training as an alternative,
   but explain the tradeoff. Numbers and implementation_id remain unapproved.
   Reconciliation must have a meaningful stated payoff for non-Orc players too,
   since they never had the cap. Do not invent hidden mechanical bond bonuses.
   Never substitute supplies for a promised permanent skill/perk after acceptance.

7. For these first major pilot arcs, propose player-scoped one-off repeat keys;
   preserve existing repeat_key identities. Another roster member cannot rerun
   the same reward chain. Reusable personality/voice facets are separate from
   one-off story availability. Character-scoped motifs may be proposed separately,
   not silently enabled here. Introduction disclosure stays character-scoped.

8. Preserve distinction between identity establishment and optional emotional
   development; closed characters continue ordinary memories and progression.
   Retire resolved hostile lines, not history. Romance remains separate from
   platonic devotion; no need to add romance to this pilot.

Consolidate repeated review/save-load warnings into short shared notes, while
keeping concrete gameplay prerequisites and branch consequences. Aim for roughly
3,500-5,000 words TOTAL across the JSON, not 8,000+ words. Return one complete
JSON object/file, no markdown or text outside it. Include honest self_review;
claim no programmatic validator ran. Identify remaining unsupported mechanics,
unreachable routes, reward promises and IDs retired/added in this revision.
```
