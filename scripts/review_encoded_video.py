#!/usr/bin/env python3
"""Decode deterministic clip samples from an MP4 and fail on black video."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from ffmpeg_tools import resolve_ffmpeg
from timeline_lib import load_timeline, snap

BLACK_YAVG = 17.0


def sample_times(clip: dict, fps: float) -> list[tuple[str, float]]:
    start = float(clip["start"])
    duration = float(clip["duration"])
    frame = 1 / fps
    return [
        ("start", snap(start + frame, fps)),
        ("middle", snap(start + duration / 2, fps)),
        ("end", snap(start + duration - frame, fps)),
    ]


def y_average(ffmpeg: Path, video: Path, seconds: float) -> float:
    command = [
        str(ffmpeg),
        "-v",
        "error",
        "-ss",
        f"{seconds:.6f}",
        "-i",
        str(video),
        "-frames:v",
        "1",
        "-vf",
        "crop=iw:ih*0.78:0:0,signalstats,metadata=print:file=-",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"ffmpeg failed at {seconds}s")
    match = re.search(r"lavfi\.signalstats\.YAVG=([0-9.]+)", result.stdout)
    if not match:
        raise RuntimeError(f"ffmpeg did not emit signalstats YAVG at {seconds}s")
    return float(match.group(1))


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
    parser.add_argument(
        "--min-yavg",
        type=float,
        default=BLACK_YAVG,
        help=f"minimum top-78%% luma average; default {BLACK_YAVG}",
    )
    args = parser.parse_args()
    if args.min_yavg <= 0:
        parser.error("--min-yavg must be positive")

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
    warnings: list[str] = []
    failures: list[str] = []
    for clip_index, clip in enumerate(timeline["clips"], start=1):
        dark_phases: list[str] = []
        for phase, seconds in sample_times(clip, fps):
            frame_path = output / f"encoded-{clip_index:02}-{clip['id']}-{phase}.png"
            extract_png(ffmpeg, video, seconds, frame_path)
            average = y_average(ffmpeg, video, seconds)
            sample = {
                "clip": clip["id"],
                "phase": phase,
                "seconds": seconds,
                "frame": str(frame_path),
                "top_78_percent_yavg": average,
            }
            samples.append(sample)
            if average < args.min_yavg:
                message = (
                    f"{clip['id']} {phase} at {seconds:.3f}s is near-black "
                    f"(YAVG {average:.2f} < {args.min_yavg:.2f})"
                )
                warnings.append(message)
                dark_phases.append(phase)
        if len(dark_phases) == 3:
            failures.append(
                f"{clip['id']} is near-black at start, middle, and end; "
                "encoded clip visibility likely failed"
            )

    report = {
        "video": str(video),
        "threshold_top_78_percent_yavg": args.min_yavg,
        "samples": samples,
        "passed": not failures,
        "warnings": warnings,
        "failures": failures,
    }
    report_path = output / "encoded-review.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if failures:
        print(f"Encoded review failed; see {report_path}", file=sys.stderr)
        return 2
    if warnings:
        print(
            f"Encoded review passed with near-black warnings; see {report_path}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
