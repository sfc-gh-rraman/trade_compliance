from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from models.schemas import (
    BrokerListResponse,
    BrokerSummary,
    BrokerDetail,
    OnboardingRequest,
    OnboardingResponse,
)
from database import execute_query, execute_query_single
from services.agent_service import AgentService
import uuid

router = APIRouter(prefix="/brokers", tags=["brokers"])


@router.get("", response_model=BrokerListResponse)
async def list_brokers(
    region: Optional[str] = Query(None, description="Filter by region"),
    status: Optional[str] = Query(None, description="Filter by status"),
):
    """
    List all brokers with scorecard metrics.
    
    Returns broker performance data including exception rates and quality scores.
    """
    where_clauses = ["1=1"]
    if region:
        where_clauses.append(f"REGION = '{region}'")
    if status:
        where_clauses.append(f"STATUS = '{status}'")
    
    where_sql = " AND ".join(where_clauses)
    
    sql = f"""
        SELECT 
            b.BROKER_ID,
            b.BROKER_NAME,
            b.REGION,
            b.STATUS,
            COUNT(e.LINE_ID) as TOTAL_ENTRIES,
            COALESCE(SUM(CASE WHEN e.STATUS = 'OPEN' THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(e.LINE_ID), 0), 0) as EXCEPTION_RATE,
            COALESCE(AVG(TIMESTAMPDIFF('HOUR', e.CREATED_AT, COALESCE(e.RESOLVED_AT, CURRENT_TIMESTAMP()))), 0) as AVG_PROCESSING_TIME_HOURS,
            COALESCE(b.QUALITY_SCORE, 0) as QUALITY_SCORE
        FROM ATOMIC.BROKER b
        LEFT JOIN TRADE_COMPLIANCE.ENTRY_LINE e ON b.BROKER_ID = e.BROKER_ID
        WHERE {where_sql}
        GROUP BY b.BROKER_ID, b.BROKER_NAME, b.REGION, b.STATUS, b.QUALITY_SCORE
        ORDER BY b.BROKER_NAME
    """
    
    try:
        rows = execute_query(sql)
        brokers = [
            BrokerSummary(
                broker_id=row["BROKER_ID"],
                broker_name=row["BROKER_NAME"],
                region=row["REGION"],
                total_entries=int(row["TOTAL_ENTRIES"]),
                exception_rate=float(row["EXCEPTION_RATE"]),
                avg_processing_time_hours=float(row["AVG_PROCESSING_TIME_HOURS"]),
                quality_score=float(row["QUALITY_SCORE"]),
                status=row["STATUS"],
            )
            for row in rows
        ]
        
        return BrokerListResponse(brokers=brokers, total=len(brokers))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{broker_id}", response_model=BrokerDetail)
