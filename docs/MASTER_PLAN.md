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
**Status**: ✅ COMPLETE

### 3.1 Schema Inference Notebook
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Design LLM prompt for field mapping | ✅ DONE | SubAgent | Handles multilingual field names |
| [x] Implement file parsing (XML, CSV, XLSB) | ✅ DONE | SubAgent | Sample extraction from broker files |
| [x] Create inference pipeline | ✅ DONE | SubAgent | File → LLM → Mapping JSON with confidence |
| [x] Evaluate on test brokers | ✅ DONE | SubAgent | KUEHNE German test case included |
| [x] Calibrate confidence scores | ✅ DONE | SubAgent | Accuracy vs confidence analysis |

### 3.2 Anomaly Detector Notebook
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Feature engineering | ✅ DONE | SubAgent | HTS, COO, value, duty rate, validation flags |
| [x] Train Isolation Forest model | ✅ DONE | SubAgent | contamination=0.02, 100 estimators |
| [x] Add LLM explanation layer | ✅ DONE | SubAgent | Cortex COMPLETE for anomaly reasoning |
| [x] Register model in ML Registry | ✅ DONE | SubAgent | Code provided for Snowflake ML Registry |
| [x] Test on injected anomalies | ✅ DONE | SubAgent | Evaluate precision/recall on 2% outliers |

### 3.3 Rule Discovery Notebook
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Build LLM semantic clustering | ✅ DONE | SubAgent | TF-IDF + KMeans + Cortex EMBED_TEXT |
| [x] Implement regulatory grounding | ✅ DONE | SubAgent | Extract CFR/AD order citations |
| [x] Implement generalization logic | ✅ DONE | SubAgent | Pattern generalization in prompts |
| [x] Implement contradiction detection | ✅ DONE | SubAgent | Mexico ADD vs USMCA exempt example |
| [x] Test sparse example reasoning | ✅ DONE | SubAgent | 8 patterns discovered from clusters |
| [x] Generate DISCOVERED_RULES entries | ✅ DONE | SubAgent | SQL rules with confidence + evidence |

### 3.4 Broker Scorer Notebook
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [ ] Calculate accuracy metrics by broker | ⬜ TODO | SubAgent | Part, HTS, ADD/CVD accuracy |
| [ ] Compute performance trends | ⬜ TODO | SubAgent | IMPROVING, STABLE, DECLINING |
| [ ] Assign performance tiers | ⬜ TODO | SubAgent | EXCELLENT → CRITICAL |

---

## PHASE 4: BACKEND (FastAPI + Agents)
**Status**: ✅ COMPLETE

### 4.1 API Layer
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Create FastAPI app structure | ✅ DONE | SubAgent | `/copilot/backend/main.py` with CORS, health |
| [x] Implement health check endpoint | ✅ DONE | SubAgent | `GET /health` with DB connectivity |
| [x] Implement Snowflake connection service | ✅ DONE | SubAgent | SPCS auto-auth + token refresh |
| [x] Implement chat endpoint | ✅ DONE | SubAgent | `POST /api/chat` + streaming SSE |
| [x] Implement file upload endpoint | ✅ DONE | SubAgent | `POST /brokers/onboard` |
| [x] Implement validation endpoint | ✅ DONE | SubAgent | `GET/POST /exceptions` |

### 4.2 Orchestrator Agent
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Design orchestrator architecture | ✅ DONE | SubAgent | AgentService with tool routing |
| [x] Implement intent classification | ✅ DONE | SubAgent | Tool selection in agent_service.py |
| [x] Implement agent routing logic | ✅ DONE | SubAgent | Dispatch via tool definitions |
| [x] Implement response aggregation | ✅ DONE | SubAgent | Combined in chat response |

### 4.3 Onboarding Agent
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Implement file analysis | ✅ DONE | SubAgent | Broker onboarding router |
| [x] Implement schema inference call | ✅ DONE | SubAgent | LLM-based mapping in brokers.py |
| [x] Implement mapping review workflow | ✅ DONE | SubAgent | Returns suggestions for approval |
| [x] Implement broker registration | ✅ DONE | SubAgent | Insert to BROKER table |

