"""
tests/test_data.py
-------------------
Comprehensive unit test suite for src/data.py: parameter dataclasses,
DataFrame construction, calculation correctness, and validation functions.
"""

from dataclasses import FrozenInstanceError
import numpy as np
import pandas as pd
import pytest

from src.data import (
    DrawdownParameters,
    BuildupParameters,
    get_drawdown_params,
    get_buildup_params,
    get_drawdown_dataframe,
    get_buildup_dataframe,
    validate_drawdown_data,
    validate_buildup_data,
)


def test_drawdown_parameters_default_values_and_types():
    """Verify DrawdownParameters default parameter values, types, and immutability."""
    params = get_drawdown_params()
    assert isinstance(params, DrawdownParameters)
    assert params.q == 50.0
    assert params.p_i == 1326.6
    assert params.h == 25.0
    assert params.phi == 0.276
    assert params.r_w == 0.36
    assert params.B == 1.099
    assert params.c_t == 9.4e-6
    assert params.mu == 5.28

    # Verify frozen immutability
    with pytest.raises(FrozenInstanceError):
        params.q = 60.0


def test_buildup_parameters_default_values_and_types():
    """Verify BuildupParameters default parameter values, types, and immutability."""
    params = get_buildup_params()
    assert isinstance(params, BuildupParameters)
    assert params.q == 10.0
    assert params.p_i == 1192.45
    assert params.h == 10.0
    assert params.phi == 0.319
    assert params.r_w == 0.34
    assert params.B == 1.098
    assert params.c_t == 10.9e-6
    assert params.mu == 5.11
    assert params.t_p == 960.0
    assert params.A == 80.0

    # Verify frozen immutability
    with pytest.raises(FrozenInstanceError):
        params.t_p = 1000.0


def test_get_drawdown_dataframe_structure_and_values():
    """Verify get_drawdown_dataframe shape, column names, calculations, and exact values."""
    params = get_drawdown_params()
    df = get_drawdown_dataframe()

    # Shape and columns check
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (26, 3)
    assert list(df.columns) == ['time_hr', 'p_wf_psi', 'delta_p_psi']

    # Check first point
    assert df['time_hr'].iloc[0] == 0.100
    assert df['p_wf_psi'].iloc[0] == 1109.0
    assert pytest.approx(df['delta_p_psi'].iloc[0], rel=1e-6) == (1326.6 - 1109.0)
    assert pytest.approx(df['delta_p_psi'].iloc[0], rel=1e-6) == 217.60

    # Check last point (row 25)
    assert df['time_hr'].iloc[25] == 48.000
    assert df['p_wf_psi'].iloc[25] == 324.7
    assert pytest.approx(df['delta_p_psi'].iloc[25], rel=1e-6) == (1326.6 - 324.7)
    assert pytest.approx(df['delta_p_psi'].iloc[25], rel=1e-6) == 1001.90

    # Verify delta_p calculation across all rows
    expected_delta_p = params.p_i - df['p_wf_psi']
    np.testing.assert_allclose(df['delta_p_psi'].values, expected_delta_p.values)


def test_get_buildup_dataframe_structure_and_values():
    """Verify get_buildup_dataframe shape, columns, Agarwal time, Horner ratio, and delta_p."""
    params = get_buildup_params()
    df = get_buildup_dataframe()

    # Shape and columns check
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (33, 5)
    assert list(df.columns) == ['delta_t_hr', 'p_ws_psi', 't_e_hr', 'horner_ratio', 'delta_p_psi']

    # Index 0 check (dt = 0)
    assert df['delta_t_hr'].iloc[0] == 0.0
    assert df['p_ws_psi'].iloc[0] == 1192.45
    assert df['t_e_hr'].iloc[0] == 0.0
    assert np.isinf(df['horner_ratio'].iloc[0])
    assert df['delta_p_psi'].iloc[0] == 0.0

    # Index 1 check (dt = 0.05)
    dt1 = 0.05
    p_ws1 = 1206.92
    expected_te1 = (960.0 * dt1) / (960.0 + dt1)
    expected_horner1 = (960.0 + dt1) / dt1
    expected_dp1 = p_ws1 - 1192.45

    assert df['delta_t_hr'].iloc[1] == dt1
    assert df['p_ws_psi'].iloc[1] == p_ws1
    assert pytest.approx(df['t_e_hr'].iloc[1], rel=1e-6) == expected_te1
    assert pytest.approx(df['horner_ratio'].iloc[1], rel=1e-6) == expected_horner1
    assert pytest.approx(df['delta_p_psi'].iloc[1], rel=1e-6) == expected_dp1

    # Index 32 (last point, dt = 72.0)
    dt32 = 72.0
    p_ws32 = 1317.81
    expected_te32 = (960.0 * dt32) / (960.0 + dt32)
    expected_horner32 = (960.0 + dt32) / dt32
    expected_dp32 = p_ws32 - 1192.45

    assert df['delta_t_hr'].iloc[32] == dt32
    assert df['p_ws_psi'].iloc[32] == p_ws32
    assert pytest.approx(df['t_e_hr'].iloc[32], rel=1e-6) == expected_te32
    assert pytest.approx(df['horner_ratio'].iloc[32], rel=1e-6) == expected_horner32
    assert pytest.approx(df['delta_p_psi'].iloc[32], rel=1e-6) == expected_dp32


