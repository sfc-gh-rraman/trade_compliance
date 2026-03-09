# Synthetic Data Generation Plan for Cummins Entry Visibility

## Data Extracted from Screenshots

### 1. Exception Report Structure (image6.png - PRIMARY DATA SOURCE)
The Exception Report shows actual data with these columns:

| Column | Sample Values | Data Type | Notes |
|--------|---------------|-----------|-------|
| Broker | CEVA, EXPEDITOR | VARCHAR(50) | Broker company name |
| Entry Date | 2025-10-28, 2025-11-01 | DATE | Customs entry date |
| Entry # | 00416681212, 231-4067539-5 | VARCHAR(20) | Entry number format varies by broker |
| Entry Summary Line # | 1, 2, 3, 4, 5, 6, 7 | INTEGER | Line item sequence |
| Product # | SO38774, SO38429, WOODEN SKID, E150168, 00-045836 | VARCHAR(50) | Part number format varies |
| Part Number | FAIL, PASS | VARCHAR(10) | Validation status |
| HS Code | FAIL, PASS | VARCHAR(10) | Validation status |
| GTM HS Code | Invalid Part, HS Code missing in GTM, 8302498090, 8453905090 | VARCHAR(20) | Reference HTS or error message |
| Preferential Program | PASS | VARCHAR(10) | FTA validation status |
| ADD/CVD | PASS | VARCHAR(10) | Anti-dumping/countervailing duty status |
| Audit Comments | PASS | VARCHAR(10) | Audit status |
| PDF | Yes, No | BOOLEAN | Document attachment flag |

### 2. Source Tables Identified (image1.png, image5.png)

**SCUC.FACT_TRADE_TARIFF_DETAIL** - Main transaction fact table
**SCUC.DIM_PART** - Part master dimension
**SCUC.FACT_TRADE_TARIFF_VALIDATION** - Validation results
**SCUC.DIM_ADD_CVD_VALIDATION** - ADD/CVD reference data

### 3. Validation Rules Logic (image1.png, image5.png)

| Rule | Logic | Source Tables |
|------|-------|---------------|
| PART NUMBER | Broker Part Number exists in GTM US parts list | FACT_TRADE_TARIFF_DETAIL, DIM_PART |
| HTSUS | If COO=US: PASS. If COO<>US: Broker HTS matches any GTM HTS? | FACT_TRADE_TARIFF_DETAIL, DIM_PART |
| ADD/CVD | Broker ADD/CVD data matches Trade team for Part+COO | FACT_TRADE_TARIFF_DETAIL, DIM_ADD_CVD_VALIDATION |

### 4. Data Flow Layers (image2.png)

```
Raw Layer (CORE_<ENV>_RL_FLATFILE_DB)
    ↓ Standardized
Integration Layer (CORE_<ENV>_IL_COMREF_DB)
    ↓ Basic Validation
    ├── Valid Data → Consolidated View (CORE_<ENV>_PL_PROCESSFILE_DB)
    └── Failed Data → Integration Layer (error tables)
            ↓
COMREFTRAN (CORE_<ENV>_PL_COMREF_DB, CORE_<ENV>_PL_LOGISTICS_DB)
            ↓
SCUC (SUPPLYCHAIN_<ENV>_PL_DB)
            ↓
SCEXT (SUPPLYCHAIN_<ENV>_PL_DB)
```

### 5. Brokers (image6.png)
- CEVA Logistics
- EXPEDITOR

### 6. Entry Number Patterns
- CEVA: `00416681212` (11-digit numeric)
- EXPEDITOR: `231-4067539-5` (formatted with hyphens)

---

## Synthetic Data Generation Plan

### Phase 1: Reference Data Tables

#### 1.1 GTM_PART_MASTER (DIM_PART equivalent)
```sql
CREATE TABLE SYNTHETIC.GTM_PART_MASTER (
    PART_ID VARCHAR(50) PRIMARY KEY,
    PART_NUMBER VARCHAR(50),
    DESCRIPTION VARCHAR(255),
    COMMODITY_CODE VARCHAR(20),
    HTS_CODE VARCHAR(12),
    COO_DEFAULT VARCHAR(3),
    ADD_APPLICABLE BOOLEAN,
    CVD_APPLICABLE BOOLEAN,
    FTA_ELIGIBLE BOOLEAN,
    CREATED_DATE TIMESTAMP,
    UPDATED_DATE TIMESTAMP
);
```

