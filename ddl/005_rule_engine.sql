-- ============================================================================
-- TRADE COMPLIANCE - 005_rule_engine.sql
-- Dynamic rule engine for validation
-- ============================================================================

USE DATABASE TRADE_COMPLIANCE_DB;
USE SCHEMA RULES;
USE WAREHOUSE COMPLIANCE_COMPUTE_WH;

-- ============================================================================
-- ACTIVE_RULES - Rules currently in production
-- ============================================================================
CREATE OR REPLACE TABLE ACTIVE_RULES (
    RULE_ID VARCHAR(50) PRIMARY KEY,
    RULE_NAME VARCHAR(255) NOT NULL,
    RULE_DESCRIPTION TEXT,
    
    -- Rule Logic
    RULE_TYPE VARCHAR(50),               -- 'SQL', 'PYTHON_UDF', 'LLM_EVAL'
    RULE_CONDITION_SQL TEXT,             -- SQL WHERE clause that indicates FAILURE
    RULE_ACTION VARCHAR(50),             -- 'FAIL', 'FLAG', 'WARN'
    VALIDATION_FIELD VARCHAR(50),        -- Which field this validates: 'PART', 'HTS', 'ADDCVD'
    
    -- Applicability
    APPLIES_TO_BROKER_TYPES ARRAY,       -- ['US', 'EU'] or NULL for all
    APPLIES_TO_PRODUCT_CATEGORIES ARRAY,
    APPLIES_TO_COUNTRIES ARRAY,          -- Country of origin filter
    
    -- Priority
    PRIORITY INT DEFAULT 100,            -- Lower = runs first
    
    -- Source
    SOURCE VARCHAR(50),                  -- 'BASELINE', 'DISCOVERED', 'MANUAL'
    DISCOVERED_RULE_ID VARCHAR(50),      -- If source is DISCOVERED, link to ML.DISCOVERED_RULES
    
    -- Status
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    
    -- Audit
    CREATED_BY VARCHAR(100),
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    MODIFIED_BY VARCHAR(100),
    MODIFIED_AT TIMESTAMP_NTZ
);

-- ============================================================================
-- Insert baseline validation rules
-- ============================================================================
INSERT INTO ACTIVE_RULES (RULE_ID, RULE_NAME, RULE_DESCRIPTION, RULE_TYPE, RULE_CONDITION_SQL, RULE_ACTION, VALIDATION_FIELD, PRIORITY, SOURCE, CREATED_BY) VALUES

-- Rule 1: Part Number Validation
('RULE-001', 
 'Part Number Must Exist in GTM', 
 'Check if broker part number exists in GTM US parts list. FAIL if part not found.',
 'SQL',
 'NOT EXISTS (SELECT 1 FROM ATOMIC.GTM_PART_MASTER g WHERE g.PART_NUMBER = el.PART_NUMBER)',
 'FAIL',
 'PART',
 10,
 'BASELINE',
 'SYSTEM'),

-- Rule 2: US Origin Auto-Pass for HTS
('RULE-002', 
 'US Origin HTS Auto-Pass', 
 'US country of origin automatically passes HTS validation.',
 'SQL',
 'el.BROKER_COO = ''US''',
 'PASS',
 'HTS',
 20,
 'BASELINE',
 'SYSTEM'),

-- Rule 3: HTS Code Match for Non-US
('RULE-003', 
 'HTS Code Must Match GTM for Non-US Origin', 
 'For non-US origin, broker HTS must match one of the GTM HTS codes for that part.',
 'SQL',
 'el.BROKER_COO != ''US'' AND NOT EXISTS (
    SELECT 1 FROM ATOMIC.GTM_PART_MASTER g 
    WHERE g.PART_NUMBER = el.PART_NUMBER 
    AND (g.HTS_CODE = el.BROKER_HTS_CODE 
         OR g.HTS_CODE_ALT1 = el.BROKER_HTS_CODE 
         OR g.HTS_CODE_ALT2 = el.BROKER_HTS_CODE)
 )',
 'FAIL',
 'HTS',
 30,
 'BASELINE',
 'SYSTEM'),

-- Rule 4: 9801 Special Handling
('RULE-004', 
 '9801 HTS Special Validation', 
 'HTS codes starting with 9801 require special handling - must exist exactly in GTM.',
 'SQL',
 'el.BROKER_HTS_CODE LIKE ''9801%'' AND NOT EXISTS (
    SELECT 1 FROM ATOMIC.GTM_PART_MASTER g 
    WHERE g.PART_NUMBER = el.PART_NUMBER 
    AND g.HTS_CODE = el.BROKER_HTS_CODE
 )',
 'FAIL',
 'HTS',
 25,
 'BASELINE',
 'SYSTEM'),

