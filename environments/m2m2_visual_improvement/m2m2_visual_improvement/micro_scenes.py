"""Deterministic short Manim scenes used as the controlled RL laboratory."""

from __future__ import annotations

from copy import deepcopy
from typing import Annotated

from pydantic import Field, JsonValue

from .schemas import FocusBeat, NonEmpty, SourceCode, StrictFrozenModel


class BaseScene(StrictFrozenModel):
    base_scene_id: NonEmpty
    scene_name: NonEmpty
    title: NonEmpty
    prompt: NonEmpty
    audience: NonEmpty
    required_concepts: tuple[NonEmpty, ...] = Field(min_length=1)
    required_formulas: tuple[NonEmpty, ...] = Field(min_length=1)
    required_narrative_beats: tuple[NonEmpty, ...] = Field(min_length=1)
    duration_seconds: Annotated[float, Field(ge=6.0, le=12.0)]
    scene_spec: dict[str, JsonValue]
    code: SourceCode
    focus_beats: tuple[FocusBeat, ...] = Field(min_length=1)


_TOPICS = (
    (
        "negative_product",
        "Why two negatives make a positive",
        "Show why multiplying two negative numbers gives a positive result.",
        ("negative direction", "repeated reversal"),
        (r"(-2)(-3)=6",),
    ),
    (
        "fraction_equivalence",
        "Equivalent fractions share one amount",
        "Show why one half and two quarters are equal.",
        ("fraction", "partition", "equivalence"),
        (r"\frac{1}{2}=\frac{2}{4}",),
    ),
    (
        "slope_triangle",
        "Slope is rise over run",
        "Build a slope triangle on a line.",
        ("slope", "rise", "run"),
        (r"m=\frac{\Delta y}{\Delta x}",),
    ),
    (
        "pythagorean_tiles",
        "The squares rearrange",
        "Show the Pythagorean theorem with area tiles.",
        ("right triangle", "area", "rearrangement"),
        (r"a^2+b^2=c^2",),
    ),
    (
        "quadratic_roots",
        "Roots are axis crossings",
        "Connect factors of a quadratic to its graph roots.",
        ("factor", "root", "x-intercept"),
        (r"(x-1)(x+2)=0",),
    ),
    (
        "derivative_tangent",
        "A secant becomes a tangent",
        "Zoom from a secant slope to a derivative.",
        ("secant", "tangent", "limit"),
        (r"f'(x)=\lim_{h\to0}\frac{f(x+h)-f(x)}{h}",),
    ),
    (
        "integral_area",
        "Thin rectangles accumulate",
        "Build area under a curve from rectangles.",
        ("Riemann sum", "area", "integral"),
        (r"\int_a^b f(x)\,dx",),
    ),
    (
        "unit_circle",
        "Coordinates trace sine and cosine",
        "Project a rotating radius onto the axes.",
        ("unit circle", "sine", "cosine"),
        (r"(\cos\theta,\sin\theta)",),
    ),
    (
        "vector_addition",
        "Vectors add head to tail",
        "Show vector addition geometrically.",
        ("vector", "translation", "resultant"),
        (r"\vec a+\vec b=\vec c",),
    ),
    (
        "matrix_transform",
        "A matrix moves a basis",
        "Transform basis vectors and a grid with a matrix.",
        ("basis", "linear transformation", "matrix"),
        (r"A\vec e_i=\vec v_i",),
    ),
    (
        "probability_tree",
        "Branch probabilities multiply",
        "Use a tree to compute a joint probability.",
        ("conditional probability", "branch", "joint event"),
        (r"P(A\cap B)=P(A)P(B\mid A)",),
    ),
    (
        "exponential_growth",
        "Equal time means equal factors",
        "Compare repeated multiplication with linear growth.",
        ("exponential growth", "doubling", "rate"),
        (r"N(t)=N_0\,2^{t/T}",),
    ),
    (
        "sine_wave",
        "Circular motion writes a wave",
        "Unroll circular motion into a sine wave.",
        ("phase", "amplitude", "period"),
        (r"y=A\sin(\omega t+\phi)",),
    ),
    (
        "complex_rotation",
        "Multiplication rotates the plane",
        "Show complex multiplication as rotation.",
        ("complex plane", "rotation", "magnitude"),
        (r"re^{i\theta}z",),
    ),
    (
        "dot_product",
        "The dot product measures alignment",
        "Project one vector onto another.",
        ("projection", "angle", "dot product"),
        (r"\vec a\cdot\vec b=\|\vec a\|\|\vec b\|\cos\theta",),
    ),
    (
        "epsilon_limit",
        "A shrinking band traps the graph",
        "Visualize the epsilon-delta definition of a limit.",
        ("limit", "epsilon", "delta"),
        (r"0<|x-a|<\delta\Rightarrow|f(x)-L|<\varepsilon",),
    ),
    (
        "fourier_modes",
        "Simple waves build a signal",
        "Add Fourier modes one at a time.",
        ("frequency", "mode", "superposition"),
        (r"f(x)=\sum_n c_n e^{inx}",),
    ),
    (
        "heat_equation",
        "High frequencies cool first",
        "Show why Fourier modes solve the heat equation.",
        ("diffusion", "Fourier mode", "decay"),
        (r"u_t=\alpha u_{xx}", r"e^{-\alpha k^2t}"),
    ),
)


