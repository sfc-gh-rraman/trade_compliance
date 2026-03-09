-- ============================================================================
-- TRADE COMPLIANCE - 004_datamart_views.sql
-- Analytics views for reporting and dashboards
-- ============================================================================

USE DATABASE TRADE_COMPLIANCE_DB;
USE SCHEMA TRADE_COMPLIANCE;
USE WAREHOUSE COMPLIANCE_COMPUTE_WH;

-- ============================================================================
-- V_EXCEPTION_REPORT - Main exception report view
-- ============================================================================
CREATE OR REPLACE VIEW V_EXCEPTION_REPORT AS
SELECT 
    b.BROKER_NAME,
    eh.ENTRY_DATE,
    eh.ENTRY_NUMBER,
    el.LINE_NUMBER AS ENTRY_SUMMARY_LINE,
    el.PART_NUMBER AS PRODUCT_NUMBER,
    
    -- Validation Status columns
    el.PART_VALIDATION AS PART_NUMBER_STATUS,
    el.HTS_VALIDATION AS HS_CODE_STATUS,
    el.GTM_HTS_CODE,
    'PASS' AS PREFERENTIAL_PROGRAM,      -- Default for now
    el.ADDCVD_VALIDATION AS ADD_CVD_STATUS,
    el.AUDIT_COMMENT AS AUDIT_COMMENTS,
    CASE WHEN el.PDF_LINK IS NOT NULL THEN 'Yes' ELSE 'No' END AS PDF,
    
    -- AI Fields
    el.ANOMALY_FLAG,
    el.ANOMALY_TYPE,
    el.ANOMALY_SCORE,
    el.ANOMALY_REASON,
    
    -- Additional context
    el.BROKER_HTS_CODE,
    el.BROKER_COO AS COUNTRY_OF_ORIGIN,
    el.ENTERED_VALUE,
    el.DUTY_AMOUNT,
    el.OVERALL_STATUS,
    
    -- IDs for drill-down
    el.LINE_ID,
    el.ENTRY_ID,
    b.BROKER_ID
    
FROM ATOMIC.ENTRY_LINE el
JOIN ATOMIC.ENTRY_HEADER eh ON el.ENTRY_ID = eh.ENTRY_ID
JOIN ATOMIC.BROKER b ON el.BROKER_ID = b.BROKER_ID
WHERE el.OVERALL_STATUS = 'FAIL' 
   OR el.ANOMALY_FLAG = TRUE;

