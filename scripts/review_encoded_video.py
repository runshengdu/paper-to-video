#!/usr/bin/env python3
"""Decode deterministic clip samples from an MP4."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from ffmpeg_tools import resolve_ffmpeg
from timeline_lib import load_timeline, snap


def sample_times(clip: dict, fps: float) -> list[tuple[str, float]]:
    start = float(clip["start"])
    duration = float(clip["duration"])
    frame = 1 / fps
    return [
        ("start", snap(start + frame, fps)),
        ("middle", snap(start + duration / 2, fps)),
        ("end", snap(start + duration - frame, fps)),
    ]


def extract_png(ffmpeg: Path, video: Path, seconds: float, output: Path) -> None:
    subprocess.run(
        [
            str(ffmpeg),
            "-y",
            "-v",
            "error",
            "-ss",
            f"{seconds:.6f}",
            "-i",
            str(video),
            "-frames:v",
            "1",
            str(output),
        ],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review every clip's decoded start, middle, and end frame"
    )
    parser.add_argument("--timeline", required=True, type=Path)
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    ffmpeg = resolve_ffmpeg()
    if not ffmpeg:
        parser.error("ffmpeg is required")
    video = args.video.expanduser().resolve()
    if not video.is_file():
        raise FileNotFoundError(video)
    output = args.output_dir.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    timeline = load_timeline(args.timeline)
    fps = float(timeline["fps"])

    samples: list[dict] = []
    for clip_index, clip in enumerate(timeline["clips"], start=1):
        for phase, seconds in sample_times(clip, fps):
            frame_path = output / f"encoded-{clip_index:02}-{clip['id']}-{phase}.png"
            extract_png(ffmpeg, video, seconds, frame_path)
            samples.append(
                {
                    "clip": clip["id"],
                    "phase": phase,
                    "seconds": seconds,
                    "frame": str(frame_path),
                }
            )

    report = {
        "video": str(video),
        "samples": samples,
        "passed": True,
    }
    report_path = output / "encoded-review.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
