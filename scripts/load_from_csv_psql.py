#!/usr/bin/env python3
"""Load cleaned CSV files into PostgreSQL using COPY.

Usage examples:
  export DATABASE_URL='postgresql+psycopg://etl_user:etl_pass@localhost:5432/ecommerce'
  python scripts/load_from_csv_psql.py --data-dir data/

The script will look for these files in the data directory (if they exist):
 - cleaned_customers.csv -> customers
 - cleaned_products.csv -> products
 - cleaned_orders.csv -> orders
 - cleaned_order_items.csv -> order_items
 - cleaned_returns.csv -> returns

The script reads the CSV header to generate a COPY statement that matches CSV columns.
"""
import argparse
import csv
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.exc import DBAPIError
import pandas as pd
from sqlalchemy import text


MAPPINGS = {
    'cleaned_customers.csv': 'customers',
    'cleaned_products.csv': 'products',
    'cleaned_orders.csv': 'orders',
    'cleaned_order_items.csv': 'order_items',
    'cleaned_returns.csv': 'returns',
}

# Expected table columns (must match `sql/oltp_schema_psql.sql`)
TABLE_COLUMNS = {
    'customers': ['customer_id','customer_name','segment','postal_code','city','state','country','region'],
    'products': ['product_id','category','sub_category','product_name'],
    'orders': ['order_id','order_date','ship_date','ship_mode','order_priority','market','region','customer_id'],
    'order_items': ['order_id','product_id','row_id','quantity','sales','discount','profit','shipping_cost'],
    'returns': ['order_id','returned_flag'],
}


