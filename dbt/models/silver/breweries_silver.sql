{{ config(
    materialized = "table"
) }}

WITH bronze AS (
    SELECT
        id,
        name,
        brewery_type,
        address_1,
        address_2,
        address_3,
        city,
        state,
        state_province,
        postal_code,
        country,
        longitude,
        latitude,
        phone,
        website_url,
        street,
        ingestion_date
    FROM {{ ref('breweries_bronze') }}

),
cleaned AS (
    SELECT
        id::VARCHAR                    AS brewery_id,
        trim(name)                     AS brewery_name,
        lower(trim(brewery_type))      AS brewery_type,
        trim(address_1)                AS address_1,
        trim(address_2)                AS address_2,
        trim(address_3)                AS address_3,
        trim(city)                     AS city,
        trim(state)                    AS state,
        trim(state_province)           AS state_province,
        trim(postal_code)              AS postal_code,
        trim(country)                  AS country,
        longitude::DOUBLE              AS longitude,
        latitude::DOUBLE               AS latitude,
        trim(phone)                    AS phone,
        trim(website_url)              AS website_url,
        trim(street)                   AS street,
        ingestion_date
    FROM bronze
    WHERE id IS NOT NULL

),
deduplicated AS (
    SELECT *
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY brewery_id
                ORDER BY ingestion_date DESC
            ) AS rn
        FROM cleaned
    )
    WHERE rn = 1

)
SELECT * FROM deduplicated
