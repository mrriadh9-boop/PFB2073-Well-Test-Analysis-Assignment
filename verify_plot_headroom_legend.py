import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.welltest import analyze_problem1_drawdown, analyze_problem2_buildup, compute_type_curve

def check_plot_overlap():
    p1 = analyze_problem1_drawdown()
    p2 = analyze_problem2_buildup()

    # 1. Problem 1 Diagnostic Log-Log
    fig, ax = plt.subplots(figsize=(8.5, 6.5), dpi=300)
    ax.scatter(p1.df['time_hr'], p1.df['delta_p_psi'], color='navy', marker='o', s=35, label='Test $\Delta p$ (psi)')
    ax.scatter(p1.df['time_hr'], p1.df['bourdet_derivative'], color='darkred', marker='s', s=35, label="Test Bourdet Derivative $\Delta p'$ (psi)")
    t_min = max(p1.df['time_hr'].min(), 0.01)
    t_max = p1.df['time_hr'].max()
    t_dense = np.logspace(np.log10(t_min), np.log10(t_max), 200)
    t_D_dense = (0.0002637 * p1.type_curve.k * t_dense) / (p1.params.phi * p1.params.mu * p1.params.c_t * (p1.params.r_w**2))
    p_D_dense, dp_D_dense = compute_type_curve(t_D_dense, p1.type_curve.C_D, p1.type_curve.s)
    p_mult = (141.2 * p1.params.q * p1.params.B * p1.params.mu) / (p1.type_curve.k * p1.params.h)
    dp_model = p_mult * p_D_dense
    dp_prime_model = p_mult * dp_D_dense
    ax.plot(t_dense, dp_model, label='Model')
    ax.plot(t_dense, dp_prime_model, label='Model Derivative')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(bottom=ymin, top=ymax * 4.0)
    leg = ax.legend(loc='upper left', fontsize=10)
    fig.canvas.draw()
    
    inv = ax.transData.inverted()
    leg_bbox_display = leg.get_window_extent(fig.canvas.get_renderer())
    leg_bbox_data = inv.transform(leg_bbox_display)
    
    # In log scale, data bounds:
    x_leg_min, y_leg_min = leg_bbox_data[0]
    x_leg_max, y_leg_max = leg_bbox_data[1]

    # Check points inside legend
    p1_loglog_overlaps = []
    for x, y in zip(p1.df['time_hr'], p1.df['delta_p_psi']):
        if x_leg_min <= x <= x_leg_max and y_leg_min <= y <= y_leg_max:
            p1_loglog_overlaps.append(('dp_data', x, y))
    for x, y in zip(p1.df['time_hr'], p1.df['bourdet_derivative']):
        if x_leg_min <= x <= x_leg_max and y_leg_min <= y <= y_leg_max:
            p1_loglog_overlaps.append(('dp_prime_data', x, y))
    for x, y in zip(t_dense, dp_model):
        if x_leg_min <= x <= x_leg_max and y_leg_min <= y <= y_leg_max:
            p1_loglog_overlaps.append(('dp_model', x, y))
    for x, y in zip(t_dense, dp_prime_model):
        if x_leg_min <= x <= x_leg_max and y_leg_min <= y <= y_leg_max:
            p1_loglog_overlaps.append(('dp_prime_model', x, y))

    print("=== Problem 1 LogLog Diagnostic Legend Overlaps ===")
    print(f"Legend Data BBox: X=[{x_leg_min:.4f}, {x_leg_max:.4f}], Y=[{y_leg_min:.4f}, {y_leg_max:.4f}]")
    print(f"Overlapping points count: {len(p1_loglog_overlaps)}")

    # 2. Problem 1 SemiLog
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8.5, 6.5), dpi=300)
    ax.scatter(p1.df['time_hr'], p1.df['p_wf_psi'], label='Measured pwf')
    t_line = np.logspace(np.log10(t_min), np.log10(t_max), 100)
    pwf_fit = p1.semilog.intercept + p1.semilog.slope * np.log10(t_line)
    ax.plot(t_line, pwf_fit, label='MTR Line')
    ax.set_xscale('log')
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(bottom=ymin - 10.0, top=ymax + 150.0)
    leg = ax.legend(loc='upper left', fontsize=10)
    fig.canvas.draw()
    
    inv = ax.transData.inverted()
    leg_bbox_display = leg.get_window_extent(fig.canvas.get_renderer())
    leg_bbox_data = inv.transform(leg_bbox_display)
    x_leg_min, y_leg_min = leg_bbox_data[0]
    x_leg_max, y_leg_max = leg_bbox_data[1]

    p1_semilog_overlaps = []
    for x, y in zip(p1.df['time_hr'], p1.df['p_wf_psi']):
        if x_leg_min <= x <= x_leg_max and y_leg_min <= y <= y_leg_max:
            p1_semilog_overlaps.append(('pwf_data', x, y))
    for x, y in zip(t_line, pwf_fit):
        if x_leg_min <= x <= x_leg_max and y_leg_min <= y <= y_leg_max:
            p1_semilog_overlaps.append(('pwf_fit', x, y))

    print("\n=== Problem 1 SemiLog Legend Overlaps ===")
    print(f"Legend Data BBox: X=[{x_leg_min:.4f}, {x_leg_max:.4f}], Y=[{y_leg_min:.4f}, {y_leg_max:.4f}]")
    print(f"Overlapping points count: {len(p1_semilog_overlaps)}")
    if p1_semilog_overlaps:
        print("  Overlaps details:", p1_semilog_overlaps)

    # 3. Problem 2 Diagnostic Log-Log
    plt.close(fig)
    valid_df = p2.df[p2.df['delta_t_hr'] > 0].copy()
    fig, ax = plt.subplots(figsize=(8.5, 6.5), dpi=300)
    ax.scatter(valid_df['t_e_hr'], valid_df['delta_p_psi'], label='Test dp')
    ax.scatter(valid_df['t_e_hr'], valid_df['bourdet_derivative'], label='Test Bourdet')
    te_min = max(valid_df['t_e_hr'].min(), 0.01)
    te_max = valid_df['t_e_hr'].max()
    te_dense = np.logspace(np.log10(te_min), np.log10(te_max), 200)
    t_D_dense = (0.0002637 * p2.type_curve.k * te_dense) / (p2.params.phi * p2.params.mu * p2.params.c_t * (p2.params.r_w**2))
    p_D_dense, dp_D_dense = compute_type_curve(t_D_dense, p2.type_curve.C_D, p2.type_curve.s)
    p_mult = (141.2 * p2.params.q * p2.params.B * p2.params.mu) / (p2.type_curve.k * p2.params.h)
    dp_model = p_mult * p_D_dense
    dp_prime_model = p_mult * dp_D_dense
    ax.plot(te_dense, dp_model, label='Model dp')
    ax.plot(te_dense, dp_prime_model, label='Model dp_prime')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(bottom=ymin, top=ymax * 4.0)
    leg = ax.legend(loc='upper left', fontsize=10)
    fig.canvas.draw()

    inv = ax.transData.inverted()
    leg_bbox_display = leg.get_window_extent(fig.canvas.get_renderer())
    leg_bbox_data = inv.transform(leg_bbox_display)
    x_leg_min, y_leg_min = leg_bbox_data[0]
    x_leg_max, y_leg_max = leg_bbox_data[1]

    p2_loglog_overlaps = []
    for x, y in zip(valid_df['t_e_hr'], valid_df['delta_p_psi']):
        if x_leg_min <= x <= x_leg_max and y_leg_min <= y <= y_leg_max:
            p2_loglog_overlaps.append(('dp_data', x, y))
    for x, y in zip(valid_df['t_e_hr'], valid_df['bourdet_derivative']):
        if x_leg_min <= x <= x_leg_max and y_leg_min <= y <= y_leg_max:
            p2_loglog_overlaps.append(('dp_prime_data', x, y))
    for x, y in zip(te_dense, dp_model):
        if x_leg_min <= x <= x_leg_max and y_leg_min <= y <= y_leg_max:
            p2_loglog_overlaps.append(('dp_model', x, y))
    for x, y in zip(te_dense, dp_prime_model):
        if x_leg_min <= x <= x_leg_max and y_leg_min <= y <= y_leg_max:
            p2_loglog_overlaps.append(('dp_prime_model', x, y))

    print("\n=== Problem 2 LogLog Diagnostic Legend Overlaps ===")
    print(f"Legend Data BBox: X=[{x_leg_min:.4f}, {x_leg_max:.4f}], Y=[{y_leg_min:.4f}, {y_leg_max:.4f}]")
    print(f"Overlapping points count: {len(p2_loglog_overlaps)}")

    # 4. Problem 2 Horner
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8.5, 6.5), dpi=300)
    ax.scatter(valid_df['horner_ratio'], valid_df['p_ws_psi'], label='Measured pws')
    hr_min = 1.0
    hr_max = valid_df['horner_ratio'].max()
    hr_line = np.logspace(np.log10(hr_min), np.log10(hr_max), 100)
    pws_fit = p2.semilog.intercept + p2.semilog.slope * np.log10(hr_line)
    ax.plot(hr_line, pws_fit, label='Horner MTR Line')
    ax.set_xscale('log')
    ax.invert_xaxis()
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(bottom=ymin - 10.0, top=ymax + 50.0)
    leg = ax.legend(loc='upper left', fontsize=10)
    fig.canvas.draw()

    inv = ax.transData.inverted()
    leg_bbox_display = leg.get_window_extent(fig.canvas.get_renderer())
    leg_bbox_data = inv.transform(leg_bbox_display)
    # Inverted x axis means leg_bbox_data[0][0] might be larger than leg_bbox_data[1][0]
    x1, y1 = leg_bbox_data[0]
    x2, y2 = leg_bbox_data[1]
    x_leg_min, x_leg_max = min(x1, x2), max(x1, x2)
    y_leg_min, y_leg_max = min(y1, y2), max(y1, y2)

    p2_horner_overlaps = []
    for x, y in zip(valid_df['horner_ratio'], valid_df['p_ws_psi']):
        if x_leg_min <= x <= x_leg_max and y_leg_min <= y <= y_leg_max:
            p2_horner_overlaps.append(('pws_data', x, y))
    for x, y in zip(hr_line, pws_fit):
        if x_leg_min <= x <= x_leg_max and y_leg_min <= y <= y_leg_max:
            p2_horner_overlaps.append(('pws_fit', x, y))

    print("\n=== Problem 2 Horner Legend Overlaps ===")
    print(f"Legend Data BBox: X=[{x_leg_min:.4f}, {x_leg_max:.4f}], Y=[{y_leg_min:.4f}, {y_leg_max:.4f}]")
    print(f"Overlapping points count: {len(p2_horner_overlaps)}")
    if p2_horner_overlaps:
        print("  Overlaps details:", p2_horner_overlaps)

if __name__ == '__main__':
    check_plot_overlap()
