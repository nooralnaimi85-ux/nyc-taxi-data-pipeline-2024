# Designing an End-to-End Data Pipeline for NYC Taxi Trip Data Analytics

**DSAI5102 — Data Architecture & Engineering**  
**Dataset:** NYC Taxi & Limousine Commission (TLC) Yellow Taxi trip records, **January–December 2024**  
**Platform:** Windows 10/11, Python 3.12, DuckDB, Prefect, Streamlit

## 1. Project overview

This project demonstrates a reproducible local batch data pipeline:

**NYC TLC monthly Parquet files → `data/raw/` → DuckDB `staging_trips` → cleaned `fact_trips` → four analytical summary views → CSV exports + Streamlit dashboard.**

A Prefect flow provides optional orchestration. Running the Prefect flow manually **does not** establish that an unattended schedule has been deployed.

## 2. Folder structure

```text
nyc-taxi-data-pipeline/
├── README.md                    # This guide
├── requirements.txt             # Python dependencies
├── dashboard.py                 # Streamlit dashboard
├── src/
│   ├── pipeline.py              # Main pipeline (all 2024 months by default)
│   ├── ingestion.py             # Downloads monthly NYC TLC Parquet files
│   ├── transform.py             # Cleaning, DuckDB tables/views, CSV exports
│   ├── orchestration.py         # Optional Prefect flow
│   └── config.py                # File paths
├── tests/                       # Automated tests
├── docs/                        # Methodology, plan and troubleshooting
├── data/raw/                    # Downloaded files (created/populated at runtime)
├── data/taxi.duckdb             # Generated DuckDB database
└── outputs/                     # Generated summary CSVs
```

## 3. First-time setup on Windows (PowerShell)

**Important: do not run these commands from `C:\WINDOWS\system32`.** Extract the ZIP first, then open PowerShell **inside the inner `nyc-taxi-data-pipeline` folder** that contains `requirements.txt`, `dashboard.py`, and `src`.

For example, with the revised ZIP extracted in Downloads:

```powershell
cd "C:\Users\60328122\Downloads\nyc-taxi-data-pipeline-2024-revised\nyc-taxi-data-pipeline"
```

If you extracted it elsewhere, replace the path with your own. Confirm the folder:

```powershell
Get-Location
Get-ChildItem
```

You should see `requirements.txt`, `dashboard.py`, and `src`.

### A. Create a virtual environment

If Python 3.12 is installed at the path below:

```powershell
& "C:\Program Files\Python312\python.exe" -m venv .venv
```

If you already created `.venv` in the **outer** `nyc-taxi-data-pipeline-2024-revised` folder, you can reuse it instead of creating another one. Set its Python path with:

```powershell
$python = "C:\Users\60328122\Downloads\nyc-taxi-data-pipeline-2024-revised\.venv\Scripts\python.exe"
```

Otherwise, if you created `.venv` in the **inner project folder**, set:

```powershell
$python = ".\.venv\Scripts\python.exe"
```

Use **one** of those `$python` assignments for the rest of this session.

### B. Install dependencies (first time only)

```powershell
& $python -m pip install -r requirements.txt
```

A notice that a newer version of pip is available is not an error. Wait for installation to complete.

## 4. Run the data pipeline

### Option A — Full year 2024 (recommended for final submission)

```powershell
& $python -m src.pipeline
```

This downloads and processes **all 12 months (2024-01 through 2024-12)**. The first run may take considerable time and disk space. A successful run prints a Python dictionary containing `raw_rows`, `clean_rows`, `excluded_or_deduplicated_rows`, `months`, and `database`.

### Option B — January 2024 pilot (faster testing)

```powershell
& $python -m src.pipeline --months 2024-01
```

**Warning:** This replaces the analytical results with January-only results. To restore the full-year dashboard, rerun Option A afterward.

### Option C — Selected months

```powershell
& $python -m src.pipeline --months 2024-01 2024-02 2024-03
```

Only the months selected in the command will be represented in the resulting database and dashboard.

## 5. Open the interactive dashboard

From the same inner project folder, run:

```powershell
& $python -m streamlit run dashboard.py
```

Streamlit normally opens your browser automatically. If not, open **http://localhost:8501**. Keep the PowerShell window running while using the dashboard; press **Ctrl+C** to stop the server.

The dashboard displays:

1. Monthly trip volume (12 bars for a full-year run)
2. Trips by pickup hour
3. Trips by payment type (**numeric source codes**, not decoded labels)
4. Top 15 pickup location IDs (**numeric source codes**)

If you see fewer than 12 months, rerun the full-year pipeline (Section 4, Option A).

## 6. Run automated tests

Open another PowerShell window in the **inner project folder**, set `$python` again using the appropriate command in Section 3, then run:

