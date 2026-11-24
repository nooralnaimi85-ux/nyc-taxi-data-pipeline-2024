# Architecture
```mermaid
flowchart LR
 A[NYC TLC monthly Parquet] --> B[Python ingestion / raw cache]
 B --> C[DuckDB staging_trips]
 C --> D[SQL validation and DISTINCT]
 D --> E[fact_trips]
 E --> F[Four analytical views]
 E --> G[pipeline_audit]
 F --> H[CSV exports]
 F --> I[Streamlit dashboard]
```
Prefect defines ingestion tasks with retries followed by warehouse construction. The CLI is the demonstrated annual execution path. The dashboard queries the four views read-only. The curated table is rebuilt on each run rather than appended. See `src/transform.py` for the actual executable SQL.
