# Wood-fire ambience

The Green Warhost Mission Board has one continuous, quiet wood-fire layer alongside its occasional goblin sounds. The brief was soft dry crackles, settling embers and muted pops, without roaring fire, loud snaps, voices or music. Original generation is preserved in `staging-sfx/event-ambience-v1/wood_fire.mp3`; processed playback is `frontend/public/assets/sfx/ambient/wood_fire.mp3`. Both are local generated media, excluded from public Git.

Generated with ElevenLabs sound-effects v2 and its loop option: 24 seconds, one paid request (API-reported cost 240). The request receipt and measured levels are in the local ambience manifest. Processing softens treble at 4.5 kHz and limits peaks; no per-cycle fades are applied. Actual listening remains a user review, rather than an automated quality claim. [Official generation API](https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert).

The existing ambient player starts one looping layer after audio unlock. It fades in over 1.8 seconds and out over 1.2 seconds when leaving the public/private board or when the Goblin event ends. Base, roster and combat do not inherit this layer. Hidden-page suspension releases it; returning starts a gentle fade-in. Master and Ambient Sounds volume apply, including mute. Failed files do not retry continuously. No additional animation loop or audio timer is introduced.

Use Sound settings → Preview ambient sounds to hear the new clip. Existing generation tool supports `--only wood_fire`, and `--process-only --only wood_fire` reprocesses the preserved original without another paid request. The tool never replaces an existing generated original.
