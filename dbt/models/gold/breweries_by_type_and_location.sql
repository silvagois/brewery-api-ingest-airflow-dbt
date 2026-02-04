{{ config(
    materialized = "table"
) }}

SELECT
    brewery_type,
    country,
    state,
    city,
    COUNT(*) AS breweries_count,
    MAX(ingestion_date) AS last_ingestion_date
FROM {{ ref('breweries_silver') }}
GROUP BY
    brewery_type,
    country,
    state,
    city
