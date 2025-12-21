"""Warehouse loader for BigQuery and Redshift"""

import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class BigQueryLoader:
    """Load data warehouse to BigQuery"""
    
    def __init__(self, project_id: str, dataset_id: str):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize BigQuery client"""
        try:
            from google.cloud import bigquery
            self.client = bigquery.Client(project=self.project_id)
            logger.info(f"BigQuery client initialized for project {self.project_id}")
        except ImportError:
            logger.error("google-cloud-bigquery not installed")
            raise
    
    def load_from_postgres(self, source_db: str, warehouse_type: str = 'bigquery'):
        """Load data from PostgreSQL to BigQuery"""
        import sqlite3
        import pandas as pd
        
        tables = ['customers', 'products', 'orders', 'order_items', 'returns']
        
        # Connect to source database
        conn = sqlite3.connect(source_db)
        
        for table in tables:
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                table_id = f"{self.project_id}.{self.dataset_id}.{table}"
                
                job_config = bigquery.LoadJobConfig(
                    write_disposition='WRITE_TRUNCATE',
                    autodetect=True,
                )
                
                job = self.client.load_table_from_dataframe(
                    df, table_id, job_config=job_config
                )
                job.result()
                
                logger.info(f"Loaded {table} to BigQuery: {table_id}")
            except Exception as e:
                logger.error(f"Error loading {table}: {e}")
                raise
        
        conn.close()


class RedshiftLoader:
    """Load data warehouse to Redshift"""
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str, schema: str = 'public'):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.schema = schema
        self.conn = None
        self._init_connection()
    
    def _init_connection(self):
        """Initialize Redshift connection"""
        try:
            import psycopg2
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
            )
            logger.info(f"Connected to Redshift: {self.host}:{self.port}/{self.database}")
        except Exception as e:
            logger.error(f"Failed to connect to Redshift: {e}")
            raise
    
    def load_from_postgres(self, source_db: str):
        """Load data from PostgreSQL to Redshift using COPY"""
        import sqlite3
        import pandas as pd
        
        tables = ['customers', 'products', 'orders', 'order_items', 'returns']
        
        # Connect to source database
        source_conn = sqlite3.connect(source_db)
        cursor = self.conn.cursor()
        
        for table in tables:
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table}", source_conn)
                
                # Create table if not exists
                self._create_table(cursor, table, df)
                
                # Load data using COPY
                self._copy_data(cursor, table, df)
                self.conn.commit()
                
                logger.info(f"Loaded {table} to Redshift")
            except Exception as e:
                self.conn.rollback()
                logger.error(f"Error loading {table}: {e}")
                raise
        
        cursor.close()
        source_conn.close()
    
    def _create_table(self, cursor, table_name: str, df):
        """Create table in Redshift if not exists"""
        # Determine column types from dataframe
        columns = []
        for col, dtype in df.dtypes.items():
            if 'int' in str(dtype):
                col_type = 'INTEGER'
            elif 'float' in str(dtype):
                col_type = 'DECIMAL(10,2)'
            elif 'datetime' in str(dtype):
                col_type = 'TIMESTAMP'
            else:
                col_type = 'VARCHAR(255)'
            columns.append(f"{col} {col_type}")
        
        create_sql = f"CREATE TABLE IF NOT EXISTS {self.schema}.{table_name} ({', '.join(columns)})"
        cursor.execute(create_sql)
    
    def _copy_data(self, cursor, table_name: str, df):
        """Copy data to Redshift"""
        # Convert dataframe to CSV and use COPY command
        import io
        
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, header=False)
        buffer.seek(0)
        
        cursor.copy_from(
            buffer,
            f"{self.schema}.{table_name}",
            sep=',',
        )


def load_dw_to_warehouse(
    dw_db: str,
    warehouse_type: str = 'bigquery',
    **kwargs
):
    """Main function to load DW to target warehouse"""
    logger.info(f"Loading DW to {warehouse_type}...")
    
    if warehouse_type == 'bigquery':
        project_id = kwargs.get('project_id') or os.getenv('GCP_PROJECT_ID')
        dataset_id = kwargs.get('dataset_id') or os.getenv('BIGQUERY_DATASET', 'ecommerce_dw')
        
        loader = BigQueryLoader(project_id, dataset_id)
        loader.load_from_postgres(dw_db)
        
    elif warehouse_type == 'redshift':
        host = kwargs.get('host') or os.getenv('REDSHIFT_HOST')
        port = int(kwargs.get('port', 5439) or os.getenv('REDSHIFT_PORT', 5439))
        database = kwargs.get('database') or os.getenv('REDSHIFT_DBNAME', 'ecommerce_dw')
        user = kwargs.get('user') or os.getenv('REDSHIFT_USER')
        password = kwargs.get('password') or os.getenv('REDSHIFT_PASSWORD')
        schema = kwargs.get('schema') or os.getenv('REDSHIFT_SCHEMA', 'public')
        
        loader = RedshiftLoader(host, port, database, user, password, schema)
        loader.load_from_postgres(dw_db)
    
    else:
        raise ValueError(f"Unsupported warehouse type: {warehouse_type}")
    
    logger.info(f"Successfully loaded DW to {warehouse_type}")
