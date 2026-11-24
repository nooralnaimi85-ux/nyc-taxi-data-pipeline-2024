from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
DB = ROOT / "data" / "taxi.duckdb"
for folder in (RAW, PROCESSED, OUTPUTS):
    folder.mkdir(parents=True, exist_ok=True)
