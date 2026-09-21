#!/usr/bin/env python3
import argparse
from importlib import metadata
import json
import shutil
import subprocess
import sys
from pathlib import Path

from ffmpeg_tools import resolve_ffmpeg, supports_subtitles
from fonts import font_match

SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RUNTIME_DIR = SKILL_ROOT / "runtime"


def package_version(name):
    try:
        version = metadata.version(name)
    except metadata.PackageNotFoundError:
        return {"available": False, "version": None}
    return {"available": True, "version": version}


def command_version(command, args=("--version",), cwd=None):
    path = command if Path(command).exists() else shutil.which(command)
    if not path:
        return {"available": False, "path": None, "version": None}
    result = subprocess.run(
        [str(path), *args],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        cwd=cwd,
    )
    output = (result.stdout or result.stderr).strip().splitlines()
    return {
        "available": result.returncode == 0,
        "path": str(path),
        "version": output[0] if output else None,
    }


def ffmpeg_subtitles_filter(ffmpeg):
    if not ffmpeg:
        return {
            "available": False,
            "path": None,
            "reason": "FFmpeg subtitles filter requires libass support",
        }
    return {
        "available": supports_subtitles(ffmpeg),
        "path": str(ffmpeg),
        "reason": None,
    }


def main():
    parser = argparse.ArgumentParser(description="Check the timeline video runtime")
    parser.add_argument(
        "--runtime-dir",
        type=Path,
        default=DEFAULT_RUNTIME_DIR,
        help=f"isolated npm runtime (default: {DEFAULT_RUNTIME_DIR})",
    )
    parser.add_argument("--required-font", action="append", default=[])
    parser.add_argument(
        "--burn-subtitles",
        action="store_true",
        help="require the FFmpeg subtitles filter needed for burned-in captions",
    )
    args = parser.parse_args()

    runtime = args.runtime_dir.expanduser().resolve()
    ffmpeg_binary = resolve_ffmpeg(require_subtitles=args.burn_subtitles)
    candidate = runtime / "node_modules" / ".bin" / "hyperframes"
    hyperframes = (
        command_version(candidate, ("--help",), cwd=runtime)
        if candidate.exists()
        else {"available": False, "path": str(candidate), "version": None}
    )
    vendor = runtime / "vendor" / "katex" / "katex.min.js"
    katex = {"available": vendor.is_file(), "path": str(vendor) if vendor.is_file() else None}
    bundle = runtime / "vendor" / "gsap" / "gsap.min.js"
    gsap = {"available": bundle.is_file(), "path": str(bundle) if bundle.is_file() else None}

    report = {
        "python": {
            "available": sys.version_info >= (3, 10),
            "path": sys.executable,
            "version": sys.version.split()[0],
        },
        "pyyaml": package_version("PyYAML"),
        "node": command_version("node"),
        "npm": command_version("npm"),
        "ffmpeg": command_version(ffmpeg_binary or "ffmpeg", ("-version",)),
        "ffprobe": command_version("ffprobe", ("-version",)),
        "hyperframes": hyperframes,
        "katex_vendor": katex,
        "gsap_vendor": gsap,
    }
    if args.burn_subtitles:
        report["ffmpeg_subtitles_filter"] = ffmpeg_subtitles_filter(ffmpeg_binary)
    if args.required_font:
        report["required_fonts"] = {font: font_match(font) for font in args.required_font}

    required = ["python", "pyyaml", "node", "npm", "ffmpeg", "ffprobe", "hyperframes"]
    failures = [name for name in required if not report[name]["available"]]
    if not report["katex_vendor"]["available"]:
        failures.append("katex_vendor")
    if not report["gsap_vendor"]["available"]:
        failures.append("gsap_vendor")
    if args.burn_subtitles and not report["ffmpeg_subtitles_filter"]["available"]:
        failures.append("ffmpeg_subtitles_filter")
    for font, match in report.get("required_fonts", {}).items():
        if match["available"] is False:
            failures.append(f"font:{font}")

    report["ready"] = not failures
    report["missing"] = failures
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
