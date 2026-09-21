#!/usr/bin/env python3
"""Generate the approved SRT from subtitle fields in timeline.yaml."""
import argparse
import sys
from pathlib import Path

from timeline_lib import load_timeline


def clock(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    whole_seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{whole_seconds:02},{milliseconds:03}"


def cue_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    if not cleaned:
        raise ValueError("subtitle cannot be empty")
    return cleaned


def warn_if_too_tall(text: str, max_lines: int) -> None:
    line_count = len(text.splitlines())
    if line_count > max_lines:
        print(
            f"warning: subtitle needs {line_count} lines, exceeding "
            f"captions.layout.max_lines={max_lines}: {text}",
            file=sys.stderr,
        )


def build_cues(timeline: dict) -> list[tuple[float, float, str]]:
    captions = timeline.get("captions")
    if not isinstance(captions, dict) or not captions.get("enabled"):
        raise ValueError("timeline captions.enabled must be true to generate captions")
    max_lines = captions["layout"]["max_lines"]
    cues: list[tuple[float, float, str]] = []
    for clip in sorted(timeline["clips"], key=lambda item: (item["start"], item["track"])):
        active_text: str | None = None
        active_start: float | None = None
        for beat in sorted(clip.get("beats") or [], key=lambda item: item["at"]):
            if "subtitle" not in beat:
                continue
            absolute = clip["start"] + beat["at"]
            if active_text is not None and active_start is not None and absolute > active_start:
                cues.append((active_start, absolute, active_text))
            text = cue_text(beat["subtitle"])
            warn_if_too_tall(text, max_lines)
            active_text = text
            active_start = absolute
        clip_end = clip["start"] + clip["duration"]
        if active_text is not None and active_start is not None and clip_end > active_start:
            cues.append((active_start, clip_end, active_text))
    if not cues:
        raise ValueError("timeline contains no beat subtitle fields")
    return cues


def srt_content(cues: list[tuple[float, float, str]]) -> str:
    content = "\n\n".join(
        f"{index}\n{clock(start)} --> {clock(end)}\n{text}"
        for index, (start, end, text) in enumerate(cues, start=1)
    )
    return f"{content}\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate UTF-8 SRT captions from timeline beat subtitles"
    )
    parser.add_argument("--timeline", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    cues = build_cues(load_timeline(args.timeline))
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(srt_content(cues), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
