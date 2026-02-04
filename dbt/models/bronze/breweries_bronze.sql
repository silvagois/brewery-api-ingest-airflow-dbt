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
    "/tmp"
) %}

SELECT
    *,
    '{{ execution_date }}'::DATE AS ingestion_date
FROM try_read_json(
    '{{ data_root }}/landing/breweries/{{ execution_date }}/list_breweries.json'
)
