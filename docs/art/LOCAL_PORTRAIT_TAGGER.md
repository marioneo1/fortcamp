# Local structured portrait tagging

Implemented October 3 in standalone sibling project:
`E:\Other Games\Fortcamp\character-tagger`. Its README contains the complete
setup, configuration, schema and troubleshooting reference. Cloud tagging was
paused at the user's request; this tool requires no API key.

Pinned model: SmilingWolf WD EVA02-Large v3 ONNX, revision
`b25b82a03f7282e41aa2f257a52c7583b710bd1c`. Own Windows virtual environment and
CUDA/cuDNN runtime wheels; local review server at 127.0.0.1:7862. No game/prod
save, source portrait or existing appearance registry is modified.

## Identity and visual attributes

Pool-assigned race/species and gender are imported as known metadata, not
classified again. Champion race and available gender come from authored
catalogues parsed without executing game code. Original pool cells are preferred;
compatibility aliases are excluded. Stable IDs include collection/pool/variant
paths. Portrait role suffixes aren't treated as actual classes.

WD detects hair, eyes, skin, anatomy, clothing, equipment and expression. Editable
controlled mappings keep hair/skin/eye colors separate; skin never implies race.
Unknown values aren't filled from race defaults. No captions/narrative are generated.

Default thresholds: >=0.65 accepted; >=0.40 and <0.65 review candidate; lower
scores preserved only in raw data. Category thresholds and required fields are
configurable. Single categories choose the highest score, retaining alternatives;
multi categories deduplicate. Scores are not calibrated accuracy percentages.

## Persistence and review

SQLite separates immutable raw runs, original/updated normalization, known game
metadata, manual overrides, edit history and review state. The UI supports
corrections, accepting/removing/adding tags, marking reviewed, navigation, review
filters, mapped raw scores, phrase search and structured filters. Stale saves
from two windows are rejected. Manual edits never overwrite machine scores.

Exports: `output/character_tags.json`, `character_tags.csv`, `raw_tags.json`.
Raw export includes all scores/historical runs; UI/normalized mappings are SFW.
Search supports `blue-haired green-skinned woman` or
`api.search_characters(gender='female', hair_color='blue', skin_color='green')`.

Resume checks filename/location/size/mtime/model; optional SHA-256 comparison.
Rules remap cached scores without inference. Forced retags retain manual edits
but reset review state. Corrupt images don't stop other images; failed batches
retry individual images.

## Validation and limits

All **2,072** installed images were processed successfully. Main GPU pass:
2,059 new images / 237 seconds (~8.7 images/s), with 13 pilot images skipped.
Subsequent full-library run skipped all 2,072 without retagging. GPU/CPU real
inference and Windows setup launcher passed. Eighteen automated tests passed;
browser QA covered edits, suggestions, saves, raw scores, search and mobile layout
in an isolated fixture DB. Nine Champions and twelve original samples were
visually checked; five corrections remain separate from raw scores, and samples
were not falsely marked fully reviewed. Gojo's blindfolded eyes stay unknown;
Sakura Matou wasn't confused with Sakura Haruno, who isn't currently installed.

Common colors/features work, but ordinary skin tones, small eyes, slime and
unusual anatomy often remain unknown. Warm lighting can skew colors. No claim
of full-library accuracy is made. Full raw output is approximately 1.3 GB; the
initial working database was about 432 MB. Normalized data is much smaller.

## Deferred integration

Fortcamp still uses existing appearance registries. Do not publish unreviewed
detections over game/user metadata. Next: review representative original-race
samples, decide on game-facing structured fields, then add a reviewed-only
importer preserving individual manual descriptions, shared frames and portrait
IDs. Existing CLIP auditing is legacy; don't rerun it over reviewed replacements.

An optional later VLM should focus on missing skin/material, uncertain colors
and obscure anatomy while retaining WD raw scores. Qwen is not installed or
benchmarked here. Compare any candidate against reviewed actual portraits;
exact race classification is unnecessary for already assigned pools.
