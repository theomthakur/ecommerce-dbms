import os
import sqlite3
from pathlib import Path


def test_oltp_exists():
    assert Path('oltp.db').exists(), 'oltp.db should exist'


def test_dw_exists():
    assert Path('dw.db').exists(), 'dw.db should exist'


def test_dw_tables_nonempty():
    con = sqlite3.connect('dw.db')
    cur = con.cursor()
    cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='fact_sales'")
    assert cur.fetchone()[0] == 1, 'fact_sales table should exist'
    cur.execute('SELECT COUNT(*) FROM fact_sales')
    cnt = cur.fetchone()[0]
    assert cnt > 0, 'fact_sales should contain rows'
    con.close()
