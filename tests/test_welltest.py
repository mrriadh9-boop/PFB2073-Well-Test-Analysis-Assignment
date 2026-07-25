"""
tests/test_welltest.py
----------------------
Comprehensive unit test suite for src/welltest.py:
  - Bourdet derivative function output & edge cases
  - Semi-log analysis for Drawdown (Problem 1) and Buildup (Problem 2)
  - Analytical Gringarten/Bourdet type curve model & Stehfest Laplace inversion
  - Automated non-linear type curve matching convergence & parameter constraints (k > 0, C > 0)
  - Boundary radius evaluation r_inv at 72 hours & 80-acre 2x1 rectangle analysis
  - End-to-end wrapper functions analyze_problem1_drawdown() and analyze_problem2_buildup()
"""

import numpy as np
import pandas as pd
import pytest

from src.data import (
    get_drawdown_params,
    get_buildup_params,
    get_drawdown_dataframe,
    get_buildup_dataframe,
)
from src.welltest import (
    compute_bourdet_derivative,
    stehfest_weights,
    pD_laplace,
    compute_type_curve,
    analyze_drawdown_semilog,
    analyze_buildup_semilog,
    fit_drawdown_type_curve,
    fit_buildup_type_curve,
    analyze_problem1_drawdown,
    analyze_problem2_buildup,
    DrawdownSemilogResult,
    BuildupSemilogResult,
    TypeCurveMatchResult,
    Problem1AnalysisResult,
    Problem2AnalysisResult,
)


def test_compute_bourdet_derivative_synthetic_linear_log():
    """Verify Bourdet derivative on dp = A * ln(t) + B equals exact constant A."""
    t = np.logspace(-1, 2, 50)
    A = 42.0
    B = 100.0
    dp = A * np.log(t) + B

    # For L=0 (central diff) or small L, dp' = t * d(dp)/dt = A
    deriv = compute_bourdet_derivative(t, dp, L=0.05)
    np.testing.assert_allclose(deriv[5:-5], A, rtol=1e-2)


def test_compute_bourdet_derivative_edge_cases():
    """Verify Bourdet derivative handles zero, negative time, and small arrays safely."""
    # Short array
    assert len(compute_bourdet_derivative([1.0], [10.0])) == 1
    assert compute_bourdet_derivative([1.0], [10.0])[0] == 0.0

    # Zero or negative time
    t_bad = np.array([0.0, -1.0, 2.0, 5.0])
    dp_bad = np.array([0.0, 10.0, 20.0, 30.0])
    deriv = compute_bourdet_derivative(t_bad, dp_bad)
    assert len(deriv) == 4
    assert deriv[0] == 0.0
    assert deriv[1] == 0.0


def test_stehfest_weights_properties():
    """Verify Stehfest weighting coefficients computation and properties."""
    V8 = stehfest_weights(8)
    assert len(V8) == 8
    # Sum of Stehfest weights V_i for any N is theoretically 0
    assert pytest.approx(np.sum(V8), abs=1e-10) == 0.0

    # Non-even N should raise ValueError
    with pytest.raises(ValueError, match="even integer"):
        stehfest_weights(7)


def test_compute_type_curve_asymptotic_limits():
    """Verify Gringarten/Bourdet model asymptotic limits: unit slope early, 0.5 plateau late."""
    C_D = 100.0
    s = 2.0

    # Early time t_D = 1e-2 -> t_D / C_D = 1e-4 -> p_D ~ t_D/C_D = 1e-4, dp_D ~ 1e-4
    tD_early = np.array([1e-2])  # t_D / C_D = 1e-4
    pD_e, dpD_e = compute_type_curve(tD_early, C_D, s)
    assert pytest.approx(pD_e[0], rel=0.05) == 1e-4
    assert pytest.approx(dpD_e[0], rel=0.05) == 1e-4

    # Late time t_D = 1e6 -> t_D / C_D = 1e4 -> Bourdet derivative plateau ~ 0.5
    tD_late = np.array([1e6])  # t_D / C_D = 1e4
    pD_l, dpD_l = compute_type_curve(tD_late, C_D, s)
    assert pytest.approx(dpD_l[0], rel=0.02) == 0.5


def test_analyze_drawdown_semilog_values():
    """Verify Drawdown Problem 1 semi-log analysis output structure and physical accuracy."""
    res = analyze_drawdown_semilog()
    assert isinstance(res, DrawdownSemilogResult)

    # Physical parameter checks
    assert res.m == pytest.approx(133.26, abs=0.1)
    assert res.k == pytest.approx(14.16, abs=0.1)
    assert res.s == pytest.approx(2.51, abs=0.1)
    assert res.C_D == pytest.approx(111.6, abs=0.5)
    assert 1e-4 < res.C < 1e-2
    assert 400.0 < res.p_1hr < 700.0
    assert res.r2 > 0.99


def test_analyze_buildup_semilog_values():
    """Verify Buildup Problem 2 semi-log analysis output structure and physical accuracy."""
    res = analyze_buildup_semilog()
    assert isinstance(res, BuildupSemilogResult)

    # Physical parameter checks
    assert res.m == pytest.approx(30.29, abs=0.1)
    assert res.k == pytest.approx(30.12, abs=0.1) or res.k == pytest.approx(30.09, abs=0.1)
    assert res.s == pytest.approx(-1.86, abs=0.1)
    assert res.C_D == pytest.approx(351.3, abs=0.5)
    assert 1e-4 < res.C < 1e-2
    assert 1200.0 < res.p_1hr < 1300.0
    assert 1300.0 < res.p_star < 1400.0
    assert res.r2 > 0.99


