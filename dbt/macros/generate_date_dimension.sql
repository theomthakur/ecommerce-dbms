-- Macro: generate_date_dimension
-- Generates a date dimension table

{% macro generate_date_dimension(start_date, end_date) %}
    with date_range as (
        select
            dateadd('day', seq4(), '{{ start_date }}'::date) as date_day
        from table(generator(rowcount => {{ (end_date | as_date - start_date | as_date).days + 1 }}))
    )
    select
        date_day,
        extract(year from date_day) as year,
        extract(month from date_day) as month,
        extract(quarter from date_day) as quarter,
        extract(day from date_day) as day_of_month,
        extract(week from date_day) as week_of_year,
        extract(dayofweek from date_day) as day_of_week,
        case
            when extract(dayofweek from date_day) in (6, 7) then 1
            else 0
        end as is_weekend,
        case
            when extract(month from date_day) in (12, 1, 2) then 'Winter'
            when extract(month from date_day) in (3, 4, 5) then 'Spring'
            when extract(month from date_day) in (6, 7, 8) then 'Summer'
            else 'Fall'
        end as season
    from date_range
    order by date_day
{% endmacro %}
