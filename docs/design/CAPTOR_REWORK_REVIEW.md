# Captor and Resolve - implemented October 7, 2026

Captor is an isolation/control specialist for taking enemies alive. This is the dev implementation; numerical balance and advanced personality-driven AI remain open.

## Capture rules

Capture tools provide two independent basic commands: **Attack [A]** is lethal unarmed damage with the existing punch delivery; **Subdue [N]** uses the existing capture/net delivery and reduces Resolve without HP damage. Other Jobs can use basic Subdue with eligible equipment. Captor techniques do not require a capture weapon; basic Subdue does.

Maximum Resolve initially equals maximum HP. HP and Resolve remain independent thereafter. Resolve mitigation is `100 / (100 + 2 * (INT + AGI))`; ordinary armor does not mitigate it. Resolve power is `6 + balanced rating + tool quality / 4`, where balanced rating is the lowest STR/DEX/INT plus 35% of the difference between their average and lowest value. No equipped capture tool uses quality 8 for Captor techniques. Resolve damage rounds to whole points, minimum one while Resolve remains.

At zero Resolve the target is Capture Ready but remains conscious and active. Every successful Resolve-damaging hit (Subdue, Subduing Blow, Bola, Hook and Drag) makes a capture check when Resolve is zero afterward, including the hit that empties it. Hold makes its own repeated checks at zero Resolve. Misses never roll capture; failed capture checks leave the target conscious. Contact accuracy and capture odds are shown separately. Wounds do not increase these new capture odds.

Authored base_capture_chance overrides defaults of 35% for ordinary enemies and 1% for bosses/chieftains. Existing perk/gear capture bonuses are added, tool quality above 8 multiplies by `1 + (quality - 8) / 100`, then Clean Capture multiplies by `1 + current HP / maximum HP`. Final chance is bounded to 0-95%. A 1% boss with no other bonuses becomes 2% at full HP with Clean Capture; existing Captor traits may raise that actual value.

Success uses the existing unconscious/carrying/prison pipeline, without lethal damage procs or death effects. Explicitly captured unconscious enemies are collected when the map completes, including completion by retreat/failure, unless lost/fled/temporary. Victory's existing recovery rules still apply to other unconscious enemies. Capture does not automatically recruit a prisoner.

## Eight skills

| Skill | Behavior | Cost |
|---|---|---|
| Subduing Blow | 1.5x Resolve power; isolation adds 1x plus 0.5x each unique Hobble/Disarm/Stun, maximum 4x; 25% chance to select one control effect, then resistance applies. | Main; no cooldown |
| Bola | Range 3, 1x Resolve power; four Hobble layers, each lasting four target activations and checking resistance. | Main; cooldown 5 |
| Hook and Drag | Range 3, 0.75x Resolve power; pull two cells, stopping adjacent; no HP/collision damage. | Quick against already Hobbled target, otherwise main; cooldown 4 |
| Abduct | Adjacent Hobbled target; choose destination, paired legal route with separate maximum-movement allowance; target deliberately targets Captor for one activation. | Main; cooldown 4 |
| Restraining Hold | Consume an isolated adjacent target's Hobble layers for that many Hold ticks; no special duration cap. | Main to begin; cooldown 3 after ending |
| Blitz | +3 movement and +25 evasion through the next activation. | Quick; cooldown 2 after expiry |
| Restraint | Adjacent Disarm and Hobble for two activations; successful Hobble limits movement to one cell. | Main; cooldown 3 |
| Clean Capture | Multiply capture chance by 1 + current HP fraction. | Slotted passive |

Isolation uses cardinal adjacency across unblocked edges: Captor must be adjacent, and no third active unit may be cardinal adjacent to the target. Preview explicitly reports isolation. Diagonal units do not interfere.

Hold can begin **before** Capture Ready. Initiation secures it; each subsequent completed Captor activation deals **0.75x Resolve damage, never HP damage**, then makes one capture check if Resolve is zero. Target cannot act and Captor is committed. Guard/end activation maintains it; Release Hold is free. Another unit entering adjacency, displacement, incapacitation or disabling control breaks it. Consuming Hobble prevents immediately reusing the same accumulated layers for another long Hold. Tick identity prevents duplicate processing.

Abduct uses a paired path search rather than refilling ordinary movement. Target follows the Captor's previous tile. Walls, occupants, terrain costs, pits and real hazard entries apply; Blitz increases the allowance. Target and destination selection can be cancelled before E confirmation. Carrying a payload prevents Abduct.

Disarm blocks basic attacks and physical weapon techniques, while spells/healing/utility remain possible. Existing hard-control and displacement resistance remain in force. Multiple Quick Actions may precede the activation-ending main action.

## UI, persistence and migration

Enemy Resolve appears when relevant to capture. Forecasts distinguish contact, Resolve loss, remaining Resolve, capture odds and isolation. Generated rope/bola/hook effects and four foley cues use the combat playback timeline; displayed Resolve updates at its event rather than revealing the server's final value early. Attack/Subdue remain separate controls; the desktop seven-command layout uses four columns to preserve map height.

Character migration version 1 maps legacy Captor IDs to the new pool, preserves ordered equipped slots and learns current starters. Existing battle snapshots gain Resolve and a lethal unarmed attack profile. Hold ownership, consumed duration, tick identity, cooldown and Blitz expiry are JSON-persisted. Standard five equipped slots and progression rules are unchanged.

## AI and limits

A bounded Captor heuristic can maintain Hold, attempt capture at zero Resolve and use straightforward control/Resolve attacks. Advanced isolation planning, coordinated Abduct routes, player capture intent and hidden-personality decisions are deferred. Generic auto behavior still favors capture when carrying capture equipment; manual Attack remains available.

Balance concerns: repeated 1% checks can be tedious; uncapped earned Hold duration can remove a target for a long time; third-party interruption offers counterplay. Resolve equal to HP still makes high-HP targets require more setup even though defense uses INT/AGI. These are explicit playtest targets rather than claimed final balance.

Validation: Captor behavior tests cover separate HP/Resolve, unique isolation bonuses, retries, unconscious recovery, Hold before readiness, interruption, paired routes, Quick/main sequencing, persistence, free release, Disarm and Rat capture. Browser fixtures exercise commands, Abduct confirmation, Resolve display, Hold replacement and effect cleanup. Frontend build passes. See ../art/CAPTOR_V1.md for asset provenance.

Latest validation: 151 focused backend tests passed, followed by all 19 Captor tests after adding the pass-through interference regression; all 379 frontend tests passed. The isolated Captor browser scenario and frontend production build passed. The build retains its existing large-chunk advisory.

## October 7 usability correction

Resolve HUD no longer matches the generic portrait span selector, so it cannot cover the portrait. Existing lower-right HP badges remain; a full HP/Resolve redesign is deferred. Attack button, A hotkey, help and cursor now retain lethal Attack rather than being remapped to Subdue; N independently selects Subdue. Abduct reuses the styled Summoner placement panel, E/C buttons and shared saved draggable positioning. Browser regression now checks actual sent Attack/Subdue commands, hotkey switching, portrait/HUD geometry and styled clickable Abduct controls.
