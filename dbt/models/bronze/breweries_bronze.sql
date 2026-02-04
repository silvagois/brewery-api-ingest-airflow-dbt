{{ config(
    materialized = "external",
    external_location="bronze/breweries",
    partition_by=["ingestion_date"],
    post_hook = "select count(*) from {{ this }}"
) }}

SELECT
    *,
    '{{ var("execution_date") }}'::DATE AS ingestion_date
FROM read_json(
    '/opt/airflow/data/landing/breweries/{{ var("execution_date") }}/list_breweries.json'
)
