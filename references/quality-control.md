# Quality control

Rendering without an exception is not evidence that a scene communicates clearly. Review by clock time.

## Approved-script conformance

Before rendering, confirm the YAML and scene implementation reproduce the approved storyboard and subtitle narration. Do not use Phase 3 review to rewrite its scope, claim strength, scene order, term teaching, or subtitle prose; revise the approved script only with user approval.

## Mandatory review gate

Do not publish or replace the final MP4 until this review has passed. Snapshot named beat times and every clip boundary into `review/`, then repair issues following the scene loop. Render a complete draft MP4 and inspect decoded samples from every clip before the high-quality render. For videos with captions, also inspect captioned frames from every cue that spans two lines and every beat with content nearest the caption clearance boundary. Do not omit an approved scene; if the loop reaches a blocker, report it.

## Scene loop

1. `scripts/apply_timeline.py` so hosts match YAML.
2. Run `scripts/lint_scene_contract.py --animation-dir animation/`, then `hyperframes lint` on the animation directory.
3. Run `scripts/review_times.py --timeline timeline.yaml` and snapshot the emitted `--at` list: clip starts, beat starts and midpoints, end holds, and paired clip-boundary frames.
4. Inspect those PNGs at full detail. For every non-hold beat, compare its start and midpoint: identify the named focal node that changed state, and reject a scene that shows all future beat content from the first frame unless the approved storyboard explicitly calls it a static overview. Mark the clearance boundary from `margin.bottom` before judging content near the lower edge.
5. Render the whole composition at `--quality draft`, then run `scripts/review_encoded_video.py --timeline timeline.yaml --video review/<paper>.draft.mp4 --output-dir review/encoded-draft/`. Fail only when a clip is near-black at start, middle, and end. Treat a single dark sample as a warning and inspect that PNG. Inspect start/middle/end PNGs for every clip; this gate catches encoded-video failures that composition snapshots cannot.
6. After captions are burned into a pending video, run `scripts/review_times.py --timeline timeline.yaml --two-line-captions` and inspect those frame times plus every lower-edge beat; the subtitle must be readable and must not cover scene content. Also inspect any cue that warned it exceeded `max_lines`.
7. Check the clip against its approved purpose and end state.
8. Fix only the hit scene file or YAML fields responsible for the problem, then rerender the draft/pending video and repeat the relevant review.
9. Repeat, with at most three failed repair attempts before reporting a blocker.

## Visual checks

- No title, label, equation, graph, or moving stroke crosses the safe margin configured in `timeline.yaml`.
- The subtitle clearance zone configured in `timeline.yaml` remains free of all essential content, persistent cards, diagrams, focal objects, and their transformed states.
- Future or retired beat nodes do not retain flex/grid allocation that pushes active content into another node or the caption clearance zone.
- Text remains legible against every background it crosses. Body copy, titles, and default labels use `var(--text)` and keep WCAG AA contrast on `background`.
- Text does not obscure charts or moving objects; arrows have an unambiguous target.
- KaTeX glyphs match the YAML `tex` and do not drop symbols.
- Formula rendering is scoped to the scene root and appears once; it does not show MathML or raw-TeX fallback text.
- Highlights target the named SVG id; labels disappear when their object is gone.
- Semantic colors remain consistent with earlier clips.
- Motion has a clear visual target and does not compete with unrelated motion.

For charts, also check axes, units, baselines, legend meaning, data order, and uncertainty. Compare reconstructed values with the paper.

## Final checks

After the mandatory review gate passes:

- Run the verification and atomic-publication command in [hyperframes workflow](hyperframes-workflow.md).
- Confirm the first and last frames are intentional. Automated checks cannot judge visual legibility or composition, so retain the reviewed snapshots with the output.
