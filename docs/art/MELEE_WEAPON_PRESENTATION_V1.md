# Melee weapon and capture-net presentation V1

Implemented in dev, October 5, 2026. Uses the built-in imagegen tool and ElevenLabs sound effects through the existing generator. Original atlases and API audio are preserved; no existing asset pack was removed. Media remain local/ignored under the existing repository policy.

## Runtime rules

Basic melee attacks derive their delivery from the equipped weapon: swords slash, axes hack, hammers/maces/flails crush, clubs/quarterstaffs strike bluntly, unarmed hands punch, spears/daggers stab. Legacy enemy snapshots fall back to weapon names. A definition may explicitly override `melee_style`. These profiles change motion/art/audio only, never damage or cell displacement.

Driving Strike has an authored blunt delivery regardless of weapon. Earthbreaker and Chain Snare retain their authored effects. Slashes use a small twisting flinch; crushing uses compression/shake; stabbing uses a tight jolt. Fists use one quick jab for the one resolved attack, not invented combo damage. All share the existing 185 ms contact marker. Structure hits retain structure-impact sounds instead of flesh hits.

Any equipped capture weapon named net/mesh emits the net cast, including a Fighter holding one. Existing capture range and chance still apply. Other capture weapons retain their delivery. The painted rope opens and rotates during flight, reaches the target at 320 ms, then cinches on success or slips off on failure. The feedback reads Subdued/Escaped; no fake HP damage number is added. Successful capture still uses the existing unconscious condition. Reduced motion shows a short static fade. Temporary sprites are removed after playback.

## Art generation brief and exact atlas layouts

Melee brief: one transparent canvas requested at 2048x1536, uniform 4-column/3-row cells, equal spacing by cell, no separators/text/gutters; one stylized painted impact centred in each cell with generous transparent margins. Match warm ivory/gold brushwork of combat-presentation-v2 physical_hit.png; muted red flecks only, SFW, no gore, people, weapons or opaque ground plates. Pair immediate-contact and dissipating-fade forms for each family. Order: slash contact/fade, hack contact/fade, crush contact/fade, blunt contact/fade, fist contact/fade, stab contact/fade. The tool returned 1536x1024; import uses relative cell boundaries and preserves proportions instead of stretching.

Net brief: one transparent 1024x1024 atlas, exactly 2x2 equal square cells, no gutters, separators or text; 64px transparent margins requested. One consistent coarse brown rope net with small bronze weights, pure overhead, warm painted fantasy style. No pole, character, anatomy, neon or gore. Order: folded (top-left), opening (top-right), spread (bottom-left), cinched (bottom-right). The tool returned 1280x1280; import uses its actual dimensions. Art is crossfaded/transformed with the existing browser animation system; no separate Effekseer runtime required.

Sources: staging-ui/melee-families-v1/atlas.png and staging-ui/capture-net-v1/atlas.png. Imports: `python tools/import_melee_effects.py` and `python tools/import_melee_effects.py --net`. Each exports 256px transparent square canvases with unchanged proportions and manifest records. Runtime assets are under frontend/public/assets/melee-families-v1 and capture-net-v1.

## Audio

Twelve family swing/contact clips and three net cast/cinch/slip clips. Reproduce with the existing tools/generate_sfx_pack.py --pack melee-families-v1 or --pack capture-net-v1; cached source clips avoid repeat paid generation. SFX_GENERATION_GUIDE.md preserves all individual prompts. Dry, nonmelodic, softened treble, no screams/gore. WAV exports are 48kHz mono, normalized with peak limiting; original API MP3s remain in staging-sfx. Each swing plays before contact; misses do not play the weapon flesh hit.

Audition pages: /assets/sfx/preview-melee-families-v1.html and /assets/sfx/preview-capture-net-v1.html. Automated checks confirm valid/nonempty audio and no clipping. Subjective listening approval is still the player's review, not claimed by automated checks.

## Validation and limits

79 related backend tests, 244 frontend tests and frontend production build pass. Isolated real-renderer browser playback exercises all six families, successful/failed nets, 74 weapon choices and feedback timing. Screenshots: staging-ui/melee-families-v1/*-browser.png. No live saves or production touched. Browser fixture uses temporary combat data; backend persistence tests separately cover isolation. Existing bundle size warning remains. Ranged weapon redesign and individual dagger combos are deferred.
