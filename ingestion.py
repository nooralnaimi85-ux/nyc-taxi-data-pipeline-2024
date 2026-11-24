"""Official NYC TLC yellow taxi monthly Parquet downloads."""
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from .config import RAW

def download_month(month: str, dest: Path = RAW) -> Path:
    if len(month) != 7 or month[4] != '-' or not (month[:4] + month[5:]).isdigit():
        raise ValueError('Month must be YYYY-MM')
    year, mon = map(int, month.split('-'))
    if not (2009 <= year <= 2100 and 1 <= mon <= 12):
        raise ValueError('Invalid month')
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / f'yellow_tripdata_{month}.parquet'
    if target.exists() and target.stat().st_size > 0:
        return target
    url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month}.parquet'
    temporary = target.with_suffix('.part')
    try:
        with urlopen(url, timeout=90) as response, temporary.open('wb') as output:
            while True:
                block = response.read(1024 * 1024)
                if not block: break
                output.write(block)
        if temporary.stat().st_size == 0:
            raise RuntimeError('Downloaded file is empty')
        temporary.replace(target)
    except (HTTPError, URLError, OSError, RuntimeError):
        temporary.unlink(missing_ok=True)
        raise
    return target
