# Mage rework — implemented in dev, October 6, 2026

Current Frozen/Scorched presentation: [Mage surfaces V2](../art/MAGE_SURFACES_V2.md) supersedes the initial cage and ground stamps with two dedicated sheets, face frost/spread/shatter/thaw and a connected terrain stain with sparse top-down flame frames. Gameplay below is unchanged.

Mage creates elemental states and dangerous ground, then exploits them with spells or allies. This extends the existing five-slot loadouts, damage pipeline, resistance, displacement, movement previews, zones and persisted battle JSON. No Mana system, new Champion kits or production rollout.

## Kit and progression

All techniques are main actions. Cooldowns count the caster's own activations. Reach is five cells unless noted. Areas use the existing Manhattan diamond, clipped to the map and line of sight; walls stop blasts and Lightning bounces.

| Skill | Unlock: successful contracts | Cooldown | Implemented rules |
| --- | --- | --- | --- |
| Chain Lightning | Starter | 4 | Enemy target. Primary 150%, bounces 125% attack; Wet targets 250%/175%. Continue to the nearest unhit enemy within two cells of the previous victim, with clear sight. Once per enemy, no fixed victim cap. Wet is retained; each landed Wet hit rolls 25% one-turn Paralysis before resistance. |
| Fireball | Starter | 2 | Ground or enemy centre, radius two. Centre 150%, outer 125%; landed hits apply Burn. Wet is consumed into two-turn Blister. Leaves ally-safe Scorched ground for two caster turns. |
| Typhoon | Starter | 3 | Target yourself; radius three. All OTHER units, including allies, take 25% attack, are pushed two cells on a hit, and receive Wet for two target turns. The caster is excluded. Normal walls, collisions, pits and displacement resistance apply. |
| Flash Freeze | 2 | 4 | Arm radius-two ground. At the END of your NEXT activation, freeze enemies still inside for two target turns. No channel; you can act normally. Resistant targets receive Wet instead. |
| Enchant Weapon | 5 | 5 | Ally target, reach four. Choose Fire/Frost/Lightning in the centred dialog; cancel spends nothing. Lasts two ally turns and replaces the previous enchant. |
| Singularity | 9 | 5 | Ground radius two. Centre 200%, outer 25% attack; landed victims outside the centre are pulled one cell inward. Normal collision/hazard/resistance rules apply. |
| Debuffer | 12 | Passive slot | Halve direct Mage spell damage. Double Burn stack application OR Wet/Blister/enchantment duration. No doubled hard control, ground lifetime or Burn duration. Basic attacks, collisions, ground damage and status ticks are not halved. |
| Meteor | 16 | 6 | Ground radius three. Channel to the START of your next activation; release spends that activation. Inner radius two 400%, outer ring 300%, plus Burn and two caster turns of Scorched ground. |

New Mages learn/equip Chain Lightning, Fireball and Typhoon. Ordinary five-slot rules remain. No extra combat resource or Quick Action was added.

## Elemental rules and costs

- **Wet** is elemental setup, not inferred from race. Lightning retains it; Fireball consumes it. Duration is two target turns, four with Debuffer.
- **Elemental Frozen** prevents acting and movement. Direct HP damage breaks the ice AFTER the full hit; fully absorbed Barrier hits and DoTs do not. Natural expiry, damage or cleansing leaves Wet. Existing boss one-activation control duration, selective Freeze resistance and shared control recovery still apply. A failed Freeze applies Wet immediately, including a recovery-blocked attempt.
- **Legacy equipment Freeze** retains its old movement restriction and direct-damage vulnerability in existing saves. Only newly authored Mage Freeze has `elemental_freeze` metadata and the above ice-breaking rules. This avoids silently rewriting previous gear balance.
- **Burn** uses independent source/duration layers, like Poison. Each Mage stack deals 8% of the caster's effective attack, rounded, minimum one HP, at the next two target starts. New stacks do not refresh older spell/weapon layers. Legacy single Burn converts without losing its original damage. Selective Burn resistance applies.
- **Blister** lowers outgoing damage by 10% and accuracy by 10 percentage points. It affects all outgoing damage, including status damage; explicit guaranteed accuracy remains guaranteed.
- **Scorched ground** uses the existing committed-path resolver: each entered tile deals three damage, including repeated entry and push/pull. Discarded movement previews are free. Entry also refreshes a separate ground Burn layer per caster (two with Debuffer); repeated movement does not multiply ground layers indefinitely. It also triggers at enemy activation start on the ground. Overlapping fire-ground zones do not multiply entry damage. Allies are safe, consistent with existing Ember rules.
- **Meteor** can be interrupted by defeat, hard control/Bind, Mute or actual displacement. Ordinary damage does not interrupt. A visible warning lets enemies leave. Preparing and releasing occupy two activations; the cooldown starts on preparation. The queued cast snapshots its attack/passive bonuses, consumes one-use Rally once, and survives JSON persistence. Freeze zones do not require an uninterrupted caster.

