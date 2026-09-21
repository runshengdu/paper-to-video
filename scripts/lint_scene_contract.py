#!/usr/bin/env python3
"""Reject scene patterns that diverge between snapshots and encoded renders."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT_SELECTORS = (
    r"""["']#root["']""",
    r"""["']\.clip["']""",
    r"\broot\b",
)
VISIBILITY_PROPERTIES = r"\b(?:autoAlpha|opacity|visibility|display)\b"


def line_number(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def root_variables(text: str) -> set[str]:
    return {
        match.group("name")
        for match in re.finditer(
            r"""\b(?:const|let|var)\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*
                document\.getElementById\(\s*["']root["']\s*\)""",
            text,
            re.VERBOSE,
        )
    }


def is_root_target(target: str, root_names: set[str]) -> bool:
    compact = re.sub(r"\s+", "", target)
    return (
        compact in root_names
        or compact in {'"#root"', "'#root'", '".clip"', "'.clip'"}
    )


def visibility_animation_errors(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    names = root_variables(text)
    call = re.compile(
        r"""\b(?:gsap|tl|timeline)\s*\.\s*
            (?P<method>set|to|from|fromTo)\s*
            \(\s*(?P<target>[^,]+)\s*,\s*
            (?P<first>\{[^{}]*\})
            (?:\s*,\s*(?P<second>\{[^{}]*\}))?""",
        re.VERBOSE | re.DOTALL,
    )
    for match in call.finditer(text):
        if not is_root_target(match.group("target"), names):
            continue
        values = (match.group("first") or "") + (match.group("second") or "")
        if re.search(VISIBILITY_PROPERTIES, values):
            errors.append(
                f"{path}:{line_number(text, match.start())}: "
                "do not animate visibility on nested scene #root or .clip; "
                "HyperFrames owns clip visibility"
            )

    hidden_css = re.compile(
        r"""(?P<selector>[^{}]+)\{
            (?P<body>[^{}]*(?:display\s*:\s*none|visibility\s*:\s*hidden|
            opacity\s*:\s*0(?:\D|$))[^{}]*)\}""",
        re.IGNORECASE | re.VERBOSE,
    )
    for match in hidden_css.finditer(text):
        selector = match.group("selector")
        if "#root" in selector or ".clip" in selector:
            errors.append(
                f"{path}:{line_number(text, match.start())}: "
                "do not hide nested scene #root or .clip in CSS"
            )

    direct_style = re.compile(
        r"""\b(?:document\.getElementById\(\s*["']root["']\s*\)|root)
            \s*\.style\s*\.\s*(?:opacity|visibility|display)\b""",
        re.VERBOSE,
    )
    for match in direct_style.finditer(text):
        errors.append(
            f"{path}:{line_number(text, match.start())}: "
            "do not set visibility styles on nested scene #root"
        )
    return errors


def formula_runtime_errors(path: Path, text: str) -> list[str]:
    if "data-tex=" not in text:
        return []
    errors: list[str] = []
    if "../vendor/katex/katex.min.js" not in text:
        errors.append(f"{path}: formula scene must load local KaTeX")
    if "../formula_runtime.js" not in text:
        errors.append(f"{path}: formula scene must load ../formula_runtime.js after KaTeX")
    for match in re.finditer(r"\b(?:window\.)?katex\.render\s*\(", text):
        errors.append(
            f"{path}:{line_number(text, match.start())}: "
            "formula rendering belongs in formula_runtime.js, not scene code"
        )
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
        errors.extend(visibility_animation_errors(path, text))
        errors.extend(formula_runtime_errors(path, text))

    if errors:
        print("Scene contract errors:", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 2
    print(f"Scene contract ok: {len(list(scenes.glob('*.html')))} scenes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
