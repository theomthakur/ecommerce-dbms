import os
from sqlalchemy import create_engine


def get_engine(sqlite_path: str = "oltp.db"):
    """Return a SQLAlchemy engine.

    Behavior:
    - If the environment variable `DATABASE_URL` is set, create an engine from it
      (useful for PostgreSQL or other SQLAlchemy-compatible DBs).
    - Otherwise fall back to a local SQLite file at `sqlite_path`.
    """
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        # allow callers to configure pool size via env if desired; keep defaults reasonable
        return create_engine(db_url, pool_size=10, max_overflow=20)
    return create_engine(f"sqlite:///{sqlite_path}")
