#!/usr/bin/env python3
"""Print deterministic snapshot times for the mandatory visual review."""
from __future__ import annotations

import argparse
from pathlib import Path

from generate_captions import build_cues
from timeline_lib import load_timeline, snap


def format_times(times: set[float], fps: float) -> str:
    values = sorted(snap(time, fps) for time in times)
    return ",".join(f"{time:.3f}".rstrip("0").rstrip(".") for time in values)


def snapshot_times(timeline: dict) -> set[float]:
    fps = float(timeline["fps"])
    duration = float(timeline["duration"])
    points: set[float] = set()
    clips = sorted(timeline["clips"], key=lambda clip: (clip["start"], clip["track"]))

    for clip in clips:
        clip_start = float(clip["start"])
        clip_end = clip_start + float(clip["duration"])
        points.update((clip_start, clip_end))
        for beat in clip.get("beats") or []:
            beat_start = clip_start + float(beat["at"])
            beat_end = beat_start + float(beat["duration"])
            points.add(beat_start)
            if beat["kind"] != "hold":
                points.add((beat_start + beat_end) / 2)

    ends = [float(clip["start"]) + float(clip["duration"]) for clip in clips]
    tolerance = 0.5 / fps
    boundaries = {
        float(clip["start"])
        for clip in clips
        if clip["start"] > 0
        and any(abs(end - float(clip["start"])) <= tolerance for end in ends)
    }
    for boundary in boundaries:
        points.add(max(0.0, boundary - 0.75))
        points.add(min(duration, boundary + 0.75))
    return {snap(point, fps) for point in points}


def two_line_caption_times(timeline: dict) -> set[float]:
    fps = float(timeline["fps"])
    captions = timeline.get("captions")
    if not isinstance(captions, dict) or not captions.get("enabled"):
        return set()
    return {
        snap((start + end) / 2, fps)
        for start, end, text in build_cues(timeline)
        if len(text.splitlines()) > 1
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print comma-separated HyperFrames review times from timeline.yaml"
    )
    parser.add_argument("--timeline", required=True, type=Path)
    parser.add_argument(
        "--two-line-captions",
        action="store_true",
        help="print only midpoints for subtitles that occupy two or more lines",
    )
    args = parser.parse_args()

    timeline = load_timeline(args.timeline)
    fps = float(timeline["fps"])
    times = (
        two_line_caption_times(timeline)
        if args.two_line_captions
        else snapshot_times(timeline)
    )
    print(format_times(times, fps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
