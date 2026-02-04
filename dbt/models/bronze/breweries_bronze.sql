{{
  config(
    materialized = "external",
    external_location = "bronze/breweries",
    partition_by = ["ingestion_date"],
    post_hook = "select count(*) from {{ this }}"
  )
}}

{% set execution_date = var(
    "execution_date",
    run_started_at.strftime("%Y-%m-%d")
) %}

{% set data_root = var(
    "data_root",
    "/opt/airflow/data"
) %}

{% if target.name == "ci" %}

-- CI: tabela vazia com CONTRATO COMPLETO
SELECT
    NULL::VARCHAR AS id,
    NULL::VARCHAR AS name,
    NULL::VARCHAR AS brewery_type,
    NULL::VARCHAR AS city,
    NULL::VARCHAR AS state,
    '{{ execution_date }}'::DATE AS ingestion_date
WHERE 1 = 0

{% else %}

-- PROD / AIRFLOW
SELECT
    id,
    name,
    brewery_type,
    city,
    state,
    '{{ execution_date }}'::DATE AS ingestion_date
FROM read_json(
    '{{ data_root }}/landing/breweries/{{ execution_date }}/list_breweries.json'
)

{% endif %}
