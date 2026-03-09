# CUMMINS ENTRY VISIBILITY - MASTER IMPLEMENTATION PLAN
## AI-First Trade Compliance Platform

**Status**: IN PROGRESS  
**Last Updated**: March 9, 2026  
**Target Completion**: TBD

---

## EXECUTIVE SUMMARY

Build an AI-powered trade compliance platform that solves the **scaling problem** of broker onboarding and rule discovery. Unlike traditional rules-based systems, this uses AI to:
1. **Auto-map new broker schemas** (any format, any language)
2. **Detect anomalies without explicit rules**
3. **Discover new rules from correction patterns using LLM semantic reasoning**

### Architecture Pattern
Following the ATLAS Capital Delivery reference application:
- **Frontend**: React 18 + TypeScript + Tailwind
- **Backend**: FastAPI + Python multi-agent system
- **AI Layer**: Snowflake Cortex (Analyst, Search, Agent, LLM)
- **Data Layer**: Snowflake (RAW → ATOMIC → ML → RULES schemas)
- **Deployment**: SPCS (Snowpark Container Services)

---

## PHASE 0: FOUNDATION
**Status**: ✅ COMPLETE

### 0.1 Project Setup
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Create project folder structure | ✅ DONE | - | `/copilot`, `/cortex`, `/ddl`, `/notebooks`, `/data`, `/docs` |
| [x] Document requirements | ✅ DONE | - | `/docs/entry_visibility_requirements.md` |
| [x] Document implementation plan | ✅ DONE | - | `/docs/implementation_plan.md` |
| [x] Document synthetic data plan | ✅ DONE | - | `/docs/synthetic_data_plan.md` |
| [x] Create master tracking document | ✅ DONE | - | This file |

### 0.2 Synthetic Data Generation
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Create reference data generator | ✅ DONE | SubAgent | GTM_PART_MASTER (5K), GTM_HTS_REFERENCE (500), ADD_CVD_REFERENCE (200) |
| [x] Create CEVA broker raw data | ✅ DONE | SubAgent | CSV, 50K rows, CEVA naming conventions |
| [x] Create EXPEDITOR broker raw data | ✅ DONE | SubAgent | CSV, 30K rows, EXPEDITOR naming (hyphenated, dots) |
| [x] Create KUEHNE broker raw data | ✅ DONE | SubAgent | CSV, 10K rows, German field names for AI inference test |
| [x] Create integrated FACT_TRADE_TARIFF_DETAIL | ✅ DONE | SubAgent | 90K rows standardized from 3 brokers |
| [x] Create FACT_TRADE_TARIFF_VALIDATION | ✅ DONE | SubAgent | 90K rows, 70% part pass, 65% HTS pass |
| [x] Create CORRECTIONS_HISTORY | ✅ DONE | SubAgent | 2,500 rows with 8 discoverable patterns for LLM |
| [x] Inject anomalies (2% outliers) | ✅ DONE | SubAgent | 2% anomalies in validation data |

---

## PHASE 1: DATABASE & INFRASTRUCTURE
**Status**: ✅ COMPLETE

### 1.1 DDL Deployment
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Create database and schemas | ✅ DONE | - | RAW, ATOMIC, TRADE_COMPLIANCE, ML, DOCS, RULES, SPCS |
| [x] Create atomic tables | ✅ DONE | - | BROKER, ENTRY_HEADER, ENTRY_LINE, GTM_PART_MASTER, VALIDATION_CORRECTION |
| [x] Create ML tables | ✅ DONE | - | DISCOVERED_RULES, ANOMALY_DETECTIONS, SCHEMA_INFERENCE_LOG, SEMANTIC_CLUSTERS |
| [x] Create datamart views | ✅ DONE | - | V_EXCEPTION_REPORT, V_BROKER_SCORECARD, V_KPI_SUMMARY + 3 more |
| [x] Create rule engine objects | ✅ DONE | - | ACTIVE_RULES, EXECUTE_VALIDATION_BATCH, ACTIVATE_DISCOVERED_RULE |
| [x] Create stages | ✅ DONE | - | BROKER_FILES, GTM_EXPORTS, SEMANTIC_MODELS, MODEL_ARTIFACTS |
| [x] Create warehouses | ✅ DONE | - | COMPLIANCE_COMPUTE_WH, COMPLIANCE_ML_WH |

