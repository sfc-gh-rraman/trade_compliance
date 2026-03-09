-- ============================================================================
-- TRADE COMPLIANCE - 003_ml_tables.sql
-- ML tables for AI-powered features
-- ============================================================================

USE DATABASE TRADE_COMPLIANCE_DB;
USE SCHEMA ML;
USE WAREHOUSE COMPLIANCE_COMPUTE_WH;

-- ============================================================================
-- DISCOVERED_RULES - AI-suggested validation rules
-- ============================================================================
CREATE OR REPLACE TABLE DISCOVERED_RULES (
    RULE_ID VARCHAR(50) PRIMARY KEY,
    DISCOVERY_DATE DATE NOT NULL,
    
    -- Rule Definition
    RULE_NAME VARCHAR(255),
    RULE_DESCRIPTION TEXT,
    RULE_CONDITION TEXT,                 -- Human-readable condition
    RULE_SQL TEXT,                       -- Generated SQL WHERE clause
    
    -- Discovery Context
    DISCOVERY_METHOD VARCHAR(50),        -- 'CORRECTION_PATTERN', 'ANOMALY_CLUSTER', 'LLM_SEMANTIC'
    SUPPORTING_EVIDENCE VARIANT,         -- JSON: examples that led to this rule
    CORRECTION_COUNT INT,                -- How many corrections support this
    
    -- LLM Semantic Reasoning
    LLM_REASONING TEXT,                  -- Full LLM reasoning chain
    REGULATORY_BASIS TEXT,               -- Cited regulations (CFR, AD orders)
    GENERALIZATION_FROM TEXT,            -- Original narrow pattern
    SEMANTIC_CLUSTER_ID VARCHAR(50),     -- Which cluster of corrections
    
    -- Confidence
    CONFIDENCE_SCORE FLOAT,              -- 0-1
    ESTIMATED_IMPACT FLOAT,              -- Estimated $ impact
    
    -- Status
    STATUS VARCHAR(30),                  -- 'SUGGESTED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'ACTIVE'
    REVIEWED_BY VARCHAR(100),
    REVIEW_DATE DATE,
    REJECTION_REASON VARCHAR(500),
    
    -- If approved, when was it deployed
    DEPLOYED_DATE DATE,
    
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- ANOMALY_DETECTIONS - AI-flagged unusual entries
-- ============================================================================
CREATE OR REPLACE TABLE ANOMALY_DETECTIONS (
    ANOMALY_ID VARCHAR(50) PRIMARY KEY,
    LINE_ID VARCHAR(50) NOT NULL,
    DETECTION_DATE DATE NOT NULL,
    
    -- Anomaly Details
    ANOMALY_TYPE VARCHAR(100),           -- 'STATISTICAL_OUTLIER', 'PATTERN_DEVIATION', 'VALUE_SPIKE'
    ANOMALY_SCORE FLOAT,                 -- 0-1, higher = more anomalous
    
    -- What triggered it
    TRIGGER_FIELD VARCHAR(100),          -- Which field is anomalous
    TRIGGER_VALUE VARCHAR(200),          -- The anomalous value
    EXPECTED_RANGE VARCHAR(200),         -- What was expected
    
    -- LLM Explanation
    EXPLANATION TEXT,                    -- Human-readable explanation
    RECOMMENDED_ACTION TEXT,
    
    -- Financial Impact
    POTENTIAL_IMPACT FLOAT,
    
    -- Resolution
    STATUS VARCHAR(30),                  -- 'NEW', 'INVESTIGATING', 'VALID_ISSUE', 'FALSE_POSITIVE'
    RESOLUTION_NOTES TEXT,
    RESOLVED_BY VARCHAR(100),
    RESOLVED_DATE DATE,
    
    -- Model Info
    MODEL_NAME VARCHAR(100),
    MODEL_VERSION VARCHAR(20),
    
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- SCHEMA_INFERENCE_LOG - AI schema mapping history
-- ============================================================================
CREATE OR REPLACE TABLE SCHEMA_INFERENCE_LOG (
    INFERENCE_ID VARCHAR(50) PRIMARY KEY,
    BROKER_ID VARCHAR(50),
    INFERENCE_DATE TIMESTAMP_NTZ,
    
    -- Input
    FILE_NAME VARCHAR(255),
    FILE_FORMAT VARCHAR(20),
    SAMPLE_ROWS INT,
    SOURCE_COLUMNS ARRAY,
    
    -- Output
    INFERRED_MAPPINGS VARIANT,           -- JSON: full mapping result
    OVERALL_CONFIDENCE FLOAT,
    UNMAPPED_FIELDS ARRAY,
    
    -- LLM Details
    LLM_MODEL VARCHAR(100),
    LLM_PROMPT_TOKENS INT,
    LLM_COMPLETION_TOKENS INT,
    LLM_REASONING TEXT,
    
    -- Review
    HUMAN_REVIEWED BOOLEAN DEFAULT FALSE,
    CORRECTIONS_MADE INT DEFAULT 0,
    
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- BROKER_PERFORMANCE_SCORES - Broker accuracy metrics
-- ============================================================================
CREATE OR REPLACE TABLE BROKER_PERFORMANCE_SCORES (
    SCORE_ID VARCHAR(50) PRIMARY KEY,
    BROKER_ID VARCHAR(50) NOT NULL,
    SCORE_DATE DATE NOT NULL,
    
    -- Accuracy by validation type
    PART_ACCURACY_PCT FLOAT,
    HTS_ACCURACY_PCT FLOAT,
    ADDCVD_ACCURACY_PCT FLOAT,
    OVERALL_ACCURACY_PCT FLOAT,
    
    -- Volume
    ENTRY_COUNT INT,
    LINE_COUNT INT,
    EXCEPTION_COUNT INT,
    ANOMALY_COUNT INT,
    
    -- Trend
    ACCURACY_TREND VARCHAR(20),          -- 'IMPROVING', 'STABLE', 'DECLINING'
    
    -- Tier
    PERFORMANCE_TIER VARCHAR(20),        -- 'EXCELLENT', 'GOOD', 'NEEDS_IMPROVEMENT', 'CRITICAL'
    
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- SEMANTIC_CLUSTERS - LLM-identified correction clusters
-- ============================================================================
CREATE OR REPLACE TABLE SEMANTIC_CLUSTERS (
    CLUSTER_ID VARCHAR(50) PRIMARY KEY,
    CLUSTER_DATE DATE NOT NULL,
    
    -- Cluster Definition
    CLUSTER_NAME VARCHAR(255),
    CLUSTER_DESCRIPTION TEXT,
    CLUSTER_THEME VARCHAR(100),          -- 'ADD_CVD', 'HTS_CLASSIFICATION', 'COO_MISATTRIBUTION'
    
    -- Members
    CORRECTION_IDS ARRAY,                -- List of CORRECTION_IDs in this cluster
    MEMBER_COUNT INT,
    
    -- LLM Analysis
    COMMON_PHRASES ARRAY,                -- Phrases that unite this cluster
    REGULATORY_THEMES ARRAY,             -- Regulatory references found
    LLM_SUMMARY TEXT,                    -- LLM summary of the pattern
    
    -- Rule Generation
    SUGGESTED_RULE_ID VARCHAR(50),       -- If a rule was generated
    RULE_GENERATION_STATUS VARCHAR(30),  -- 'PENDING', 'GENERATED', 'REJECTED'
    
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

COMMENT ON TABLE DISCOVERED_RULES IS 'AI-suggested validation rules with LLM semantic reasoning';
COMMENT ON TABLE ANOMALY_DETECTIONS IS 'ML-flagged unusual entries without explicit rules';
COMMENT ON TABLE SCHEMA_INFERENCE_LOG IS 'History of AI broker schema inference';
COMMENT ON TABLE SEMANTIC_CLUSTERS IS 'LLM-identified clusters of similar corrections';
