# Monk rework review

October 5, 2026. **Accepted and implemented in dev.** The sections below preserve the inspected rationale and agreed initial tuning; they are not a claim of final gameplay balance. The map-status spacing adjustment described in the history is implemented separately. This review preserves the finalized Fighter and Barbarian, twelve starting Jobs, five shared active/passive slots, equipment abilities outside those slots and existing combat turns.

## Pre-rework inspection and reuse

Before this pass, `backend/job_loadouts.py` gave Monk Driving Palm, ally Brace, Riposte, Joint Lock, Returning Hand and Patient Stance. This is predominantly displacement, protection and counters, overlapping Fighter rather than producing a sequence-based damage dealer. There was no combo state or multi-hit technique resolver.

`backend/combat_abilities.py` already has stable skill IDs, learned/equipped snapshots, ordered effects, hit conditions, owner-activation cooldowns and charge limits. Cooldown 1 means ready on the next personal turn; cooldown 3 means ready on the third subsequent personal turn. Selecting a skill or hovering does not tick these clocks. The pre-rework validator permitted only one attack effect and attack power from 100% to 250%; the implementation adds explicit multi-hit support and a narrowly extended power range, not several attack effects slipped past validation.

`backend/combat.py` already provides accuracy previews, deterministic hit rolls, movement plus casting, walls/doors, line of sight, reactions/interception, committed-path ground damage, Barrier absorption, attack packets and synchronized feedback. Hit chance can reach 100%. The inspected direct-attack resolver does not supply an ordinary critical-hit result; do not invent a critical guarantee for Crushing Fist.

Damage currently subtracts flat armor per damage call and adds flat weapon/perk damage in that same call. Weapon on-hit effects can roll per call. Simply calling that resolver three times would overcharge armor and multiply equipment bonuses/procs. Shared reactions are already limited, but their evaluation must occur after the complete technique rather than interrupting its individual punches.

The current Vulnerable effect is a one-use reduction of 3 armor, **not** 25% increased damage. Normal status durations use target turns; the proposed offensive setup needs an explicitly source-owned expiry so a fast enemy does not erase it before the Monk can finish.

Base HP is driven by VIT/race/perks, not a separate HP tier for every Job. V1 should distinguish Monk durability through its kit rather than silently rebalancing Fighter/Barbarian or adding equipment restrictions. The existing hotbar, saved ordering, slotted-passive tooltips, availability reasons, readiness badges and Barbarian resource presentation can be extended for Monk.

## Recommended eight skills

Numbers below are initial tuning targets. Percentages are attack power before defense, not guaranteed final HP damage. All techniques use the main action. No Ki meter or additional action is needed.

| Skill | Function and starting numbers | Cooldown |
| --- | --- | --- |
| Rapid Palm | Adjacent opener; three separately rolled punches, 120% total attack budget. Each landed punch adds 10% Exposed Guard for three target turns, capped at 30% and refreshed on hit. Two or three hits guarantee Follow-up Ready; one hit has an 80% progression chance; zero hits do not advance. Stop striking a defeated target. A lethal hit still counts. | 1 |
| Crushing Fist | Adjacent opener; one 150% strike. A landed strike has a 70% chance to grant Follow-up Ready. After successful combo advancement, roll a 50% one-turn stun, reduced by status resistance and blocked by recovery. | 1 |
| Iron Reversal | Follow-up; adjacent 100% strike. A hit grants Finisher Ready and a defensive form reducing the next direct attack's damage by 20%, expiring at the start of the next Monk turn if unused. Also grants +25 evasion against the struck enemy until next Monk turn start. Self only; no ally protection or automatic counter. | 1 |
| Breaking Combination | Follow-up; adjacent two-punch technique, 120% total budget. Any landed punch advances to Finisher Ready. Apply Open Guard after the combination: 25% more direct attack damage from any ally until the end of the applying Monk's next turn. No stacking. Grants Combat Rhythm: 3 HP per landed attack for the next three Monk turns; individual punches and crossed Dash enemies count. | 2 |
| Heaven-Piercing Strike | Finisher; 300% attack, three-cell Manhattan reach with clear line of effect. A physical palm-force release, not a teleport, jump or defense bypass. Consumes the stage on use. | 3 |
| Sweeping Dash | Ground target; up to three traversed cells. Pass through enemies for one 50% hit per crossed enemy, then land on a legal empty tile. Walls, closed gates and impassable terrain block it. Grants 10% single-target physical melee/ranged parry until next Monk turn. Magic/AoE excluded. No combo advancement or extra action. | 2 |
| Perfect Rhythm | Slotted passive. Follow-ups gain 10 percentage points of accuracy. A ready finisher cannot miss; defenses, interception and barriers still work. No critical guarantee. | Passive |
| Flowing Footwork | Slotted passive. Advancing to Follow-up Ready or Finisher Ready grants +1 movement for the next Monk turn and +10 evasion until the end of that turn. Refreshes; does not stack. No extra turn or repeated bonus for merely restarting the same stage. | Passive |

