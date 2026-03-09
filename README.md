# Trade Compliance - Cummins Entry Visibility

AI-First Trade Compliance Platform for Cummins Supply Chain

## Overview

This platform uses AI to solve the **scaling problem** of broker onboarding and validation rule discovery:

1. **AI-Powered Onboarding** - Auto-map new broker schemas (any format, any language)
2. **AI-Powered Validation** - Known rules (SQL) + Unknown patterns (ML anomaly detection)
3. **AI-Powered Rule Discovery** - Learn from corrections using LLM semantic reasoning

## Architecture

- **Frontend**: React 18 + TypeScript + Tailwind
- **Backend**: FastAPI + Python multi-agent system
- **AI Layer**: Snowflake Cortex (Analyst, Search, Agent, LLM)
- **Data Layer**: Snowflake (RAW → ATOMIC → ML → RULES schemas)
- **Deployment**: SPCS (Snowpark Container Services)

## Project Structure

```
trade_compliance/
├── copilot/
│   ├── frontend/          # React application
│   └── backend/           # FastAPI + Agents
├── cortex/                # Semantic model, search, agent configs
├── ddl/                   # Database DDL scripts
├── notebooks/             # ML notebooks (schema inference, anomaly, rule discovery)
├── data/synthetic/        # Synthetic test data
├── docs/                  # Documentation
│   ├── MASTER_PLAN.md     # Project tracking
│   ├── entry_visibility_requirements.md
│   ├── implementation_plan.md
│   └── synthetic_data_plan.md
└── deploy.sh              # One-command deployment
```

## The "Wow" Moment

> A new EU broker was onboarded in **2 hours** instead of 2 weeks.
> The AI mapped 47 fields automatically - including German field names.
> It then discovered 3 new EU-specific validation rules that saved $340K.

## Getting Started

See [docs/MASTER_PLAN.md](docs/MASTER_PLAN.md) for implementation progress.

## Built With

- [Snowflake](https://www.snowflake.com/) - Data Cloud
- [Snowflake Cortex](https://www.snowflake.com/en/data-cloud/cortex/) - AI/ML Services
- [SPCS](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/overview) - Container Services
