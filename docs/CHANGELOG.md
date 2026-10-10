# 2026-10-10 · Native walking gait repair

- Reused existing Miku source pixels in an independently controlled two-leg textured rig, as explicitly chosen by the user. Added the missing opposite leading-foot half-cycle; no paid image generation.
- Baked eight distinct rightward poses and mirrored individual cells for leftward motion after independent QA approval. The frame order and native 120ms/220ms durations are preserved.
- Replaced the 32-frame animated atlas with a single static v2 atlas. The host now controls movement phase; removed the independent 1280ms image-clock cycle.
- Retained the previously approved static micro-action base in non-locomotion rows and the original sixteen look cells. Atlas size decreased from 44,272,996 to 2,653,580 bytes.
- Independent file QA accepted both movement rows with warnings for angular knees, overlapping feet near the seam and the host-defined final hold. No major structure, identity, clipping or direction issue remained.
- Final CSS/data-URL headless validation covers all nine rows, eight distinct movement poses, 1060ms cycles, short stop, reversal, three-cycle idle fallback, reduced motion and sixteen static look cells. The actual Codex window has not been inspected or automatically reloaded.
- Added content-hash gates for approved walking rows, final browser verification, installation and packaging.

# Earlier 2026-10-10 · Lightweight motion update (superseded native implementation)

## Native Codex correction

- The earlier registration calculations were all zero: the previously installed compatibility atlas had exactly the original visible pixels. Actual interpolation and layered animation only ran in the standalone player. Those earlier native-improvement claims were incorrect.
- The main deliverable now loads as a Codex v2 custom pet: a 32-frame animated WebP atlas, baked offline from the original Codex sprite layers and accepted RIFE gesture frames. No standalone process is required during playback.
- The installed Codex 26.930.4958.0 bundle was read to confirm its data-URL image loader, 8x11 CSS grid, fixed action counts/durations and sixfold idle slowdown. Program files were not modified.
- The embedded image animation changes eight states; the failure reaction remains original. The 16 original directional drawings gain foot-anchored breathing (vertical scale +/-0.3%) so pointer/caret tracking does not freeze the pet. Their initial frame retains the original visible pixels; direction semantics are preserved. Fully transparent RGB may be filled by the WebP animation decoder; it remains invisible.
- Added a standard static fallback, native-only installer/package, original-versus-native previews and tests that confirm the actual installed asset changes over time under the same CSS/data-URL mechanism.
- Corrected a closed-eye skin sampling error before acceptance. The final baked model keeps the original native sprite's identity and proportions.
- The running Codex window has not been restarted or inspected. A full application reload/reselection is required to replace its cached image; a same-engine headless test is not an in-app visual verification.

## Earlier standalone implementation

- Preserved the original atlas as `assets/source-spritesheet.webp`.
- Applied bounded horizontal registration to the existing standard frames; no per-frame rescaling or intentional jump-height change. The existing static idle/default slot and all 16 look cells are preserved.
- Added an editable six-layer PSD cut from the existing canonical artwork. Blink lids reuse an existing blink frame. No new AI images were generated. Small skin regions behind the separated eyes use cloned local skin pixels.
- Reused Anime2.5DRig for continuous breathing, blinking, restrained head motion and twin-tail sway. These are lightweight 2.5D motions, not a finished Live2D/Cubism model.
- Added an offline interpolation pipeline and preserved cyclic last-to-first transitions, original loop durations and long holds. Older `rife-anime` experiments produced material edge artifacts and were rejected; final acceptance is recorded separately for the newer model.
- Added a player that chooses continuous rigging for idle/work/wait/review and accepted frame sequences for locomotion/gestures. It includes original comparison, a registered-frame fallback, pause, state debounce and 30/60 fps targets.
- Added a minimal pywebview desktop host and reused the existing Codex record parser. No startup registration, desktop-wide pointer following, camera or microphone input.
- Accepted 23 new RIFE v4.6 midpoint poses across four actions. Two failed transitions retain the preceding source pose for its original duration; duplicate time slots are not counted as new poses.
- Pause hidden/inactive layered animation to reduce unnecessary work. Returning to the current Codex state cancels any obsolete queued transition.
- Passed both headless player integration and a scoped actual EdgeChromium pet-window check. These verify loading/state selection, not sustained FPS or resource usage.

Validation reports distinguish native atlas geometry, headless browser integration, independent image QA and actual desktop-window testing. The pre-existing `validation-extended.json`, direction reports and `standard-visual-qa.md` describe the original source artwork; they do not claim a new performance benchmark.