### 1.2 Data Loading
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Load reference data | ⬜ TODO | - | GTM parts, HTS codes, ADD/CVD reference |
| [ ] Load broker raw data | ⬜ TODO | - | CEVA, EXPEDITOR, KUEHNE test data |
| [ ] Load corrections history | ⬜ TODO | - | For rule discovery testing |

---

## PHASE 2: CORTEX AI SERVICES
**Status**: ✅ COMPLETE

### 2.1 Semantic Model (Cortex Analyst)
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Design semantic model YAML | ✅ DONE | SubAgent | Tables: entry_lines, brokers, discovered_rules, anomaly_detections |
| [x] Define dimensions and facts | ✅ DONE | SubAgent | part_number, hts_code, anomaly_flag, entered_value, duty_at_risk |
| [x] Define metrics | ✅ DONE | SubAgent | exception_count, pass_rate, total_duty_at_risk, anomaly_score |
| [x] Create verified queries | ✅ DONE | SubAgent | 6 queries: worst_broker, pending_rules, todays_anomalies, etc. |
| [x] Write custom instructions | ✅ DONE | SubAgent | AI-first guidance for trade compliance domain |
| [x] Deploy semantic model to stage | ✅ DONE | - | `@TRADE_COMPLIANCE.SEMANTIC_MODELS/trade_compliance_semantic_model.yaml` |
| [ ] Test with sample questions | ⬜ TODO | - | "Which broker has worst accuracy?" |

### 2.2 Cortex Search Services
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Create EXCEPTION_SEARCH service | ✅ DONE | - | Search on validation failures and anomalies |
| [x] Create RULE_SEARCH service | ✅ DONE | - | Search on discovered + active rules |
| [x] Create CORRECTION_SEARCH service | ✅ DONE | - | Search historical corrections for patterns |

### 2.3 Cortex Agent
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Define agent tools | ✅ DONE | SubAgent | 10 tools: validate_entry, search_exceptions, suggest_rule, etc. |
| [x] Create agent prompt template | ✅ DONE | SubAgent | Trade compliance domain context + AI capabilities |
| [ ] Implement tool handlers | ⬜ TODO | SubAgent | Python functions for each tool |
| [ ] Test conversational flows | ⬜ TODO | - | "Show me anomalies from today" |

---

## PHASE 3: ML NOTEBOOKS
**Status**: 🟡 IN PROGRESS

### 3.1 Schema Inference Notebook
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Design LLM prompt for field mapping | ⬜ TODO | SubAgent | Handle multilingual field names |
| [ ] Implement file parsing (XML, CSV, XLSB) | ⬜ TODO | SubAgent | Sample extraction logic |
| [ ] Create inference pipeline | ⬜ TODO | SubAgent | File → LLM → Mapping JSON |
| [ ] Evaluate on test brokers | ⬜ TODO | SubAgent | KUEHNE German test case |
| [ ] Calibrate confidence scores | ⬜ TODO | SubAgent | Ensure accuracy reflects confidence |

### 3.2 Anomaly Detector Notebook
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Feature engineering | ⬜ TODO | SubAgent | HTS, COO, value, duty rate features |
| [ ] Train Isolation Forest model | ⬜ TODO | SubAgent | On historical pass/fail data |
| [ ] Add LLM explanation layer | ⬜ TODO | SubAgent | Generate human-readable anomaly reasons |
| [ ] Register model in ML Registry | ⬜ TODO | SubAgent | For production deployment |
| [ ] Test on injected anomalies | ⬜ TODO | SubAgent | Verify detection of 2% outliers |

