-- Data Warehouse (Star Schema) DDL

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY, -- YYYYMMDD
    date DATE,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    day INTEGER,
    weekday INTEGER,
    is_weekend BOOLEAN
);

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT,
    customer_name TEXT,
    segment TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    postal_code TEXT
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_key INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT,
    category TEXT,
    sub_category TEXT,
    product_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_region (
    region_key INTEGER PRIMARY KEY AUTOINCREMENT,
    region TEXT
);

CREATE TABLE IF NOT EXISTS fact_sales (
    fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_key INTEGER,
    customer_key INTEGER,
    product_key INTEGER,
    region_key INTEGER,
    order_id TEXT,
    quantity INTEGER,
    sales REAL,
    discount REAL,
    profit REAL,
    shipping_cost REAL,
    FOREIGN KEY(date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY(customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY(product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY(region_key) REFERENCES dim_region(region_key)
);
