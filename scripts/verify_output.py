#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

from generate_captions import build_cues, srt_content
from media_validation import media_report, probe_media, validate_video
from timeline_lib import load_timeline


def main():
    parser = argparse.ArgumentParser(description="Verify final paper video media properties")
    parser.add_argument("video", type=Path)
    parser.add_argument("--subtitles", choices=("burned", "no"), required=True)
    parser.add_argument("--max-duration", required=True, type=float)
    parser.add_argument("--srt", type=Path)
    parser.add_argument("--timeline", type=Path)
    parser.add_argument(
        "--replace-output",
        type=Path,
        help="Atomically publish this verified temporary video at the given final path",
    )
    args = parser.parse_args()
    if args.max_duration <= 0:
        parser.error("--max-duration must be positive")
    if args.subtitles == "burned" and not args.srt:
        parser.error("--srt is required when subtitles are enabled")
    if args.subtitles == "burned" and not args.timeline:
        parser.error("--timeline is required when subtitles are burned in")
    if args.subtitles == "no" and (args.srt or args.timeline):
        parser.error("subtitle options are not allowed when subtitles are disabled")
    video = args.video.expanduser().resolve()
    if not video.is_file():
        raise FileNotFoundError(video)
    srt = args.srt.expanduser().resolve() if args.srt else None
    timeline = args.timeline.expanduser().resolve() if args.timeline else None
    replace_output = (
        args.replace_output.expanduser().resolve() if args.replace_output else None
    )

    info = probe_media(video)
    failures = validate_video(info, args.max_duration)
    captions = None
    if args.subtitles == "burned":
        if not srt or not srt.is_file():
            failures.append(f"expected separate SRT file, missing {srt}")
        else:
            try:
                text = srt.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                failures.append(f"SRT must be UTF-8: {srt}")
            else:
                if not text.strip():
                    failures.append(f"SRT must not be empty: {srt}")
                if "-->" not in text:
                    failures.append(f"SRT has no timestamp cue: {srt}")
                if timeline:
                    try:
                        timeline_data = load_timeline(timeline)
                        captions = timeline_data.get("captions")
                        if not isinstance(captions, dict):
                            raise ValueError("timeline requires a captions mapping")
                        expected = srt_content(build_cues(timeline_data))
                    except (OSError, ValueError) as error:
                        failures.append(f"timeline captions are invalid: {error}")
                    else:
                        if text != expected:
                            failures.append(
                                "SRT differs from the authoritative timeline beat subtitles"
                            )
    if not failures and replace_output:
        replace_output.parent.mkdir(parents=True, exist_ok=True)
        os.replace(video, replace_output)

    report = {
        "file": str(replace_output or video),
        "max_duration_seconds": args.max_duration,
        **media_report(info),
        "caption_language": captions["language"] if captions else None,
        "srt": str(srt) if srt else None,
        "passed": not failures,
        "failures": failures,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
