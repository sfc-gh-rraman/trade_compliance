# Cummins Entry Visibility - Implementation Plan
## AI-First Trade Compliance Platform (Following ATLAS Patterns)

---

## Executive Summary

This document outlines the implementation plan for the Cummins Entry Visibility application. Unlike traditional rules-based systems, this platform uses **AI to scale broker onboarding and discover validation rules** - not just execute them.

### The Three AI Pillars

| Pillar | ATLAS Equivalent | Cummins Implementation |
|--------|------------------|------------------------|
| **Pattern Detection** | "Hidden Discovery" - grounding pattern | Rule Discovery from corrections |
| **Semantic Search** | CO narrative search | Exception/audit comment search |
| **Natural Language** | Cortex Analyst queries | Query + Rule authoring |
| **NEW: Schema Inference** | N/A | AI broker onboarding |
| **NEW: Anomaly Detection** | N/A | Unknown-unknown flagging |

### The "Wow" Moment

> "A new EU broker was onboarded in **2 hours** instead of 2 weeks.
> The AI mapped 47 fields automatically - including German field names.
> It then discovered 3 new EU-specific validation rules that saved $340K."

---

## 1. Folder Structure

```
cummins_entry_visibility/
├── copilot/
│   ├── frontend/               # React 18 + TypeScript + Tailwind
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   │   ├── Landing.tsx
│   │   │   │   ├── MissionControl.tsx      # Main dashboard + chat
│   │   │   │   ├── BrokerOnboarding.tsx    # AI schema mapping UI
│   │   │   │   ├── ExceptionReport.tsx     # Validation results
│   │   │   │   ├── RuleDiscovery.tsx       # AI-suggested rules
│   │   │   │   ├── BrokerPerformance.tsx   # Broker scorecards
│   │   │   │   └── Architecture.tsx
│   │   │   └── styles/
│   │   └── package.json
│   │
│   ├── backend/                # FastAPI + Python
│   │   ├── api/main.py
│   │   ├── agents/
│   │   │   ├── orchestrator.py
│   │   │   ├── onboarding_agent.py     # AI schema inference
│   │   │   ├── validation_agent.py     # Rules + anomaly detection
│   │   │   ├── discovery_agent.py      # Rule discovery from patterns
│   │   │   └── compliance_agent.py     # Exception management
│   │   └── services/
│   │       ├── snowflake_service.py
│   │       ├── schema_inference.py     # LLM-powered field mapping
│   │       └── anomaly_detector.py     # ML anomaly detection
│   │
│   └── deploy/
│       ├── Dockerfile
│       ├── nginx.conf
│       └── service_spec.yaml
│
├── cortex/
│   ├── entry_visibility_semantic_model.yaml
│   ├── deploy_search.sql
│   ├── deploy_agent.py
│   └── schema_inference_prompt.txt     # LLM prompt for field mapping
│
├── ddl/
│   ├── 001_database.sql
│   ├── 002_atomic_tables.sql
│   ├── 003_ml_tables.sql
│   ├── 004_datamart_views.sql
│   └── 005_rule_engine.sql             # Dynamic rule execution
│
├── notebooks/
│   ├── SCHEMA_INFERENCE_NB.ipynb       # Field mapping ML
│   ├── ANOMALY_DETECTOR_NB.ipynb       # Unknown-unknown detection
│   ├── RULE_DISCOVERY_NB.ipynb         # Learn rules from corrections
│   └── BROKER_SCORER_NB.ipynb          # Broker performance
│
├── data/
│   └── synthetic/
│
├── scripts/
│   └── generate_synthetic_data.py
│
├── docs/
│   ├── entry_visibility_requirements.md
│   └── implementation_plan.md
│
├── deploy.sh
└── README.md
```

---

## 2. Database Architecture

### 001_database.sql

