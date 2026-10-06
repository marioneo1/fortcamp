# Rogue rework review

October 5, 2026. **Design review only; not implemented.** User clarification: multiple Quick Actions are allowed. Backflip is a Quick Action, including after the main attack. Preserve Fighter, Barbarian, Monk, five character slots, gear abilities outside those slots and existing saves.

## Inspected current implementation

`backend/job_loadouts.py` supplies Open Wound, Pocket Sand, Footwork, Venom Edge, Pinning Strike and Close Counter. These overlap control/counter kits rather than implementing the proposed positional saboteur. `backend/combat_abilities.py` already provides IDs, bounded effects, owner-activation cooldowns, charges, availability and snapshots. Every current active spends the main action. `backend/combat.py` marks the action and automatically finishes the activation for `skill` and `attack`; the engine has no Quick Action budget or post-main-action casting flow.

Movement is provisional from START until commitment. The final committed path charges per-cell hazards; discarded previews are free. `_apply_displacement` already passes traversed push/pull cells to `_apply_zone_route`, with route/contact feedback. Existing zones can trigger once per actual tile entry, but most statuses and binding zones have activation caps. Prepared defense traps are enemy-only, single-use terrain and resolve principally at the committed endpoint. Do not use that older representation unchanged for a persistent Caltrop strip.

Bleed and Hobbled are currently single refreshed statuses: `conditions.apply` removes an existing copy before adding one. Hobbled halves movement with a minimum of one; extra copies do not currently intensify it. Bleed currently deals 2?4 physical HP damage after an activation in which its owner moved or used a physical action; it is not an automatic poison-style activation-start tick. Stacked Bleed needs explicit extension. Current attack validation permits 100?300% power, so Crippling Cut at 25% and Exploit Weakness at up to 400% need narrow bounds/validated identities rather than bypassing validation.

The current battle UI supports unit/ground targeting, movement-plus-casting forecasts, cancellation, hotkeys, square icons and saved skill ordering. It lacks enemy-then-destination targeting and a rotated strip with explicit confirmation. Construction has its own placement controls; reuse their interaction conventions, not the whole base editor or save API.

Base HP is currently derived from attributes, race and equipment rather than a separate HP tier for each Job. Rogue will lose its old generic evasion/counter passives in this replacement, and will have no healing/protection engine. Do not claim a literal automatic low-HP Job modifier unless separately implemented and documented.

## Action economy: multiple Quick Actions

No shared one-Quick-Action cap. Each equipped Quick Action can be used when its own cooldown permits. Cooldowns of at least two activations prevent repeatedly using the same skill during one activation. No resource meter.

Crippling Cut, Shadowstep and Backflip are Quick Actions. Cheap Shot, Exploit Weakness and Caltrops use the main action. Throwing Knife is an attack-mode modifier, not a second damaging skill or an additional Quick Action charge.

A Quick Action commits the prior provisional movement and locks normal walking for the rest of the activation. The main action also commits normal walking. Neither lock is a Root/Bind status: Shadowstep and Backflip must remain available after that lock. Actual immobilizing control, incapacitation, carrying restrictions and map legality still apply. Never implement this by returning zero from the entire mobility calculation and then accidentally prohibiting the escape skills.

Rogue main attacks must not immediately advance the turn if a legal equipped Quick Action can still be used. Keep the actor current for the post-attack window; the main attack remains spent. End Turn finishes the activation. If no usable Quick Actions remain, finish automatically; a clear End Turn control remains available even when a cooldown-ready action has no useful target. Do not change other Jobs' automatic finish. Example: move ? Crippling Cut ? Exploit Weakness ? Backflip ? End Turn; or Shadowstep ? Cheap Shot ? Backflip ? End Turn. An unspent main action still allows the existing end-turn Guard; an already spent main action never gives a free Guard.

Quick Actions do not increment cooldown/status clocks, expire ground zones, trigger a second summon phase, or tick Bleed again just because another command was sent. Exactly one finish-activation pass runs when the actor actually ends. The enemy waits for each action's playback; the player cannot race a follow-up through unfinished impact/forced movement. Queued follow-ups must be revalidated against the resolved position and living targets. Orders, hotbar rearrangement and cancelling previews spend nothing.

## Recommended eight-skill pool

