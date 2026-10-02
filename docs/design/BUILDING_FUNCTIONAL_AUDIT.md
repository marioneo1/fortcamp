# Building functionality audit — October 1, 2026

This records current behavior rather than planned features in BUILDINGS_DESIGN_WIP.md. Existing buildings and recruited characters are preserved.

| Building | Working purpose | Gaps and recommendation |
|---|---|---|
| Tent | Two-hour incapacitation recovery instead of four-hour field rest | Listed beds do not enforce roster capacity; keep the recovery role |
| Campfire | Starting camp landmark | No cooking recipes or benefit from assigning a worker yet; make it an unstaffed landmark until campfire recipes are designed |
| Storage Shed | Extends the production catch-up cap from 12 to 18 hours per shed; required by some missions | No general inventory limit; no benefit from staff. Describe the catch-up bonus honestly |
| Workshop | Constructor training with a qualified teacher | Equipment repair is not implemented; correct the description rather than promise repairs |
| Infirmary | Thirty-minute injury recovery; Medic training | Future staffing bonuses are not implemented |
| Barracks | Listed six beds; available via blueprint research | Housing capacity has no gameplay enforcement yet. Defer marketing it as a progression upgrade until accommodation has a useful, forgiving mechanic |
| Watchpost | Can accept guard assignments | No watch/raid/base-defense benefit. Candidate for retiring from future construction/rewards until base defense is implemented |
| Guild Hall | Mission-rank unlocks and free-for-all claim-allowance upgrades | Staff currently adds no board bonus |
| Training Ground | Combatant, Scavenger and Survivalist training | Teacher-based rules replace the old implication that training is automatic |
| Prison Cell | Four secure prisoner slots; temporary-stockade swaps; reserves a Warden slot | INT-based shared warden negotiation and personal recruitment terms implemented; security/trader acquisition remains pending |
| Arcane Sanctum | Arcanist training | Keep |
| Alchemy Lab | Alchemist training | Keep |
| Lumbermill / Quarry / Salvage Yard / Farm / Herb Garden | Production yield upgrades, assignable work and work proficiency practice | Keep |
| Kitchen | Prepare and consume meals with field/recovery/study effects | Keep; no starvation/offline food upkeep |

Camp hiring has been removed from both UI and server action. Workers must be encountered through missions. Later prisoner recruitment and a trader who offers captives require authored acquisition, pricing and loyalty rules; these are not implemented by this pass.

Loyalty now checks command reliability once per combat activation: independent-action chance equals 100 minus loyalty. Missing NPC loyalty defaults to 80; the player is immune. Conversations, meal gifts and service records are implemented; prisoner recruitment and INT-based warden negotiation are implemented. See CHARACTER_RELATIONSHIPS.md and PRISON_RECRUITMENT_PROPOSAL.md.
