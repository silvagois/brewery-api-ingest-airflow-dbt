{{ config(
    materialized = "incremental",
    unique_key = "id",
    on_schema_change = "fail"
) }}

SELECT
    id,
    name,
    brewery_type,
    city,
    state,
    country,
    ingestion_date
FROM {{ ref('breweries_bronze') }}

{% if is_incremental() %}
  WHERE ingestion_date > (SELECT MAX(ingestion_date) FROM {{ this }})
{% endif %}