| Skill | Recommended V1 | Action / cooldown |
| --- | --- | --- |
| Cheap Shot | Adjacent positional attack. Highest of 100%, 150% for another occupied side, 200% for opposite sides, 220% for three sides or 250% for four sides. Cardinal adjacency only. | Main / 1 |
| Crippling Cut | 25% base attack; a landed hit adds one Hobbled stack lasting two target activations. Lock ordinary walking after commitment, including on a miss; retain the main action. | Quick / 3 |
| Exploit Weakness | 100% + 50 percentage points per qualifying negative stack, capped at 400% base attack. Preview lists the counted statuses and stacks. | Main / 2 |
| Shadowstep | Choose a visible enemy within three Manhattan cells, then choose a legal adjacent destination and confirm. No damage or automatic attack. Lock ordinary walking after commitment. | Quick / 3 |
| Caltrops | A centered horizontal/vertical 1?3 strip, all three cells legal, placement center within three cells with clear line of effect. Each actual entry attempts one Bleed and one Hobbled stack. Lasts until the start of the Rogue's second subsequent activation. | Main / 4 |
| Backflip | Choose a legal cardinal landing one, two or three cells away; reuse leap wall/sight/elevation/carrying checks. No attack. Can be used after the main action; locks ordinary walking. | Quick / 2 |
| Trap Expert | The Rogue does not trigger tagged traps, including Caltrops, while this passive is equipped. Does not negate fire, poison zones, pits or arbitrary terrain hazards. | Slotted passive |
| Throwing Knife Technique | Arm a thrown delivery for basic Attack, equipped Cheap Shot or equipped Exploit Weakness. Hit a visible target beyond normal melee reach, within three cells, with a clear projectile path. No extra damage multiplier or separate attack. | Modifier; uses the chosen main attack / 3 |

Cooldown 1 means ready next personal activation; 3 means the third subsequent activation. The table is initial tuning, not playtested balance. All eight choices remain visible in progression; normal five-slot opportunity costs apply. Suggested starter: Cheap Shot, Crippling Cut, Exploit Weakness, which gives a solo Rogue an immediate setup/payoff. Suggested unlocks: Shadowstep at 2 successes, Caltrops at 5, Backflip at 9, Trap Expert at 12, Throwing Knife at 16. Battle Lab should expose full pool at 16 and mixed parties for surround/trap tests.

## Position and thrown delivery

Count the four sides actually occupied by living conscious allied combat units, including the Rogue's strike side. Bodies, structures, neutral units and wall-separated allies are not attackers. Count sides, not the number of units; diagonals do not contribute. Combat summons can contribute a legal occupied side; do not arbitrarily exclude allies solely for being summoned. Recompute at resolution, including after movement/interception, using the resolved recipient.

Knife delivery derives one virtual cardinal strike side from the direction of the incoming projectile, without mutating coordinates or causing entry hazards. Use the dominant axis; resolve exact ties consistently and show the selected side in the forecast. The virtual side counts once even if an ally already occupies it. It is not an extra fifth surrounding unit. Physical Cheap Shot starts at adjacency 100%; ranged Cheap Shot uses that virtual side plus actual allied sides. A normal ranged attack alone does not earn a positional bonus.

Arming Knife or selecting an eligible attack is a free UI choice. Only a committed thrown main attack spends both Knife's cooldown and the selected attack cooldown. A committed miss still spends them. Cancellation, invalid target or lost line of sight spends neither. No automatically learned/unequipped attack is granted. Initial compatible attacks are basic Attack, Cheap Shot and Exploit Weakness; Crippling Cut remains a close-contact Quick Action. This small explicit compatibility list can expand later without making Knife a universal ranged conversion for every weapon skill or area attack. Capture weapons retain their subdue-only rule.

## Stacks, damage and counterplay

Add stack-aware storage specifically for Bleed/Hobbled, retaining old one-stack statuses and all unrelated status behavior. Each application keeps its source and two-target-activation expiry; adding a stack does not make all old stacks immortal. The UI shows aggregate counts plus clear duration/source details. Resist Bleed and Hobbled independently using the existing status resistance pipeline. Cleansing removes the matching stacks. Do not silently cap the stacks at three: three is just one strip's maximum in a straight traversal, not a global stack limit.

Hobbled stacks count individually for Exploit but do not repeatedly halve movement. One or six stacks still halve it once, minimum one; Bind remains the immobilizer. Bleed stacks each contribute the existing per-stack exertion damage, resolved once at activation end if movement/physical exertion occurred. Do not charge the full stack damage after every preview, command or Caltrop cell. Newly acquired stacks participate in the next genuine exertion resolution. This keeps the environmental setup powerful without introducing an accidental burst of six Bleed ticks in one movement packet. Source credit and actual damage statistics must remain truthful for multi-owner stacks.

Exploit's count uses an explicit negative-status allowlist. Examples: Bleed/Hobbled count each stack; poison, burn, blind, slow, stun, sleep, freeze, bind, paralysis, fear, silence, armor fracture and actual enemy debuff Mark count their represented negative layers. Monk's three Exposed Guard stacks contribute three; Open Guard contributes one. Guard, Barrier, Footwork, parry, regeneration, knockback resistance, recovery immunity, cooldown readiness, corpses and merely standing on a zone contribute zero. A single status row with `turns:3` is one debuff, not three stacks. Count before consuming a one-use Vulnerable bonus. Never infer debuff status from a UI color or substring.

