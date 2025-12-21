{{ config(
    materialized='view',
    tags=['staging', 'orders']
) }}

-- Staging model for orders fact table
-- 1:1 mapping with source orders table

select
    order_id,
    customer_id,
    order_date,
    ship_date,
    ship_mode,
    order_priority,
    market,
    region,
    created_at,
    updated_at
from {{ source('ecommerce', 'orders') }}
where order_id is not null
    and customer_id is not null
    and order_date is not null
