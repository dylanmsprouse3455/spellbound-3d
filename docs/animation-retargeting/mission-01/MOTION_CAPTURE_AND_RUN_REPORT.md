# Preview 6 — reproducible motion capture and Ch08 running

## Findings
Preview 5 changed the arm twice per frame: the animation mixer applied the source Run and a procedural layer changed the same joints. The earlier checks mainly covered arm height. Full-cycle review showed insufficient backward swing: hands stayed forward through the back half of the stride. A captured automatic Fire combo followed by running did not show a stale attack action once running settled; the screenshot alone could not establish a Fire-specific failure.

## Implementation
The player now loads Ch08_Run_Verified_v1.json for exploration Run. It retains the source leg and torso tracks and bakes eight shoulder/arm/wrist tracks into 46 samples over a 0.733333-second loop. Opposing leg motion drives the arm swing from -1.0 to +0.35 radians. Shoulders use neutral local orientation; wrists align with forearms. The 53-track clip has a continuous arm loop seam. Procedural running-arm corrections are removed from gameplay. Running suppresses the legacy throw arm layer; Lightning already yields to exploration Run. Locomotion actions explicitly repeat when reused.

## Local capture
The Capture motion button exports the last 10 seconds of active actions and blend weights, motion/attack state, arm writers, and the actual full bound rig local rotations and positions. It records at most 160 samples, with detailed tracing at 15 Hz. Capture stays in memory until explicitly exported through a local Blob download. No capture upload, background storage, account data or remote commands are added. Export was checked for fetch requests.

The same-origin diagnostic motion-review.html opens JSON files locally, replays the recorded rig, offers front/side/back views and scrubbing, and outlines the right arm. Replay normalizes root location and facing for inspection. Imported files are restricted to 4 MB, 160 samples and 200 joints per sample with finite bounded numeric values; names map only to existing rig bones. File content is parsed as data and is never executed or used as a URL.

## Evidence and verification
- evidence/motion-ownership/fire-reproduction.json: automatic Fire sequence before replacement.
- bake.json and clip-validation.json: track/sample counts, finite unit quaternions, zero arm loop seam difference.
- baked-run-cycle.png and cycle-review.json: eight phases from front, right side and back.
- verification.json: touch-driven Fire combo including two-hand wave, running in four directions, stop, Lightning channel and return to Run, wrist alignment, single arm writer during settled running, bounded capture, local export and successful file replay. The final local replay matched all saved joint rotations and local positions with zero measured difference. A real downloaded JSON file was verified on disk.
- capture-replay-fixture.json is a synthetic test session, not a user recording.

A first concurrent software-rendered combat wait timed out; the sequential combo completed. That initial touch viewport still selected desktop quality; the final checks also set an iPhone user agent and exercise the mobile rendering path. The old pose assertion also assumed near-horizontal wrists and was replaced with forearm-relative palm roll plus anatomical height limits for the larger swing. A missing diagnostic favicon was corrected. These failed checks were not counted as success.

Tests use Chromium touch emulation at 390 x 844; this is not physical iPhone Safari or a measured iPhone FPS result. If an iPhone pose still looks wrong, save a capture immediately and pair it with a screen recording.

## Reproduction
Serve the checkout, then run tools/verify_motion_ownership.py [preview URL] and tools/review_run_cycle.py [preview URL]. tools/bake_verified_run.py reconstructs the baking lab from the recorded Preview 5 git revision 3e87598 and exports the new clip; it requires the local HTTP server, Selenium and Chromium. The main game root and original source animation assets are preserved.
