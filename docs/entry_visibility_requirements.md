# Cummins Entry Visibility - Requirements Document

## Overview
Entry Visibility is a Cummins supply chain analytics project focused on trade compliance and customs data management. The core challenge is **scaling broker onboarding and validation rule discovery** - not just executing known rules.

## The Real Problem

### Current State Pain Points
| Challenge | Impact |
|-----------|--------|
| **6 brokers, 6 different formats** | XLSB, XML, CSV - each requires manual field mapping |
| **New broker = weeks of work** | Schema discovery, field mapping, rule writing |
| **Unknown validation rules** | EU broker has different regulations than US - rules aren't documented |
| **Manual rule maintenance** | Every regulation change requires developer intervention |
| **No pattern learning** | System doesn't learn from historical corrections |

### Why Rules-Based Approaches Don't Scale
1. **Schema Variance**: Each broker sends data differently - field names, formats, structures vary
2. **Regulatory Complexity**: US vs EU vs other regions have different compliance requirements
3. **Unknown-Unknowns**: New brokers may have validation needs nobody has documented
4. **Static Rules**: Hard-coded SQL can't adapt to new patterns

## AI-First Solution Architecture

### The Three AI Pillars

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PILLAR 1: AI-POWERED ONBOARDING                                        │
│  ─────────────────────────────────                                      │
│  New broker file (any format) → Cortex LLM → Auto schema mapping        │
│  Result: 2-hour onboarding vs 2-week projects                           │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  PILLAR 2: AI-POWERED VALIDATION                                        │
│  ─────────────────────────────────                                      │
│  Known Rules (SQL) + Unknown Patterns (ML Anomaly Detection)            │
│  Result: Catch issues even without explicit rules                       │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  PILLAR 3: AI-POWERED RULE DISCOVERY                                    │
│  ───────────────────────────────────                                    │
│  Learn from corrections → Surface patterns → Suggest new rules          │
│  Result: System gets smarter over time                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Business Context
- **Company**: Cummins (global engine/power solutions manufacturer)
- **Domain**: Supply Chain - Logistics
- **Focus**: Trade Compliance, GTM (Global Trade Management) Integration

## Key Stakeholders
- Bala Muthukrishnan (Cummins/Snowflake)
- Balamurugan Kathireasan - Architect Lead for Logistics Track
- Sunita Giriajan - 22 years at Cummins, Supply Chain Analytics
- Jeremy Dodge (Snowflake)
- Sushrutha Pokala (Cummins)

## Data Sources

### Source Systems
- **Brokers**: CEVA, EXPEDITOR, FedEx, UPS + others (5 US, 1 EU)
- **File Formats**: XLSB, XML, CSV (variety of formats)
- **Frequency**: Daily (potentially many files per day)
- **Oracle GTM**: Global Trade Management - reference data for validation

### The Schema Challenge
Each broker sends different file structures:

| Broker | Format | HTS Field | COO Field | Part Field |
|--------|--------|-----------|-----------|------------|
| CEVA | XML | `<TariffCode>` | `<OriginCountry>` | `<ProductID>` |
| FedEx | CSV | `HS_CODE` | `COUNTRY_ORIGIN` | `PART_NUM` |
| UPS | XLSB | `HTS_NUMBER` | `COO` | `ITEM_NO` |
| EU Broker | XML | `<CN_Code>` | `<CountryOfOrigin>` | `<ArticleNumber>` |

**This is why AI schema inference is critical** - humans shouldn't manually map every new format.

## AI Use Cases

### Use Case 1: Intelligent Broker Onboarding

**Problem**: New broker files require weeks of manual field mapping and ETL development.

**AI Solution**: Cortex LLM analyzes file structure and semantically maps fields.

```
Input: New XLSB file from broker "DHL"
       Columns: ZOLL_TARIF, URSPRUNGSLAND, ARTIKEL_NR, WERT_USD

AI Analysis:
  - ZOLL_TARIF (German: "customs tariff") → HTS_CODE (confidence: 97%)
  - URSPRUNGSLAND (German: "country of origin") → COO (confidence: 99%)
  - ARTIKEL_NR (German: "article number") → PART_NUMBER (confidence: 95%)
  - WERT_USD → ENTERED_VALUE (confidence: 98%)

Output: Auto-generated mapping configuration + validation SQL
```

**Benefit**: 2-hour onboarding vs 2-week projects.

### Use Case 2: Anomaly Detection (Unknown-Unknowns)

**Problem**: Can't write rules for patterns you don't know exist.

**AI Solution**: ML model trained on historical data flags statistical anomalies.

```
Examples of detected anomalies:
- "Duty rate 47% is 3 standard deviations above norm for HTS 8503"
- "This EU broker never sends ADD/CVD data - is that correct?"
- "Part X from China has no anti-dumping case but similar parts do"
- "Entry value $5M for product typically valued at $50K"
```

**Benefit**: Catch compliance issues before they become costly.

### Use Case 3: Rule Discovery from Corrections

**Problem**: Compliance team manually corrects entries, but those corrections don't improve the system.

**AI Solution**: Learn from corrections to suggest new validation rules.

```
Pattern Detected:
  - 147 entries manually corrected in past 6 months
  - All had HTS starting with "8481" (valves/taps)
  - All from Country of Origin = "Taiwan"
  - Correction: Changed HTS from 8481.80.9000 to 8481.80.5090

Suggested Rule:
  "For HTS 8481.* from Taiwan, validate against specific subheading list"
  
Compliance team reviews → approves → rule auto-codified
```

