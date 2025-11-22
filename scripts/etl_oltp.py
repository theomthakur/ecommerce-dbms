#!/usr/bin/env python3
"""ETL script: Clean CSVs and populate normalized OLTP SQLite DB (oltp.db).

Usage:
    python scripts/etl_oltp.py --orders data/Awesome_Inc_Superstore_Orders.csv --returns data/Awesome_Inc_Superstore_Returns.csv
"""
import argparse
import logging
from pathlib import Path
import pandas as pd
from sqlalchemy import text
import sys
from pathlib import Path as _Path
# Ensure repo root is on sys.path so `import scripts.*` works when running the script directly
_ROOT = _Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import scripts.transform as transform_module
import scripts.logger as logger_module
import scripts.db as db_module

# module logger
logger = logger_module.get_logger('etl')


def build_oltp(orders_csv: Path, returns_csv: Path, out_db: Path = Path('oltp.db')):
    # Use a permissive encoding to handle special characters in the CSVs
    orders = pd.read_csv(orders_csv, dtype=str, encoding='latin1', low_memory=False)
    returns = pd.read_csv(returns_csv, dtype=str, encoding='latin1', low_memory=False)

    # Use central transform functions
    orders = transform_module.clean_orders(orders)
    returns = transform_module.clean_returns(returns)

    # Build customers
    customers = orders[['Customer ID', 'Customer Name', 'Segment', 'Postal Code', 'City', 'State', 'Country', 'Region']].drop_duplicates()
    customers.columns = ['customer_id', 'customer_name', 'segment', 'postal_code', 'city', 'state', 'country', 'region']

    # Build products
    products = orders[['Product ID', 'Category', 'Sub-Category', 'Product Name']].drop_duplicates()
    products.columns = ['product_id', 'category', 'sub_category', 'product_name']

    # Orders - unique orders (one row per order)
    orders_unique = orders[['Order ID', 'Order Date', 'Ship Date', 'Ship Mode', 'Order Priority', 'Market', 'Region', 'Customer ID']].drop_duplicates()
    orders_unique.columns = ['order_id', 'order_date', 'ship_date', 'ship_mode', 'order_priority', 'market', 'region', 'customer_id']

    # Order items - keep numeric metrics per row
    order_items = orders[['Row ID', 'Order ID', 'Product ID', 'Quantity', 'Sales', 'Discount', 'Profit', 'Shipping Cost']].copy()
    order_items.columns = ['row_id', 'order_id', 'product_id', 'quantity', 'sales', 'discount', 'profit', 'shipping_cost']
    order_items['quantity'] = pd.to_numeric(order_items['quantity'], errors='coerce').fillna(0).astype(int)
    # Normalize returns
    returns.columns = ['Returned', 'Order ID', 'Region'] if list(returns.columns[:3]) == ['Returned', 'Order ID', 'Region'] else list(returns.columns)
    returns = returns.rename(columns={returns.columns[0]:'returned_flag', returns.columns[1]:'order_id'})

    # Write to SQLite using SQLAlchemy engine
    engine = db_module.get_engine(str(out_db))

    # Create schema from SQL file if present
    sql_file = Path(__file__).resolve().parents[1] / 'sql' / 'oltp_schema.sql'
    if sql_file.exists():
        sql_text = sql_file.read_text()
        # Use raw_connection().executescript to run multiple statements in sqlite
        raw_conn = engine.raw_connection()
        try:
            raw_conn.executescript(sql_text)
        finally:
            raw_conn.close()

    # Upsert via replace for simplicity
    customers.to_sql('customers', engine, if_exists='replace', index=False)
    products.to_sql('products', engine, if_exists='replace', index=False)
    orders_unique.to_sql('orders', engine, if_exists='replace', index=False)
    order_items.to_sql('order_items', engine, if_exists='replace', index=False)
    returns.to_sql('returns', engine, if_exists='replace', index=False)

    # Write cleaned CSVs for reproducibility / notebook use
    data_dir = Path(orders_csv).parent
    try:
        customers.to_csv(data_dir / 'cleaned_customers.csv', index=False)
        products.to_csv(data_dir / 'cleaned_products.csv', index=False)
        orders.to_csv(data_dir / 'cleaned_orders.csv', index=False)
        order_items.to_csv(data_dir / 'cleaned_order_items.csv', index=False)
        returns.to_csv(data_dir / 'cleaned_returns.csv', index=False)
    except Exception:
        # best-effort write; do not fail the ETL for CSV write issues
        pass

    # Add basic indexes
    with engine.begin() as conn:
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);'))
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_items_order ON order_items(order_id);'))
        conn.execute(text('CREATE INDEX IF NOT EXISTS idx_items_product ON order_items(product_id);'))

    # Simple validations
    with engine.connect() as conn:
        cnt_orders = conn.execute(text('SELECT COUNT(*) FROM orders')).scalar()
        cnt_items = conn.execute(text('SELECT COUNT(*) FROM order_items')).scalar()
        cnt_customers = conn.execute(text('SELECT COUNT(*) FROM customers')).scalar()
    logger.info('OLTP DB written to %s — orders: %s, order_items: %s, customers: %s', out_db, cnt_orders, cnt_items, cnt_customers)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--orders', required=True, help='Path to Orders CSV')
    parser.add_argument('--returns', required=True, help='Path to Returns CSV')
    parser.add_argument('--out', default='oltp.db', help='Output SQLite DB file')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    build_oltp(Path(args.orders), Path(args.returns), Path(args.out))


if __name__ == '__main__':
    main()