### 3.3 Rule Discovery Notebook
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Build LLM semantic clustering | ⬜ TODO | SubAgent | Cluster corrections by meaning |
| [ ] Implement regulatory grounding | ⬜ TODO | SubAgent | Extract CFR/AD order citations |
| [ ] Implement generalization logic | ⬜ TODO | SubAgent | E-prefix → Chapter 85 |
| [ ] Implement contradiction detection | ⬜ TODO | SubAgent | Mexico ADD vs USMCA exempt |
| [ ] Test sparse example reasoning | ⬜ TODO | SubAgent | 3 corrections → rule suggestion |
| [ ] Generate DISCOVERED_RULES entries | ⬜ TODO | SubAgent | With LLM reasoning field |

### 3.4 Broker Scorer Notebook
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Calculate accuracy metrics by broker | ⬜ TODO | SubAgent | Part, HTS, ADD/CVD accuracy |
| [ ] Compute performance trends | ⬜ TODO | SubAgent | IMPROVING, STABLE, DECLINING |
| [ ] Assign performance tiers | ⬜ TODO | SubAgent | EXCELLENT → CRITICAL |

---

## PHASE 4: BACKEND (FastAPI + Agents)
**Status**: ⬜ NOT STARTED

### 4.1 API Layer
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Create FastAPI app structure | ⬜ TODO | SubAgent | `/api/main.py` |
| [ ] Implement health check endpoint | ⬜ TODO | SubAgent | `GET /health` |
| [ ] Implement Snowflake connection service | ⬜ TODO | SubAgent | SPCS auto-auth |
| [ ] Implement chat endpoint | ⬜ TODO | SubAgent | `POST /api/chat` |
| [ ] Implement file upload endpoint | ⬜ TODO | SubAgent | `POST /api/upload` |
| [ ] Implement validation endpoint | ⬜ TODO | SubAgent | `POST /api/validate` |

### 4.2 Orchestrator Agent
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Design orchestrator architecture | ⬜ TODO | SubAgent | Route to specialist agents |
| [ ] Implement intent classification | ⬜ TODO | SubAgent | onboarding, validation, discovery, query |
| [ ] Implement agent routing logic | ⬜ TODO | SubAgent | Dispatch to correct agent |
| [ ] Implement response aggregation | ⬜ TODO | SubAgent | Combine agent outputs |

### 4.3 Onboarding Agent
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Implement file analysis | ⬜ TODO | SubAgent | Read sample rows from any format |
| [ ] Implement schema inference call | ⬜ TODO | SubAgent | Call LLM for mapping |
| [ ] Implement mapping review workflow | ⬜ TODO | SubAgent | Human-in-the-loop approval |
| [ ] Implement broker registration | ⬜ TODO | SubAgent | Save to BROKER table |

### 4.4 Validation Agent
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Implement rule execution | ⬜ TODO | SubAgent | Run ACTIVE_RULES |
| [ ] Implement anomaly scoring | ⬜ TODO | SubAgent | Call ML model |
| [ ] Implement validation result storage | ⬜ TODO | SubAgent | Write to ENTRY_LINE |
| [ ] Implement explanation generation | ⬜ TODO | SubAgent | LLM explains failures |

### 4.5 Discovery Agent
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Implement correction pattern analysis | ⬜ TODO | SubAgent | Call rule discovery notebook |
| [ ] Implement rule suggestion generation | ⬜ TODO | SubAgent | Create DISCOVERED_RULES entries |
| [ ] Implement rule approval workflow | ⬜ TODO | SubAgent | Human review → ACTIVE_RULES |

### 4.6 Compliance Agent
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Implement Cortex Analyst integration | ⬜ TODO | SubAgent | Natural language queries |
| [ ] Implement Cortex Search integration | ⬜ TODO | SubAgent | Exception search |
| [ ] Implement report generation | ⬜ TODO | SubAgent | Export to Excel/PDF |

---

## PHASE 5: FRONTEND (React)
**Status**: ⬜ NOT STARTED

### 5.1 Project Setup
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Initialize React 18 + TypeScript project | ⬜ TODO | SubAgent | Vite or Create React App |
| [ ] Configure Tailwind CSS | ⬜ TODO | SubAgent | Styling framework |
| [ ] Set up routing (React Router) | ⬜ TODO | SubAgent | Page navigation |
| [ ] Create API client service | ⬜ TODO | SubAgent | Fetch wrapper for backend |

