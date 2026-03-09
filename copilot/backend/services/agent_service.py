from typing import Any, Optional
import json
from database import execute_query, get_cursor
from config import get_settings


class AgentService:
    def __init__(self):
        self.settings = get_settings()
        self._conversation_history: list[dict] = []
    
    async def infer_broker_schema(
        self, sample_file_path: str
    ) -> tuple[dict[str, str], dict[str, float]]:
        """
        Use Cortex LLM to infer schema mapping from a sample broker file.
        
        Returns inferred field mappings and confidence scores.
        """
        prompt = f"""Analyze this broker file and map columns to standard trade compliance fields.

Standard fields:
- entry_number: Customs entry number
- entry_date: Date of entry
- part_number: Product/item identifier
- hts_code: Harmonized Tariff Schedule code
- country_of_origin: Country code (COO)
- declared_value: Line item value
- quantity: Quantity of items
- unit_of_measure: UOM
- add_cvd_flag: Anti-dumping/countervailing duty indicator
- preferential_program: Trade agreement code (FTA, USMCA, etc.)

File path: {sample_file_path}

Return JSON with two objects:
1. "mappings": source_column -> standard_field
2. "confidence": standard_field -> confidence_score (0-1)

Only include fields you can confidently map."""

        sql = """
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                %(model)s,
                %(prompt)s
            ) as RESPONSE
        """
        
        try:
            with get_cursor() as cursor:
                cursor.execute(sql, {
                    "model": self.settings.cortex_model,
                    "prompt": prompt,
                })
                result = cursor.fetchone()
            
            if result and result["RESPONSE"]:
                response = result["RESPONSE"]
                if isinstance(response, str):
                    json_start = response.find("{")
                    json_end = response.rfind("}") + 1
                    if json_start >= 0:
                        response = json.loads(response[json_start:json_end])
                
                return (
                    response.get("mappings", {}),
                    response.get("confidence", {}),
                )
        except Exception:
            pass
        
        return {}, {}
    
    async def search_exceptions(
        self, query: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """
        Search exceptions using Cortex Search.
        """
        sql = f"""
            SELECT *
            FROM TABLE(
                SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                    '{self.settings.cortex_search_service}',
                    %(query)s,
                    {{
                        'columns': ['LINE_ID', 'ENTRY_NUMBER', 'PART_NUMBER', 'AUDIT_COMMENTS'],
                        'limit': {limit}
                    }}
                )
            )
        """
        
        try:
            return execute_query(sql, {"query": query})
        except Exception:
            return []
    
    async def analyze_pattern(self, pattern_description: str) -> dict[str, Any]:
        """
        Analyze a pattern in exceptions using LLM.
        """
        sql = """
            SELECT 
                PART_NUMBER, BROKER_NAME, COUNTRY_OF_ORIGIN,
                BROKER_HTS_CODE, COUNT(*) as EXCEPTION_COUNT
            FROM TRADE_COMPLIANCE.ENTRY_LINE_EXCEPTIONS
            WHERE STATUS = 'OPEN'
            GROUP BY PART_NUMBER, BROKER_NAME, COUNTRY_OF_ORIGIN, BROKER_HTS_CODE
            HAVING COUNT(*) > 1
            ORDER BY EXCEPTION_COUNT DESC
            LIMIT 20
        """
        
        patterns = execute_query(sql)
        
        prompt = f"""Analyze these exception patterns and identify the root cause:

Pattern request: {pattern_description}

Exception data:
{json.dumps(patterns, default=str, indent=2)}

Provide:
1. Root cause analysis
2. Recommended action
3. Potential rule to prevent future occurrences"""

        analysis_sql = """
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                %(model)s,
                %(prompt)s
            ) as RESPONSE
        """
        
        try:
            with get_cursor() as cursor:
                cursor.execute(analysis_sql, {
                    "model": self.settings.cortex_model,
                    "prompt": prompt,
                })
                result = cursor.fetchone()
            
            return {
                "analysis": result["RESPONSE"] if result else "Analysis unavailable",
                "patterns": patterns,
            }
        except Exception as e:
            return {"error": str(e), "patterns": patterns}
    
    async def run_agent(
        self, message: str, conversation_history: Optional[list[dict]] = None
    ):
        """
        Run the agent with a message and yield streaming responses.
        """
        if conversation_history:
            self._conversation_history = conversation_history
        
        self._conversation_history.append({"role": "user", "content": message})
        
        yield {"type": "status", "content": "Analyzing query..."}
        
        intent = self._classify_intent(message)
        yield {"type": "status", "content": f"Detected intent: {intent}"}
        
        if intent == "search":
            results = await self.search_exceptions(message)
            yield {"type": "tool_result", "content": results}
            response = f"Found {len(results)} relevant exceptions."
        
        elif intent == "pattern":
            analysis = await self.analyze_pattern(message)
            yield {"type": "tool_result", "content": analysis["patterns"]}
            response = analysis.get("analysis", "Analysis complete.")
        
        elif intent == "kpi":
            response = await self._get_kpi_response()
        
        else:
            response = await self._get_analyst_response(message)
        
        yield {"type": "text", "content": response}
        yield {"type": "done"}
        
        self._conversation_history.append({"role": "assistant", "content": response})
    
    def _classify_intent(self, message: str) -> str:
        """
        Classify the user's intent from their message.
        """
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["search", "find", "look for", "similar"]):
            return "search"
        if any(word in message_lower for word in ["pattern", "trend", "analyze", "root cause"]):
            return "pattern"
        if any(word in message_lower for word in ["kpi", "metric", "dashboard", "summary"]):
            return "kpi"
        
        return "analyst"
    
    async def _get_kpi_response(self) -> str:
        """
        Generate KPI response.
        """
        sql = """
            SELECT
                COUNT(*) as TOTAL,
                SUM(CASE WHEN STATUS = 'OPEN' THEN 1 ELSE 0 END) as OPEN_COUNT
            FROM TRADE_COMPLIANCE.ENTRY_LINE_EXCEPTIONS
        """
        
        result = execute_query(sql)
        if result:
            r = result[0]
            return f"Current KPIs: {r['TOTAL']} total exceptions, {r['OPEN_COUNT']} open."
        return "Unable to retrieve KPIs."
    
    async def _get_analyst_response(self, query: str) -> str:
        """
        Get response from Cortex Analyst.
        """
        try:
            with get_cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE(
                        'analyst', 
                        OBJECT_CONSTRUCT(
                            'semantic_model', '{self.settings.semantic_model_path}',
                            'query', %(query)s
                        )
                    ) as RESPONSE
                    """,
                    {"query": query}
                )
                result = cursor.fetchone()
            
            if result:
                response = result["RESPONSE"]
                if isinstance(response, str):
                    response = json.loads(response)
                return response.get("answer", response.get("text", str(response)))
        except Exception as e:
            return f"Error querying analyst: {str(e)}"
        
        return "Unable to process query."
