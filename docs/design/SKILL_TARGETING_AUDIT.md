# Skill targeting audit - October 8, 2026

Scope: click routing for all 12 base Jobs (97 catalogue entries, 77 active techniques). This is a controls audit, not a new balance pass.

## Findings and implemented changes

### Provenance and why the first correction missed it

Git history traces the approach-menu guard to `a2b3558`, October 1, 2026,
"Remember inventory visibility and add previewed movement attacks", in
`frontend/src/main.js` / `renderBattle`. That change deliberately routed targets
requiring movement into a second confirmation menu. It predates the mobile pass;
there is no evidence that mobile changes introduced this guard.

The October 8 first correction exempted basic Attack but retained the guard for
skills/Subdue. Its browser test explicitly expected a menu for a distant target,
preserving the old interaction assumption instead of checking the desired
selected-action contract. Backend range/approach tests could pass while this UI
detour remained. The subsequent fix and tests exercise the actual click bindings,
selected skill IDs, adjacent/approached targets, occupied floor clicks and invalid
target fallback. No evidence establishes when this old guard became more
noticeable in the user's live encounter.

- The shared unit-click handler opened the generic action menu whenever a skill/Subdue preview contained `move_to`. Basic Attack alone had been exempted in the previous fix. This is independent of mobile gestures.
- Selected unit-targeted skills and Subdue now execute their own validated approach and action on one click. Skill ID and target ID remain explicit; previews do not alter range or movement budgets.
- Invalid explicit targets no longer fall through to a generic menu offering a different skill or basic Attack. Clicking the floor under a target likewise filters contextual choices to the selected action. Move mode retains its contextual menu.
- Tarin Fen and Rovan Rook are generated names, not special targeting rules. A target requiring an approach used the faulty branch; pulling that target into reach bypassed it. This explains the report, although the exact live encounter was not inspected.

## Routing reviewed

| Targeting family | Handler and retained interaction |
|---|---|
| Enemy/ally unit, including melee, shots, control, healing | Shared unit click: direct selected action, optional validated approach |
| Self-target buffs, songs and forms | `bindSpellTargets` self capture; click the acting unit |
| Ground AoE, leap, dash and placed magic zones | `bindSpellTargets` ground capture; cast at valid cell or occupied cell |
| Bard Cue the Strike | Choose allied attacker, then enemy; no generic approach menu |
| Mage Enchant Weapon | Ally selection followed by element choice |
| Rogue Shadowstep, Backflip, Caltrops, Throwing Knife; Druid Bramble Wall | Dedicated Rogue placement capture; retain destination/orientation/attack choice and confirmation |
| Captor Abduct | Dedicated target + drag destination + confirmation |
| Summoner summons, orders, swaps and management | Dedicated Summoner capture; retain relevant placement/target choices |
| Engineer construction | Dedicated construction placement and confirmation |
| Engineer other techniques | Existing ground/self/machine target handlers |
| Passive skills | No cast or approach menu |

## Catalogue inventory

The inventory below covers the registered base-Job catalogue reviewed against the handler families above. It is not a claim that every possible combat state was exercised in a browser.

| Job | Active skills | Passives |
|---|---|---|
| Fighter | Driving Strike; Chain Snare; Earthbreaker; Hold Together; Brace; Second Wind; Victory Strike | Intercept; Riposte |
| Barbarian | Reckless Blow; Skullbreaker; Groundbreaker | Bloodfury; Bloodied Strength; Too Angry to Fall; Bloodthirst; Unstoppable |
| Rogue | Cheap Shot; Crippling Cut; Exploit Weakness; Shadowstep; Caltrops; Backflip; Throwing Knife Technique | Trap Expert |
| Ranger | Mark Quarry; Longshot; Poison Attack; Multi-Shot; Rapid Fire; Pestilence Shot; Rupturing Blow | Sharpshooter |
| Mage | Chain Lightning; Fireball; Typhoon; Flash Freeze; Enchant Weapon; Singularity; Meteor | Debuffer |
| Cleric | Mend; Rest; Holy Light; Heal; Sanctuary; Smite | Exorcist; Battle Priest |
| Monk | Rapid Palm; Iron Reversal; Heaven-Piercing Strike; Crushing Fist; Sweeping Dash; Breaking Combination | Perfect Rhythm; Flowing Footwork |
| Bard | Jeering Verse; Cue the Strike; Accelerando; Quickening Chorus; War Anthem; Song of Peace | Battle Musician; Maestro |
| Druid | Prowler Form; Rejuvenation; Bramble Wall; Bulwark Form; Living Armor; Rat Form | Nature's Persistence; Wild Instinct |
| Engineer | Sentry Turret; Dynamite; Rapid Assembly; Man the Guns; Heavy Emplacement; Proximity Charge; Overclock; Scuttle Protocol |  |
| Summoner | Bound Companion; Transposition; Life Pact; Wisp Swarm; Spirit Projection; Sacrifice; Overload | Rapid Conjuration |
| Captor | Subduing Blow; Bola; Hook and Drag; Abduct; Restraining Hold; Blitz; Restraint | Clean Capture |

## Verification

Final results: 404 frontend tests, 401 base-Job/backend tests, isolated Chrome
interaction checks and frontend build passed.

- Actual shared click bindings exercised for Driving Strike, ranged attacks, Monk follow-ups, Captor techniques, ally healing/protection, Subdue, invalid selection and clicks on occupied floor cells. Tests cover direct and approached commands and preserve the selected skill ID.
- Isolated Chrome: actual hotbar selection and near/far Driving Strike clicks; basic Attack, cursor inheritance and doorway checks.
- Existing base-Job backend suites exercised. An obsolete Fighter test expected capture equipment to disable Earthbreaker/Chain Snare, conflicting with current availability and capture-gear behavior; updated the assertion and replaced its boolean capture-weapon placeholder with the proper profile shape. No availability rule was changed.
- Existing dedicated placement, ground-target, self-target and gesture tests retained. Exact live Tarin/Fen encounter and physical iPhone Safari testing remain manual.
