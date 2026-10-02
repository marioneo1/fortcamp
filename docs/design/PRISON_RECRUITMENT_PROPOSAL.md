# Prison recruitment proposal

Status: original design proposal, October 1, 2026. The first playable recruitment pass is now documented in PRISON_RECRUITMENT.md. Unimplemented ideas below remain proposals. Mousewheel camera controls are implemented separately.

## Existing foundation

Prison Cell provides four secure slots and one worker assignment. Captured unconscious enemy people can be retained; creatures are excluded. Sales, securing/swapping prisoners and one hour of cumulative stockade time work. Warden assignment currently has no recruitment effect. Capture records preserve identity, portrait and encounter provenance but not a complete recruitable character profile.

## Recommended loop

Capture → choose sell, retain or later release → assign a warden → discover a concern through conversation → reduce resistance → meet an allegiance condition where appropriate → recruit → earn loyalty through shared activity.

Use two separate values: **Resistance** measures unwillingness to join and ends when recruitment succeeds; **Loyalty** measures command reliability afterward, using the existing 100 minus loyalty chance. Lowering resistance must not grant perfect loyalty. Personality affects how the captive responds, while individual concerns and tastes persist independently.

Wardens spend a shared work budget on prioritized prisoners, rather than granting every prisoner unlimited simultaneous progress. Intelligence supports understanding and negotiation; Combat capability supports security. Existing proficiency/gear effects should explicitly disclose any relevant benefit. Warden assignment trades against using that character in expeditions/production. Changing wardens or moving cells must not reset progress, rewards, timers or rolls. Ordinary prisoners should require only a few meaningful interactions; reserve longer authored allegiance quests for exceptional recruits.

Player talks discover actionable concerns: a missing companion, debt, allegiance to a former leader, fear of reprisals, respect for strength, or an offer of protection. Present understandable choices and their intent, not an invisible right-answer quiz. Resistance setbacks should be limited; no forced total resets or permanent recruit destruction from one bad conversation. Random rolls may change progress or bonuses, but cannot trap an ordinary captive behind endless recruitment failure rolls after all conditions are met. Avoid torture/minigame escalation; pressure can produce early cooperation at lower starting loyalty rather than mechanically superior unconditional recruitment.

Connect Kitchen meals, Medical Ward treatment, Private Contracts, faction standing and existing loyalty. Favorite food is individual and discovered, not guaranteed by race/personality. No unattended starvation simulation. Intel can unlock a bounded personal lead before recruitment, giving a reason to retain a captive other than roster power. Each meaningful lead/reward is claimable once.

## Boss balance

Capturing a boss remains a valuable achievement. Recruiting exceptional enemies additionally requires an authored allegiance contract or resolve condition proportionate to their actual recruitable strength, not merely a decorative boss flag. Regular named officers can use simpler recruitment. No blanket ban on recruiting bosses or permanent loyalty ceiling simply because they were prisoners.

Preserve the actual person's race, identity, portrait, underlying attributes and legitimate skills. Do not convert encounter HP/attack directly into roster attributes or randomly replace them with a weaker unrelated character. Encounter-only phases, boss HP multipliers, arena powers, reinforcement summons and damage scaling are explicitly separate from recruitable abilities. Real powerful traits stay, using shared equipment/action costs and normal counters. Show the prospective roster profile before players invest in recruitment. Some boss abilities can become authored equipment/skills or personal progression where their mechanics support fair party play.

Converted captives begin with less loyalty than voluntary recruits, according to treatment and allegiance resolution. Show command reliability before deployment; avoid punitive starting values without ways to earn early trust. A powerful recruit with unreliable commands is a meaningful choice, but low loyalty alone does not balance an overpowered independent attacker. Appropriate underlying stats, ability costs/counters and recruitment effort must do that work too.

Security can give Watchpost/warden Combat an actual role later. Do not add random offline losses to the first pass: security incidents should become visible decisions or encounters players can respond to. Storage and active warden attention provide initial constraints without maintenance spam.

## First implementation batch

1. Persist recruitable snapshots for newly captured characters; explicitly migrate older incomplete records without inventing encounter-derived stats.
2. Prison UI with candidate preview, resistance, warden priority and understandable recruitment conditions.
3. Warden work and a small reusable conversation library; cooldowns shared by prisoner identity and bounded offline progress, never refreshed by clicking/swapping.
4. Ordinary recruit conversion with stable personality/tastes, starting loyalty and one-time transactional removal from prison. Existing unique-character ownership rules must hold.
5. Goblin chieftain allegiance Private Contract as the first boss example; branch into a goblin alliance or other authored resolution, not repeatable capture-to-roster shortcuts.

Defer security incidents, extensive faction ransom markets and species-specific creature taming until this loop is enjoyable. Prices, work cadence and loyalty gains require simulation against solo/newbie and developed guild progression before becoming live rules.

## Inspirations

RimWorld's resistance/warden interactions and Bannerlord's conformity-based recruitment are references, not designs to copy wholesale. Fortcamp should add personal conditions and short authored contracts rather than rely entirely on waiting or repeated percentage checks.
