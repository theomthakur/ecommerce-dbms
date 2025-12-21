{{ config(
    materialized='table',
    tags=['marts', 'finance', 'revenue']
) }}

-- Finance mart: Revenue analysis
-- Monthly and regional revenue metrics

with order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

revenue_metrics as (
    select
        date_trunc('month', o.order_date) as revenue_month,
        o.region,
        o.market,
        sum(oi.sales) as gross_revenue,
        sum(oi.profit) as net_profit,
        sum(oi.shipping_cost) as shipping_cost,
        sum(oi.discount) as total_discounts,
        count(distinct o.order_id) as order_count,
        sum(oi.quantity) as total_items
    from orders o
    left join order_items oi on o.order_id = oi.order_id
    group by 1, 2, 3
)

select
    revenue_month,
    region,
    market,
    gross_revenue,
    net_profit,
    shipping_cost,
    total_discounts,
    order_count,
    total_items,
    round(gross_revenue - shipping_cost, 2) as revenue_after_shipping,
    round(net_profit / nullif(gross_revenue, 0), 3) as profit_margin,
    round(gross_revenue / nullif(order_count, 0), 2) as avg_revenue_per_order,
    current_timestamp as updated_at
from revenue_metrics
where revenue_month is not null
order by revenue_month desc, region, market
