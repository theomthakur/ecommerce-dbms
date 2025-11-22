-- Views for DW analytics
CREATE VIEW IF NOT EXISTS vw_monthly_sales AS
SELECT d.year, d.month, SUM(f.sales) AS total_sales
FROM fact_sales f JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month;

CREATE VIEW IF NOT EXISTS vw_top_products AS
SELECT p.product_name, SUM(f.sales) AS total_sales
FROM fact_sales f JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_name
ORDER BY total_sales DESC;