Cheap Shot and Exploit Weakness are separate main attacks. Knife changes delivery, not damage. Consequently these cannot accidentally become 2.5? ? 4? from one main attack. Exploit's cap is its authored skill coefficient, not a global ceiling on gear and ally amplifiers. Existing target damage amplifiers remain explicit; Monk's exposure/Open Guard already add together. Apply the chosen Rogue coefficient to base attack, then ordinary armor/equipment/target rules once. Example: a fully stacked 400% Exploit against 30% Exposed Guard plus 25% Open Guard can reach 620% before armor/other rules. This is intentional supported setup, not an accidental product of two Rogue skills.

## Trap traversal and placement

Caltrops affect enemies and allies, including their owner, unless Trap Expert is equipped. Each traversed cell applies its two independently resisted stacks. Standing still does not repeatedly trigger them. Real re-entry after leaving a cell is a new entry and may trigger again. Ordinary committed walking, push/pull, ground Dash and true landing all use the shared entry path; a teleport does not walk through its intermediate cells, and a leap only triggers its actual landing. Corpses do not gain stacks or trigger live trap processing.

Overlapping strips on the same cell produce one Caltrop entry, not one per owner. Different consecutive cells still trigger separately. One owner's recast replaces their prior strip. Route/step identity prevents replaying the same committed event twice without confusing a later legitimate revisit with a duplicate. Preserve source attribution when overlaps are deduplicated. Reversible movement previews and discarded routes never add stacks.

UI: select Caltrops ? preview all three tiles ? R rotates ? click selects the placement ? explicit Place/Confirm. C/Escape and dropping a drag outside the map cancel. A partially illegal strip is shown invalid, not silently shortened into another shape. Copy construction's familiar rotate/preview/cancel conventions while keeping battle input, costs and server validation separate. There is no existing shared instant-placement preference to adopt blindly; explicit confirmation is the initial behavior.

Shadowstep: enemy selection shows legal cardinal adjacent landings; choosing one shows destination, exposed allies/opponents and resulting Cheap Shot geometry. Confirm commits one atomic command. A closed wall/gate between target and candidate excludes that side; visible enemy targeting never reveals other concealed occupants. Server rejects newly occupied destinations without spending cooldown or Quick Action. Backflip uses cardinal endpoint selection and the existing landing legality; actual Root/Bind/freeze prevents it, but the normal-movement lock does not. Do not add opportunity attacks as part of this Job pass; current counter reactions remain tied to attacks.

## AI, visuals, migration and implementation order

AI should choose opportunities rather than a fixed rotation: compare current positional/Exploit forecasts, consider Shadowstep landings, use Cut when it improves the following burst, lay strips on likely approaches, and Backflip after attacking if a safer legal landing exists. Existing hidden personality weights aggression/risk. Use a bounded plan of the equipped cooldown-ready Quick Actions plus one main action, mark each spent once, then end. Do not implement recursive action selection that retries an impossible teleport forever or scans a large action tree each render.

Use one coherent packed Rogue icon/effect atlas when implementing: eight square ability icons plus thrown knife, cut contact, strip tile, shadow departure/arrival and Backflip trail. Keep light melee flesh/hard-contact sound families, landing/teleport/trap contact timing and enemy serialization. No images or audio are generated in this review.

1. Add quick/main state, normal-walk lock and post-main window, including AI and animation locks; test move ? quick ? main ? escape.
2. Implement position/debuff counting and cheap/cut/Exploit forecasts with migrated five-slot loadouts.
3. Add chosen-destination Shadowstep, Backflip and Knife delivery; validate cancellation, blocked edges and hidden targets.
4. Add stack-aware Caltrops, per-cell forced routes, Trap Expert, attribution and readable stack feedback; test Fighter/Monk interactions.
5. Import packed art, test all eight in Battle Lab, inspect real UI/playback, compare equal-tier martial kits and tune.

Map old skill IDs deliberately, preserve earned practice/learned skills/order and leave active battle snapshots intact. No production changes or save rewrite in this review. Tests must cover one main plus several distinct Quick Actions, no second main attack, no free post-main Guard, mobility after ordinary-lock versus true immobilization, clocks/bleed ticking only once, cancellation, cardinal geometry/virtual ties, debuff counts, stacks/expiry/cleanses/resists, trap route deduplication, ground hazards, proc budgets, AI termination and serialized defeat/escape playback.

## Changes from the brief

Keep multiple Quick Actions per user clarification and classify Backflip as Quick. Add a post-main-action escape window to avoid a useless Backflip button. Keep Hobbled stack count without exponential movement reduction. Retain Bleed's existing exertion timing while extending stack contributions. Treat Knife as a delivery modifier with an explicit compatible main-attack list. Cheap Shot and Exploit remain alternatives, not additive skills in one attack. No global Rogue damage cap, extra resource meter, formal combo, blanket trap immunity to non-trap hazards or overall combat rewrite.
