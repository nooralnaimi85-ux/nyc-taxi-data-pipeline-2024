"""Batch entry point: full calendar year 2024 by default."""
import argparse
from pathlib import Path
from .ingestion import download_month
from .transform import process
MONTHS_2024 = [f"2024-{m:02d}" for m in range(1, 13)]

def run(months=None, local_files=None):
    months = MONTHS_2024 if months is None else months
    files = [Path(f) for f in local_files] if local_files else [download_month(m) for m in months]
    return process(files, months=months)

def main():
    parser = argparse.ArgumentParser(description="NYC Yellow Taxi 2024 batch analytics")
    parser.add_argument('--months', nargs='+', default=None, help='YYYY-MM; default: all 12 months of 2024')
    parser.add_argument('--files', nargs='+', help='Local Parquet files (requires --months matching those files)')
    args = parser.parse_args()
    if args.files and not args.months:
        parser.error('--files requires --months to define the corresponding period')
    print(run(args.months, args.files))
if __name__ == '__main__':
    main()
