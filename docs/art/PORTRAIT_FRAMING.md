# Portrait framing and Portrait Lab

Implemented in development: **Mission Board → debug controls → Open Portrait Lab** lists all installed generic pool images and Champion defaults/expressions. Search by race, name or image ID; filter collections or individual image sets. Sixty circle previews per page keep the library manageable.

Click a preview to edit it. Drag the circle or use horizontal/vertical sliders; circle size and mouse wheel change how much of the original image is included. The editor shows the full photo and a live circular preview. Save stores a shared default for that image. **Use recommended framing** removes the library correction and returns to the automatic recommendation.

**Roster → Appearance → Adjust portrait framing** saves an individual character override. This takes priority over library defaults. A replacement photo gets its own framing; the old photo's override is not applied to it. Framing never changes portrait identity, filenames, pool order or the original full photo. Image proportions are preserved.

Automatic recommendations live in `data/portrait_framing.json`; manual library corrections live separately in `data/portrait_framing_overrides.json`, so rerunning `tools/audit_portrait_framing.py` does not erase corrections. Keep both files when transferring local artwork to another installation; these local art files are excluded from Git. Portrait Lab is denied in production even if debug is accidentally enabled, and requires a server admin unless dev bypass is enabled. Uploaded player photos are edited through their character, not exposed in the shared art browser.

The first automatic audit covers 1,304 portraits. Face detection is an estimate, especially for nonhuman faces, horns and centaurs; the Lab exists for visual review and corrections. Framing cannot restore head/hair pixels already missing from the source. The newer Aasimar female healer sheet was reimported with the same twenty IDs and backed up before replacement. Future pool imports preserve full cells with padding rather than trimming rectangular cells to squares. New upload thumbnails preserve aspect ratio; legacy upload thumbnails use their full source for framing.

Validation: backend tests cover persistent defaults, audit replacement, individual overrides, portrait replacement, catalogue keys and production/admin restrictions; frontend production build is required. Existing battles may retain an individual character's frame captured at battle creation; shared library recommendations are resolved when battle views are returned.
