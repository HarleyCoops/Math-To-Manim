"""The mathematics shown in examples/mythos/pole_survives_the_mix.py.

Every number the film puts on screen is checked here: the symbol
m(s) = (1 - q)(2q - 1) with q = 2^(-s), its value at the first zeta zero,
the floor on vertical lines, the zeros on the two walls, the three arrows,
and the eigen-relation of the mix on a tone. The scene module needs Manim,
so these tests skip without it.
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("manim")

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "examples" / "mythos" / "pole_survives_the_mix.py"
FILM = ROOT / "docs" / "showcase" / "pole-survives-the-mix"


@pytest.fixture(scope="module")
def film():
    spec = importlib.util.spec_from_file_location("pole_survives_the_mix", SCENE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_symbol_is_the_three_weighted_delays(film):
    rng = np.random.default_rng(3)
    s = rng.uniform(-1, 2, 50) + 1j * rng.uniform(-30, 30, 50)
    q = film.q_of(s)
    assert np.allclose(film.m_of(s), -1 + 3 * q - 2 * q ** 2)
    assert np.allclose(q, 2.0 ** (-s))
    assert np.allclose(np.abs(q), 2.0 ** (-s.real))


def test_values_at_the_first_zeta_zero(film):
    assert film.RHO == complex(0.5, 14.134725141734693)
    assert abs(film.Q_RHO - complex(-0.658571, 0.257458)) < 1e-6
    assert abs(abs(film.Q_RHO) - 2 ** -0.5) < 1e-12
    assert abs(np.degrees(np.angle(film.Q_RHO)) - 158.648) < 1e-3   # "159 degrees"
    assert abs(film.M_RHO - complex(-3.710574, 1.450591)) < 1e-6
    assert abs(abs(film.M_RHO) - 3.984040) < 1e-6                    # "3.98", "3.984"


def test_the_three_arrows_end_at_m_rho(film):
    q = film.Q_RHO
    assert abs((-1 + 3 * q - 2 * q ** 2) - film.M_RHO) < 1e-12
    # the tone has phase 0 at U0, so the reference arrow points along +Re
    assert abs(np.exp(1j * film.GAMMA1 * film.U0) - 1) < 1e-9


def test_floor_on_vertical_lines(film):
    assert abs(film.floor_of(0.5) - (3 / np.sqrt(2) - 2)) < 1e-12   # "0.121"
    assert abs(film.floor_of(np.log2(4 / 3)) - 0.125) < 1e-12        # the largest floor
    for sigma in np.linspace(0.01, 0.99, 50):
        t = np.linspace(0, 40, 4001)
        size = np.abs(film.m_of(sigma + 1j * t))
        assert size.min() >= film.floor_of(sigma) - 1e-12
        assert size.min() > 0


def test_zeros_sit_on_the_walls_only(film):
    assert abs(film.PERIOD - 9.064720) < 1e-6                         # "9.06"
    for k in range(-2, 4):
        assert abs(film.m_of(1j * k * film.PERIOD)) < 1e-12
        assert abs(film.m_of(1 + 1j * k * film.PERIOD)) < 1e-12
    sigma, t = np.meshgrid(np.linspace(0.02, 0.98, 49), np.linspace(-5, 45, 2001))
    assert np.abs(film.m_of(sigma + 1j * t)).min() > 0.006


def test_the_mix_returns_the_tone_times_m_rho(film):
    """The three weighted, delayed helices add up to the ivory helix."""
    c = np.zeros(3)
    base = film.helix_points(c, 0.0, 1.0)
    total = (-(film.helix_points(c, 0.0, 1.0) - [0, 0, film.HZ])
             + 3 * (film.helix_points(c, film.LOG2, 1.0) - [0, 0, film.HZ])
             - 2 * (film.helix_points(c, 2 * film.LOG2, 1.0) - [0, 0, film.HZ]))
    mixed = film.helix_points(c, 0.0, film.M_RHO) - [0, 0, film.HZ]
    u = (base[:, 0] - film.HX0) / film.HXS
    started = u > 2 * film.LOG2 + 1e-9
    # x is not a value of the tone: compare the (Re, Im) columns
    assert np.allclose(total[started, 1:], mixed[started, 1:], atol=1e-9)


def test_the_lane_curve_is_the_stated_mix(film):
    u = np.linspace(0, film.U_MAX, 320)
    expected = (-film.g_delayed(u, 0.0) + 3 * film.g_delayed(u, film.LOG2)
                - 2 * film.g_delayed(u, 2 * film.LOG2))
    assert np.allclose(film.mix_points()[:, 2], expected)
    assert film.g_fun(0.0) == 0.0            # delayed copies start without a jump
    assert np.all(film.g_delayed(u, film.LOG2)[u <= film.LOG2] == 0)


def test_tent_identity():
    """(4/t-1)+ - 3(2/t-1)+ + 2(1/t-1)+ is the tent on (1, 4)."""
    t = np.linspace(0.05, 6, 2000)
    ramp = lambda x: np.maximum(x - 1, 0)
    tent = np.where(t <= 1, 0, np.where(t <= 2, 2 * (1 - 1 / t), np.where(t < 4, 4 / t - 1, 0)))
    assert np.allclose(ramp(4 / t) - 3 * ramp(2 / t) + 2 * ramp(1 / t), tent)


def test_captions_have_at_most_fourteen_words():
    source = SCENE.read_text(encoding="utf-8")
    captions = re.findall(r'"([A-Z][^"\\]{20,}[.?])"', source)
    assert len(captions) >= 40
    assert [c for c in captions if len(c.split()) > 14] == []


def test_the_committed_stage_replies_replay_through_the_harness(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "operate_mythos_chain", ROOT / "scripts" / "operate_mythos_chain.py")
    op = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(op)
    stages = tmp_path / "stages"
    stages.mkdir()
    shutil.copy(FILM / "prompt.txt", stages / "prompt.txt")
    for path in sorted(FILM.glob("0[1-6]_*.json")):
        shutil.copy(path, stages / path.name)
    shutil.copy(SCENE, stages / "mythos_scene.py")
    rc, run_dir = op.operate(stages, runs_dir=tmp_path / "runs")
    assert rc == 0
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["static_check"]["passed"] is True
    shots = json.loads((run_dir / "05_shot_list.json").read_text(encoding="utf-8"))["shots"]
    assert sum(s["verb"] == "ZOOM_IN" for s in shots) <= sum(
        s["verb"] in {"PULL_BACK", "BEAT", "TILT_3D"} for s in shots)


def test_the_committed_companions_pass_their_static_checks():
    from mythos.companions import check_lean_source, check_paper_source

    assert check_paper_source((FILM / "paper.tex").read_text(encoding="utf-8")) == []
    lean = (FILM / "DelayedPoleSurvival.lean").read_text(encoding="utf-8")
    assert check_lean_source(lean) == []
    for name in ("symbol_ne_zero", "symbol_norm_lower", "laplace_mix", "pole_survives_mix",
                 "mix_poleData", "tent_eq"):
        assert f"theorem {name}" in lean