**Data Generation Logic:**
- Generate 5,000 part numbers following Cummins patterns:
  - SO##### (e.g., SO38774) - 40%
  - #####-##### (e.g., 00-045836) - 30%
  - E###### (e.g., E150168) - 20%
  - DESCRIPTOR (e.g., WOODEN SKID) - 10%
- HTS codes: Real 10-digit US harmonized codes from Chapters 84, 85, 87 (machinery, electrical, vehicles)

#### 1.2 GTM_HTS_REFERENCE
```sql
CREATE TABLE SYNTHETIC.GTM_HTS_REFERENCE (
    HTS_CODE VARCHAR(12) PRIMARY KEY,
    HTS_DESCRIPTION VARCHAR(500),
    CHAPTER VARCHAR(2),
    SECTION VARCHAR(50),
    DUTY_RATE DECIMAL(5,2),
    ADD_RATE DECIMAL(5,2),
    CVD_RATE DECIMAL(5,2),
    EFFECTIVE_DATE DATE,
    EXPIRATION_DATE DATE
);
```

**Data Generation Logic:**
- Source real HTS codes from US Harmonized Tariff Schedule
- Focus on chapters relevant to Cummins: 84 (machinery), 85 (electrical), 87 (vehicles), 73 (steel articles)
- Include ~500 realistic HTS codes

#### 1.3 ADD_CVD_REFERENCE
```sql
CREATE TABLE SYNTHETIC.ADD_CVD_REFERENCE (
    CASE_ID VARCHAR(50) PRIMARY KEY,
    COO VARCHAR(3),
    HTS_CODE VARCHAR(12),
    ADD_ORDER_NUMBER VARCHAR(50),
    CVD_ORDER_NUMBER VARCHAR(50),
    ADD_RATE DECIMAL(5,2),
    CVD_RATE DECIMAL(5,2),
    EFFECTIVE_DATE DATE,
    STATUS VARCHAR(20)
);
```

**Data Generation Logic:**
- Focus on countries with ADD/CVD orders: CN (China), MX (Mexico), IN (India), KR (Korea)
- ~200 realistic ADD/CVD case combinations

### Phase 2: Broker Raw Data (Multi-Format)

#### 2.1 BROKER_CEVA_RAW (XML-like structure)
```sql
CREATE TABLE SYNTHETIC.BROKER_CEVA_RAW (
    FILE_ID VARCHAR(50),
    LOAD_TIMESTAMP TIMESTAMP,
    ENTRY_NUM VARCHAR(20),
    ENTRY_DT DATE,
    LINE_NUM INTEGER,
    ITEM_NUM VARCHAR(50),       -- Their field name for Part Number
    TARIFF_NUM VARCHAR(20),     -- Their field name for HTS
    ORIGIN_CTRY VARCHAR(3),
    ENTERED_VALUE DECIMAL(15,2),
    DUTY_AMT DECIMAL(15,2),
    ADD_FLAG VARCHAR(1),
    CVD_FLAG VARCHAR(1),
    RAW_XML TEXT
);
```

**Format Characteristics (CEVA):**
- Entry numbers: 11-digit numeric (e.g., 00416681212)
- XML source files
- Field names: ITEM_NUM, TARIFF_NUM, ORIGIN_CTRY
- Dates: YYYY-MM-DD format

#### 2.2 BROKER_EXPEDITOR_RAW (CSV-like structure)
```sql
CREATE TABLE SYNTHETIC.BROKER_EXPEDITOR_RAW (
    FILE_ID VARCHAR(50),
    LOAD_TIMESTAMP TIMESTAMP,
    ENTRY_NUMBER VARCHAR(20),
    ENTRY_DATE VARCHAR(20),     -- MM/DD/YYYY format
    LINE_NO INTEGER,
    PART_NO VARCHAR(50),        -- Different field name
    HTS VARCHAR(20),            -- Different field name
    COUNTRY_OF_ORIGIN VARCHAR(50), -- Full country name
    VALUE DECIMAL(15,2),
    DUTY DECIMAL(15,2),
    ANTIDUMPING VARCHAR(10),
    COUNTERVAILING VARCHAR(10)
);
```

