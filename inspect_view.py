
import duckdb
db_path = r"C:\Users\marco\Documents\desafios-tecnicos-entrevistas\AbInbev\projeto-base\duckdb-dbt-airflow\data\duckdb\brewery.duckdb"
try:
    con = duckdb.connect(db_path)
    # Check for view definition
    res = con.sql("SELECT sql FROM sqlite_master WHERE name = 'breweries_bronze'").fetchone()
    if res:
        print("View Definition from sqlite_master:")
        print(res[0])
    else:
        print("View not found in sqlite_master. Checking duckdb_views...")
        res = con.sql("SELECT sql FROM duckdb_views WHERE view_name = 'breweries_bronze'").fetchone()
        if res:
             print("View Definition from duckdb_views:")
             print(res[0])
        else:
             print("View not found.")
except Exception as e:
    print(e)
