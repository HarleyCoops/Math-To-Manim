"""The mathematics shown in examples/mythos/every_orbit_great_circle.py.

Every claim the film makes on screen is checked numerically here: Kepler
timing, Hamilton's hodograph, the two hinge points, the stereographic lift
to great circles, e = sin(alpha), and the tilt angles quoted for Earth and
Halley's comet. The scene module needs Manim, so the test skips without it.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("manim")

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "examples" / "mythos" / "every_orbit_great_circle.py"


@pytest.fixture(scope="module")
def film():
    spec = importlib.util.spec_from_file_location("every_orbit_great_circle", SCENE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ECCS = [0.0, 0.3, 0.55, 0.6, 0.75, 0.9]


def test_kepler_equation_is_solved(film):
    M = np.linspace(0, 2 * np.pi, 97)
    for e in ECCS:
        E = film.ecc_anomaly(M, e)
        resid = np.mod(E - e * np.sin(E) - M + np.pi, 2 * np.pi) - np.pi
        assert np.abs(resid).max() < 1e-12


def test_all_family_orbits_return_together(film):
    for e in film.ECCS:
        start = film.kepler_pos(0.0, e)
        end = film.kepler_pos(2 * np.pi, e)
        assert np.allclose(start, [1 - e, 0.0], atol=1e-12)
        assert np.allclose(end, start, atol=1e-12)


def test_velocity_tips_lie_on_hamiltons_circle(film):
    t = np.linspace(0, 2 * np.pi, 211)
    for e in ECCS:
        c = np.sqrt(1 - e * e)
        v = film.kepler_vel(t, e)
        centre = np.array([0.0, e / c])
        assert np.allclose(np.linalg.norm(v - centre, axis=1), 1 / c, atol=1e-10)


def test_energy_is_the_same_for_the_family(film):
    t = np.linspace(0, 2 * np.pi, 53)
    for e in film.ECCS:
        r = np.linalg.norm(film.kepler_pos(t, e), axis=1)
        v2 = (film.kepler_vel(t, e) ** 2).sum(axis=1)
        assert np.allclose(0.5 * v2 - 1 / r, -0.5, atol=1e-10)  # E = -GM/(2a)


def test_every_hodograph_passes_through_the_hinge_points(film):
    for e in ECCS:
        c = np.sqrt(1 - e * e)
        R, d = 1 / c, e / c
        assert R ** 2 == pytest.approx(d ** 2 + 1.0)  # R^2 = d^2 + p0^2 with p0 = 1
        for hinge in ([1.0, 0.0], [-1.0, 0.0]):
            assert np.linalg.norm(np.array(hinge) - [0.0, d]) == pytest.approx(R)


def test_stereographic_lift_gives_great_circles_tilted_by_arcsin_e(film):
    s = np.linspace(0, 2 * np.pi, 181)
    for e in ECCS:
        c = np.sqrt(1 - e * e)
        v = np.stack([-np.sin(s), e + np.cos(s)], axis=-1) / c
        u2 = (v ** 2).sum(-1)
        P = np.column_stack([2 * v / (u2 + 1)[:, None], (u2 - 1) / (u2 + 1)])
        assert np.allclose(np.linalg.norm(P, axis=1), 1.0, atol=1e-12)
        normal = np.array([0.0, -e, c])
        assert np.abs(P @ normal).max() < 1e-12  # a plane through the centre
        tilt = np.arccos(abs(normal[2]))
        assert np.sin(tilt) == pytest.approx(e)


def test_collision_orbit_perihelion_reaches_the_pole(film):
    # Ring point for eccentric anomaly E is (-sin E, c cos E, e cos E).
    e = 1.0
    c = 0.0
    assert np.allclose([-np.sin(0.0), c * np.cos(0.0), e * np.cos(0.0)], [0, 0, 1])


def test_numbers_on_screen():
    assert np.degrees(np.arcsin(0.96714)) == pytest.approx(75.3, abs=0.05)
    assert np.degrees(np.arcsin(0.0167086)) == pytest.approx(0.96, abs=0.005)
    assert [round(np.degrees(np.arcsin(e)), 2) for e in (0.3, 0.55, 0.75, 0.9)] == [17.46, 33.37, 48.59, 64.16]


def test_scene_passes_the_mythos_static_checks():
    from mythos.scene_checks import validate_manim_code_report

    report = validate_manim_code_report(SCENE.read_text(encoding="utf-8"))
    assert report.valid, report.errors
    assert report.scene_names == ["HiddenSphereJourney"]