def test_validate_drawdown_data_success():
    """Verify validate_drawdown_data returns True for valid dataframe."""
    df = get_drawdown_dataframe()
    assert validate_drawdown_data(df) is True


def test_validate_drawdown_data_failures():
    """Verify validate_drawdown_data raises ValueError for invalid inputs."""
    df_valid = get_drawdown_dataframe()

    # Non-DataFrame input
    with pytest.raises(ValueError, match="must be a pandas DataFrame"):
        validate_drawdown_data("not_a_dataframe")

    # Missing column
    df_bad = df_valid.drop(columns=['delta_p_psi'])
    with pytest.raises(ValueError, match="Missing required drawdown columns"):
        validate_drawdown_data(df_bad)

    # Wrong row count
    df_bad = df_valid.iloc[:20]
    with pytest.raises(ValueError, match="Expected exactly 26 rows"):
        validate_drawdown_data(df_bad)

    # Contains NaN
    df_bad = df_valid.copy()
    df_bad.iloc[5, 1] = np.nan
    with pytest.raises(ValueError, match="contains NaN or null values"):
        validate_drawdown_data(df_bad)

    # Non-positive time
    df_bad = df_valid.copy()
    df_bad.iloc[0, 0] = 0.0
    with pytest.raises(ValueError, match="must be strictly positive"):
        validate_drawdown_data(df_bad)

    # Non-monotonic time
    df_bad = df_valid.copy()
    df_bad.iloc[5, 0] = df_bad.iloc[4, 0] - 0.1
    with pytest.raises(ValueError, match="must be strictly monotonic increasing"):
        validate_drawdown_data(df_bad)

    # Non-decreasing pressure
    df_bad = df_valid.copy()
    df_bad.iloc[5, 1] = df_bad.iloc[4, 1] + 10.0
    with pytest.raises(ValueError, match="must be strictly monotonic decreasing"):
        validate_drawdown_data(df_bad)

    # Non-positive delta_p
    df_bad = df_valid.copy()
    df_bad.iloc[10, 2] = -5.0
    with pytest.raises(ValueError, match="must be strictly positive"):
        validate_drawdown_data(df_bad)


def test_validate_buildup_data_success():
    """Verify validate_buildup_data returns True for valid dataframe."""
    df = get_buildup_dataframe()
    assert validate_buildup_data(df) is True


def test_validate_buildup_data_failures():
    """Verify validate_buildup_data raises ValueError for invalid inputs."""
    df_valid = get_buildup_dataframe()

    # Non-DataFrame input
    with pytest.raises(ValueError, match="must be a pandas DataFrame"):
        validate_buildup_data([1, 2, 3])

    # Missing column
    df_bad = df_valid.drop(columns=['t_e_hr'])
    with pytest.raises(ValueError, match="Missing required buildup columns"):
        validate_buildup_data(df_bad)

    # Wrong row count
    df_bad = df_valid.iloc[:30]
    with pytest.raises(ValueError, match="Expected exactly 33 rows"):
        validate_buildup_data(df_bad)

    # Contains NaN
    df_bad = df_valid.copy()
    df_bad.iloc[2, 3] = np.nan
    with pytest.raises(ValueError, match="contains NaN or null values"):
        validate_buildup_data(df_bad)

    # Negative time
    df_bad = df_valid.copy()
    df_bad.iloc[0, 0] = -1.0
    with pytest.raises(ValueError, match="must be non-negative"):
        validate_buildup_data(df_bad)

    # Non-monotonic shut-in time
    df_bad = df_valid.copy()
    df_bad.iloc[4, 0] = df_bad.iloc[3, 0] - 0.01
    with pytest.raises(ValueError, match="must be strictly monotonic increasing"):
        validate_buildup_data(df_bad)

    # Non-increasing shut-in pressure
    df_bad = df_valid.copy()
    df_bad.iloc[5, 1] = df_bad.iloc[4, 1] - 5.0
    with pytest.raises(ValueError, match="must be strictly monotonic increasing"):
        validate_buildup_data(df_bad)

    # Negative t_e_hr
    df_bad = df_valid.copy()
    df_bad.iloc[3, 2] = -0.5
    with pytest.raises(ValueError, match="must be non-negative"):
        validate_buildup_data(df_bad)

    # Non-zero delta_p at delta_t = 0
    df_bad = df_valid.copy()
    df_bad.iloc[0, 4] = 2.0
    with pytest.raises(ValueError, match="must start at 0.0"):
        validate_buildup_data(df_bad)

    # Non-positive delta_p for dt > 0
    df_bad = df_valid.copy()
    df_bad.iloc[10, 4] = -1.0
    with pytest.raises(ValueError, match="must be strictly positive for delta_t > 0"):
        validate_buildup_data(df_bad)


def test_custom_parameter_propagation():
    """Verify custom DrawdownParameters and BuildupParameters propagate to DataFrames."""
    custom_drawdown = DrawdownParameters(p_i=1500.0)
    df_dd = get_drawdown_dataframe(custom_drawdown)
    assert pytest.approx(df_dd['delta_p_psi'].iloc[0], rel=1e-6) == (1500.0 - 1109.0)

    custom_buildup = BuildupParameters(t_p=500.0)
    df_bu = get_buildup_dataframe(custom_buildup)
    dt1 = df_bu['delta_t_hr'].iloc[1]
    expected_te1 = (500.0 * dt1) / (500.0 + dt1)
    assert pytest.approx(df_bu['t_e_hr'].iloc[1], rel=1e-6) == expected_te1
