"""Locate an FFmpeg binary suitable for paper-video production."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def _candidates() -> list[Path]:
    paths: list[Path] = []
    configured = os.environ.get("PAPER_TO_VIDEO_FFMPEG")
    if configured:
        paths.append(Path(configured).expanduser())
    command = shutil.which("ffmpeg")
    if command:
        paths.append(Path(command))
    paths.extend(
        [
            Path("/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"),
            Path("/usr/local/opt/ffmpeg-full/bin/ffmpeg"),
        ]
    )
    unique: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved.is_file() and resolved not in unique:
            unique.append(resolved)
    return unique


def supports_subtitles(binary: Path) -> bool:
    result = subprocess.run(
        [str(binary), "-hide_banner", "-filters"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and any(
        len(parts := line.split()) > 1 and parts[1] == "subtitles"
        for line in result.stdout.splitlines()
    )


def resolve_ffmpeg(require_subtitles: bool = False) -> Path | None:
    for binary in _candidates():
        if not require_subtitles or supports_subtitles(binary):
            return binary
    return None
