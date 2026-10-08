# Captor V1 art and audio

Generated October 7, 2026 with the built-in image generation tool; no LinkAPI helper. Existing portraits, punch animation and net/Subdue animation are reused.

## Packed images

Source atlas: staging-art/captor-v1/atlas.png. Runtime eight square icons: frontend/public/assets/captor-v1/{subduing_blow,bola,hook_and_drag,abduct,restraining_hold,blitz,restraint,clean_capture}.png.

Atlas prompt direction: a production fantasy Captor 4x3 packed sheet, eight ability icons plus bola, hook, rope and manacles props, consistent warm bronze/teal on navy painterly art, equal tiles, no letters, no borders or gutters. Original generated output: C:/Users/neo_m/.codex/generated_images/01a0b5d5-838b-7532-a029-207add4a0d21/exec-1e172ccf-ccdf-41d5-9a82-7e485f73b700.png.

A second transparent 4x1 strip supplies cleaner effect props: staging-art/captor-v1/props.png. Prompt direction: matching top-down weighted bola, chain hook, coiled restraint rope and manacles, four isolated equal cells with real transparency, no background or text. Original: same generated-images directory, exec-50180439-5b81-4d25-85c1-df7bd0dc4869.png. Runtime bola_prop.png, hook_prop.png, rope_prop.png and manacles_prop.png are 256-pixel transparent canvases in the same runtime directory; manacles are reserved for further capture presentation.

Reproducible importer: tools/import_captor_art.py; crop manifest staging-art/captor-v1/crops.json. It imports the icon atlas and replaces effect props from the transparent strip. Images are shared across units, not generated per character. Runtime rope tightening, spinning bola, chain tether/retraction and Blitz cue compose these small assets with CSS and existing actor motion; no separate Effekseer runtime is needed for this pass.

## ElevenLabs foley

Runtime frontend/public/assets/sfx/{captor_bola,captor_drag,captor_hold,captor_blitz}.wav. Retained original MP3s and generation reports live in staging-sfx/captor-v1/<clip>/. Exact prompts, durations and regeneration script: tools/generate_captor_sfx.py.

Prompts request compact grounded rope/weighted catch, chain catch/earth friction, restraint creak/cinch and pursuit footfalls respectively, without music, voices or shrill ringing. Existing basic Subdue net audio is preserved. Foley and effects are attached to action/contact packets; Resolve feedback uses teal and avoids lethal blood/contact flashes.

Browser fixtures and captures: tools/captor_browser_qa.mjs and data/browser-qa/captor-{ready,hold}.png. Artistic and sound mix feedback remains open; generated clips were wired and exercised, not declared a final mastered mix.