```sql
CREATE DATABASE IF NOT EXISTS TRADE_COMPLIANCE_DB;
USE DATABASE TRADE_COMPLIANCE_DB;

-- Core Schemas (following ATLAS pattern)
CREATE SCHEMA IF NOT EXISTS RAW;              -- Landing zone for broker files
CREATE SCHEMA IF NOT EXISTS ATOMIC;           -- Normalized entity model
CREATE SCHEMA IF NOT EXISTS TRADE_COMPLIANCE; -- Analytics data mart
CREATE SCHEMA IF NOT EXISTS ML;               -- ML predictions & discoveries
CREATE SCHEMA IF NOT EXISTS DOCS;             -- Cortex Search documents
CREATE SCHEMA IF NOT EXISTS RULES;            -- Dynamic rule engine
CREATE SCHEMA IF NOT EXISTS SPCS;             -- Container services

-- Warehouses
CREATE WAREHOUSE IF NOT EXISTS COMPLIANCE_COMPUTE_WH
    WAREHOUSE_SIZE = 'SMALL' AUTO_SUSPEND = 60;
CREATE WAREHOUSE IF NOT EXISTS COMPLIANCE_ML_WH
    WAREHOUSE_SIZE = 'MEDIUM' AUTO_SUSPEND = 120;

-- Stages
CREATE STAGE IF NOT EXISTS RAW.BROKER_FILES;
CREATE STAGE IF NOT EXISTS RAW.GTM_EXPORTS;
CREATE STAGE IF NOT EXISTS TRADE_COMPLIANCE.SEMANTIC_MODELS;
```

### 002_atomic_tables.sql