### 5.2 Mission Control Page (Dashboard)
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Design dashboard layout | ⬜ TODO | SubAgent | KPIs + chat + alerts |
| [ ] Implement KPI cards | ⬜ TODO | SubAgent | Pass rate, anomaly count, pending rules |
| [ ] Implement chat interface | ⬜ TODO | SubAgent | Natural language queries |
| [ ] Implement alerts panel | ⬜ TODO | SubAgent | Recent anomalies, rule suggestions |

### 5.3 Broker Onboarding Page
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Design file upload UI | ⬜ TODO | SubAgent | Drag-and-drop + progress |
| [ ] Implement schema mapping review | ⬜ TODO | SubAgent | Show AI mappings + confidence |
| [ ] Implement mapping editor | ⬜ TODO | SubAgent | Override AI suggestions |
| [ ] Implement approval workflow | ⬜ TODO | SubAgent | Approve → create broker |

### 5.4 Exception Report Page
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Design data grid | ⬜ TODO | SubAgent | Filterable, sortable table |
| [ ] Implement filters | ⬜ TODO | SubAgent | By broker, status, date range |
| [ ] Implement detail panel | ⬜ TODO | SubAgent | Line-level validation details |
| [ ] Implement export | ⬜ TODO | SubAgent | Excel/PDF download |

### 5.5 Anomaly Review Page
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Design anomaly cards | ⬜ TODO | SubAgent | Score, reason, recommended action |
| [ ] Implement accept/reject workflow | ⬜ TODO | SubAgent | User feedback loop |
| [ ] Implement bulk actions | ⬜ TODO | SubAgent | Mark multiple as false positive |

### 5.6 Rule Discovery Page
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Design rule suggestion cards | ⬜ TODO | SubAgent | Name, description, confidence, evidence |
| [ ] Implement approval workflow | ⬜ TODO | SubAgent | Approve/Reject/Modify |
| [ ] Implement rule preview | ⬜ TODO | SubAgent | Show SQL, test on sample data |
| [ ] Implement LLM reasoning display | ⬜ TODO | SubAgent | Why AI suggested this rule |

### 5.7 Broker Performance Page
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Design scorecard layout | ⬜ TODO | SubAgent | Per-broker accuracy metrics |
| [ ] Implement trend charts | ⬜ TODO | SubAgent | Accuracy over time |
| [ ] Implement comparison view | ⬜ TODO | SubAgent | Broker vs broker |

### 5.8 Architecture Page
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Create interactive system diagram | ⬜ TODO | SubAgent | Data flow visualization |

---

## PHASE 6: DEPLOYMENT (SPCS)
**Status**: ⬜ NOT STARTED

### 6.1 Container Configuration
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Create Dockerfile | ⬜ TODO | SubAgent | Multi-stage build (React + FastAPI) |
| [ ] Create nginx.conf | ⬜ TODO | SubAgent | Reverse proxy configuration |
| [ ] Create service_spec.yaml | ⬜ TODO | SubAgent | SPCS service definition |
| [ ] Build and test locally | ⬜ TODO | - | Docker Compose testing |

### 6.2 SPCS Deployment
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Create image repository | ⬜ TODO | - | Snowflake image registry |
| [ ] Push container image | ⬜ TODO | - | `docker push` to Snowflake |
| [ ] Create compute pool | ⬜ TODO | - | SPCS compute resources |
| [ ] Deploy service | ⬜ TODO | - | `CREATE SERVICE` |
| [ ] Configure ingress | ⬜ TODO | - | Public endpoint |
| [ ] Test deployed application | ⬜ TODO | - | End-to-end verification |

### 6.3 Deployment Script
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Create deploy.sh | ⬜ TODO | SubAgent | One-command deployment |
| [ ] Document deployment steps | ⬜ TODO | SubAgent | README with instructions |

---

## PHASE 7: TESTING & VALIDATION
**Status**: ⬜ NOT STARTED

