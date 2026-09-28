#!/usr/bin/env python3
"""Lint formula scenes for local KaTeX and formula_runtime.js."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def line_number(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def formula_runtime_errors(path: Path, text: str) -> list[str]:
    if "data-tex=" not in text:
        return []
    errors: list[str] = []
    if "../vendor/katex/katex.min.js" not in text:
        errors.append(f"{path}: formula scene must load local KaTeX")
    if "../formula_runtime.js" not in text:
        errors.append(f"{path}: formula scene must load ../formula_runtime.js after KaTeX")
    for match in re.finditer(
        r"""document\.querySelectorAll\(\s*["']\[data-tex\]["']\s*\)""", text
    ):
        errors.append(
            f"{path}:{line_number(text, match.start())}: "
            "formula selection must be scoped to the scene root by formula_runtime.js"
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lint paper-to-video scene contracts beyond HyperFrames' built-in lint"
    )
    parser.add_argument("--animation-dir", required=True, type=Path)
    args = parser.parse_args()

    scenes = args.animation_dir.expanduser().resolve() / "scenes"
    if not scenes.is_dir():
        parser.error(f"scene directory not found: {scenes}")

    errors: list[str] = []
    for path in sorted(scenes.glob("*.html")):
        text = path.read_text(encoding="utf-8")
        errors.extend(formula_runtime_errors(path, text))

    if errors:
        print("Scene contract errors:", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 2
    print(f"Scene contract ok: {len(list(scenes.glob('*.html')))} scenes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