async def get_broker(broker_id: str):
    """
    Get detailed broker information and performance metrics.
    
    Includes schema mapping, validation failure rates by type, and quality score.
    """
    sql = """
        SELECT 
            b.BROKER_ID,
            b.BROKER_NAME,
            b.REGION,
            b.CONTACT_EMAIL,
            b.SCHEMA_MAPPING,
            b.ONBOARDING_DATE,
            b.STATUS,
            b.QUALITY_SCORE,
            COUNT(e.LINE_ID) as TOTAL_ENTRIES,
            SUM(CASE WHEN e.STATUS IN ('OPEN', 'ESCALATED') THEN 1 ELSE 0 END) as TOTAL_EXCEPTIONS,
            COALESCE(SUM(CASE WHEN e.PART_VALIDATION = 'FAIL' THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(e.LINE_ID), 0), 0) as PART_FAIL_RATE,
            COALESCE(SUM(CASE WHEN e.HTS_VALIDATION = 'FAIL' THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(e.LINE_ID), 0), 0) as HTS_FAIL_RATE,
            COALESCE(SUM(CASE WHEN e.ADD_CVD_VALIDATION = 'FAIL' THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(e.LINE_ID), 0), 0) as ADD_CVD_FAIL_RATE,
            COALESCE(AVG(TIMESTAMPDIFF('HOUR', e.CREATED_AT, COALESCE(e.RESOLVED_AT, CURRENT_TIMESTAMP()))), 0) as AVG_PROCESSING_TIME_HOURS
        FROM ATOMIC.BROKER b
        LEFT JOIN TRADE_COMPLIANCE.ENTRY_LINE e ON b.BROKER_ID = e.BROKER_ID
        WHERE b.BROKER_ID = %(broker_id)s
        GROUP BY b.BROKER_ID, b.BROKER_NAME, b.REGION, b.CONTACT_EMAIL, 
                 b.SCHEMA_MAPPING, b.ONBOARDING_DATE, b.STATUS, b.QUALITY_SCORE
    """
    
    try:
        row = execute_query_single(sql, {"broker_id": broker_id})
        if not row:
            raise HTTPException(status_code=404, detail=f"Broker {broker_id} not found")
        
        schema_mapping = None
        if row["SCHEMA_MAPPING"]:
            import json
            schema_mapping = json.loads(row["SCHEMA_MAPPING"]) if isinstance(row["SCHEMA_MAPPING"], str) else row["SCHEMA_MAPPING"]
        
        total_entries = int(row["TOTAL_ENTRIES"])
        total_exceptions = int(row["TOTAL_EXCEPTIONS"])
        exception_rate = total_exceptions / total_entries if total_entries > 0 else 0
        
        return BrokerDetail(
            broker_id=row["BROKER_ID"],
            broker_name=row["BROKER_NAME"],
            region=row["REGION"],
            contact_email=row["CONTACT_EMAIL"],
            schema_mapping=schema_mapping,
            total_entries=total_entries,
            total_exceptions=total_exceptions,
            exception_rate=exception_rate,
            part_fail_rate=float(row["PART_FAIL_RATE"]),
            hts_fail_rate=float(row["HTS_FAIL_RATE"]),
            add_cvd_fail_rate=float(row["ADD_CVD_FAIL_RATE"]),
            avg_processing_time_hours=float(row["AVG_PROCESSING_TIME_HOURS"]),
            quality_score=float(row["QUALITY_SCORE"]) if row["QUALITY_SCORE"] else 0,
            onboarding_date=row["ONBOARDING_DATE"],
            status=row["STATUS"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/onboard", response_model=OnboardingResponse)
async def onboard_broker(request: OnboardingRequest):
    """
    Start AI-powered broker onboarding process.
    
    Uses Cortex LLM to infer schema mapping from sample file.
    Returns inferred schema with confidence scores for human review.
    """
    try:
        agent = AgentService()
        inferred_schema, confidence_scores = await agent.infer_broker_schema(
            request.sample_file_path
        )
        
        broker_id = f"BRK-{uuid.uuid4().hex[:8].upper()}"
        
        insert_sql = """
            INSERT INTO ATOMIC.BROKER (
                BROKER_ID, BROKER_NAME, REGION, CONTACT_EMAIL,
                SCHEMA_MAPPING, STATUS, ONBOARDING_DATE
            ) VALUES (
                %(broker_id)s, %(broker_name)s, %(region)s, %(contact_email)s,
                PARSE_JSON(%(schema_mapping)s), 'PENDING', CURRENT_TIMESTAMP()
            )
        """
        
        import json
        execute_query(insert_sql, {
            "broker_id": broker_id,
            "broker_name": request.broker_name,
            "region": request.region,
            "contact_email": request.contact_email,
            "schema_mapping": json.dumps(inferred_schema),
        })
        
        return OnboardingResponse(
            broker_id=broker_id,
            status="PENDING",
            inferred_schema=inferred_schema,
            confidence_scores=confidence_scores,
            message=f"Broker {request.broker_name} created. Review inferred schema and approve.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
