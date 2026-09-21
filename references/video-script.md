## Write the approval-ready script from the approved analysis

After the analysis is approved, create `output/<paper_short_name>/video-script.md` from the approved analysis. Copy the paper title and video-text language; select the candidate font and duration limit for this script. Follow the analysis's contributions, mechanisms, and results in their existing order, unfolding that chain once: do not add a scene that only restates the executive overview, and do not restage the Results section if those numbers already appear in the contribution scenes that produced them. Rewrite for public language and visual beats; do not select a separate theme, invent a tighter story, or strengthen a claim beyond the approved analysis.

On-screen actors are the analysis's own objects—the quantities, structures, and mechanisms it already explained. Do not replace them with a benchmark setting or everyday prop used only as a metaphor. An experiment appears as the protagonist only in the scene that reports that experiment.

First write the subtitle narration from the approved analysis. It is the explanatory spine of the video; do this before drafting any `On screen` content or scene choreography. Start with a short scene-purpose outline derived from the analysis, then write the complete subtitle track in clock order and split it into beats.

Rewrite subtitle text in public language:

- Use one idea per subtitle sentence. Keep each sentence short enough to read in its beat; do not lengthen a sentence to create flow.
- Choose the actual cue length. The ranges below are starting points, not quotas: do not pad, truncate, or split a sentence just to hit a number, and do not put a character limit in `timeline.yaml`.
  - Chinese: about 28–40 characters per cue.
  - English: about 14–30 words per cue.
  - Other languages: aim for the same visual width and the beat's reading time.
- Prefer one or two on-screen lines. Put a newline in the beat subtitle only when you want that break on screen. Caption generation copies the wording; a long single line may wrap when burned.
- Open the video, or an explicitly labeled chapter reset, with an analysis object in an active role. Later subtitles continue that chain with a shared subject or connective phrasing such as “it / so / therefore / next,” rather than restarting with a new technical noun.
- Explain what a technical thing does before naming it. Prefer “它会先挑出可能有用的内容” to a definition built around an unfamiliar noun.
- Present related metrics and comparisons together in a single beat (e.g. in a unified chart or card) rather than artificially fragmenting them across micro-beats. Avoid overloading a single subtitle sentence with both a dense definition and complex numbers, but do not force an artificial split when a concept and its metric or comparison naturally belong together.
- Replace paper-style abstractions and nominalisations with visible actions and consequences. Say what changed, who or what did it.
- For an unfamiliar concept that remains, use this sequence: **analysis object in a visible role → visible action → consequence or reason it matters → paper term as a secondary label**. The object is the thing the analysis already named, shown before its term, not a substitute protagonist.
- Expand an acronym once at first use; afterwards, use the paper term only when it is needed to follow the causal chain, and otherwise use its plain-language role.

Treat the subtitle track as one continuous narration. Before designing the storyboard, concatenate the subtitles in clock order and revise until they read as a short essay:

- Adjacent beats must continue the previous sentence's subject or causal chain. A demonstrative (“this / that / it / 这种 / 这”) is allowed only when its antecedent is in the previous subtitle, not only on screen or in a scene heading.
- The first subtitle of a scene must answer, continue, or explicitly turn from the last subtitle of the previous scene. Do not open a scene with a definition of the scene title.
- Consecutive subtitles must not restate the same fact. If the concatenated passage has a topic dump, an orphaned pronoun, or a hard cut, fix the beat subtitles. Do not write a separate narration.

Only after the subtitle track passes that reading, derive `On screen` from each beat's subtitle. The visual sequence must make the subtitle's claim visible through the paper's own objects, actions, comparisons, or measurements; it must not introduce a new factual claim, conclusion, or unexplained term. On-screen text is a compact aid—labels, numbers, terms, and short callouts—not a duplicate transcript of the subtitle. Keep ordinary text cards to one sentence.

The visual sequence must still make sense without subtitles. Use comparisons, highlights, arrows, labels, and concise text cards to carry the reasoning. This is a quality requirement for the visual explanation, not permission to change the narration or invent a separate visual story.

Create `video-script.md` with:

- Proposed title, duration limit with its selection rationale, video-text language, and candidate font.
- A **Subtitle narration** section before the storyboard (title it **字幕通读** when the video-text language is Chinese). It is the approved explanatory source: concatenate every beat subtitle in clock order, grouped by scene. This block must be that exact beat-level narration, not a rewrite.
- The scene-by-scene storyboard derived from the approved subtitle narration.
- A **Technical note** recording the candidate font and that Phase 3 must verify it before scene HTML is written. If Phase 3 substitutes a font, update this note.

For each scene, write:

- **Concept or conclusion → plain-language explanation:** name the one concept, visible change, or result this scene explains, followed by one sentence the viewer should remember.
- **Duration and visual handoff:** the duration; what enters from the previous scene; the initial composition; the final visual state; and the visible transition into the next scene. Document how objects, colors, labels, and camera context carry across the boundary.
- **Beats:** use the compact beat format below. Copy the exact approved subtitle into the matching beat, then describe the screen content that explains that subtitle. On-screen copy and subtitles appear only in the beat where they change. Every planned term, acronym, symbol, and formula must have its visual role and plain-language wording in its introducing beat.

For every beat, use this bullet format:

```text
- 0:00–0:06 — beat name
  - Subtitle: exact public-language wording, if it changes.
  - On screen: the paper object, action, comparison, or measurement that makes this subtitle claim visible; then composition, position, hierarchy, persistent or hidden objects, reveal order, movement, emphasis, and hold. Quote the exact wording of every title card, label, and new numeral in 「」. Do not repeat the full subtitle as a card unless the subtitle itself is the item under analysis.
```

Do not add a source-basis, glossary, or citation line to a beat. Ground claims in the approved analysis. When a beat shows a formula, copy its TeX from the paper even if the analysis explained that relation in words. Teach a first-use term on screen as a secondary label after its visible role, and in the subtitle in public language.

Do not write generic beat instructions such as “show the mechanism” or “redraw the figure.” Describe what fills the frame, what enters or changes first, where the viewer should look, and what visual fact supports the accompanying subtitle. A transition must name a concrete handoff action such as carrying, transforming, zooming, splitting, or an explicitly labeled chapter reset.

Before requesting approval, run a subtitle-to-screen mapping check:

- Every non-hold beat with a subtitle has one clear visual proof: an object/action, comparison, or measurement that supports that sentence.
- Every material on-screen claim is present in that beat's subtitle or is a direct label for the visual evidence; otherwise revise the subtitle first.
- The screen does not repeat a whole subtitle sentence merely because it is available as text.

The selected duration is the maximum budget. Sum scene timings before asking for approval and leave time for transitions and the final insight. If the story does not fit, reduce scope or propose a longer duration; do not silently compress it.
