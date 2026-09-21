#!/usr/bin/env python3
import argparse
import html
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from timeline_lib import REQUIRED_COLORS, load_timeline

SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VENDOR_FROM = SKILL_ROOT / "runtime" / "vendor"


INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="{language}">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <link rel="stylesheet" href="./style.css">
  <link rel="stylesheet" href="./timeline.css">
  <script src="./vendor/gsap/gsap.min.js"></script>
</head>
<body>
  <div
    id="root"
    data-composition-id="paper-root"
    data-start="0"
    data-duration="{duration}"
    data-width="{width}"
    data-height="{height}"
  >
{hosts}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    window.__timelines["paper-root"] = gsap.timeline({{ paused: true }});
  </script>
</body>
</html>
"""

HOST_TEMPLATE = """    <div
      id="{clip_id}"
      class="clip"
      data-composition-id="{clip_id}"
      data-composition-src="{src}"
      data-start="{start}"
      data-duration="{duration}"
      data-track-index="{track}"
    ></div>"""

TOKEN_STYLESHEET = '<link rel="stylesheet" href="../timeline.css">'
FORMULA_RUNTIME_SCRIPT = '<script src="../formula_runtime.js"></script>'
FORMULA_RUNTIME_SOURCE = SKILL_ROOT / "assets" / "starter" / "formula_runtime.js"


def copy_vendor(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise FileNotFoundError(f"vendor directory not found: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def write_timeline_css(output: Path, data: dict) -> None:
    colors = data["colors"]
    margin = data.get("margin") or {}

    def _dim(val, default: str) -> str:
        if val is None:
            return default
        if isinstance(val, (int, float)):
            return f"{int(val)}px"
        return str(val)

    pad_x = _dim(margin.get("x"), "140px")
    pad_top = _dim(margin.get("top"), "80px")
    pad_bottom = _dim(margin.get("bottom"), "200px")
    frame_width = int(data["width"])
    frame_height = int(data["height"])
    stage_content_width = frame_width - 2 * int(margin.get("x", 140))

    extra_decls = "".join(
        f"  --{name}: {value};\n"
        for name, value in colors.items()
        if name not in REQUIRED_COLORS
    )
    css = f"""/* Generated from timeline.yaml. Do not edit by hand. */
