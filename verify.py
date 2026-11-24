"""Read-only verification of the existing warehouse; does not rerun ingestion."""
import duckdb
from src.config import DB
with duckdb.connect(str(DB), read_only=True) as con:
    raw, clean, excluded = con.execute('SELECT source_rows, curated_rows, excluded_or_deduplicated_rows FROM pipeline_audit').fetchone()
    actual = con.execute('SELECT count(*) FROM fact_trips').fetchone()[0]
    staging = con.execute('SELECT count(*) FROM staging_trips').fetchone()[0]
    months, total = con.execute('SELECT count(*), sum(trips) FROM monthly_summary').fetchone()
    print(dict(raw=raw, curated=clean, excluded=excluded, months=months, monthly_total=total))
    assert raw == staging and clean == actual and raw-clean == excluded
    assert months == 12 and total == actual, 'Expected full-year data'
    for view in ('hourly_summary', 'payment_summary'):
        assert con.execute(f'SELECT sum(trips) FROM {view}').fetchone()[0] == actual
    print('Warehouse checks passed')
