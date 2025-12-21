#!/bin/bash
# Quick start guide for modern analytics stack

set -e

echo "🚀 Quick Start: Modern Analytics Stack"
echo "======================================"
echo ""

AIRFLOW_HOME="./airflow"

# Check if Airflow is initialized
if [ ! -f "$AIRFLOW_HOME/airflow.db" ]; then
    echo "❌ Airflow not initialized!"
    echo "Run: bash setup_analytics_stack.sh"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Copy .env.template and configure your warehouse credentials"
    exit 1
fi

# Start services
echo "Starting Airflow services..."
echo ""

# Create logs directory
mkdir -p $AIRFLOW_HOME/logs

# Start webserver in background
echo "📡 Starting Airflow Web Server..."
nohup airflow webserver --port 8080 > $AIRFLOW_HOME/logs/webserver.log 2>&1 &
WEBSERVER_PID=$!
echo "   Webserver PID: $WEBSERVER_PID"

# Give webserver time to start
sleep 5

# Start scheduler in background
echo "📅 Starting Airflow Scheduler..."
nohup airflow scheduler > $AIRFLOW_HOME/logs/scheduler.log 2>&1 &
SCHEDULER_PID=$!
echo "   Scheduler PID: $SCHEDULER_PID"

# Give scheduler time to start
sleep 5

echo ""
echo "✅ Services started!"
echo ""
echo "📊 Access Dashboard: http://localhost:8080"
echo "   Default Username: admin"
echo ""
echo "📝 Available DAGs:"
airflow dags list | tail -n +3
echo ""
echo "💡 Trigger main DAG:"
echo "   airflow dags trigger ecommerce_etl_pipeline"
echo ""
echo "📖 View logs:"
echo "   tail -f $AIRFLOW_HOME/logs/webserver.log"
echo "   tail -f $AIRFLOW_HOME/logs/scheduler.log"
echo ""
echo "🛑 Stop services:"
echo "   kill $WEBSERVER_PID $SCHEDULER_PID"
echo "   # or simply Ctrl+C in each terminal"
echo ""