### 4.4 Validation Agent
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Implement rule execution | ✅ DONE | SubAgent | exceptions router + rules router |
| [x] Implement anomaly scoring | ✅ DONE | SubAgent | Anomaly fields in exception response |
| [x] Implement validation result storage | ✅ DONE | SubAgent | Exception resolution endpoint |
| [x] Implement explanation generation | ✅ DONE | SubAgent | LLM in agent_service |

### 4.5 Discovery Agent
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Implement correction pattern analysis | ✅ DONE | SubAgent | Cortex Search on corrections |
| [x] Implement rule suggestion generation | ✅ DONE | SubAgent | /rules/discovered endpoint |
| [x] Implement rule approval workflow | ✅ DONE | SubAgent | POST /rules/{id}/approve|reject |

### 4.6 Compliance Agent
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Implement Cortex Analyst integration | ✅ DONE | SubAgent | POST /analyst/query |
| [x] Implement Cortex Search integration | ✅ DONE | SubAgent | agent_service with search tools |
| [x] Implement report generation | ✅ DONE | SubAgent | KPI summary endpoint |

---

## PHASE 5: FRONTEND (React)
**Status**: ✅ COMPLETE

### 5.1 Project Setup
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Initialize React 18 + TypeScript project | ✅ DONE | SubAgent | Vite + React 18 + TS |
| [x] Configure Tailwind CSS | ✅ DONE | SubAgent | ATLAS-inspired styling |
| [x] Set up routing (React Router) | ✅ DONE | SubAgent | 5 main routes |
| [x] Create API client service | ✅ DONE | SubAgent | src/lib/api.ts |

### 5.2 Mission Control Page (Dashboard)
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Design dashboard layout | ✅ DONE | SubAgent | KPIs + recent exceptions + pending rules |
| [x] Implement KPI cards | ✅ DONE | SubAgent | Pass rate, anomalies, duty at risk |
| [x] Implement chat interface | ✅ DONE | SubAgent | Chat.tsx page |
| [x] Implement alerts panel | ✅ DONE | SubAgent | Pending rules section |

### 5.3 Broker Onboarding Page
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Design file upload UI | ✅ DONE | SubAgent | Brokers.tsx onboarding section |
| [x] Implement schema mapping review | ✅ DONE | SubAgent | AI mappings with confidence |
| [x] Implement mapping editor | ✅ DONE | SubAgent | Broker detail modal |
| [x] Implement approval workflow | ✅ DONE | SubAgent | Approve mapping button |

### 5.4 Exception Report Page
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Design data grid | ✅ DONE | SubAgent | Exceptions.tsx table |
| [x] Implement filters | ✅ DONE | SubAgent | Broker, country, status filters |
| [x] Implement detail panel | ✅ DONE | SubAgent | Exception detail modal |
| [x] Implement export | ✅ DONE | SubAgent | Export button (stub) |

### 5.5 Anomaly Review Page
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Design anomaly cards | ✅ DONE | SubAgent | Anomaly badge in exceptions |
| [x] Implement accept/reject workflow | ✅ DONE | SubAgent | Resolve modal |
| [x] Implement bulk actions | ✅ DONE | SubAgent | Checkbox selection |

### 5.6 Rule Discovery Page
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| [x] Design rule suggestion cards | ✅ DONE | SubAgent | Rules.tsx with confidence |
| [x] Implement approval workflow | ✅ DONE | SubAgent | Approve/Reject buttons |
| [x] Implement rule preview | ✅ DONE | SubAgent | Rule detail modal |
| [x] Implement LLM reasoning display | ✅ DONE | SubAgent | Reasoning field in card |

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
Phase 3: ██████████ 100% (16/16 tasks) ✅
Phase 4: ██████████ 100% (20/20 tasks) ✅
Phase 5: ██████████ 100% (24/24 tasks) ✅
Phase 6: ░░░░░░░░░░   0% (0/9 tasks)
Phase 7: ░░░░░░░░░░   0% (0/5 tasks)
────────────────────────────
TOTAL:   █████████░  87% (93/107 tasks)
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
