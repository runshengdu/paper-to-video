#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
from pathlib import Path


DEPENDENCIES = (
    "hyperframes@0.8.54",
    "gsap@3.15.0",
    "katex@0.18.7",
)

SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RUNTIME_DIR = SKILL_ROOT / "runtime"


def run(command, cwd):
    subprocess.run(command, cwd=cwd, check=True)


def replace_directory(source: Path, destination: Path) -> Path:
    if not source.is_dir():
        raise FileNotFoundError(f"vendor source missing at {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    return destination


def copy_vendor_assets(runtime: Path) -> Path:
    katex_dist = runtime / "node_modules" / "katex" / "dist"
    katex_vendor = runtime / "vendor" / "katex"
    if not katex_dist.is_dir():
        raise FileNotFoundError(f"KaTeX dist missing at {katex_dist}")
    katex_vendor.mkdir(parents=True, exist_ok=True)
    for name in ("katex.min.js", "katex.min.css"):
        shutil.copy2(katex_dist / name, katex_vendor / name)
    fonts = katex_dist / "fonts"
    if fonts.is_dir():
        replace_directory(fonts, katex_vendor / "fonts")

    gsap_source = runtime / "node_modules" / "gsap" / "dist" / "gsap.min.js"
    if not gsap_source.is_file():
        raise FileNotFoundError(f"GSAP bundle missing at {gsap_source}")
    gsap_vendor = runtime / "vendor" / "gsap"
    gsap_vendor.mkdir(parents=True, exist_ok=True)
    shutil.copy2(gsap_source, gsap_vendor / "gsap.min.js")
    return runtime / "vendor"


def main():
    parser = argparse.ArgumentParser(
        description="Install HyperFrames, GSAP, and KaTeX into the skill runtime directory"
    )
    parser.add_argument(
        "--runtime-dir",
        type=Path,
        default=DEFAULT_RUNTIME_DIR,
        help=f"isolated npm runtime (default: {DEFAULT_RUNTIME_DIR})",
    )
    args = parser.parse_args()
    runtime = args.runtime_dir.expanduser().resolve()
    runtime.mkdir(parents=True, exist_ok=True)
    if any(runtime.iterdir()) and not (runtime / "package.json").exists():
        raise SystemExit(
            f"{runtime} is not empty and is not a previous runtime; choose a new directory"
        )

    package = runtime / "package.json"
    if not package.exists():
        package.write_text(
            json.dumps(
                {
                    "name": "paper-to-timeline-video-runtime",
                    "private": True,
                    "dependencies": {},
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    run(["npm", "install", "--save-exact", *DEPENDENCIES], cwd=runtime)
    vendor = copy_vendor_assets(runtime)
    print(vendor)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
