#!/usr/bin/env python3
"""Wrapper to migrate cleaned CSVs into Postgres and run DDL + COPY loader.

Features:
- Optionally run the existing ETL to produce cleaned CSV snapshots if missing.
- Prepare a temporary load directory where `cleaned_returns.csv` is normalized to boolean values.
- Apply `sql/oltp_schema_psql.sql` to the target database.
- Invoke `scripts/load_from_csv_psql.py --data-dir <tmp>` to COPY CSVs.
- Print simple row counts for a smoke test.

Usage:
  export DATABASE_URL='postgresql+psycopg://etl_user:etl_pass@localhost:5432/ecommerce'
  python scripts/migrate_to_postgres.py --run-etl

"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
PG_LOAD_DIR = DATA_DIR / 'pg_load'
DDL_FILE = ROOT / 'sql' / 'oltp_schema_psql.sql'
ETL_SCRIPT = ROOT / 'scripts' / 'etl_oltp.py'
LOADER = ROOT / 'scripts' / 'load_from_csv_psql.py'


def ensure_cleaned_csvs(run_etl: bool):
    # Expected cleaned CSV filenames produced by ETL
    expected = [
        'cleaned_customers.csv',
        'cleaned_products.csv',
        'cleaned_orders.csv',
        'cleaned_order_items.csv',
        'cleaned_returns.csv',
    ]
    missing = [f for f in expected if not (DATA_DIR / f).exists()]
    if missing:
        if not run_etl:
            raise SystemExit(f'Missing cleaned CSVs: {missing}. Rerun with --run-etl to generate them')
        # Run ETL script to generate cleaned CSVs. Attempt to locate source files in data/
        orders_src = DATA_DIR / 'Awesome_Inc_Superstore_Orders.csv'
        returns_src = DATA_DIR / 'Awesome_Inc_Superstore_Returns.csv'
        if not orders_src.exists() or not returns_src.exists():
            raise SystemExit('Source CSVs not found in data/. Cannot run ETL')
        cmd = [sys.executable, str(ETL_SCRIPT), '--orders', str(orders_src), '--returns', str(returns_src), '--out', 'oltp.db']
        print('Running ETL to produce cleaned CSVs:',' '.join(cmd))
        subprocess.run(cmd, check=True)


def prepare_pg_load_dir():
    if PG_LOAD_DIR.exists():
        shutil.rmtree(PG_LOAD_DIR)
    PG_LOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Copy cleaned CSVs; normalize returns
    files_to_copy = [
        'cleaned_customers.csv',
        'cleaned_products.csv',
        'cleaned_orders.csv',
        'cleaned_order_items.csv',
        'cleaned_returns.csv',
    ]
    for fname in files_to_copy:
        src = DATA_DIR / fname
        dst = PG_LOAD_DIR / fname
        if not src.exists():
            print(f'Warning: {src} not found; skipping')
            continue
        if fname == 'cleaned_returns.csv':
            # Normalize common values to TRUE/FALSE/\n
            df = pd.read_csv(src, dtype=str, keep_default_na=False)
            if 'returned_flag' in df.columns:
                df['returned_flag'] = df['returned_flag'].str.strip().str.lower().map(
                    {'yes': 'TRUE', 'y': 'TRUE', 'true': 'TRUE', '1': 'TRUE', 'no': 'FALSE', 'n': 'FALSE', 'false': 'FALSE', '0': 'FALSE'}).where(lambda s: s.notna(), None)
            else:
                # If column not present, try to detect likely flag column names
                for c in df.columns:
                    if 'return' in c.lower():
                        df[c] = df[c].str.strip().str.lower().map(
                            {'yes': 'TRUE', 'y': 'TRUE', 'true': 'TRUE', '1': 'TRUE', 'no': 'FALSE', 'n': 'FALSE', 'false': 'FALSE', '0': 'FALSE'}).where(lambda s: s.notna(), None)
            df.to_csv(dst, index=False)
            print(f'Prepared normalized returns CSV -> {dst}')
        else:
            # For potentially large tables (customers, orders) perform non-destructive dedupe
            # and write the deduped/staged CSV to PG_LOAD_DIR so source CSVs are not mutated.
            if fname in ('cleaned_customers.csv', 'cleaned_orders.csv'):
                try:
                    df = pd.read_csv(src, dtype=str, keep_default_na=False)
                    before = len(df)
                    df = df.drop_duplicates()
                    after = len(df)
                    df.to_csv(dst, index=False)
                    print(f'Copied and deduped {src} -> {dst} (rows: {before} -> {after})')
                except Exception:
                    # If anything goes wrong reading/deduping, fall back to raw copy
                    shutil.copy2(src, dst)
                    print(f'Copied (no dedupe) {src} -> {dst}')
            else:
                shutil.copy2(src, dst)
                print(f'Copied {src} -> {dst}')


def apply_ddl(engine):
    if not DDL_FILE.exists():
        raise SystemExit(f'DDL file not found: {DDL_FILE}')
    sql_text = DDL_FILE.read_text()
    # split into statements by semicolon to avoid driver-specific multi-statement issues
    stmts = [s.strip() for s in sql_text.split(';') if s.strip()]
    with engine.begin() as conn:
        for stmt in stmts:
            # exec_driver_sql works for raw SQL statements
            conn.exec_driver_sql(stmt)
    print('Applied DDL')


def truncate_tables(engine):
    """Truncate target OLTP tables to provide idempotent loads during testing/reruns."""
    tables = ['customers', 'products', 'orders', 'order_items', 'returns']
    with engine.begin() as conn:
        conn.exec_driver_sql(f"TRUNCATE {', '.join(tables)} RESTART IDENTITY CASCADE;")
    print('Truncated target tables')


def run_loader(db_url):
    cmd = [sys.executable, str(LOADER), '--data-dir', str(PG_LOAD_DIR), '--database-url', db_url]
    print('Running loader:', ' '.join(cmd))
    subprocess.run(cmd, check=True)


def print_counts(engine):
    tables = ['customers', 'products', 'orders', 'order_items', 'returns']
    with engine.connect() as conn:
        for t in tables:
            try:
                res = conn.execute(text(f'SELECT COUNT(*) FROM {t}'))
                cnt = res.scalar()
            except Exception:
                cnt = 'ERROR'
            print(f'{t}: {cnt}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--database-url', default=os.environ.get('DATABASE_URL'))
    parser.add_argument('--run-etl', action='store_true', help='Run ETL to generate cleaned CSVs if missing')
    parser.add_argument('--truncate', action='store_true', help='Truncate target tables before loading')
    args = parser.parse_args()

    db_url = args.database_url
    if not db_url:
        raise SystemExit('Please provide --database-url or set DATABASE_URL environment variable')

    ensure_cleaned_csvs(args.run_etl)
    prepare_pg_load_dir()

    engine = create_engine(db_url)
    print('Applying Postgres DDL...')
    apply_ddl(engine)

    if args.truncate:
        print('Truncating target tables...')
        truncate_tables(engine)

    print('Running COPY loader...')
    run_loader(db_url)

    print('\nRow counts (smoke test):')
    print_counts(engine)


if __name__ == '__main__':
    main()
