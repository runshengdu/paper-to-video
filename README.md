<p>
  <a href="README.md"><img alt="中文" src="https://img.shields.io/badge/%E4%B8%AD%E6%96%87-111111?style=for-the-badge"></a>
  <a href="README.en.md"><img alt="English" src="https://img.shields.io/badge/English-ededed?style=for-the-badge"></a>
</p>

# Paper to Video

把一篇研究论文做成面向大众的**无声讲解视频**：声明式时间轴 + HTML/SVG 画面，再由 HyperFrames 逐帧渲染成 1920×1080、30fps 的 MP4。

成品没有音轨。默认把字幕烧进画面，方便静音观看。

## 样片

下面两支视频来自 `media/`，都是用本 skill 从论文生成的讲解片。

### Transformers are RNNs

线性注意力如何把二次方的自注意力改写成线性计算，并在因果生成时等价于 RNN。时长 3:00。

<video src="media/transformers-are-rnns.mp4" controls muted playsinline width="100%"></video>

[下载 MP4](media/transformers-are-rnns.mp4)

### Scaling Automatic Research Agents

自动科研 agent 如何规模化。时长 3:15。

<video src="media/scaling-automatic-research-agents.mp4" controls muted playsinline width="100%"></video>

[下载 MP4](media/scaling-automatic-research-agents.mp4)

## 它怎么工作

这不是剪辑素材，也不是录屏。Agent 写的是一份**可以按时钟寻址的网页动画**，渲染器再按时间逐帧拍照。

| 文件 | 职责 |
|---|---|
| `timeline.yaml` | 全局时钟、语义颜色、字体、公式 TeX、字幕文案 |
| `animation/scenes/*.html` | 这一场的 SVG/HTML 画面，以及一段暂停的 GSAP 时间轴 |
| `animation/index.html` | 由 YAML 生成的根合成：每个 clip 带上 `data-start` / `data-duration` |

场景时间轴从本地 `0` 起算。整片第 `1:23` 落到哪一场，就是 `clip.start + 本地时间`。GSAP 一律 `paused: true`，禁止 `Date.now()` 和 `requestAnimationFrame`。HyperFrames 用 Chromium seek 到某一秒、截图，FFmpeg 再收成 MP4。

所以改时长不必重写动画，改图不必重排整片时钟；也可以直接说「1:23 把公式改成 …」。

## 制作流程

两道明确的批准门。反馈或「再改一改」都不算批准。

1. **论文 → 技术分析**  
   读完整篇论文，写成大众能跟上的 `paper-analysis.md`。人批准后冻结。
2. **分析 → 分镜与字幕**  
   先写出完整字幕通读，再从字幕推导画面证据，写成 `video-script.md`。人批准后冻结。默认 2–5 分钟，按论文范围选时长。
3. **分镜 → 成片**  
   把分镜落到 `timeline.yaml` 和场景 HTML，检查字体与渲染环境，snapshot 校对，先出 draft MP4，再出高质量无声片，最后烧字幕并校验后发布。

成片之后，按时钟改某一秒是编辑，不是重新从 Phase 1 开始。

## 产出

论文相关文件都写在当前工作目录的 `output/<paper_short_name>/`：

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

共享运行时在 skill 的 `runtime/`（HyperFrames、GSAP、KaTeX），不按论文复制一份。

最终 MP4：16:9、1920×1080、30fps、无音轨。启用字幕时字幕烧进画面，文件里不保留独立字幕轨。

## 使用

把这篇论文交给使用本 skill 的 agent，并指定画面/字幕语言（例如简体中文）。Agent 会先停在技术分析，再停在分镜与字幕，两步都得到明确批准后才渲染。

环境需要 `python3`、`node`、`npm`、`ffmpeg`、`ffprobe`。运行时不齐时，agent 会列出缺项并等到你要求后再安装。

更细的时间轴约定、视觉语法、渲染步骤和质检门槛见 `references/`。
