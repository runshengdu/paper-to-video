#!/usr/bin/env python3
"""Shared timeline load/resolve helpers. Requires PyYAML for YAML timelines."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import yaml


REQUIRED_TIMELINE = ("fps", "width", "height", "duration", "font", "colors", "clips")
REQUIRED_COLORS = ("background", "text", "primary", "secondary", "accent", "muted")
EXTRA_COLOR_NAME = re.compile(r"^[A-Za-z_][\w-]*$")
RESERVED_CSS_COLOR_NAMES = frozenset(
    {
        "bg",
        "font",
        "frame-width",
        "frame-height",
        "frame-aspect-ratio",
        "stage-padding-x",
        "stage-padding-top",
        "stage-padding-bottom",
        "stage-content-width",
        "caption-clearance-bottom",
        "caption-clearance-guard",
    }
)
REQUIRED_CLIP = ("id", "start", "duration", "track", "file", "purpose")
REQUIRED_BEAT = ("id", "at", "duration", "kind", "job")
REQUIRED_CAPTION_LAYOUT = (
    "font_size",
    "margin_bottom",
    "max_lines",
    "outline",
)
CAPTION_CLEARANCE_GUARD = 16
CAPTION_LINE_HEIGHT = 1.25
DEFAULT_MARGIN_X = 140


def snap(seconds: float, fps: float) -> float:
    return round(seconds * fps) / fps


def parse_clock(value: str) -> float:
    text = value.strip()
    if not text:
        raise ValueError("empty clock time")
    if ":" in text:
        parts = text.split(":")
        if len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + float(seconds)
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        raise ValueError(f"unsupported clock format: {value}")
    return float(text)


def format_clock(seconds: float) -> str:
    total = max(0.0, seconds)
    minutes = int(total // 60)
    remainder = total - minutes * 60
    if abs(remainder - round(remainder)) < 1e-6:
        return f"{minutes}:{int(round(remainder)):02d}"
    return f"{minutes}:{remainder:04.1f}"


def load_timeline(path: Path) -> dict:
    path = path.expanduser().resolve()
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a mapping")
    validate_timeline(data)
    return data


def validate_timeline(data: dict) -> None:
    for key in REQUIRED_TIMELINE:
        if key not in data:
            raise ValueError(f"timeline missing {key}")
    if data["fps"] <= 0:
        raise ValueError("fps must be positive")
    for name in ("width", "height", "duration"):
        if (
            not isinstance(data[name], (int, float))
            or isinstance(data[name], bool)
            or data[name] <= 0
        ):
            raise ValueError(f"timeline {name} must be a positive number")
    if not isinstance(data["font"], str) or not data["font"].strip():
        raise ValueError("timeline font must be a non-empty string")
    colors = data["colors"]
    if not isinstance(colors, dict):
        raise ValueError("timeline colors must be a mapping")
    for name in REQUIRED_COLORS:
        if not isinstance(colors.get(name), str) or not colors[name].strip():
            raise ValueError(f"timeline color {name} must be a non-empty string")
    for name, value in colors.items():
        if name in REQUIRED_COLORS:
            continue
        if not EXTRA_COLOR_NAME.fullmatch(name):
            raise ValueError(
                f"timeline extra color {name!r} must be a CSS identifier "
                "(start with a letter or underscore; then letters, digits, hyphen, or underscore)"
            )
        if name in RESERVED_CSS_COLOR_NAMES:
            raise ValueError(
                f"timeline extra color {name} collides with a generated CSS variable"
            )
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"timeline extra color {name} must be a non-empty string")
    if "margin" in data and data["margin"] is not None:
        if not isinstance(data["margin"], dict):
            raise ValueError("timeline margin must be a mapping")
        for name in ("x", "top", "bottom"):
            if name in data["margin"] and (
                not isinstance(data["margin"][name], (int, float))
                or isinstance(data["margin"][name], bool)
                or data["margin"][name] < 0
            ):
                raise ValueError(f"timeline margin {name} must be a non-negative number")
    captions = data.get("captions")
    if captions is not None:
        if not isinstance(captions, dict):
            raise ValueError("timeline captions must be a mapping")
        if not isinstance(captions.get("enabled"), bool):
            raise ValueError("timeline captions.enabled must be boolean")
        if captions["enabled"]:
            language = captions.get("language")
            if not isinstance(language, str) or not re.fullmatch(r"[a-z]{3}", language):
                raise ValueError(
                    "timeline captions.language must be a lowercase three-letter ISO 639 code"
                )
            layout = captions.get("layout")
            if not isinstance(layout, dict):
                raise ValueError("timeline captions.layout must be a mapping")
            for name in REQUIRED_CAPTION_LAYOUT:
                if name not in layout:
                    raise ValueError(f"timeline captions.layout missing {name}")
            for name in ("font_size", "max_lines"):
                if (
                    not isinstance(layout[name], int)
                    or isinstance(layout[name], bool)
                    or layout[name] <= 0
                ):
                    raise ValueError(f"timeline captions.layout {name} must be a positive integer")
            for name in ("margin_bottom", "outline"):
                if (
                    not isinstance(layout[name], (int, float))
                    or isinstance(layout[name], bool)
                    or layout[name] < 0
                ):
                    raise ValueError(
                        f"timeline captions.layout {name} must be non-negative"
                    )
            stage_bottom = (data.get("margin") or {}).get("bottom", 200)
            caption_height = (
                layout["font_size"] * CAPTION_LINE_HEIGHT * layout["max_lines"]
                + layout["margin_bottom"]
                + 2 * layout["outline"]
                + CAPTION_CLEARANCE_GUARD
            )
            if caption_height > stage_bottom:
                raise ValueError(
                    "timeline margin.bottom must fit caption line height, "
                    "outline, and clearance guard"
                )
    clips = data["clips"]
    if not isinstance(clips, list) or not clips:
        raise ValueError("timeline needs at least one clip")
    ids = []
    for clip in clips:
        for key in REQUIRED_CLIP:
            if key not in clip:
                raise ValueError(f"clip missing {key}: {clip.get('id')}")
        ids.append(clip["id"])
        end = clip["start"] + clip["duration"]
        if clip["start"] < 0 or clip["duration"] <= 0:
            raise ValueError(f"clip {clip['id']} has invalid timing")
        if end - 1e-9 > data["duration"]:
            raise ValueError(
                f"clip {clip['id']} ends at {end}, past duration {data['duration']}"
            )
        beats = clip.get("beats") or []
        beat_ids = []
        for beat in beats:
            for key in REQUIRED_BEAT:
                if key not in beat:
                    raise ValueError(f"beat missing {key} in clip {clip['id']}")
            kind = beat["kind"]
            if not isinstance(kind, str) or not kind.strip():
                raise ValueError(
                    f"beat {beat['id']} in {clip['id']} needs a non-empty kind"
                )
            if beat["at"] < 0 or beat["duration"] <= 0:
                raise ValueError(f"beat {beat['id']} has invalid timing")
            if beat["at"] + beat["duration"] - 1e-9 > clip["duration"]:
                raise ValueError(
                    f"beat {beat['id']} overruns clip {clip['id']}"
                )
            if beat["kind"] == "formula" and (
                not isinstance(beat.get("tex"), str) or not beat["tex"]
            ):
                raise ValueError(
                    f"formula beat {beat['id']} in {clip['id']} needs a non-empty tex value"
                )
            if "subtitle" in beat and (
                not isinstance(beat["subtitle"], str) or not beat["subtitle"].strip()
            ):
                raise ValueError(
                    f"subtitle for beat {beat['id']} in {clip['id']} must be non-empty text"
                )
            beat_ids.append(beat["id"])
        if len(beat_ids) != len(set(beat_ids)):
            raise ValueError(f"duplicate beat id in clip {clip['id']}")
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate clip id")


def resolve_time(data: dict, seconds: float) -> dict:
    fps = float(data["fps"])
    t = snap(seconds, fps)
    hits = [
        clip
        for clip in data["clips"]
        if clip["start"] <= t < clip["start"] + clip["duration"]
        or (
            math.isclose(t, clip["start"] + clip["duration"])
            and math.isclose(t, float(data["duration"]))
        )
    ]
    if not hits:
        return {
            "seconds": t,
            "clock": format_clock(t),
            "clip": None,
            "beat": None,
            "local": None,
            "message": "no clip covers this time",
        }
    hits.sort(key=lambda clip: (-int(clip["track"]), clip["duration"]))
    clip = hits[0]
    local = snap(t - clip["start"], fps)
    beat_hit = None
    for beat in clip.get("beats") or []:
        start = beat["at"]
        end = beat["at"] + beat["duration"]
        if start <= local < end or (
            math.isclose(local, end) and math.isclose(end, clip["duration"])
        ):
            if beat_hit is None or beat["duration"] < beat_hit["duration"]:
                beat_hit = beat
    result = {
        "seconds": t,
        "clock": format_clock(t),
        "clip": clip["id"],
        "clip_start": clip["start"],
        "clip_duration": clip["duration"],
        "local": local,
        "file": clip["file"],
        "beat": None,
    }
    if beat_hit:
        result["beat"] = beat_hit["id"]
        result["beat_kind"] = beat_hit["kind"]
        result["beat_at"] = beat_hit["at"]
        result["beat_duration"] = beat_hit["duration"]
        result["absolute_beat_start"] = snap(clip["start"] + beat_hit["at"], fps)
        result["absolute_beat_clock"] = format_clock(result["absolute_beat_start"])
    return result


