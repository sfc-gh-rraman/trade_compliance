-- ============================================================================
-- TRADE COMPLIANCE DATABASE - 001_database.sql
-- Creates database, schemas, warehouses, and stages
-- ============================================================================

USE ROLE ACCOUNTADMIN;

-- Create Database
CREATE DATABASE IF NOT EXISTS TRADE_COMPLIANCE_DB
    COMMENT = 'AI-Powered Trade Compliance Platform for Cummins Entry Visibility';

USE DATABASE TRADE_COMPLIANCE_DB;

-- ============================================================================
-- SCHEMAS (following ATLAS pattern)
-- ============================================================================

-- RAW: Landing zone for broker files
CREATE SCHEMA IF NOT EXISTS RAW
    COMMENT = 'Landing zone for raw broker files (CEVA, EXPEDITOR, KUEHNE)';

-- ATOMIC: Normalized entity model
CREATE SCHEMA IF NOT EXISTS ATOMIC
    COMMENT = 'Normalized atomic tables - brokers, entries, lines, parts';

-- TRADE_COMPLIANCE: Analytics data mart
CREATE SCHEMA IF NOT EXISTS TRADE_COMPLIANCE
    COMMENT = 'Analytics data mart for trade compliance reporting';

-- ML: ML predictions & discoveries
CREATE SCHEMA IF NOT EXISTS ML
    COMMENT = 'ML tables - discovered rules, anomaly detections, schema inference';

-- DOCS: Cortex Search documents
CREATE SCHEMA IF NOT EXISTS DOCS
    COMMENT = 'Documents for Cortex Search - exceptions, rules';

-- RULES: Dynamic rule engine
CREATE SCHEMA IF NOT EXISTS RULES
    COMMENT = 'Dynamic rule engine - active rules, execution logs';

-- SPCS: Container services
CREATE SCHEMA IF NOT EXISTS SPCS
    COMMENT = 'Snowpark Container Services objects';

-- ============================================================================
-- WAREHOUSES
-- ============================================================================

CREATE WAREHOUSE IF NOT EXISTS COMPLIANCE_COMPUTE_WH
    WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'General compute for trade compliance queries';

CREATE WAREHOUSE IF NOT EXISTS COMPLIANCE_ML_WH
    WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 120
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'ML workloads - anomaly detection, rule discovery';

-- ============================================================================
-- STAGES
-- ============================================================================

CREATE STAGE IF NOT EXISTS RAW.BROKER_FILES
    COMMENT = 'Landing stage for broker data files';

CREATE STAGE IF NOT EXISTS RAW.GTM_EXPORTS
    COMMENT = 'Stage for GTM reference data exports';

CREATE STAGE IF NOT EXISTS TRADE_COMPLIANCE.SEMANTIC_MODELS
    COMMENT = 'Stage for Cortex Analyst semantic model YAML';

CREATE STAGE IF NOT EXISTS ML.MODEL_ARTIFACTS
    COMMENT = 'Stage for ML model artifacts';

-- ============================================================================
-- FILE FORMATS
-- ============================================================================

CREATE FILE FORMAT IF NOT EXISTS RAW.CSV_FORMAT
    TYPE = 'CSV'
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1
    NULL_IF = ('', 'NULL', 'null')
    COMMENT = 'Standard CSV format for broker files';

CREATE FILE FORMAT IF NOT EXISTS RAW.JSON_FORMAT
    TYPE = 'JSON'
    STRIP_OUTER_ARRAY = TRUE
    COMMENT = 'JSON format for API responses';

-- Set default warehouse
USE WAREHOUSE COMPLIANCE_COMPUTE_WH;

-- Verify creation
SHOW SCHEMAS IN DATABASE TRADE_COMPLIANCE_DB;
