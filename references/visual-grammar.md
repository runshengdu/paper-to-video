# Visual grammar

Use these principles when turning the approved script into HyperFrames scenes.

## Build understanding spatially

- Start concrete and move toward abstraction.
- For every new concept, show the analysis object in an active role first, state its plain-language role second, then reveal the paper term or acronym as a secondary label. Do not substitute a benchmark setting or everyday prop as the protagonist.
- Keep an object on screen when its meaning continues; replace it only when the idea changes.
- Connect geometric, numeric, and symbolic views of the same quantity.
- Reveal complexity progressively. Dim or hide irrelevant objects.
- Let the ending state of a scene motivate the next one. Preserve shared object ids and colors across clips.

## Maintain semantic continuity

Assign colors by meaning in `timeline.yaml` before writing HTML. Invent one palette for this paper. Dark, light, and tinted canvases are all allowed; do not default to `#000000`, and do not copy the starter hex values. `colors` must include `background`, `text`, `primary`, `secondary`, `accent`, and `muted`. Pair `text` with `background` so body copy stays readable. `apply_timeline.py` generates `timeline.css`; reference its CSS variables in scene CSS and SVG (`var(--text)`, `var(--primary)`, `var(--accent)`, extra named colors, etc.) rather than hard-coding semantic colors. A variable, category, or hypothesis keeps the same CSS color across scenes. Reserve the accent color for attention or a new insight; prefer two semantic colors plus neutrals in an ordinary scene. Extra named colors are for additional categories that would otherwise collide in the required slots.

Do not encode a meaningful distinction by color alone. Combine color with position, shape, label, line style, or motion.

Do not show dense implementation notation, variables, or unexplained abbreviations as the dominant visual. Replace them with a role label such as “select,” “share,” or “rebuild” unless the notation is essential and its meaning has already been demonstrated. A formula may appear only after an animation has made its relationship visible; it must clarify one essential relationship, not inventory the paper's notation. Copy that formula's TeX from the paper. To reveal a formula in stages, give each stage its own formula node and `tex`; do not render KaTeX from scene scripts.

Use contrast against the chosen canvas, and opacity, to establish hierarchy. Body copy, titles, and default labels use `var(--text)`.

## Layout rules

- Keep essential content inside `.stage` and outside the caption clearance zone configured in `timeline.yaml`; `--caption-clearance-bottom` is a visual exclusion zone, not extra space for content. See the [timeline layout contract](clip-timeline.md#timelineyaml-schema).
- Use flex or grid. Do not scatter absolute `top`/`left` coordinates as the primary layout.
- At 1080p, titles ~56–72px, body ~36–48px, labels at least 30px.
- Keep text away from axes, graph lines, and moving strokes.
- Never place essential content, persistent cards, diagrams, or focal objects in the bottom subtitle clearance zone (bottom 200px by default).
- Before implementing a scene, budget the available stage height after the top and bottom margins for the persistent header, active beat, and gaps. If they do not fit, replace, collapse, or reduce prior visual state; do not let flex shrink children until their contents overlap or overflow.
- Compose against `--stage-content-width` and `--frame-aspect-ratio`, not just the centered middle of the canvas. At 16:9, the dominant visual group should normally span about 60–85% of the available stage width; leave more empty space only when it visibly establishes hierarchy, comparison, scale, or motion direction.
- Prefer horizontal composition for comparisons, sequences, matrices, and pipelines. If a deliberately narrow focal object is centered, use meaningful left/right context—inputs and outputs, before and after states, labels, axes, or a supporting diagram—instead of unused symmetric margins.
- Do not make “fill every pixel” the goal. The scene must preserve a readable focus and intentional negative space, while avoiding a generic narrow card floating in the center of a 16:9 frame.
- Follow the [scene-state layout contract](clip-timeline.md#scene-html-contract) for mutually exclusive beats; review their transformed bounds as part of the active composition.
- Treat transformed bounds as visual bounds. A `scale` or `y` tween can collide with another object or the caption zone even when its original flex/grid allocation did not.
- One dominant visual focus per beat.
- Keep ordinary text compact enough to read without pausing.
- Treat the storyboard's composition instructions as implementation requirements: preserve the stated hierarchy, positions, persistent objects, and reveal order. Do not substitute a generic chart or text card for a specified visual explanation.

## Motion rules

- Follow the [timeline motion contract](clip-timeline.md#scene-html-contract). Implement approved storyboard handoffs, including transform, morph, and zoom; do not replace them with a fade-only substitute.
- Avoid simultaneous unrelated motion. The viewer should know where to look.
- Add a short `hold` beat after a reveal, comparison, or completed derivation.
- HyperFrames owns clip visibility. Do not hide, fade, or otherwise animate a whole scene's `#root` or `.clip` host in GSAP or CSS; animate a descendant group instead.

## Scene handoffs

Each clip boundary needs a visual contract in the script and timeline:

1. Identify the object, color, label, and camera context carried from the prior clip.
2. Recreate the prior clip's final visual state at the next clip's start before beginning new motion.
3. Use a visible handoff action—carry, transform, zoom, split, merge, or follow—to introduce the next idea.
4. Use a hard cut only for an explicitly labeled chapter reset; do not rely on a prose transition note to explain a discontinuity.

When isolated scene HTML prevents literal DOM reuse, match the carried object's geometry, color, label, and position closely enough that paired boundary snapshots read as one continuous shot.

## Redrawing paper figures

Reconstruct charts and diagrams from the underlying values when available. Preserve axes, units, ordering, uncertainty, and meaningful baselines. Replace dense legends with direct labels and introduce series one at a time.

For conceptual figures, rebuild the causal or procedural structure with SVG groups and arrows. Give every highlightable part a stable id. Do not trace low-resolution screenshots unless the paper's exact image is itself the subject.
