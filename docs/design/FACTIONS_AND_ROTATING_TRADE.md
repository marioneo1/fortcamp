# Factions, rotating trade and personal consequences

Implemented in dev, October 2, 2026. Runtime sources: `backend/economy.py`, `backend/faction_contracts.py`, `backend/mission_branches.py` and the mission services. No production deployment in this pass.

## Trade

Base → Supplies → Trade with contacts opens one saved camp trade screen. Exactly one of the three current faction traders is present for a 48-hour window: Hedgerow Watch, Meridian Artificers or Lantern Caravan. Player/server identity determines a stable rotation offset. Reopening does not reroll stock; the active faction and purchases are saved. A returning visit restocks its goods. An expired offer cannot be purchased through an old screen. Contacts remain available while their trader is away.

Each current trader has four goods, one copy of each per visit. Relationship gates are 0/15/35/65; base prices are 12/30/65/120 gold. Relationship 20 gives 5% off and 45 gives 10% off, rounded to whole gold. Saved purchase history is pruned after old rotation windows. Adding factions and their stock later is supported by the faction catalogue; this pass does not invent additional factions.

Independent traveling merchants retain their separate, player-specific daily arrival check (45%), saved offers, possible rare stock and a 24-hour visit from first encounter. Basic food (2 gold), medicine resource (6), Field Dressing (8), Restorative Tonic (18) and Cleansing Salts (14) remain available between visits. Treatments are actual inventory copies, not refillable battle charges.

## Private agreements

Each faction offers one E, C and B agreement at relationship 6, 20 and 45 respectively. Guild rank visibility still applies. E agreements use dialogue checks and can revise an initial failed proposal. C/B agreements have quiet/direct approaches, tactical encounters and an evidence handover after victory. Requests immediately open the normal party planner. One active copy per player; fulfilled agreements cannot be repeatedly farmed. Failed or expired attempts may be retried. No shared-board claim points are spent on these invitations.

| Contact | E | C | B |
| --- | --- | --- | --- |
| Hedgerow Watch | A Signal Both Sides Trust | The Patrol That Did Not Return | Three Horns, One Road |
| Meridian Artificers | A Measure Worth Sharing | The Missing Governor | The Custodian Who Would Not Stop |
| Lantern Caravan | Every Sack Accounted For | The Wagon on the Wrong Road | Who Collects the Second Toll? |

Success gives the normal rank-scaled guild fee and relationship gain (+3 success, +5 critical). An optional record check unlocks a separate keepsake drop: 12% E or 18% C/B, plus seven percentage points on a critical mission result. Neither the check nor critical success guarantees an item. Fourteen mission-exclusive keepsakes give defensive/support techniques or carrying/resistance rules; they never enter general caches or faction shops. Their initial art deliberately reuses existing icons pending a dedicated art pass.

## Personal story consequences

The aftermath calls saved world flags **Story milestones**. They are personal, not changes to the entire server. Five existing finales now make an additional private agreement visible at its faction contact:

| Completed milestone | Contact | New agreement |
| --- | --- | --- |
| Laid the Empty Hearse to Rest | Lantern | The Names Left on the Road |
| Broke the Black Banner Court | Hedgerow | The Last Collection Order |
| Mastered the Meridian Engine | Meridian | Where the Spare Current Goes |
| Restored the Titan Roads | Hedgerow | A Road Wide Enough for Everyone |
| Sealed the Starless Treaty | Meridian | A Light on This Side |

These require the personal milestone and the matching C/B Guild Hall access. They do not silently change regional event rolls or other players' outcomes. The contact invitation remains available until fulfilled; each requested contract has the normal 24-hour private deadline.

## Ordinary mission branches

Caravan Account, Wards at the Waystation, Watch Negotiation and Meridian Calibration now offer a routine roll route and an optional deeper investigation. Investigation failure can start a fight; critical failure can introduce a stronger commander. A victorious fight returns to an authored evidence choice. Beginner timber, shed and herb combat branches likewise return to a handover choice. Safe beginner routes remain roll-based.

Delivery keeps the earned result. Optional examination can unlock a separate item roll; failing that check does not replace a battle victory with a failed mission. Final payment, recruits, career records and completion notices wait until the handover. The scene revision prevents replaying a choice; rewards are issued once. A lost fight resolves its failure directly, without a victorious handover paragraph.

## Next work

More factions, richer stock per visit, additional authored mission branches, longer faction arcs and live multiplayer pacing review remain future work. Existing side routes, unique low-rank drops and finale-only relic rates remain intact. This is a focused expansion, not a rewrite of every quest.

## Validation

Backend behavior checks cover stable rotation, expired offers, permanent provisions, relationship/rank/milestone gates, private ownership/deduplication, exclusive loot, supply ownership and delayed one-time handover rewards. Browser checks exercise the actual trade and battle screens, responsive widths, immediate planner opening and supply commands. See the current pass entry in FEATURE_BACKLOG.md for final suite totals.
