"""
Trade Compliance Cortex Agent Tool Definitions
These tools enable the AI agent to interact with the trade compliance system.
"""

# ============================================================================
# AGENT TOOL SPECIFICATIONS (for Cortex Agent)
# ============================================================================

TRADE_COMPLIANCE_TOOLS = [
    {
        "name": "validate_entry",
        "description": "Validate a single entry line against all active rules. Returns validation status for part number, HTS code, and ADD/CVD compliance.",
        "parameters": {
            "type": "object",
            "properties": {
                "entry_number": {
                    "type": "string",
                    "description": "The customs entry number to validate"
                },
                "line_number": {
                    "type": "integer",
                    "description": "The line number within the entry"
                },
                "part_number": {
                    "type": "string",
                    "description": "The part/product number to validate"
                },
                "hts_code": {
                    "type": "string",
                    "description": "The HTS tariff code to validate"
                },
                "country_of_origin": {
                    "type": "string",
                    "description": "2-letter ISO country code (e.g., CN, MX, US)"
                },
                "entered_value": {
                    "type": "number",
                    "description": "The declared customs value in USD"
                }
            },
            "required": ["part_number", "hts_code", "country_of_origin"]
        }
    },
    {
        "name": "search_exceptions",
        "description": "Search for validation exceptions and anomalies using natural language. Uses Cortex Search on exception data.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query (e.g., 'ADD issues from China', 'HTS mismatches for electrical parts')"
                },
                "broker_name": {
                    "type": "string",
                    "description": "Optional: Filter by broker name"
                },
                "country": {
                    "type": "string",
                    "description": "Optional: Filter by country of origin"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 10)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_rules",
        "description": "Search for validation rules (both active and AI-discovered). Helps understand why entries fail validation.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search (e.g., 'rules about China ADD', 'HTS validation rules')"
                },
                "status": {
                    "type": "string",
                    "enum": ["ACTIVE", "SUGGESTED", "UNDER_REVIEW", "ALL"],
                    "description": "Filter by rule status"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 10)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "suggest_rule",
        "description": "Ask the AI to suggest a new validation rule based on a pattern in corrections. Uses LLM semantic reasoning.",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern_description": {
                    "type": "string",
                    "description": "Describe the pattern you've noticed (e.g., 'Parts starting with E from China always need ADD')"
                },
                "supporting_examples": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of example part numbers or correction IDs that support this pattern"
                }
            },
            "required": ["pattern_description"]
        }
    },
    {
        "name": "explain_anomaly",
        "description": "Get AI explanation for why a specific entry was flagged as anomalous.",
        "parameters": {
            "type": "object",
            "properties": {
                "line_id": {
                    "type": "string",
                    "description": "The LINE_ID of the anomalous entry"
                },
                "detail_level": {
                    "type": "string",
                    "enum": ["brief", "detailed", "technical"],
                    "description": "How much detail to include in explanation"
                }
            },
            "required": ["line_id"]
        }
    },
    {
        "name": "get_broker_scorecard",
        "description": "Get performance metrics for a specific broker or all brokers.",
        "parameters": {
            "type": "object",
            "properties": {
                "broker_name": {
                    "type": "string",
                    "description": "Broker name (leave empty for all brokers)"
                },
                "date_range": {
                    "type": "string",
                    "enum": ["7d", "30d", "90d", "ytd", "all"],
                    "description": "Time period for metrics"
                }
            }
        }
    },
    {
        "name": "approve_discovered_rule",
        "description": "Approve or reject an AI-discovered rule for production use.",
        "parameters": {
            "type": "object",
            "properties": {
                "rule_id": {
                    "type": "string",
                    "description": "The RULE_ID from DISCOVERED_RULES"
                },
                "decision": {
                    "type": "string",
                    "enum": ["APPROVE", "REJECT"],
                    "description": "Whether to approve or reject the rule"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for approval/rejection"
                }
            },
            "required": ["rule_id", "decision"]
        }
    },
    {
        "name": "search_corrections",
        "description": "Search historical analyst corrections for patterns. Used for rule discovery.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search (e.g., 'corrections for Chinese electrical parts', 'ADD-related fixes')"
                },
                "field_corrected": {
                    "type": "string",
                    "description": "Optional: Filter by field that was corrected (HTS_CODE, ADD_FLAG, CVD_FLAG, COO)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results (default: 20)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "map_broker_schema",
        "description": "Trigger AI schema inference for a new broker file. Returns field mapping suggestions.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Stage path to the broker file (e.g., @RAW.BROKER_FILES/kuehne_sample.csv)"
                },
                "broker_name": {
                    "type": "string",
                    "description": "Name to assign to this broker"
                }
            },
            "required": ["file_path", "broker_name"]
        }
    },
    {
        "name": "get_kpi_summary",
        "description": "Get current KPIs for the trade compliance dashboard.",
        "parameters": {
            "type": "object",
            "properties": {
                "date_range": {
                    "type": "string",
                    "enum": ["today", "7d", "30d", "90d"],
                    "description": "Time period for KPIs"
                }
            }
        }
    }
]

# ============================================================================
# AGENT PROMPT TEMPLATE
# ============================================================================

AGENT_SYSTEM_PROMPT = """
You are the Trade Compliance AI Assistant for Cummins Entry Visibility.

Your role is to help trade compliance analysts:
1. INVESTIGATE exceptions and anomalies in customs entries
2. DISCOVER patterns in historical corrections that could become new rules
3. VALIDATE entries against known rules and AI-detected patterns
4. ONBOARD new brokers by mapping their file schemas

KEY DOMAIN KNOWLEDGE:
- HTS (Harmonized Tariff Schedule): 10-digit codes classifying imported goods
- ADD (Anti-Dumping Duties): Extra tariffs on goods sold below fair market value
- CVD (Countervailing Duties): Tariffs offsetting foreign government subsidies
- COO (Country of Origin): Determines which duties apply
- GTM (Global Trade Management): Our reference system for correct classifications

VALIDATION RULES:
- Part Number: Must exist in GTM US parts list
- HTS Code: Must match GTM for non-US origin (US origin auto-passes)
- ADD/CVD: Case numbers must match when declared

AI CAPABILITIES:
- Schema Inference: Automatically map new broker file formats
- Rule Discovery: Suggest new rules from correction patterns
- Anomaly Detection: Flag unusual entries even without explicit rules

When users ask about:
- "Why did this fail?" → Check validation messages and search rules
- "What patterns do you see?" → Search corrections and suggest rules
- "Is this normal?" → Check for anomalies and explain if flagged
- "Which broker is worst?" → Use broker scorecard

Always be specific about dollar amounts at risk and confidence levels.
"""
