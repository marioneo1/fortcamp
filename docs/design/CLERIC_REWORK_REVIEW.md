# Cleric rework — implemented in dev, October 7, 2026

Cleric is a finite-restoration healer or a self-sustaining Battle Priest. It uses
the existing five equipped Job slots, per-unit activation clocks, charge usage,
statuses, placed zones, movement commitment and damage pipeline. No Mana system
or second character progression system was added.

## Skill pool

| Skill | Behavior | Cost |
| --- | --- | --- |
| Mend | Yourself or an adjacent conscious ally; INT healing, capped at 15% of recipient maximum HP, minimum 1 | 5 charges |
| Heal | Yourself or a conscious ally within 3 cells and clear sight; 40% of recipient maximum HP | 2 charges |
| Sanctuary | Place a fixed 3×3 zone within 3 cells; allies heal at their turn start for max(5, floor(INT/2)); expires after 3 caster turns; walls clip the area; Burn blocks healing | 1 charge |
| Rest | Begin continuous recovery; +75% damage received from all sources | Main action; no cooldown |
| Smite | Quick Action; weapon hits add an INT-based holy magical damage component for the casting turn and the next two own turns; commit current position and allow at most one tile of further normal walking this activation | Cooldown 5 |
| Exorcist | Successful direct attacks against Undead, Revenants, Banshees and Vampires roll 25% Stun for one target turn, before resistance/recovery | Slotted passive |
| Holy Light | Ground or unit-centered cross extending 1 cell cardinally, 5 cells before clipping; 150% INT magical power; landed hits apply one-turn Blind before resistance; allies safe | Cooldown 4, cast range 4 |
| Battle Priest | Transform healing into self-only cooldown skills; improve Smite and Exorcist | Slotted passive |

Traditional healing has no cooldown. All healing clamps to missing HP, cannot
revive, and uses normal rounding. Mend's small cap preserves the difference from
Heal at high INT. Percentage Heal has no added cap: current stat ranges do not
justify one yet. Sanctuary overlaps heal only once per zone type per activation.

Mend, Rest and Holy Light start learned. Heal, Sanctuary, Smite, Exorcist and
Battle Priest unlock at 2, 5, 9, 12 and 16 successful contracts respectively.
Battle Lab uses this same pool and progression; choose the 16-success tier to
test every option, retaining five equipped slots.

## Continuous Rest

The activation spent starting Rest counts as its first completed Rest turn.
End Turn/Guard while remaining stationary can continue it; it need not be cast
again. Each completed resting activation restores 10% own maximum HP and one
Mend charge. Every second restores one Heal charge; every third restores one
Sanctuary charge. No charge can exceed its starting maximum. Only equipped
healing skills recover. Repeated processing of one activation does not duplicate
recovery.

Movement, actual forced displacement, attacking, another ability, direct HP
damage, hard control or Mute ends Rest. Absorbed hits and DoT do not interrupt it;
DoT still receives the +75% vulnerability. Select **End Rest** to cancel freely.
Session progress resets when Rest ends. The interface shows the current completed
Rest turns. This is intentionally easier to interrupt than an indefinite safe
healing engine.

## Battle Priest

The same equipped healing IDs transform in the battle snapshot:

- Mend: self-only, normal healing formula, cooldown 3.
- Heal: self-only, 40% own maximum HP, cooldown 5.
- Sanctuary: renamed Regeneration, self-only, the Sanctuary healing amount at
  each of the next three own turn starts, cooldown 6.
- Smite: cooldown 4; Exorcist: 50% before resistance.
- Take 15% less damage from all sources, including DoT, through the shared
  incoming-damage pipeline. Normal minimum damage and rounding still apply.

These heals have no charges and cannot target allies. Rest remains available for
its 10% self-healing and vulnerability, with no charge recovery. It is usually a
poor use of a Battle Priest slot, but needs no additional incompatibility rule.

## Damage and presentation

Smite uses the shared damage pipeline for a second holy magical component, not
a doubled physical number. Fortcamp currently shares armor subtraction between
physical and magical damage; magic reduction and racial elemental resistance
then distinguish the component. There is no separate magic-defense stat. Guard
is consumed once, Barrier carries across components, and forecasts use the same
sequence. The bonus component does not retrigger weapon enchantment or Monk
on-hit healing. Exorcist rolls once per landed weapon attack, not once per Smite
component. Holy Light also supports Exorcist.

Eight new cohesive square icons, charge counts, End Rest, self-target indicators,
Regeneration naming, cross/zone previews and impact-linked damage/status feedback
are implemented. Holy Light has a brief golden cross layered with existing
painted force art; healing reuses restoration art. Existing cast/guard audio is
reused; dedicated Cleric audio was not generated. See ../art/CLERIC_V1.md.

## Persistence, AI and limits

Existing per-battle ability usage persists across requests/reloads; schema
adaptation does not refill charges. New battles start full. Older character
loadouts map Cleanse→Heal, Steadfast→Exorcist, Barrier→Smite and Intercept→Holy
Light, preserve practice/order and learn the new starters. Battle Priest is not
automatically equipped by migration. Existing active battles keep their saved
ability snapshots; begin a new Battle Lab fight for the new kit.

Baseline AI heals wounded allies in immediate range, uses Holy Light with legal
targets, activates Smite before an available weapon attack, and rests only when
enemies cannot reach it using estimated movement plus attack range. It honors
Jeering Verse's deliberate attack target and permits healing inside Song of
Peace. This is conservative fallback behavior, not the deferred personality-aware
Job AI pass. It does not yet plan Sanctuary placements or allied protection for
Rest.

Watch total Sanctuary healing on large groups, Rest safety on unpressured maps,
and late-game INT/multi-hit Smite combinations in playtesting. No changes were
made to Fighter, Barbarian or Monk kits.

## Validation

Automated checks cover finite charges, resume, migration, healing formulas,
Rest interruption/recovery/caps, Battle Priest transformations, exact regeneration
ticks, zone timing, Holy Light geometry, Smite component resistance/Barrier/Guard,
linked feedback, Exorcist, AI target restrictions and read-only forecasts.
Isolated browser QA checks icon loading, charge labels, the 9-cell Sanctuary and
5-cell Holy Light previews, End Rest, self-only healing, active zone rendering,
Holy Light impact and cleanup. It uses no live API or player saves.
