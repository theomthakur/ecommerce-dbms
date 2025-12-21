"""dbt initialization and utilities"""

from pathlib import Path
import logging
import subprocess
import os

logger = logging.getLogger(__name__)

DBT_DIR = Path(__file__).resolve().parent / 'dbt'


def run_dbt_command(command: str, target: str = None, profiles_dir: str = None):
    """Run dbt command and capture output"""
    if profiles_dir is None:
        profiles_dir = str(DBT_DIR)
    
    cmd = ['dbt', command, '--profiles-dir', profiles_dir]
    if target:
        cmd.extend(['--target', target])
    
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(DBT_DIR), capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error(f"dbt command failed: {result.stderr}")
        raise RuntimeError(f"dbt {command} failed: {result.stderr}")
    
    logger.info(result.stdout)
    return result.stdout


def validate_dbt_project(target: str = None):
    """Validate dbt project configuration"""
    logger.info("Validating dbt project...")
    return run_dbt_command('parse', target=target)


def run_dbt_models(select: str = None, target: str = None):
    """Run dbt models"""
    cmd = 'run'
    if select:
        cmd += f' --select {select}'
    logger.info(f"Running dbt models: {select or 'all'}")
    return run_dbt_command(cmd, target=target)


def run_dbt_tests(select: str = None, target: str = None):
    """Run dbt tests"""
    cmd = 'test'
    if select:
        cmd += f' --select {select}'
    logger.info(f"Running dbt tests: {select or 'all'}")
    return run_dbt_command(cmd, target=target)


def generate_dbt_docs(target: str = None):
    """Generate dbt documentation"""
    logger.info("Generating dbt documentation...")
    return run_dbt_command('docs generate', target=target)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    validate_dbt_project()
    print("✅ dbt project is valid")
