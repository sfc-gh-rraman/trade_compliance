# Trade Compliance Platform
## AI-Powered Cummins Entry Visibility

An AI-powered trade compliance platform that leverages Snowflake Cortex for intelligent broker onboarding, validation rule discovery, and anomaly detection.

![Status](https://img.shields.io/badge/status-development-yellow)
![Snowflake](https://img.shields.io/badge/Snowflake-Cortex-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Overview

This platform transforms trade compliance from a rule-execution system to an **AI-assisted discovery system**:

1. **Schema Inference**: AI automatically maps new broker file formats to standard schema
2. **Rule Discovery**: LLM analyzes historical corrections to suggest new validation rules
3. **Anomaly Detection**: ML models flag unusual entries even without explicit rules

### Three AI Pillars

| Pillar | Problem | AI Solution |
|--------|---------|-------------|
| **Schema Inference** | New brokers have different field names (even German!) | LLM maps to standard schema |
| **Rule Discovery** | Unknown rules exist in analyst corrections | LLM clusters corrections by meaning |
| **Anomaly Detection** | Not all issues have explicit rules | ML flags statistical outliers |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     REACT FRONTEND                               │
│  Dashboard │ Exceptions │ Rules │ Brokers │ Chat                │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                              │
│  /api/exceptions │ /api/rules │ /api/brokers │ /api/analyst     │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                   SNOWFLAKE CORTEX                               │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐     │
│  │  ANALYST  │  │  SEARCH   │  │   AGENT   │  │   LLM    │     │
│  │ Semantic  │  │ Exception │  │   Tools   │  │ Complete │     │
│  │  Model    │  │ + Rules   │  │           │  │          │     │
│  └───────────┘  └───────────┘  └───────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     SNOWFLAKE DATA                               │
│  ATOMIC          │  ML              │  RULES                     │
│  ├─ BROKER       │  ├─ DISCOVERED   │  ├─ ACTIVE_RULES          │
│  ├─ ENTRY_LINE   │  │   _RULES      │  └─ EXECUTION_LOG         │
│  ├─ GTM_PART     │  ├─ ANOMALY      │                           │
│  └─ CORRECTION   │  │   _DETECTIONS │                           │
│                  │  └─ SEMANTIC     │                           │
│                  │      _CLUSTERS   │                           │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
trade_compliance/
├── copilot/
│   ├── backend/           # FastAPI application
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── routers/       # API endpoints
│   │   └── services/      # Agent orchestration
│   └── frontend/          # React application
│       ├── src/pages/     # Dashboard, Exceptions, Rules, etc.
│       └── src/components/
├── cortex/                # Cortex AI configurations
│   ├── trade_compliance_semantic_model.yaml
│   ├── deploy_cortex_search.sql
│   └── agent_tools.py
├── ddl/                   # Snowflake DDL
│   ├── 001_database.sql
│   ├── 002_atomic_tables.sql
│   ├── 003_ml_tables.sql
│   ├── 004_datamart_views.sql
│   ├── 005_rule_engine.sql
│   └── 006_spcs_deployment.sql
├── notebooks/             # ML notebooks
│   ├── 01_schema_inference.ipynb
│   ├── 02_anomaly_detection.ipynb
│   └── 03_rule_discovery.ipynb
├── data/synthetic/        # Test data (278K rows)
├── scripts/               # Deployment scripts
└── docs/                  # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Snowflake account with Cortex access
- Docker (for local development)
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### 1. Deploy Snowflake Objects

```bash
# Set connection
export SNOWFLAKE_CONNECTION=my_snowflake

# Deploy DDL
snow sql -f ddl/001_database.sql -c $SNOWFLAKE_CONNECTION
snow sql -f ddl/002_atomic_tables.sql -c $SNOWFLAKE_CONNECTION
snow sql -f ddl/003_ml_tables.sql -c $SNOWFLAKE_CONNECTION
snow sql -f ddl/004_datamart_views.sql -c $SNOWFLAKE_CONNECTION
snow sql -f ddl/005_rule_engine.sql -c $SNOWFLAKE_CONNECTION
```

### 2. Upload Semantic Model

```bash
snow sql -c $SNOWFLAKE_CONNECTION -q "
PUT file://cortex/trade_compliance_semantic_model.yaml 
@TRADE_COMPLIANCE_DB.TRADE_COMPLIANCE.SEMANTIC_MODELS 
AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
"
```

### 3. Local Development

```bash
# Start with Docker Compose
docker-compose up --build

# Or run separately:
# Backend
cd copilot/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd copilot/frontend
npm install
npm run dev
```

### 4. SPCS Deployment

```bash
# Deploy to Snowpark Container Services
./scripts/deploy_spcs.sh
```

## 🔑 Key Features

### Broker Onboarding (AI Schema Inference)
- Upload any broker file (CSV, XML, XLSB)
- AI maps columns to standard schema
- Human reviews and approves mappings
- Handles multilingual field names

### Validation Engine
- 6 baseline rules (part validation, HTS match, ADD/CVD)
- Dynamic rule execution via stored procedure
- AI-discovered rules can be approved and activated

### Rule Discovery (LLM Semantic Reasoning)
- Analyzes CORRECTION_REASON free text
- Clusters corrections by semantic meaning
- Suggests validation rules with regulatory basis
- Handles contradictions and sparse examples

### Anomaly Detection
- Isolation Forest trained on historical data
- Flags statistical outliers (2% contamination)
- LLM generates human-readable explanations

## 📊 Data Summary

| Table | Rows | Purpose |
|-------|------|---------|
| BROKER | 3 | CEVA, EXPEDITOR, KUEHNE |
| GTM_PART_MASTER | 5,000 | Reference parts |
| ENTRY_LINE | 90,000 | Trade entries |
| VALIDATION_CORRECTION | 2,500 | Historical corrections |
| DISCOVERED_RULES | Dynamic | AI-suggested rules |
| ANOMALY_DETECTIONS | Dynamic | ML-flagged anomalies |

## 🔐 Security

- SPCS OAuth integration for authentication
- Token-based refresh for long-running sessions
- No secrets in code (environment variables only)

## 📚 Documentation

- [Master Plan](docs/MASTER_PLAN.md) - Complete project tracking
- [Implementation Plan](docs/implementation_plan.md) - Technical approach
- [Synthetic Data Plan](docs/synthetic_data_plan.md) - Test data design

## 🤝 Contributing

This project follows the ATLAS Capital Delivery reference architecture pattern.

## 📄 License

MIT License - See LICENSE file for details.

---

Built with ❄️ Snowflake Cortex | 🤖 AI-Powered | 🚀 SPCS Deployed