Iron Reversal protects against a direct attack, not poison, burning ground, pits or collision damage. For multi-hit incoming attacks, its reduction covers the entire incoming technique, not just its first punch. It is weaker than Fighter's 25% protection and costs a combo-stage action; its advantage is continuing offense while preparing the finisher.

Open Guard benefits direct attacks, including other allies, but does not amplify poison/burn ticks, ground hazards, collision damage or environmental falls. This deliberately narrows the proposed “all damage” amplifier. Apply after the follow-up's own damage, so it does not boost itself. Use one modifier per target; a later application replaces the previous ownership/expiry rather than stacking copies. Clean up when the source permanently leaves battle, and when its scheduled expiry occurs. Skipped turns still expire it. Display its source and precise expiry. Cleansing can remove it. Additional amplification from other systems needs a documented combination rule; do not accidentally multiply two copies of this status.

## Combo rules

- Each stage becomes usable on the **next** personal activation. It remains available through the end of the following two personal activations. Example: opener on turn 1; follow-up may be used on turn 2 or turn 3, then the stage expires.
- Basic attacks, equipment actions, Guard and Sweeping Dash do not immediately erase readiness. They use time in that existing window. Stunned/skipped activations count, giving control effects meaningful counterplay.
- A landed follow-up always advances; it has no second progression roll. A missed follow-up leaves the old stage available until its original expiry; it does not extend that window.
- A new opener deliberately restarts setup and replaces existing readiness with the result of that opener. Its failed progression does not retain a previously ready finisher.
- Using a finisher consumes readiness even if it misses without Perfect Rhythm. Completing a finisher does not trigger Flowing Footwork. Changing targets is allowed, and defeating the setup target does not discard the chain.
- Death, capture, extraction and battle completion clear the chain. Inspection, polling, equipment UI and loadout-order changes never advance or reset it.
- Show Neutral / Follow-up Ready / Finisher Ready beside the acting character, with remaining turns. Explain locked follow-ups/finishers in skill availability and tooltips. Do not expose hidden enemies through readiness or target forecasts.

This permits one utility turn without unlimited preparation. Choosing utility before a finisher can lose Open Guard's shorter damage window: a visible tradeoff rather than a hidden timing bug.

At 90% individual accuracy, Rapid Palm lands at least two punches 97.2% of the time. Including the 80% one-hit fallback gives 99.36% opener progression, versus 63% for Crushing Fist. At 70% individual accuracy these become 91.98% versus 49%. These are probabilities for this implemented rule, not measured balance results. Rapid Palm is intentionally a reliable setup option; Crushing Fist trades reliability for immediate damage. No opener is guaranteed through blind or extreme evasion.

## Multi-hit resolution and proc budget

Represent one technique with a hit count, total attack budget and authored contact offsets. Split the total flat armor burden and additive damage bonuses across those hits, preserving rounding remainders. Do not impose the entire armor subtraction or minimum-one-damage floor separately on every punch. Each punch rolls accuracy, contributes only its own allocated damage on hit and absorbs remaining Barrier normally. Allocate one-use outgoing/incoming bonuses to the complete technique before splitting; they are consumed by that attack even if it misses. Do not alter the semantics of existing single-hit abilities.

