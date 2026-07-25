# Project: Petroleum Engineering Well Test Analysis Solution

## Architecture
Modular Python architecture for automated reservoir well test analysis, diagnostic plotting, Excel workbook generation, and APA 7th Edition report generation.

```
project_root/
├── src/
│   ├── data.py
│   ├── welltest.py
│   ├── plotting.py
│   ├── excel_exporter.py
│   └── doc_exporter.py
├── tests/
│   ├── test_data.py
│   ├── test_welltest.py
│   ├── test_plotting.py
│   └── test_excel_exporter.py
├── PFB2073_WellTest_Results.xlsx
├── PFB2073_WellTest_Analysis_Report.docx
└── *.png (diagnostic log-log and semi-log plots)
```

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Context Review & Data Setup | Inspect course notes, confirm formulas, parse datasets | none | DONE |
| 2 | Mathematical Analysis Engine | Bourdet derivative, Agarwal time, curve fitting for k, s, C | M1 | DONE |
| 3 | Visualizations & Excel Export | Diagnostic plots & formatted Excel workbook with plots | M2 | DONE |
| 4 | APA 7th Edition Document | Full academic .docx report with tables & figures | M3 | DONE |
| 5 | E2E Testing & Forensic Audit | Verification of criteria & code integrity audit | M4 | DONE |
| 6 | R1-R3 Dynamic APA 7th Update | Universal OMML (headings/body/tables), unit spacing, standalone figure/table pages | M5 | DONE |
| 7 | Final Verification & Audit | 39 unit/integration tests, stress tests, Forensic Audit CLEAN | M6 | DONE |

## Code Layout
- `src/data.py`: Raw dataset containers and unit conversions.
- `src/welltest.py`: Bourdet derivative, Agarwal time, semi-log analysis, analytical type curve models ($p_D, p_D'$), non-linear fitting engine.
- `src/plotting.py`: Matplotlib log-log and semi-log diagnostic plot generation (`loc='upper left'`, headroom scaling).
- `src/excel_exporter.py`: Openpyxl generator for `PFB2073_WellTest_Results.xlsx`.
- `src/report_generator.py`: Python-docx generator for APA 7th edition report `PFB2073_WellTest_Report_APA.docx` (dynamic binding, universal LaTeX to OMML, number-unit spacing pre-processor, horizontal borders only, running head, standalone figures/tables after References).
- `well_test_analysis.py`: Top-level CLI driver script running the end-to-end pipeline.

## Acceptance Criteria Checklist
- [x] Automated Python execution calculates $k > 0, s, C > 0$ for both problems without user intervention.
- [x] Type curve matching automated using non-linear curve fitting (`scipy.optimize`).
- [x] `PFB2073_WellTest_Results.xlsx` created with sheets "Problem 1 Drawdown" and "Problem 2 Buildup".
- [x] Excel file includes computed parameters ($k, s, C$) and embedded Log-Log plots.
- [x] `PFB2073_WellTest_Report_APA.docx` created adhering strictly to APA 7th edition style (running head, horizontal borders, LaTeX inline math units).
- [x] High-resolution diagnostic `.png` plot files generated with upper-left legends and 0 curve overlap.
- [x] R1 Universal LaTeX to OMML Equation Parsing across all headings (including Level 3 headings like `Dimensional Wellbore Storage ($C$)`), body paragraphs, and table cells.
- [x] R2 Dynamic Number-Unit Spacing Pre-Processor enforcing single space between numeric values and physical units (`660 ft`, `14.16 mD`, `1314 psia`, `0.001314 bbl/psi`, `72 hr`).
- [x] R3 APA 7th Edition Figure & Table Placement putting narrative callouts in Results and placing all tables and figures on individual separate pages after References.
- [x] All 39 pytest unit and integration tests passing cleanly.
- [x] Forensic Auditor integrity check CLEAN (100% dynamic calculation, zero hardcoding or facade implementations).

