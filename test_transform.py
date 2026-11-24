import duckdb
import pytest
from src.transform import process

def make_parquet(tmp_path):
    parquet = tmp_path / 'sample.parquet'
    with duckdb.connect() as con:
        con.execute("""COPY (SELECT * FROM (VALUES
            (TIMESTAMP '2024-01-01 12:00:00', TIMESTAMP '2024-01-01 12:15:00', 2.5, 15.0, 1, 100),
            (TIMESTAMP '2024-02-01 12:00:00', TIMESTAMP '2024-02-01 12:15:00', 2.5, 15.0, 1, 100),
            (TIMESTAMP '2025-01-01 12:00:00', TIMESTAMP '2025-01-01 12:15:00', 2.5, 15.0, 1, 100)
        ) t(tpep_pickup_datetime, tpep_dropoff_datetime, trip_distance, total_amount, payment_type, PULocationID))
        TO ? (FORMAT PARQUET)""", [str(parquet)])
    return parquet

def test_january_filter_and_idempotence(tmp_path):
    file = make_parquet(tmp_path)
    db = tmp_path / 'taxi.duckdb'
    a = process([file], db, tmp_path / 'out', ['2024-01'])
    b = process([file], db, tmp_path / 'out', ['2024-01'])
    assert a['clean_rows'] == b['clean_rows'] == 1
    assert a['raw_rows'] == 3

def test_reject_non_2024_month(tmp_path):
    with pytest.raises(ValueError):
        process([make_parquet(tmp_path)], tmp_path / 'db.duckdb', tmp_path / 'out', ['2025-01'])
