-- ============================================================================
-- TRADE COMPLIANCE - deploy_cortex_search.sql
-- Cortex Search Services for exception and rule search
-- ============================================================================

USE DATABASE TRADE_COMPLIANCE_DB;
USE SCHEMA DOCS;
USE WAREHOUSE COMPLIANCE_COMPUTE_WH;

-- ============================================================================
-- EXCEPTION_SEARCH - Search on validation failures and anomalies
-- ============================================================================
CREATE OR REPLACE CORTEX SEARCH SERVICE EXCEPTION_SEARCH
ON SEARCH_TEXT
ATTRIBUTES BROKER_NAME, VALIDATION_TYPE, COUNTRY_OF_ORIGIN, PART_NUMBER
WAREHOUSE = COMPLIANCE_COMPUTE_WH
TARGET_LAG = '1 hour'
AS (
    SELECT 
        el.LINE_ID,
        b.BROKER_NAME,
        el.PART_NUMBER,
        el.BROKER_HTS_CODE AS HTS_CODE,
        el.BROKER_COO AS COUNTRY_OF_ORIGIN,
        CASE 
            WHEN el.PART_VALIDATION = 'FAIL' THEN 'PART_VALIDATION'
            WHEN el.HTS_VALIDATION = 'FAIL' THEN 'HTS_VALIDATION'
            WHEN el.ADDCVD_VALIDATION = 'FAIL' THEN 'ADDCVD_VALIDATION'
            WHEN el.ANOMALY_FLAG = TRUE THEN 'ANOMALY'
            ELSE 'UNKNOWN'
        END AS VALIDATION_TYPE,
        CONCAT(
            'Part: ', COALESCE(el.PART_NUMBER, 'N/A'),
            ' | HTS: ', COALESCE(el.BROKER_HTS_CODE, 'N/A'),
            ' | Country: ', COALESCE(el.BROKER_COO, 'N/A'),
            ' | Status: ', COALESCE(el.OVERALL_STATUS, 'N/A'),
            ' | Part Validation: ', COALESCE(el.PART_VALIDATION_MSG, ''),
            ' | HTS Validation: ', COALESCE(el.HTS_VALIDATION_MSG, ''),
            ' | ADD/CVD Validation: ', COALESCE(el.ADDCVD_VALIDATION_MSG, ''),
            ' | Anomaly: ', CASE WHEN el.ANOMALY_FLAG THEN COALESCE(el.ANOMALY_REASON, 'Flagged') ELSE '' END,
            ' | Audit Comments: ', COALESCE(el.AUDIT_COMMENT, '')
        ) AS SEARCH_TEXT
    FROM TRADE_COMPLIANCE_DB.ATOMIC.ENTRY_LINE el
    JOIN TRADE_COMPLIANCE_DB.ATOMIC.BROKER b ON el.BROKER_ID = b.BROKER_ID
    WHERE el.OVERALL_STATUS = 'FAIL' OR el.ANOMALY_FLAG = TRUE
);

-- ============================================================================
-- RULE_SEARCH - Search on discovered and active rules
-- ============================================================================
CREATE OR REPLACE CORTEX SEARCH SERVICE RULE_SEARCH
ON RULE_TEXT
ATTRIBUTES STATUS, DISCOVERY_METHOD, RULE_TYPE
WAREHOUSE = COMPLIANCE_COMPUTE_WH
TARGET_LAG = '1 hour'
AS (
    -- Discovered rules (from ML)
    SELECT 
        RULE_ID,
        STATUS,
        DISCOVERY_METHOD,
        'DISCOVERED' AS RULE_TYPE,
        CONCAT(
            'Rule: ', COALESCE(RULE_NAME, ''),
            ' | Description: ', COALESCE(RULE_DESCRIPTION, ''),
            ' | Condition: ', COALESCE(RULE_CONDITION, ''),
            ' | Reasoning: ', COALESCE(LLM_REASONING, ''),
            ' | Regulatory Basis: ', COALESCE(REGULATORY_BASIS, ''),
            ' | Confidence: ', COALESCE(CAST(CONFIDENCE_SCORE AS VARCHAR), ''),
            ' | Impact: $', COALESCE(CAST(ESTIMATED_IMPACT AS VARCHAR), '')
        ) AS RULE_TEXT
    FROM TRADE_COMPLIANCE_DB.ML.DISCOVERED_RULES
    
    UNION ALL
    
    -- Active rules (from RULES schema)
    SELECT 
        RULE_ID,
        CASE WHEN IS_ACTIVE THEN 'ACTIVE' ELSE 'INACTIVE' END AS STATUS,
        SOURCE AS DISCOVERY_METHOD,
        RULE_TYPE,
        CONCAT(
            'Rule: ', COALESCE(RULE_NAME, ''),
            ' | Description: ', COALESCE(RULE_DESCRIPTION, ''),
            ' | SQL: ', COALESCE(RULE_CONDITION_SQL, ''),
            ' | Action: ', COALESCE(RULE_ACTION, ''),
            ' | Validates: ', COALESCE(VALIDATION_FIELD, '')
        ) AS RULE_TEXT
    FROM TRADE_COMPLIANCE_DB.RULES.ACTIVE_RULES
);

-- ============================================================================
-- CORRECTION_SEARCH - Search on historical corrections for patterns
-- ============================================================================
CREATE OR REPLACE CORTEX SEARCH SERVICE CORRECTION_SEARCH
ON CORRECTION_TEXT
ATTRIBUTES BROKER_NAME, FIELD_CORRECTED, COUNTRY_OF_ORIGIN, CORRECTION_CATEGORY
WAREHOUSE = COMPLIANCE_COMPUTE_WH
TARGET_LAG = '1 hour'
AS (
    SELECT 
        CORRECTION_ID,
        BROKER_NAME,
        FIELD_CORRECTED,
        COUNTRY_OF_ORIGIN,
        CORRECTION_CATEGORY,
        CONCAT(
            'Part: ', COALESCE(PART_NUMBER, ''),
            ' | Field: ', COALESCE(FIELD_CORRECTED, ''),
            ' | From: ', COALESCE(ORIGINAL_VALUE, ''),
            ' | To: ', COALESCE(CORRECTED_VALUE, ''),
            ' | Reason: ', COALESCE(CORRECTION_REASON, ''),
            ' | Notes: ', COALESCE(ANALYST_NOTES, ''),
            ' | Regulation: ', COALESCE(REGULATORY_REFERENCE, ''),
            ' | Context: ', COALESCE(BUSINESS_CONTEXT, ''),
            ' | Broker: ', COALESCE(BROKER_NAME, ''),
            ' | Country: ', COALESCE(COUNTRY_OF_ORIGIN, '')
        ) AS CORRECTION_TEXT
    FROM TRADE_COMPLIANCE_DB.ATOMIC.VALIDATION_CORRECTION
);

-- Verify services created
SHOW CORTEX SEARCH SERVICES IN SCHEMA TRADE_COMPLIANCE_DB.DOCS;
