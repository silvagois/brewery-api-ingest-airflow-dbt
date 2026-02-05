from src.ingestion.ingest_landing import ingest_breweries
from pathlib import Path


def test_ingestion_creates_file():
    path = ingest_breweries(per_page=1)
    assert isinstance(path, Path)
    assert path.exists()
