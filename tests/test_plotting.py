"""
tests/test_plotting.py
-----------------------
Unit tests for src/plotting.py visualization module.
Verifies that log-log diagnostic plots and semi-log/Horner plots for Drawdown
(Problem 1) and Buildup (Problem 2) execute without exceptions and generate
non-empty PNG files at expected paths.
"""

import os
import pytest
from src.welltest import analyze_problem1_drawdown, analyze_problem2_buildup
from src.plotting import (
    plot_drawdown_diagnostic,
    plot_drawdown_semilog,
    plot_buildup_diagnostic,
    plot_buildup_horner,
    generate_all_plots,
)


@pytest.fixture
def p1_result():
    return analyze_problem1_drawdown()


@pytest.fixture
def p2_result():
    return analyze_problem2_buildup()


def test_plot_drawdown_diagnostic(tmp_path, p1_result):
    save_file = str(tmp_path / "test_p1_loglog.png")
    result_path = plot_drawdown_diagnostic(p1_result, save_path=save_file)
    
    assert result_path == save_file
    assert os.path.exists(save_file)
    assert os.path.getsize(save_file) > 1000  # File is non-empty PNG


def test_plot_drawdown_semilog(tmp_path, p1_result):
    save_file = str(tmp_path / "test_p1_semilog.png")
    result_path = plot_drawdown_semilog(p1_result, save_path=save_file)

    assert result_path == save_file
    assert os.path.exists(save_file)
    assert os.path.getsize(save_file) > 1000  # File is non-empty PNG


def test_plot_buildup_diagnostic(tmp_path, p2_result):
    save_file = str(tmp_path / "test_p2_loglog.png")
    result_path = plot_buildup_diagnostic(p2_result, save_path=save_file)

    assert result_path == save_file
    assert os.path.exists(save_file)
    assert os.path.getsize(save_file) > 1000  # File is non-empty PNG


def test_plot_buildup_horner(tmp_path, p2_result):
    save_file = str(tmp_path / "test_p2_semilog.png")
    result_path = plot_buildup_horner(p2_result, save_path=save_file)

    assert result_path == save_file
    assert os.path.exists(save_file)
    assert os.path.getsize(save_file) > 1000  # File is non-empty PNG


def test_generate_all_plots(tmp_path, p1_result, p2_result):
    plot_dict = generate_all_plots(p1_result, p2_result, output_dir=str(tmp_path))

    assert isinstance(plot_dict, dict)
    expected_keys = {"p1_loglog", "p1_semilog", "p2_loglog", "p2_semilog"}
    assert expected_keys.issubset(plot_dict.keys())

    for key, file_path in plot_dict.items():
        assert os.path.exists(file_path), f"File for {key} does not exist: {file_path}"
        assert os.path.getsize(file_path) > 1000, f"File for {key} is empty: {file_path}"


def test_plot_nested_directory_creation(tmp_path, p1_result):
    nested_path = str(tmp_path / "nested" / "subfolder" / "p1_loglog.png")
    result_path = plot_drawdown_diagnostic(p1_result, save_path=nested_path)
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 1000


def test_plot_buildup_diagnostic_empty_valid_df_fallback(tmp_path, p2_result):
    import copy
    p2_modified = copy.deepcopy(p2_result)
    p2_modified.df['delta_t_hr'] = 0.0
    save_file = str(tmp_path / "test_p2_empty_valid_df.png")
    result_path = plot_buildup_diagnostic(p2_modified, save_path=save_file)
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 1000
