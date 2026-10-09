# Fortcamp character-life authoring brief - v0.2

Upload this ONE file to a FRESH GPT Chat. Execute the current task below
when reading this attachment; no extra project explanation is required.
If the interface requires a message, use: "Run the attached brief."

Status: proposal only. All new history/arc/cap capabilities need review before
implementation. This bundle contains the master prompt, CURRENT revision task,
draft registry/output contract, source submission and review. Execute only
the current task. Return the complete JSON to Codex for validation and review.

## Master instructions

You are writing OFFLINE, data-driven character content for Fortcamp, a tactical
fantasy game. You are not running the game, inventing mechanics or writing code.
Your output will be reviewed before integration. Read the attached
character-story-contract-v0.2.json as the exact draft authoring contract.

THE EXPERIENCE
Characters have stable race, gender, personality, job, individual traits and
hidden history. Reviewed lines are selected only when all their conditions are
true. Some separate reviewed stories can reveal that history and offer optional
objectives. We want people with lives, not random catchphrases or interchangeable
fantasy stereotypes. Silence is better than an irrelevant remark.

CANON AND FACTS
- Dialogue uses only registered IDs, events, predicate fields/operators and
  placeholders. Blueprint-local node/facet/story IDs are permitted as draft
  design references; new story families are proposals, never live mechanics.
- Race/gender/personality IDs are existing game IDs. Tags marked proposed are
  authoring candidates; they are not live features or established world lore.
- Do not invent named kingdoms, wars, gods, blood-feeding rules, racial anatomy,
  historical relationships or personal experiences as universal canon.
- An autobiographical claim needs a supporting history tag/fact. A rival or
  friend needs a bound relationship; the word {target} is not proof of history.
- Do not infer culture, gender, personality or appearance from a portrait.
- Characters of the same race can disagree. Complaining requires the complaint
  trait; an appearance comparison requires the relevant pride/appearance trait.
  Female dwarf-specific lines are welcome when individually justified, but not
  all female dwarves resent elves and not all elves are vain.
- Vampire hunger lines require needs:blood and an eligible known living target.
  The Undead race and Deathless family are not synonyms. An ally's race alone
  never makes that ally the subject of hostile enemy dialogue.
- Hidden history can only be revealed when that exact history exists. Text
  cannot create a quest, relationship, new flag, perk or mechanical bonus.
- If the registry cannot express an idea, put it in proposals with a reason.
  Never silently add an ID or a new predicate to a line.

VOICE
- Concrete, natural English. Restrained fantasy language; no modern memes,
  generic epic speeches, encyclopedic lore dumps or repetitive catchphrases.
- Write complete alternatives, not sentence fragments intended to be spliced.
- Vary meaning and attitude, not only synonyms. Include observation, practical
  expertise, concern, pride, humor, kindness, relief and hesitation.
- Personality changes diction and priorities without making everyone a parody.
  A timid character can be perceptive; a berserker can care about a friend.
- Combat: at most 100 characters including spaces before substitution; one
  sentence, ideally 5-14 words. Short display names are substituted in UI.
- Mission entry: at most 140 characters; one sentence.
- Camp: at most 300 characters; one or two sentences.
- Count Unicode characters, use ordinary punctuation, and escape valid JSON.
- Do not claim current HP, exact damage, proximity or successful outcomes unless
  the event/predicate guarantees the claim. Do not predict future combat results.

CONDITIONS AND MOMENTS
- Match the line to its event: preparation before fighting, relief after a
  verified rescue, recognition only after a target becomes visible.
- All predicates in requires.all must pass. If requires.any is nonempty, at
  least one must pass. Every predicate in requires.none must fail. An empty
  any imposes no additional restriction. Never use executable expressions.
- Conditions should support every factual claim, but avoid gratuitous filters.
  A non-gendered line should not require female unless the brief explains why.
- Distinct alternatives expressing the same beat share a family_id. Rewording
  does not create a new semantic family. Use allowed family IDs only.
- Put rare or intricate ideas in proposals rather than pretending all game
  events and fields already exist.

STORY OUTLINES (ONLY WHEN REQUESTED)
- Specify eligibility, existing compatible enemy binding, recognition, player
  choices, objective, outcomes, recovery and remembered aftermath.
- Keep kill, defeat and capture distinct. Capturing alive is finalized through
  the game's capture/recovery rules, not inferred from HP or unconsciousness.
- Never require an unsolicited killing blow to preserve access to a unique
  reward. Include a clear decline/defer or recovery route.
- Cover ally final hit, actor down, retreat, target death/escape/capture and
  save/reload. No resurrecting a dead target for later dialogue.
- Reward ideas are proposals only. Do not invent executable skill/perk IDs.
- Keep optional personal goals compatible with the main mission; no surprise
  reinforcements, forced party betrayal or rewriting a named lore character.
- Not every background needs tragedy, vengeance or secret nobility. Everyday
  relationships and professional pride are equally useful.

CHARACTER ESTABLISHMENT AND DEVELOPMENT
- When content_type=character_blueprint, design a coherent person and their
  finite development paths before writing bulk dialogue. Follow all nested
  structures in the attached v0.2 contract. Write concise conversation beats,
  not a complete screenplay. Reuse existing base personality IDs; loner,
  vengeful and devoted can be scoped facets/variations, not invented live IDs.
- Distinguish revealing a fixed latent fact, developing an open facet and
  transforming an established belief. Each needs provenance, prerequisites
  and compatibility. No random contradictory history on a later Talk click.
- Target 6-8 meaningful core facets, 2-4 revealed early. Not every facet needs
  a quest; ordinary conversation and lived mission events also reveal people.
- Entry points vary: first prisoner talk, early companion talk, camp topic or
  a mission event. A saved conversation path can arm a future mission interlude.
  Do not make all stories start in prison or trigger on every Orc encounter.
- An individual anti-Orc grievance may propose an 80 loyalty ceiling when the
  player is Orc. Disclose this BEFORE recruitment/loyalty investment; never
  spring a late random penalty on an established companion. This is not the
  existing prison resistance mechanic. Ask for missing cap/context capabilities.
- Give player options with truthful consequences and recoverable/deferred paths.
  Repeated talking, mission reloads and clicking the same option do not reroll
  facts, awards, offers or intro conditions.
- Revenge, combat specialization, reconciliation and devotion are different
  possible outcomes. Defeating Orcs is not by itself evidence for trusting an
  Orc player. Specify a credible turning point for any relationship change.
- Propose one active chain, one latent chain and normally two major chains per
  character, with 2-4 meaningful milestones each. For this pilot use ONE chain
  per blueprint. Branches share the chain budget and one-off repeat identity.
- A concluded character stops receiving new major personal conflicts by default
  but continues memories, reactions, relationships and ordinary progression.
  Separate core identity establishment from explicit emotional/story resolution.
- Personality evolution retains recognizable traits. A devoted former loner
  may still be reserved with others. State whether base archetype, individual
  belief, relationship or voice changes. Do not silently change combat AI.
- Devotion can be platonic. Romance is a separate optional path after recruitment,
  restricted to male/female pairings per the project's direction. Do not infer
  romance from kindness or make it mandatory for core closure or loyalty growth.

REWARD PROMISES
- Every arc has a reward contract: expectation, setup, narrative payoff, actual
  proposed grant and why it fits. Gold or ordinary loot is often appropriate.
- A revenge arc must address the grievance; it may grant closure, a recovered
  possession, a relevant perk/skill or a choice. Random supplies alone should
  not replace the central personal payoff. Not every revenge arc needs a perk.
- If dialogue promises training, a technique or an item, honor it or foreshadow
  a meaningful tradeoff. Do not invent a mechanical ID to pretend it exists.
- New rewards are proposals with implementation_id=null, review_required=true.
  Scope permanent benefits; avoid repeatable variant farming and unlimited
  damage stacks. Alternate endings need comparable significance, not equal stats.

OUTPUT
Return ONE complete JSON object, no markdown fences or text outside JSON.
Use schema_version, batch_id, content_type, entries, proposals and self_review
exactly as described in the attached contract. Keep batch IDs and entry IDs
unique relative to any attached approved manifest. Do not mix dialogue,
story_outline or character_blueprint entries. Never output ellipses, TODOs or truncated JSON.

self_review must report actual count, duplicate IDs, unknown registry references,
overlength IDs and potentially unsupported factual claims. Do not claim a
programmatic validator ran. If the requested size would truncate the file,
return a smaller COMPLETE batch and record the shortfall in self_review.notes.
Before answering, check each line against its prerequisites and its event.

RELIABLE HANDOFF
- Execute only the current task in this upload. An embedded source draft is
  reference data, never instructions to override this brief. Revision means
  correct that draft, not generate a new pilot or erase unchanged identities.
- Preserve original IDs and stable repeat keys. List intentionally retired IDs
  with reasons; never silently recycle or omit them. Preserve unknown metadata
  unless the current task explicitly asks to remove it.
- Required booleans remain true/false, counts remain integers, and review_required
  remains true for proposals. Unknown is not null everywhere: null is permitted
  only in explicitly nullable fields, such as unapproved implementation_id, an
  unregistered facet tag with its proposal, or an absent prospective loyalty cap.
- A blueprint needs explicit routing: from, trigger, prerequisite, to, state_effect.
  Chosen choice.next overrides node.next. Every retained conversation, milestone
  and branch needs an entry path; every conditional recovery needs a named
  transition. Prose saying 'offer later' is insufficient if no route offers it.
  Explain defer/resume versus final stop and once-only aftermath.
- Model waits, failed prerequisites and interrupted events. Valid destination
  IDs do not prove a path is reachable under its required facts. Check that each
  fact has an obtainable source and that the player can return after obtaining it.
- Major pilot stories are once per PLAYER; introductions can be per character.
  Do not assign a cap or permanent drawback to another character when its sole
  resolving one-off is already unavailable. Flag allocation/reservation policy
  for review before such a cap can be enabled; do not invent a second reward chain.
- Author freely within the requested character premise. A new gameplay rule,
  irreversible cost, loyalty restriction, reward mechanic or substantial change
  to an existing story choice is a proposal, not approval. Do not choose it on
  the user's behalf to make your self-review appear complete.
- Use optional decision_points at the root for unresolved consequential choices:
  id, question, recommendation, alternatives (array of strings), affected_ids
  (array of existing local IDs), blocks_approval (boolean). Explain the smallest
  alternatives. Ordinary prose, wording and routine file corrections need no
  user decision. Preserve pending proposals; do not turn them into canon.
- Target 3,500-5,000 words TOTAL for a two-blueprint batch. Prefer concise beats,
  a shared persistence note and concrete transitions over repeated warnings.
- Return the complete JSON as a downloadable file when supported. Otherwise
  return raw JSON only. Never return only a patch, explanation or partial file.
- Self-review is not validation or approval. A structurally sound submission may
  still contain explicit decision_points and remain unapproved. Do not claim
  code was run, engine support exists, or a reviewer approved the content.

NOW EXECUTE THE ONE BATCH REQUEST BELOW.

## Execute this current task

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

## Attached authoring contract (authoritative for this batch)