## Enchantments

Fire adds one Burn stack per landed weapon hit (two with Debuffer). Frost rolls 20% Freeze per landed hit before resistance; later hits can break that ice, and recovery prevents instant repeat freezing. Lightning rolls 25% Paralysis against Wet per landed hit until successful, then remembers that victim for the lifetime of this enchant. Other Wet targets can still be paralyzed once each. Wet is retained.

Physical techniques and multi-hit attacks are supported per hit, as are ordinary wand/rod basic attacks. A landed hit fully absorbed by Barrier can still apply the enchant. Mage spells, other magical techniques, damage ticks, reactions, collisions and nonlethal capture delivery do not recursively trigger weapon enchantments. Owner metadata lives on the real enchanted unit, so copied multi-hit damage sources cannot reset the once-per-target list.

Debuffer doubles the enchant's duration and Fire stack applications, not Frost/Lightning proc chances or hard-control duration.

## Example five-slot builds

**Storm controller:** Typhoon / Chain Lightning / Flash Freeze / Singularity / Fireball. Create Wet, group enemies, decide whether to retain Wet for Lightning or trade it for Blister. Costs: friendly displacement, long control cooldowns and poor safety if surrounded. Counters: spread out, use walls, pressure the caster, resist individual controls.

**Siege caster:** Fireball / Singularity / Meteor / Flash Freeze / Chain Lightning. Group or freeze victims before committing Meteor. Powerful areas, but setup costs activations and enemies can escape or interrupt. No one-button mandatory winning rotation.

**Elemental enchanter:** Enchant Weapon / Typhoon / Flash Freeze / Chain Lightning / Debuffer. Trade direct spell damage for longer Wet/enchantments and doubled Burn applications; enable allied multi-hit pressure. Cleansing, selective resistance, separated enemies and forcing the Mage to defend interrupt this plan. It deliberately sacrifices immediate burst.

## UI, AI and compatibility

Eight matching painted icons, eight reusable effect assets and five local sound clips are documented in [Mage art/audio](../art/MAGE_V1.md). Projectiles, contact flashes, typed damage, pushes, collision recovery and next-actor playback use the existing shared impact clock. Ice encloses the portrait; Wet has a cyan rim; channeling has a gravity orbit. Ground warnings distinguish armed Freeze and incoming Meteor from active Scorched terrain. The enchant dialog is centred over the map and preserves combined movement/cast selection.

Forecasts include every affected unit and displacement/collision information. They use current positions; delayed spells cannot promise victims will stay. Request-local terrain, blast and approach caches avoid repeating identical searches, never persist, and rebuild after map changes. On a local 8×8/five-unit Warcamp with four area skills and Enchant, median view generation dropped from 85.4 ms to 23.7 ms; this is a fixture measurement, not a network-latency or large-map guarantee.

AI uses legal current-position attacks, Wet/chain and area scoring, ally enchantment and avoids Typhoon when it would hit allies. Existing fallback movement/basic attacks remain. It does not yet predict delayed-zone exits, coordinate elemental combinations across multiple turns or deliberately protect a channeling ally. Further AI strategy is deferred rather than claimed.

Old Mage choices map to the new kit: Embers → Fireball; Ward → Enchant Weapon; Footwork/Armored → Debuffer; Binding/Bind → Flash Freeze; Scorch → Chain Lightning. Learned IDs, equipped IDs and saved order are deduplicated; practice and identity remain. New starters are learned without forcing extra slots into a full loadout. Existing in-progress battle definitions stay snapshotted. Both normal and Battle Lab command schemas preserve the selected `element`; no changes to credentials, saves or environment flags.

## Testing and remaining review

Mage behavior tests cover propagation, Wet retention/conversion, selective boss resistance, ice breaking/expiry/cleansing, shield interaction, delayed timing, channel interruption, persisted Meteor, Rally consumption, spell/ground lifetime, per-hit enchants and copied sources, Burn layers, Debuffer, Blister, friendly Typhoon, committed hazardous paths, previews, AI, loadout migration and Battle Lab schema. Full relevant backend/frontend regression totals are recorded in the history entry.

Real Chrome fixtures check loaded icons, cancel-without-command, selected Frost dispatch, ice/channel overlays, five impact types and effect cleanup. Frontend production build passes with the existing bundle-size warning. Runtime assets are included in Git; generated source atlases remain staging references.

Numeric balance across ranks, human listening/aesthetic review of the synthesized clips, full-channel pacing in live fights and advanced elemental AI remain playtesting work. This pass does not claim all encounters are balanced or all spells have cinematic bespoke animation.