def test_buildup_boundary_analysis_72hr():
    """Verify radius of investigation and boundary arrival evaluation for Problem 2 at t=72 hrs."""
    res = analyze_buildup_semilog()

    # Radius of investigation at 72 hours
    params = get_buildup_params()
    expected_r_inv = np.sqrt((res.k * 72.0) / (948.0 * params.phi * params.mu * params.c_t))
    assert pytest.approx(res.r_inv_72hr, rel=1e-5) == expected_r_inv

    # Boundary analysis for 80-acre 2x1 rectangle (d = 660 ft)
    assert res.nearest_boundary_ft == 660.0
    assert res.boundary_reached is False  # r_inv ~ 358.8 ft < 660 ft
    assert res.r_inv_72hr < 660.0

    # Time to reach boundary
    expected_t_b = (948.0 * params.phi * params.mu * params.c_t * (660.0**2)) / res.k
    assert pytest.approx(res.time_to_boundary_hr, rel=1e-5) == expected_t_b
    assert res.time_to_boundary_hr > 72.0


def test_fit_drawdown_type_curve_convergence_and_constraints():
    """Verify automated non-linear curve fitting for Problem 1 enforces k > 0, C > 0 and converges."""
    res = fit_drawdown_type_curve()
    assert isinstance(res, TypeCurveMatchResult)

    # Strict physical constraints
    assert res.k > 0
    assert res.C > 0
    assert res.C_D > 0
    assert res.C_D_e2s > 0

    # Realistic physical values for Problem 1
    assert 10.0 < res.k < 25.0
    assert 1.0 < res.s < 6.0
    assert 1e-4 < res.C < 1e-2
    assert res.r2_overall > 0.98

    # Predictions match array lengths (26 points)
    assert len(res.dp_pred) == 26
    assert len(res.dp_prime_pred) == 26


def test_fit_buildup_type_curve_convergence_and_constraints():
    """Verify automated non-linear curve fitting for Problem 2 enforces k > 0, C > 0 and converges."""
    res = fit_buildup_type_curve()
    assert isinstance(res, TypeCurveMatchResult)

    # Strict physical constraints
    assert res.k > 0
    assert res.C > 0
    assert res.C_D > 0
    assert res.C_D_e2s > 0

    # Realistic physical values for Problem 2
    assert 20.0 < res.k < 45.0
    assert -4.0 < res.s < 1.0
    assert 1e-4 < res.C < 1e-2
    assert res.r2_overall > 0.90

    # Predictions match valid shut-in points (32 points for dt > 0)
    assert len(res.dp_pred) == 32
    assert len(res.dp_prime_pred) == 32


def test_analyze_problem1_drawdown_wrapper():
    """Verify end-to-end wrapper function analyze_problem1_drawdown()."""
    res = analyze_problem1_drawdown()
    assert isinstance(res, Problem1AnalysisResult)
    assert isinstance(res.df, pd.DataFrame)
    assert 'bourdet_derivative' in res.df.columns
    assert len(res.df) == 26
    assert res.semilog.k > 0
    assert res.type_curve.k > 0


def test_analyze_problem2_buildup_wrapper():
    """Verify end-to-end wrapper function analyze_problem2_buildup()."""
    res = analyze_problem2_buildup()
    assert isinstance(res, Problem2AnalysisResult)
    assert isinstance(res.df, pd.DataFrame)
    assert 'bourdet_derivative' in res.df.columns
    assert len(res.df) == 33
    assert res.semilog.k > 0
    assert res.type_curve.k > 0
    assert res.semilog.boundary_reached is False


def test_type_curve_corrupted_pressure_drops_robustness():
    """Verify that zero, negative, or NaN pressure drop values do not crash fitting routines."""
    params_dd = get_drawdown_params()
    df_dd = get_drawdown_dataframe(params_dd)

    # 1. Zero pressure drop at t=0 or early time
    df_zero = df_dd.copy()
    df_zero.loc[0, 'delta_p_psi'] = 0.0
    res_zero = fit_drawdown_type_curve(df_zero, params_dd)
    assert np.isfinite(res_zero.k) and res_zero.k > 0
    assert np.isfinite(res_zero.C) and res_zero.C > 0

    # 2. Negative pressure drop in dataset
    df_neg = df_dd.copy()
    df_neg.loc[5, 'delta_p_psi'] = -15.0
    res_neg = fit_drawdown_type_curve(df_neg, params_dd)
    assert np.isfinite(res_neg.k) and res_neg.k > 0
    assert np.isfinite(res_neg.C) and res_neg.C > 0

    # 3. NaN pressure drop in dataset
    df_nan = df_dd.copy()
    df_nan.loc[10, 'delta_p_psi'] = np.nan
    res_nan = fit_drawdown_type_curve(df_nan, params_dd)
    assert np.isfinite(res_nan.k) and res_nan.k > 0
    assert np.isfinite(res_nan.C) and res_nan.C > 0

    # 4. Buildup test with zero, negative, and NaN delta_p
    params_bu = get_buildup_params()
    df_bu = get_buildup_dataframe(params_bu)

    df_bu_corrupt = df_bu.copy()
    df_bu_corrupt.loc[1, 'delta_p_psi'] = 0.0
    df_bu_corrupt.loc[8, 'delta_p_psi'] = -5.0
    df_bu_corrupt.loc[15, 'delta_p_psi'] = np.nan
    res_bu = fit_buildup_type_curve(df_bu_corrupt, params_bu)
    assert np.isfinite(res_bu.k) and res_bu.k > 0
    assert np.isfinite(res_bu.C) and res_bu.C > 0

