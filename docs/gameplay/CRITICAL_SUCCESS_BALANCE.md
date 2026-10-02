# Critical success and progression

Ordinary success pays normal contract rewards and rolls normal loot. Mission-specific discoveries remain available on ordinary success; critical bonuses improve their chances without guaranteeing an item. This pass changes rolled critical odds, not item drop rates.

## Soft caps and exceptional mastery

Pass the d20 success check first, then use an independently seeded percentile confirmation. Special critical criteria must match. A natural 20 does not automatically award a critical. Chance depends on the margin above mission difficulty: relevant lead capability plus support, racial, role and authored modifier bonuses plus the die, minus difficulty.

| Rank | Close success | Soft cap | Margin to reach soft cap | Pure-stat limit |
| --- | ---: | ---: | ---: | ---: |
| E | 3% | 20% | 12 | 100% |
| D | 3% | 16% | 12 | 100% |
| C | 3% | 12% | 12 | 100%, exceptionally distant |
| B | 3% | 10% | 12 | Below 50% |
| A | 2% | 8% | 8 | Below 10% |
| S | 2% | 5% | 8 | 5% |

These percentages are conditional on a successful check, not overall mission odds. The actual lineup preview includes failure, critical failure and any locked critical criteria. A/S reach their useful soft caps earlier because their contracts are rare and cost more claim points. E/D/C continue growing well beyond the soft cap. B/A continue growing slowly toward their stated limits. S stays at its explicit stat limit.

After the soft cap, E/D/C use a shifted square-root curve: E gains `10 * (sqrt(extra + 16) - 4)`, D gains `8 * (sqrt(extra + 25) - 5)`, C gains `3 * (sqrt(extra + 100) - 10)`. Each additional percentage becomes more expensive. B gains `40 * extra / (extra + 240)`; A gains `2 * extra / (extra + 80)`. B/A are truncated to 49.99%/9.99% so rounding cannot reach forbidden thresholds. Confirmation uses 10,000 equal faces, representing percentages to two decimals. The UI displays overall odds to two decimals.

| Margin above difficulty | E | D | C | B | A | S |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 12 | 20% | 16% | 12% | 10% | 8.09% | 5% |
| 24 | 32.91% | 24.66% | 13.74% | 11.9% | 8.33% | 5% |
| 40 | 46.33% | 34.24% | 15.94% | 14.17% | 8.57% | 5% |
| 80 | 71.65% | 53.14% | 20.88% | 18.83% | 8.94% | 5% |

## Reaching a genuine 100%

Existing natural-one critical failures remain until an eligible E/D/C check reaches 100% confirmation. At that point, exceptional mastery overrides the natural one. Otherwise a supposed 100% would secretly be capped at 95%.

E reaches 100% at margin 140, D at 228, C at 1460. To guarantee an entire mission rather than only its best possible die roll, even the minimum die must reach that margin. At difficulty 14 this requires total team check bonuses of 153, 241 and 1473 respectively. These are long-term curve targets, not a claim that current normal equipment and character progression already provide those values. No new stat-growth system or automatic critical consumable was added. Special criteria remain mandatory even at extreme stats. B/A/S natural-one risk remains; their maximum overall odds are slightly below their conditional limits.

## Scenes and tactical missions

Dialogue checks use the same rank curve. A clean completed scene gets one final confirmation based on average successful-check margin. Adding nodes cannot multiply final critical opportunities. Unchecked choices cannot create critical success alone. An earlier failed check prevents a critical finale under the existing clean-scene rule.

Combat bonus objectives still earn critical success deterministically. These are authored rescue/capture/alarm/protection accomplishments rather than pure-stat critical rolls. Combat loot is separately rolled. Existing debug-forced outcomes remain available under their criterion gates.

## Pacing and scope

Pools refresh every 30 minutes. E/D cost one claim point, C two, B three, A four and S five. Two opening waves provide five points apiece; free-for-all adds three plus upgrades and ten extra while solo. Lower-rank exclusive drops give developed teams a reason to revisit. A/S have an earlier soft-cap boost because players get fewer attempts.

Existing accepted missions resolve using this curve when finished; completed results stay unchanged. Saved lineup analyses may show earlier odds until refreshed. The resolver and current previews share one classifier. Normal reward scaling and drop tables remain unchanged. Future dedicated perks/items/consumables may break stat-only limits through an explicit separate mechanic; this pass does not invent those overrides. Review actual trial completion frequencies before further tuning.
