# PFB2073 / PEB3033 Well Test Analysis Assignment

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-39%20passed-success.svg)](tests/)
[![APA 7th Edition](https://img.shields.io/badge/report-APA%207th%20Edition-green.svg)](PFB2073_WellTest_Report_APA.docx)

Comprehensive automated reservoir well test analysis solution for petroleum engineering, featuring Bourdet pressure derivative calculation, Agarwal effective time transformation, non-linear type curve matching, high-resolution diagnostic plotting, formatted Excel workbook generation, and automated APA 7th Edition report generation.

---

## 📌 Executive Summary & Results

| Parameter | Symbol | Units | Problem 1 (Drawdown) | Problem 2 (Buildup) |
|---|---|---|---|---|
| **Permeability** | $k$ | mD | **14.16** | **23.50** |
| **Skin Factor** | $s$ | dimensionless | **+3.42** | **+5.18** |
| **Wellbore Storage** | $C$ | bbl/psi | **0.001314** | **0.008450** |
| **Initial / Extrapolated Pressure** | $p_i / p^*$ | psia | N/A | **3250.0** |

---

## 🏗️ Architecture & Code Layout

```
PFB2073-Well-Test-Analysis-Assignment/
├── src/
│   ├── data.py             # Dataset containers, validation & unit conversions
│   ├── welltest.py         # Bourdet derivative, Agarwal time, curve fitting engine
│   ├── plotting.py         # Matplotlib log-log diagnostic & semi-log plot generation
│   ├── excel_exporter.py   # Openpyxl generator for formatted Excel results workbook
│   └── report_generator.py # Python-docx generator for APA 7th Edition academic report
├── tests/
│   ├── test_data.py        # Unit tests for data loading and validation
│   ├── test_welltest.py    # Unit tests for mathematical engine & curve fitting
│   ├── test_plotting.py    # Unit tests for diagnostic plot generation
│   ├── test_excel_exporter.py # Unit tests for Excel workbook structure & images
│   └── test_report_generator.py # Unit tests for APA 7th report generation
├── well_test_analysis.py   # Top-level CLI driver script running E2E pipeline
├── PFB2073_WellTest_Results.xlsx   # Output Excel workbook with embedded plots
├── PFB2073_WellTest_Report_APA.docx # Output APA 7th Edition Word report
├── PFB2073_WellTest_Report_APA.pdf  # PDF export of final APA report
├── Problem1_LogLog_Diagnostic.png  # Diagnostic log-log plot for Problem 1
├── Problem1_SemiLog.png            # Semi-log plot for Problem 1
├── Problem2_LogLog_Diagnostic.png  # Diagnostic log-log plot for Problem 2
├── Problem2_Horner.png             # Horner plot for Problem 2
├── PROJECT.md              # Project specifications and milestone status
├── README.md               # Repository documentation
└── .gitignore              # Python gitignore
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Dependencies: `numpy`, `scipy`, `matplotlib`, `pandas`, `openpyxl`, `python-docx`, `pytest`

### Installation
```bash
pip install numpy scipy matplotlib pandas openpyxl python-docx pytest
```

### Running the Analysis
To run the full automated analysis and regenerate all plots, Excel workbooks, and report documents:
```bash
python well_test_analysis.py
```

### Running Tests
To run the 39 unit and integration tests:
```bash
python -m pytest -v
```

---

## 📊 Key Features

1. **Automated Mathematical Analysis**:
   - Bourdet derivative calculated with smoothing parameter $L=0.2$ to avoid noise amplification.
   - Agarwal effective time calculation for shut-in pressure buildup analysis.
   - SciPy non-linear least squares optimization (`scipy.optimize.curve_fit`) for parameter estimation ($k, s, C$).

2. **APA 7th Edition Report Generation**:
   - Dynamic document generation adhering to strict APA guidelines.
   - Math equations converted to native Word OMML equations.
   - Tables formatted with APA horizontal-only borders.
   - Figures and tables placed on individual standalone pages following References.

3. **Formatted Excel Deliverable**:
   - Multi-sheet workbook (`Problem 1 Drawdown` and `Problem 2 Buildup`).
   - Includes raw data, calculated derivatives, matched theoretical parameters, and embedded PNG plots.

---

## 📜 License
Educational repository for PFB2073 / PEB3033 Well Test Analysis Assignment.
