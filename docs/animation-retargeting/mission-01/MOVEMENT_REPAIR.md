# Mission 1 — Exploration/Combat Movement Repair

Date: 2026-10-16

The published preview used Walk and a 2.5-unit movement speed everywhere. The local exploration speed change had been omitted when the isolated preview was published.

Restored behavior:

- Exploration uses the existing Standing Run Forward clip and up to 4.25 units/second. Run is preloaded with Idle and Walk.
- Enemy proximity enters combat movement at 7 units. Combat movement remains active until the target is more than 8 units away to avoid rapid mode toggling.
- Combat retains the existing 2.5-unit speed, backpedaling/strafing, channeling pose, warning ring and automatic attack logic.
- Hand effects appear near enemies or during an active attack; exploration is free of permanent hand effects.
- Releasing touch stops movement. Returning to exploration restores Run; stopping restores Idle.
- Animation selection now also recovers when the requested locomotion state is unchanged but an attack cancellation changed the active clip.

Verification: iPhone-sized Chromium with actual browser touch events. Exploration selected Run at 4.25 with hand effects hidden; proximity selected Back at 2.5 with effects and warning visible; stopping near a target enabled the existing lightning channel. Leaving range restored Run; release restored Idle at speed 0. No severe browser errors were recorded. Running phases and the combat-ready pose were visually inspected.

Evidence: evidence/movement/results.json and the four movement screenshots. The live root game page and tunnel configuration are unchanged.
