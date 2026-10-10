# Mission resource reward preview ? UI proposal

Status: proposed October 9; awaiting layout discussion. No reward display added.

Use one compact Resource Rewards comparison below outcome chances in the mission
briefing. Four visible rows, in order: Critical Failure, Failure, Success, Critical
Success. Dynamic resource columns contain only currencies/materials relevant to
that mission: icon plus short label, aligned numeric amounts or random ranges.
Use a dash for no reward, with accessible text identifying zero. Highlight Success
subtly; Critical Success uses gold emphasis. Failure styling is muted, not alarming.
Avoid four separate cards and repeated prose. Keep existing possible equipment
separate; no hidden drop names/probabilities exposed.

On narrow screens retain four outcomes as stacked rows, each with wrapping
resource chips. No tiny text or sideways scrolling. Initial party selection may
update disclosed party bonuses if they actually affect those rewards. Label rewards
before mission costs; keep losses/fees separate so gains are not mistaken for net.

Source amounts from the real award rules, not authored duplicate forecasts or
placeholder guesses. Success uses rank commission plus normal reward block;
Critical Success adds critical block; Failure currently offers only a small
random token gold payout when pays_gold is true; Critical Failure has no normal
contract resource payout. Conditional battlefield recovery, radiant loot, secrets,
gear fallback gold and other variable extras must be distinguished from the
base contract estimate. Known resource reward rolls can be represented honestly
as possible extras/ranges rather than guaranteed amounts. Actual captured/defeated
units are unknown at briefing time; do not promise their loot.

Prefer one shared preview calculation for all missions with supported award data,
starting validation with audited E/D quests. Unsupported special reward rules
should show an honest conditional note, not fabricated numbers. No per-mission
manual tables required. Do not simulate rewards or mutate RNG/saves to compute it.