**Benefit**: System learns and improves over time.

### Use Case 4: Natural Language Rule Authoring

**Problem**: Business users know the rules but can't write SQL.

**AI Solution**: Cortex Agent translates natural language to validation logic.

```
User: "For EU imports, if the product category is 'machinery' and 
       country of origin is China, we need to check against the 
       EU anti-dumping regulation 2016/1036, not the US ADD list."

Agent Response:
  "I'll create a validation rule for EU machinery imports from China.
   
   Generated SQL:
   CASE 
     WHEN broker_type = 'EU' 
       AND product_category = 'MACHINERY'
       AND country_of_origin = 'CN'
     THEN check_eu_antidumping(hts_code, coo)
     ELSE check_us_addcvd(hts_code, coo)
   END
   
   Should I add this to the validation pipeline?"
```

**Benefit**: Democratize rule creation - no developer bottleneck.

### Use Case 5: Conversational Exception Analysis

**Problem**: Auditors need to query exception data but don't know SQL.

**AI Solution**: Cortex Analyst + Semantic Model for natural language queries.

```
User: "Which broker has the worst HTS accuracy this quarter?"
User: "Show me all China imports over $100K with ADD/CVD issues"
User: "What's our total duty exposure from HTS misclassifications?"
```

**Benefit**: Self-service analytics without BI tool training.

## Known Validation Rules (Baseline)

These are the documented rules that will be implemented as SQL:

### 1. Part Number Validation
- Check if Broker Part Number exists in GTM US parts list
- PASS if exists, FAIL if not

### 2. HTSUS Validation (Harmonized Tariff Schedule US)
- If COO (Country of Origin) = US → Auto PASS
- If COO ≠ US → Broker HTS must match any GTM HTS
  - PASS if match found, FAIL otherwise
- Special case: HTS starting with "9801"
  - If Broker HTS starts with 9801 → check if exists in GTM
  - If GTM HTS starts with 9801 → FAIL

### 3. ADD/CVD Validation (Anti-Dumping/Countervailing Duty)
- If Broker has ADD/CVD data for Part+COO:
  - Check if Trade team has ADD/CVD data for Part+COO
  - If Trade team has data but broker missing → FAIL
  - If neither has data → PASS
- If both have data → Check Part+COO+ADD and CVD Number match
  - Both match → Overall PASS
  - Either mismatch → Overall FAIL

**These known rules are the FLOOR, not the ceiling.** AI discovers additional rules.

## Key Acronyms
| Acronym | Definition |
|---------|------------|
| GTM | Global Trade Management |
| COO | Country of Origin |
| HTS | Harmonized Tariff Schedule |
| HTSUS | HTS of United States |
| ADD | Anti-Dumping Duty |
| CVD | Countervailing Duty |
| FTA | Free Trade Agreement |
| IOR | Importer of Record |
| CN Code | Combined Nomenclature (EU equivalent of HTS) |

## Exception Report (Target Output)

The Exception Report shows validation results with columns:
- Broker, Entry Date, Entry #, Entry Summary Line #, Product #
- Part Number (PASS/FAIL)
- HS Code (PASS/FAIL)
- GTM HS Code
- Preferential Program
- ADD/CVD (PASS/FAIL)
- **Anomaly Flag** (AI-detected issues without explicit rules)
- **Confidence Score** (ML model confidence)
- Audit Comments
- PDF link

## Technical Requirements

| Requirement | Solution |
|-------------|----------|
| Fast broker onboarding | AI schema inference (Cortex LLM) |
| Validation rule automation | Known rules (SQL) + Unknown patterns (ML) |
| Data quality | Anomaly detection + data profiling |
| Data lineage | Snowflake lineage tracking |
| Self-service analytics | Cortex Analyst + Semantic Model |
| Rule authoring | Cortex Agent for natural language → SQL |

## Success Metrics

| Metric | Current State | Target State |
|--------|---------------|--------------|
| Broker onboarding time | 2-3 weeks | < 4 hours |
| Rule discovery | Manual only | AI-suggested |
| Unknown issue detection | 0% (no visibility) | 80%+ anomalies flagged |
| Analyst query time | Hours (SQL required) | Seconds (natural language) |
| Compliance team productivity | Reactive | Proactive |

## The "Wow" Moment

> "A new EU broker was onboarded in **2 hours** instead of 2 weeks.
> 
> The AI automatically mapped 47 fields with 96% accuracy, including 
> German field names it had never seen before.
>
> Within the first week, it discovered 3 validation rules specific to 
> EU regulations that the team hadn't explicitly defined - saving 
> $340,000 in potential duty miscalculations.
>
> The system now suggests new rules weekly based on correction patterns,
> and compliance analysts query the data in plain English instead of 
> waiting for IT to build reports."

## Goals for Snowflake Implementation

1. **AI-Powered Broker Onboarding** - Any file format → standardized schema
2. **Hybrid Validation Engine** - Known rules (SQL) + Unknown patterns (ML)
3. **Continuous Rule Discovery** - Learn from corrections, suggest new rules
4. **Natural Language Interface** - Query data and author rules conversationally
5. **Exception Reporting** - Surface issues with confidence scores
6. **Proactive Compliance** - Catch issues before they become costly
