#!/usr/bin/env python3
"""Build Data Warehouse (star schema) from OLTP SQLite DB.

Usage:
    python scripts/build_dw.py --oltp oltp.db --dw dw.db
"""
import argparse
from pathlib import Path
import pandas as pd
from sqlalchemy import text
import sys
from pathlib import Path as _Path
# Ensure repo root is on sys.path so `import scripts.*` works when running the script directly
_ROOT = _Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import scripts.db as db_module
import scripts.logger as logger_module

logger = logger_module.get_logger('build_dw')


def create_dim_date(df_dates: pd.Series) -> pd.DataFrame:
    s = pd.to_datetime(df_dates.dropna().unique())
    df = pd.DataFrame({'date': s})
    df['date_key'] = df['date'].dt.strftime('%Y%m%d').astype(int)
    df['year'] = df['date'].dt.year
    df['quarter'] = df['date'].dt.quarter
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['weekday'] = df['date'].dt.weekday
    df['is_weekend'] = df['weekday'].isin([5,6])
    return df[['date_key','date','year','quarter','month','day','weekday','is_weekend']]


def build_dw(oltp_db: Path, dw_db: Path):
    engine_oltp = db_module.get_engine(str(oltp_db))
    engine_dw = db_module.get_engine(str(dw_db))

    orders = pd.read_sql_table('orders', engine_oltp)
    order_items = pd.read_sql_table('order_items', engine_oltp)
    customers = pd.read_sql_table('customers', engine_oltp)
    products = pd.read_sql_table('products', engine_oltp)

    # dim_date
    dim_date = create_dim_date(orders['order_date'])

    # dim_customer
    dim_customer = customers.copy()
    dim_customer['customer_key'] = range(1, len(dim_customer) + 1)
    dim_customer = dim_customer[['customer_key','customer_id','customer_name','segment','city','state','country','postal_code']]

    # dim_product
    dim_product = products.copy()
    dim_product['product_key'] = range(1, len(dim_product) + 1)
    dim_product = dim_product[['product_key','product_id','category','sub_category','product_name']]

    # dim_region
    # Regions derived from orders and customers
    regions = pd.DataFrame(sorted(set(list(orders['region'].dropna().unique()) + list(customers['region'].dropna().unique()))), columns=['region'])
    regions['region_key'] = range(1, len(regions) + 1)
    dim_region = regions[['region_key','region']]

    # Prepare fact table by joining
    # Join order_items -> orders to get order_date, customer_id, region
    merged = order_items.merge(orders[['order_id','order_date','customer_id','region']], on='order_id', how='left')

    # map to keys
    merged = merged.merge(dim_customer[['customer_key','customer_id']], on='customer_id', how='left')
    merged = merged.merge(dim_product[['product_key','product_id']], on='product_id', how='left')
    merged = merged.merge(dim_region, on='region', how='left')

    merged['date_key'] = pd.to_datetime(merged['order_date']).dt.strftime('%Y%m%d').astype(int)

    # Ensure numeric columns are properly typed in the fact table
    for col in ['quantity','sales','discount','profit','shipping_cost']:
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors='coerce').fillna(0.0)

    fact_sales = merged.rename(columns={'order_id':'order_id'})
    fact_sales = fact_sales[['date_key','customer_key','product_key','region_key','order_id','quantity','sales','discount','profit','shipping_cost']]

    # Write schema SQL if present
    sql_file = Path(__file__).resolve().parents[1] / 'sql' / 'dw_schema.sql'
    if sql_file.exists():
        sql_text = sql_file.read_text()
        raw_conn = engine_dw.raw_connection()
        try:
            raw_conn.executescript(sql_text)
        finally:
            raw_conn.close()

    # Save dims and facts
    dim_date.to_sql('dim_date', engine_dw, if_exists='replace', index=False)
    dim_customer.to_sql('dim_customer', engine_dw, if_exists='replace', index=False)
    dim_product.to_sql('dim_product', engine_dw, if_exists='replace', index=False)
    dim_region.to_sql('dim_region', engine_dw, if_exists='replace', index=False)
    fact_sales.to_sql('fact_sales', engine_dw, if_exists='replace', index=False)

    logger.info('DW written to %s — dim_date: %s, dim_customer: %s, dim_product: %s, facts: %s', dw_db, len(dim_date), len(dim_customer), len(dim_product), len(fact_sales))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--oltp', required=True, help='OLTP SQLite DB file')
    parser.add_argument('--dw', default='dw.db', help='Output DW SQLite DB file')
    args = parser.parse_args()
    build_dw(Path(args.oltp), Path(args.dw))


if __name__ == '__main__':
    main()
