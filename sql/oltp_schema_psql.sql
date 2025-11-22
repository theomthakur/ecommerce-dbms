-- PostgreSQL version of the OLTP schema
-- Convert types for Postgres and use IDENTITY for autoincrement

CREATE SCHEMA IF NOT EXISTS public;

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    segment TEXT,
    postal_code TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    region TEXT
);

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    category TEXT,
    sub_category TEXT,
    product_name TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    order_date DATE,
    ship_date DATE,
    ship_mode TEXT,
    order_priority TEXT,
    market TEXT,
    region TEXT,
    customer_id TEXT REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id TEXT REFERENCES orders(order_id),
    product_id TEXT REFERENCES products(product_id),
    row_id INTEGER,
    quantity INTEGER,
    sales NUMERIC(14,2),
    discount NUMERIC(12,4),
    profit NUMERIC(14,2),
    shipping_cost NUMERIC(14,2)
);

CREATE TABLE IF NOT EXISTS returns (
    order_id TEXT PRIMARY KEY REFERENCES orders(order_id),
    returned_flag BOOLEAN
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orderitems_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_orderitems_product ON order_items(product_id);
