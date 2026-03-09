from fastapi import APIRouter, HTTPException
from models.schemas import AnalystQueryRequest, AnalystQueryResponse
from database import execute_query, get_cursor
from config import get_settings
import json

router = APIRouter(prefix="/analyst", tags=["analyst"])


@router.post("/query", response_model=AnalystQueryResponse)
async def query_analyst(request: AnalystQueryRequest):
    """
    Send a natural language query to Cortex Analyst.
    
    Uses the semantic model to convert natural language to SQL and execute.
    Returns the answer, optionally with SQL and raw results.
    """
    settings = get_settings()
    
    analyst_sql = """
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'analyst',
            %(semantic_model)s,
            %(query)s
        ) as RESPONSE
    """
    
    try:
        with get_cursor() as cursor:
            cursor.execute(
                f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'analyst', 
                    OBJECT_CONSTRUCT(
                        'semantic_model', '{settings.semantic_model_path}',
                        'query', %(query)s
                    )
                ) as RESPONSE
                """,
                {"query": request.query}
            )
            result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=500, detail="No response from Cortex Analyst")
        
        response_data = result["RESPONSE"]
        if isinstance(response_data, str):
            response_data = json.loads(response_data)
        
        answer = response_data.get("answer", response_data.get("text", ""))
        sql = response_data.get("sql")
        
        results = None
        if request.include_sql and sql:
            try:
                results = execute_query(sql)
                if len(results) > 100:
                    results = results[:100]
            except Exception:
                pass
        
        visualization = response_data.get("visualization")
        
        return AnalystQueryResponse(
            answer=answer,
            sql=sql if request.include_sql else None,
            results=results,
            visualization=visualization,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/stream")
async def query_analyst_stream(request: AnalystQueryRequest):
    """
    Stream a natural language query response from Cortex Analyst.
    
    Returns Server-Sent Events for streaming responses.
    """
    from fastapi.responses import StreamingResponse
    from config import get_settings
    
    settings = get_settings()
    
    async def event_generator():
        try:
            yield f"data: {json.dumps({'type': 'status', 'content': 'Processing query...'})}\n\n"
            
            with get_cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE(
                        'analyst', 
                        OBJECT_CONSTRUCT(
                            'semantic_model', '{settings.semantic_model_path}',
                            'query', %(query)s
                        )
                    ) as RESPONSE
                    """,
                    {"query": request.query}
                )
                result = cursor.fetchone()
            
            if result:
                response_data = result["RESPONSE"]
                if isinstance(response_data, str):
                    response_data = json.loads(response_data)
                
                answer = response_data.get("answer", response_data.get("text", ""))
                yield f"data: {json.dumps({'type': 'text', 'content': answer})}\n\n"
                
                sql = response_data.get("sql")
                if sql and request.include_sql:
                    yield f"data: {json.dumps({'type': 'sql', 'content': sql})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
