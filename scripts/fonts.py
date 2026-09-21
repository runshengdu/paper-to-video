#!/usr/bin/env python3
"""Resolve a timeline font family through fontconfig."""
from __future__ import annotations

import shutil
import subprocess


def font_match(font: str) -> dict:
    matcher = shutil.which("fc-match")
    if not matcher:
        return {
            "available": None,
            "matched_family": None,
            "file": None,
            "index": 0,
        }
    result = subprocess.run(
        [matcher, "-f", "%{family}\n%{file}\n%{index}", font],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    lines = result.stdout.strip().splitlines()
    family = lines[0] if lines else None
    file_path = lines[1] if len(lines) > 1 else None
    try:
        index = int(lines[2]) if len(lines) > 2 and lines[2].strip() else 0
    except ValueError:
        index = 0
    requested = " ".join(font.casefold().split())
    matched_names = [" ".join(name.casefold().split()) for name in (family or "").split(",")]
    return {
        "available": requested in matched_names,
        "matched_family": family,
        "file": file_path,
        "index": index,
    }
