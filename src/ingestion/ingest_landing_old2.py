import requests
import json
from pathlib import Path

API_URL = "https://api.openbrewerydb.org/v1/breweries"


def fetch_breweries(per_page: int = 50) -> list[dict]:
    response = requests.get(API_URL, params={"per_page": per_page}, timeout=15)
    response.raise_for_status()
    return response.json()


def write_landing(
    data: list[dict],
    execution_date: str,
    base_path: str = "/opt/airflow/data/landing/breweries",
) -> Path:
    landing_path = Path(base_path) / execution_date
    landing_path.mkdir(parents=True, exist_ok=True)

    file_path = landing_path / "list_breweries.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Landing file written to {file_path}")
    print(f"[OK] Records ingested: {len(data)}")

    return file_path


# 🔥 FUNÇÃO QUE O AIRFLOW CHAMA
def ingest_breweries(execution_date: str, per_page: int = 50):
    breweries = fetch_breweries(per_page=per_page)
    write_landing(breweries, execution_date)
