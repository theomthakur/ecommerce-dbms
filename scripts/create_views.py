#!/usr/bin/env python3
"""Create SQL views in DW and OLTP databases from SQL files."""
from pathlib import Path
from . import db as db_module


def apply_sql(db_path: Path, sql_file: Path):
    engine = db_module.get_engine(str(db_path))
    sql_text = sql_file.read_text()
    raw_conn = engine.raw_connection()
    try:
        raw_conn.executescript(sql_text)
    finally:
        raw_conn.close()


def main():
    root = Path(__file__).resolve().parents[1]
    dw = root / 'dw.db'
    views = root / 'sql' / 'views.sql'
    if views.exists():
        apply_sql(dw, views)
        print('Applied views to', dw)
    else:
        print('No views.sql found')


if __name__ == '__main__':
    main()
