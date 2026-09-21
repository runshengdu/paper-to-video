# Clip timeline

Timing, semantic tokens, and formula TeX live in `timeline.yaml`. Scene HTML owns layout, SVG, and seekable motion. An agent edit named as a clock time must resolve to one clip and optionally one beat.

## Source of truth

| File | Role | Who edits it |
|---|---|---|
| `paper-analysis.md` | Technical explanation: all major contributions, concepts, and results | Agent writes; human approves, then freeze |
| `video-script.md` | Narrative approval: duration budget, scene purpose, beats, public-language copy | Agent writes; human approves, then freeze |
| `timeline.yaml` | Clock time, clip ids, tracks, beat map, font, semantic colors, formula TeX, and caption source/layout | Agent edits |
| `animation/index.html` | Root HyperFrames composition; hosts scene clips | Generated from YAML |
| `animation/timeline.css` | Font and semantic color CSS variables | Generated from YAML |
| `animation/scenes/<id>.html` | One scene: HTML/CSS, SVG, paused GSAP | Agent content edits |

Do not store global clock times in GSAP. Scene timelines are always 0-based: local `0` is the clip's `start`. Changing a scene's position on the film is a YAML edit, then `apply_timeline.py`.

## Time model

- Display times as `m:ss` or `m:ss.s` (`1:23`, `1:23.5`).
- Store seconds as a float. Snap to the frame grid: `round(t * fps) / fps`.
- Default `fps: 30`, `width: 1920`, `height: 1080`.
- The composition `duration` is the approved budget from `video-script.md`. No clip may extend past it.
- Never think in frame numbers at the edit surface. Convert frames only at render time.

Resolve a clock time `t` before editing. A single-clip interior time may be read from YAML. Run `scripts/resolve_time.py --timeline timeline.yaml 1:23` when clips overlap, the time is on a clip boundary, or the hit is otherwise ambiguous:

1. Convert `t` to seconds.
2. Find clips where `start <= t < start + duration`. If several overlap, prefer the highest `track`, then the smallest duration.
3. `local = t - clip.start`.
4. Find the beat where `at <= local < at + duration`. If none, the hit is the clip itself.

Print the hit as `clip_id @ local` plus `beat_id` when present. Then edit only that target.

## Hierarchy

```text
composition          full video, one duration
  scene clip         one narrative job from video-script.md
    beat             one on-screen change: diagram, formula, highlight, card
```

Tracks are timeline lanes, not paint order. Use CSS `z-index` for stacking. Overlapping motion belongs on separate tracks.

## `timeline.yaml` schema

Required top-level fields: `fps`, `width`, `height`, `duration`, `font`, `colors`, `clips`. `colors` must define `background`, `text`, `primary`, `secondary`, `accent`, and `muted`. Additional named colors are allowed; `apply_timeline.py` emits each extra key as `--<name>` when the name is a CSS identifier that does not collide with generated layout variables. Ordinary scenes should still prefer two semantic colors plus neutrals. The starter YAML shows required keys, not a house palette; replace every hex value.  
Optional top-level fields: `margin` with `x` (default 140), `top` (default 80), `bottom` (default 200), controlling `--stage-padding-*` in `timeline.css`. `apply_timeline.py` also derives `--frame-width`, `--frame-height`, `--frame-aspect-ratio`, and `--stage-content-width`; use them for scene geometry rather than assuming a fixed canvas.  
When subtitles are enabled, require a top-level `captions` mapping: `enabled: true`, a lowercase three-letter ISO 639 code in `language`, and `layout` fields `font_size`, `margin_bottom`, `max_lines`, and `outline`. Subtitle wording length is chosen in Phase 2 from the suggestions in [video-script.md](video-script.md). `generate_captions.py` copies each beat `subtitle` into the SRT, keeping explicit newlines. `burn_subtitles.py` reads the same YAML font, caption-layout, `colors.text`, `colors.background`, and `margin.x` (default 140) for left/right inset; overlong lines may wrap at burn. `apply_timeline.py` also generates `--caption-clearance-bottom` from `margin.bottom` and a fixed `--caption-clearance-guard` of 16px. The caption block and `margin.bottom` are one layout contract: `margin.bottom` must accommodate `font_size × 1.25 × max_lines + margin_bottom + 2 × outline + 16px`. This is a reserved visual exclusion zone, not merely padding. If a cue's explicit newlines exceed `max_lines`, generation warns and emits the extra lines rather than failing. Inspect those cues in review.  
Required clip fields: `id`, `start`, `duration`, `track`, `file`, `purpose`.  
Required beat fields: `id`, `at`, `duration`, `kind`, `job`.  
`at` is local to the clip. Absolute time of a beat is `clip.start + beat.at`.

Beat `kind` is an unconstrained label. Common values are `diagram`, `formula`, `chart`, `card`, `label`, `highlight`, and `hold`; others are allowed and not validated. `formula` still requires `tex`, and `hold` is still skipped for midpoint snapshots. If a beat needs two jobs, split it.

See `assets/starter/timeline.example.yaml` for a filled example.

## Scene HTML contract

Each `file` is a nested HyperFrames composition:

