#!/bin/bash
# ============================================================================
# TRADE COMPLIANCE - deploy_ddl.sh
# Deploy DDL to Snowflake
# ============================================================================

set -e

CONNECTION="${SNOWFLAKE_CONNECTION:-default}"
echo "🚀 Deploying Trade Compliance DDL to Snowflake"
echo "   Connection: $CONNECTION"
echo "=============================================="

# Deploy in order
for sql_file in ddl/001_database.sql ddl/002_atomic_tables.sql ddl/003_ml_tables.sql ddl/004_datamart_views.sql ddl/005_rule_engine.sql; do
    echo ""
    echo "📄 Deploying: $sql_file"
    snow sql -f "$sql_file" -c "$CONNECTION" --format json || {
        echo "❌ Failed to deploy $sql_file"
        exit 1
    }
    echo "✅ $sql_file deployed successfully"
done

echo ""
echo "=============================================="
echo "✅ All DDL deployed successfully!"
echo ""
echo "Next steps:"
echo "  1. Load synthetic data: snow sql -c $CONNECTION -q \"PUT file://data/synthetic/reference/*.csv @TRADE_COMPLIANCE_DB.RAW.GTM_EXPORTS\""
echo "  2. Deploy Cortex services"
echo "  3. Build backend application"