-- ============================================================================
-- V_BROKER_SCORECARD - Broker performance summary
-- ============================================================================
CREATE OR REPLACE VIEW V_BROKER_SCORECARD AS
SELECT 
    b.BROKER_NAME,
    b.BROKER_TYPE,
    b.FILE_FORMAT,
    b.SCHEMA_CONFIDENCE,
    
    -- Current period metrics
    COUNT(DISTINCT eh.ENTRY_ID) AS ENTRY_COUNT,
    COUNT(el.LINE_ID) AS LINE_COUNT,
    
    -- Accuracy metrics
    ROUND(SUM(CASE WHEN el.PART_VALIDATION = 'PASS' THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(COUNT(*), 0), 1) AS PART_ACCURACY_PCT,
    ROUND(SUM(CASE WHEN el.HTS_VALIDATION = 'PASS' THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(COUNT(*), 0), 1) AS HTS_ACCURACY_PCT,
    ROUND(SUM(CASE WHEN el.ADDCVD_VALIDATION = 'PASS' THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(COUNT(*), 0), 1) AS ADDCVD_ACCURACY_PCT,
    ROUND(SUM(CASE WHEN el.OVERALL_STATUS = 'PASS' THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(COUNT(*), 0), 1) AS OVERALL_ACCURACY_PCT,
    
    -- Exception counts
    SUM(CASE WHEN el.OVERALL_STATUS = 'FAIL' THEN 1 ELSE 0 END) AS EXCEPTION_COUNT,
    SUM(CASE WHEN el.ANOMALY_FLAG = TRUE THEN 1 ELSE 0 END) AS ANOMALY_COUNT,
    
    -- Financial impact
    SUM(CASE WHEN el.OVERALL_STATUS = 'FAIL' THEN el.DUTY_AMOUNT ELSE 0 END) AS DUTY_AT_RISK,
    
    -- Performance tier
    CASE 
        WHEN SUM(CASE WHEN el.OVERALL_STATUS = 'PASS' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) >= 95 
        THEN 'EXCELLENT'
        WHEN SUM(CASE WHEN el.OVERALL_STATUS = 'PASS' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) >= 85 
        THEN 'GOOD'
        WHEN SUM(CASE WHEN el.OVERALL_STATUS = 'PASS' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) >= 70 
        THEN 'NEEDS_IMPROVEMENT'
        ELSE 'CRITICAL'
    END AS PERFORMANCE_TIER
    
FROM ATOMIC.BROKER b
LEFT JOIN ATOMIC.ENTRY_HEADER eh ON b.BROKER_ID = eh.BROKER_ID
LEFT JOIN ATOMIC.ENTRY_LINE el ON eh.ENTRY_ID = el.ENTRY_ID
GROUP BY 
    b.BROKER_NAME, b.BROKER_TYPE, b.FILE_FORMAT, b.SCHEMA_CONFIDENCE;

-- ============================================================================
-- V_PENDING_RULES - Rules awaiting approval
-- ============================================================================
CREATE OR REPLACE VIEW V_PENDING_RULES AS
SELECT 
    RULE_ID,
    RULE_NAME,
    RULE_DESCRIPTION,
    DISCOVERY_METHOD,
    CORRECTION_COUNT,
    CONFIDENCE_SCORE,
    ESTIMATED_IMPACT,
    LLM_REASONING,
    REGULATORY_BASIS,
    STATUS,
    DISCOVERY_DATE
FROM ML.DISCOVERED_RULES
WHERE STATUS IN ('SUGGESTED', 'UNDER_REVIEW')
ORDER BY ESTIMATED_IMPACT DESC;

-- ============================================================================
-- V_RECENT_ANOMALIES - Recent AI-detected anomalies
-- ============================================================================
CREATE OR REPLACE VIEW V_RECENT_ANOMALIES AS
SELECT 
    ad.ANOMALY_ID,
    ad.DETECTION_DATE,
    el.PART_NUMBER,
    el.BROKER_HTS_CODE AS HTS_CODE,
    b.BROKER_NAME,
    ad.ANOMALY_TYPE,
    ad.ANOMALY_SCORE,
    ad.EXPLANATION,
    ad.RECOMMENDED_ACTION,
    ad.POTENTIAL_IMPACT,
    ad.STATUS,
    ad.RESOLUTION_NOTES
FROM ML.ANOMALY_DETECTIONS ad
JOIN ATOMIC.ENTRY_LINE el ON ad.LINE_ID = el.LINE_ID
JOIN ATOMIC.BROKER b ON el.BROKER_ID = b.BROKER_ID
WHERE ad.DETECTION_DATE >= CURRENT_DATE() - 30
ORDER BY ad.ANOMALY_SCORE DESC;

-- ============================================================================
-- V_CORRECTION_PATTERNS - Patterns in historical corrections
-- ============================================================================
CREATE OR REPLACE VIEW V_CORRECTION_PATTERNS AS
SELECT 
    FIELD_CORRECTED,
    BROKER_NAME,
    COUNTRY_OF_ORIGIN,
    ORIGINAL_VALUE,
    CORRECTED_VALUE,
    COUNT(*) AS OCCURRENCE_COUNT,
    COUNT(DISTINCT PART_NUMBER) AS DISTINCT_PARTS,
    ARRAY_AGG(DISTINCT CORRECTION_REASON) AS REASONS,
    ARRAY_AGG(DISTINCT REGULATORY_REFERENCE) AS REGULATIONS
FROM ATOMIC.VALIDATION_CORRECTION
WHERE PATTERN_EXTRACTED = FALSE
GROUP BY 1, 2, 3, 4, 5
HAVING COUNT(*) >= 3
ORDER BY OCCURRENCE_COUNT DESC;

-- ============================================================================
-- V_KPI_SUMMARY - Dashboard KPIs
-- ============================================================================
CREATE OR REPLACE VIEW V_KPI_SUMMARY AS
SELECT 
    -- Volume metrics
    (SELECT COUNT(*) FROM ATOMIC.ENTRY_LINE WHERE CREATED_AT >= CURRENT_DATE() - 30) AS LINES_LAST_30_DAYS,
    (SELECT COUNT(DISTINCT ENTRY_ID) FROM ATOMIC.ENTRY_HEADER WHERE CREATED_AT >= CURRENT_DATE() - 30) AS ENTRIES_LAST_30_DAYS,
    
    -- Pass rates
    (SELECT ROUND(SUM(CASE WHEN OVERALL_STATUS = 'PASS' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 1)
     FROM ATOMIC.ENTRY_LINE WHERE CREATED_AT >= CURRENT_DATE() - 30) AS PASS_RATE_30_DAYS,
    
    -- Exception count
    (SELECT COUNT(*) FROM ATOMIC.ENTRY_LINE 
     WHERE OVERALL_STATUS = 'FAIL' AND CREATED_AT >= CURRENT_DATE() - 7) AS EXCEPTIONS_LAST_7_DAYS,
    
    -- Anomaly count
    (SELECT COUNT(*) FROM ATOMIC.ENTRY_LINE 
     WHERE ANOMALY_FLAG = TRUE AND CREATED_AT >= CURRENT_DATE() - 7) AS ANOMALIES_LAST_7_DAYS,
    
    -- Pending rules
    (SELECT COUNT(*) FROM ML.DISCOVERED_RULES WHERE STATUS = 'SUGGESTED') AS PENDING_RULES,
    
    -- Duty at risk
    (SELECT COALESCE(SUM(DUTY_AMOUNT), 0) FROM ATOMIC.ENTRY_LINE 
     WHERE OVERALL_STATUS = 'FAIL' AND CREATED_AT >= CURRENT_DATE() - 30) AS DUTY_AT_RISK_30_DAYS;

COMMENT ON VIEW V_EXCEPTION_REPORT IS 'Main exception report matching Cummins format';
COMMENT ON VIEW V_BROKER_SCORECARD IS 'Broker performance summary with accuracy metrics';
COMMENT ON VIEW V_KPI_SUMMARY IS 'Dashboard KPIs for Mission Control';
