"""Prefect flow for the selected 2024 months; scheduling is optional."""
from prefect import flow, task
from .ingestion import download_month
from .transform import process
from .pipeline import MONTHS_2024

@task(retries=3, retry_delay_seconds=15)
def ingest(month):
    return download_month(month)

@task
def build_warehouse(paths, months):
    return process(paths, months=months)

@flow(name='nyc-taxi-2024-batch-pipeline', log_prints=True)
def taxi_flow(months=None):
    months = MONTHS_2024 if months is None else months
    paths = [ingest(m) for m in months]
    return build_warehouse(paths, months)

if __name__ == '__main__':
    print(taxi_flow())
