{{ config(
    materialized='table',
    tags=['marts', 'core', 'customer_analytics']
) }}

-- Customer analytics mart
-- Customer-level aggregations and metrics

with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

order_items as (
    select * from {{ ref('stg_order_items') }}
),

customer_orders as (
    select
        c.customer_id,
        c.customer_name,
        c.segment,
        c.city,
        c.state,
        c.country,
        count(distinct o.order_id) as total_orders,
        count(distinct o.order_date) as days_since_first_order,
        sum(oi.quantity) as total_quantity,
        sum(oi.sales) as total_sales,
        sum(oi.profit) as total_profit,
        round(avg(oi.sales), 2) as avg_order_value,
        max(o.order_date) as last_order_date,
        min(o.order_date) as first_order_date
    from customers c
    left join orders o on c.customer_id = o.customer_id
    left join order_items oi on o.order_id = oi.order_id
    group by 1, 2, 3, 4, 5, 6
)

select
    customer_id,
    customer_name,
    segment,
    city,
    state,
    country,
    total_orders,
    days_since_first_order,
    total_quantity,
    total_sales,
    total_profit,
    avg_order_value,
    last_order_date,
    first_order_date,
    round(total_profit / nullif(total_sales, 0), 3) as profit_margin,
    case
        when total_orders >= 10 then 'VIP'
        when total_orders >= 5 then 'Regular'
        else 'At-Risk'
    end as customer_tier,
    current_timestamp as updated_at
from customer_orders
where customer_id is not null