Example with attack 20 and armor 6, without other modifiers: Rapid Palm's full landed budget is 24 - 6 = 18, distributed as three base 6-damage punches, then Exposed Guard raises later landed slices (6, 7, 7 at this scale). Repeating the current resolver at 40% would instead produce three 2-damage punches and accidentally invalidate the intended skill. A partially landed sequence receives only the landed portions. Barrier 10 absorbs the first 6 and then 4 of the second; later hits can reach HP. All three punches with the new exposure cause 10 HP loss after that Barrier, rather than the original 8.

Generic weapon on-hit procs get one eligibility check per technique per target after at least one hit, not three independent attempts. Generic flat on-hit bonuses have one budget. Resolve shared counter reactions once after the technique. Explicit future equipment that says “per punch” can opt in deliberately; this is not a gear-active limit. Area/movement attacks retain one attempt per actual target, not one global proc for the entire group. Stop damage to a defeated unit and record only actual HP loss for statistics.

Animation packets must carry individual punch contact offsets. Damage, Barrier feedback and hit reactions occur at those contacts; defeat follows the lethal contact, and the next actor waits for the complete packet. A multi-hit skill must not be three disconnected melee lunges or three overwritten animation events.

## Sweeping Dash boundaries

Use a short, previewed traversal route. It may pass through enemy-occupied cells specifically for this technique, but cannot end on a unit, solid prop, wall or closed door. It cannot cross a diagonal wall corner or jump a pit like Earthbreaker. Avoid double hits from crossing one enemy's footprint more than once. Allies take no damage.

The preview shows the route, crossed targets, landing tile and committed ground damage. Charge hazards for every traversed affected tile, using existing movement rules. Discarded previews remain free. Commit any prior provisional walking path before the dash route; do not count the same segment twice. Death or immobilization interrupts traversal at its real contact. Range three limits the dash's traversal itself; ordinary pre-cast movement may precede it, as for other skills.

## Progression and five-slot builds

Start with Rapid Palm, Iron Reversal and Heaven-Piercing Strike, giving a complete chain immediately. Unlike the current two-active/one-passive starter convention, these are three actives; the existing registration/loadout structure permits it. Implemented unlocks: Perfect Rhythm at 2 successful contracts, Crushing Fist at 5, Sweeping Dash at 9, Breaking Combination at 12, Flowing Footwork at 16. All eight are published in the Job progression view from the outset.

Example loadouts:

- **Reliable skirmisher:** Rapid Palm, Iron Reversal, Heaven-Piercing Strike, Perfect Rhythm, Sweeping Dash. Predictable setup, one-hit protection, mobility; gives up vulnerability and passive evasion.
- **Offensive sequence:** Rapid Palm, Breaking Combination, Heaven-Piercing Strike, Perfect Rhythm, Sweeping Dash. Ally damage setup and earned payoff; no defensive follow-up.
- **Adaptive martial artist:** Rapid Palm, Iron Reversal, Breaking Combination, Heaven-Piercing Strike, Flowing Footwork. Chooses offense/defense mid-chain; lacks dash and guaranteed finisher accuracy.
- **Aggressive opportunist:** Crushing Fist, Breaking Combination, Heaven-Piercing Strike, Sweeping Dash, Flowing Footwork. Immediate pressure and mobility; substantially less reliable progression and no miss-proof finisher.

The player can omit the finisher for a simpler technique/gear-oriented build, but its pool still has real opportunity costs. No sixth free Job skill, mandatory passive or new gear cap.

## Balance, AI and presentation

