-- ============================================================================
-- TRADE COMPLIANCE - 002_atomic_tables.sql
-- Core atomic tables for trade compliance
-- ============================================================================

USE DATABASE TRADE_COMPLIANCE_DB;
USE SCHEMA ATOMIC;
USE WAREHOUSE COMPLIANCE_COMPUTE_WH;

-- ============================================================================
-- BROKER - Source broker entity with AI schema mapping
-- ============================================================================
CREATE OR REPLACE TABLE BROKER (
    BROKER_ID VARCHAR(50) PRIMARY KEY,
    BROKER_NAME VARCHAR(255) NOT NULL,
    BROKER_CODE VARCHAR(20),
    BROKER_TYPE VARCHAR(50),             -- 'US', 'EU'
    REGION VARCHAR(50),
    FILE_FORMAT VARCHAR(20),             -- 'XML', 'CSV', 'XLSB'
    
    -- AI-Generated Schema Mapping
    SCHEMA_MAPPING VARIANT,              -- JSON: {"source_field": "target_field", ...}
    SCHEMA_CONFIDENCE FLOAT,             -- AI confidence in mapping (0-1)
    MAPPING_DATE TIMESTAMP_NTZ,
    
    -- Performance Metrics
    ACCURACY_RATE FLOAT,
    EXCEPTION_RATE FLOAT,
    
    ACTIVE_FLAG BOOLEAN DEFAULT TRUE,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- BROKER_SCHEMA_MAPPING - AI-inferred field mappings (detail)
-- ============================================================================
CREATE OR REPLACE TABLE BROKER_SCHEMA_MAPPING (
    MAPPING_ID VARCHAR(50) PRIMARY KEY,
    BROKER_ID VARCHAR(50) NOT NULL REFERENCES BROKER(BROKER_ID),
    
    -- Source Field Info
    SOURCE_FIELD_NAME VARCHAR(100),
    SOURCE_FIELD_TYPE VARCHAR(50),
    SOURCE_SAMPLE_VALUES ARRAY,
    
    -- Target Field Info
    TARGET_FIELD_NAME VARCHAR(100),      -- Our standard schema field
    
    -- AI Inference
    CONFIDENCE_SCORE FLOAT,
    INFERENCE_METHOD VARCHAR(50),        -- 'SEMANTIC', 'PATTERN', 'EXACT_MATCH'
    LLM_REASONING TEXT,                  -- Why AI made this mapping
    
    -- Status
    STATUS VARCHAR(20),                  -- 'SUGGESTED', 'APPROVED', 'REJECTED'
    REVIEWED_BY VARCHAR(100),
    REVIEWED_AT TIMESTAMP_NTZ,
    
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- ENTRY_HEADER - Customs entry header
-- ============================================================================
CREATE OR REPLACE TABLE ENTRY_HEADER (
    ENTRY_ID VARCHAR(50) PRIMARY KEY,
    BROKER_ID VARCHAR(50) NOT NULL REFERENCES BROKER(BROKER_ID),
    
    ENTRY_NUMBER VARCHAR(30),
    ENTRY_TYPE VARCHAR(20),
    FILER_CODE VARCHAR(10),
    
    ENTRY_DATE DATE,
    IMPORT_DATE DATE,
    RELEASE_DATE DATE,
    
    IMPORTER_OF_RECORD VARCHAR(255),
    IOR_NUMBER VARCHAR(30),
    PORT_OF_ENTRY VARCHAR(10),
    PORT_NAME VARCHAR(100),
    
    TOTAL_ENTERED_VALUE FLOAT,
    TOTAL_DUTY FLOAT,
    TOTAL_TAX FLOAT,
    TOTAL_ADD_CVD FLOAT,
    
    -- Validation Summary
    VALIDATION_STATUS VARCHAR(30),       -- 'PENDING', 'PASS', 'FAIL', 'PARTIAL'
    EXCEPTION_COUNT INT DEFAULT 0,
    ANOMALY_COUNT INT DEFAULT 0,         -- AI-detected issues
    
    FILE_SOURCE VARCHAR(255),
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- ENTRY_LINE - Entry line items (THE CORE TABLE)
-- ============================================================================
CREATE OR REPLACE TABLE ENTRY_LINE (
    LINE_ID VARCHAR(50) PRIMARY KEY,
    ENTRY_ID VARCHAR(50) NOT NULL REFERENCES ENTRY_HEADER(ENTRY_ID),
    BROKER_ID VARCHAR(50) NOT NULL REFERENCES BROKER(BROKER_ID),
    
    LINE_NUMBER INT,
    ENTRY_SUMMARY_LINE VARCHAR(30),
    
    -- Product Info
    PART_NUMBER VARCHAR(100),
    PART_DESCRIPTION VARCHAR(500),
    PRODUCT_CATEGORY VARCHAR(100),
    
    -- Broker-Provided Values
    BROKER_HTS_CODE VARCHAR(20),
    BROKER_COO VARCHAR(5),               -- Country of Origin
    BROKER_ADD_CASE VARCHAR(50),
    BROKER_CVD_CASE VARCHAR(50),
    BROKER_ADD_RATE FLOAT,
    BROKER_CVD_RATE FLOAT,
    BROKER_DUTY_RATE FLOAT,
    
    -- GTM Reference Values (lookup results)
    GTM_PART_EXISTS BOOLEAN,
    GTM_HTS_CODE VARCHAR(20),
    GTM_ADD_CASE VARCHAR(50),
    GTM_CVD_CASE VARCHAR(50),
    
    -- Financial
    ENTERED_VALUE FLOAT,
    DUTY_AMOUNT FLOAT,
    ADD_AMOUNT FLOAT,
    CVD_AMOUNT FLOAT,
    
    -- RULE-BASED VALIDATION RESULTS
    PART_VALIDATION VARCHAR(10),         -- 'PASS', 'FAIL'
    PART_VALIDATION_MSG VARCHAR(255),
    HTS_VALIDATION VARCHAR(10),
    HTS_VALIDATION_MSG VARCHAR(255),
    ADDCVD_VALIDATION VARCHAR(10),
    ADDCVD_VALIDATION_MSG VARCHAR(255),
    OVERALL_STATUS VARCHAR(10),
    
    -- AI-POWERED VALIDATION RESULTS
    ANOMALY_FLAG BOOLEAN DEFAULT FALSE,  -- AI detected something unusual
    ANOMALY_TYPE VARCHAR(100),           -- What kind of anomaly
    ANOMALY_SCORE FLOAT,                 -- How anomalous (0-1)
    ANOMALY_REASON TEXT,                 -- LLM explanation
    
    -- Audit
    AUDIT_COMMENT VARCHAR(1000),
    MANUAL_OVERRIDE BOOLEAN DEFAULT FALSE,
    OVERRIDE_REASON VARCHAR(500),
    PDF_LINK VARCHAR(500),
    
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- GTM_PART_MASTER - Reference data from Global Trade Management
-- ============================================================================
CREATE OR REPLACE TABLE GTM_PART_MASTER (
    GTM_PART_ID VARCHAR(50) PRIMARY KEY,
    PART_NUMBER VARCHAR(100) NOT NULL,
    PART_DESCRIPTION VARCHAR(500),
    
    HTS_CODE VARCHAR(20),
    HTS_CODE_ALT1 VARCHAR(20),
    HTS_CODE_ALT2 VARCHAR(20),
    
    PREFERENTIAL_PROGRAM VARCHAR(100),
    
    ADD_CASE_NUMBER VARCHAR(50),
    ADD_RATE FLOAT,
    CVD_CASE_NUMBER VARCHAR(50),
    CVD_RATE FLOAT,
    
    COUNTRY_OF_ORIGIN VARCHAR(5),
    
    EFFECTIVE_DATE DATE,
    EXPIRATION_DATE DATE,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Note: Snowflake uses automatic micro-partitioning instead of traditional indexes
-- For lookup performance, consider clustering keys on frequently filtered columns

-- ============================================================================
-- GTM_HTS_REFERENCE - HTS code reference data
-- ============================================================================
CREATE OR REPLACE TABLE GTM_HTS_REFERENCE (
    HTS_CODE VARCHAR(20) PRIMARY KEY,
    HTS_DESCRIPTION VARCHAR(500),
    CHAPTER VARCHAR(2),
    SECTION VARCHAR(50),
    DUTY_RATE FLOAT,
    ADD_RATE FLOAT,
    CVD_RATE FLOAT,
    EFFECTIVE_DATE DATE,
    EXPIRATION_DATE DATE
);

-- ============================================================================
-- ADD_CVD_REFERENCE - Anti-dumping/Countervailing duty reference
-- ============================================================================
CREATE OR REPLACE TABLE ADD_CVD_REFERENCE (
    CASE_ID VARCHAR(50) PRIMARY KEY,
    COO VARCHAR(5),
    HTS_CODE VARCHAR(20),
    ADD_ORDER_NUMBER VARCHAR(50),
    CVD_ORDER_NUMBER VARCHAR(50),
    ADD_RATE FLOAT,
    CVD_RATE FLOAT,
    EFFECTIVE_DATE DATE,
    STATUS VARCHAR(20)
);

-- ============================================================================
-- VALIDATION_CORRECTION - Historical corrections for rule learning
-- ============================================================================
CREATE OR REPLACE TABLE VALIDATION_CORRECTION (
    CORRECTION_ID VARCHAR(50) PRIMARY KEY,
    LINE_ID VARCHAR(50),
    ENTRY_NUMBER VARCHAR(30),
    ENTRY_DATE DATE,
    BROKER_NAME VARCHAR(100),
    PART_NUMBER VARCHAR(100),
    COUNTRY_OF_ORIGIN VARCHAR(5),
    HTS_CODE VARCHAR(20),
    ENTERED_VALUE FLOAT,
    
    -- What was corrected
    FIELD_CORRECTED VARCHAR(100),
    ORIGINAL_VALUE VARCHAR(255),
    CORRECTED_VALUE VARCHAR(255),
    
    -- SEMANTIC FIELDS FOR LLM REASONING
    CORRECTION_REASON TEXT,              -- "Per CBP ruling HQ H301245..."
    ANALYST_NOTES TEXT,                  -- "Broker didn't check Section 301 list..."
    REGULATORY_REFERENCE TEXT,           -- "19 CFR 159.1; AD Order A-570-067"
    RELATED_CASES TEXT,                  -- Links to similar corrections
    BUSINESS_CONTEXT TEXT,               -- "Part of engine assembly line..."
    
    -- Structured metadata
    CORRECTION_CATEGORY VARCHAR(50),
    CORRECTED_BY VARCHAR(100),
    CORRECTION_DATE TIMESTAMP_NTZ,
    WAS_FLAGGED_BY_SYSTEM BOOLEAN DEFAULT FALSE,
    CONFIDENCE_LEVEL VARCHAR(20),        -- HIGH/MEDIUM/LOW
    TIME_TO_RESOLVE_MINUTES INT,
    REQUIRED_RESEARCH BOOLEAN DEFAULT FALSE,
    
    -- AI Analysis
    PATTERN_EXTRACTED BOOLEAN DEFAULT FALSE,
    PATTERN_ID VARCHAR(50),
    
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Add vector column for semantic search (Cortex embeddings)
-- ALTER TABLE VALIDATION_CORRECTION ADD COLUMN REASON_EMBEDDING VECTOR(FLOAT, 768);

COMMENT ON TABLE BROKER IS 'Customs brokers with AI-inferred schema mappings';
COMMENT ON TABLE ENTRY_LINE IS 'Entry line items with validation and anomaly detection results';
COMMENT ON TABLE VALIDATION_CORRECTION IS 'Historical corrections - gold mine for LLM rule discovery';
