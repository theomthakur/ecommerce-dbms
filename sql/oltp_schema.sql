-- OLTP normalized schema DDL
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT,
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
    customer_id TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT,
    product_id TEXT,
    row_id INTEGER,
    quantity INTEGER,
    sales REAL,
    discount REAL,
    profit REAL,
    shipping_cost REAL,
    FOREIGN KEY(order_id) REFERENCES orders(order_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS returns (
    order_id TEXT PRIMARY KEY,
    returned_flag TEXT
);

-- Useful indexes
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orderitems_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_orderitems_product ON order_items(product_id);