- Wrap markup in `<template>`. Root has `data-composition-id` equal to the clip `id`.
- Host in `index.html` copies `data-start` and `data-duration` from YAML. Never hand-edit those host attributes.
- Every timed node has a stable `id` matching a beat id or a persistent object id.
- Formula beats need a non-empty `tex` value in YAML. Give the matching scene node the beat `id`; `apply_timeline.py` writes its `data-tex` value.
- To reveal a formula in stages, use multiple formula beats with separate node ids (or mutually exclusive `.beat-slot`s), each with its own `tex`. Do not call `katex.render` from scene HTML.
- Diagrams are SVG with named groups. Highlights target those ids.
- One paused GSAP timeline, registered as `window.__timelines[clip.id]`.
- Tweens use `fromTo` with explicit positions. Never `Date.now()` or `requestAnimationFrame`.
- Animate `autoAlpha`, `x`, `y`, `scale`, `strokeDashoffset`. Do not animate `top`, `left`, `width`, or `height`.
- `autoAlpha`, `opacity`, `visibility`, and `display` may only target scene descendants. Never apply them to `#root`, a `.clip` host, or any ancestor of scene content: HyperFrames owns clip visibility and encoded rendering can diverge from snapshots otherwise.
- For formula nodes, `apply_timeline.py` injects `../formula_runtime.js` after local KaTeX. Do not call `katex.render` from scene HTML; the helper scopes rendering to `#root` and emits HTML-only KaTeX to avoid duplicate visual output. Stepwise formulas are extra formula nodes, not in-scene KaTeX.
- Implement the approved storyboard's named handoffs, including carry, transform, morph, zoom, split, merge, and labeled chapter reset. Default vocabulary also includes fade, slide, highlight, draw-on stroke, count-up, and dim/undim. Scale implements zoom; morphs are state-to-state transforms of the same object ids.
- Use `.scene-content > .beat-slot` for mutually exclusive beat states. Every inactive slot must use `hidden` or `.beat-slot.is-inactive` so it leaves normal layout flow; the active slot may be absolutely positioned within that bounded area. Never use `visibility: hidden` or zero opacity alone to hide a flex/grid child that should no longer reserve space.

Layout uses flex/grid inside `.stage` (safe margins: 140px horizontal, 80px top, 200px bottom). One dominant focus per beat. Budget persistent headers, active content, and gaps against the actual `.stage` width and height before adding a beat. `apply_timeline.py` generates `timeline.css` from the YAML `font`, `colors`, dimensions, and optional `margin`; scene CSS and SVG must use those variables (`var(--text)`, `var(--primary)`, `var(--stage-content-width)`, `var(--caption-clearance-bottom)`, etc.) rather than hard-coded canvas dimensions. `burn_subtitles.py` reads the same YAML font, caption-layout, `colors.text`, and `colors.background` values; do not set subtitle size, color, or vertical margin independently at the command line.

## Mapping from `video-script.md`

After the analysis and script are approved, fill `timeline.yaml` without changing story order:

1. Copy each scene's duration into a clip. Sum must be ≤ the approved duration limit. Leave leftover as holds, not as faster motion.
2. Derive the clip `purpose` from the scene's concept or conclusion → plain-language explanation. Copy its visual handoff's start/end states, evidence, and transition into the clip fields.
3. Turn each storyboard beat into a YAML beat. Keep a still `hold` after every reveal. Copy quoted 「」 text from the beat's `On screen` line onto the matching card or label; this is compact visual evidence, not a required duplication of the full subtitle. When a beat is a formula, copy its `tex` from the paper. When subtitles are enabled, copy each changed approved beat subtitle to the beat's `subtitle` field; an omitted `subtitle` extends the prior subtitle through that beat. Generate the SRT with `scripts/generate_captions.py`, never by hand.
4. Persistent objects keep the same id and color across clips.
5. Generate hosts, `timeline.css`, and formula bindings with `apply_timeline.py`. If generated assets and YAML disagree, YAML wins.

Do not write scene HTML until this YAML exists and the clip times sum correctly. Writing this YAML after script approval does not require a rendering runtime.

## Agent edit protocol

| User says | Verb | Default action |
|---|---|---|
| `1:23 把公式改成 …` | Content | Resolve `t`; edit that beat's `tex` / SVG / card copy |
| `1:23 再停 2 秒` | Hold | Increase that clip/beat `duration` by 2; do not retime tweens |
| `把 scene-03 改成 20 秒，动作不变` | Retime + hold | Set `duration: 20`; pad a `hold` beat |
| `1:23 的揭示再慢一点，拉到 6 秒` | Retime motion | Set the hit beat to 6s and scale its tweens |
| `scene-03 从 1:20 开始` | Move | Set `start: 80`; do not rewrite local `at` values |
| `在 1:23 切开` | Split | Split the clip at local time into two ids |
| `1:23 插入一张图，后面顺延` | Insert + ripple | New clip at `t`; shift later clips |
| `1:23 插入一张图，后面不动` | Insert + overlay | New clip on a free track |
| `字幕再高一点` | Restack | Change `z-index` / `track`; freeze timing |

Defaults: one variable per render; absolute targets; freeze everything not named; extra time is a hold; inserts do not ripple unless the user says `后面顺延`. After any time edit, regenerate hosts and snapshot the named time.

If `1:23` lands on a diagram and the formula is at `1:28`, report both times and ask which beat to edit.

## Allowed vs refused motion

Allowed: the approved storyboard's named handoffs (carry, transform, morph, zoom, split, merge, labeled chapter reset); one focus moving; dim previous context; draw an arrow to a named target; fade a card; count a number; highlight a symbol that is already on screen. Do not replace an approved morph or zoom with a fade-only substitute.

Refused as the default path: camera orbits, simultaneous unrelated motion, layout-property animation, wall-clock CSS animation, regenerating an approved scene to "improve" it.
