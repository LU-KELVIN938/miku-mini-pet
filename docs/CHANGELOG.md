# 2026-10-10 · Lightweight motion update

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