def _scene_spec(
    *,
    base_scene_id: str,
    scene_name: str,
    title: str,
    formula: str,
    duration_seconds: float,
) -> dict[str, JsonValue]:
    return {
        "schema_version": "m2m2.micro_scene.v1",
        "base_scene_id": base_scene_id,
        "scene_name": scene_name,
        "duration_seconds": duration_seconds,
        "objects": [
            {
                "id": "title",
                "kind": "text",
                "text": title,
                "x": 0.0,
                "y": 2.7,
                "font_size": 34,
            },
            {
                "id": "formula",
                "kind": "math",
                "text": formula,
                "x": 0.0,
                "y": 0.0,
                "scale": 0.9,
            },
            {
                "id": "focus_target",
                "kind": "marker",
                "x": 0.0,
                "y": -1.6,
                "radius": 0.35,
            },
        ],
        "staging": {
            "clear_title_before_formula": True,
            "simultaneous_decoys": 2,
        },
        "camera": {
            "zoom_scale": 0.8,
            "center_x": 0.0,
            "center_y": -1.6,
        },
        "focus_beats": [
            {
                "beat_id": "detail",
                "timestamp": 5.0,
                "target_id": "focus_target",
                "intended_region": [-0.35, -0.35, 0.35, 0.35],
                "min_viewport_occupancy": 0.04,
                "max_viewport_occupancy": 0.45,
            }
        ],
    }


def render_scene_code(scene_name: str, spec: dict[str, JsonValue]) -> str:
    """Compile the small declarative fixture spec to complete Manim source."""

    objects = {item["id"]: item for item in spec["objects"]}  # type: ignore[index]
    title = objects["title"]
    formula = objects["formula"]
    target = objects["focus_target"]
    staging = spec["staging"]
    camera = spec["camera"]
    clear_title = bool(staging["clear_title_before_formula"])  # type: ignore[index]
    decoys = int(staging["simultaneous_decoys"])  # type: ignore[index]
    transition = "self.play(FadeOut(title))" if clear_title else "self.wait(0.2)"
    return (
        "from manim import *\n\n\n"
        f"class {scene_name}(MovingCameraScene):\n"
        "    def construct(self):\n"
        "        self.camera.background_color = \"#f3ecd8\"\n"
        f"        title = Text({title['text']!r}, color=\"#241a12\", "
        f"font_size={int(title['font_size'])})\n"
        f"        title.move_to([{float(title['x'])}, {float(title['y'])}, 0])\n"
        f"        formula = MathTex({formula['text']!r}, color=\"#241a12\")"
        f".scale({float(formula['scale'])})\n"
        f"        formula.move_to([{float(formula['x'])}, "
        f"{float(formula['y'])}, 0])\n"
        f"        target = Dot([{float(target['x'])}, {float(target['y'])}, 0], "
        f"radius={float(target['radius'])}, color=\"#b24c3d\")\n"
        f"        decoys = VGroup(*[Dot(color=\"#4f766f\").shift("
        f"RIGHT * ((i % 8) - 3.5) + DOWN * (1 + i // 8)) "
        f"for i in range({decoys})])\n"
        "        self.play(Write(title))\n"
        f"        {transition}\n"
        "        self.play(Write(formula), FadeIn(target), FadeIn(decoys))\n"
        "        self.play(self.camera.frame.animate"
        f".scale({float(camera['zoom_scale'])})"
        f".move_to([{float(camera['center_x'])}, "
        f"{float(camera['center_y'])}, 0]))\n"
        "        self.wait(1)\n"
    )


def _build_base_scenes() -> dict[str, BaseScene]:
    scenes: dict[str, BaseScene] = {}
    for index, (slug, title, prompt, concepts, formulas) in enumerate(
        _TOPICS,
        start=1,
    ):
        base_scene_id = f"scene_{index:02d}_{slug}"
        scene_name = "".join(part.title() for part in slug.split("_")) + "Scene"
        duration = 6.0 + (index % 7) * 0.75
        spec = _scene_spec(
            base_scene_id=base_scene_id,
            scene_name=scene_name,
            title=title,
            formula=formulas[0],
            duration_seconds=duration,
        )
        scenes[base_scene_id] = BaseScene(
            base_scene_id=base_scene_id,
            scene_name=scene_name,
            title=title,
            prompt=prompt,
            audience="secondary or early university learner",
            required_concepts=concepts,
            required_formulas=formulas,
            required_narrative_beats=(
                f"Introduce {title.lower()}",
                "Reveal the mathematical relation",
                "Focus the camera on the active detail",
            ),
            duration_seconds=duration,
            scene_spec=spec,
            code=render_scene_code(scene_name, spec),
            focus_beats=tuple(
                FocusBeat.model_validate(item)
                for item in spec["focus_beats"]  # type: ignore[index]
            ),
        )
    return scenes


BASE_SCENES = _build_base_scenes()


def mutable_scene_spec(scene: BaseScene) -> dict[str, JsonValue]:
    """Return a deep mutable copy suitable for a deterministic mutation."""

    return deepcopy(scene.scene_spec)


__all__ = [
    "BASE_SCENES",
    "BaseScene",
    "mutable_scene_spec",
    "render_scene_code",
]