```powershell
& $python -m pytest -q
```

Capture the actual test output for the report or presentation. Do not claim tests passed unless the command confirms this.

## 7. Run the optional Prefect workflow

From the inner project folder:

```powershell
& $python -m src.orchestration
```

This invokes the Prefect flow for all 12 months. It is an **on-demand run**, not proof of a deployed recurring schedule. Capture Prefect logs if your instructor requires orchestration evidence.

## 8. Check the generated results

After a successful full-year pipeline run, look for:

```text
data/taxi.duckdb
outputs/monthly_summary.csv
outputs/hourly_summary.csv
outputs/payment_summary.csv
outputs/location_summary.csv
```

To inspect the monthly CSV in PowerShell:

```powershell
Import-Csv .\outputs\monthly_summary.csv | Format-Table
```

To confirm all 12 months appear:

```powershell
(Import-Csv .\outputs\monthly_summary.csv).Count
```

The count should be **12** for a complete full-year run with valid data in each month.

**Important data check:** `raw_rows - clean_rows` must equal `excluded_or_deduplicated_rows` because the current code calculates the last metric as that difference. If your displayed output does not reconcile, rerun the command and save the complete text output before using those figures in the report.

## 9. Cleaning rules and interpretation

The pipeline retains trips with pickup months explicitly selected from 2024, and applies these project-specific checks:

- Pickup and drop-off timestamps must be present; drop-off must be later than pickup.
- Duration must be greater than 0 and at most 360 minutes.
- Trip distance must be greater than 0 and at most 200 miles.
- Total amount must be between $0 and $10,000, inclusive.
- Exact duplicate fact records are removed using `DISTINCT`.

`total_amount` is the recorded total amount, **not necessarily the base fare**. The audit metric combines all exclusions and deduplication; it does not show a per-rule breakdown. Payment and location codes are not mapped to descriptive names.

## 10. Common problems

| Message / symptom | What to do |
|---|---|
| `requirements.txt` not found | You are likely in the outer extracted folder. Enter the **inner** `nyc-taxi-data-pipeline` folder. |
| `Access is denied: C:\WINDOWS\system32\.venv` | Move out of `system32` and into the project folder before creating `.venv`. |
| `\.venv\Scripts\python.exe is not recognized` | Create the environment first or use the `$python` variable pointing to your existing outer-folder environment. |
| `No module named ...` | Run `& $python -m pip install -r requirements.txt` from the inner project folder. |
| Streamlit says database not found | Run `& $python -m src.pipeline` successfully before opening the dashboard. |
| Only one month in the dashboard | Rerun the pipeline **without** `--months`. |
| Dashboard port 8501 already in use | Stop the other Streamlit instance with Ctrl+C, or use `--server.port 8502`. |
| PowerShell command stopped with Ctrl+C | Run it again and wait for the printed summary or any error. |

## 11. Submission checklist

- [ ] Full 2024 pipeline completes without errors.
- [ ] Monthly CSV has 12 months and the dashboard displays 12 monthly bars.
- [ ] All four dashboard charts are captured in screenshots.
- [ ] Automated tests run and their real output is recorded.
- [ ] Prefect on-demand execution is demonstrated; do not describe it as scheduled unless deployed.
- [ ] Report numbers and conclusions match the generated 2024 CSVs.
- [ ] Report is 5–10 pages (PDF) and includes dataset, architecture, implementation, results, limitations, and conclusion.
- [ ] Presentation supports approximately 15 minutes plus 5 minutes Q&A.
- [ ] Repository includes source code, requirements, README, tests and documentation; excludes `.venv`, raw data and generated database.

## 12. Data source

Official NYC TLC Trip Record Data: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Use the original project title consistently in the report and presentation. The project uses public records for academic analysis and does not claim to represent every NYC taxi trip without the documented filters.

## 13. Final submission and verification

The report and presentation are in `docs/`. Run `& $python verify.py` against the completed annual database; `sql/verify.sql` contains equivalent inspection queries. See `docs/COMPLIANCE.md` for evidence limits and `docs/ARCHITECTURE.md` for the architecture diagram.

To publish, create an empty private GitHub repository named `nyc-taxi-data-pipeline-2024`, then from the project root run:

```powershell
git init
git add .
git commit -m "Final NYC taxi data pipeline project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/nyc-taxi-data-pipeline-2024.git
git push -u origin main
```

Replace YOUR-USERNAME with your actual GitHub username. Grant instructor access if private. Submit the repository URL with the corrected PDF and existing PowerPoint. Review `git status` before pushing; do not include credentials or large generated data. The report and slides contain student names/IDs, so keep the repository private unless authorized to publish them.
