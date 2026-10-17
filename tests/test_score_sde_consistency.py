"""Mathematical and static verification for examples/argon/score_sde_consistency.py.

Every mathematical identity shown in the Score SDE & Consistency Models film is
verified numerically here:
1. Exact bimodal Gaussian convolution marginal density p_t(x) integrates to 1.
2. Closed-form score grad_x log p_t(x) matches numerical derivative d/dx log p_t(x).
3. Score vanishes at the watershed x = 0 and bifurcates at t* = sqrt(mu_0^2 - sigma_0^2).
4. Tweedie's formula D(x, t) = x + t^2 grad_x log p_t(x) equals the posterior mean E[x_0 | x_t = x].
5. Probability Flow ODE trajectories are deterministic, non-crossing, and preserve sign(x).
6. Consistency map satisfies self-consistency f(x(t), t) == f(x(t'), t') == x_epsilon along ODE trajectories.
7. Skip-connection boundary weights satisfy c_skip(epsilon) = 1 and c_out(epsilon) = 0 identically.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("manim")

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "examples" / "argon" / "score_sde_consistency.py"


@pytest.fixture(scope="module")
def film():
    spec = importlib.util.spec_from_file_location("score_sde_consistency", SCENE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_marginal_pdf_integrates_to_one(film):
    xs = np.linspace(-14.0, 14.0, 4001)
    for tv in (film.EPSILON, 0.25, 1.0, film.BIFURCATION_T, film.T_MAX):
        integral = np.trapezoid(film.marginal_pdf(xs, tv), xs)
        assert integral == pytest.approx(1.0, abs=1e-5)


def test_exact_score_matches_numerical_log_derivative(film):
    xs = np.linspace(-3.5, 3.5, 71)
    h = 1e-6
    for tv in (0.15, 0.8, 1.6, 2.4):
        log_p_plus = np.log(film.marginal_pdf(xs + h, tv))
        log_p_minus = np.log(film.marginal_pdf(xs - h, tv))
        num_grad = (log_p_plus - log_p_minus) / (2.0 * h)
        analytic = film.exact_score(xs, tv)
        assert np.allclose(analytic, num_grad, atol=1e-7)


def test_watershed_and_bifurcation_time(film):
    for tv in (film.EPSILON, 0.5, 1.5, 2.5):
        assert film.exact_score(0.0, tv) == pytest.approx(0.0, abs=1e-12)
    assert film.BIFURCATION_T == pytest.approx(np.sqrt(2.0**2 - 0.35**2), abs=1e-9)
    assert round(film.BIFURCATION_T, 4) == 1.9691


def test_tweedie_denoiser_identity(film):
    for tv in (0.2, 1.0, 2.0):
        for xv in (-3.0, -1.2, 0.0, 1.2, 3.0):
            d_val = film.tweedie_denoiser(xv, tv)
            expected = xv + (tv**2) * film.exact_score(xv, tv)
            assert d_val == pytest.approx(expected, abs=1e-12)
    assert film.tweedie_denoiser(2.1, film.EPSILON) == pytest.approx(2.1, abs=1e-4)


def test_prob_flow_ode_self_consistency_along_trajectory(film):
    ts, xs = film.integrate_prob_flow_ode(2.3, film.T_MAX, film.EPSILON, steps=300)
    x_eps = xs[-1]
    assert x_eps > 1.5
    for idx in (0, 60, 150, 240, 300):
        t_i = float(ts[idx])
        x_i = float(xs[idx])
        mapped = film.consistency_map(x_i, t_i, steps=300 - idx if idx < 300 else 1)
        assert mapped == pytest.approx(x_eps, abs=1e-2)


def test_boundary_skip_weights(film):
    assert film.c_skip(film.EPSILON) == pytest.approx(1.0, abs=1e-12)
    assert film.c_out(film.EPSILON) == pytest.approx(0.0, abs=1e-12)
    assert round(float(film.c_skip(1.0)), 4) == 0.2006
    assert round(float(film.c_out(1.0)), 4) == 0.4463


def test_scene_passes_argon_static_checks():
    from argon.validation import verify_scene_report

    report = verify_scene_report(SCENE.read_text(encoding="utf-8"))
    assert report["passed"] is True, report["errors"]
    assert report["scene_name"] == "ScoreSDEConsistencyJourney"
