import requests
import json
from pathlib import Path
from typing import List, Dict
from requests.exceptions import RequestException, Timeout

API_URL = "https://api.openbrewerydb.org/v1/breweries"
DEFAULT_TIMEOUT = 15


class IngestionError(Exception):
    """Erro genérico de ingestão."""
    pass


def fetch_breweries(per_page: int = 50) -> List[Dict]:
    """
    Fetch breweries from Open Brewery DB API.

    Raises:
        IngestionError: If API call fails or returns invalid data.
    """
    try:
        response = requests.get(
            API_URL,
            params={"per_page": per_page},
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()

    except Timeout as exc:
        raise IngestionError(
            f"[ERROR] Timeout after {DEFAULT_TIMEOUT}s calling Open Brewery API"
        ) from exc

    except RequestException as exc:
        raise IngestionError(
            f"[ERROR] Failed to fetch data from Open Brewery API: {exc}"
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise IngestionError(
            "[ERROR] API response is not valid JSON"
        ) from exc

    if not isinstance(data, list):
        raise IngestionError(
            f"[ERROR] Unexpected API response format: {type(data)}"
        )

    if len(data) == 0:
        raise IngestionError(
            "[ERROR] API returned empty dataset"
        )

    print(f"[OK] API returned {len(data)} records")

    return data


def write_landing(
    data: List[Dict],
    execution_date: str,
    base_path: str = "/opt/airflow/data/landing/breweries",
) -> Path:
    """
    Writes raw API data to landing zone partitioned by execution_date.
    """
    try:
        landing_path = Path(base_path) / execution_date
        landing_path.mkdir(parents=True, exist_ok=True)

        file_path = landing_path / "list_breweries.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    except OSError as exc:
        raise IngestionError(
            f"[ERROR] Failed to write landing file: {exc}"
        ) from exc

    print(f"[OK] Landing file written to {file_path}")
    print(f"[OK] Records ingested: {len(data)}")

    return file_path



def ingest_breweries(execution_date: str, per_page: int = 50) -> None:
    """
    Main ingestion entrypoint for Airflow.
    """
    print(f"[INFO] Starting ingestion for execution_date={execution_date}")

    breweries = fetch_breweries(per_page=per_page)
    write_landing(breweries, execution_date)

    print("[SUCCESS] Ingestion completed successfully")
