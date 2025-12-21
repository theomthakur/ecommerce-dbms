{{ config(
    materialized='table',
    tags=['marts', 'core', 'order_analytics']
) }}

-- Order analytics mart
-- Order-level facts with dimensional attributes

with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

order_items as (
    select * from {{ ref('stg_order_items') }}
),

returns as (
    select * from {{ ref('stg_returns') }}
),

order_summary as (
    select
        o.order_id,
        o.customer_id,
        c.customer_name,
        c.segment as customer_segment,
        o.order_date,
        o.ship_date,
        o.ship_mode,
        o.order_priority,
        o.region,
        o.market,
        sum(oi.quantity) as total_quantity,
        sum(oi.sales) as total_sales,
        sum(oi.profit) as total_profit,
        sum(oi.shipping_cost) as total_shipping_cost,
        sum(oi.discount) as total_discount,
        count(distinct oi.product_id) as unique_products,
        max(case when r.return_id is not null then 1 else 0 end) as has_returns,
        count(r.return_id) as return_count,
        datediff(day, o.order_date, o.ship_date) as days_to_ship
    from orders o
    left join customers c on o.customer_id = c.customer_id
    left join order_items oi on o.order_id = oi.order_id
    left join returns r on o.order_id = r.order_id
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
)

select
    order_id,
    customer_id,
    customer_name,
    customer_segment,
    order_date,
    ship_date,
    ship_mode,
    order_priority,
    region,
    market,
    total_quantity,
    total_sales,
    total_profit,
    total_shipping_cost,
    total_discount,
    unique_products,
    has_returns,
    return_count,
    days_to_ship,
    round(total_profit / nullif(total_sales, 0), 3) as profit_margin,
    case
        when total_sales > 500 then 'High Value'
        when total_sales > 100 then 'Medium Value'
        else 'Low Value'
    end as order_value_category,
    current_timestamp as updated_at
from order_summary
where order_id is not null
