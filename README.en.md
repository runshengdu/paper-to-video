<p>
  <a href="README.md"><img alt="中文" src="https://img.shields.io/badge/%E4%B8%AD%E6%96%87-ededed?style=for-the-badge"></a>
  <a href="README.en.md"><img alt="English" src="https://img.shields.io/badge/English-111111?style=for-the-badge"></a>
</p>

# Paper to Video

Turn a research paper into a **silent explainer for a general audience**: a declarative timeline plus HTML/SVG frames, rendered by HyperFrames into a 1920×1080, 30 fps MP4.

The finished file has no audio track. Subtitles are burned into the picture by default so the video can be watched on mute.

## Samples

The two videos below live in `media/`. Both were generated from papers with this skill.

### Transformers are RNNs

How linear attention rewrites quadratic self-attention as linear computation, and is equivalent to an RNN during causal generation. Runtime 3:00.

<video src="media/transformers-are-rnns.mp4" controls muted playsinline width="100%"></video>

[Download MP4](media/transformers-are-rnns.mp4)

### Scaling Automatic Research Agents

How automatic research agents can scale. Runtime 3:15.

<video src="media/scaling-automatic-research-agents.mp4" controls muted playsinline width="100%"></video>

[Download MP4](media/scaling-automatic-research-agents.mp4)

## How it works

This is not edited footage, and it is not a screen recording. The agent writes a **clock-addressable web animation**; the renderer then photographs it frame by frame.

| File | Role |
|---|---|
| `timeline.yaml` | Global clock, semantic colors, font, formula TeX, subtitle copy |
| `animation/scenes/*.html` | This scene's SVG/HTML graphics, plus a paused GSAP timeline |
| `animation/index.html` | Root composition generated from YAML; each clip has `data-start` / `data-duration` |

Scene timelines start at local `0`. Second `1:23` of the film lands in whichever clip satisfies `clip.start + local time`. GSAP is always `paused: true`; `Date.now()` and `requestAnimationFrame` are forbidden. HyperFrames seeks Chromium to a given second, takes a screenshot, and FFmpeg packs the frames into an MP4.

So changing duration does not require rewriting the animation, and changing graphics does not require relaying the whole clock. You can also say “at 1:23 change the formula to …”.

## Production process

Two explicit approval gates. Feedback or “tweak it a bit” is not approval.

1. **Paper → technical analysis**  
   Read the full paper and write a `paper-analysis.md` a general audience can follow. Freeze it after human approval.
2. **Analysis → storyboard and subtitles**  
   Write the complete subtitle narration first, then derive on-screen evidence from that narration, and save both in `video-script.md`. Freeze it after human approval. Default length is 2–5 minutes, chosen from the paper's scope.
3. **Storyboard → finished film**  
   Land the storyboard in `timeline.yaml` and scene HTML, check fonts and the render environment, review snapshots, render a draft MP4, then a high-quality silent film, then burn subtitles and publish after verification.

Once a full video exists, changing a specific second by clock time is an edit, not a restart from Phase 1.

## Output

Paper-specific files go in `output/<paper_short_name>/` under the current working directory:

```text
output/<paper_short_name>/
├── paper-analysis.md
├── video-script.md
├── timeline.yaml
├── animation/
│   ├── index.html
│   ├── style.css
│   ├── timeline.css
│   └── scenes/
│       └── scene_*.html
├── captions.<language>.srt
└── <paper_short_name>.mp4
```

The shared runtime lives in this skill's `runtime/` (HyperFrames, GSAP, KaTeX). It is not copied per paper.

Final MP4: 16:9, 1920×1080, 30 fps, no audio track. When subtitles are enabled they are burned into the picture; the file does not keep a separate subtitle stream.

## Usage

Give the paper to an agent using this skill, and specify the on-screen / subtitle language (for example Simplified Chinese). The agent stops first at the technical analysis, then at the storyboard and subtitles, and renders only after both are explicitly approved.

The environment needs `python3`, `node`, `npm`, `ffmpeg`, and `ffprobe`. If the runtime is incomplete, the agent lists what is missing and waits until you ask it to install.

See `references/` for timeline conventions, visual grammar, render steps, and quality-control gates.
