"""Mythos cinematography: the visual grammar for Claude Mythos-driven Manim.

Design language
---------------
The Mythos house style treats the camera as the narrator:

- HEADLINE   — say it huge, in plain words, before any symbol appears
- ZOOM IN    — fly into the exact term being explained
- PULL BACK  — restore context so the part is seen inside the whole
- TERM TOUR  — walk a formula term by term, captioning each in English
- SET PIECE  — tilt into true 3D for fields, surfaces, and worldlines

All helpers target Manim CE >= 0.19 and a ``ThreeDScene`` using the
"top-down stage" pattern: formulas and diagrams live in world space on the
z=0 plane, the camera starts top-down (phi=0) so the stage reads as 2D, and
tilts into 3D only for set pieces. Captions/headlines are fixed-in-frame.

Camera moves use ``scene.move_camera(...)`` (never ``.animate`` on the
camera), which is the CE-0.19-safe path for ThreeDScene.
"""

from __future__ import annotations

import numpy as np
from manim import (
    BLACK,
    DEGREES,
    DOWN,
    UP,
    LEFT,
    RIGHT,
    ORIGIN,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    MathTex,
    Mobject,
    ParametricFunction,
    Sphere,
    SurroundingRectangle,
    Text,
    ThreeDScene,
    VGroup,
    Write,
    interpolate_color,
    rgb_to_color,
)

# ---------------------------------------------------------------------------
# Mythos palette (Anthropic brand, tuned for dark stage)
# ---------------------------------------------------------------------------

INK = "#0c0c0b"          # stage background (near #141413, deepened for video)
IVORY = "#faf9f5"        # primary text
CORAL = "#d97757"        # matter / primary accent
SKY = "#6a9bcc"          # light, gauge fields / secondary accent
OLIVE = "#788c5d"        # mass, structure / tertiary accent
FOG = "#b0aea5"          # secondary text
GOLD = "#d4a27f"         # interaction, emphasis
EMBER = "#bd5d3a"        # deep accent for glows

TERM_COLORS = {
    "matter": CORAL,
    "light": SKY,
    "mass": OLIVE,
    "interaction": GOLD,
}

HEADLINE_FONT = "Poppins"   # falls back silently if not installed
CAPTION_FONT = "Lora"


def stage(scene: ThreeDScene, background: str = INK) -> None:
    """Initialize the top-down 2D-looking stage inside a ThreeDScene."""
    scene.camera.background_color = background
    scene.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=1.0)


# ---------------------------------------------------------------------------
# Headlines and captions (fixed in frame: the narration layer)
# ---------------------------------------------------------------------------

def headline(
    scene: ThreeDScene,
    text: str,
    sub: str | None = None,
    color: str = IVORY,
    accent: str = CORAL,
    hold: float = 1.6,
    font_size: int = 76,
) -> None:
    """Full-screen plain-language statement. The idea before the symbols."""
    title = Text(text, font=HEADLINE_FONT, font_size=font_size, weight="BOLD", color=color)
    title.set(width=min(title.width, 12.0))
    group = VGroup(title)
    if sub:
        subline = Text(sub, font=CAPTION_FONT, font_size=30, slant="ITALIC", color=FOG)
        subline.set(width=min(subline.width, 10.0))
        subline.next_to(title, DOWN, buff=0.55)
        group.add(subline)
    rule = Text("—", font=HEADLINE_FONT, font_size=40, color=accent)
    rule.next_to(group, UP, buff=0.5)
    group.add(rule)
    group.move_to(ORIGIN)
    scene.add_fixed_in_frame_mobjects(group)
    group.set_opacity(0)
    scene.play(group.animate.set_opacity(1).shift(UP * 0.12), run_time=1.1)
    scene.wait(hold)
    scene.play(FadeOut(group, shift=UP * 0.4), run_time=0.7)


def caption(
    scene: ThreeDScene,
    text: str,
    color: str = IVORY,
    hold: float = 0.0,
    font_size: int = 30,
) -> Text:
    """Lower-third caption. Replaces any previous caption automatically."""
    new = Text(text, font=CAPTION_FONT, font_size=font_size, slant="ITALIC", color=color)
    new.set(width=min(new.width, 11.5))
    new.to_edge(DOWN, buff=0.55)
    scene.add_fixed_in_frame_mobjects(new)
    new.set_opacity(0)
    old = getattr(scene, "_mythos_caption", None)
    if old is not None:
        scene.play(FadeOut(old, run_time=0.35), new.animate.set_opacity(1), run_time=0.6)
    else:
        scene.play(new.animate.set_opacity(1), run_time=0.6)
    scene._mythos_caption = new
    if hold:
        scene.wait(hold)
    return new


def clear_caption(scene: ThreeDScene) -> None:
    old = getattr(scene, "_mythos_caption", None)
    if old is not None:
        scene.play(FadeOut(old), run_time=0.4)
        scene._mythos_caption = None


# ---------------------------------------------------------------------------
# Camera choreography (ThreeDScene-safe)
# ---------------------------------------------------------------------------

def zoom_to(
    scene: ThreeDScene,
    target: Mobject,
    zoom: float = 2.4,
    run_time: float = 1.6,
    added_anims: list | None = None,
) -> None:
    """Fly the camera into a mobject (or formula part). The signature move."""
    scene.move_camera(
        frame_center=target.get_center(),
        zoom=zoom,
        run_time=run_time,
        added_anims=added_anims or [],
    )


def pull_back(
    scene: ThreeDScene,
    zoom: float = 1.0,
    center=ORIGIN,
    run_time: float = 1.4,
    added_anims: list | None = None,
) -> None:
    """Restore context: the part within the whole."""
    scene.move_camera(
        frame_center=center,
        zoom=zoom,
        run_time=run_time,
        added_anims=added_anims or [],
    )


