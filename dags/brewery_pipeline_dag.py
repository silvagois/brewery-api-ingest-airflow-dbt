from airflow import DAG
#from airflow.operators.python import PythonOperator
#from airflow.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator

from datetime import datetime, timedelta

from src.ingestion.ingest_landing import ingest_breweries

default_args = {
    "owner": "data-platform",
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="brewery_data_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule ="@daily",
    catchup=False,
    default_args=default_args,
    tags=["brewery", "duckdb", "dbt"],
) as dag:

    ingest_landing = PythonOperator(
        task_id="ingest_breweries_landing",
        python_callable=ingest_breweries,
        op_kwargs={
            "execution_date": "{{ ds }}", # melhorar essa etapa para pegar o timezone do brazil
            "per_page": 200,
        },
    )

    # dbt_bronze = BashOperator(
    #     task_id="dbt_bronze",
    #     bash_command="""
    #     dbt run \
    #     --project-dir /opt/airflow/dbt \
    #     --profiles-dir /opt/airflow/dbt \
    #     --select breweries_bronze \
    #     --vars '{"execution_date": "{{ ds }}"}'
    #     """
    # )

    dbt_bronze = BashOperator(
        task_id="dbt_bronze",
        bash_command="""
        dbt run \
        --models bronze.breweries_bronze \
        --vars '{
            "execution_date": "{{ ds }}",
            "data_root": "/opt/airflow/data"
        }'
        """
    )

    dbt_silver = BashOperator(
        task_id="dbt_silver",
        bash_command="""
        dbt run \
        --project-dir /opt/airflow/dbt \
        --profiles-dir /opt/airflow/dbt \
        --select breweries_silver
        """
    )

    dbt_gold = BashOperator(
        task_id="dbt_gold",
        bash_command="""
        dbt run \
        --project-dir /opt/airflow/dbt \
        --profiles-dir /opt/airflow/dbt \
          --select breweries_by_type_and_location
        """
    )    

    dbt_test = BashOperator(
         task_id="dbt_test",
         bash_command="""
         cd /opt/airflow/dbt && \
         dbt test \
             --project-dir /opt/airflow/dbt \
             --profiles-dir /opt/airflow/dbt
     """
    )
    # dbt_test = BashOperator(
    #     task_id="dbt_test",
    #     env={
    #         "DBT_PROFILES_DIR": "/opt/airflow/dbt"
    #     },
    #     bash_command="""
    #     set -e
    #     cd /opt/airflow/dbt
    #     dbt test --project-dir .
    #     """
    # )


    ingest_landing >> dbt_bronze >> dbt_silver >> dbt_gold >> dbt_test