### 7.1 Test Cases
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Test schema inference (KUEHNE German) | ⬜ TODO | - | Map TEILENUMMER → part_number |
| [ ] Test anomaly detection | ⬜ TODO | - | Catch injected outliers |
| [ ] Test rule discovery (semantic) | ⬜ TODO | - | 5 test cases from plan |
| [ ] Test Cortex Analyst queries | ⬜ TODO | - | Verified queries work |
| [ ] Test end-to-end onboarding flow | ⬜ TODO | - | Upload → mapping → approval |

### 7.2 Demo Preparation
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Prepare demo script | ⬜ TODO | SubAgent | 3 demo scenarios |
| [ ] Create demo data subset | ⬜ TODO | SubAgent | Curated for demo flow |
| [ ] Record demo video | ⬜ TODO | - | Backup for live demo |

---

## SUBAGENT ASSIGNMENTS

The following tasks are designated for parallel subagent execution:

### Batch 1: Synthetic Data (Can run in parallel)
- [ ] Reference data generator
- [ ] CEVA raw data generator
- [ ] EXPEDITOR raw data generator  
- [ ] KUEHNE raw data generator

### Batch 2: Cortex Services (Can run in parallel)
- [ ] Semantic model YAML
- [ ] Cortex Agent tools and prompts
- [ ] Cortex Search service definitions

### Batch 3: ML Notebooks (Can run in parallel)
- [ ] Schema inference notebook
- [ ] Anomaly detector notebook
- [ ] Rule discovery notebook
- [ ] Broker scorer notebook

### Batch 4: Backend Agents (Can run in parallel)
- [ ] Onboarding agent
- [ ] Validation agent
- [ ] Discovery agent
- [ ] Compliance agent

### Batch 5: Frontend Pages (Can run in parallel)
- [ ] Mission Control page
- [ ] Broker Onboarding page
- [ ] Exception Report page
- [ ] Anomaly Review page
- [ ] Rule Discovery page

---

## RISK REGISTER

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM schema inference accuracy | High | Fallback to human review for low-confidence mappings |
| Anomaly detection false positives | Medium | Feedback loop to retrain model |
| Rule discovery generates invalid SQL | High | Validate generated SQL before approval |
| SPCS deployment complexity | Medium | Test locally first with Docker Compose |
| Cortex Analyst query failures | Medium | Comprehensive verified queries + custom instructions |

---

## DEPENDENCIES

```
Phase 0 (Synthetic Data) ────┐
                             ▼
Phase 1 (DDL + Data Load) ───┐
                             ▼
Phase 2 (Cortex Services) ◄──┤
Phase 3 (ML Notebooks) ◄─────┤
                             ▼
Phase 4 (Backend) ◄──────────┤
                             ▼
Phase 5 (Frontend) ◄─────────┤
                             ▼
Phase 6 (Deployment)
                             ▼
Phase 7 (Testing)
```

---

## PROGRESS TRACKING

### Overall Progress
```
Phase 0: ██████████ 100% (14/14 tasks) ✅
Phase 1: ██████████ 100% (8/8 tasks) ✅
Phase 2: ██████████ 100% (11/11 tasks) ✅
Phase 3: ░░░░░░░░░░   0% (0/16 tasks)
Phase 4: ░░░░░░░░░░   0% (0/20 tasks)
Phase 5: ░░░░░░░░░░   0% (0/24 tasks)
Phase 6: ░░░░░░░░░░   0% (0/9 tasks)
Phase 7: ░░░░░░░░░░   0% (0/5 tasks)
────────────────────────────
TOTAL:   ███░░░░░░░  31% (33/106 tasks)
```

---

## CHANGE LOG

| Date | Change | Author |
|------|--------|--------|
| 2026-03-09 | Initial master plan created | Cortex Code |
| 2026-03-09 | Added LLM semantic rule discovery requirements | Cortex Code |
| 2026-03-09 | PHASE 0 COMPLETE - All synthetic data generated (278K rows total) | Cortex Code |
| 2026-03-09 | PHASE 2 COMPLETE - Cortex services defined (semantic model, 3 search services, 10 agent tools) | Cortex Code |

---

*This document is the single source of truth for project tracking. Update task status as work progresses.*
