{{ config(
    materialized='table',
    tags=['marts', 'marketing', 'product']
) }}

-- Marketing mart: Product performance
-- Product-level performance metrics

with products as (
    select * from {{ ref('stg_products') }}
),

order_items as (
    select * from {{ ref('stg_order_items') }}
),

returns as (
    select * from {{ ref('stg_returns') }}
),

product_performance as (
    select
        p.product_id,
        p.product_name,
        p.category,
        p.sub_category,
        count(distinct oi.order_id) as total_orders,
        sum(oi.quantity) as total_sold,
        sum(oi.sales) as total_revenue,
        sum(oi.profit) as total_profit,
        round(avg(oi.sales), 2) as avg_price,
        count(distinct r.return_id) as total_returns,
        round(100.0 * count(distinct r.return_id) / nullif(count(distinct oi.order_id), 0), 2) as return_rate
    from products p
    left join order_items oi on p.product_id = oi.product_id
    left join returns r on oi.order_id = r.order_id
    group by 1, 2, 3, 4
)

select
    product_id,
    product_name,
    category,
    sub_category,
    total_orders,
    total_sold,
    total_revenue,
    total_profit,
    avg_price,
    total_returns,
    return_rate,
    round(total_profit / nullif(total_revenue, 0), 3) as profit_margin,
    case
        when total_orders > 100 then 'Star'
        when total_orders > 50 then 'Cash Cow'
        when total_orders > 10 then 'Question Mark'
        else 'Dog'
    end as product_category,
    current_timestamp as updated_at
from product_performance
where product_id is not null
order by total_revenue desc