def tilt_to_3d(
    scene: ThreeDScene,
    phi: float = 65 * DEGREES,
    theta: float = -45 * DEGREES,
    zoom: float = 0.9,
    run_time: float = 2.0,
) -> None:
    """Leave the flat stage and enter a 3D set piece."""
    scene.move_camera(phi=phi, theta=theta, zoom=zoom, run_time=run_time)


def return_to_stage(scene: ThreeDScene, run_time: float = 1.8, zoom: float = 1.0) -> None:
    scene.move_camera(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=zoom,
                      frame_center=ORIGIN, run_time=run_time)


def orbit(scene: ThreeDScene, rate: float = 0.06, duration: float = 4.0) -> None:
    """Slow ambient orbit during a 3D set piece."""
    scene.begin_ambient_camera_rotation(rate=rate)
    scene.wait(duration)
    scene.stop_ambient_camera_rotation()


# ---------------------------------------------------------------------------
# Formula spotlighting
# ---------------------------------------------------------------------------

def spotlight(
    scene: ThreeDScene,
    formula: MathTex,
    part: Mobject,
    color: str = CORAL,
    dim: float = 0.25,
    run_time: float = 0.9,
):
    """Dim the formula, ignite one part."""
    others = [m for m in formula.family_members_with_points()
              if m not in part.family_members_with_points()]
    frame = SurroundingRectangle(part, color=color, buff=0.12, stroke_width=2.5)
    scene.play(
        *[m.animate.set_opacity(dim) for m in others],
        part.animate.set_color(color).set_opacity(1.0),
        Create(frame),
        run_time=run_time,
    )
    return frame


def unspotlight(scene: ThreeDScene, formula: MathTex, frame: Mobject, run_time: float = 0.7) -> None:
    scene.play(
        formula.animate.set_opacity(1.0),
        FadeOut(frame),
        run_time=run_time,
    )


def term_tour(
    scene: ThreeDScene,
    formula: MathTex,
    stops: list[dict],
    zoom: float = 2.4,
    context_zoom: float = 1.0,
) -> None:
    """Walk a formula term by term.

    Each stop: {"tex": str | None, "part": Mobject | None, "color": str,
                "caption": str, "hold": float}
    Provide either ``tex`` (resolved via get_part_by_tex) or an explicit part.
    """
    for stop in stops:
        part = stop.get("part") or formula.get_part_by_tex(stop["tex"])
        color = stop.get("color", CORAL)
        frame = spotlight(scene, formula, part, color=color)
        zoom_to(scene, part, zoom=stop.get("zoom", zoom))
        caption(scene, stop["caption"], color=color, hold=stop.get("hold", 1.4))
        pull_back(scene, zoom=context_zoom)
        unspotlight(scene, formula, frame)


# ---------------------------------------------------------------------------
# Light: glows, starfields, fields
# ---------------------------------------------------------------------------

def glow(mobject: Mobject, color: str = CORAL, layers: int = 5, max_width: float = 18,
         opacity: float = 0.22) -> VGroup:
    """Halo built from blurred-looking stroke layers behind a mobject."""
    halo = VGroup()
    for i in range(layers, 0, -1):
        layer = mobject.copy()
        layer.set_stroke(color, width=max_width * i / layers, opacity=opacity * (1 - (i - 1) / layers) + 0.04)
        layer.set_fill(opacity=0)
        halo.add(layer)
    return halo


def glow_dot(point=ORIGIN, color: str = CORAL, radius: float = 0.07, layers: int = 6) -> VGroup:
    core = Dot(point=point, radius=radius, color=IVORY)
    halo = VGroup(*[
        Dot(point=point, radius=radius * (1 + 0.85 * i), color=color,
            fill_opacity=0.55 / (i + 1.2))
        for i in range(1, layers + 1)
    ])
    return VGroup(halo, core)


def starfield(n: int = 180, x: float = 10.0, y: float = 6.0, z: float = 4.0,
              seed: int = 7) -> VGroup:
    rng = np.random.default_rng(seed)
    stars = VGroup()
    for _ in range(n):
        p = [rng.uniform(-x, x), rng.uniform(-y, y), rng.uniform(-z, z)]
        s = Dot(point=p, radius=float(rng.uniform(0.008, 0.03)),
                color=interpolate_color(rgb_to_color([0.98, 0.97, 0.96]),
                                        rgb_to_color([0.85, 0.6, 0.45]),
                                        float(rng.random())))
        s.set_opacity(float(rng.uniform(0.25, 0.95)))
        stars.add(s)
    return stars


def photon_path(p0, p1, color: str = SKY, waves: float = 9.0, amp: float = 0.16,
                stroke_width: float = 3.0) -> ParametricFunction:
    """Wavy photon line between two points (in the z=0 plane)."""
    p0 = np.array(p0, dtype=float)
    p1 = np.array(p1, dtype=float)
    d = p1 - p0
    length = np.linalg.norm(d)
    u = d / max(length, 1e-8)
    nvec = np.array([-u[1], u[0], 0.0])

    def f(t: float):
        return p0 + d * t + nvec * amp * np.sin(t * waves * 2 * np.pi)

    return ParametricFunction(f, t_range=[0, 1], color=color, stroke_width=stroke_width)


__all__ = [
    "INK", "IVORY", "CORAL", "SKY", "OLIVE", "FOG", "GOLD", "EMBER", "TERM_COLORS",
    "stage", "headline", "caption", "clear_caption",
    "zoom_to", "pull_back", "tilt_to_3d", "return_to_stage", "orbit",
    "spotlight", "unspotlight", "term_tour",
    "glow", "glow_dot", "starfield", "photon_path",
]
