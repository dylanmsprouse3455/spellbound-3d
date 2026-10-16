# Mission 1 — Visual and Optimization Batch 2

Date: 2026-10-16

## Scope

Updated only the isolated Mission 1 preview directory on the existing GitHub Pages origin. The live root page, Ch08 source assets in the original working directory, and Cloudflare/Tailscale routing remain outside this change. Work was prepared in a separate git worktree from the previously published preview.

## Visible changes

- Food court service counter and menu boards; arcade cabinets; clothing displays and varied shop fascia.
- Clustered fallen debris and soft contact shadows beneath furniture and characters.
- Adjusted floor brightness, fog and lighting balance without adding environmental realtime lights.
- Fixed a fixture counter bug that previously kept all fluorescent banks dark; working banks now flicker at a limited update rate.
- More readable enemy skin tones, asymmetric clothing scraps and shoulder detail, using the existing rig.
- Hit flash now restores the original materials instead of permanently tinting enemies blue; eye glow turns off on death.
- Smaller HUD; 98 × 48 CSS-pixel portrait ability buttons; safe-area spacing and landscape layout.
- Corrected wing labels, side-corridor openings and floor boundaries.
- Follow camera stops before large walls and lifts near very tight corners, preserving the original view elsewhere.
- Escalators now reach guarded top landings. Targeting and enemy attacks respect the height difference.

## Measured comparison

Same initial atrium camera, 390 × 844 CSS-pixel iPhone-emulated Chromium viewport, pixel ratio 1, mobile shadow maps disabled in both versions.

| Metric | Previous preview | Batch 2 |
|---|---:|---:|
| Draw calls | 156 | 80 |
| Renderer geometry resources in this view | 129 | 30 |
| Scene children | 557 | 144 |
| Rendered triangles | 87,146 | 91,678 |
| Ch08 GLB bytes | 14,637,724 | 4,278,288 |
| Enemy GLB bytes | 8,091,444 | 1,378,332 |
| Enemy animation clips in GLB | 43 | 5 |

The two GLBs together are approximately 75% smaller. The triangle count rose approximately 5% because the batch adds visible shop and clothing detail. Draw calls vary with camera position; the table describes the initial view, not a full-map maximum. The initial texture count rose from 12 to 19 with menu/contact textures, while copied Ch08 images were reduced to at most 1024 pixels per side.

## Asset safety

The optimized GLBs are new files; original bundled GLBs remain available. Node transforms, joint lists, skin data and retained non-image buffer data were checked against their originals. Images were resized/recompressed; 38 unused enemy clips and their unused buffers were removed from the copied enemy file. No animation retargeting was introduced in this batch.

See asset-optimization.json for exact image and file measurements. Reproduction helpers are under tools/.

## Verification and evidence

- All eight Ch08 FBX files parsed in Chromium: one clip and 53 tracks each.
- Four animated enemies loaded. Patrol/pursuit, damage/hit reaction and inactive death state were exercised.
- Actual browser touch events selected both abilities, moved Ch08 and released to a stable stopped position.
- Touch ascent reached y=5.08 at the landing; descent returned to ground level. The ground-enemy warning was absent upstairs.
- Portrait and landscape ability controls fit within their viewports with 48-pixel button heights.
- Corridor, tight-wall, atrium, walking, hit and death screenshots were captured and visually inspected.
- Browser checks recorded no severe page errors.
- evidence/qa-results.json contains the movement, animation, combat and stair checks; evidence/camera-qa.json contains the later camera/visual checks.

## Limits

Physical iPhone Safari FPS and thermal behavior remain unmeasured. Headless Chromium software rendering is not a phone performance benchmark. The environment remains a procedural, stylized prototype with display/counter alcoves; full shop interiors and a connected upper balcony route are not built. Enemies use the existing generic humanoid rig. Death still plays LayToIdle in reverse; this batch does not replace it with a dedicated death clip.

The live game has not been integrated with this preview.
