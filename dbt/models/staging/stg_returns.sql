{{ config(
    materialized='view',
    tags=['staging', 'returns']
) }}

-- Staging model for returns
-- 1:1 mapping with source returns table

select
    return_id,
    order_id,
    return_date,
    return_reason,
    return_status,
    created_at,
    updated_at
from {{ source('ecommerce', 'returns') }}
where return_id is not null
    and order_id is not null
