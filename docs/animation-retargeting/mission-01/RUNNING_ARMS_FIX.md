# Preview 4: lowered running arms

The imported Run clip raises an arm near the head. The isolated preview now adds a running-only arm pose after the animation mixer: upper arms stay below the shoulders, elbows remain bent, and each arm swings opposite its leg. Original clips, skinning and leg animation are unchanged.

The pose applies only during exploration Run. Combat walking/backpedaling, lightning stance, automatic attacks, warning circle and fire selection retain their existing logic. Exploration speed remains 4.25; combat speed remains 2.5.

## Verification

Chromium with a 390 x 844 iPhone viewport and actual emulated touch input passed Run → combat movement → stationary lightning channel → Run → Idle. Both upper arms pointed downward and both hands stayed below their shoulders at two stride phases and after leaving combat. No browser console errors. Screenshots run-a.png and run-b.png were visually reviewed. This is browser emulation, not physical Safari testing.

The West Wing test teleport produced an obstructed combat screenshot; combat transitions were verified from actual animation/combat state and bound bone data. Camera behavior was not changed in this arm correction.

Evidence: evidence/running-arms/results.json and screenshots. Reproduce with tools/verify_running_arms.py [URL]. The live root page and hosting configuration are unchanged.
