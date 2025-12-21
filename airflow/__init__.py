"""Airflow initialization and configuration"""

from airflow import configuration
from pathlib import Path

# Set AIRFLOW_HOME if not set
AIRFLOW_HOME = Path(__file__).resolve().parent
configuration.conf.set('core', 'airflow_home', str(AIRFLOW_HOME))
configuration.conf.set('core', 'dags_folder', str(AIRFLOW_HOME / 'dags'))
configuration.conf.set('core', 'plugins_folder', str(AIRFLOW_HOME / 'plugins'))
configuration.conf.set('core', 'executor', 'LocalExecutor')
configuration.conf.set('database', 'sql_alchemy_conn', f'sqlite:///{AIRFLOW_HOME}/airflow.db')
configuration.conf.set('core', 'load_examples', 'False')