With the October 5 buff and no defense/rounding, a fully landed offensive sequence is approximately 132% + 156% + 465% = 753% attack over three personal turns. The defensive sequence is approximately 132% + 130% + 390% = 652%. Exposed Guard adds up to 30% and Open Guard adds 25%; together they give 55%, not a multiplicative 62.5%. These are ideal setup ceilings, not guaranteed DPS. Fighter can deliver immediate disruption/AoE without setup; Barbarian has early 200% damage, Fury/low-HP bonuses and substantial kill healing. Monk's competitive strength is repeated single-target pressure and mobility, paid for in slots, sequencing and missed setup opportunities. Keep the finisher at cooldown 3 initially; raising it to 4 creates an unnecessary gap in the fastest three-turn loop.

Counterplay: deny melee setup, break line of effect, use control to waste readiness, reposition, shield the payoff, intercept, cleanse Open Guard, or force the Monk to choose Iron Reversal/escape over offense. Low-damage punches do not ignore armor; Perfect Rhythm does not ignore protection. Monk gains no heavy healing, team interception or permanent armor passive. Do not promise lower class HP until a separate Job-stat policy is actually approved.

Auto-battle needs stage-aware choices, not simply the first available attack. Score finishers against valuable reachable targets, preserve a stage for necessary survival/objective actions, choose defensive follow-up under pressure, prefer reliable setup normally, and use dash only when its landing improves survival/objective pressure. Existing hidden personality may weight aggression and risk; it must not bypass legal targeting, combo gates or costs. Expose the same legal action/preview data to player, Lab and AI. No extra map-wide planner or per-frame database work is required.

Presentation should use the existing square hotbar/readiness icons and a compact three-stage display. Produce one coherent packed icon sheet for the eight skills and stage/form icons when implementation begins. Author punch contact timing, defensive-flow accents, the dash trail and physical finisher impact; use flesh/hard-contact audio families rather than generic magic casting. The implementation imports one coherent 4?4 icon/effect atlas; see ../art/MONK_V1.md. Audio reuses approved fist flesh/hard-contact sounds, with quieter repeated swings; no new audio was generated.

## Implementation gates and verification

Small engine extensions: technique-scoped multi-hit resolution; owner-clock combo requirements and advancement; a bounded enemy-crossing dash; explicit temporary defensive form and source-clock Open Guard. Extend existing ability definitions and validation rather than creating a parallel skill system. Keep definitions authored and bounded.

Monk IDs/loadouts require an explicit migration from six existing skills to eight new skills. Preserve earned progress, map retired IDs into sensible unlocked replacements, deduplicate, preserve five-slot limits and publish a truthful migration summary. Already-running battle snapshots should finish on their existing kit. Combo state is battle-local, starts Neutral and persists through reconnects.

Verification scope: test stage timing/expiry and reconnect; miss/partial-hit/lethal-hit transitions; Barrier/armor/rounding; one-use damage/protection and per-technique procs; interception/counters/Fury interactions; source-owned vulnerability expiry and cleanse; dash walls/doors/corners/occupied landings and committed hazards; player/AI parity; migration; and browser contact/defeat/input-lock playback. Test five-slot builds against the same Battle Lab enemies and weapon tiers as Fighter/Barbarian. Do not report the numerical proposal as validated gameplay balance.

## Changes from the supplied proposal

Recommend reliable hit-based follow-up progression, two-turn readiness windows, no invented critical-hit guarantee, attack-scoped armor/proc handling, direct-attack-only vulnerability, movement/evasion instead of cooldown acceleration, and a full starter combo. Preserve all eight skill roles, long-range earned payoff, both opener/follow-up decisions, five-slot customization and the existing Job system.

## Implementation and verification record

The eight definitions, complete three-active starter, deterministic combo state, technique-scoped multi-hit budget, short enemy-crossing dash, temporary forms and stage-aware AI are implemented in dev. State uses existing personal activations, not timers. Perfect Rhythm is still a slotted passive, not a free innate bonus. Existing regular Monks receive an idempotent retired-ID migration preserving earned skills/practice, ordering and the five-slot limit. A player-facing migration note explains the replacement. Already-running battle snapshots retain their existing authored abilities.

