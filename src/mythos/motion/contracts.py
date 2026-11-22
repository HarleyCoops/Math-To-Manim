"""Typed contracts between the motion stages.

BriefSpec (stage 1) -> StyleSheet (stage 2) -> Timeline (stage 3) ->
scene code (stage 4) -> QAReport (stage 5) -> repair (stage 6).

Each model is permissive about extra keys (models add useful notes) and
strict about the values later stages compute with. The ``*_problems``
functions return human-readable problems for one retry of the stage that
produced the artifact; an empty list means the artifact is usable.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
DURATION_TOLERANCE_S = 0.1
FIELD_TYPES = ("format", "colour", "timing", "text", "layout", "motion", "element", "rule")
FieldType = Literal["format", "colour", "timing", "text", "layout", "motion", "element", "rule"]


def _hex(value: str) -> str:
    value = value.strip()
    if len(value) == 4 and value.startswith("#"):
        value = "#" + "".join(ch * 2 for ch in value[1:])
    if not HEX.fullmatch(value):
        raise ValueError(f"not a #RRGGBB colour: {value!r}")
    return value.upper()


class _Model(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


# ---------------------------------------------------------------------- #
# Stage 1: BriefSpec                                                      #
# ---------------------------------------------------------------------- #

class Colour(_Model):
    role: str
    hex: str
    #: True when the brief states the hex; False when the parser chose it for
    #: a colour the brief names in words ("pale lilac").
    exact: bool = True
    source: str

    @field_validator("hex")
    @classmethod
    def check_hex(cls, value: str) -> str:
        return _hex(value)


class Font(_Model):
    role: str
    family: str
    weight: str | None = None
    source: str


class TextString(_Model):
    id: str
    text: str
    role: str = "label"
    order: int | None = None
    source: str


class Element(_Model):
    id: str
    description: str
    kind: str = "shape"
    position: str | None = None
    #: The brief describes a real brand's logo or mark: render as text only.
    brand_mark: bool = False
    source: str


class TimingBeat(_Model):
    id: str
    description: str
    start_s: float | None = None
    end_s: float | None = None
    source: str


class MotionSpec(_Model):
    id: str
    target: str
    verb: str
    direction: str | None = None
    easing: str | None = None
    continuous: bool = False
    source: str


class Rule(_Model):
    id: str
    rule: str
    source: str


class BriefSpec(_Model):
    aspect_ratio: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    duration_s: float = Field(gt=0)
    fps: float = Field(gt=0)
    format_source: str
    background: str
    camera: str
    depth_permitted: bool = False
    audio: str = "none"
    palette: list[Colour] = Field(default_factory=list)
    fonts: list[Font] = Field(default_factory=list)
    texts: list[TextString] = Field(default_factory=list)
    elements: list[Element] = Field(default_factory=list)
    beats: list[TimingBeat] = Field(default_factory=list)
    motions: list[MotionSpec] = Field(default_factory=list)
    rules: list[Rule] = Field(default_factory=list)
    brand_names: list[str] = Field(default_factory=list)


def _norm(text: str) -> str:
    text = text.replace("→", "->").replace("—", "-").replace("–", "-")
    text = re.sub(r"[“”]", '"', text)
    text = re.sub(r"[‘’]", "'", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def source_found(source: str, brief: str) -> bool:
    """True when ``source`` quotes the brief, or names a charter default."""
    if source.strip().lower().startswith(("default", "charter")):
        return True
    needle = _norm(source).strip(" .\"'")
    if not needle:
        return False
    hay = _norm(brief)
    if needle in hay:
        return True
    # Allow an ellipsis-joined quote: every fragment must appear in order.
    parts = [p.strip(" .\"'") for p in re.split(r"\.\.\.|…", needle) if p.strip(" .")]
    position = 0
    for part in parts:
        found = hay.find(part, position)
        if found == -1:
            return False
        position = found + len(part)
    return bool(parts)


def brief_spec_problems(spec: BriefSpec, brief: str) -> list[str]:
    problems: list[str] = []
    for group in ("palette", "fonts", "texts", "elements", "beats", "motions", "rules"):
        for item in getattr(spec, group):
            if not source_found(item.source, brief):
                label = getattr(item, "id", None) or getattr(item, "role", "?")
                problems.append(f"{group}[{label}].source does not quote the brief: "
                                f"{item.source[:120]!r}")
    if not spec.texts and '"' in brief:
        problems.append("the brief quotes text strings but 'texts' is empty")
    w, h = spec.width, spec.height
    ratio = {"16:9": 16 / 9, "9:16": 9 / 16, "1:1": 1.0, "4:5": 4 / 5, "4:3": 4 / 3}
    expected = ratio.get(spec.aspect_ratio.replace(" ", ""))
    if expected and abs(w / h - expected) > 0.01:
        problems.append(f"{w}x{h} does not match aspect ratio {spec.aspect_ratio}")
    return problems


# ---------------------------------------------------------------------- #
# Stage 2: StyleSheet                                                     #
# ---------------------------------------------------------------------- #

class TypeStyle(_Model):
    role: str
    font: str
    size_px: float = Field(gt=0)
    weight: str = "regular"
    colour: str

    @field_validator("colour")
    @classmethod
    def check_colour(cls, value: str) -> str:
        return _hex(value)


class Easing(_Model):
    name: str
    use: str
    #: A Manim rate function (e.g. "ease_out_cubic", "smooth") or a custom
    #: one the coder must define in the scene.
    manim_rate_func: str


class ColourRole(_Model):
    role: str
    hex: str
    opacity: float = Field(default=1.0, ge=0, le=1)
    #: "brief" when the hex is in BriefSpec.palette; otherwise the palette
    #: hex it is derived from (a tint or shade the brief permits).
    derived_from: str = "brief"
    justification: str = ""

    @field_validator("hex")
    @classmethod
    def check_hex(cls, value: str) -> str:
        return _hex(value)


class StyleSheet(_Model):
    type_scale: list[TypeStyle] = Field(min_length=1)
    grid: dict = Field(default_factory=dict)
    safe_margin_px: int = Field(ge=0)
    easings: list[Easing] = Field(min_length=1)
    colour_roles: list[ColourRole] = Field(min_length=1)


def style_sheet_problems(sheet: StyleSheet, spec: BriefSpec) -> list[str]:
    palette = {c.hex for c in spec.palette}
    problems = []
    for role in sheet.colour_roles:
        if role.derived_from == "brief" and role.hex not in palette:
            problems.append(f"colour role {role.role!r} uses {role.hex}, which is not in "
                            "BriefSpec.palette; set derived_from and a justification")
        if role.derived_from != "brief" and not role.justification.strip():
            problems.append(f"colour role {role.role!r} is derived but has no justification")
    short_side = min(spec.width, spec.height)
    if sheet.safe_margin_px < 0.05 * short_side - 0.5:
        problems.append(f"safe_margin_px {sheet.safe_margin_px} is below 5% of the short "
                        f"side ({0.05 * short_side:.0f}px)")
    for easing in sheet.easings:
        if easing.manim_rate_func.strip() == "linear" and "linear" not in easing.use.lower():
            problems.append(f"easing {easing.name!r} is linear; the charter forbids linear "
                            "easing unless the brief asks for it")
    return problems


# ---------------------------------------------------------------------- #
# Stage 3: Timeline                                                       #
# ---------------------------------------------------------------------- #

class Motion(_Model):
    element: str
    motion: str
    start_s: float = Field(ge=0)
    duration_s: float = Field(ge=0)
    easing: str = ""


class Beat(_Model):
    id: str
    start_s: float = Field(ge=0)
    end_s: float = Field(gt=0)
    focal_point: str
    on_screen: list[str] = Field(default_factory=list)
    enter: list[Motion] = Field(default_factory=list)
    exit: list[Motion] = Field(default_factory=list)
    continuous: list[str] = Field(default_factory=list)
    camera: str = "static"


class Timeline(_Model):
    duration_s: float = Field(gt=0)
    beats: list[Beat] = Field(min_length=1)


def timeline_problems(timeline: Timeline, spec: BriefSpec) -> list[str]:
    problems = []
    if abs(timeline.duration_s - spec.duration_s) > DURATION_TOLERANCE_S:
        problems.append(f"timeline duration {timeline.duration_s}s differs from the brief's "
                        f"{spec.duration_s}s by more than {DURATION_TOLERANCE_S}s")
    beats = sorted(timeline.beats, key=lambda b: b.start_s)
    if beats[0].start_s > 1e-6:
        problems.append(f"first beat starts at {beats[0].start_s}s, not 0")
    for prev, nxt in zip(beats, beats[1:]):
        if abs(nxt.start_s - prev.end_s) > 1e-3:
            problems.append(f"gap or overlap between beats {prev.id!r} (ends {prev.end_s}) "
                            f"and {nxt.id!r} (starts {nxt.start_s})")
    for beat in beats:
        if beat.end_s <= beat.start_s:
            problems.append(f"beat {beat.id!r} ends before it starts")
    total = sum(b.end_s - b.start_s for b in beats)
    if abs(total - spec.duration_s) > DURATION_TOLERANCE_S:
        problems.append(f"beats sum to {total:.3f}s, brief duration is {spec.duration_s}s")
    return problems


# ---------------------------------------------------------------------- #
# Stage 5: QAReport                                                       #
# ---------------------------------------------------------------------- #

class QACheck(_Model):
    field: str
    field_type: FieldType
    expected: str
    observed: str = ""
    passed: bool
    method: Literal["probe", "pixel", "vision"]
    frame: str | None = None
    note: str = ""


class QAReport(_Model):
    loop: int = 0
    checks: list[QACheck] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return bool(self.checks) and all(c.passed for c in self.checks)

    @property
    def failures(self) -> list[QACheck]:
        return [c for c in self.checks if not c.passed]

    def pass_rate_by_type(self) -> dict[str, dict[str, float]]:
        table: dict[str, dict[str, float]] = {}
        for check in self.checks:
            row = table.setdefault(check.field_type, {"passed": 0, "total": 0})
            row["total"] += 1
            row["passed"] += int(check.passed)
        for row in table.values():
            row["rate"] = round(row["passed"] / row["total"], 3) if row["total"] else 0.0
        return table


#: JSON schema the visual QA agent must answer with (vision checks only).
VISION_QA_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["checks"],
    "properties": {
        "checks": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["field", "field_type", "expected", "observed", "passed", "frame"],
                "properties": {
                    "field": {"type": "string"},
                    "field_type": {"type": "string",
                                   "enum": ["colour", "timing", "text", "layout", "motion",
                                            "element", "rule"]},
                    "expected": {"type": "string"},
                    "observed": {"type": "string"},
                    "passed": {"type": "boolean"},
                    "frame": {"type": ["string", "null"]},
                    "note": {"type": "string"},
                },
            },
        },
    },
}
