# Prison recruitment: first playable pass

## October 2 prison workspace

Prisoners use a selectable list beside one detail panel, with capacity, secure-cell and stockade counts. Name/race search and custody filters remain available; selection survives polling. Conversation and terms open on selection, while holding and sale actions have a separate collapsible area. The panel identifies the assigned available warden and shows negotiation readiness from the existing cooldown; negotiations are disabled when unavailable. Securing a prisoner with full cells requires explicitly choosing someone to swap out. Stockade warnings and remaining time remain per prisoner; UI changes do not reset timers or change agreement costs, recruitment rules or sale values. Narrow screens stack list and details.

Implemented October 1, 2026 in alpha/dev. This supersedes the first-batch proposals in PRISON_RECRUITMENT_PROPOSAL.md; broader faction/security ideas remain proposals.

## Player flow

Open Base → Prisoners → Recruitment (or use the Prisoners shortcut in Roster). Talk reveals persistent personal terms. Either fulfill a requested payment/item, add an allegiance quest to Private Contracts, or use Warden negotiation where the ordinary recruitment route is available. Fulfilled terms unlock Offer recruitment; conversion is explicit rather than silently adding someone after a quest.

Each captive receives a fixed route and prospective recruit profile at capture. Existing records receive a stable authored profile when normalized because old saves contain no underlying NPC attributes. These profiles do not infer attributes from encounter HP or damage. Identity, portrait and terms remain stable; an existing authored recruitable snapshot can supply real attributes/perks. Generic conversion refuses unique Champions/Celestials, whose acquisition needs dedicated ownership enforcement. Creature taming remains separate and unimplemented.

## Eight initial concerns

| Route | Terms and reason |
|---|---|
| Debt | Gold clears a family debt to a road broker |
| Refuge | Wood rebuilds burned roofs and a defensive fence |
| Wounded | Medicine supports sick survivors; undead captives ask for their living keepers |
| Field tool | Ordinary captives request an unequipped Field Pack; officers ask for an Ironcap Buckler or Breaching Charge for a specific road/gate problem |
| Rival | Break the rival warband controlling their route |
| Former command | Defeat the warband that sent them to die |
| Strength | Defeat the fighters occupying their ground |
| Rescue | Recover a camp member alive from a prisoner wagon |

Conversation explains the request. Four tactical routes have E–S templates, restricted to owner-only Private Contracts. Enemy race follows the captive for warband routes; rescue uses the existing wagon extraction scenario. E-rank warband encounters use two opponents, and E/D rescue defenses are reduced for solo accessibility. Higher-rank rescue opponents gain rank-scaled HP and attack; the wagon map/objective is reused. Deeper encounter variations remain a later pass. No temporary faction reputation simulation is claimed.

## Resistance and warden work

Ordinary resistance starts at 18; bosses at 36. An assigned idle warden lowers resistance by `min(12, 4 + floor(effective INT / 2))` per negotiation. The player chooses which prisoner receives that session. One session per warden every 30 minutes is shared across prisoners and cells, persisted by warden identity. A typical 4–5 INT warden needs three sessions over about an hour for an ordinary captive. Talking is unlimited but does not lower resistance or reroll terms. No offline starvation, escape or free automatic negotiation.

Wardens cover secure prisoners in capture order against prison buildings ordered by stable building ID, four slots per building. Swapping prisoners can change who covers them; progress and warden cooldown do not reset. Security/Combat-based warden effects are deferred.

Ordinary captives may join at zero resistance or bypass it by fulfilling their agreement. Bosses require their agreement regardless of resistance. B/A/S bosses with resource or item demands also require a proof-of-strength contract after payment; the payment cannot be charged twice. Starting loyalty is 70 through ordinary negotiation or 80 through an agreement. No permanent loyalty ceiling: existing meals, conversations and successful expeditions retain their established behavior. Captive allegiance history is stored on the recruited character for future personal loyalty quests.

## Initial resource sinks

For rank tier E=0 through S=5: gold asks for `180 + 120 × tier`, plus 300 for a boss; wood asks for `30 + 15 × tier`, plus 30 for a boss; medicine asks for `8 + 4 × tier`, plus 8 for a boss. Requested gear consumes one unequipped copy. These are initial tuning values, not multiplayer pacing guarantees; review against actual guild income and acquisition times. Ordinary negotiation provides an alternative to a costly request.

## Persistence and retries

One active quest per prisoner; two prisoners can hold separate instances of the same template. Unstarted quests use the existing 24-hour private expiry. Failed/expired attempts can be recreated without changing terms, paid resources or resistance. Success/critical success fulfills only the linked captive's agreement once; failure grants no agreement progress. A missing/sold/unsecured captive cannot start the contract. An already running mission can finish after the captive is sold, but no recruitment credit is awarded. Payments, conversion and quest creation share the existing per-player mutation lock; duplicate requests cannot duplicate rewards or recruits. Stockade timing remains the existing cumulative one-hour rule.

## Next content passes

Author deeper multi-step negotiations, lore-specific opponents and named temporary factions with meaningful obligations. Add individual loyalty follow-ups after recruitment, with one-time milestone rewards rather than unlimited repeatable loyalty farming. Broaden demand items by rank, author race/personality-specific concerns, and add security incidents as player decisions rather than random offline losses. Do not expose secret mission requirements in public help.

## Validation

Backend tests cover stable migration/swaps, shared warden cooldown, resistance versus boss terms, payment consumption, equipped-item protection, unique-character protection, per-captive private quest identity/retries and actual claim→battle-result agreement credit. Isolated browser checks exercise prisoner conversation, payment, button availability and recruitment removal using mocked API responses generated by the backend. Live multiplayer recruitment and long-term economy pacing require playtesting.

## Prisoner UI refinement (October 1, 2026)

Prisoner cards separate Conversation & terms from Recruit profile and remember the selected tab and expansion across refreshes. Warden negotiation has a resistance meter and explains its shared cooldown; custody/sale actions sit below recruitment. Agreement fulfillment, prisoner sales and contract abandonment use the shared in-game confirmation dialog instead of browser confirmation prompts. Payment confirmations show the exact resource/item and whether a further personal task is required. Cancel, Escape and backdrop dismissal do not submit an action. Duplicate prisoner requests are blocked while an action is pending.

Verified with production build, frontend tests and the actual frontend browser fixture: conversation, payment cancellation, profile preservation, sale cancellation by Escape, payment and recruitment. Browser fixture uses simulated API responses; no live prisoner data changed.

## Dedicated prisoner workspace

Prisoners now live in Base / Prisoners, with a direct Roster shortcut, capacity summary, holding filter and name/race search. They are no longer below the character detail screen. Manage prison facilities opens the Prison Cell inspector for warden assignment. See CAMP_INTERFACE.md for the complete base/roster navigation.