The battle hotbar has eight matching packed icons, a three-stage acting-card meter, source-owned status tooltips, physical contact artwork, a defensive-flow aura and a physical finisher release. Individual punch damage/audio share contact timestamps, and existing playback locks serialize the next actor. Sweeping Dash previews route, empty landing, visible crossed targets and committed ground damage; hidden units remain hidden in forecasts. Burned ground charges every crossed tile on commitment. Interrupted movement on an occupied enemy crossing returns to the last empty route tile without creating a second normal walk.

Automated coverage includes combo gates/expiry/misses/lethal hits, armor/Barrier/rounding, one-use modifiers, proc/counter limits, Open Guard expiry and Unstoppable, Footwork clocks, hidden enemies, dash blockers/hazards, preview immutability, migration and auto selection. Browser fixture checked Neutral ? Follow-up ? Finisher display, all five equipped icons and playback completion without runtime errors. A full Monk Goblin Warcamp preview measured approximately 19?23 ms locally. This is a small development sample, not a deployment latency guarantee. Frontend build passes with the existing large-bundle warning. Manual balance comparisons, broader weapon interactions and final aesthetic approval remain to be played in Battle Lab. Production and player save files were not changed.

### What +10 evasion means

Flowing Footwork adds ten **evasion stat points**, not ten percentage points of dodge. Current accuracy formulas subtract 0.6 times evasion for ordinary melee, 1.0 for ballistic ranged attacks, and 0.3 for magic using the ignore-elevation rule. Away from accuracy limits this changes enemy hit chance by approximately 6, 10 or 3 percentage points respectively. Other accuracy modifiers, resistance rules and the hit-chance clamp can reduce the actual change; Perfect Rhythm's guaranteed finisher remains guaranteed.

## October 5: accepted buff and selective boss resistance pass

Rapid Palm's exposure stacks between contacts, is refreshed for three target activations, caps at three stacks and affects direct attacks from any ally. It adds to Open Guard. Poison, terrain, collisions and falls do not receive these amplifiers. Technique armor/additive/proc budgets remain shared; later punches scale their allocated portion by the current exposure. Full-hit forecasts include that progression. Unstoppable can cleanse exposure as a harmful status.

Crushing Fist rolls its stun only after its landed hit successfully advances the combo. Base stun chance is 50%; a 25% stun-resistant chief reduces that to approximately 38%, independent of the earlier hit and advancement rolls. Control recovery still blocks application. This is not a guaranteed stun or an ordinary attack critical-hit mechanic.

Iron Reversal's next-hit reduction stays 20%. The additional 25 evasion is tied to the struck enemy and lasts until next Monk activation start, even if the reduction has already been consumed. It does not protect against other enemies. Normal melee loses about 15 percentage points of accuracy; combined with the one-hit reduction this is a useful short defense without granting a tank kit.

Breaking Combination grants Combat Rhythm after its own contacts: up to 3 HP on each subsequent landed attack through the end of the next three Monk activations. Barrier-absorbed landed hits count; misses, poison/ground/collision damage do not. Each punch and each Dash victim counts, and healing cannot exceed max HP. It is hit-triggered recovery, not a free start-of-turn regeneration tick.

Sweeping Dash grants 10% parry on completion until next Monk turn start. The preview folds this into single-target physical melee/ballistic hit chance; parried contacts show ?Parried.? Elemental magic and area attacks bypass it. Perfect Rhythm's explicitly guaranteed finisher remains guaranteed. Dash's effect refreshes without stacking; no extra action/reaction budget is created.

Boss resistance lives in the existing conditions pipeline. A chief generally has 25% stun resistance, cartmasters resist binding (40%) and slowing (25%), caster bosses resist burn (50%) and silence (25%); inorganic/undead poison immunity remains. Authored `status_resistances` can override the selective profile. Racial resistance and boss resistance use the stronger value, not two hidden multipliers. No blanket debuff resistance is introduced. Boss control duration is still capped at one target turn and post-control recovery prevents immediate stun-locking; these are shown separately from innate percentages in unit inspection. Unlisted debuffs remain available for strategy. Numerical buffs remain initial tuning; test a fresh battle because already-running skill snapshots retain their authored descriptions.