**Format Characteristics (EXPEDITOR):**
- Entry numbers: Hyphenated format (e.g., 231-4067539-5)
- CSV source files
- Field names: PART_NO, HTS, COUNTRY_OF_ORIGIN
- Dates: MM/DD/YYYY format

#### 2.3 BROKER_KUEHNE_RAW (XLSB-like structure - NEW BROKER)
```sql
CREATE TABLE SYNTHETIC.BROKER_KUEHNE_RAW (
    DATEI_ID VARCHAR(50),
    LADEN_ZEIT TIMESTAMP,
    EINTRITTSNUMMER VARCHAR(20),     -- German field names
    EINTRITTSDATUM DATE,
    ZEILE INTEGER,
    TEILENUMMER VARCHAR(50),
    ZOLLTARIFNUMMER VARCHAR(20),
    URSPRUNGSLAND VARCHAR(3),
    WARENWERT DECIMAL(15,2),
    ZOLLBETRAG DECIMAL(15,2),
    ANTIDUMPING_ZOLL VARCHAR(1),
    AUSGLEICHSZOLL VARCHAR(1)
);
```

**Format Characteristics (Kuehne+Nagel - Simulated New Broker):**
- German field names (tests AI schema inference)
- XLSB binary Excel format
- Entry numbers: Different format (DE-2025-######)
- Dates: DD.MM.YYYY format

### Phase 3: Integrated/Standardized Layer

#### 3.1 FACT_TRADE_TARIFF_DETAIL
```sql
CREATE TABLE SYNTHETIC.FACT_TRADE_TARIFF_DETAIL (
    LINE_ID VARCHAR(50) PRIMARY KEY,
    ENTRY_ID VARCHAR(50),
    ENTRY_NUMBER VARCHAR(20),
    ENTRY_DATE DATE,
    BROKER_ID VARCHAR(50),
    BROKER_NAME VARCHAR(100),
    LINE_NUMBER INTEGER,
    PART_NUMBER VARCHAR(50),
    PART_DESCRIPTION VARCHAR(255),
    BROKER_HTS_CODE VARCHAR(12),
    COUNTRY_OF_ORIGIN VARCHAR(3),
    ENTERED_VALUE DECIMAL(15,2),
    DUTY_AMOUNT DECIMAL(15,2),
    ADD_AMOUNT DECIMAL(15,2),
    CVD_AMOUNT DECIMAL(15,2),
    BROKER_ADD_FLAG BOOLEAN,
    BROKER_CVD_FLAG BOOLEAN,
    LOAD_TIMESTAMP TIMESTAMP,
    SOURCE_FILE VARCHAR(255)
);
```

### Phase 4: Corrections History (CRITICAL for Unknown-Known Rule Discovery)

#### 4.1 CORRECTIONS_HISTORY (Semantic-Rich for LLM Analysis)
```sql
CREATE TABLE SYNTHETIC.CORRECTIONS_HISTORY (
    CORRECTION_ID VARCHAR(50) PRIMARY KEY,
    LINE_ID VARCHAR(50),
    ENTRY_NUMBER VARCHAR(20),
    ENTRY_DATE DATE,
    BROKER_NAME VARCHAR(100),
    PART_NUMBER VARCHAR(50),
    COUNTRY_OF_ORIGIN VARCHAR(3),
    HTS_CODE VARCHAR(12),
    ENTERED_VALUE DECIMAL(15,2),
    
    -- What was corrected
    FIELD_CORRECTED VARCHAR(50),
    ORIGINAL_VALUE VARCHAR(255),
    CORRECTED_VALUE VARCHAR(255),
    
    -- SEMANTIC FIELDS FOR LLM REASONING (FREE TEXT)
    CORRECTION_REASON TEXT,              -- "Per CBP ruling HQ H301245 dated 2024-03-15 on Chinese electrical assemblies"
    ANALYST_NOTES TEXT,                  -- "Broker didn't check Section 301 list. Common issue with CEVA on electronics."
    REGULATORY_REFERENCE TEXT,           -- "19 CFR 159.1; USTR Section 301 List 3; AD Order A-570-067"
    RELATED_CASES TEXT,                  -- "Similar to CORR-2024-1123, CORR-2024-0892 - same root cause"
    BUSINESS_CONTEXT TEXT,               -- "Part of engine assembly line - high volume, critical path"
    
    -- Structured metadata
    CORRECTION_CATEGORY VARCHAR(50),
    CORRECTED_BY VARCHAR(100),
    CORRECTION_DATE TIMESTAMP,
    WAS_FLAGGED_BY_SYSTEM BOOLEAN,
    CONFIDENCE_LEVEL VARCHAR(20),        -- How certain was the analyst? HIGH/MEDIUM/LOW
    TIME_TO_RESOLVE_MINUTES INTEGER,     -- How long did this take to figure out?
    REQUIRED_RESEARCH BOOLEAN,           -- Did analyst need to look up regulations?
    
    -- Embedding for semantic search (populated by Cortex)
    REASON_EMBEDDING VECTOR(FLOAT, 768)  -- For semantic similarity clustering
);
```

**This table is the GOLD MINE for LLM-powered rule discovery.** The free-text fields contain the semantic richness that enables LLM reasoning beyond simple pattern counting.

#### 4.2 Semantic Correction Examples (LLM Training Data)

These examples show how DIFFERENT analyst language describes the SAME underlying rule - the LLM must understand semantic equivalence:

**Pattern CP-001: Chinese Electrical Components → ADD Applicable**

| Correction ID | CORRECTION_REASON | ANALYST_NOTES | REGULATORY_REFERENCE |
|---------------|-------------------|---------------|----------------------|
| CORR-001 | "ADD applies per CBP ruling HQ H301245 on Chinese electrical assemblies" | "CEVA keeps missing this. Third time this month." | "AD Order A-570-067; 19 CFR 159.1" |
| CORR-047 | "Antidumping duty required - PRC origin motor components" | "Broker flagged as non-ADD but it's clearly covered" | "Section 301 List 3, USTR 2018" |
| CORR-089 | "China ADD order covers this - check USITC database" | "E-prefix parts are usually electrical = ADD country" | "A-570-067" |
| CORR-112 | "需要反倾销税 - broker missed it" | "Analyst Li caught this, added Chinese note" | "Commerce Dept AD order" |

**LLM must recognize these 4 corrections describe ONE rule** despite different wording, languages, and specificity levels.

**Pattern CP-004: Indian Steel Fasteners → CVD Applicable**

| Correction ID | CORRECTION_REASON | ANALYST_NOTES | REGULATORY_REFERENCE |
|---------------|-------------------|---------------|----------------------|
| CORR-201 | "CVD applies to Indian fasteners per C-533-866" | "Standard issue with bolts/nuts from India" | "CVD Order C-533-866" |
| CORR-215 | "Countervailing duty missing - Indian origin steel" | "HTS 7318 = fasteners, India = CVD. Simple." | "19 USC 1671" |
| CORR-230 | "India CVD case covers threaded fasteners" | "EXPEDITOR doesn't check CVD on Indian goods" | "ITC Investigation 701-TA-549" |

**Pattern CP-007: USMCA Exemption (Contradicts Simple Rules)**

| Correction ID | CORRECTION_REASON | ANALYST_NOTES | REGULATORY_REFERENCE |
|---------------|-------------------|---------------|----------------------|
| CORR-301 | "USMCA certificate on file - ADD doesn't apply" | "Broker over-declared. Mexico origin with valid cert = exempt" | "19 CFR 182; USMCA Art 2.4" |
| CORR-318 | "Remove ADD - preferential treatment under trade agreement" | "Check the cert before flagging Mexican goods" | "USMCA Rules of Origin" |

**This is where LLM reasoning shines:** It can learn that "Mexico + ADD = usually exempt IF USMCA certified" - a nuanced rule that simple pattern matching would miss.

#### 4.3 Correction Pattern Seeds (With Semantic Variations)

| Pattern ID | Field | Original → Corrected | Context | Frequency | Discoverable Rule |
|------------|-------|---------------------|---------|-----------|-------------------|
| CP-001 | ADD_FLAG | N → Y | PART starts with 'E', COO='CN' | 47 | "E-prefix parts from China always have ADD" |
| CP-002 | HTS_CODE | 8453905090 → 8453906000 | Chapter 84 subheading | 23 | "Common misclassification in metal-cutting machines" |
| CP-003 | PREFERENTIAL | Y → N | VALUE > $50,000 | 15 | "High-value entries don't qualify for FTA preference" |
| CP-004 | CVD_FLAG | N → Y | COO='IN', HTS starts with '7318' | 31 | "Indian steel fasteners have CVD" |
| CP-005 | COO | CN → TW | PART contains 'PRECISION' | 12 | "Precision parts often misattributed to China vs Taiwan" |
| CP-006 | HTS_CODE | 8544422000 → 8544429090 | Insulated wire > 80V | 19 | "Voltage classification affects HTS for electrical cables" |
| CP-007 | ADD_FLAG | Y → N | COO='MX', USMCA certified | 28 | "USMCA-certified Mexican goods exempt from ADD" |
| CP-008 | DUTY_AMOUNT | Calculated → Manual | Multiple HTS per line | 8 | "Split-line entries require manual duty calc" |

#### 4.3 Correction Generation Logic
```python
# Corrections follow patterns that can be mined
CORRECTION_PATTERNS = [
    {
        "pattern_id": "CP-001",
        "condition": lambda row: row['PART_NUMBER'].startswith('E') and row['COO'] == 'CN',
        "field": "ADD_FLAG",
        "from_value": "N",
        "to_value": "Y",
        "reason": "ADD applicable per CBP ruling - E-prefix parts from China",
        "category": "ADD_CVD_COMPLIANCE",
        "frequency": 47,  # How many times to inject
    },
    {
        "pattern_id": "CP-002", 
        "condition": lambda row: row['BROKER_HTS_CODE'] == '8453905090',
        "field": "HTS_CODE",
        "from_value": "8453905090",
        "to_value": "8453906000",
        "reason": "Correct subheading for metal-cutting machine parts",
        "category": "HTS_CLASSIFICATION",
        "frequency": 23,
    },
    # ... additional patterns
]
```

#### 4.4 LLM-Powered Rule Discovery Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     LLM SEMANTIC RULE DISCOVERY PIPELINE                     │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: SEMANTIC CLUSTERING (not frequency counting)
┌─────────────────────────────────────────────────────────────────────────────┐
│  LLM reads CORRECTION_REASON + ANALYST_NOTES from all corrections           │
│                                                                             │
│  Groups by MEANING, not exact text:                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Cluster A: "Chinese electrical ADD"                                  │   │
│  │   - "ADD applies per CBP ruling HQ H301245 on Chinese electrical"   │   │
│  │   - "Antidumping duty required - PRC origin motor components"       │   │
│  │   - "需要反倾销税 - broker missed it"  (Chinese language!)           │   │
│  │   - "China ADD order covers this"                                    │   │
│  │   → 47 corrections, 4 different phrasings, 2 languages              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

Step 2: REGULATORY GROUNDING
┌─────────────────────────────────────────────────────────────────────────────┐
│  LLM extracts cited regulations from REGULATORY_REFERENCE field:            │
│                                                                             │
│  Cluster A references:                                                      │
│    - "AD Order A-570-067" (3 mentions)                                     │
│    - "19 CFR 159.1" (2 mentions)                                           │
│    - "Section 301 List 3" (1 mention)                                      │
│                                                                             │
│  LLM validates: "A-570-067 is real AD order for Chinese electrical goods"  │
│  Confidence boost: Rule is grounded in actual regulation                    │
└─────────────────────────────────────────────────────────────────────────────┘

Step 3: GENERALIZATION (beyond observed patterns)
┌─────────────────────────────────────────────────────────────────────────────┐
│  LLM reasons beyond exact matches:                                          │
│                                                                             │
│  Observed: "E-prefix parts from China → ADD"                               │
│  LLM asks: "What makes E-prefix special?"                                  │
│  LLM infers: "E = Electrical components. AD Order A-570-067 covers         │
│               electrical goods broadly, not just E-prefix."                 │
│                                                                             │
│  GENERALIZED RULE: "Electrical components (HTS Chapter 85) from China      │
│                     are subject to AD Order A-570-067"                      │
│                                                                             │
│  This catches parts that don't start with 'E' but ARE electrical!          │
└─────────────────────────────────────────────────────────────────────────────┘

Step 4: CONTRADICTION DETECTION
┌─────────────────────────────────────────────────────────────────────────────┐
│  LLM finds conflicting corrections:                                         │
│                                                                             │
│  Correction 301: "Mexico origin → ADD applies"                             │
│  Correction 318: "Mexico origin → ADD exempt (USMCA)"                      │
│                                                                             │
│  LLM reasons: "Both are correct! Difference is USMCA certification."       │
│                                                                             │
│  NUANCED RULE: "Mexican goods subject to ADD UNLESS USMCA cert on file"    │
│                                                                             │
│  Simple pattern mining would see contradiction and give up.                 │
│  LLM understands the conditional logic.                                     │
└─────────────────────────────────────────────────────────────────────────────┘

Step 5: SPARSE EXAMPLE REASONING
┌─────────────────────────────────────────────────────────────────────────────┐
│  Only 3 corrections mention "Vietnamese steel" but LLM knows:               │
│                                                                             │
│  - AD/CVD orders exist for Vietnamese steel (domain knowledge)             │
│  - Pattern matches Indian steel corrections (semantic similarity)           │
│  - Analyst notes say "Same as India case" (explicit link)                  │
│                                                                             │
│  SUGGESTED RULE (high confidence despite sparse data):                      │
│  "Vietnamese steel products (HTS 72xx, 73xx) subject to AD/CVD"            │
└─────────────────────────────────────────────────────────────────────────────┘

OUTPUT: DISCOVERED_RULES table with LLM-generated entries
┌─────────────────────────────────────────────────────────────────────────────┐
│  RULE_ID: DR-2025-001                                                       │
│  RULE_NAME: "Chinese Electrical Components ADD"                             │
│  RULE_LOGIC: HTS_CODE LIKE '85%' AND COO = 'CN' → ADD_FLAG = 'Y'           │
│  CONFIDENCE: 0.94                                                           │
│  EVIDENCE_COUNT: 47 corrections                                             │
│  REGULATORY_BASIS: "AD Order A-570-067; 19 CFR 159.1"                      │
│  LLM_REASONING: "Clustered 47 corrections with 4 distinct phrasings.       │
│                  Generalized from E-prefix to Chapter 85 based on           │
│                  regulatory scope. Validated against AD order database."    │
│  SUGGESTED_BY: AI_RULE_DISCOVERY_AGENT                                      │
│  STATUS: PENDING_REVIEW                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 5: Validation Results

#### 5.1 FACT_TRADE_TARIFF_VALIDATION
```sql
CREATE TABLE SYNTHETIC.FACT_TRADE_TARIFF_VALIDATION (
    VALIDATION_ID VARCHAR(50) PRIMARY KEY,
    LINE_ID VARCHAR(50),
    ENTRY_NUMBER VARCHAR(20),
    ENTRY_DATE DATE,
    BROKER_NAME VARCHAR(100),
    LINE_NUMBER INTEGER,
    PART_NUMBER VARCHAR(50),
    
    -- Validation Results (PASS/FAIL)
    PART_NUMBER_STATUS VARCHAR(10),
    PART_NUMBER_MESSAGE VARCHAR(255),
    
    HS_CODE_STATUS VARCHAR(10),
    HS_CODE_MESSAGE VARCHAR(255),
    GTM_HS_CODE VARCHAR(12),
    
    PREFERENTIAL_PROGRAM_STATUS VARCHAR(10),
    PREFERENTIAL_PROGRAM_MESSAGE VARCHAR(255),
    
    ADD_CVD_STATUS VARCHAR(10),
    ADD_CVD_MESSAGE VARCHAR(255),
    
    AUDIT_COMMENTS_STATUS VARCHAR(10),
    AUDIT_COMMENTS VARCHAR(500),
    
    PDF_ATTACHED BOOLEAN,
    
    OVERALL_STATUS VARCHAR(10),
    VALIDATION_TIMESTAMP TIMESTAMP
);
```

---

## Data Generation Scripts

### Volume Targets

| Table | Row Count | Notes |
|-------|-----------|-------|
| GTM_PART_MASTER | 5,000 | Parts in GTM system |
| GTM_HTS_REFERENCE | 500 | US HTS codes |
| ADD_CVD_REFERENCE | 200 | Active ADD/CVD cases |
| BROKER_CEVA_RAW | 50,000 | 6 months of entries |
| BROKER_EXPEDITOR_RAW | 30,000 | 6 months of entries |
| BROKER_KUEHNE_RAW | 10,000 | New broker onboarding simulation |
| FACT_TRADE_TARIFF_DETAIL | 90,000 | Combined standardized |
| FACT_TRADE_TARIFF_VALIDATION | 90,000 | All validation results |
| CORRECTIONS_HISTORY | 2,500 | Historical analyst corrections (rule mining source) |

### Error Distribution (Realistic)

Based on image6.png exception report patterns:

| Validation Type | Pass Rate | Fail Patterns |
|-----------------|-----------|---------------|
| Part Number | 70% | "Invalid Part", Part not in GTM |
| HS Code | 65% | "HS Code missing in GTM", mismatch |
| GTM HS Code | 80% | Missing reference, multiple matches |
| Preferential Program | 95% | FTA eligibility issues |
| ADD/CVD | 90% | Missing broker declaration |

### Anomaly Injection (for ML Training)

| Anomaly Type | Injection Rate | Description |
|--------------|----------------|-------------|
| Value Outliers | 2% | Entered values 10x normal |
| HTS Drift | 1% | Same part, changing HTS over time |
| Duty Arbitrage | 0.5% | Suspiciously low duty rates |
| New Pattern | 3% | Never-before-seen combinations |

---

## Implementation Order

### Step 1: Reference Data (Day 1)
```python
# Generate GTM_PART_MASTER with realistic Cummins part patterns
# Generate GTM_HTS_REFERENCE from public HTS data
# Generate ADD_CVD_REFERENCE for key countries
```

### Step 2: Broker Raw Data (Day 2-3)
```python
# Generate CEVA data with XML-style field naming
# Generate EXPEDITOR data with CSV-style field naming
# Generate KUEHNE data with German field names (AI inference test)
```

### Step 3: Standardized Layer (Day 4)
```python
# Transform broker data to FACT_TRADE_TARIFF_DETAIL
# Apply field mapping transformations
# Document schema inference requirements
```

### Step 4: Validation Layer (Day 5)
```python
# Execute validation rules
# Generate FACT_TRADE_TARIFF_VALIDATION
# Inject realistic error patterns
```

### Step 5: Anomaly Injection (Day 6)
```python
# Inject statistical anomalies
# Create "unknown unknown" patterns
# Document for ML model training
```

---

## Key Realism Factors

### 1. Broker-Specific Entry Number Formats
- CEVA: `00416681212` (11 digits, no separators)
- EXPEDITOR: `231-4067539-5` (hyphenated)
- Kuehne: `DE-2025-001234` (prefix + year + sequence)

### 2. Field Name Variations (Schema Inference Challenge)
| Standard Field | CEVA | EXPEDITOR | Kuehne |
|----------------|------|-----------|--------|
| part_number | ITEM_NUM | PART_NO | TEILENUMMER |
| hts_code | TARIFF_NUM | HTS | ZOLLTARIFNUMMER |
| country_of_origin | ORIGIN_CTRY | COUNTRY_OF_ORIGIN | URSPRUNGSLAND |
| entry_date | ENTRY_DT | ENTRY_DATE | EINTRITTSDATUM |

### 3. Date Format Variations
- CEVA: YYYY-MM-DD
- EXPEDITOR: MM/DD/YYYY
- Kuehne: DD.MM.YYYY

### 4. Country Code Variations
- CEVA: ISO 2-letter (CN, MX, US)
- EXPEDITOR: Full name (China, Mexico, United States)
- Kuehne: ISO 3-letter (CHN, MEX, USA)

### 5. HTS Code Format Variations
- CEVA: 8302498090 (10 digits, no dots)
- EXPEDITOR: 8302.49.80.90 (with dots)
- Kuehne: 8302 4980 90 (with spaces)

---

## Validation Test Cases

### Test Case 1: Schema Inference
Load BROKER_KUEHNE_RAW and verify AI correctly maps:
- TEILENUMMER → part_number
- ZOLLTARIFNUMMER → hts_code
- URSPRUNGSLAND → country_of_origin

### Test Case 2: Anomaly Detection
Verify ML model flags:
- Part SO38774 with entered_value of $1,000,000 (normal: $500)
- Same part with 5 different HTS codes in 30 days
- Entry with 0% duty when ADD applies

### Test Case 3: LLM Semantic Rule Discovery (Unknown-Known Rules)

**This tests LLM reasoning, NOT SQL pattern counting.**

#### 3A: Semantic Clustering Test
Inject 47 corrections with DIFFERENT phrasings for the SAME rule:
- "ADD applies per CBP ruling HQ H301245 on Chinese electrical assemblies"
- "Antidumping duty required - PRC origin motor components"  
- "需要反倾销税 - broker missed it" (Chinese language)
- "China ADD order covers this - check USITC database"

**Pass Criteria:** LLM clusters all 47 as ONE rule despite language/phrasing differences.

#### 3B: Generalization Test
Corrections mention "E-prefix parts" but LLM should generalize:
- Observed: E-prefix + CN → ADD
- Expected LLM output: "HTS Chapter 85 (electrical) from China → ADD"
- Reasoning: LLM understands E-prefix = Electrical, and AD order covers chapter broadly

**Pass Criteria:** Suggested rule covers MORE than just E-prefix parts.

#### 3C: Contradiction Resolution Test
Inject conflicting corrections:
- CORR-301: "Mexico origin → ADD applies"
- CORR-318: "Mexico origin → ADD exempt (USMCA)"

**Pass Criteria:** LLM outputs CONDITIONAL rule: "Mexican goods subject to ADD UNLESS USMCA certified"

#### 3D: Sparse Example Reasoning Test
Only 3 corrections mention Vietnamese steel, but LLM should still suggest rule:
- Evidence: 3 corrections + analyst note "Same as India case"
- LLM knowledge: AD/CVD orders exist for Vietnamese steel
- Semantic similarity: Matches Indian steel correction pattern

**Pass Criteria:** LLM suggests Vietnamese steel CVD rule with confidence > 70% despite only 3 examples.

#### 3E: Regulatory Grounding Test
Verify LLM extracts and validates regulatory citations:
- Input: REGULATORY_REFERENCE = "AD Order A-570-067; 19 CFR 159.1"
- Expected: LLM confirms these are real regulations in output

**Pass Criteria:** DISCOVERED_RULES.REGULATORY_BASIS contains validated citations.

| Test | Input | Expected LLM Behavior | Pass Criteria |
|------|-------|----------------------|---------------|
| 3A | 47 corrections, 4 phrasings, 2 languages | Semantic clustering | 1 cluster output |
| 3B | E-prefix corrections | Generalization to Chapter 85 | Broader rule scope |
| 3C | Contradictory Mexico corrections | Conditional rule generation | IF/THEN logic in rule |
| 3D | 3 Vietnamese steel corrections | Sparse reasoning | Confidence > 70% |
| 3E | Regulatory references in text | Citation extraction | Valid CFR/AD references |

### Test Case 4: New Broker Onboarding (End-to-End)
Simulate onboarding Kuehne+Nagel:
1. Load BROKER_KUEHNE_RAW with German field names
2. AI Schema Inference maps fields automatically
3. First batch processed - some fail validation
4. Corrections entered by analysts
5. After 50+ corrections, rule discovery surfaces new patterns specific to Kuehne
6. New rules auto-proposed and activated

---

## Files to Generate

```
/data/synthetic/
├── reference/
│   ├── gtm_part_master.csv
│   ├── gtm_hts_reference.csv
│   └── add_cvd_reference.csv
├── broker_raw/
│   ├── ceva/
│   │   ├── ceva_entry_202510.xml
│   │   └── ceva_entry_202511.xml
│   ├── expeditor/
│   │   ├── expeditor_202510.csv
│   │   └── expeditor_202511.csv
│   └── kuehne/
│       └── kuehne_entries.xlsb
├── integrated/
│   └── fact_trade_tariff_detail.parquet
├── validation/
│   └── fact_trade_tariff_validation.parquet
└── corrections/
    └── corrections_history.parquet       # THE RULE DISCOVERY GOLD MINE
```

This synthetic data plan creates realistic data that:
1. **Matches actual Cummins data structure** from screenshots
2. **Tests AI schema inference** with multi-format, multi-language broker files
3. **Enables anomaly detection training** with injected outliers
4. **Supports LLM-powered rule discovery** with semantic-rich CORRECTIONS_HISTORY:
   - Free-text CORRECTION_REASON and ANALYST_NOTES for semantic clustering
   - Multi-language corrections (English + Chinese) to test cross-lingual understanding
   - Contradictory corrections to test conditional rule generation
   - Regulatory citations for grounding validation
   - Sparse examples to test reasoning beyond frequency counting
5. **Tests the full LLM reasoning pipeline:**
   - Semantic clustering (not just exact match)
   - Generalization (E-prefix → Chapter 85)
   - Contradiction resolution (Mexico ADD vs USMCA exempt)
   - Sparse example reasoning (3 corrections → high-confidence rule)
   - Regulatory grounding (cite real CFR/AD orders)
