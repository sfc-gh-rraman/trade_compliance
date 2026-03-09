from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from models.schemas import KPISummary, KPITrends, TrendPoint
from database import execute_query, execute_query_single

router = APIRouter(prefix="/kpi", tags=["kpi"])


@router.get("/summary", response_model=KPISummary)
async def get_kpi_summary():
    """
    Get dashboard KPI summary.
    
    Returns key metrics: total entries, exceptions, rates, and AI stats.
    """
    sql = """
        SELECT
            COUNT(*) as TOTAL_ENTRIES,
            SUM(CASE WHEN STATUS IN ('OPEN', 'ESCALATED') THEN 1 ELSE 0 END) as TOTAL_EXCEPTIONS,
            SUM(CASE WHEN STATUS = 'RESOLVED' THEN 1 ELSE 0 END) as RESOLVED_COUNT,
            AVG(CASE WHEN RESOLVED_AT IS NOT NULL 
                THEN TIMESTAMPDIFF('HOUR', CREATED_AT, RESOLVED_AT) 
                ELSE NULL END) as AVG_RESOLUTION_TIME
        FROM TRADE_COMPLIANCE.ENTRY_LINE_EXCEPTIONS
    """
    
    broker_sql = """
        SELECT COUNT(DISTINCT BROKER_ID) as ACTIVE_BROKERS
        FROM ATOMIC.BROKER
        WHERE STATUS = 'ACTIVE'
    """
    
    rules_sql = """
        SELECT COUNT(*) as DISCOVERED_RULES
        FROM RULES.DISCOVERED_RULES
        WHERE STATUS = 'PENDING'
    """
    
    anomaly_sql = """
        SELECT COUNT(*) as ANOMALY_COUNT
        FROM ML.ANOMALY_DETECTIONS
        WHERE DETECTION_DATE >= DATEADD('DAY', -30, CURRENT_DATE())
    """
    
    try:
        main_result = execute_query_single(sql)
        broker_result = execute_query_single(broker_sql)
        rules_result = execute_query_single(rules_sql)
        anomaly_result = execute_query_single(anomaly_sql)
        
        total_entries = int(main_result["TOTAL_ENTRIES"]) if main_result else 0
        total_exceptions = int(main_result["TOTAL_EXCEPTIONS"]) if main_result else 0
        resolved_count = int(main_result["RESOLVED_COUNT"]) if main_result else 0
        avg_resolution = float(main_result["AVG_RESOLUTION_TIME"]) if main_result and main_result["AVG_RESOLUTION_TIME"] else 0
        
        exception_rate = total_exceptions / total_entries if total_entries > 0 else 0
        resolution_rate = resolved_count / (total_exceptions + resolved_count) if (total_exceptions + resolved_count) > 0 else 0
        
        return KPISummary(
            total_entries=total_entries,
            total_exceptions=total_exceptions,
            exception_rate=exception_rate,
            resolution_rate=resolution_rate,
            avg_resolution_time_hours=avg_resolution,
            active_brokers=int(broker_result["ACTIVE_BROKERS"]) if broker_result else 0,
            discovered_rules=int(rules_result["DISCOVERED_RULES"]) if rules_result else 0,
            ai_detected_anomalies=int(anomaly_result["ANOMALY_COUNT"]) if anomaly_result else 0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends", response_model=KPITrends)
async def get_kpi_trends(
    period: str = Query("30d", description="Trend period: 7d, 30d, 90d"),
):
    """
    Get KPI trend data over time.
    
    Returns exception, resolution, and volume trends for charting.
    """
    period_days = {"7d": 7, "30d": 30, "90d": 90}.get(period, 30)
    
    exception_sql = f"""
        SELECT 
            DATE_TRUNC('DAY', CREATED_AT) as DATE,
            COUNT(*) as VALUE
        FROM TRADE_COMPLIANCE.ENTRY_LINE_EXCEPTIONS
        WHERE CREATED_AT >= DATEADD('DAY', -{period_days}, CURRENT_DATE())
        GROUP BY DATE_TRUNC('DAY', CREATED_AT)
        ORDER BY DATE
    """
    
    resolution_sql = f"""
        SELECT 
            DATE_TRUNC('DAY', RESOLVED_AT) as DATE,
            COUNT(*) as VALUE
        FROM TRADE_COMPLIANCE.ENTRY_LINE_EXCEPTIONS
        WHERE RESOLVED_AT IS NOT NULL 
          AND RESOLVED_AT >= DATEADD('DAY', -{period_days}, CURRENT_DATE())
        GROUP BY DATE_TRUNC('DAY', RESOLVED_AT)
        ORDER BY DATE
    """
    
    volume_sql = f"""
        SELECT 
            DATE_TRUNC('DAY', ENTRY_DATE) as DATE,
            COUNT(*) as VALUE
        FROM TRADE_COMPLIANCE.ENTRY_LINE
        WHERE ENTRY_DATE >= DATEADD('DAY', -{period_days}, CURRENT_DATE())
        GROUP BY DATE_TRUNC('DAY', ENTRY_DATE)
        ORDER BY DATE
    """
    
    try:
        exception_rows = execute_query(exception_sql)
        resolution_rows = execute_query(resolution_sql)
        volume_rows = execute_query(volume_sql)
        
        exception_trend = [
            TrendPoint(date=row["DATE"], value=float(row["VALUE"]))
            for row in exception_rows
        ]
        
        resolution_trend = [
            TrendPoint(date=row["DATE"], value=float(row["VALUE"]))
            for row in resolution_rows
        ]
        
        volume_trend = [
            TrendPoint(date=row["DATE"], value=float(row["VALUE"]))
            for row in volume_rows
        ]
        
        return KPITrends(
            exception_trend=exception_trend,
            resolution_trend=resolution_trend,
            volume_trend=volume_trend,
            period=period,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
