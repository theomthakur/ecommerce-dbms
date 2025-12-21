#!/bin/bash
# Initialize modern analytics stack

set -e

echo "🚀 Initializing Modern Analytics Stack..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install -r requirements.txt --upgrade

# 2. Setup Airflow
echo -e "${BLUE}✈️  Setting up Airflow...${NC}"
export AIRFLOW_HOME=./airflow
mkdir -p $AIRFLOW_HOME/logs $AIRFLOW_HOME/plugins

airflow db init

# Create default admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@company.com \
    || echo "Admin user already exists"

# Set Airflow variables
airflow variables set orders_csv_path "$(pwd)/data/Awesome_Inc_Superstore_Orders.csv"
airflow variables set returns_csv_path "$(pwd)/data/Awesome_Inc_Superstore_Returns.csv"
airflow variables set oltp_db_path "$(pwd)/data/oltp.db"
airflow variables set dw_db_path "$(pwd)/data/dw.db"
airflow variables set warehouse_type "postgres"

echo -e "${GREEN}✅ Airflow initialized${NC}"

# 3. Setup dbt
echo -e "${BLUE}🔧 Configuring dbt...${NC}"
cd dbt

# Test connection
if dbt debug --profiles-dir . 2>/dev/null; then
    echo -e "${GREEN}✅ dbt connection successful${NC}"
else
    echo -e "${BLUE}⚠️  dbt connection test skipped (configure warehouse in profiles.yml)${NC}"
fi

cd ..

# 4. Setup Great Expectations
echo -e "${BLUE}✓ Setting up Great Expectations...${NC}"
mkdir -p great_expectations/stores
mkdir -p great_expectations/validations
mkdir -p great_expectations/data_docs

# 5. Create environment template
echo -e "${BLUE}📋 Creating .env template...${NC}"
if [ ! -f .env ]; then
    cp warehouse_config/.env.template .env
    echo -e "${GREEN}✅ Created .env file (edit with your credentials)${NC}"
else
    echo -e "${GREEN}ℹ️  .env file already exists${NC}"
fi

# 6. Summary
echo -e "\n${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Modern Analytics Stack initialized!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}\n"

echo "📚 Next steps:"
echo "1. Edit .env with your warehouse credentials:"
echo "   nano .env"
echo ""
echo "2. Start Airflow (2 terminals):"
echo "   Terminal 1: airflow webserver --port 8080"
echo "   Terminal 2: airflow scheduler"
echo ""
echo "3. Access Airflow UI: http://localhost:8080"
echo "   Username: admin / Password: (set during installation)"
echo ""
echo "4. Configure dbt (if not using PostgreSQL):"
echo "   Edit dbt/profiles.yml with your warehouse details"
echo ""
echo "5. Trigger main DAG:"
echo "   airflow dags trigger ecommerce_etl_pipeline"
echo ""
echo "📖 Full documentation: See MODERN_ANALYTICS_STACK.md"
