import requests
import json
from datetime import date
from pathlib import Path

API_URL = "https://api.openbrewerydb.org/v1/breweries"


def fetch_breweries(per_page: int = 50) -> list[dict]:
    response = requests.get(API_URL, params={"per_page": per_page}, timeout=15)
    response.raise_for_status()
    data = response.json()    
    return data


def write_landing(data: list[dict], base_path: str = "C:\\Users\\marco\\Documents\\desafios-tecnicos-entrevistas\\AbInbev\\projeto-base\\duckdb-dbt-airflow\\data\\landing\\breweries\\") -> Path:
    current_date = date.today().isoformat()
    landing_path = Path(base_path) / current_date
    landing_path.mkdir(parents=True, exist_ok=True)

    file_path = landing_path / "list_breweries.json"

    print(f"[INFO] Landing file written to {file_path}")
    print(f"[INFO] Records ingested: {len(data)}")

    with open(file_path,"w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return file_path


def run_ingestion():
    breweries = fetch_breweries()
    write_landing(breweries)

def main():
    run_ingestion()

if __name__=='__main__':
    main()
