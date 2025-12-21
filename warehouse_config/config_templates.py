"""Environment configuration templates for different warehouses"""

# PostgreSQL Configuration
POSTGRES_CONFIG = {
    'database': 'ecommerce_dw',
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
}

# BigQuery Configuration
BIGQUERY_CONFIG = {
    'project_id': 'YOUR_GCP_PROJECT_ID',
    'dataset_id': 'ecommerce_dw',
    'credentials_path': '/path/to/service-account-key.json',
    'location': 'US',
}

# Redshift Configuration
REDSHIFT_CONFIG = {
    'host': 'your-redshift-cluster.region.redshift.amazonaws.com',
    'port': 5439,
    'database': 'ecommerce_dw',
    'user': 'admin',
    'password': 'YourPassword123!',
    'schema': 'public',
}

# Snowflake Configuration
SNOWFLAKE_CONFIG = {
    'account': 'your_account.region',
    'user': 'your_user',
    'password': 'your_password',
    'warehouse': 'ecommerce_wh',
    'database': 'ecommerce_dw',
    'schema': 'public',
}
