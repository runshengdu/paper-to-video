"""Shared media inspection and validation for final paper videos."""
from __future__ import annotations

import json
import subprocess
from fractions import Fraction
from pathlib import Path


def probe_media(video: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(video),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def validate_video(info: dict, max_duration: float) -> list[str]:
    streams = info.get("streams", [])
    videos = [stream for stream in streams if stream.get("codec_type") == "video"]
    audio = [stream for stream in streams if stream.get("codec_type") == "audio"]
    subtitle_streams = [
        stream for stream in streams if stream.get("codec_type") == "subtitle"
    ]
    failures: list[str] = []

    if len(videos) != 1:
        failures.append(f"expected one video stream, found {len(videos)}")
    else:
        stream = videos[0]
        if (stream.get("width"), stream.get("height")) != (1920, 1080):
            failures.append(
                f"expected 1920x1080, found {stream.get('width')}x{stream.get('height')}"
            )
        rate_text = stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "0/1"
        rate = float(Fraction(rate_text))
        if abs(rate - 30.0) > 0.05:
            failures.append(f"expected 30 fps, found {rate:.3f}")

    duration = float(info.get("format", {}).get("duration", 0))
    if not 0 < duration <= max_duration:
        failures.append(
            f"duration must be within 0–{max_duration:g} seconds, found {duration:.3f}"
        )
    if audio:
        failures.append(f"expected no audio streams, found {len(audio)}")
    if subtitle_streams:
        failures.append(
            f"final video must not contain subtitle streams, found {len(subtitle_streams)}"
        )
    return failures


def media_report(info: dict) -> dict:
    streams = info.get("streams", [])
    return {
        "duration_seconds": float(info.get("format", {}).get("duration", 0)),
        "video_streams": sum(
            stream.get("codec_type") == "video" for stream in streams
        ),
        "audio_streams": sum(
            stream.get("codec_type") == "audio" for stream in streams
        ),
        "subtitle_streams": sum(
            stream.get("codec_type") == "subtitle" for stream in streams
        ),
    }
