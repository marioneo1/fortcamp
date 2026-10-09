# Character-life authoring workflow

Planning/authoring tooling only. No importer or live story framework exists.

## What the user does

1. Upload [CHARACTER_LIFE_GPT_BRIEF.md](CHARACTER_LIFE_GPT_BRIEF.md) to a **fresh
   GPT chat**. The attachment contains the task and all needed references. If
   the interface needs a message, say only: `Run the attached brief.`
2. Return GPT's JSON file to Codex. A file produced by GPT is a draft, even if
   its self-review says it is correct.
3. Answer only consequential choices Codex cannot infer from already approved
   direction. Codex handles formatting, mechanical repairs, file organization,
   checks and updating the next upload bundle.

Current bundle requests **pilot 001 revision 3**, not a new pair of characters.
Revision 3 has now been received and structurally checked. The user delegated
the two choices: use a nonfinancial trust test and reserve the cap-bearing story
for one character per player. See the decision record in reviews. The concrete
trust scene still needs authoring. Do not resend the completed request; Codex
will prepare any next bounded task. No further user upload is needed now.
It includes revision 2 and its review; no other attachments are needed. Keep the
fresh chat for this batch; use a new chat for a subsequent independently prepared
bundle. Do not rely on GPT remembering another conversation.

## What Codex maintains

- `CHARACTER_STORY_AUTHORING_PROMPT.md`: reusable writing and handoff rules.
- `character-story-contract-v0.2.json`: current catalogue and authoring format.
- `CHARACTER_LIFE_CURRENT_REQUEST.md`: the single current task and its boundaries.
- `tools/build_character_life_brief.py`: packages those sources plus the selected
  revision submission/review into the upload file. Update selected source paths
  when advancing batches; do not accidentally repackage an obsolete task.
- `drafts/`: untouched submissions with explicit revisions. `reviews/`: findings,
  approvals and unresolved decisions. Content index: authoritative status links.

When preparing a new batch, replace the current request and selected inputs,
refresh the catalogue against canonical code, rebuild the bundle and check it.
The user's action remains one upload rather than assembling a prompt each time.
Instructions within generated stories are reference data, not authoring commands.

## Acceptance gates

1. **Received:** preserve the exact file. Parse JSON with duplicate-key rejection.
2. **Structurally checked:** run the offline checker against the prior submission:

   ```powershell
   .venv\Scripts\python.exe tools/validate_character_blueprints.py <returned-file> --baseline <previous-revision>
   ```

   It checks required blueprint sections, key types, canonical identity IDs,
   duplicate IDs, local references, routing endpoints and baseline ID/repeat-key
   preservation. It catches the 23 null regressions in revision 2. It is not a
   complete JSON Schema validator, conditional-flow proof or gameplay simulator.
3. **Design reviewed:** manually follow branches, prerequisites and recovery;
   inspect truthfulness, promised rewards, costs, one-off/cap interactions,
   coherent voice and actual engine capabilities. Structural success alone
   cannot advance a file to approved.
4. **Decisions resolved:** ask the user about new consequential mechanics or
   substantive story changes. Recommendations are explicit proposals. Routine
   corrections need no separate GPT round or user approval. Open decision_points
   are allowed in a clean draft; they block the affected approval.
5. **Approved:** register exact content/IDs and remaining dependencies. Approval
   is not implementation. Only then commission dialogue for those exact stages.
6. **Implemented:** integrate an authorized vertical slice, test persistence,
   repeat exclusion, outcomes and rewards before marking anything live.

Prefer local mechanical repairs in a new revision over asking the user to relay
repeated trivial correction prompts. Use GPT for substantive authoring/variation.
This current revision request also tests whether the stronger single-file prompt
can produce a reliable handoff in a fresh chat.

## Maintenance and validation

```powershell
.venv\Scripts\python.exe tools/build_character_life_brief.py
.venv\Scripts\python.exe tools/build_character_life_brief.py --check
.venv\Scripts\python.exe -m unittest tests.test_character_blueprint_authoring
```

Adding a race, Job, personality, tag, story or event requires catalogue/content
index review under AGENTS.md. Preserve retired IDs and player completion history.
New content must not silently reopen a one-off. Bump the contract for incompatible
format changes; additive review metadata does not make drafts executable.
