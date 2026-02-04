SELECT
    id,
    name,
    LOWER(brewery_type) AS brewery_type,
    city,
    state_province,
    country,
    CAST(latitude AS DOUBLE) AS latitude,
    CAST(longitude AS DOUBLE) AS longitude,
    ingestion_date
FROM {{ ref("breweries_bronze") }}
WHERE country IS NOT NULL