```sql
USE DATABASE TRADE_COMPLIANCE_DB;
USE SCHEMA ATOMIC;

-- ============================================================================
-- BROKER - Source broker entity
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
    SCHEMA_CONFIDENCE FLOAT,             -- AI confidence in mapping
    MAPPING_DATE TIMESTAMP_NTZ,
    
    -- Performance Metrics
    ACCURACY_RATE FLOAT,
    EXCEPTION_RATE FLOAT,
    
    ACTIVE_FLAG BOOLEAN DEFAULT TRUE,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- BROKER_SCHEMA_MAPPING - AI-inferred field mappings
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
    VALIDATION_STATUS VARCHAR(30),
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
    BROKER_COO VARCHAR(5),
    BROKER_ADD_CASE VARCHAR(50),
    BROKER_CVD_CASE VARCHAR(50),
    BROKER_ADD_RATE FLOAT,
    BROKER_CVD_RATE FLOAT,
    BROKER_DUTY_RATE FLOAT,
    
    -- GTM Reference Values
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
    HTS_VALIDATION VARCHAR(10),
    ADDCVD_VALIDATION VARCHAR(10),
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
-- GTM_PART_MASTER - Reference data
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

-- ============================================================================
-- VALIDATION_CORRECTION - Historical corrections for rule learning
-- ============================================================================
CREATE OR REPLACE TABLE VALIDATION_CORRECTION (
    CORRECTION_ID VARCHAR(50) PRIMARY KEY,
    LINE_ID VARCHAR(50) NOT NULL REFERENCES ENTRY_LINE(LINE_ID),
    
    -- What was corrected
    FIELD_CORRECTED VARCHAR(100),        -- 'HTS_CODE', 'ADD_CASE', etc.
    ORIGINAL_VALUE VARCHAR(200),
    CORRECTED_VALUE VARCHAR(200),
    
    -- Context
    BROKER_ID VARCHAR(50),
    PART_NUMBER VARCHAR(100),
    COUNTRY_OF_ORIGIN VARCHAR(5),
    
    -- Correction metadata
    CORRECTED_BY VARCHAR(100),
    CORRECTION_REASON VARCHAR(500),
    CORRECTION_DATE TIMESTAMP_NTZ,
    
    -- AI Analysis
    PATTERN_EXTRACTED BOOLEAN DEFAULT FALSE,
    PATTERN_ID VARCHAR(50),              -- Link to discovered pattern
    
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

### 003_ml_tables.sql

```sql
USE DATABASE TRADE_COMPLIANCE_DB;
USE SCHEMA ML;

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
    RULE_SQL TEXT,                       -- Generated SQL
    
    -- Discovery Context
    DISCOVERY_METHOD VARCHAR(50),        -- 'CORRECTION_PATTERN', 'ANOMALY_CLUSTER', 'USER_DEFINED'
    SUPPORTING_EVIDENCE VARIANT,         -- JSON: examples that led to this rule
    CORRECTION_COUNT INT,                -- How many corrections support this
    
    -- Confidence
    CONFIDENCE_SCORE FLOAT,
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
    ANOMALY_TYPE VARCHAR(100),           -- 'STATISTICAL_OUTLIER', 'PATTERN_DEVIATION', 'MISSING_EXPECTED'
    ANOMALY_SCORE FLOAT,                 -- 0-1, higher = more anomalous
    
    -- What triggered it
    TRIGGER_FIELD VARCHAR(100),          -- Which field is anomalous
    TRIGGER_VALUE VARCHAR(200),          -- The anomalous value
    EXPECTED_RANGE VARCHAR(200),         -- What was expected
    
    -- LLM Explanation
    EXPLANATION TEXT,
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
-- RULE_EXECUTION_LOG - Track which rules fired
-- ============================================================================
CREATE OR REPLACE TABLE RULE_EXECUTION_LOG (
    LOG_ID VARCHAR(50) PRIMARY KEY,
    LINE_ID VARCHAR(50) NOT NULL,
    RULE_ID VARCHAR(50) NOT NULL,
    EXECUTION_DATE TIMESTAMP_NTZ,
    
    -- Result
    RULE_RESULT VARCHAR(10),             -- 'PASS', 'FAIL'
    RULE_OUTPUT VARIANT,                 -- Any additional output
    
    -- Performance
    EXECUTION_TIME_MS INT,
    
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

### 005_rule_engine.sql - Dynamic Rule Execution

```sql
USE DATABASE TRADE_COMPLIANCE_DB;
USE SCHEMA RULES;

-- ============================================================================
-- ACTIVE_RULES - Rules currently in production
-- ============================================================================
CREATE OR REPLACE TABLE ACTIVE_RULES (
    RULE_ID VARCHAR(50) PRIMARY KEY,
    RULE_NAME VARCHAR(255) NOT NULL,
    RULE_DESCRIPTION TEXT,
    
    -- Rule Logic
    RULE_TYPE VARCHAR(50),               -- 'SQL', 'PYTHON_UDF', 'LLM_EVAL'
    RULE_CONDITION_SQL TEXT,             -- SQL WHERE clause
    RULE_ACTION VARCHAR(50),             -- 'FAIL', 'FLAG', 'WARN'
    
    -- Applicability
    APPLIES_TO_BROKER_TYPES ARRAY,       -- ['US', 'EU'] or NULL for all
    APPLIES_TO_PRODUCT_CATEGORIES ARRAY,
    
    -- Priority
    PRIORITY INT DEFAULT 100,            -- Lower = runs first
    
    -- Status
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    
    -- Audit
    CREATED_BY VARCHAR(100),
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    MODIFIED_BY VARCHAR(100),
    MODIFIED_AT TIMESTAMP_NTZ
);

-- Insert baseline rules
INSERT INTO ACTIVE_RULES (RULE_ID, RULE_NAME, RULE_DESCRIPTION, RULE_TYPE, RULE_CONDITION_SQL, RULE_ACTION, PRIORITY) VALUES
('RULE-001', 'Part Number Exists in GTM', 'Check if broker part number exists in GTM parts list', 'SQL',
 'NOT EXISTS (SELECT 1 FROM ATOMIC.GTM_PART_MASTER g WHERE g.PART_NUMBER = l.PART_NUMBER)', 'FAIL', 10),

('RULE-002', 'US Origin Auto-Pass', 'US country of origin auto-passes HTS validation', 'SQL',
 'l.BROKER_COO = ''US''', 'PASS', 20),

('RULE-003', 'HTS Code Match', 'Broker HTS must match GTM HTS for non-US origin', 'SQL',
 'l.BROKER_COO != ''US'' AND NOT EXISTS (SELECT 1 FROM ATOMIC.GTM_PART_MASTER g WHERE g.PART_NUMBER = l.PART_NUMBER AND (g.HTS_CODE = l.BROKER_HTS_CODE OR g.HTS_CODE_ALT1 = l.BROKER_HTS_CODE))', 'FAIL', 30),

('RULE-004', '9801 Special Handling', 'HTS starting with 9801 requires special validation', 'SQL',
 'l.BROKER_HTS_CODE LIKE ''9801%'' AND NOT EXISTS (SELECT 1 FROM ATOMIC.GTM_PART_MASTER g WHERE g.PART_NUMBER = l.PART_NUMBER AND g.HTS_CODE = l.BROKER_HTS_CODE)', 'FAIL', 40),

('RULE-005', 'ADD/CVD Case Match', 'ADD/CVD case numbers must match when both have data', 'SQL',
 '(l.BROKER_ADD_CASE IS NOT NULL OR l.BROKER_CVD_CASE IS NOT NULL) AND NOT EXISTS (SELECT 1 FROM ATOMIC.GTM_PART_MASTER g WHERE g.PART_NUMBER = l.PART_NUMBER AND g.ADD_CASE_NUMBER = l.BROKER_ADD_CASE AND g.CVD_CASE_NUMBER = l.BROKER_CVD_CASE)', 'FAIL', 50);

-- ============================================================================
-- Stored Procedure: Execute all active rules on an entry
-- ============================================================================
CREATE OR REPLACE PROCEDURE RULES.EXECUTE_VALIDATION(ENTRY_ID_PARAM VARCHAR)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    result VARIANT;
BEGIN
    -- This would iterate through ACTIVE_RULES and execute each
    -- Results logged to RULE_EXECUTION_LOG
    -- Simplified for illustration
    
    UPDATE ATOMIC.ENTRY_LINE l
    SET OVERALL_STATUS = CASE 
        WHEN PART_VALIDATION = 'FAIL' OR HTS_VALIDATION = 'FAIL' OR ADDCVD_VALIDATION = 'FAIL' 
        THEN 'FAIL' ELSE 'PASS' 
    END
    WHERE l.ENTRY_ID = :ENTRY_ID_PARAM;
    
    RETURN OBJECT_CONSTRUCT('status', 'completed', 'entry_id', ENTRY_ID_PARAM);
END;
$$;
```

---

## 3. Multi-Agent Architecture

### Agent Design (Enhanced from ATLAS)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     COMPASS ORCHESTRATOR                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ ONBOARDING  │  │ VALIDATION  │  │  DISCOVERY  │  │ COMPLIANCE  │    │
│  │   AGENT     │  │   AGENT     │  │   AGENT     │  │   AGENT     │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │            │
│   AI Schema         Rules +          Learn from        Query &         │
│   Inference         Anomaly ML       Corrections       Report          │
│         │                │                │                │            │
│         └────────────────┴────────────────┴────────────────┘            │
│                                   │                                     │
│                          ┌───────▼───────┐                              │
│                          │  ORCHESTRATOR  │                             │
│                          └───────┬───────┘                              │
└──────────────────────────────────┼──────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
              ┌──────────┐                  ┌──────────┐
              │  REACT   │                  │SNOWFLAKE │
              │ FRONTEND │◄────────────────►│ CORTEX   │
              └──────────┘                  └──────────┘
```

### Onboarding Agent (NEW - not in ATLAS)

```python
class OnboardingAgent:
    """AI-powered broker onboarding via schema inference."""
    
    async def analyze_file(self, file_path: str, broker_name: str) -> Dict:
        """
        Analyze a new broker file and infer schema mapping.
        
        Uses Cortex LLM to:
        1. Parse file structure (XML, CSV, XLSB)
        2. Extract sample values from each field
        3. Semantically map to standard schema
        4. Return confidence scores per field
        """
        # Read sample of file
        sample_data = self._read_sample(file_path)
        
        # Build prompt for LLM
        prompt = f"""
        Analyze this broker file and map fields to our standard schema.
        
        Source fields with sample values:
        {sample_data}
        
        Target schema fields:
        - ENTRY_NUMBER: Customs entry identifier
        - PART_NUMBER: Product/item identifier  
        - HTS_CODE: Harmonized Tariff Schedule code (10 digits)
        - COUNTRY_OF_ORIGIN: 2-letter ISO country code
        - ENTERED_VALUE: Declared value in USD
        - DUTY_AMOUNT: Calculated duty
        - ADD_CASE: Anti-dumping case number
        - CVD_CASE: Countervailing duty case number
        
        For each source field, provide:
        1. Most likely target field match
        2. Confidence score (0-1)
        3. Reasoning for the match
        
        Return as JSON.
        """
        
        # Call Cortex LLM
        result = self.sf.cortex_complete(prompt, model='mistral-large')
        
        return {
            "mappings": result["mappings"],
            "overall_confidence": result["avg_confidence"],
            "unmapped_fields": result["unmapped"],
            "ready_for_review": result["avg_confidence"] > 0.85
        }
```

### Discovery Agent (Enhanced Hidden Discovery)

```python
class DiscoveryAgent:
    """Learn validation rules from historical corrections."""
    
    async def find_correction_patterns(self) -> Dict:
        """
        Analyze VALIDATION_CORRECTION table to find patterns
        that should become rules.
        """
        sql = """
        WITH correction_patterns AS (
            SELECT 
                FIELD_CORRECTED,
                BROKER_ID,
                COUNTRY_OF_ORIGIN,
                ORIGINAL_VALUE,
                CORRECTED_VALUE,
                COUNT(*) as occurrence_count,
                COUNT(DISTINCT PART_NUMBER) as part_count
            FROM ML.VALIDATION_CORRECTION
            WHERE PATTERN_EXTRACTED = FALSE
            GROUP BY 1,2,3,4,5
            HAVING COUNT(*) >= 5  -- At least 5 similar corrections
        )
        SELECT * FROM correction_patterns
        ORDER BY occurrence_count DESC
        """
        
        patterns = self.sf.execute_query(sql)
        
        # For each pattern, generate a rule suggestion
        suggested_rules = []
        for pattern in patterns:
            rule = await self._generate_rule_from_pattern(pattern)
            suggested_rules.append(rule)
        
        return {
            "patterns_found": len(patterns),
            "suggested_rules": suggested_rules,
            "total_corrections_covered": sum(p["occurrence_count"] for p in patterns)
        }
    
    async def _generate_rule_from_pattern(self, pattern: Dict) -> Dict:
        """Use LLM to generate a rule from a correction pattern."""
        
        prompt = f"""
        Based on this correction pattern, generate a validation rule:
        
        Pattern:
        - Field: {pattern['FIELD_CORRECTED']}
        - Broker: {pattern['BROKER_ID']}  
        - Country: {pattern['COUNTRY_OF_ORIGIN']}
        - Original value: {pattern['ORIGINAL_VALUE']}
        - Corrected to: {pattern['CORRECTED_VALUE']}
        - Occurrences: {pattern['occurrence_count']}
        
        Generate:
        1. Rule name (concise)
        2. Rule description (what it checks)
        3. SQL condition (for WHERE clause)
        4. Estimated impact
        
        Return as JSON.
        """
        
        return self.sf.cortex_complete(prompt, model='mistral-large')
```

---

## 4. Cortex Integration

### Semantic Model (entry_visibility_semantic_model.yaml)

```yaml
name: entry_visibility_model
description: >
  Semantic model for trade compliance with AI-powered validation.
  Enables natural language queries and rule authoring.

tables:
  - name: entry_lines
    description: Customs entry lines with validation results and anomaly flags.
    base_table:
      database: TRADE_COMPLIANCE_DB
      schema: ATOMIC
      table: ENTRY_LINE
    
    dimensions:
      - name: part_number
        description: Product part number
        synonyms: ["product", "item", "SKU", "article"]
      
      - name: broker_hts_code
        description: HTS code provided by broker
        synonyms: ["tariff code", "HS code", "HTSUS", "CN code"]
      
      - name: broker_coo
        description: Country of origin provided by broker
        synonyms: ["country", "origin", "COO"]
      
      - name: overall_status
        description: Final validation status
        sample_values: ["PASS", "FAIL"]
      
      - name: anomaly_flag
        description: AI-detected anomaly indicator
        sample_values: [true, false]
    
    facts:
      - name: entered_value
        description: Declared value in USD
        synonyms: ["value", "amount", "customs value"]
      
      - name: duty_amount
        description: Calculated duty in USD
      
      - name: anomaly_score
        description: AI anomaly confidence (0-1)
    
    metrics:
      - name: exception_count
        expr: SUM(CASE WHEN overall_status = 'FAIL' THEN 1 ELSE 0 END)
      
      - name: anomaly_count  
        expr: SUM(CASE WHEN anomaly_flag = TRUE THEN 1 ELSE 0 END)
      
      - name: pass_rate
        expr: SUM(CASE WHEN overall_status = 'PASS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
      
      - name: total_duty_at_risk
        expr: SUM(CASE WHEN overall_status = 'FAIL' THEN duty_amount ELSE 0 END)

  - name: brokers
    description: Broker entities with performance metrics.
    base_table:
      database: TRADE_COMPLIANCE_DB
      schema: ATOMIC
      table: BROKER
    
    dimensions:
      - name: broker_name
        synonyms: ["broker", "customs broker", "filer"]
      
      - name: broker_type
        description: US or EU broker
        sample_values: ["US", "EU"]
    
    facts:
      - name: schema_confidence
        description: AI confidence in schema mapping
      
      - name: accuracy_rate
        description: Historical validation accuracy

  - name: discovered_rules
    description: AI-suggested validation rules.
    base_table:
      database: TRADE_COMPLIANCE_DB
      schema: ML
      table: DISCOVERED_RULES
    
    dimensions:
      - name: rule_name
        synonyms: ["rule", "validation rule"]
      
      - name: status
        sample_values: ["SUGGESTED", "APPROVED", "REJECTED", "ACTIVE"]
    
    facts:
      - name: confidence_score
        description: AI confidence in rule validity
      
      - name: estimated_impact
        description: Estimated dollar impact

verified_queries:
  - name: broker_accuracy
    question: "Which broker has the worst accuracy?"
    sql: |
      SELECT b.broker_name, b.broker_type,
             COUNT(CASE WHEN l.overall_status = 'FAIL' THEN 1 END) as failures,
             COUNT(*) as total,
             ROUND(COUNT(CASE WHEN l.overall_status = 'PASS' THEN 1 END) * 100.0 / COUNT(*), 1) as accuracy_pct
      FROM __brokers b
      JOIN __entry_lines l ON b.broker_id = l.broker_id
      GROUP BY 1, 2
      ORDER BY accuracy_pct ASC

  - name: pending_rules
    question: "Show me suggested rules waiting for approval"
    sql: |
      SELECT rule_name, rule_description, confidence_score, estimated_impact
      FROM __discovered_rules
      WHERE status = 'SUGGESTED'
      ORDER BY estimated_impact DESC

  - name: anomalies_today
    question: "What anomalies were detected today?"
    sql: |
      SELECT l.part_number, l.broker_hts_code, l.anomaly_type, 
             l.anomaly_score, l.anomaly_reason
      FROM __entry_lines l
      WHERE l.anomaly_flag = TRUE
        AND l.created_at >= CURRENT_DATE()
      ORDER BY l.anomaly_score DESC

custom_instructions: >
  This is an AI-powered trade compliance system. Key capabilities:
  
  1. BROKER ONBOARDING: AI maps new broker file formats automatically
  2. RULE DISCOVERY: AI suggests new rules from correction patterns
  3. ANOMALY DETECTION: AI flags unusual entries without explicit rules
  
  When users ask about:
  - "onboarding" or "new broker" → discuss schema inference
  - "rules" or "validation" → can be known rules OR discovered rules
  - "anomalies" or "unusual" → AI-detected issues, not rule failures
  
  The system learns and improves over time based on corrections.
```

### Cortex Search Service

```sql
-- Search on exception/audit comments
CREATE OR REPLACE CORTEX SEARCH SERVICE TRADE_COMPLIANCE_DB.DOCS.EXCEPTION_SEARCH
ON COMBINED_TEXT
ATTRIBUTES BROKER_ID, EXCEPTION_TYPE, PART_NUMBER, HTS_CODE
WAREHOUSE = COMPLIANCE_COMPUTE_WH
TARGET_LAG = '1 hour'
AS (
    SELECT 
        LINE_ID,
        BROKER_ID,
        PART_NUMBER,
        BROKER_HTS_CODE as HTS_CODE,
        OVERALL_STATUS || ' - ' || COALESCE(AUDIT_COMMENT, '') || ' ' || 
        COALESCE(ANOMALY_REASON, '') AS COMBINED_TEXT
    FROM TRADE_COMPLIANCE_DB.ATOMIC.ENTRY_LINE
    WHERE OVERALL_STATUS = 'FAIL' OR ANOMALY_FLAG = TRUE
);

-- Search on discovered rules
CREATE OR REPLACE CORTEX SEARCH SERVICE TRADE_COMPLIANCE_DB.DOCS.RULE_SEARCH
ON RULE_CONTENT
ATTRIBUTES STATUS, DISCOVERY_METHOD
WAREHOUSE = COMPLIANCE_COMPUTE_WH
TARGET_LAG = '1 hour'
AS (
    SELECT 
        RULE_ID,
        STATUS,
        DISCOVERY_METHOD,
        RULE_NAME || ' - ' || RULE_DESCRIPTION || ' ' || RULE_CONDITION AS RULE_CONTENT
    FROM TRADE_COMPLIANCE_DB.ML.DISCOVERED_RULES
);
```

---

## 5. ML Notebooks

### Notebook 1: SCHEMA_INFERENCE_NB.ipynb
**Purpose**: Train/evaluate the schema mapping model
- Input: Sample broker files with known mappings
- Output: Fine-tuned prompts for field matching
- Metrics: Mapping accuracy, confidence calibration

### Notebook 2: ANOMALY_DETECTOR_NB.ipynb  
**Purpose**: Build anomaly detection model
- Input: Historical entry lines with pass/fail labels
- Features: HTS code, COO, value, duty rate, broker
- Output: Anomaly scores + explanations
- Model: Isolation Forest + LLM for explanations

### Notebook 3: RULE_DISCOVERY_NB.ipynb
**Purpose**: Mine correction patterns for rules
- Input: VALIDATION_CORRECTION table
- Method: Association rule mining + clustering
- Output: Rule suggestions with confidence scores

### Notebook 4: BROKER_SCORER_NB.ipynb
**Purpose**: Score broker performance over time
- Input: Historical accuracy by broker
- Output: Performance tiers + trend analysis

---

## 6. Application Pages

| Page | Purpose | Key Features |
|------|---------|--------------|
| **Mission Control** | Main dashboard + AI chat | KPIs, alerts, natural language queries |
| **Broker Onboarding** | Add new brokers | Upload file → AI mapping → human review |
| **Exception Report** | View validation failures | Filter by broker, type, date + export |
| **Anomaly Review** | Review AI-flagged items | Accept/reject anomalies, provide feedback |
| **Rule Discovery** | Manage AI-suggested rules | Approve/reject, see supporting evidence |
| **Broker Performance** | Broker scorecards | Accuracy trends, comparison charts |
| **Architecture** | System diagram | Interactive technical overview |

---

## 7. Deployment

### deploy.sh
```bash
#!/bin/bash
# COMPASS Trade Compliance - Snowflake Deployment

CONNECTION="${SNOWFLAKE_CONNECTION:-demo}"
DATABASE="${SNOWFLAKE_DATABASE:-TRADE_COMPLIANCE_DB}"

echo "🧭 COMPASS - AI-Powered Trade Compliance Platform"
echo "=================================================="

# Step 1: Deploy DDL
echo "📦 Step 1: Deploying database schema..."
for sql_file in ddl/*.sql; do
    snow sql -f "$sql_file" -c "$CONNECTION"
done

# Step 2: Deploy Cortex services
echo "🧠 Step 2: Deploying Cortex services..."
snow stage copy cortex/entry_visibility_semantic_model.yaml \
    "@${DATABASE}.TRADE_COMPLIANCE.SEMANTIC_MODELS" -c "$CONNECTION"
snow sql -f cortex/deploy_search.sql -c "$CONNECTION"

# Step 3: Deploy ML notebooks  
echo "📓 Step 3: Deploying ML notebooks..."
cd notebooks && bash deploy_notebooks.sh "$CONNECTION" && cd ..

# Step 4: Load sample data (if exists)
if [ -d "data/synthetic" ]; then
    echo "📊 Step 4: Loading sample data..."
    snow stage copy data/synthetic/*.parquet \
        "@${DATABASE}.RAW.BROKER_FILES" -c "$CONNECTION"
fi

echo "✅ Deployment Complete!"
echo ""
echo "Next steps:"
echo "  1. Run SCHEMA_INFERENCE_NB.ipynb to test broker onboarding"
echo "  2. Run ANOMALY_DETECTOR_NB.ipynb to train anomaly model"
echo "  3. Deploy SPCS application: cd copilot/deploy && ./deploy.sh"
```

---

## 8. Success Metrics

| Metric | Current | Target | How AI Helps |
|--------|---------|--------|--------------|
| Broker onboarding time | 2-3 weeks | < 4 hours | Schema inference |
| Rules in system | ~5 (manual) | 50+ (AI-discovered) | Rule discovery |
| Unknown issues caught | 0% | 80%+ | Anomaly detection |
| Analyst query time | Hours | Seconds | Cortex Analyst |
| Correction → Rule cycle | Never | Weekly | Continuous learning |

---

## 9. Demo Script Highlights

### Demo 1: AI Broker Onboarding

```
User uploads: new_broker_germany.xlsb

COMPASS: "I've analyzed the file from your new German broker.

📋 Schema Mapping Results (47 fields):
• ZOLL_TARIF → HTS_CODE (confidence: 97%)
• URSPRUNGSLAND → COUNTRY_OF_ORIGIN (confidence: 99%)
• ARTIKEL_NR → PART_NUMBER (confidence: 95%)
• WERT_USD → ENTERED_VALUE (confidence: 98%)

Overall confidence: 96%

3 fields need manual review:
• SONDER_CODE - I'm not sure what this maps to. Sample values: [A1, B2, C3]

Would you like to approve this mapping and start processing entries?"
```

### Demo 2: Rule Discovery

```
User: "Are there any patterns in our corrections we should codify?"

COMPASS: "Yes! I found 3 patterns that should become rules:

🔍 Pattern 1: Taiwan Valve HTS Codes
• 147 corrections in past 6 months
• All HTS 8481.* from Taiwan
• Changed from 8481.80.9000 → 8481.80.5090
• Estimated annual impact: $234,000

Suggested Rule:
'For valves (HTS 8481.*) from Taiwan, validate against 
subheading list [8481.80.5090, 8481.80.5050]'

[Approve] [Reject] [Modify]"
```

### Demo 3: Anomaly Detection

```
User: "Show me anomalies from today"

COMPASS: "I flagged 12 entries that look unusual:

⚠️ High Priority (3):
1. Entry 2024-0847, Line 5
   Part: ENG-4521, HTS: 8408.90.9000, Value: $2.3M
   Anomaly: Value is 15x typical for this part
   Score: 0.94

2. Entry 2024-0851, Line 12
   Part: PUMP-892, COO: VN, ADD Case: None
   Anomaly: Similar parts from Vietnam usually have ADD case
   Score: 0.87

[Review All] [Export to Excel]"
```

---

*Built on Snowflake • Powered by Cortex AI • Learns and Improves Over Time*
