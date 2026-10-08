# Burn, Poison and Bleed - implemented in dev, October 6, 2026

This is the current canonical rule, superseding attack-scaled independent DoT durations and exertion-only Bleed in earlier Job documents.

| Status | Base damage | Normal trigger | Decay |
| --- | --- | --- | --- |
| Burn | 2% of target maximum HP, minimum 1 per stack before modifiers | Target turn end | Remove one stack after damage |
| Poison | 10% of target maximum HP total, regardless of stack count | Target turn end | Remove one duration stack after damage |
| Bleed | 5% of target maximum HP | Target turn end | Remove one stack after damage |

Burn and Bleed stacks contribute to one damage event. Poison stacks are duration only: five stacks cause five 10%-max-HP base ticks, not a 50% tick. Additional Poison extends duration. Five Burn stacks on a 50-HP target deal 5 base damage, then four stacks deal 4 on the next turn end. No tick at activation start, during polling, discarded movement previews or each Quick Action. Guarding and skipped activations still end a turn and resolve DoTs. Owned temporary units resolve their own end once during their owner's entity phase.

## Application, resistance and damage

Burn resistance cannot block application. Base percentage damage is calculated first; existing outgoing/incoming modifiers apply, then Burn damage resistance reduces the result. At 100% Burn resistance, stacks still apply but deal zero damage. Armor does not reduce these DoTs; Barrier still absorbs damage. Existing integer damage rounding applies, so fractional results are rounded for actual HP loss. Minimum Burn damage is a base minimum, not a guarantee of one damage after resistance.

Poison and Bleed retain selective application resistance and authored immunity. No species is inferred from color. Cleansing removes the matching pool. Multi-hit Fire enchantments still add stacks per landed eligible hit; Debuffer doubles Burn applications without doubling hard-control duration. These percentage values are deliberately strong against high-HP enemies; encounter and resistance balance still need live testing.

## Ground entry

Each actually entered Scorched tile adds one Burn stack (two for a Debuffer-authored patch), then immediately deals damage from the target's complete resulting Burn pool. This entry hit does not remove a stack. Leaving and entering again counts again; real push/pull paths also count. Only the final committed route from START is charged. Views and route forecasts do not mutate stacks or HP.

Overlapping Scorched/Ember areas share one fire entry trigger. Scorched areas also render as one union, with one animated patch per cell: no double Scorched effect. Source zones may coexist internally to retain ownership and independent expiry. Scorched affects everyone; legacy Ember retains its hostile-only relation. Merely remaining on a burning tile does not add an activation-start stack.

Caltrops apply Bleed/Hobble on placement occupants and actual entry, without immediate Bleed damage. Bleed resolves only at turn end. Future Poison-entry traps should similarly add Poison without an immediate Poison tick; this pass does not create a new Poison-trap asset or zone type.

## Persistence and Ranger cashout

Pools retain a layer per application for source metadata. Former per-layer expiry and attack-scaled tick damage no longer determine damage; old nonlayered statuses become one stack unless they explicitly stored a stack count. Old `turns` is not a stack count. Reading battle views normalizes copies, not the saved battle.

Rupturing Blow estimates remaining unmodified Poison damage as 10% max HP times remaining duration stacks. Bleed still uses per-stack base times n(n+1)/2 across its shrinking damage pool. It consumes both pools after a landed hit and cashes out half that potential through current damage modifiers once. It does not assume future exertion or predict future defensive changes.

Aggregate tick credit currently uses the oldest remaining layer's source; individual layer source metadata remains available. Splitting statistical credit between several contributors is future work. Existing battle skill snapshots remain intact; start a fresh battle to test the new three-activation Fireball cooldown.

Validation covers percentage/rounding order, resistance, stack decay, Quick Actions, temporary units, legacy JSON, Barrier, trap entry, shared fire overlap, pure movement previews and Ranger cashout. See the latest history entry for test totals.


October 7 correction: Poison is duration stacking, not damage stacking. Its end-turn tick remains 10% maximum HP before the existing incoming modifiers, Barrier and integer rounding. Exactly one duration stack is removed per completed target turn. Application resistance/immunity, ownership, once-per-end resolution and no damage on Poison trap entry remain unchanged. Existing pools retain their counts without save migration. Ranger cashout, previews and descriptions use the corrected linear remaining Poison damage.
