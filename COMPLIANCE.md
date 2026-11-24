# Final submission compliance review
Basis: instructor project description, pages 1–4; uploaded report and presentation; existing revised source archive.

| Requirement | Deliverable | Status / evidence | Remaining action |
|---|---|---|---|
| Problem and dataset | Report sections 1–2, slides 2–4 | Present | None |
| Batch ingestion and raw storage | src/ingestion.py, pipeline.py | Code present; annual CLI screenshot | Verify on target PC if needed |
| Analytical storage and transformations | src/transform.py | Staging, fact, views, audit and CSV export implemented | Run verify.py on annual database |
| Workflow orchestration | src/orchestration.py | Flow definition present | Execute Prefect flow; schedule not mandatory |
| At least two dashboard tiles | dashboard.py | Four charts implemented; January pilot evidence | Capture actual annual charts and CSVs |
| Reproducibility | README.md, requirements.txt, config.py | Included | Install dependencies on target PC |
| Automated tests | tests/ | Four ingestion tests passed in packaging environment; full suite blocked by missing DuckDB | Run full pytest suite on target PC |
| PDF report 5–10 pages | docs/report.pdf | 10 pages; transcription corrected against embedded screenshot | Replace previously uploaded report if permitted |
| Presentation ~15 min + 5 min Q&A | docs/presentation.pptx | 20 slides, existing uploaded deck preserved | Rehearse timing; approximate pilot values and external monthly chart are not annual curated results |
| GitHub repository | This package | Ready for upload, not published | Create repository and share link with instructor |
| Docker if applicable | Not included | Optional; local Python deployment | None |

## Evidence limits
Annual screenshot reports 41,169,720 raw, 39,809,562 curated, 1,360,158 excluded/deduplicated (96.70% retained). This is not an independent database audit. Annual CSVs, current dashboard screenshots and Prefect run logs were not supplied. No new full-year run was performed. Confirm team contribution descriptions. The report correction changes the earlier transcription, not the source data.
