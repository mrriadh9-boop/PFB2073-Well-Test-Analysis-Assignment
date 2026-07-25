"""
src/plotting.py
----------------
Visualization engine for Petroleum Engineering Well Test Analysis.
Generates log-log diagnostic plots with Bourdet derivative and fitted analytical
type curves, as well as semi-log / Horner analysis plots for Drawdown (Problem 1)
and Buildup (Problem 2).
"""

import os
from typing import Dict, Optional, Any
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt

from src.welltest import (
    Problem1AnalysisResult,
    Problem2AnalysisResult,
    analyze_problem1_drawdown,
    analyze_problem2_buildup,
    compute_type_curve,
)


def plot_drawdown_diagnostic(
    res: Optional[Problem1AnalysisResult] = None,
    save_path: str = "problem1_loglog_diagnostic.png"
) -> str:
    """
    Generates Log-Log diagnostic plot for Problem 1 Drawdown test pressure change
    dp and Bourdet derivative dp', along with fitted analytical model curves.

    Parameters:
        res       : Problem1AnalysisResult object. If None, analyzed automatically.
        save_path : File path to save the output PNG plot.

    Returns:
        str: Absolute or relative path to saved image file.
    """
    if res is None:
        res = analyze_problem1_drawdown()

    params = res.params
    df = res.df
    tc = res.type_curve

    fig, ax = plt.subplots(figsize=(8.5, 6.5), dpi=300)

    # Test observation points
    ax.scatter(
        df['time_hr'], df['delta_p_psi'],
        color='navy', marker='o', s=35, label='Test $\\Delta p$ (psi)', zorder=3
    )
    ax.scatter(
        df['time_hr'], df['bourdet_derivative'],
        color='darkred', marker='s', s=35, label="Test Bourdet Derivative $\\Delta p'$ (psi)", zorder=3
    )

    # Dense time grid for smooth analytical model curve
    t_min = max(df['time_hr'].min(), 0.01)
    t_max = df['time_hr'].max()
    t_dense = np.logspace(np.log10(t_min), np.log10(t_max), 200)

    t_D_dense = (0.0002637 * tc.k * t_dense) / (params.phi * params.mu * params.c_t * (params.r_w**2))
    p_D_dense, dp_D_dense = compute_type_curve(t_D_dense, tc.C_D, tc.s)

    p_mult = (141.2 * params.q * params.B * params.mu) / (tc.k * params.h)
    dp_model = p_mult * p_D_dense
    dp_prime_model = p_mult * dp_D_dense

    ax.plot(
        t_dense, dp_model,
        color='blue', linestyle='-', linewidth=2.0,
        label=f'Model $\\Delta p$ ($k={tc.k:.2f}$ md, $s={tc.s:.2f}$, $C={tc.C:.4f}$ bbl/psi)', zorder=2
    )
    ax.plot(
        t_dense, dp_prime_model,
        color='red', linestyle='--', linewidth=2.0,
        label="Model Derivative $\\Delta p'$", zorder=2
    )

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Time t (hr)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Pressure Change & Derivative (psi)', fontsize=12, fontweight='bold')
    ax.set_title('Problem 1: Drawdown Log-Log Diagnostic Plot', fontsize=14, fontweight='bold', pad=12)

    ax.grid(True, which='major', linestyle='-', color='gray', alpha=0.5)
    ax.grid(True, which='minor', linestyle=':', color='lightgray', alpha=0.5)
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(bottom=ymin, top=ymax * 4.0)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.95, facecolor='white', edgecolor='gray')

    plt.tight_layout()
    dirname = os.path.dirname(save_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    fig.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    return save_path


def plot_drawdown_semilog(
    res: Optional[Problem1AnalysisResult] = None,
    save_path: str = "problem1_semilog.png"
) -> str:
    """
    Generates semi-log plot (pwf vs log t) for Problem 1 Drawdown with MTR straight line fit.

    Parameters:
        res       : Problem1AnalysisResult object. If None, analyzed automatically.
        save_path : File path to save the output PNG plot.

    Returns:
        str: Absolute or relative path to saved image file.
    """
    if res is None:
        res = analyze_problem1_drawdown()

    df = res.df
    semilog = res.semilog

    fig, ax = plt.subplots(figsize=(8.5, 6.5), dpi=300)

    # Measured flowing bottomhole pressure
    ax.scatter(
        df['time_hr'], df['p_wf_psi'],
        color='navy', marker='o', s=40, label='Measured $p_{wf}$ (psia)', zorder=3
    )

    # MTR straight line extrapolation
    t_min = df['time_hr'].min()
    t_max = df['time_hr'].max()
    t_line = np.logspace(np.log10(t_min), np.log10(t_max), 100)
    pwf_fit = semilog.intercept + semilog.slope * np.log10(t_line)

    label_str = (
        f'MTR Straight Line ($m={semilog.m:.2f}$ psi/cycle,\n'
        f'$k={semilog.k:.2f}$ md, $s={semilog.s:.2f}$, $p_{{1hr}}={semilog.p_1hr:.1f}$ psia)'
    )
    ax.plot(t_line, pwf_fit, color='red', linestyle='--', linewidth=2.0, label=label_str, zorder=2)

    # Highlight MTR region points used for fitting
    mtr_df = df[(df['time_hr'] >= semilog.mtr_start_time) & (df['time_hr'] <= semilog.mtr_end_time)]
    ax.scatter(
        mtr_df['time_hr'], mtr_df['p_wf_psi'],
        color='gold', edgecolor='black', marker='o', s=60, label='MTR Fitting Region', zorder=4
    )

    ax.set_xscale('log')
    ax.set_xlabel('Time t (hr)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Wellbore Flowing Pressure $p_{wf}$ (psi)', fontsize=12, fontweight='bold')
    ax.set_title('Problem 1: Drawdown Semi-Log Analysis ($p_{wf}$ vs log t)', fontsize=14, fontweight='bold', pad=12)

    ax.grid(True, which='major', linestyle='-', color='gray', alpha=0.5)
    ax.grid(True, which='minor', linestyle=':', color='lightgray', alpha=0.5)
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(bottom=ymin - 10.0, top=ymax + 150.0)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.95, facecolor='white', edgecolor='gray')

    plt.tight_layout()
    dirname = os.path.dirname(save_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    fig.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    return save_path


def plot_buildup_diagnostic(
    res: Optional[Problem2AnalysisResult] = None,
    save_path: str = "problem2_loglog_diagnostic.png"
) -> str:
    """
    Generates Log-Log diagnostic plot for Problem 2 Buildup (te vs dp and Bourdet derivative),
    with test points and fitted analytical model curves.

    Parameters:
        res       : Problem2AnalysisResult object. If None, analyzed automatically.
        save_path : File path to save the output PNG plot.

    Returns:
        str: Absolute or relative path to saved image file.
    """
    if res is None:
        res = analyze_problem2_buildup()

    params = res.params
    df = res.df
    tc = res.type_curve

    valid_df = df[df['delta_t_hr'] > 0].copy()
    if valid_df.empty:
        valid_df = df.copy()

    fig, ax = plt.subplots(figsize=(8.5, 6.5), dpi=300)

    # Test observation points against Agarwal equivalent time t_e
    ax.scatter(
        valid_df['t_e_hr'], valid_df['delta_p_psi'],
        color='navy', marker='o', s=35, label='Test $\\Delta p$ (psi)', zorder=3
    )
    ax.scatter(
        valid_df['t_e_hr'], valid_df['bourdet_derivative'],
        color='darkred', marker='s', s=35, label="Test Bourdet Derivative $\\Delta p'$ (psi)", zorder=3
    )

    # Dense t_e grid for model curves
    te_min = max(valid_df['t_e_hr'].min(), 0.01)
    te_max = valid_df['t_e_hr'].max()
    te_dense = np.logspace(np.log10(te_min), np.log10(te_max), 200)

    t_D_dense = (0.0002637 * tc.k * te_dense) / (params.phi * params.mu * params.c_t * (params.r_w**2))
    p_D_dense, dp_D_dense = compute_type_curve(t_D_dense, tc.C_D, tc.s)

    p_mult = (141.2 * params.q * params.B * params.mu) / (tc.k * params.h)
    dp_model = p_mult * p_D_dense
    dp_prime_model = p_mult * dp_D_dense

    ax.plot(
        te_dense, dp_model,
        color='blue', linestyle='-', linewidth=2.0,
        label=f'Model $\\Delta p$ ($k={tc.k:.2f}$ md, $s={tc.s:.2f}$, $C={tc.C:.4f}$ bbl/psi)', zorder=2
    )
    ax.plot(
        te_dense, dp_prime_model,
        color='red', linestyle='--', linewidth=2.0,
        label="Model Derivative $\\Delta p'$", zorder=2
    )

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Agarwal Equivalent Time $t_e$ (hr)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Pressure Change & Derivative (psi)', fontsize=12, fontweight='bold')
    ax.set_title('Problem 2: Buildup Log-Log Diagnostic Plot', fontsize=14, fontweight='bold', pad=12)

    ax.grid(True, which='major', linestyle='-', color='gray', alpha=0.5)
    ax.grid(True, which='minor', linestyle=':', color='lightgray', alpha=0.5)
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(bottom=ymin, top=ymax * 4.0)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.95, facecolor='white', edgecolor='gray')

    plt.tight_layout()
    dirname = os.path.dirname(save_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    fig.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    return save_path


def plot_buildup_horner(
    res: Optional[Problem2AnalysisResult] = None,
    save_path: str = "problem2_semilog.png"
) -> str:
    """
    Generates Horner plot (pws vs Horner time ratio) for Problem 2 Buildup with MTR straight line fit.

    Parameters:
        res       : Problem2AnalysisResult object. If None, analyzed automatically.
        save_path : File path to save the output PNG plot.

    Returns:
        str: Absolute or relative path to saved image file.
    """
    if res is None:
        res = analyze_problem2_buildup()

    df = res.df
    semilog = res.semilog

    valid_df = df[df['delta_t_hr'] > 0].copy()
    if valid_df.empty:
        valid_df = df.copy()

    fig, ax = plt.subplots(figsize=(8.5, 6.5), dpi=300)

    # Measured shut-in pressure vs Horner ratio
    ax.scatter(
        valid_df['horner_ratio'], valid_df['p_ws_psi'],
        color='navy', marker='o', s=40, label='Measured $p_{ws}$ (psia)', zorder=3
    )

    # MTR straight line fit across Horner ratio range down to 1.0 (extrapolated p*)
    hr_min = 1.0
    hr_max = valid_df['horner_ratio'].max()
    hr_line = np.logspace(np.log10(hr_min), np.log10(hr_max), 100)
    pws_fit = semilog.intercept + semilog.slope * np.log10(hr_line)

    label_str = (
        f'Horner MTR Line ($m={semilog.m:.2f}$ psi/cycle,\n'
        f'$p^*={semilog.p_star:.2f}$ psia, $k={semilog.k:.2f}$ md, $s={semilog.s:.2f}$)'
    )
    ax.plot(hr_line, pws_fit, color='red', linestyle='--', linewidth=2.0, label=label_str, zorder=2)

    # Highlight p* extrapolated point at Horner ratio = 1
    ax.scatter(
        [1.0], [semilog.p_star],
        color='crimson', marker='*', s=120, label=f'Extrapolated $p^* = {semilog.p_star:.2f}$ psia', zorder=5
    )

    # Highlight MTR fitting points
    mtr_df = valid_df[(valid_df['delta_t_hr'] >= semilog.mtr_start_dt) & (valid_df['delta_t_hr'] <= semilog.mtr_end_dt)]
    ax.scatter(
        mtr_df['horner_ratio'], mtr_df['p_ws_psi'],
        color='gold', edgecolor='black', marker='o', s=60, label='MTR Fitting Region', zorder=4
    )

    ax.set_xscale('log')
    ax.set_xlabel('Horner Time Ratio $(t_p + \\Delta t) / \\Delta t$', fontsize=12, fontweight='bold')
    ax.set_ylabel('Shut-in Pressure $p_{ws}$ (psi)', fontsize=12, fontweight='bold')
    ax.set_title('Problem 2: Buildup Horner Plot ($p_{ws}$ vs Horner Ratio)', fontsize=14, fontweight='bold', pad=12)

    # Invert x-axis so time progresses left to right (Horner ratio decreases towards 1)
    ax.invert_xaxis()

    ax.grid(True, which='major', linestyle='-', color='gray', alpha=0.5)
    ax.grid(True, which='minor', linestyle=':', color='lightgray', alpha=0.5)
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(bottom=ymin - 10.0, top=ymax + 50.0)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.95, facecolor='white', edgecolor='gray')

    plt.tight_layout()
    dirname = os.path.dirname(save_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    fig.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    return save_path


def generate_all_plots(
    p1_res: Optional[Problem1AnalysisResult] = None,
    p2_res: Optional[Problem2AnalysisResult] = None,
    output_dir: Optional[str] = None
) -> Dict[str, str]:
    """
    Wrapper function to execute all four diagnostic plot functions.

    Parameters:
        p1_res     : Problem1AnalysisResult object (optional).
        p2_res     : Problem2AnalysisResult object (optional).
        output_dir : Target directory to save diagnostic plot images (optional).

    Returns:
        Dict[str, str]: Dictionary mapping plot names to generated image file paths.
    """
    if p1_res is None:
        p1_res = analyze_problem1_drawdown()
    if p2_res is None:
        p2_res = analyze_problem2_buildup()

    def _path(filename: str) -> str:
        return os.path.join(output_dir, filename) if output_dir else filename

    p1_loglog = plot_drawdown_diagnostic(p1_res, _path("Problem1_LogLog_Diagnostic.png"))
    p1_semilog = plot_drawdown_semilog(p1_res, _path("Problem1_SemiLog.png"))
    p2_loglog = plot_buildup_diagnostic(p2_res, _path("Problem2_LogLog_Diagnostic.png"))
    p2_horner = plot_buildup_horner(p2_res, _path("Problem2_Horner.png"))

    return {
        "p1_loglog": p1_loglog,
        "p1_semilog": p1_semilog,
        "p2_loglog": p2_loglog,
        "p2_semilog": p2_horner,
        "p2_horner": p2_horner,
    }
