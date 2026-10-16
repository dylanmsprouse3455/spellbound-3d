# Preview 5 — running arm orientation

Scope: exploration running movement only.

## Cause
Preview 4 aimed elbow and wrist positions using rotations from the Run clip. A direction constraint does not determine bone roll, so the source arm twist remained. It also left the source wrist rotation intact. Visual stride inspection showed mismatched palm orientation. The previous height-only checks missed this.

## Correction
Rebuild upper arm and forearm orientation from the character neutral local rotations before applying the opposing leg swing. Reduce swing amplitude from 0.9 to 0.65 (cap from 0.55 to 0.42 radians). Align the wrist with the forearm and keep the index-finger side upward using the actual middle/index/pinky bone geometry. Blend the completed pose from the source pose on entry.

All pose correction is gated to exploration Run. Speed values, combat code, environment, assets, controls and root page are unchanged.

## Verification
Rendered stride screenshots reviewed during diagnosis and after correction. Emulated iPhone touch test covers Run, combat backpedal, stationary lightning channel, Run again and Idle. New checks validate finger/forearm alignment and consistent wrist orientation in addition to lowered arms, including after combat. See evidence/running-arms-v5/results.json. Physical iPhone Safari still requires user observation.
