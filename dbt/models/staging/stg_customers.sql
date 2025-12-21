{{ config(
    materialized='view',
    tags=['staging', 'customers']
) }}

-- Staging model for customers dimension
-- 1:1 mapping with source customers table

select
    customer_id,
    customer_name,
    segment,
    postal_code,
    city,
    state,
    country,
    region,
    {{ dbt_utils.generate_dbt_utils_dispatch_list(
        macro_namespace='dbt_utils',
        search_list=['macro_default']
    ) }}
from {{ source('ecommerce', 'customers') }}
where customer_id is not null