-- Rule 5: ADD/CVD Case Match
('RULE-005', 
 'ADD/CVD Case Number Must Match', 
 'When broker declares ADD/CVD, case numbers must match GTM reference.',
 'SQL',
 '(el.BROKER_ADD_CASE IS NOT NULL OR el.BROKER_CVD_CASE IS NOT NULL) 
  AND NOT EXISTS (
    SELECT 1 FROM ATOMIC.GTM_PART_MASTER g 
    WHERE g.PART_NUMBER = el.PART_NUMBER 
    AND (g.ADD_CASE_NUMBER = el.BROKER_ADD_CASE OR el.BROKER_ADD_CASE IS NULL)
    AND (g.CVD_CASE_NUMBER = el.BROKER_CVD_CASE OR el.BROKER_CVD_CASE IS NULL)
 )',
 'FAIL',
 'ADDCVD',
 50,
 'BASELINE',
 'SYSTEM'),

-- Rule 6: ADD Required for China Electrical (Example discovered rule)
('RULE-006', 
 'ADD Required for China Electrical Components', 
 'Parts with E-prefix from China require ADD declaration. AI-discovered from correction patterns.',
 'SQL',
 'el.PART_NUMBER LIKE ''E%'' AND el.BROKER_COO = ''CN'' AND (el.BROKER_ADD_CASE IS NULL OR el.BROKER_ADD_CASE = '''')',
 'FAIL',
 'ADDCVD',
 60,
 'DISCOVERED',
 'AI_RULE_DISCOVERY');

-- ============================================================================
-- RULE_EXECUTION_LOG - Track which rules fired
-- ============================================================================
CREATE OR REPLACE TABLE RULE_EXECUTION_LOG (
    LOG_ID VARCHAR(50) PRIMARY KEY,
    EXECUTION_BATCH_ID VARCHAR(50),      -- Group executions together
    LINE_ID VARCHAR(50) NOT NULL,
    RULE_ID VARCHAR(50) NOT NULL,
    EXECUTION_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- Result
    RULE_RESULT VARCHAR(10),             -- 'PASS', 'FAIL', 'SKIP', 'ERROR'
    RULE_MESSAGE VARCHAR(500),           -- Explanation
    
    -- Performance
    EXECUTION_TIME_MS INT,
    
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- Stored Procedure: Execute all active rules on a batch of lines
-- ============================================================================
CREATE OR REPLACE PROCEDURE EXECUTE_VALIDATION_BATCH(ENTRY_IDS ARRAY)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    batch_id VARCHAR;
    lines_processed INT;
    rules_executed INT;
BEGIN
    batch_id := UUID_STRING();
    
    -- Update PART_VALIDATION based on Rule 001
    UPDATE ATOMIC.ENTRY_LINE el
    SET PART_VALIDATION = CASE 
            WHEN EXISTS (SELECT 1 FROM ATOMIC.GTM_PART_MASTER g WHERE g.PART_NUMBER = el.PART_NUMBER)
            THEN 'PASS' ELSE 'FAIL' 
        END,
        PART_VALIDATION_MSG = CASE 
            WHEN EXISTS (SELECT 1 FROM ATOMIC.GTM_PART_MASTER g WHERE g.PART_NUMBER = el.PART_NUMBER)
            THEN 'Part found in GTM' ELSE 'Part not found in GTM parts list'
        END
    WHERE el.ENTRY_ID IN (SELECT VALUE FROM TABLE(FLATTEN(INPUT => :ENTRY_IDS)));
    
    -- Update HTS_VALIDATION based on Rules 002, 003, 004
    UPDATE ATOMIC.ENTRY_LINE el
    SET HTS_VALIDATION = CASE 
            -- US Origin auto-pass
            WHEN el.BROKER_COO = 'US' THEN 'PASS'
            -- Non-US must match GTM
            WHEN EXISTS (
                SELECT 1 FROM ATOMIC.GTM_PART_MASTER g 
                WHERE g.PART_NUMBER = el.PART_NUMBER 
                AND (g.HTS_CODE = el.BROKER_HTS_CODE 
                     OR g.HTS_CODE_ALT1 = el.BROKER_HTS_CODE 
                     OR g.HTS_CODE_ALT2 = el.BROKER_HTS_CODE)
            ) THEN 'PASS'
            ELSE 'FAIL'
        END,
        GTM_HTS_CODE = (
            SELECT g.HTS_CODE FROM ATOMIC.GTM_PART_MASTER g 
            WHERE g.PART_NUMBER = el.PART_NUMBER LIMIT 1
        ),
        HTS_VALIDATION_MSG = CASE 
            WHEN el.BROKER_COO = 'US' THEN 'US origin - auto pass'
            WHEN EXISTS (
                SELECT 1 FROM ATOMIC.GTM_PART_MASTER g 
                WHERE g.PART_NUMBER = el.PART_NUMBER 
                AND (g.HTS_CODE = el.BROKER_HTS_CODE 
                     OR g.HTS_CODE_ALT1 = el.BROKER_HTS_CODE 
                     OR g.HTS_CODE_ALT2 = el.BROKER_HTS_CODE)
            ) THEN 'HTS matches GTM'
            ELSE 'HTS mismatch - broker HTS not in GTM'
        END
    WHERE el.ENTRY_ID IN (SELECT VALUE FROM TABLE(FLATTEN(INPUT => :ENTRY_IDS)));
    
    -- Update ADDCVD_VALIDATION based on Rule 005
    UPDATE ATOMIC.ENTRY_LINE el
    SET ADDCVD_VALIDATION = CASE 
            WHEN el.BROKER_ADD_CASE IS NULL AND el.BROKER_CVD_CASE IS NULL THEN 'PASS'
            WHEN EXISTS (
                SELECT 1 FROM ATOMIC.GTM_PART_MASTER g 
                WHERE g.PART_NUMBER = el.PART_NUMBER 
                AND COALESCE(g.ADD_CASE_NUMBER, '') = COALESCE(el.BROKER_ADD_CASE, '')
                AND COALESCE(g.CVD_CASE_NUMBER, '') = COALESCE(el.BROKER_CVD_CASE, '')
            ) THEN 'PASS'
            ELSE 'FAIL'
        END,
        ADDCVD_VALIDATION_MSG = CASE 
            WHEN el.BROKER_ADD_CASE IS NULL AND el.BROKER_CVD_CASE IS NULL THEN 'No ADD/CVD declared'
            WHEN EXISTS (
                SELECT 1 FROM ATOMIC.GTM_PART_MASTER g 
                WHERE g.PART_NUMBER = el.PART_NUMBER 
                AND COALESCE(g.ADD_CASE_NUMBER, '') = COALESCE(el.BROKER_ADD_CASE, '')
                AND COALESCE(g.CVD_CASE_NUMBER, '') = COALESCE(el.BROKER_CVD_CASE, '')
            ) THEN 'ADD/CVD matches GTM'
            ELSE 'ADD/CVD mismatch'
        END
    WHERE el.ENTRY_ID IN (SELECT VALUE FROM TABLE(FLATTEN(INPUT => :ENTRY_IDS)));
    
    -- Update OVERALL_STATUS
    UPDATE ATOMIC.ENTRY_LINE el
    SET OVERALL_STATUS = CASE 
            WHEN PART_VALIDATION = 'FAIL' OR HTS_VALIDATION = 'FAIL' OR ADDCVD_VALIDATION = 'FAIL'
            THEN 'FAIL' ELSE 'PASS'
        END
    WHERE el.ENTRY_ID IN (SELECT VALUE FROM TABLE(FLATTEN(INPUT => :ENTRY_IDS)));
    
    -- Count results
    SELECT COUNT(*) INTO lines_processed 
    FROM ATOMIC.ENTRY_LINE 
    WHERE ENTRY_ID IN (SELECT VALUE FROM TABLE(FLATTEN(INPUT => :ENTRY_IDS)));
    
    RETURN OBJECT_CONSTRUCT(
        'status', 'completed',
        'batch_id', batch_id,
        'lines_processed', lines_processed,
        'timestamp', CURRENT_TIMESTAMP()
    );
END;
$$;

-- ============================================================================
-- Stored Procedure: Activate a discovered rule
-- ============================================================================
CREATE OR REPLACE PROCEDURE ACTIVATE_DISCOVERED_RULE(DISCOVERED_RULE_ID VARCHAR, ACTIVATED_BY VARCHAR)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    new_rule_id VARCHAR;
BEGIN
    new_rule_id := 'RULE-' || REPLACE(UUID_STRING(), '-', '');
    
    -- Copy from DISCOVERED_RULES to ACTIVE_RULES
    INSERT INTO ACTIVE_RULES (
        RULE_ID, RULE_NAME, RULE_DESCRIPTION, RULE_TYPE, RULE_CONDITION_SQL, 
        RULE_ACTION, PRIORITY, SOURCE, DISCOVERED_RULE_ID, IS_ACTIVE, CREATED_BY
    )
    SELECT 
        :new_rule_id,
        RULE_NAME,
        RULE_DESCRIPTION,
        'SQL',
        RULE_SQL,
        'FAIL',
        100,
        'DISCOVERED',
        RULE_ID,
        TRUE,
        :ACTIVATED_BY
    FROM ML.DISCOVERED_RULES
    WHERE RULE_ID = :DISCOVERED_RULE_ID;
    
    -- Update status in DISCOVERED_RULES
    UPDATE ML.DISCOVERED_RULES
    SET STATUS = 'ACTIVE', 
        DEPLOYED_DATE = CURRENT_DATE(),
        REVIEWED_BY = :ACTIVATED_BY,
        REVIEW_DATE = CURRENT_DATE()
    WHERE RULE_ID = :DISCOVERED_RULE_ID;
    
    RETURN OBJECT_CONSTRUCT(
        'status', 'success',
        'new_rule_id', new_rule_id,
        'discovered_rule_id', DISCOVERED_RULE_ID,
        'activated_by', ACTIVATED_BY
    );
END;
$$;

COMMENT ON TABLE ACTIVE_RULES IS 'Active validation rules - baseline + AI-discovered';
COMMENT ON PROCEDURE EXECUTE_VALIDATION_BATCH(ARRAY) IS 'Execute all validation rules on a batch of entries';
COMMENT ON PROCEDURE ACTIVATE_DISCOVERED_RULE(VARCHAR, VARCHAR) IS 'Promote an AI-discovered rule to active status';
