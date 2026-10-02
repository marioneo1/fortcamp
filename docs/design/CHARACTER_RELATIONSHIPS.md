# Character relationships: foundation and staged design

## October 2 conversation workspace

Conversation now has a portrait/personality sidebar, loyalty meter and independent-action chance, a scrollable dialogue area, and four topic buttons with brief explanations. Keep up to eight exchanges per character for this browser session; this is not persistent chat history or an AI dialogue service. Polling preserves the reading position, last chosen topic and meal drawer. Rapid repeated clicks issue only one pending request. A late reply cannot switch the screen back to a previously selected companion. The meal drawer shows prepared quantities, discovered preferences and the next gift time; unavailable meals, cooldowns and away characters disable the relevant actions. Service Record remains in its own tab. Existing authored responses, tastes, loyalty gains and gift rules are unchanged.

## Implemented

Non-player loyalty and personality persist. Missing loyalty defaults to 80; explicit loyalty is preserved and clamped 0..100. The player avatar is always 100 and never disobeys. Generic personalities derive from stable identity, not race or portrait. Champion defaults live in CHAMPION_PERSONALITIES; personality_override supports authored name, description, behavior and dialogue voice independently of the default trope. Race does not prescribe personality.

An independent turn has exactly `100 - loyalty` percent chance. Check once per activation using battle seed, round and turn index. The stamp persists with battle state; preview, mode switches and repeated repositioning cannot reroll. Independence replaces command input for that activation. Existing panic/status and Retreat All rules have priority and are separate from the loyalty check.

Twelve tropes: Berserker, Self-preserver, Timid, Protector, Duty-bound, Proud duelist, Opportunist, Strategist, Daredevil, Merciful, Curious explorer and Steadfast companion. They currently share seven policies: aggressive attack; protected positioning/guard or injured withdrawal; withdrawal; guard near a vulnerable ally; pursue objectives; prioritize strong opponents; and nonlethal takedown/guard. Some tropes share a policy while differing in voice. Do not claim twelve unique AI engines. Cover seeking is positional, without new ally damage redirection. Exits retain next-turn readiness.

Normal success adds one loyalty; critical success adds two. Failure does not reduce loyalty in this pass, avoiding a failure/disobedience spiral. At low loyalty disobedience is intentionally frequent; review player feedback before adding penalties.

## Conversation and tastes

Roster Conversation tab offers Last expedition, Food preferences, Trust and Outlook. Curated replies use only the character's own expedition memories; combat replies can mention actual kills/subdues. This is not an LLM conversation service or a complete Champion voice library. Talking gives no farmable loyalty. Loyalty currently means command reliability; romantic affection is a separate future axis, not a label implied by high loyalty.

Favorite/disliked meals are individual, seeded independently of personality/race. Food conversation reveals the favorite. Future weighted tastes can bias probabilities without replacing individuality. Gifts consume a prepared Kitchen meal: favorite +4 loyalty, neutral +1, disliked +0. One six-hour cooldown per character applies across meal types and survives restarts. Giving a meal reveals that taste. Idle/recovering companions can interact; companions away on assignments cannot. Gear/item gifts are deferred.

## Service record

Missions taken increments on expedition acceptance, not contract reservation. Completion/failure counters update on resolution, including bodyguards. Success rate uses resolved missions; pending missions do not lower it. Legacy/debug resolution without an acceptance flag counts one taken mission on resolution. Historical missions are not backfilled.

Combat credits actual HP removed, excluding overkill. Track kills, subdues, defeats, total damage, started own combat activations and best turn damage. Damage over time credits its recorded source. Counters persist to characters when battle resolves; closing the browser does not reset battle counters. Noncombat critical-failure incapacitation counts as a defeat. Retain eight expedition memories, with actual combat facts for the latest result. Records start with this update.

Damage per turn is total damage divided by started activations, not real-time DPS. Show this definition in the UI rather than inventing a per-second measure for a turn-based game.

## Next stages: not implemented

1. More authored debriefs, named battle beats, dialogue choices and Champion voice/profile data. Replies must use witnessed facts.
2. Item/gear/trinket gifts and craftsperson recipes. Do not add an idle workshop before recipes have a purpose. Preserve valuable items and limit gift farming.
3. Relationship events and rivalries using recent performance, including healers, rescuers and defenders rather than rewarding only damage dealers.
4. Separate opt-in adult romance/marriage and consenting polyamorous arrangements, with SFW dialogue and character-specific availability. Family/children lifecycle needs its own roster and progression design. Do not assume all characters qualify for romance.
5. Award ceremonies should favor titles, cosmetics and utility. If permanent attributes are introduced, begin with +1 to one attribute and explicit lifetime/season caps. No uncapped recurring stat inflation. Establish cadence and eligibility first.
6. In-game handbook, contextual rule explanations and discovery pages; keep secret requirements out of public help.

AGENTS.md requires documentation/backlog updates in the same feature pass. docs/INDEX.md is the document map and glossary. Repository instructions handle this more reliably than a separate skill that may not be invoked.

## Roster presentation (2026-10-01)

Career statistics now live in a separate Service Record tab. Conversation contains personality, loyalty, topics and meal gifts. Statistics and conversation behavior are unchanged.

## Captive recruitment

Prisoner conversation and agreements now precede roster membership; see PRISON_RECRUITMENT.md. Recruits keep stable identity/tastes and join with 70 loyalty through ordinary negotiation or 80 through a fulfilled agreement. Allegiance provenance is retained for later loyalty contracts; those follow-ups are not implemented yet.
