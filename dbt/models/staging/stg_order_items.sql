{{ config(
    materialized='view',
    tags=['staging', 'order_items']
) }}

-- Staging model for order items
-- 1:1 mapping with source order_items table

select
    row_id,
    order_id,
    product_id,
    quantity,
    sales,
    discount,
    profit,
    shipping_cost,
    created_at,
    updated_at
from {{ source('ecommerce', 'order_items') }}
where order_id is not null
    and product_id is not null
    and quantity > 0
