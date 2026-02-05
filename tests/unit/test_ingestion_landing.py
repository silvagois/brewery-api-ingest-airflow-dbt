import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.ingestion.ingest_landing import (
    fetch_breweries,
    write_landing,
    ingest_breweries,
    IngestionError,
)


# ------------------------
# FIXTURES
# ------------------------

@pytest.fixture
def sample_api_response():
    return [
        {"id": "1", "name": "Brewery One"},
        {"id": "2", "name": "Brewery Two"},
    ]


@pytest.fixture
def tmp_landing_dir(tmp_path):
    return tmp_path / "landing" / "breweries"


# ------------------------
# TEST fetch_breweries
# ------------------------

@patch("src.ingestion.ingest_landing.requests.get")
def test_fetch_breweries_success(mock_get, sample_api_response):
    mock_response = MagicMock()
    mock_response.json.return_value = sample_api_response
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = fetch_breweries(per_page=2)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["name"] == "Brewery One"


@patch("src.ingestion.ingest_landing.requests.get")
def test_fetch_breweries_timeout(mock_get):
    mock_get.side_effect = Exception("Timeout")

    with pytest.raises(IngestionError):
        fetch_breweries()


@patch("src.ingestion.ingest_landing.requests.get")
def test_fetch_breweries_empty_response(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    with pytest.raises(IngestionError):
        fetch_breweries()


# ------------------------
# TEST write_landing
# ------------------------

def test_write_landing_success(sample_api_response, tmp_landing_dir):
    execution_date = "2026-02-01"

    file_path = write_landing(
        data=sample_api_response,
        execution_date=execution_date,
        base_path=str(tmp_landing_dir),
    )

    assert file_path.exists()

    with open(file_path) as f:
        content = json.load(f)

    assert len(content) == 2
    assert content[0]["name"] == "Brewery One"


def test_write_landing_invalid_path(sample_api_response):
    with pytest.raises(IngestionError):
        write_landing(
            data=sample_api_response,
            execution_date="2026-02-01",
            base_path="/root/invalid_path",
        )


# ------------------------
# TEST ingest_breweries (INTEGRATION STYLE)
# ------------------------

@patch("src.ingestion.ingest_landing.fetch_breweries")
@patch("src.ingestion.ingest_landing.write_landing")
def test_ingest_breweries_success(
    mock_write,
    mock_fetch,
    sample_api_response,
):
    mock_fetch.return_value = sample_api_response
    mock_write.return_value = Path("/fake/path/list_breweries.json")

    ingest_breweries(
        execution_date="2026-02-01",
        per_page=2,
    )

    mock_fetch.assert_called_once()
    mock_write.assert_called_once()
