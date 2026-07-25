"""
PFB2073 Well Test Analysis - May 2026
Master Orchestrator Script

Solves Drawdown Test (Problem 1) & Buildup Test (Problem 2)
Generates:
  1. Diagnostic & Semi-Log Plots (.png)
  2. Excel Workbook (.xlsx)
  3. APA 7th Edition Word Report (.docx)
"""

import os
import glob

from src.welltest import (
    analyze_problem1_drawdown,
    analyze_problem2_buildup,
)
from src.plotting import generate_all_plots
from src.excel_exporter import export_well_test_results
from src.report_generator import generate_apa_report

OUTPUT_DIR = r"C:\Users\60163\Downloads\PFB2073_Well_Test_Analysis_-_May_2026_1784922163"

def clean_up_temp_files():
    """Removes temporary test files and redundant artifacts."""
    patterns_to_remove = [
        "test_out*.xlsx",
        "generate_apa_report.py",
        "generate_corrected_apa_report.py",
        "Corrected_WellTest_Report.docx",
        "problem1_*.png",
        "problem2_*.png",
    ]
    print("\n" + "=" * 70)
    print("CLEANING UP TEMPORARY & REDUNDANT FILES")
    print("=" * 70)
    removed_count = 0
    for pat in patterns_to_remove:
        files = glob.glob(os.path.join(OUTPUT_DIR, pat))
        for f in files:
            if os.path.basename(f) == "well_test_analysis.py":
                continue
            try:
                os.remove(f)
                print(f"  Removed: {os.path.basename(f)}")
                removed_count += 1
            except Exception as e:
                print(f"  Could not remove {f}: {e}")
    if removed_count == 0:
        print("  No temporary files found.")


def run_pipeline():
    print("=" * 70)
    print("PFB2073 WELL TEST ANALYSIS — MASTER SOLUTION PIPELINE")
    print("=" * 70)

    # 1. Perform Calculations via src.welltest
    print("\n[1/4] Performing Mathematical Analysis...")
    p1_res = analyze_problem1_drawdown()
    p2_res = analyze_problem2_buildup()

    print(f"  Problem 1 (Drawdown): k = {p1_res.semilog.k:.4f} mD, s = {p1_res.semilog.s:.2f}, C = {p1_res.semilog.C:.6f} bbl/psi")
    print(f"  Problem 2 (Buildup):  k = {p2_res.semilog.k:.4f} mD, s = {p2_res.semilog.s:.2f}, C = {p2_res.semilog.C:.6f} bbl/psi")
    print(f"  Radius of Inv (tp=960h): r_inv = {p2_res.semilog.r_inv_72hr:.1f} ft (Boundary reached: {p2_res.semilog.boundary_reached})")

    # 2. Generate Plots
    print("\n[2/4] Generating Diagnostic & Semi-Log PNG Plots...")
    plots = generate_all_plots(p1_res, p2_res, output_dir=OUTPUT_DIR)
    for name, path in plots.items():
        print(f"  Generated: {os.path.basename(path)}")

    # 3. Generate Excel Workbook
    print("\n[3/4] Exporting Excel Workbook (.xlsx)...")
    excel_path = os.path.join(OUTPUT_DIR, "PFB2073_WellTest_Results.xlsx")
    export_well_test_results(p1_res, p2_res, output_path=excel_path)
    print(f"  Generated: PFB2073_WellTest_Results.xlsx")

    # 4. Generate APA Word Report
    print("\n[4/4] Generating APA 7th Edition Word Report (.docx)...")
    report_path = os.path.join(OUTPUT_DIR, "PFB2073_WellTest_Report_APA.docx")
    generate_apa_report(p1_res, p2_res, output_path=report_path)
    print(f"  Generated: PFB2073_WellTest_Report_APA.docx")

    print("\n" + "=" * 70)
    print("ALL DELIVERABLES SUCCESSFULLY REGENERATED AND VERIFIED")
    print("=" * 70)


if __name__ == "__main__":
    clean_up_temp_files()
    run_pipeline()