def load_csv_to_postgres(engine, csv_path: Path, table_name: str):
    print(f'Loading {csv_path} -> {table_name}')
    if not csv_path.exists():
        print(f'  Skipping, file not found: {csv_path}')
        return

    # Read header to get columns
    with csv_path.open('r', encoding='utf-8', errors='replace') as fh:
        reader = csv.reader(fh)
        try:
            headers = next(reader)
        except StopIteration:
            print('  Empty file, skipping')
            return

    # Normalize header names helper
    import re
    def normalize(h: str) -> str:
        h2 = re.sub(r"[^0-9a-zA-Z]+", "_", h).lower()
        return h2.strip('_')

    # If CSV contains columns that map to table columns, build a staged CSV
    expected = TABLE_COLUMNS.get(table_name)
    staged_path = None
    if expected:
        # build mapping from expected col -> original header name (if present)
        hdr_map = {}
        for h in headers:
            n = normalize(h)
            if n in expected:
                hdr_map[n] = h

        if set(expected).issubset(set(hdr_map.keys())):
            # create a staged CSV containing only the expected columns, with header names matching table columns
            import pandas as _pd
            df = _pd.read_csv(csv_path, dtype=str)
            reordered = [hdr_map[c] for c in expected]
            staged_df = df[reordered].copy()
            staged_df.columns = expected
            staged_path = csv_path.with_name(f"{csv_path.stem}.staged.csv")
            staged_df.to_csv(staged_path, index=False)
            cols = ','.join(expected)
        else:
            # fallback to using raw headers (may fail if headers don't match table)
            cols = ','.join([h for h in headers])
    else:
        cols = ','.join([h for h in headers])

    # Build COPY SQL now so psycopg v3 branch can use it
    sql = f"COPY {table_name} ({cols}) FROM STDIN WITH CSV HEADER"

    # Record starting row count so we can validate the COPY actually inserted rows
    try:
        with engine.connect() as _conn:
            start_cnt = _conn.execute(text(f'SELECT COUNT(*) FROM {table_name}')).scalar()
    except Exception:
        start_cnt = None

    # Try psycopg (v3) native COPY first if available. This avoids the
    # DB-API cursor differences (psycopg v3 doesn't expose copy_expert).
    try:
        import psycopg as psycopg3  # type: ignore
    except Exception:
        psycopg3 = None

    if psycopg3 is not None:
        try:
            # Build a minimal DSN from the SQLAlchemy engine URL
            u = engine.url
            dsn = []
            if u.host:
                dsn.append(f"host={u.host}")
            if u.port:
                dsn.append(f"port={u.port}")
            if u.database:
                dsn.append(f"dbname={u.database}")
            if u.username:
                dsn.append(f"user={u.username}")
            if u.password:
                dsn.append(f"password={u.password}")
            dsn = ' '.join(dsn)

            use_path = staged_path or csv_path
            # psycopg3 exposes a copy API on cursor objects; try to use it.
            with psycopg3.connect(dsn) as pconn:
                with pconn.cursor() as pcur:
                    # use cursor.copy which takes the COPY SQL and a file-like
                    # object in psycopg v3; if not available, fall through
                    if hasattr(pcur, 'copy'):
                        with use_path.open('r', encoding='utf-8', errors='replace') as f:
                            try:
                                pcur.copy(sql, f)
                                pconn.commit()
                                print('  Done (psycopg v3 COPY)')
                                # validate rows were inserted
                                try:
                                    with engine.connect() as _conn:
                                        new_cnt = _conn.execute(text(f'SELECT COUNT(*) FROM {table_name}')).scalar()
                                except Exception:
                                    new_cnt = None
                                if start_cnt is None or (new_cnt is not None and new_cnt > (start_cnt or 0)):
                                    return
                                else:
                                    print('  psycopg v3 COPY did not increase row count, will attempt fallback')
                            except Exception as e:
                                print('  psycopg v3 copy failed, falling back to DB-API methods:', e)
                    # otherwise fall-through to DB-API path
        except Exception as e:
            print('  psycopg v3 connection/copy attempt failed, falling back:', e)

    # If psycopg3 copy didn't run, try psql client-side \copy as a robust fallback
    try:
        # Build a libpq URL for psql
        u = engine.url
        user = u.username or ''
        pw = u.password or ''
        host = u.host or 'localhost'
        port = u.port or 5432
        db = u.database or ''
        if pw:
            psql_url = f"postgresql://{user}:{pw}@{host}:{port}/{db}"
        else:
            psql_url = f"postgresql://{user}@{host}:{port}/{db}"
        use_path = staged_path or csv_path
        psql_cmd = [
            'psql', psql_url,
            '-c', f"\\copy {table_name} ({cols}) FROM '{use_path}' WITH CSV HEADER"
        ]
        print('  Attempting psql \copy fallback...')
        import subprocess
        res = subprocess.run(psql_cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print('  Done (psql \copy)')
            # validate rows were inserted
            try:
                with engine.connect() as _conn:
                    new_cnt = _conn.execute(text(f'SELECT COUNT(*) FROM {table_name}')).scalar()
            except Exception:
                new_cnt = None
            if start_cnt is None or (new_cnt is not None and new_cnt > (start_cnt or 0)):
                return
            else:
                print('  psql \copy did not increase row count, continuing to DB-API fallback')
        else:
            print('  psql \copy failed:', res.stderr.strip())
    except Exception as e:
        print('  psql \copy attempt failed, continuing to DB-API fallback:', e)

    # Use raw connection and psycopg COPY for best performance.
    # SQLAlchemy 2.x's raw_connection() return value doesn't support the
    # context manager protocol, so manage it explicitly for compatibility.
    raw_conn = engine.raw_connection()
    try:
        cur = raw_conn.cursor()
        sql = f"COPY {table_name} ({cols}) FROM STDIN WITH CSV HEADER"
        # psycopg2 exposes `copy_expert`; psycopg (v3) may not. Provide a
        # compatibility fallback that uses pandas.to_sql if COPY isn't
        # available on the DB-API cursor.
        if hasattr(cur, 'copy_expert'):
            # choose file: staged if present else original
            use_path = staged_path or csv_path
            with use_path.open('r', encoding='utf-8', errors='replace') as f:
                cur.copy_expert(sql, f)
            raw_conn.commit()
        else:
            # Fallback: use pandas to load in chunks via SQLAlchemy
            print('  COPY not available on cursor; falling back to pandas.to_sql (slower)')
            df = pd.read_csv(csv_path, dtype=str)
            # Ensure no empty dataframe
            if not df.empty:
                # Try progressively smaller chunksizes if the DB complains about too many parameters
                inserted = False
                for chunksize in (500, 200, 100, 50, 10):
                    try:
                        df.to_sql(table_name, engine, if_exists='append', index=False, method='multi', chunksize=chunksize)
                        inserted = True
                        break
                    except DBAPIError as e:
                        msg = str(e).lower()
                        # If it's a parameter/statement-size related complaint, retry smaller chunks
                        if 'too many' in msg or 'parameter' in msg or 'statement' in msg or 'argument' in msg:
                            print(f'    chunksize {chunksize} failed due to DB limits, retrying smaller chunk')
                            continue
                        else:
                            raise
                if not inserted:
                    raise RuntimeError(f'Failed to insert rows into {table_name} via pandas.to_sql; consider installing psycopg2 or enabling COPY support')
    finally:
        try:
            raw_conn.close()
        except Exception:
            pass
    print('  Done')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', default='data', help='Directory containing cleaned CSVs')
    parser.add_argument('--database-url', default=os.environ.get('DATABASE_URL'), help='SQLAlchemy DB URL (or set DATABASE_URL)')
    args = parser.parse_args()

    db_url = args.database_url
    if not db_url:
        raise SystemExit('DATABASE_URL not provided; set DATABASE_URL or use --database-url')

    engine = create_engine(db_url)
    data_dir = Path(args.data_dir)

    for fname, table in MAPPINGS.items():
        path = data_dir / fname
        load_csv_to_postgres(engine, path, table)


if __name__ == '__main__':
    main()