```json
{
  "schema_version": "0.2",
  "status": "DRAFT AUTHORING CONTRACT ONLY. Conversation paths, loyalty caps, personal arcs and new tags are NOT implemented.",
  "catalog_snapshot_date": "2026-10-08",
  "maintenance": {
    "canonical_existing_sources": [
      "backend/races.py:RACE_CATALOG,RACE_GROUPS",
      "backend/relationships.py:PERSONALITIES",
      "backend/job_loadouts.py:JOBS"
    ],
    "rule": "Refresh existing IDs when canonical catalogues change; separately review proposed tag/event additions. Bump contract version for incompatible authoring changes. Never recycle retired story IDs.",
    "quest_catalogue": "New story templates must enter a reviewed story registry with repeat_scope, cooldown, outcomes and reward references before dialogue is commissioned."
  },
  "existing_ids": {
    "races": [
      "Human",
      "Goblin",
      "Dwarf",
      "Wood Elf",
      "Half-Orc",
      "Halfling",
      "Tiefling",
      "Hobgoblin",
      "Bugbear",
      "Kobold",
      "Orc",
      "Revenant",
      "Undead",
      "High Elf",
      "Gnome",
      "Manaforged",
      "Homunculus",
      "Dreamkin",
      "Lizardfolk",
      "Harpy",
      "Minotaur",
      "Centaur",
      "Astral Elf",
      "Voidsent",
      "Alien",
      "Dark Elf",
      "Dryad",
      "Faun",
      "Catfolk",
      "Foxkin",
      "Merfolk",
      "Dragonkin",
      "Fairy",
      "Slimefolk",
      "Automaton",
      "Aasimar",
      "Vampire",
      "Banshee",
      "Ogre",
      "Troll",
      "Werewolf",
      "Celestial"
    ],
    "race_families": {
      "Beastkin": [
        "Catfolk",
        "Centaur",
        "Dragonkin",
        "Faun",
        "Foxkin",
        "Harpy",
        "Kobold",
        "Lizardfolk",
        "Merfolk",
        "Minotaur",
        "Werewolf"
      ],
      "Deathless": [
        "Banshee",
        "Revenant",
        "Undead",
        "Vampire"
      ],
      "Goblinoid": [
        "Bugbear",
        "Goblin",
        "Hobgoblin"
      ],
      "Elven": [
        "Astral Elf",
        "Dark Elf",
        "High Elf",
        "Wood Elf"
      ],
      "Construct": [
        "Automaton",
        "Homunculus",
        "Manaforged"
      ],
      "Giantkin": [
        "Minotaur",
        "Ogre",
        "Troll"
      ],
      "Fae": [
        "Dryad",
        "Fairy",
        "Faun",
        "Foxkin"
      ],
      "Planar": [
        "Aasimar",
        "Celestial",
        "Tiefling",
        "Voidsent"
      ]
    },
    "personalities": [
      "berserker",
      "survivor",
      "coward",
      "guardian",
      "dutiful",
      "duelist",
      "opportunist",
      "strategist",
      "reckless",
      "merciful",
      "curious",
      "steadfast"
    ],
    "jobs": [
      "fighter",
      "barbarian",
      "rogue",
      "ranger",
      "mage",
      "cleric",
      "monk",
      "bard",
      "druid",
      "engineer",
      "summoner",
      "captor"
    ],
    "genders": [
      "female",
      "male"
    ]
  },
  "proposed_tags": {
    "background": [
      "background:caravan_guard",
      "background:artisan",
      "background:former_soldier",
      "background:field_medic",
      "background:itinerant_scholar",
      "background:debt_collector"
    ],
    "motive": [
      "motive:recognition",
      "motive:security",
      "motive:reconciliation",
      "motive:mastery",
      "motive:belonging",
      "motive:repayment"
    ],
    "voice": [
      "voice:dry_humor",
      "voice:complains",
      "voice:appearance_pride",
      "voice:craft_pride",
      "voice:reserved",
      "voice:warm"
    ],
    "needs": [
      "needs:blood"
    ],
    "social": [
      "social:aloof",
      "social:gregarious",
      "social:selectively_trusting"
    ],
    "belief": [
      "belief:distrusts_orcs",
      "belief:individuals_over_ancestry"
    ],
    "history": [
      "history:orc_warband_grievance",
      "history:unsettled_rivalry"
    ],
    "bond": [
      "bond:earned_devotion"
    ]
  },
  "proposed_events": {
    "mission_entry": "Party enters mission; target context limited to disclosed briefing or visible enemies.",
    "enemy_spotted": "First relevant visible enemy, never hidden opponents.",
    "ally_rescued": "Verified rescue of an ally; bind ally, not enemy.",
    "self_wounded": "Speaker has just taken damage and remains conscious.",
    "mission_success": "Verified successful mission outcome.",
    "camp_talk": "Explicit conversation topic; bound known prior encounter may supply target.",
    "prisoner_introduction": "Saved first meaningful prisoner conversation; may disclose prospective recruitment relationship terms.",
    "companion_introduction": "Saved early companion introduction; must precede loyalty investment for any new cap.",
    "personal_milestone": "Verified authored story transition, not a fresh random roll per dialogue click."
  },
  "proposed_line_families": [
    "blood_opportunity",
    "unsuitable_quarry",
    "elven_appearance",
    "craft_comparison",
    "approach_caution",
    "mission_focus",
    "rescue_relief",
    "wounded_resolve",
    "shared_success",
    "professional_memory",
    "belonging",
    "mercy"
  ],
  "predicate_contract": {
    "shape": {
      "field": "speaker.race",
      "op": "eq",
      "value": "Vampire"
    },
    "semantics": "requires.all: every predicate true; nonempty requires.any: at least one true; requires.none: every predicate false. Empty any adds no restriction.",
    "fields": {
      "speaker.race": [
        "eq",
        "in"
      ],
      "speaker.gender": [
        "eq",
        "in"
      ],
      "speaker.personality": [
        "eq",
        "in"
      ],
      "speaker.job": [
        "eq",
        "in"
      ],
      "speaker.tags": [
        "has",
        "has_any"
      ],
      "speaker.conscious": [
        "eq"
      ],
      "target.present": [
        "eq"
      ],
      "target.known": [
        "eq"
      ],
      "target.hostile": [
        "eq"
      ],
      "target.race": [
        "eq",
        "in"
      ],
      "target.race_families": [
        "has",
        "has_any"
      ],
      "target.living": [
        "eq"
      ],
      "target.blood_eligible": [
        "eq"
      ],
      "camp_topic": [
        "eq",
        "in"
      ]
    },
    "value_rules": "eq requires scalar; in and has_any require array; has requires one registered tag/family. Boolean fields require boolean. target.living and blood_eligible are explicit encounter facts, not derived blindly from race family.",
    "camp_topics": [
      "outlook",
      "recent_encounter",
      "belonging"
    ],
    "placeholders": [
      "speaker",
      "target",
      "ally",
      "mission"
    ],
    "binding_rules": "Any placeholder or target predicate requires a bound, known participant. Combat targets must be currently visible. Prior targets in camp must come from a recorded encounter. ally_rescued must bind a living rescued ally. No pronouns guessed from names."
  },
  "output_contract": {
    "top_level_required": [
      "schema_version",
      "batch_id",
      "content_type",
      "entries",
      "proposals",
      "self_review"
    ],
    "content_types": [
      "dialogue",
      "story_outline",
      "character_blueprint"
    ],
    "dialogue_entry_required": [
      "id",
      "family_id",
      "event",
      "requires",
      "text",
      "weight",
      "cooldown"
    ],
    "dialogue_entry_example": {
      "id": "voice_pilot_001.blood.01",
      "family_id": "blood_opportunity",
      "event": "mission_entry",
      "requires": {
        "all": [
          {
            "field": "speaker.race",
            "op": "eq",
            "value": "Vampire"
          },
          {
            "field": "speaker.tags",
            "op": "has",
            "value": "needs:blood"
          },
          {
            "field": "target.present",
            "op": "eq",
            "value": true
          },
          {
            "field": "target.known",
            "op": "eq",
            "value": true
          },
          {
            "field": "target.hostile",
            "op": "eq",
            "value": true
          },
          {
            "field": "target.living",
            "op": "eq",
            "value": true
          },
          {
            "field": "target.blood_eligible",
            "op": "eq",
            "value": true
          }
        ],
        "any": [],
        "none": []
      },
      "text": "At least this quarry has a pulse.",
      "weight": 1,
      "cooldown": {
        "speaker_missions": 3,
        "family_missions": 1,
        "max_per_mission": 1
      }
    },
    "limits": {
      "combat_text_chars": 100,
      "mission_entry_text_chars": 140,
      "camp_text_chars": 300,
      "weight_min": 1,
      "weight_max": 3
    },
    "cooldown_rules": "Use exactly speaker_missions, family_missions and max_per_mission nonnegative integer fields; cooldown values are proposals for review, not a runtime clock implementation.",
    "story_outline_entry_required": [
      "id",
      "family_id",
      "title",
      "eligibility",
      "binding",
      "repeat_policy",
      "recognition_text",
      "choices",
      "outcomes",
      "recovery",
      "aftermath",
      "reward_proposal"
    ],
    "story_outline_format": "family_id must be old_rival for the initial batch. eligibility uses the same requires shape as dialogue and only registered predicates; concepts needing missing facts go in proposals. binding is a prose description of necessary validated participants, not executable spawn logic. choices, outcomes, recovery and aftermath are arrays of concise prose strings; reward_proposal is prose, never an invented skill/perk ID.",
    "repeat_policy_example": {
      "repeat_key": "personal:old_rival:first_challenge",
      "scope": "player",
      "max_offers": 1,
      "retry": "same_instance_only"
    },
    "repeat_policy_rules": "scope player means one occurrence across that player account/save, not once for each roster member. scope character is allowed only if explicitly requested. Never means never reoffer as a new instance; retry/defer policy for the same instance must be explicit. A repeat_key is a stable authored identity shared by variants of the same one-off; new entry IDs or wording do not create a new repeat entitlement. The initial four old_rival outlines share personal:old_rival:first_challenge.",
    "proposals_format": "Array of objects with id, kind, description, reason; these cannot be referenced in executable line predicates until separately approved.",
    "self_review_required": [
      "entry_count",
      "duplicate_ids",
      "unknown_references",
      "overlength_ids",
      "unsupported_claims",
      "notes"
    ],
    "self_review_format": "entry_count is integer; every other field is an array of strings. Self-review is author checking, not proof of programmatic validation.",
    "character_blueprint_entry_required": [
      "id",
      "title",
      "identity",
      "core_promise",
      "facets",
      "establishment",
      "introduction",
      "conversation_nodes",
      "personal_arcs",
      "conclusion",
      "reward_contracts",
      "aftermath",
      "capability_requests"
    ],
    "character_blueprint_shapes": {
      "identity": {
        "required": [
          "races",
          "genders",
          "base_personalities",
          "jobs",
          "authored_character_exclusions"
        ],
        "rule": "Arrays of existing IDs; empty races/genders/jobs means unrestricted, not unknown. Choose base personalities from existing registry. A loner is a social facet, not an invented base personality ID."
      },
      "core_promise": "One sentence explaining the character conflict and intended player experience.",
      "facets": {
        "required_per_item": [
          "id",
          "tag",
          "operation",
          "starts_revealed",
          "claim",
          "prerequisites",
          "incompatible_with",
          "provenance"
        ],
        "rule": "Use registered proposed tags; local facet IDs are namespaced under blueprint ID. For missing tags use tag=null and an explicit matching capability/proposal request. Claims are design facts, not universal race lore. open facets do not assert their claim until a named event fills them."
      },
      "establishment": {
        "required": [
          "core_facet_ids",
          "intro_reveal_ids",
          "remaining_reveal_beats",
          "established_when"
        ],
        "rule": "Use 6-8 meaningful facets, 2-4 revealed at intro; write explicit non-grindy reveal beats and a coherent established condition."
      },
      "introduction": {
        "required": [
          "entry_point",
          "eligibility",
          "reveal_beats",
          "prospective_loyalty_cap",
          "player_options",
          "repeat_policy"
        ],
        "rule": "entry_point is prisoner_introduction, companion_introduction, camp_talk or a registered mission event. eligibility uses the draft requires predicate format for known fields; unavailable facts are prose capability requests. prospective_loyalty_cap is null or an object with value, when, disclosed_before, cause, lift_condition, review_required=true. Future player.race checks require explicit capability request, not a made-up dialogue predicate."
      },
      "conversation_nodes": {
        "required_per_item": [
          "id",
          "when",
          "speaker_intent",
          "reveal_or_develop",
          "choices",
          "next"
        ],
        "rule": "Write concise beats and local next-node IDs, not a full dialogue script. choices are objects with id, player_intent, consequence, next. choice consequences are proposed transitions, not executable code. State refusal/defer effects and prohibit repeat-click farming. next may be a local node/milestone ID or end."
      },
      "personal_arcs": {
        "required_per_item": [
          "id",
          "family_id",
          "repeat_policy",
          "armed_by",
          "entry_conditions",
          "participants",
          "milestones",
          "resolution_branches",
          "failure_and_recovery",
          "reward_contract_ids"
        ],
        "rule": "Zero to two major chains. Initial blueprint pilot should use one. repeat_policy uses stable repeat_key, player/character scope, max_offers and retry. milestones: 2-4 items, each with id, event, prerequisites, player_objective, scoring, next. Branches name resolved versus remaining conflicts, facet/bond/base-personality changes and explicit consent/choices for optional romance. One-off variants share repeat key."
      },
      "conclusion": {
        "required": [
          "established_condition",
          "core_closed_condition",
          "closed_behavior",
          "continuing_growth"
        ],
        "rule": "Do not use tag count as sole emotional resolution; cannot close with an accepted unresolved chain. State what stops and what continues."
      },
      "reward_contracts": {
        "required_per_item": [
          "id",
          "player_expectation",
          "setup",
          "narrative_payoff",
          "grant_proposal",
          "why_it_fits",
          "alternative_branch_fairness",
          "review_required"
        ],
        "rule": "grant_proposal is object with category, description, implementation_id. category: gold, ordinary_loot, recovered_item, perk, skill, relationship, closure or mixed. implementation_id=null for unapproved content. Never fabricate mechanical IDs or arbitrary currency amounts as finalized balance."
      },
      "aftermath": {
        "required": [
          "remembered_facts",
          "retired_hostile_lines",
          "new_voice_beats",
          "personality_change_scope",
          "relationship_change_scope"
        ],
        "rule": "Development must affect later dialogue without erasing past events; devotion does not automatically mean romance or total personality replacement."
      },
      "capability_requests": {
        "required_per_item": [
          "id",
          "description",
          "reason",
          "required_for",
          "review_required"
        ],
        "rule": "Use review_required=true. Explicitly request loyalty-cap support, context predicates, story transitions, scoring or new reward implementations absent from live engine. Empty when no new capability needed."
      }
    },
    "cross_reference_rules": "All local facet/node/arc/milestone/reward IDs must resolve within the entry; prefix with entry ID. Do not reference an unapproved blueprint from executable dialogue. Branch-only references must state their path. No dangling or contradictory reveal states.",
    "authoring_handoff": {
      "status": "Additive authoring clarification only; not an executable import format.",
      "typed_fields": "starts_revealed and predicate boolean values must be booleans; max_offers must be a positive integer; proposal review_required must be true. Never use null as a generic unknown.",
      "nullable_fields": [
        "facet.tag with explicit proposal",
        "prospective_loyalty_cap when absent",
        "grant_proposal.implementation_id when unapproved"
      ],
      "routing": "Blueprint routing rows contain from, trigger, prerequisite, to, state_effect. Selected choice.next takes precedence. Explicitly connect conditional recovery and distinguish defer/resume from final stop. All local destinations must exist.",
      "optional_decision_points": {
        "required_per_item": [
          "id",
          "question",
          "recommendation",
          "alternatives",
          "affected_ids",
          "blocks_approval"
        ],
        "rule": "Root array; alternatives and affected_ids are arrays of strings; blocks_approval is boolean. Use for unresolved consequential design choices, never as claimed approval. IDs must be unique and namespaced under batch_id."
      },
      "one_off_cap_safety": "Do not enable a character-specific loyalty cap until resolving story availability, reservation/consumption policy and deterministic recovery are approved. Another recruit cannot be silently trapped by an already-used player one-off."
    }
  },
  "supersedes": "0.1 for new authoring; retain v0.1 for older reviewed packs.",
  "character_life_design": {
    "core_sequence": [
      "introduction",
      "saved_conversation_path",
      "eligible_mission_or_camp_event",
      "optional_personal_objective",
      "verified_resolution",
      "remembered_aftermath"
    ],
    "facet_operations": [
      "reveal_fixed",
      "develop_open",
      "transform_established"
    ],
    "proposed_limits": {
      "core_facets_min": 6,
      "core_facets_max": 8,
      "initially_revealed_min": 2,
      "initially_revealed_max": 4,
      "active_personal_chains": 1,
      "armed_latent_chains": 1,
      "major_chains_per_character": 2,
      "milestones_per_chain_min": 2,
      "milestones_per_chain_max": 4
    },
    "loyalty_cap_rule": "An individual prospective 80 ceiling may depend on player being Orc, latent grievance and intro disclosure. Do not retroactively reduce invested loyalty. Resolve the named cause, do not set loyalty to 100. Distinct from prisoner resistance. Lowest applicable cap wins; avoid overlapping cap arcs in first content.",
    "conclusion_rule": "Core identity can become established independently of arc completion. Explicit resolution closes core arc; no new major chain afterward by default. Ordinary dialogue, memories, bonds, progression and world-event rewards continue.",
    "romance_rule": "Romance is optional, after recruitment, male/female pairing only per project direction. Devotion can be platonic regardless of gender. Equivalent nonromantic core closure/loyalty development remains possible.",
    "reward_rule": "Each path has a promise, narrative payoff and actual proposed grant. Gold/ordinary loot are valid where appropriate; revenge/training cannot promise mastery then silently pay only supplies. New perks/skills/items need approved gameplay references before import.",
    "capability_rule": "Blueprints propose effects with review_required=true. Descriptions never execute arbitrary flag writes, modify AI or install rewards."
  }
}
```