:root {{
  --background: {colors["background"]};
  --bg: var(--background);
  --text: {colors["text"]};
  --primary: {colors["primary"]};
  --secondary: {colors["secondary"]};
  --accent: {colors["accent"]};
  --muted: {colors["muted"]};
{extra_decls}  --font: {json.dumps(data["font"], ensure_ascii=False)}, sans-serif;
  --frame-width: {frame_width}px;
  --frame-height: {frame_height}px;
  --frame-aspect-ratio: {frame_width} / {frame_height};
  --stage-padding-x: {pad_x};
  --stage-padding-top: {pad_top};
  --stage-padding-bottom: {pad_bottom};
  --stage-content-width: {stage_content_width}px;
  --caption-clearance-bottom: {pad_bottom};
  --caption-clearance-guard: 16px;
}}
"""
    (output / "timeline.css").write_text(css, encoding="utf-8")


def replace_formula_tex(text: str, beat_id: str, tex: str) -> tuple[str, bool]:
    pattern = re.compile(
        rf'<(?P<tag>[A-Za-z][\w:-]*)(?P<attrs>[^>]*\bid=(?P<quote>["\'])'
        rf"{re.escape(beat_id)}(?P=quote)[^>]*)>",
        re.IGNORECASE,
    )

    def replacement(match: re.Match) -> str:
        attributes = re.sub(
            r'\sdata-tex=(["\']).*?\1',
            "",
            match.group("attrs"),
            flags=re.DOTALL,
        )
        escaped_tex = html.escape(tex, quote=True)
        return f'<{match.group("tag")}{attributes} data-tex="{escaped_tex}">'

    updated, count = pattern.subn(replacement, text, count=1)
    return updated, count == 1


def prepare_scenes(animation_dir: Path, clips: list[dict]) -> None:
    missing_formula_nodes = []
    for clip in clips:
        target = animation_dir / clip["file"]
        text = target.read_text(encoding="utf-8")
        updated = text.replace(TOKEN_STYLESHEET, "")
        updated, stylesheet_count = re.subn(
            r'(<link\s+rel=["\']stylesheet["\']\s+href=["\'][^"\']*style\.css["\']\s*/?>)',
            rf"\1\n  {TOKEN_STYLESHEET}",
            updated,
            count=1,
            flags=re.IGNORECASE,
        )
        if not stylesheet_count:
            updated = updated.replace(
                "<template>",
                f"<template>\n  {TOKEN_STYLESHEET}",
                1,
            )
        if "data-tex=" in updated and FORMULA_RUNTIME_SCRIPT not in updated:
            katex_script = re.compile(
                r'(<script\s+src=["\'][^"\']*vendor/katex/katex\.min\.js["\']\s*></script>)',
                re.IGNORECASE,
            )
            updated, count = katex_script.subn(
                rf"\1\n  {FORMULA_RUNTIME_SCRIPT}",
                updated,
                count=1,
            )
            if not count:
                raise ValueError(
                    f"formula scene {target} must load ../vendor/katex/katex.min.js "
                    "before formula_runtime.js"
                )
        for beat in clip.get("beats") or []:
            if beat["kind"] != "formula":
                continue
            tex = beat.get("tex")
            if not isinstance(tex, str) or not tex:
                raise ValueError(
                    f"formula beat {beat['id']} in {clip['id']} needs a non-empty tex value"
                )
            updated, found = replace_formula_tex(updated, beat["id"], tex)
            if not found:
                missing_formula_nodes.append(f"{target}#{beat['id']}")
        if updated != text:
            target.write_text(updated, encoding="utf-8")
    if missing_formula_nodes:
        raise ValueError(
            "formula beat ids must match scene element ids:\n"
            + "\n".join(missing_formula_nodes)
        )


def missing_scene_files(animation_dir: Path, clips: list) -> list[str]:
    return [
        str(animation_dir / clip["file"])
        for clip in clips
        if not (animation_dir / clip["file"]).exists()
    ]


def main():
    parser = argparse.ArgumentParser(
        description="Generate HyperFrames index.html hosts from timeline.yaml"
    )
    parser.add_argument("--timeline", type=Path, required=True)
    parser.add_argument("--animation-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--vendor-from",
        type=Path,
        help="Runtime vendor directory containing katex/ and gsap/ "
        f"(default: {DEFAULT_VENDOR_FROM} when that directory exists)",
    )
    parser.add_argument("--title", default="paper-explainer")
    args = parser.parse_args()

    data = load_timeline(args.timeline)
    source_animation = args.animation_dir.expanduser().resolve()
    output = (args.output_dir or args.animation_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)

    if output != source_animation:
        style = source_animation / "style.css"
        if style.is_file():
            shutil.copy2(style, output / "style.css")
        scenes = source_animation / "scenes"
        if scenes.is_dir():
            destination = output / "scenes"
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(scenes, destination)
        vendor = source_animation / "vendor"
        if vendor.is_dir():
            destination = output / "vendor"
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(vendor, destination)

    if args.vendor_from:
        vendor_from = args.vendor_from.expanduser().resolve()
    elif DEFAULT_VENDOR_FROM.is_dir():
        vendor_from = DEFAULT_VENDOR_FROM
    else:
        vendor_from = None
    if vendor_from:
        copy_vendor(vendor_from / "katex", output / "vendor" / "katex")
        copy_vendor(vendor_from / "gsap", output / "vendor" / "gsap")
    if not FORMULA_RUNTIME_SOURCE.is_file():
        raise FileNotFoundError(f"formula runtime missing at {FORMULA_RUNTIME_SOURCE}")
    shutil.copy2(FORMULA_RUNTIME_SOURCE, output / "formula_runtime.js")

    missing = missing_scene_files(output, data["clips"])
    if missing:
        raise SystemExit("missing scene files:\n" + "\n".join(missing))
    write_timeline_css(output, data)
    prepare_scenes(output, data["clips"])

    hosts = "\n".join(
        HOST_TEMPLATE.format(
            clip_id=html.escape(clip["id"], quote=True),
            src=html.escape(clip["file"], quote=True),
            start=clip["start"],
            duration=clip["duration"],
            track=clip["track"],
        )
        for clip in data["clips"]
    )
    language = html.escape(str(data.get("language", "en")), quote=True)
    (output / "index.html").write_text(
        INDEX_TEMPLATE.format(
            language=language,
            title=html.escape(args.title),
            duration=data["duration"],
            width=data["width"],
            height=data["height"],
            hosts=hosts,
        ),
        encoding="utf-8",
    )
    print(output / "index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
