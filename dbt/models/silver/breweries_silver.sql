{{ config(
    materialized = "table"
) }}

{% if target.name == "ci" %}

-- ============================================================
-- CI MODE
-- Cria tabela vazia respeitando o CONTRATO da camada Silver
-- ============================================================

SELECT
    NULL::VARCHAR AS brewery_id,
    NULL::VARCHAR AS brewery_name,
    NULL::VARCHAR AS brewery_type,
    NULL::VARCHAR AS address_1,
    NULL::VARCHAR AS address_2,
    NULL::VARCHAR AS address_3,
    NULL::VARCHAR AS city,
    NULL::VARCHAR AS state,
    NULL::VARCHAR AS state_province,
    NULL::VARCHAR AS postal_code,
    NULL::VARCHAR AS country,
    NULL::DOUBLE  AS longitude,
    NULL::DOUBLE  AS latitude,
    NULL::VARCHAR AS phone,
    NULL::VARCHAR AS website_url,
    NULL::VARCHAR AS street,
    NULL::DATE    AS ingestion_date
WHERE 1 = 0

{% else %}

-- ============================================================
-- PROD / AIRFLOW MODE
-- ============================================================

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

SELECT
    brewery_id,
    brewery_name,
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
FROM deduplicated

{% endif %}
