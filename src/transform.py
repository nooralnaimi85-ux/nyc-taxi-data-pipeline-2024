# Validate 2024 Yellow Taxi records and produce reproducible DuckDB summaries.
from pathlib import Path
from datetime import date
import re
import duckdb
from .config import DB, OUTPUTS

REQUIRED = {'tpep_pickup_datetime', 'tpep_dropoff_datetime', 'trip_distance', 'total_amount', 'payment_type', 'PULocationID'}
SUMMARIES = ('monthly_summary', 'hourly_summary', 'payment_summary', 'location_summary')

def process(files: list[Path], database: Path = DB, output: Path = OUTPUTS, months: list[str] | None = None) -> dict:
    if not files:
        raise ValueError('At least one Parquet input is required')
    if months is None:
        months = ['2024-01']  # backwards-compatible single-month test default
    if len(months) != len(files) or len(set(months)) != len(months):
        raise ValueError('Provide one unique YYYY-MM month for each input file')
    if any(not re.fullmatch(r'2024-(0[1-9]|1[0-2])', m) for m in months):
        raise ValueError('This project accepts only months within calendar year 2024')
    for file in files:
        if not Path(file).is_file():
            raise FileNotFoundError(file)
    database.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(database))
    try:
        paths = [str(Path(f).resolve()) for f in files]
        columns = {r[0] for r in con.execute('DESCRIBE SELECT * FROM read_parquet(?)', [paths]).fetchall()}
        missing = REQUIRED - columns
        if missing:
            raise ValueError(f'Missing source columns: {sorted(missing)}')
        con.execute('CREATE OR REPLACE TABLE staging_trips AS SELECT * FROM read_parquet(?)', [paths])
        # Only include pickup dates from explicitly selected months, never spillover records.
        placeholders = ', '.join('?' for _ in months)
        con.execute(f'''CREATE OR REPLACE TABLE fact_trips AS
          WITH candidates AS (
            SELECT tpep_pickup_datetime AS pickup_at,
              tpep_dropoff_datetime AS dropoff_at,
              trip_distance, total_amount, payment_type,
              PULocationID AS pickup_location_id,
              date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime) / 60.0 AS duration_min
            FROM staging_trips
          ), valid AS (
            SELECT * FROM candidates WHERE pickup_at IS NOT NULL AND dropoff_at IS NOT NULL
              AND dropoff_at > pickup_at
              AND duration_min > 0 AND duration_min <= 360
              AND trip_distance > 0 AND trip_distance <= 200
              AND total_amount >= 0 AND total_amount <= 10000
              AND strftime(pickup_at, '%Y-%m') IN ({placeholders})
          )
          SELECT DISTINCT pickup_at, dropoff_at,
            CAST(date_trunc('month', pickup_at) AS DATE) AS trip_month,
            CAST(extract(hour FROM pickup_at) AS INTEGER) AS pickup_hour,
            pickup_location_id, payment_type, trip_distance, total_amount, duration_min
          FROM valid''', months)
        con.execute('''CREATE OR REPLACE VIEW monthly_summary AS
          SELECT trip_month, count(*) AS trips,
            round(avg(total_amount), 2) AS avg_total_amount,
            round(avg(trip_distance), 2) AS avg_distance_miles
          FROM fact_trips GROUP BY 1 ORDER BY 1''')
        con.execute('''CREATE OR REPLACE VIEW hourly_summary AS
          SELECT pickup_hour, count(*) AS trips FROM fact_trips GROUP BY 1 ORDER BY 1''')
        con.execute('''CREATE OR REPLACE VIEW payment_summary AS
          SELECT payment_type, count(*) AS trips FROM fact_trips GROUP BY 1 ORDER BY trips DESC''')
        con.execute('''CREATE OR REPLACE VIEW location_summary AS
          SELECT pickup_location_id, count(*) AS trips FROM fact_trips GROUP BY 1 ORDER BY trips DESC LIMIT 15''')
        for name in SUMMARIES:
            con.execute(f"COPY (SELECT * FROM {name}) TO ? (HEADER, DELIMITER ',')", [str(output / f'{name}.csv')])
        raw_rows = con.execute('SELECT count(*) FROM staging_trips').fetchone()[0]
        clean_rows = con.execute('SELECT count(*) FROM fact_trips').fetchone()[0]
        # Excluded count includes filtering and DISTINCT deduplication.
        con.execute('''CREATE OR REPLACE TABLE pipeline_audit AS SELECT
          ?::INTEGER AS source_rows, ?::INTEGER AS curated_rows,
          (? - ?)::INTEGER AS excluded_or_deduplicated_rows,
          current_timestamp AS processed_at''', [raw_rows, clean_rows, raw_rows, clean_rows])
        return {'raw_rows': raw_rows, 'clean_rows': clean_rows,
                'excluded_or_deduplicated_rows': raw_rows - clean_rows,
                'months': months, 'database': str(database)}
    finally:
        con.close()
