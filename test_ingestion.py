import pytest
from src.ingestion import download_month
@pytest.mark.parametrize('month', ['2024-00', '2024-13', 'hello', '202401'])
def test_bad_month(month):
    with pytest.raises(ValueError): download_month(month)
