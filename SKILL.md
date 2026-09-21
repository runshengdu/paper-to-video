---
name: paper-to-video
description: Turn a research paper into a silent, general-audience explainer on a declarative HyperFrames video.
metadata:
  version: 1.0.0
  openclaw:
    requires:
      bins:
        - python3
        - node
        - npm
        - ffmpeg
        - ffprobe
---

# Paper to Timeline Video

Create a silent visual explanation from one research paper. Author it as a clock-addressable HyperFrames composition: `timeline.yaml` owns global time, semantic colors, the font, and formula TeX; scene HTML owns graphics and local motion. Unless the user requests otherwise, select a duration between 2 and 5 minutes based on the approved scope; do not impose a shorter global limit.

Keep every paper-specific artifact in `output/<paper_short_name>/` under the current working directory, including when that directory is this skill. Derive `paper_short_name` from the paper title, lowercase it, replace unsafe characters with hyphens, and keep it short. If that directory already belongs to another paper, ask the user for a different name or append an unambiguous suffix. Do not write generated artifacts into `references/`, `scripts/`, or `assets/`. The shared HyperFrames runtime lives at `runtime/` under this skill.

## Required interaction

Before Phase 2, obtain the video-text language if the user has not already provided it. Do not ask the user to choose subtitles or duration unless they state an additional requirement:

1. Generate subtitles by default because the video has no audio. Use the video-text language for subtitles unless the user requests another subtitle language or explicitly declines subtitles. Cue length is the agent's choice from the language suggestions in [references/video-script.md](references/video-script.md).

During Phase 2, choose and record a candidate font that supports the selected video-text language. Phase 3 must verify that font before scene HTML is written; if it is unavailable, choose an equivalent supported font and update the script's technical note.

Audio is always excluded. Titles, formula labels, axis labels, and short explanatory callouts are visual content rather than subtitles.

## Approval boundaries

This skill has two explicit approval gates:

1. The user approves the paper analysis.
2. The user approves the detailed scene storyboard and the concatenated subtitle narration.

Do not write `video-script.md` before the user approves the analysis. Do not install a rendering environment, write `timeline.yaml`, write scene HTML, or render video before the user approves the script. After script approval, the agent may write `timeline.yaml` before a rendering runtime is available, but may not write scene HTML or render until the selected font and runtime pass the environment check. Feedback or a request to revise is not approval.

After a full video exists, clock-time notes such as `1:23 把公式改成 …` are edits, not a new Phase 1. Follow [references/clip-timeline.md](references/clip-timeline.md).

## Phase 1: paper to approved technical analysis

Read [references/paper-analysis.md](references/paper-analysis.md), create `paper-analysis.md`, then ask the user to approve it or request changes and stop. That reference owns analysis structure, accessible technical explanation, and factual boundaries.

## Phase 2: approved analysis to approved script

After explicit analysis approval, read [references/video-script.md](references/video-script.md) and the approved analysis. Create `video-script.md` by first deriving its complete subtitle narration from the analysis, then deriving the storyboard's on-screen evidence from that narration. Present both for approval and stop. That reference owns duration, public-language writing, visual handoffs, and subtitle continuity. The approved duration limit governs the timeline and final media check.

## Phase 3: approved script to full video

After explicit script approval:

1. Read [references/clip-timeline.md](references/clip-timeline.md), [references/visual-grammar.md](references/visual-grammar.md), [references/hyperframes-workflow.md](references/hyperframes-workflow.md), and [references/quality-control.md](references/quality-control.md).
2. Follow the timeline contract to write `timeline.yaml` from the approved script, including its caption fields when subtitles are enabled. Choose a paper-specific `colors` palette; the starter hex values are schema filler, not a house look. This non-rendering planning work does not need a runtime.
3. Follow the runtime procedure to check the environment. If it is incomplete, report every missing component and stop until the user explicitly asks for setup help. After the font and runtime pass, generate assets and implement scenes. Keep end states, object ids, geometry, colors, and labels continuous across clips.
4. Follow the visual grammar and the mandatory quality-control review gate: snapshot-review scenes, then render and inspect a complete draft MP4 before rendering a pending video; inspect captioned frames before publish; then atomically publish. Do not omit an approved scene; if the loop reaches a blocker, report it.

## Time-addressable edits

Follow the time-edit protocol in [references/clip-timeline.md](references/clip-timeline.md): resolve the clock time before touching files, edit only the hit target, then regenerate hosts and snapshot the named time. Use `scripts/resolve_time.py` when clips overlap, the time is on a boundary, or the hit is ambiguous.

## Output contract

```text
runtime/                          # shared HyperFrames, GSAP, KaTeX; not a paper artifact
output/<paper_short_name>/
├── paper-analysis.md
├── video-script.md
├── timeline.yaml
├── animation/
│   ├── index.html
│   ├── style.css
│   ├── timeline.css
│   ├── vendor/
│   └── scenes/
│       └── scene_*.html
├── review/
├── captions.<language>.srt       # unless subtitles were declined
└── <paper_short_name>.mp4
```

The final MP4 must be 16:9, 1920x1080, 30 fps, within the user-approved duration, and contain no audio stream. When subtitles are enabled, they must be burned into the image; the MP4 must not contain a subtitle stream. It must contain no subtitle stream when subtitles were declined. The output directory must not retain a silent-intermediate MP4.

## Ground rules

- Base factual claims on the paper. Supplemental sources may explain prerequisites but may not change or overstate the paper's conclusions. Formula TeX in the timeline may be copied from the paper even when the analysis explained the same relation in words.
- Follow the approved technical analysis and storyboard without changing scientific claim strength. On-screen objects are the analysis's quantities, structures, and mechanisms, not a substitute protagonist from a benchmark or everyday analogy.
- Use deterministic scripts for environment checks, timeline application, time resolution, and output verification. Use agent judgment for explanation design and visual review of snapshot PNGs.
