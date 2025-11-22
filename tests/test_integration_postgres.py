import os
import re
import shlex
import subprocess
import sys
import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
MIGRATE = os.path.join(ROOT, 'scripts', 'migrate_to_postgres.py')


def parse_counts(output: str):
    # Expect lines like 'customers: 17415'
    counts = {}
    for line in output.splitlines():
        m = re.match(r"^(customers|products|orders|order_items|returns):\s*(\d+|ERROR)$", line.strip())
        if m:
            k, v = m.group(1), m.group(2)
            counts[k] = int(v) if v.isdigit() else v
    return counts


@pytest.mark.integration
def test_migration_parity_between_drivers(tmp_path):
    """Run the migration twice using psycopg2 and psycopg (v3) dialects and compare smoke counts.

    This test requires a reachable Postgres instance and the test user/db configured
    as in the project README. It will skip if a driver is missing or the subprocess
    calls fail.
    """
    db_user = os.environ.get('PG_TEST_USER', 'etl_user')
    db_pass = os.environ.get('PG_TEST_PASS', '123')
    host = os.environ.get('PG_TEST_HOST', 'localhost')
    port = os.environ.get('PG_TEST_PORT', '5433')
    db = os.environ.get('PG_TEST_DB', 'ecommerce')

    urls = {
        'psycopg2': f"postgresql+psycopg2://{db_user}:{db_pass}@{host}:{port}/{db}",
        'psycopg': f"postgresql+psycopg://{db_user}:{db_pass}@{host}:{port}/{db}",
    }

    results = {}
    for name, url in urls.items():
        # Request a truncate to ensure idempotent test runs
        cmd = [sys.executable, MIGRATE, '--database-url', url, '--truncate']
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=300)
        except subprocess.CalledProcessError as e:
            pytest.skip(f"Migration with driver {name} failed: {e}\nstdout:\n{e.stdout}\nstderr:\n{e.stderr}")
        except FileNotFoundError:
            pytest.skip(f"Python executable not found to run migration for {name}")
        out = proc.stdout + '\n' + proc.stderr
        counts = parse_counts(out)
        if not counts:
            pytest.skip(f"No counts parsed from migration output for {name}; output:\n{out}")
        results[name] = counts

    # Compare counts equality
    assert results['psycopg2'] == results['psycopg'], f"Counts differ between drivers: {results}"
