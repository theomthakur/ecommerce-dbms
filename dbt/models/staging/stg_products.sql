{{ config(
    materialized='view',
    tags=['staging', 'products']
) }}

-- Staging model for products dimension
-- 1:1 mapping with source products table

select
    product_id,
    product_name,
    category,
    sub_category,
    created_at,
    updated_at
from {{ source('ecommerce', 'products') }}
where product_id is not null
