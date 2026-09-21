#!/usr/bin/env python3
"""Burn UTF-8 SRT subtitles into a silent MP4."""
from __future__ import annotations

import argparse
import os
import subprocess
import uuid
from pathlib import Path

from ffmpeg_tools import resolve_ffmpeg
from media_validation import probe_media, validate_video
from timeline_lib import DEFAULT_MARGIN_X, load_timeline


def hex_rgb(value: str) -> tuple[int, int, int] | None:
    text = value.strip().removeprefix("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    elif len(text) == 8:
        text = text[:6]
    if len(text) != 6 or any(ch not in "0123456789abcdefABCDEF" for ch in text):
        return None
    return int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)


def ass_color(rgb: tuple[int, int, int]) -> str:
    red, green, blue = rgb
    return f"&H00{blue:02X}{green:02X}{red:02X}"


def filter_escape(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(":", r"\:")
        .replace("'", r"\'")
        .replace(",", r"\,")
        .replace("[", r"\[")
        .replace("]", r"\]")
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Burn an SRT file into an MP4 as always-visible subtitles"
    )
    parser.add_argument("--timeline", required=True, type=Path)
    parser.add_argument("--max-duration", required=True, type=float)
    parser.add_argument("video", type=Path)
    parser.add_argument("subtitles", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    if args.max_duration <= 0:
        parser.error("--max-duration must be positive")
    ffmpeg = resolve_ffmpeg(require_subtitles=True)
    if not ffmpeg:
        parser.error(
            "FFmpeg lacks the subtitles filter. Install an FFmpeg build with libass support."
        )

    timeline = load_timeline(args.timeline)
    captions = timeline.get("captions")
    if not isinstance(captions, dict) or not captions.get("enabled"):
        parser.error("timeline captions.enabled must be true for burned subtitles")
    layout = captions.get("layout")
    if not isinstance(layout, dict):
        parser.error("timeline captions requires a layout mapping")
    font_size = layout["font_size"]
    margin_bottom = layout["margin_bottom"]
    outline = layout["outline"]
    video = args.video.expanduser().resolve()
    subtitles = args.subtitles.expanduser().resolve()
    output = args.output.expanduser().resolve()
    for path in (video, subtitles):
        if not path.is_file():
            raise FileNotFoundError(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(
        f".{output.stem}.{uuid.uuid4().hex}.pending{output.suffix}"
    )

    width = int(timeline["width"])
    height = int(timeline["height"])
    side_margin = int((timeline.get("margin") or {}).get("x", DEFAULT_MARGIN_X))
    colors = timeline["colors"]
    primary = hex_rgb(colors["text"])
    outline_color = hex_rgb(colors["background"])
    color_style = ""
    if primary is not None and outline_color is not None:
        color_style = (
            f",PrimaryColour={ass_color(primary)},"
            f"OutlineColour={ass_color(outline_color)}"
        )
    subtitle_filter = (
        f"subtitles=filename='{filter_escape(str(subtitles))}':charenc=UTF-8:"
        f"original_size={width}x{height}:"
        f"force_style='FontName={filter_escape(timeline['font'])},"
        f"FontSize={font_size},Alignment=2,WrapStyle=0,"
        f"MarginL={side_margin},MarginR={side_margin},MarginV={margin_bottom},"
        f"Outline={outline},Shadow=0{color_style},"
        f"PlayResX={width},PlayResY={height}'"
    )
    try:
        subprocess.run(
            [
                str(ffmpeg),
                "-y",
                "-v",
                "error",
                "-i",
                str(video),
                "-map",
                "0:v:0",
                "-vf",
                subtitle_filter,
                "-c:v",
                "libx264",
                "-crf",
                "18",
                "-preset",
                "medium",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                "-an",
                "-sn",
                "-dn",
                str(temporary),
            ],
            check=True,
        )
        failures = validate_video(probe_media(temporary), args.max_duration)
        if failures:
            raise RuntimeError(
                "burned video failed its pre-replacement media check: "
                + "; ".join(failures)
            )
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
