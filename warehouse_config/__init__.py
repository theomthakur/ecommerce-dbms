"""Warehouse initialization module"""

from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def create_warehouse_init():
    """Create __init__.py for warehouse config module"""
    init_file = Path(__file__).parent / '__init__.py'
    init_file.write_text('''"""Warehouse configuration and loading utilities"""

from .warehouse_loader import load_dw_to_warehouse, BigQueryLoader, RedshiftLoader
from .config_templates import POSTGRES_CONFIG, BIGQUERY_CONFIG, REDSHIFT_CONFIG

__all__ = [
    'load_dw_to_warehouse',
    'BigQueryLoader',
    'RedshiftLoader',
    'POSTGRES_CONFIG',
    'BIGQUERY_CONFIG',
    'REDSHIFT_CONFIG',
]
''')
    logger.info(f"Created {init_file}")


if __name__ == '__main__':
    create_warehouse_init()