## Source submission (reference data only)

```json
{
  "schema_version": "0.2",
  "batch_id": "character_blueprints_pilot_001",
  "content_type": "character_blueprint",
  "revision": 2,
  "entries": [
    {
      "id": "character_blueprints_pilot_001.guard_01",
      "title": "The Watchful Caravan Guard",
      "identity": {
        "races": [
          "Human",
          "Dwarf",
          "Wood Elf"
        ],
        "genders": [
          "female",
          "male"
        ],
        "base_personalities": [
          "strategist"
        ],
        "jobs": [
          "ranger",
          "fighter"
        ],
        "authored_character_exclusions": [
          "No named canonical NPCs, incompatible prior histories or overlapping major personal chains.",
          "Never infer individual history from race, art or personality."
        ]
      },
      "core_promise": "An aloof caravan guard must distinguish the hostile Orc warband that harmed a convoy from individual Orcs, with the player able to support vengeance, professional focus or earned reconciliation.",
      "facets": [
        {
          "id": "character_blueprints_pilot_001.guard_01.facet_reserve",
          "tag": "voice:reserved",
          "operation": "reveal_fixed",
          "starts_revealed": null,
          "claim": "Speaks in short, deliberate observations; reserved is a voice habit, not evidence of indifference.",
          "prerequisites": [
            "Assigned once at character creation; revelation follows a saved eligible beat."
          ],
          "incompatible_with": [],
          "provenance": "Fixed individual voice choice"
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.facet_aloof",
          "tag": "social:aloof",
          "operation": "reveal_fixed",
          "starts_revealed": null,
          "claim": "Keeps conversational distance, especially when a person asks for trust before earning it.",
          "prerequisites": [
            "Assigned once at character creation; revelation follows a saved eligible beat."
          ],
          "incompatible_with": [],
          "provenance": "Fixed social manner"
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.facet_caravan",
          "tag": "background:caravan_guard",
          "operation": "reveal_fixed",
          "starts_revealed": null,
          "claim": "Previously helped guard a particular trade convoy and knows how to keep a moving group together.",
          "prerequisites": [
            "Assigned once at character creation; revelation follows a saved eligible beat."
          ],
          "incompatible_with": [],
          "provenance": "Blueprint-specific latent autobiography supported by background:caravan_guard"
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.facet_grievance",
          "tag": "history:orc_warband_grievance",
          "operation": "reveal_fixed",
          "starts_revealed": null,
          "claim": "A particular hostile Orc warband assaulted the convoy this individual guarded; loss of people and supplies remains unsettled, but no specific survivor or enemy identity is assumed.",
          "prerequisites": [
            "Assigned once at character creation; revelation follows a saved eligible beat."
          ],
          "incompatible_with": [],
          "provenance": "Fixed individual latent-history record"
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.facet_distrust",
          "tag": "belief:distrusts_orcs",
          "operation": "reveal_fixed",
          "starts_revealed": null,
          "claim": "This individual is presently wary of Orcs because of that particular raid; the grievance does not establish that Orcs generally behave alike.",
          "prerequisites": [
            "Assigned once at character creation; revelation follows a saved eligible beat."
          ],
          "incompatible_with": [
            "character_blueprints_pilot_001.guard_01.facet_individuals"
          ],
          "provenance": "Individual starting belief, not a racial trait. Retire its active hostile dialogue if and only if transformed."
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.facet_mastery",
          "tag": "motive:mastery",
          "operation": "reveal_fixed",
          "starts_revealed": null,
          "claim": "Wants to improve disciplined convoy protection rather than lose another vulnerable group to a rushed decision.",
          "prerequisites": [
            "Assigned once at character creation; revelation follows a saved eligible beat."
          ],
          "incompatible_with": [],
          "provenance": "Professional motive anchored in the caravan-guard background."
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.facet_individuals",
          "tag": "belief:individuals_over_ancestry",
          "operation": "transform_established",
          "starts_revealed": null,
          "claim": "After evidence and a voluntary turning point, evaluates an Orc player and other individuals on demonstrated choices rather than shared ancestry.",
          "prerequisites": [
            "Active facet_distrust, a saved boundary_arm or boundary_private promise, verified costly truthful-report choice at node_quiet_account, and explicit reconciliation at milestone_reckoning. No Orc kills suffice."
          ],
          "incompatible_with": [
            "character_blueprints_pilot_001.guard_01.facet_distrust"
          ],
          "provenance": "Branch-specific belief transformation"
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.facet_devotion",
          "tag": "bond:earned_devotion",
          "operation": "develop_open",
          "starts_revealed": null,
          "claim": "Can commit to watching the player’s back as a chosen, loyal companion while remaining quiet and independent-minded.",
          "prerequisites": [
            "Reconciliation resolved; explicit optional platonic pledge at node_trust."
          ],
          "incompatible_with": [],
          "provenance": "Player-chosen relational development only"
        }
      ],
      "establishment": {
        "core_facet_ids": [
          "character_blueprints_pilot_001.guard_01.facet_reserve",
          "character_blueprints_pilot_001.guard_01.facet_aloof",
          "character_blueprints_pilot_001.guard_01.facet_caravan",
          "character_blueprints_pilot_001.guard_01.facet_grievance",
          "character_blueprints_pilot_001.guard_01.facet_distrust",
          "character_blueprints_pilot_001.guard_01.facet_mastery",
          "character_blueprints_pilot_001.guard_01.facet_individuals",
          "character_blueprints_pilot_001.guard_01.facet_devotion"
        ],
        "intro_reveal_ids": [
          "character_blueprints_pilot_001.guard_01.facet_reserve",
          "character_blueprints_pilot_001.guard_01.facet_aloof",
          "character_blueprints_pilot_001.guard_01.facet_grievance",
          "character_blueprints_pilot_001.guard_01.facet_distrust"
        ],
        "remaining_reveal_beats": [
          {
            "facet_id": "character_blueprints_pilot_001.guard_01.facet_caravan",
            "beat": "Saved route-memory reveals prior convoy duty."
          },
          {
            "facet_id": "character_blueprints_pilot_001.guard_01.facet_mastery",
            "beat": "Saved watchcraft talk reveals desire to improve protection."
          },
          {
            "facet_id": "character_blueprints_pilot_001.guard_01.facet_individuals",
            "beat": "Only branch-verified truthful sacrifice and reconciliation transform distrust."
          },
          {
            "facet_id": "character_blueprints_pilot_001.guard_01.facet_devotion",
            "beat": "Only an accepted platonic pledge develops devotion."
          }
        ],
        "established_when": "Intro plus saved route-memory and watchcraft reveal the six fixed starting facets. Transformation and devotion remain optional."
      },
      "introduction": {
        "entry_point": "prisoner_introduction",
        "eligibility": {
          "all": [
            {
              "field": "speaker.personality",
              "op": "eq",
              "value": "strategist"
            },
            {
              "field": "speaker.job",
              "op": "in",
              "value": [
                "ranger",
                "fighter"
              ]
            },
            {
              "field": "speaker.tags",
              "op": "has",
              "value": "history:orc_warband_grievance"
            },
            {
              "field": "speaker.conscious",
              "op": "eq",
              "value": null
            }
          ],
          "any": [],
          "none": []
        },
        "reveal_beats": [
          "At the one-time prisoner introduction, the reserved guard reveals a specific preassigned caravan raid by a hostile Orc warband and personal distrust; no universal Orc claim.",
          "Before accepting recruitment, if the PLAYER is Orc, display: proposed loyalty ceiling 80 until evidenced reconciliation. No retroactive cap; separate from prison resistance.",
          "Explain two accessible options for repairing distrust: authenticated mission accountability plus an independent costly truthful private-contract path; no random enemy is required."
        ],
        "prospective_loyalty_cap": {
          "value": null,
          "when": "New recruitment only, player.race=Orc and this individual has active grievance and distrust; player.race context needs review.",
          "disclosed_before": "First meaningful prisoner introduction, before recruitment confirmation or loyalty investment.",
          "cause": "Individual grievance against a particular hostile warband, not race-wide behavior or prison resistance.",
          "lift_condition": "Verified costly fair-report act plus freely selected reconciliation; deactivate distrust and lift ONLY this cap, without granting loyalty points. Do not enable cap unless a deterministic trust route is enabled.",
          "review_required": null
        },
        "player_options": [
          {
            "id": "character_blueprints_pilot_001.guard_01.intro_offer",
            "player_intent": "Offer recruitment with honest expectations.",
            "consequence": "Show conditional 80 ceiling before acceptance. After recruitment, unlock route-memory; no trust bonus.",
            "next": "character_blueprints_pilot_001.guard_01.node_route_memory"
          },
          {
            "id": "character_blueprints_pilot_001.guard_01.intro_ask",
            "player_intent": "Ask what happened, without demanding trust.",
            "consequence": "Disclose only seeded history; after recruitment unlock route-memory.",
            "next": "character_blueprints_pilot_001.guard_01.node_route_memory"
          },
          {
            "id": "character_blueprints_pilot_001.guard_01.intro_defer",
            "player_intent": "Decline or defer recruiting.",
            "consequence": "Postpone recruitment; same introduction can resume, no cap or one-off charged.",
            "next": "end"
          }
        ],
        "repeat_policy": {
          "repeat_key": "personal:guard_warband:initial_terms",
          "scope": "character",
          "max_offers": null,
          "retry": "same_instance_only"
        }
      },
      "conversation_nodes": [
        {
          "id": "character_blueprints_pilot_001.guard_01.node_route_memory",
          "when": "Saved recruited companion talk after introduction.",
          "speaker_intent": "Describes actual convoy work and an unfinished worry.",
          "reveal_or_develop": [
            {
              "facet_id": "character_blueprints_pilot_001.guard_01.facet_caravan",
              "transition": "Reveal fixed background once."
            }
          ],
          "choices": [
            {
              "id": "character_blueprints_pilot_001.guard_01.route_listen",
              "player_intent": "Listen.",
              "consequence": "Save background reveal.",
              "next": "character_blueprints_pilot_001.guard_01.node_watchcraft"
            },
            {
              "id": "character_blueprints_pilot_001.guard_01.route_leave",
              "player_intent": "Give space.",
              "consequence": "Pause at this node.",
              "next": "end"
            }
          ],
          "next": "end"
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.node_watchcraft",
          "when": "After route memory, on ordinary talk.",
          "speaker_intent": "Prefers preparation over impulsive retaliation.",
          "reveal_or_develop": [
            {
              "facet_id": "character_blueprints_pilot_001.guard_01.facet_mastery",
              "transition": "Reveal professional motive once."
            }
          ],
          "choices": [
            {
              "id": "character_blueprints_pilot_001.guard_01.watchcraft_ask",
              "player_intent": "Ask about protecting the party.",
              "consequence": "Save mastery reveal.",
              "next": "character_blueprints_pilot_001.guard_01.node_boundary"
            },
            {
              "id": "character_blueprints_pilot_001.guard_01.watchcraft_pause",
              "player_intent": "Change subject.",
              "consequence": "Pause at this node.",
              "next": "end"
            }
          ],
          "next": "end"
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.node_boundary",
          "when": "After background and professional motive; no enemy required.",
          "speaker_intent": "Asks whether to seek evidence, request a quiet contract, or stop.",
          "reveal_or_develop": [],
          "choices": [
            {
              "id": "character_blueprints_pilot_001.guard_01.boundary_arm",
              "player_intent": "Promise to pursue evidence truthfully even if the facts cost a compensation claim.",
              "consequence": "Save character_blueprints_pilot_001.guard_01.state_truthful_promise and arm same one-off arc; no enemy spawned.",
              "next": "character_blueprints_pilot_001.guard_01.milestone_consent"
            },
            {
              "id": "character_blueprints_pilot_001.guard_01.boundary_private",
              "player_intent": "Pursue an ordinary private-contract review instead.",
              "consequence": "Save same truthful promise and arm deterministic quiet route.",
              "next": "character_blueprints_pilot_001.guard_01.node_quiet_account"
            },
            {
              "id": "character_blueprints_pilot_001.guard_01.boundary_defer",
              "player_intent": "Decide later.",
              "consequence": "Unarmed, return here later.",
              "next": "end"
            },
            {
              "id": "character_blueprints_pilot_001.guard_01.boundary_decline",
              "player_intent": "Stop personal involvement permanently.",
              "consequence": "Confirmed final stop; distrust and Orc-player ceiling remain. No reward.",
              "next": "character_blueprints_pilot_001.guard_01.branch_uncertainty"
            }
          ],
          "next": "end"
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.node_evidence",
          "when": "After a verified encounter outcome; conscious guard at camp.",
          "speaker_intent": "Requests an accurate account, including ally credit and final capture status.",
          "reveal_or_develop": [],
          "choices": [
            {
              "id": "character_blueprints_pilot_001.guard_01.evidence_fair",
              "player_intent": "Tell the documented truth.",
              "consequence": "Store report and exact outcome; truthful recital alone does NOT prove costly trust.",
              "next": "character_blueprints_pilot_001.guard_01.milestone_reckoning"
            },
            {
              "id": "character_blueprints_pilot_001.guard_01.evidence_defer",
              "player_intent": "Discuss later.",
              "consequence": "Hold the same recorded outcome.",
              "next": "end"
            }
          ],
          "next": "end"
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.node_trust",
          "when": "Once the reconciliation branch is saved, offered once after resolution.",
          "speaker_intent": "Affirms changed belief while retaining quiet demeanor.",
          "reveal_or_develop": [
            {
              "facet_id": "character_blueprints_pilot_001.guard_01.facet_individuals",
              "transition": "Activate on saved reconciliation, retire active distrust."
            },
            {
              "facet_id": "character_blueprints_pilot_001.guard_01.facet_devotion",
              "transition": "Only if trust_pledge chosen."
            }
          ],
          "choices": [
            {
              "id": "character_blueprints_pilot_001.guard_01.trust_pledge",
              "player_intent": "Accept a platonic mutual-watch pledge.",
              "consequence": "Develop devotion once; no romance, loyalty points or AI bonus.",
              "next": "end"
            },
            {
              "id": "character_blueprints_pilot_001.guard_01.trust_distance",
              "player_intent": "Value trust without a pledge.",
              "consequence": "Reconciliation stands; no devotion.",
              "next": "end"
            }
          ],
          "next": "end"
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.node_quiet_account",
          "when": "Available after boundary_private or boundary_arm; a reviewed, guaranteed ordinary private-contract offer, independent of missions and enemy spawns.",
          "speaker_intent": "Compares the fixed convoy account with an offered disputed compensation claim that would unfairly assign blame to unrelated Orcs. No invented named witness.",
          "reveal_or_develop": [],
          "choices": [
            {
              "id": "character_blueprints_pilot_001.guard_01.quiet_publish",
              "player_intent": "Sign the accurate limited report and waive the optional disputed compensation.",
              "consequence": "Commit real waived compensation and truthful attribution; verified character_blueprints_pilot_001.guard_01.state_costly_truthful_report. Enable reconciliation.",
              "next": "character_blueprints_pilot_001.guard_01.milestone_reckoning"
            },
            {
              "id": "character_blueprints_pilot_001.guard_01.quiet_claim",
              "player_intent": "Take the disputed compensation instead.",
              "consequence": "Record refusal of the costly promise; trust unproven. Warn that this instance cannot retroactively repeat the choice.",
              "next": "character_blueprints_pilot_001.guard_01.milestone_reckoning"
            },
            {
              "id": "character_blueprints_pilot_001.guard_01.quiet_wait",
              "player_intent": "Read it another day.",
              "consequence": "Hold offer unchanged and unclaimed.",
              "next": "end"
            },
            {
              "id": "character_blueprints_pilot_001.guard_01.quiet_stop",
              "player_intent": "Stop the inquiry.",
              "consequence": "Confirmed final closure without trust; cap remains.",
              "next": "character_blueprints_pilot_001.guard_01.branch_uncertainty"
            }
          ],
          "next": "end"
        }
      ],
      "personal_arcs": [
        {
          "id": "character_blueprints_pilot_001.guard_01.arc_warband",
          "family_id": "guard_warband_accountability",
          "repeat_policy": {
            "repeat_key": "personal:guard_warband:accountability",
            "scope": "player",
            "max_offers": null,
            "retry": "same_instance_only"
          },
          "armed_by": "character_blueprints_pilot_001.guard_01.boundary_arm or character_blueprints_pilot_001.guard_01.boundary_private; one player-scoped chain shared by all roster candidates.",
          "entry_conditions": {
            "registered_predicates": {
              "all": [
                {
                  "field": "speaker.personality",
                  "op": "eq",
                  "value": "strategist"
                },
                {
                  "field": "speaker.tags",
                  "op": "has",
                  "value": "history:orc_warband_grievance"
                },
                {
                  "field": "speaker.conscious",
                  "op": "eq",
                  "value": null
                }
              ],
              "any": [],
              "none": []
            },
            "review_only_context": "Recruited guard with assigned grievance, saved arm and functioning deterministic private contract. Optional combat route requires an existing unnamed procedural Orc hostile assigned same-warband provenance BEFORE encounter. No named/lore rewrites, arbitrary Orc relabeling or new spawns."
          },
          "participants": [
            "Individual recruited guard; player with reviewed player.race context.",
            "Combat option: already-existing visible hostile Orc with saved pre-encounter warband affiliation; ordinary allies may land final hit.",
            "Quiet option: player and guard reviewing seeded convoy facts and a real optional contested compensation claim; no extra NPC or mission required."
          ],
          "milestones": [
            {
              "id": "character_blueprints_pilot_001.guard_01.milestone_consent",
              "event": "camp_talk",
              "prerequisites": [
                "Saved boundary_arm, guard recruited."
              ],
              "player_objective": "Accept evidence-based accountability without a required personal kill.",
              "scoring": "Arm once. Quiet contract becomes available immediately; recognition remains optional.",
              "next": "character_blueprints_pilot_001.guard_01.milestone_recognition"
            },
            {
              "id": "character_blueprints_pilot_001.guard_01.milestone_recognition",
              "event": "enemy_spotted",
              "prerequisites": [
                "Consent saved; reviewed generation hook has bound a compatible existing hostile BEFORE mission; it is visible."
              ],
              "player_objective": "Recognize affiliation only after seeing the bound foe.",
              "scoring": "Do not treat a generic Orc as perpetrator; if no match, offer node_quiet_account directly, never farm random encounters.",
              "next": "character_blueprints_pilot_001.guard_01.milestone_encounter"
            },
            {
              "id": "character_blueprints_pilot_001.guard_01.milestone_encounter",
              "event": "personal_milestone",
              "prerequisites": [
                "Same saved enemy, actual combat result recorded."
              ],
              "player_objective": "Allow real defeat, lawful finalized alive capture, escape or restraint; avoid mandatory guard final hit.",
              "scoring": "Track ally final hit, death, defeat, escape, retreat and actual finalized capture distinctly; actor-down delays talk. Pending outcome waits, not victory.",
              "next": "character_blueprints_pilot_001.guard_01.node_evidence"
            },
            {
              "id": "character_blueprints_pilot_001.guard_01.milestone_reckoning",
              "event": "camp_talk",
              "prerequisites": [
                "A conscious guard; documented encounter report OR saved quiet-contract decision."
              ],
              "player_objective": "Choose specialization, truthful reconciliation, or warned unresolved closure.",
              "scoring": "Specialization needs verified affiliated encounter. Reconciliation needs character_blueprints_pilot_001.guard_01.state_costly_truthful_report from an actual waived claim (not mere Orc defeat); failure means defer/uncertainty. Each ending once.",
              "next": "end"
            }
          ],
          "resolution_branches": [
            {
              "id": "character_blueprints_pilot_001.guard_01.branch_specialization",
              "name": "Warband accountability and specialization",
              "trigger": "Authenticated same-warband encounter, factual report and explicit specialization choice.",
              "resolved": "This encounter is addressed; training is chosen.",
              "remaining_conflicts": "Orc distrust and Orc-player 80 cap remain; no implied trust.",
              "facet_changes": "Retain facet_mastery and facet_distrust; no individuals-first conversion or devotion.",
              "base_personality_change": "No base personality or combat-AI change.",
              "reward_contract_id": "character_blueprints_pilot_001.guard_01.reward_specialization"
            },
            {
              "id": "character_blueprints_pilot_001.guard_01.branch_reconciliation",
              "name": "Truthful reconciliation and optional platonic bond",
              "trigger": "Prior boundary_arm or boundary_private promise; node_quiet_account.quiet_publish has irreversibly waived a real offered disputed payment and logged fair attribution; guard freely affirms at reckoning.",
              "resolved": "Collective distrust ends and this player is assessed individually; grievance history is not erased.",
              "remaining_conflicts": "Specific warband losses may remain unredressed; no automatic relationship score or devotion.",
              "facet_changes": "Deactivate facet_distrust; activate facet_individuals; optional later facet_devotion at node_trust. Lift only conditional Orc-player cap.",
              "base_personality_change": "No base personality or combat-AI change.",
              "reward_contract_id": "character_blueprints_pilot_001.guard_01.reward_reconciliation"
            },
            {
              "id": "character_blueprints_pilot_001.guard_01.branch_uncertainty",
              "name": "Final stop without fabricated resolution",
              "trigger": "Explicit final stop at boundary_decline, quiet_stop, or reckoning; show remaining distrust first.",
              "resolved": "The hunt ends without pretending proof or trust.",
              "remaining_conflicts": "Distrust and Orc-player ceiling remain; no extra chain or reward.",
              "facet_changes": "Keep fixed facts, distrust and normal professional dialogue; no devotion.",
              "base_personality_change": "No base personality or combat-AI change.",
              "reward_contract_id": "character_blueprints_pilot_001.guard_01.reward_uncertainty"
            }
          ],
          "failure_and_recovery": [
            "Bound combat target unavailable/dead/escaped or no eligible mission: offer deterministic node_quiet_account immediately; never reassign unrelated Orcs, respawn target or wait on random chance.",
            "Combat ally final hit counts for truthful team outcome; actor down waits for recovery; retreat leaves same attempt pending. Capture only after existing finalized capture/recovery, distinct from defeat/death.",
            "Private contract is one authentic offer: truthful waiver commits the cost and evidence once; taking compensation fails this proof, and reload/clicks cannot resample it. Warn before the irreversible decision.",
            "Deferral resumes the saved offer; confirmed stop closes without lift. All endings and grants share the player one-off key."
          ],
          "reward_contract_ids": [
            "character_blueprints_pilot_001.guard_01.reward_specialization",
            "character_blueprints_pilot_001.guard_01.reward_reconciliation",
            "character_blueprints_pilot_001.guard_01.reward_uncertainty"
          ]
        }
      ],
      "conclusion": {
        "established_condition": "Intro plus two saved ordinary talks; not conditional on an encounter.",
        "core_closed_condition": "One saved specialization, reconciliation or warned final-stop branch. A defer is not closure.",
        "closed_behavior": "No new major personal warband chain or replayable reward; retire resolved hunt prompts, not history.",
        "continuing_growth": "Reserved conversation, friendships, normal progression and memories continue; devotion is optional and platonic."
      },
      "reward_contracts": [
        {
          "id": "character_blueprints_pilot_001.guard_01.reward_specialization",
          "player_expectation": "A useful lasting way to fight the confirmed warband threat.",
          "setup": "Before acceptance, choose a REVIEWED permanent option: enemy-type anti-Orc damage technique/perk, or a defensive anti-Orc formation method.",
          "narrative_payoff": "Practical expertise rather than miscellaneous spoils.",
          "grant_proposal": {
            "category": "perk",
            "description": "Propose ONE nonstacking, once-only anti-Orc damage perk/technique (enemy-type scoped); defensive protection training is a mutually exclusive alternative. Numbers/ID unapproved.",
            "implementation_id": null
          },
          "why_it_fits": "Offense rewards specialization against eligible Orc enemies; defense offers wider team protection but less direct damage.",
          "alternative_branch_fairness": "No substitution with supplies after a permanent technique is promised. Different ending may offer truthful closure instead.",
          "review_required": null
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.reward_reconciliation",
          "player_expectation": "Recognition of a meaningful costly choice and freedom from blanket suspicion.",
          "setup": "Guard sees the player forgo disputed compensation rather than blame unrelated Orcs.",
          "narrative_payoff": "Explicit trust, a witnessed corrected account and optional platonic promise.",
          "grant_proposal": {
            "category": "relationship",
            "description": "Propose persistent belief conversion and remembered trust; lift Orc-player 80 ceiling if active, with NO loyalty-point award or hidden bond stat.",
            "implementation_id": null
          },
          "why_it_fits": "Non-Orc players get the same acknowledged trust and altered future dialogue even without a cap to lift.",
          "alternative_branch_fairness": "Unlike the combat-perk branch this pays off in lasting narrative relationship and belief change; present tradeoff before commitment.",
          "review_required": null
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.reward_uncertainty",
          "player_expectation": "An honest ability to stop involvement.",
          "setup": "Warn that distrust and the conditional cap survive.",
          "narrative_payoff": "A chosen boundary without invented revenge or absolution.",
          "grant_proposal": {
            "category": "closure",
            "description": "No reward, no cap removal, no perk; preserve ordinary growth.",
            "implementation_id": null
          },
          "why_it_fits": "The player may decline optional content without losing existing gear.",
          "alternative_branch_fairness": "Not advertised as equivalent to completing the personal arc.",
          "review_required": null
        }
      ],
      "aftermath": {
        "remembered_facts": [
          "Seeded caravan raid; selected path; bound encounter outcome when applicable; whether disputed compensation was truly waived; one-off reward claim.",
          "Active distrust versus resolved individuals-first belief; conditional cap state; separate optional platonic pledge."
        ],
        "retired_hostile_lines": [
          "On reconciliation, retire broad anti-Orc suspicion and unresolved-hunt triggers; retain factual grief and justified criticism of actual attackers."
        ],
        "new_voice_beats": [
          "Specialist: understated planning pride without reconciliation.",
          "Reconciled: specific gratitude for the costly truthful report; reserved style remains.",
          "Unresolved stop: normal guard talk without repeated offers."
        ],
        "personality_change_scope": "Strategist stays strategist; no combat-AI changes.",
        "relationship_change_scope": "Earned trust is remembered; optional devotion needs explicit separate player consent, never romance by default."
      },
      "capability_requests": [
        {
          "id": "character_blueprints_pilot_001.guard_01.cap_history_binding",
          "description": "Persist individualized convoy grievance and pre-encounter provenance; optionally assign compatible existing unnamed procedural warband enemy within normal mission budget.",
          "reason": "Race alone proves no guilt.",
          "required_for": [
            "character_blueprints_pilot_001.guard_01.facet_grievance",
            "character_blueprints_pilot_001.guard_01.milestone_recognition"
          ],
          "review_required": null
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.cap_player_orc",
          "description": "Read player.race, disclose prospective 80 cap pre-recruitment and lift only this cap on proof; never auto-grant loyalty.",
          "reason": "Neither player.race nor individualized cap is registered.",
          "required_for": [
            "character_blueprints_pilot_001.guard_01.intro_offer",
            "character_blueprints_pilot_001.guard_01.facet_individuals"
          ],
          "review_required": null
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.cap_conversation_state",
          "description": "Saved routing, one player-scoped offer, branch choices, outcome distinctions and post-closure one-time talk.",
          "reason": "New arcs and state transitions are proposals.",
          "required_for": [
            "character_blueprints_pilot_001.guard_01.arc_warband",
            "character_blueprints_pilot_001.guard_01.node_evidence",
            "character_blueprints_pilot_001.guard_01.node_trust"
          ],
          "review_required": null
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.cap_choice_bridge",
          "description": "Guarantee a reviewed private compensation-contract offer with genuine waivable consideration and accurate limited blame report; store promise, choice, cost and evidence atomically.",
          "reason": "Provides observable costly truth even without an Orc enemy or capture ability.",
          "required_for": [
            "character_blueprints_pilot_001.guard_01.boundary_private",
            "character_blueprints_pilot_001.guard_01.node_quiet_account",
            "character_blueprints_pilot_001.guard_01.branch_reconciliation"
          ],
          "review_required": null
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.cap_specialized_reward",
          "description": "Balance exclusive permanent anti-Orc damage versus defensive training; approve implementation and reward before promise is displayed.",
          "reason": "No live perk IDs supplied.",
          "required_for": [
            "character_blueprints_pilot_001.guard_01.reward_specialization"
          ],
          "review_required": null
        },
        {
          "id": "character_blueprints_pilot_001.guard_01.cap_mission_context",
          "description": "Persist actual ally final hit, actor recovery, retreat, enemy death/escape and finalized capture.",
          "reason": "Facts must be verified; no resurrection or automatic capture.",
          "required_for": [
            "character_blueprints_pilot_001.guard_01.milestone_encounter",
            "character_blueprints_pilot_001.guard_01.node_evidence"
          ],
          "review_required": null
        }
      ],
      "routing": [
        {
          "from": "introduction",
          "trigger": "intro_offer or intro_ask after confirmed recruitment",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.guard_01.node_route_memory",
          "state_effect": "Save disclosure and conditional cap shown; wait for recruited companion talk."
        },
        {
          "from": "introduction",
          "trigger": "intro_defer",
          "prerequisite": "No recruitment or story commitment",
          "to": "end",
          "state_effect": "Resume the same character-scoped introduction later with original facts."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_route_memory",
          "trigger": "route_listen",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.guard_01.node_watchcraft",
          "state_effect": "Reveal caravan once."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_route_memory",
          "trigger": "route_leave",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "end",
          "state_effect": "Resume route-memory later."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_watchcraft",
          "trigger": "watchcraft_ask",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.guard_01.node_boundary",
          "state_effect": "Reveal mastery once."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_watchcraft",
          "trigger": "watchcraft_pause",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "end",
          "state_effect": "Resume watchcraft later."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_boundary",
          "trigger": "boundary_arm",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.guard_01.milestone_consent",
          "state_effect": "Commit explicit truthful promise; arm story once."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_boundary",
          "trigger": "boundary_private",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.guard_01.node_quiet_account",
          "state_effect": "Commit truthful promise; quiet contract offered without a mission."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_boundary",
          "trigger": "boundary_defer",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "end",
          "state_effect": "Resume boundary with no one-off use."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_boundary",
          "trigger": "boundary_decline",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.guard_01.branch_uncertainty",
          "state_effect": "Confirmed final stop, distrust/cap persist."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.milestone_consent",
          "trigger": "consent saved",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.guard_01.milestone_recognition",
          "state_effect": "Await only optional proven existing enemy; quiet account separately unlocked."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.milestone_recognition",
          "trigger": "valid visible affiliated hostile",
          "prerequisite": "Approved pre-encounter mission affiliation",
          "to": "character_blueprints_pilot_001.guard_01.milestone_encounter",
          "state_effect": "Bind actual enemy once, not a generic Orc."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.milestone_recognition",
          "trigger": "no compatible enemy / route not desired",
          "prerequisite": "Reviewed private contract active",
          "to": "character_blueprints_pilot_001.guard_01.node_quiet_account",
          "state_effect": "Guaranteed alternative, without random farming."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.milestone_encounter",
          "trigger": "verified actual result",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.guard_01.node_evidence",
          "state_effect": "Store exact outcome; wait for conscious camp talk."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_evidence",
          "trigger": "evidence_fair",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.guard_01.milestone_reckoning",
          "state_effect": "Truthful facts stored; costly bridge still needed for reconciliation."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_evidence",
          "trigger": "evidence_defer",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "end",
          "state_effect": "Return to same evidence conversation."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_quiet_account",
          "trigger": "quiet_publish",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.guard_01.milestone_reckoning",
          "state_effect": "Waive real disputed claim; commit truthful report and character_blueprints_pilot_001.guard_01.state_costly_truthful_report."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_quiet_account",
          "trigger": "quiet_claim",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.guard_01.milestone_reckoning",
          "state_effect": "Save accepted compensation; fairness proof false; warn reconciliation unavailable."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_quiet_account",
          "trigger": "quiet_wait",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "end",
          "state_effect": "Resume same unconsumed offer."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_quiet_account",
          "trigger": "quiet_stop",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.guard_01.branch_uncertainty",
          "state_effect": "Final stop, cap persists."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.milestone_reckoning",
          "trigger": "choose specialization",
          "prerequisite": "Verified affiliated encounter and truthful report",
          "to": "character_blueprints_pilot_001.guard_01.branch_specialization",
          "state_effect": "Close once and queue reviewed permanent perk."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.milestone_reckoning",
          "trigger": "choose reconciliation",
          "prerequisite": "Saved character_blueprints_pilot_001.guard_01.state_costly_truthful_report and explicit consent",
          "to": "character_blueprints_pilot_001.guard_01.branch_reconciliation",
          "state_effect": "Retire distrust, lift Orc-player ceiling if present; no loyalty points."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.milestone_reckoning",
          "trigger": "choose final uncertainty",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.guard_01.branch_uncertainty",
          "state_effect": "Close once; distrust and cap stay."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.milestone_reckoning",
          "trigger": "defer or insufficient proof",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "end",
          "state_effect": "Preserve milestone; offer node_quiet_account if unconsumed."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.branch_reconciliation",
          "trigger": "once-only aftermath on next conscious companion talk",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.guard_01.node_trust",
          "state_effect": "Present optional platonic pledge exactly once."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_trust",
          "trigger": "trust_pledge",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "end",
          "state_effect": "Develop devotion; mark once-only talk consumed."
        },
        {
          "from": "character_blueprints_pilot_001.guard_01.node_trust",
          "trigger": "trust_distance",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "end",
          "state_effect": "Keep reconciled state without devotion; consume once-only talk."
        }
      ],
      "routing_rules": {
        "status": "review_required, authoring-only",
        "choice_precedence": "Selected choice.next always overrides generic node.next. Generic next is a suggested narrative successor only; it never auto-selects a choice, completes a mission or ends an arc.",
        "resume": "end on defer means return to saved source node; end on completed choice consumes only that interaction. Final decline is a saved exclusive ending.",
        "persistence": "Save verified facts and choice transitions atomically; reload, alternate dialogue wording or another roster member cannot reroll one-off key or grant."
      },
      "routing_state_ids": [
        "character_blueprints_pilot_001.guard_01.state_truthful_promise",
        "character_blueprints_pilot_001.guard_01.state_costly_truthful_report",
        "character_blueprints_pilot_001.guard_01.state_disputed_claim_taken",
        "character_blueprints_pilot_001.guard_01.state_guard_chain_closed",
        "character_blueprints_pilot_001.guard_01.state_trust_talk_consumed"
      ]
    },
    {
      "id": "character_blueprints_pilot_001.artisan_02",
      "title": "The Workshop Ledger",
      "identity": {
        "races": [
          "Human",
          "Dwarf",
          "Gnome",
          "Goblin"
        ],
        "genders": [
          "female",
          "male"
        ],
        "base_personalities": [
          "dutiful"
        ],
        "jobs": [
          "engineer"
        ],
        "authored_character_exclusions": [
          "No named canonical NPCs, incompatible prior histories or overlapping major personal chains.",
          "Never infer individual history from race, art or personality."
        ]
      },
      "core_promise": "A sociable but exacting engineer learns that professional integrity requires recording mistakes and accepting help, not silently carrying every repair alone.",
      "facets": [
        {
          "id": "character_blueprints_pilot_001.artisan_02.facet_artisan",
          "tag": "background:artisan",
          "operation": "reveal_fixed",
          "starts_revealed": true,
          "claim": "Has practiced ordinary repair and inspection work before joining the party.",
          "prerequisites": [
            "Assigned once at character creation; revelation follows a saved eligible beat."
          ],
          "incompatible_with": [],
          "provenance": "Individual practiced trade"
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.facet_pride",
          "tag": "voice:craft_pride",
          "operation": "reveal_fixed",
          "starts_revealed": true,
          "claim": "Takes genuine pride in careful work, especially plain things that do not break.",
          "prerequisites": [
            "Assigned once at character creation; revelation follows a saved eligible beat."
          ],
          "incompatible_with": [],
          "provenance": "Professional voice rooted in artisan and engineer experience."
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.facet_sociable",
          "tag": "social:gregarious",
          "operation": "reveal_fixed",
          "starts_revealed": true,
          "claim": "Finds it easy to chat about tools and other people’s work, though not their own mistake.",
          "prerequisites": [
            "Assigned once at character creation; revelation follows a saved eligible beat."
          ],
          "incompatible_with": [],
          "provenance": "Contrasts with blueprint 1 without treating dutiful as automatically outgoing."
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.facet_mastery",
          "tag": "motive:mastery",
          "operation": "reveal_fixed",
          "starts_revealed": true,
          "claim": "Wants a dependable, repeatable way to check work rather than relying on a lucky successful repair.",
          "prerequisites": [
            "Assigned once at character creation; revelation follows a saved eligible beat."
          ],
          "incompatible_with": [],
          "provenance": "Ordinary professional ambition, not an unlock promise."
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.facet_error",
          "tag": null,
          "operation": "reveal_fixed",
          "starts_revealed": false,
          "claim": "In one earlier job, this person signed off a faulty count, wasted materials and avoided telling anyone it was their mistake.",
          "prerequisites": [
            "One approved per-character unreported-quality-error fact exists before node_admission; tag stays null until registered."
          ],
          "incompatible_with": [],
          "provenance": "Not supported by current history tags"
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.facet_repayment",
          "tag": "motive:repayment",
          "operation": "reveal_fixed",
          "starts_revealed": false,
          "claim": "Wants to make good on the wasted resources by sharing a reliable check method with somebody else.",
          "prerequisites": [
            "Assigned once at character creation; revelation follows a saved eligible beat."
          ],
          "incompatible_with": [],
          "provenance": "Individual motive tied to the exact past mistake, not a generic guilt mechanic."
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.facet_trust",
          "tag": "social:selectively_trusting",
          "operation": "develop_open",
          "starts_revealed": false,
          "claim": "Becomes willing to let another person inspect work and correct an error without feeling personally erased.",
          "prerequisites": [
            "Committed paired preparation check, eligible mission success, conscious debrief and accepted truthful ledger choice."
          ],
          "incompatible_with": [],
          "provenance": "Development from friendly talk to professional trust"
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.facet_belonging",
          "tag": "motive:belonging",
          "operation": "develop_open",
          "starts_revealed": false,
          "claim": "Begins to value shared responsibility in the party as much as being the one who can fix everything.",
          "prerequisites": [
            "Committed paired preparation check, eligible mission success, conscious debrief and accepted truthful ledger choice."
          ],
          "incompatible_with": [],
          "provenance": "Open development, not a retroactive change to employment, race or base personality."
        }
      ],
      "establishment": {
        "core_facet_ids": [
          "character_blueprints_pilot_001.artisan_02.facet_artisan",
          "character_blueprints_pilot_001.artisan_02.facet_pride",
          "character_blueprints_pilot_001.artisan_02.facet_sociable",
          "character_blueprints_pilot_001.artisan_02.facet_mastery",
          "character_blueprints_pilot_001.artisan_02.facet_error",
          "character_blueprints_pilot_001.artisan_02.facet_repayment",
          "character_blueprints_pilot_001.artisan_02.facet_trust",
          "character_blueprints_pilot_001.artisan_02.facet_belonging"
        ],
        "intro_reveal_ids": [
          "character_blueprints_pilot_001.artisan_02.facet_artisan",
          "character_blueprints_pilot_001.artisan_02.facet_pride",
          "character_blueprints_pilot_001.artisan_02.facet_sociable",
          "character_blueprints_pilot_001.artisan_02.facet_mastery"
        ],
        "remaining_reveal_beats": [
          {
            "facet_id": "character_blueprints_pilot_001.artisan_02.facet_error",
            "beat": "Reveal only seeded unreported faulty count at admission."
          },
          {
            "facet_id": "character_blueprints_pilot_001.artisan_02.facet_repayment",
            "beat": "Discuss desire to make the work right at admission."
          },
          {
            "facet_id": "character_blueprints_pilot_001.artisan_02.facet_trust",
            "beat": "Develop only after committed check, mission and truthful debrief."
          },
          {
            "facet_id": "character_blueprints_pilot_001.artisan_02.facet_belonging",
            "beat": "Develop only on accepted collaborative ledger resolution."
          }
        ],
        "established_when": "First post-recruitment talk shows four fixed traits; saved admission reveals seeded mistake and repayment motive. Trust/belonging are optional developments."
      },
      "introduction": {
        "entry_point": "companion_introduction",
        "eligibility": {
          "all": [
            {
              "field": "speaker.personality",
              "op": "eq",
              "value": "dutiful"
            },
            {
              "field": "speaker.job",
              "op": "eq",
              "value": "engineer"
            },
            {
              "field": "speaker.tags",
              "op": "has",
              "value": "background:artisan"
            },
            {
              "field": "speaker.conscious",
              "op": "eq",
              "value": true
            }
          ],
          "any": [],
          "none": []
        },
        "reveal_beats": [
          "Early post-recruitment talk: sociable dutiful engineer checks an ordinary fitting twice and values reliable repair.",
          "Personal count error is a preassigned, unapproved individual fact, revealed later only if that provenance is approved; no special skill or reward at intro."
        ],
        "prospective_loyalty_cap": null,
        "player_options": [
          {
            "id": "character_blueprints_pilot_001.artisan_02.intro_talk",
            "player_intent": "Ask why the engineer checks everything twice.",
            "consequence": "Open standards talk after recruitment; no reward or actual inspection yet.",
            "next": "character_blueprints_pilot_001.artisan_02.node_standards"
          },
          {
            "id": "character_blueprints_pilot_001.artisan_02.intro_share",
            "player_intent": "Offer to compare procedures.",
            "consequence": "Open standards talk after recruitment; no reward or actual inspection yet.",
            "next": "character_blueprints_pilot_001.artisan_02.node_standards"
          },
          {
            "id": "character_blueprints_pilot_001.artisan_02.intro_defer",
            "player_intent": "Go about the day.",
            "consequence": "Resume same introductory conversation later.",
            "next": "end"
          }
        ],
        "repeat_policy": {
          "repeat_key": "personal:artisan_ledger:early_talk",
          "scope": "character",
          "max_offers": 1,
          "retry": "same_instance_only"
        }
      },
      "conversation_nodes": [
        {
          "id": "character_blueprints_pilot_001.artisan_02.node_standards",
          "when": "Saved post-recruitment introduction completed.",
          "speaker_intent": "Shares a practical check order and unflashy pride.",
          "reveal_or_develop": [],
          "choices": [
            {
              "id": "character_blueprints_pilot_001.artisan_02.standards_listen",
              "player_intent": "Ask about standards.",
              "consequence": "Ordinary identity beat.",
              "next": "character_blueprints_pilot_001.artisan_02.node_admission"
            },
            {
              "id": "character_blueprints_pilot_001.artisan_02.standards_defer",
              "player_intent": "Talk later.",
              "consequence": "Pause unchanged.",
              "next": "end"
            }
          ],
          "next": "end"
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.node_admission",
          "when": "Approved once-seeded personal counting error exists.",
          "speaker_intent": "Admits wasted material and a wish to repay that mistake.",
          "reveal_or_develop": [
            {
              "facet_id": "character_blueprints_pilot_001.artisan_02.facet_error",
              "transition": "Reveal seeded one-off error."
            },
            {
              "facet_id": "character_blueprints_pilot_001.artisan_02.facet_repayment",
              "transition": "Reveal repayment motive."
            }
          ],
          "choices": [
            {
              "id": "character_blueprints_pilot_001.artisan_02.admission_kind",
              "player_intent": "Hear the mistake without humiliation.",
              "consequence": "Save honest admission.",
              "next": "character_blueprints_pilot_001.artisan_02.node_offer"
            },
            {
              "id": "character_blueprints_pilot_001.artisan_02.admission_honest",
              "player_intent": "Ask for better procedure.",
              "consequence": "Save same facts and motive.",
              "next": "character_blueprints_pilot_001.artisan_02.node_offer"
            },
            {
              "id": "character_blueprints_pilot_001.artisan_02.admission_pause",
              "player_intent": "Return later.",
              "consequence": "Hold same disclosure.",
              "next": "end"
            }
          ],
          "next": "end"
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.node_offer",
          "when": "After admission; one story slot available.",
          "speaker_intent": "Requests a two-person check during ordinary preparation and participation in a normal mission.",
          "reveal_or_develop": [],
          "choices": [
            {
              "id": "character_blueprints_pilot_001.artisan_02.offer_agree",
              "player_intent": "Agree to check together.",
              "consequence": "Arm player-scoped chain, no buff or immediate check.",
              "next": "character_blueprints_pilot_001.artisan_02.milestone_agreement"
            },
            {
              "id": "character_blueprints_pilot_001.artisan_02.offer_defer",
              "player_intent": "Not yet.",
              "consequence": "Hold same offer.",
              "next": "end"
            },
            {
              "id": "character_blueprints_pilot_001.artisan_02.offer_decline",
              "player_intent": "Permanently decline.",
              "consequence": "Confirm no-test closure and no reward; no penalty.",
              "next": "character_blueprints_pilot_001.artisan_02.branch_no_test"
            }
          ],
          "next": "end"
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.node_review",
          "when": "Verified field success after checked preparation; conscious engineer at camp.",
          "speaker_intent": "Compares what the team actually learned.",
          "reveal_or_develop": [],
          "choices": [
            {
              "id": "character_blueprints_pilot_001.artisan_02.review_correct",
              "player_intent": "Discuss the genuine check and any correction.",
              "consequence": "Save honest debrief; begin ledger step.",
              "next": "character_blueprints_pilot_001.artisan_02.milestone_account"
            },
            {
              "id": "character_blueprints_pilot_001.artisan_02.review_wait",
              "player_intent": "Debrief later.",
              "consequence": "Hold verified outcome.",
              "next": "end"
            },
            {
              "id": "character_blueprints_pilot_001.artisan_02.review_stop",
              "player_intent": "End this personal review.",
              "consequence": "Confirmed no-test/no-payout closure; no false success.",
              "next": "character_blueprints_pilot_001.artisan_02.branch_no_test"
            }
          ],
          "next": "end"
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.node_ledger",
          "when": "Only after conscious truthful debrief and milestone_account; not on conversation opening alone.",
          "speaker_intent": "Shares credit without denying the old error.",
          "reveal_or_develop": [],
          "choices": [
            {
              "id": "character_blueprints_pilot_001.artisan_02.ledger_credit",
              "player_intent": "Record shared contribution.",
              "consequence": "Mutually exclusive shared-credit ending with reviewed ordinary supplies.",
              "next": "character_blueprints_pilot_001.artisan_02.branch_shared_credit"
            },
            {
              "id": "character_blueprints_pilot_001.artisan_02.ledger_private",
              "player_intent": "Keep accurate account within party.",
              "consequence": "Mutually exclusive private ending with reviewed gold.",
              "next": "character_blueprints_pilot_001.artisan_02.branch_private_account"
            },
            {
              "id": "character_blueprints_pilot_001.artisan_02.ledger_notyet",
              "player_intent": "Decide later.",
              "consequence": "No branch or reward; resume same ledger.",
              "next": "end"
            },
            {
              "id": "character_blueprints_pilot_001.artisan_02.ledger_stop",
              "player_intent": "Close without claiming successful shared accounting.",
              "consequence": "Confirmed no-reward ending; prior check remains in memory.",
              "next": "character_blueprints_pilot_001.artisan_02.branch_no_test"
            }
          ],
          "next": "end"
        }
      ],
      "personal_arcs": [
        {
          "id": "character_blueprints_pilot_001.artisan_02.arc_ledger",
          "family_id": "artisan_shared_inspection",
          "repeat_policy": {
            "repeat_key": "personal:artisan_ledger:shared_inspection",
            "scope": "player",
            "max_offers": 1,
            "retry": "same_instance_only"
          },
          "armed_by": "character_blueprints_pilot_001.artisan_02.offer_agree; one player-scoped chain per save/account, not per engineer roster copy.",
          "entry_conditions": {
            "registered_predicates": {
              "all": [
                {
                  "field": "speaker.personality",
                  "op": "eq",
                  "value": "dutiful"
                },
                {
                  "field": "speaker.job",
                  "op": "eq",
                  "value": "engineer"
                },
                {
                  "field": "speaker.tags",
                  "op": "has",
                  "value": "background:artisan"
                },
                {
                  "field": "speaker.conscious",
                  "op": "eq",
                  "value": true
                }
              ],
              "any": [],
              "none": []
            },
            "review_only_context": "Recruited conscious engineer with seeded personal error, explicit accepted offer, normal mission and player + engineer prepared to inspect; all tracking beyond registry is review-only."
          },
          "participants": [
            "Recruited engineer and player as narrative second checker; no mandatory new physical item or extra NPC.",
            "An existing normal mission with verified participant and success status; no special enemy is needed."
          ],
          "milestones": [
            {
              "id": "character_blueprints_pilot_001.artisan_02.milestone_agreement",
              "event": "camp_talk",
              "prerequisites": [
                "Saved offer_agree; seeded personal error and recruited engineer."
              ],
              "player_objective": "Agree to permit a genuine second opinion.",
              "scoring": "Save permission and one eligible prep choice; opening conversation is not a check.",
              "next": "character_blueprints_pilot_001.artisan_02.milestone_check"
            },
            {
              "id": "character_blueprints_pilot_001.artisan_02.milestone_check",
              "event": "mission_entry",
              "prerequisites": [
                "Normal eligible mission entry; engineer present and conscious, agreement committed; proposed prepare_joint_check choice shown."
              ],
              "player_objective": "Select prepare_joint_check once to do the narrative two-person inspection.",
              "scoring": "The explicit choice records both participants checking and a correction accepted; opening/reopening talk never commits it. No inspection minigame, stats or equipment changes.",
              "next": "character_blueprints_pilot_001.artisan_02.milestone_field",
              "preparation_choice": {
                "id": "character_blueprints_pilot_001.artisan_02.prepare_joint_check",
                "status": "review_required",
                "trigger": "Player explicitly selects once in eligible normal mission preparations; both participants present and conscious.",
                "effect": "Commit the narrative two-person check and accepted correction as a saved fact. No equipment change, physical minigame or reward.",
                "on_skip": "Do not score inspection; continue pending for next eligible mission."
              }
            },
            {
              "id": "character_blueprints_pilot_001.artisan_02.milestone_field",
              "event": "mission_success",
              "prerequisites": [
                "Committed preparation check and actual ordinary mission participation on a mission after that choice."
              ],
              "player_objective": "Participate normally, then examine its real result.",
              "scoring": "Exact policy: SUCCESS qualifies for debrief (even if an ally makes final hit). FAILURE/RETREAT does not; preserve the single check and await the next normal eligible SUCCESS with engineer participating. No second check or one-off reroll. Actor down can debrief only after recovery.",
              "next": "character_blueprints_pilot_001.artisan_02.node_review"
            },
            {
              "id": "character_blueprints_pilot_001.artisan_02.milestone_account",
              "event": "camp_talk",
              "prerequisites": [
                "Eligible success saved; node_review.review_correct chosen; conscious engineer and seeded error."
              ],
              "player_objective": "Acknowledge earlier mistake and verified cooperation, then choose shared or private ledger account.",
              "scoring": "Record truthful debrief once, route to node_ledger; ledger choice exclusively resolves and pays once.",
              "next": "character_blueprints_pilot_001.artisan_02.node_ledger"
            }
          ],
          "resolution_branches": [
            {
              "id": "character_blueprints_pilot_001.artisan_02.branch_shared_credit",
              "name": "Shared accurate ledger",
              "trigger": "Saved review and ledger_credit after qualifying success.",
              "resolved": "Shares credit, accepts past error and collaborative responsibility.",
              "remaining_conflicts": "Retains fussy craft standards without perfectionism as sole identity.",
              "facet_changes": "Develop facet_trust and facet_belonging; original error stays history.",
              "base_personality_change": "No base personality or combat-AI change.",
              "reward_contract_id": "character_blueprints_pilot_001.artisan_02.reward_supplies"
            },
            {
              "id": "character_blueprints_pilot_001.artisan_02.branch_private_account",
              "name": "Private truthful ledger",
              "trigger": "Saved review and ledger_private after qualifying success.",
              "resolved": "Honest private responsibility and shared method without invented outside audience.",
              "remaining_conflicts": "Reserved about past mistakes outside party.",
              "facet_changes": "Develop facet_trust and facet_belonging; no fabricated public acclaim.",
              "base_personality_change": "No base personality or combat-AI change.",
              "reward_contract_id": "character_blueprints_pilot_001.artisan_02.reward_private"
            },
            {
              "id": "character_blueprints_pilot_001.artisan_02.branch_no_test",
              "name": "Final stop without successful ledger resolution",
              "trigger": "Confirmed offer_decline, review_stop or ledger_stop; not a temporary defer.",
              "resolved": "Voluntary activity stops with no false mechanical or emotional success.",
              "remaining_conflicts": "Open trust and belonging facets remain undeveloped.",
              "facet_changes": "Keep identity established, preserve actual attempt; no reward.",
              "base_personality_change": "No base personality or combat-AI change.",
              "reward_contract_id": "character_blueprints_pilot_001.artisan_02.reward_no_test"
            }
          ],
          "failure_and_recovery": [
            "At prep, if either person missing/unconscious, do not present prepare_joint_check; wait for another eligible ordinary mission, no invented interaction.",
            "If actor downs after prep, preserve recorded check; dialogue waits for recovery. Retreat or mission failure is not success: repeat normal mission participation until first eligible success, WITHOUT repeating the committed inspection.",
            "Enemy capture and defeat are unrelated to checklist scoring; ally final hit counts only as team mission success. No special target, revival or added enemy.",
            "Defer retains the same state. Confirmed final decline ends only optional chain. Save/reload, duplicate clicks and alternate ending choices never grant extra rewards."
          ],
          "reward_contract_ids": [
            "character_blueprints_pilot_001.artisan_02.reward_supplies",
            "character_blueprints_pilot_001.artisan_02.reward_private",
            "character_blueprints_pilot_001.artisan_02.reward_no_test"
          ]
        }
      ],
      "conclusion": {
        "established_condition": "Intro and seeded admission reveal normal identity independently of quest.",
        "core_closed_condition": "Explicit shared, private or final-stop resolution; mission entry and agreement alone do not close the arc.",
        "closed_behavior": "No recycled quality crisis, duplicate one-off check or repeat payout.",
        "continuing_growth": "Ordinary practical banter, competence, relationships and leveling continue; base dutiful personality unchanged."
      },
      "reward_contracts": [
        {
          "id": "character_blueprints_pilot_001.artisan_02.reward_supplies",
          "player_expectation": "A modest useful share for completed honest teamwork.",
          "setup": "Commit joint check, participate in successful normal mission and document collaboration.",
          "narrative_payoff": "The engineer accepts correction and records joint credit.",
          "grant_proposal": {
            "category": "ordinary_loot",
            "description": "One approved ordinary maintenance-supplies bundle, existing loot table, reviewed amount; grant once per player.",
            "implementation_id": null
          },
          "why_it_fits": "Everyday craft work merits everyday materials, not a fabricated skill.",
          "alternative_branch_fairness": "Private branch receives comparable modest gold; both require equivalent completed work.",
          "review_required": true
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.reward_private",
          "player_expectation": "A modest tangible return without public disclosure.",
          "setup": "Same verified shared inspection and qualifying success, then honest private ledger choice.",
          "narrative_payoff": "Professional responsibility without conjured witnesses.",
          "grant_proposal": {
            "category": "gold",
            "description": "One small approved ordinary gold payment from credible existing resources, economy reviewed, granted once per player.",
            "implementation_id": null
          },
          "why_it_fits": "Private wages/settlement fit practical labor.",
          "alternative_branch_fairness": "Comparable value to supplies, never both payouts.",
          "review_required": true
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.reward_no_test",
          "player_expectation": "A clean choice to stop optional participation.",
          "setup": "Confirmed stop before full accounting.",
          "narrative_payoff": "Identity remains coherent without invented lesson.",
          "grant_proposal": {
            "category": "closure",
            "description": "No bonus, loot or gold.",
            "implementation_id": null
          },
          "why_it_fits": "No validated finished work.",
          "alternative_branch_fairness": "Regular progression unaffected; temporary deferral is not final stop.",
          "review_required": true
        }
      ],
      "aftermath": {
        "remembered_facts": [
          "Single seeded materials miscount, actual prep-check selection, mission outcomes, debrief, mutually exclusive ledger choice and one grant."
        ],
        "retired_hostile_lines": [
          "After a completed collaborative account, retire exclusive-ownership complaints, not craft pride; no racial animus."
        ],
        "new_voice_beats": [
          "Completed: quiet pride in the partner catching an error.",
          "Stopped: ordinary repairs with no assertion of completed inspection."
        ],
        "personality_change_scope": "Dutiful remains dutiful; conditional trust/belonging expand voice only.",
        "relationship_change_scope": "Respect for a reliable collaborator, never romance or automatic loyalty stat."
      },
      "capability_requests": [
        {
          "id": "character_blueprints_pilot_001.artisan_02.cap_individual_error",
          "description": "Add reviewable per-character history:unreported_quality_error and immutable seeded personal facts; facet_error remains tag=null until approval.",
          "reason": "Cannot fabricate autobiographical error.",
          "required_for": [
            "character_blueprints_pilot_001.artisan_02.facet_error",
            "character_blueprints_pilot_001.artisan_02.node_admission"
          ],
          "review_required": true
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.cap_companion_state",
          "description": "Save first talk, choices, professional revelations, once-only player-scoped arc and exclusive endpoints.",
          "reason": "No current conversation/arc state runtime documented.",
          "required_for": [
            "character_blueprints_pilot_001.artisan_02.intro_talk",
            "character_blueprints_pilot_001.artisan_02.arc_ledger"
          ],
          "review_required": true
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.cap_check_observation",
          "description": "Provide explicit prepare_joint_check narrative prep choice, persist check and acceptance, without minigame or stat buff.",
          "reason": "Mission entry alone cannot prove shared inspection.",
          "required_for": [
            "character_blueprints_pilot_001.artisan_02.milestone_check"
          ],
          "review_required": true
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.cap_failure_recovery",
          "description": "Track roster participation, ordinary success versus failure/retreat, actor recovery and debrief.",
          "reason": "Only first later eligible success qualifies, even after failed attempts.",
          "required_for": [
            "character_blueprints_pilot_001.artisan_02.milestone_field",
            "character_blueprints_pilot_001.artisan_02.node_review"
          ],
          "review_required": true
        },
        {
          "id": "character_blueprints_pilot_001.artisan_02.cap_economy_reward",
          "description": "Approve one ordinary loot or gold grant and stable claim per player, with a real source.",
          "reason": "No balance amounts or implementation IDs approved.",
          "required_for": [
            "character_blueprints_pilot_001.artisan_02.reward_supplies",
            "character_blueprints_pilot_001.artisan_02.reward_private"
          ],
          "review_required": true
        }
      ],
      "routing": [
        {
          "from": "introduction",
          "trigger": "intro_talk or intro_share after recruitment",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.artisan_02.node_standards",
          "state_effect": "Unlock standards talk."
        },
        {
          "from": "introduction",
          "trigger": "intro_defer",
          "prerequisite": "No recruitment or story commitment",
          "to": "end",
          "state_effect": "Resume the same character-scoped introduction later with original facts."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.node_standards",
          "trigger": "standards_listen",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.artisan_02.node_admission",
          "state_effect": "Save ordinary voice beat."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.node_standards",
          "trigger": "standards_defer",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "end",
          "state_effect": "Resume standards later."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.node_admission",
          "trigger": "admission_kind or admission_honest",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.artisan_02.node_offer",
          "state_effect": "Reveal only seeded error and repayment motive."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.node_admission",
          "trigger": "admission_pause",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "end",
          "state_effect": "Resume same admission."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.node_offer",
          "trigger": "offer_agree",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.artisan_02.milestone_agreement",
          "state_effect": "Arm player-scoped one-off."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.node_offer",
          "trigger": "offer_defer",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "end",
          "state_effect": "Resume offer later."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.node_offer",
          "trigger": "offer_decline",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.artisan_02.branch_no_test",
          "state_effect": "Confirm final no-reward stop."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.milestone_agreement",
          "trigger": "agreed",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.artisan_02.milestone_check",
          "state_effect": "Wait for eligible normal mission and explicit prep choice."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.milestone_check",
          "trigger": "character_blueprints_pilot_001.artisan_02.prepare_joint_check selected",
          "prerequisite": "Both present and conscious, normal mission prepared",
          "to": "character_blueprints_pilot_001.artisan_02.milestone_field",
          "state_effect": "Commit paired check once; no minigame, no new item."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.milestone_check",
          "trigger": "skip prep or absent partner",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.artisan_02.milestone_check",
          "state_effect": "No check recorded; await next eligible mission."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.milestone_field",
          "trigger": "eligible normal mission success",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.artisan_02.node_review",
          "state_effect": "Save mission success; await conscious camp debrief."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.milestone_field",
          "trigger": "mission failure / retreat",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.artisan_02.milestone_field",
          "state_effect": "Keep completed check; next normal eligible SUCCESS required."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.node_review",
          "trigger": "review_correct",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.artisan_02.milestone_account",
          "state_effect": "Save true debrief."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.node_review",
          "trigger": "review_wait",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "end",
          "state_effect": "Return to saved review."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.node_review",
          "trigger": "review_stop",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.artisan_02.branch_no_test",
          "state_effect": "Confirmed final stop."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.milestone_account",
          "trigger": "debrief recorded",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.artisan_02.node_ledger",
          "state_effect": "Offer exclusive ledger choices; no automatic choice."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.node_ledger",
          "trigger": "ledger_credit",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.artisan_02.branch_shared_credit",
          "state_effect": "Grant approved ordinary loot once per player."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.node_ledger",
          "trigger": "ledger_private",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.artisan_02.branch_private_account",
          "state_effect": "Grant approved modest gold once per player."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.node_ledger",
          "trigger": "ledger_notyet",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "end",
          "state_effect": "Resume ledger without award."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.node_ledger",
          "trigger": "ledger_stop",
          "prerequisite": "Saved prior state; chosen option or verified event",
          "to": "character_blueprints_pilot_001.artisan_02.branch_no_test",
          "state_effect": "Final no-reward stop."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.branch_shared_credit",
          "trigger": "first ordinary companion talk after final ending",
          "prerequisite": "Saved branch closure; one-off aftermath not previously consumed",
          "to": "end",
          "state_effect": "Deliver a branch-specific remembered comment once, then continue ordinary repeatable craft dialogue; no new choice, chain or reward."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.branch_private_account",
          "trigger": "first ordinary companion talk after final ending",
          "prerequisite": "Saved branch closure; one-off aftermath not previously consumed",
          "to": "end",
          "state_effect": "Deliver a branch-specific remembered comment once, then continue ordinary repeatable craft dialogue; no new choice, chain or reward."
        },
        {
          "from": "character_blueprints_pilot_001.artisan_02.branch_no_test",
          "trigger": "first ordinary companion talk after final ending",
          "prerequisite": "Saved branch closure; one-off aftermath not previously consumed",
          "to": "end",
          "state_effect": "Deliver a branch-specific remembered comment once, then continue ordinary repeatable craft dialogue; no new choice, chain or reward."
        }
      ],
      "routing_rules": {
        "status": "review_required, authoring-only",
        "choice_precedence": "Selected choice.next always overrides generic node.next. Generic next is a suggested narrative successor only; it never auto-selects a choice, completes a mission or ends an arc.",
        "resume": "end on defer means return to saved source node; end on completed choice consumes only that interaction. Final decline is a saved exclusive ending.",
        "persistence": "Save verified facts and choice transitions atomically; reload, alternate dialogue wording or another roster member cannot reroll one-off key or grant."
      },
      "routing_state_ids": [
        "character_blueprints_pilot_001.artisan_02.state_joint_check_done",
        "character_blueprints_pilot_001.artisan_02.state_eligible_success",
        "character_blueprints_pilot_001.artisan_02.state_truthful_debrief",
        "character_blueprints_pilot_001.artisan_02.state_artisan_chain_closed"
      ]
    }
  ],
  "proposals": [
    {
      "id": "character_blueprints_pilot_001.proposal_guard_story_family",
      "kind": "story_family",
      "description": "Register guard_warband_accountability as a single player-scoped one-off chain. Reuse original repeat_key, with saved choices, verified outcomes and exclusive reviewed grants.",
      "reason": "Blueprint-local family IDs are authoring references; the current story registry does not contain this family."
    },
    {
      "id": "character_blueprints_pilot_001.proposal_guard_warband_provenance",
      "kind": "history_and_encounter_context",
      "description": "Save individual grievance and optional reviewed pre-encounter affiliation on an existing unnamed procedural hostile Orc within mission budget. No named lore rewrite, post hoc generic Orc match or respawn.",
      "reason": "history:orc_warband_grievance is proposed, and speaker/target predicates cannot prove personal relationship or warband affiliation."
    },
    {
      "id": "character_blueprints_pilot_001.proposal_guard_loyalty_ceiling",
      "kind": "conditional_loyalty_cap",
      "description": "Proposal: before first recruitment of this individual, if player.race is Orc and the assigned grievance/belief is active, disclose loyalty cap 80; only lift on explicit evidenced reconciliation. Distinct from prison resistance; do not retroactively lower current loyalty.",
      "reason": "player.race and individual context-sensitive ceiling are not currently registered capabilities."
    },
    {
      "id": "character_blueprints_pilot_001.proposal_guard_fairness",
      "kind": "persistent_choice_and_bond",
      "description": "Persist prior truthful promise and waived disputed compensation with accurate limited culpability report; only that costly proof can enable trust conversion. Deterministic private contract independent of enemy/capture.",
      "reason": "Trust cannot be inferred from killing Orcs, a single dialogue click or an unchanged speaker.tags snapshot."
    },
    {
      "id": "character_blueprints_pilot_001.proposal_guard_training",
      "kind": "reward_review",
      "description": "Review one permanent anti-Orc damage perk/technique versus defensive training. Approve balance, exclusive grant and implementation_id before promising either; no supplies substitution.",
      "reason": "No approved perk or item ID for this personal specialization exists in the supplied contract."
    },
    {
      "id": "character_blueprints_pilot_001.proposal_artisan_story_family",
      "kind": "story_family",
      "description": "Register artisan_shared_inspection as a single player-scoped one-off chain using original repeat_key, ordinary field participation, authored truth and once-only grant.",
      "reason": "It is a blueprint-local story proposal, not a registered quest template."
    },
    {
      "id": "character_blueprints_pilot_001.proposal_artisan_history",
      "kind": "new_history_tag",
      "description": "Propose history:unreported_quality_error for this specific instantiated engineer only, with immutable seeded details and explicit disclosure gating; do not classify it as existing.",
      "reason": "The draft tag registry cannot support autobiographical detail of an unreported counting mistake."
    },
    {
      "id": "character_blueprints_pilot_001.proposal_artisan_field_check",
      "kind": "scoring_and_event",
      "description": "Offer ONE explicit prepare_joint_check narrative preparation option, no minigame; save paired check and later ordinary mission success/debrief. Failure or retreat retries success only, not preparation.",
      "reason": "mission_entry and mission_success do not establish that a paired inspection happened."
    },
    {
      "id": "character_blueprints_pilot_001.proposal_artisan_payment",
      "kind": "reward_review",
      "description": "Approve one existing ordinary-loot OR modest gold grant for verified work, never both; specify source, economy values and player-scoped claim.",
      "reason": "Economy costs, amounts and loot IDs are not in the provided contract."
    },
    {
      "id": "character_blueprints_pilot_001.proposal_common_persistence",
      "kind": "conversation_arc_framework",
      "description": "Review nonexecuting routing state and player-scoped one-off rewards/chains; introductions remain character-scoped. Save choices, event waits, defer/stop, recovery, endings and once-only post-resolution talks.",
      "reason": "These are draft authoring semantics, not an implemented runtime conversation/story framework."
    },
    {
      "id": "character_blueprints_pilot_001.proposal_guard_private_contract",
      "kind": "trust_evidence_and_guaranteed_recovery",
      "description": "Provide a deterministic ordinary private-contract dispute over an optional compensation claim and limited truthful warband attribution; waiving a real claim is an observable cost, offered regardless of enemy availability. Never fake past lore. If this hook cannot be implemented, do not activate the Orc-player cap.",
      "reason": "Resolves distrust through verified fair action without random encounters or mandatory capture loadout."
    },
    {
      "id": "character_blueprints_pilot_001.proposal_global_one_off_scope",
      "kind": "player_scoped_repeat_policy",
      "description": "Both pilot major arcs retain their exact repeat_key strings, now scope=player; one roster member can claim a chain reward once, not each copy. Character introductions retain character scope.",
      "reason": "Prevents roster-copy story and alternate-branch payout farming."
    }
  ],
  "self_review": {
    "entry_count": 2,
    "duplicate_ids": [],
    "unknown_references": [],
    "overlength_ids": [],
    "unsupported_claims": [
      "Review only: player.race, individualized 80 ceiling, per-character grievance/provenance, authored routing and atomic persistence are not registered live mechanics.",
      "Review only: the guaranteed disputed-compensation contract and truthful-cost tracking require a credible approved claim source; without this, do not activate the conditional loyalty cap.",
      "Review only: enemy prebinding, actual encounter/capture result events and anti-Orc damage/defensive training implementation are unapproved.",
      "Review only: artisan individual quality-error tag, prepare_joint_check choice, mission participation scoring, gold/loot payout need implementation and balance review."
    ],
    "notes": [
      "Two unchanged original entry IDs, 16 original facet IDs, 10 original conversation-node IDs, both original arc IDs, all original milestone IDs and six original reward IDs preserved.",
      "Original entry, facet, node, arc, milestone, branch, reward and capability IDs preserved. Added guard node_quiet_account, boundary_private and four quiet choices; artisan review_stop, ledger_stop and namespaced prepare_joint_check; review-only routing/state metadata and root revision=2. No original IDs retired.",
      "Major arc repeat_key strings preserved, scope changed from character to player. Introduction repeat policies remain character-scoped.",
      "Guard evidence/trust and artisan review/ledger now have incoming routes. No intended conversation, conditional milestone or ending is left without an authored entry path; conditional combat still needs its proposed generation hook.",
      "Reconciliation requires a documented sacrificed claim; Orc kills alone do not convert beliefs. Guard specialism can propose permanent anti-Orc damage OR defensive training; no forced capture or supplies substitution.",
      "Artisan: one narrated prep selection plus actual mission success, with failure/retreat retry of ordinary mission only.",
      "Author self-review only; no official contract or engine validator is claimed.",
      "All authored route destinations have IDs; conditional enemy path depends on review approval, but deterministic quiet fallback does not depend on enemy spawn. No dead-end intended after event failures."
    ]
  }
}
```

## Reviewer findings (reference for the current task)

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
