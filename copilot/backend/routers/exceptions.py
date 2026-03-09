from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from models.schemas import (
    ExceptionListResponse,
    ExceptionDetail,
    ExceptionSummary,
    ExceptionStatus,
    ValidationResult,
    ResolveRequest,
)
from database import execute_query, execute_query_single

router = APIRouter(prefix="/exceptions", tags=["exceptions"])


@router.get("", response_model=ExceptionListResponse)
async def list_exceptions(
    broker_id: Optional[str] = Query(None, description="Filter by broker ID"),
    status: Optional[ExceptionStatus] = Query(None, description="Filter by status"),
    validation_type: Optional[str] = Query(None, description="Filter by validation type (part, hts, add_cvd)"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    List exceptions with optional filters.
    
    Returns paginated list of entry line exceptions that failed validation.
    """
    offset = (page - 1) * page_size
    
    where_clauses = ["1=1"]
    if broker_id:
        where_clauses.append(f"BROKER_ID = '{broker_id}'")
    if status:
        where_clauses.append(f"STATUS = '{status.value}'")
    if validation_type == "part":
        where_clauses.append("PART_VALIDATION = 'FAIL'")
    elif validation_type == "hts":
        where_clauses.append("HTS_VALIDATION = 'FAIL'")
    elif validation_type == "add_cvd":
        where_clauses.append("ADD_CVD_VALIDATION = 'FAIL'")
    if start_date:
        where_clauses.append(f"ENTRY_DATE >= '{start_date.isoformat()}'")
    if end_date:
        where_clauses.append(f"ENTRY_DATE <= '{end_date.isoformat()}'")
    
    where_sql = " AND ".join(where_clauses)
    
    count_sql = f"""
        SELECT COUNT(*) as TOTAL
        FROM TRADE_COMPLIANCE.ENTRY_LINE_EXCEPTIONS
        WHERE {where_sql}
    """
    
    query_sql = f"""
        SELECT 
            LINE_ID, ENTRY_NUMBER, BROKER_NAME, ENTRY_DATE,
            PART_NUMBER, PART_VALIDATION, HTS_VALIDATION, 
            ADD_CVD_VALIDATION, STATUS, CREATED_AT
        FROM TRADE_COMPLIANCE.ENTRY_LINE_EXCEPTIONS
        WHERE {where_sql}
        ORDER BY CREATED_AT DESC
        LIMIT {page_size} OFFSET {offset}
    """
    
    try:
        count_result = execute_query_single(count_sql)
        total = count_result["TOTAL"] if count_result else 0
        
        rows = execute_query(query_sql)
        exceptions = [
            ExceptionSummary(
                line_id=row["LINE_ID"],
                entry_number=row["ENTRY_NUMBER"],
                broker_name=row["BROKER_NAME"],
                entry_date=row["ENTRY_DATE"],
                part_number=row["PART_NUMBER"],
                part_validation=ValidationResult(row["PART_VALIDATION"]),
                hts_validation=ValidationResult(row["HTS_VALIDATION"]),
                add_cvd_validation=ValidationResult(row["ADD_CVD_VALIDATION"]),
                status=ExceptionStatus(row["STATUS"]),
                created_at=row["CREATED_AT"],
            )
            for row in rows
        ]
        
        return ExceptionListResponse(
            exceptions=exceptions,
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{line_id}", response_model=ExceptionDetail)
async def get_exception(line_id: str):
    """
    Get detailed information for a specific exception.
    
    Returns full exception details including anomaly scores and audit info.
    """
    sql = """
        SELECT 
            LINE_ID, ENTRY_NUMBER, ENTRY_SUMMARY_LINE, BROKER_NAME, BROKER_ID,
            ENTRY_DATE, PART_NUMBER, DECLARED_VALUE, COUNTRY_OF_ORIGIN,
            BROKER_HTS_CODE, GTM_HTS_CODE, PART_VALIDATION, HTS_VALIDATION,
            ADD_CVD_VALIDATION, PREFERENTIAL_PROGRAM, AUDIT_COMMENTS,
            ANOMALY_SCORE, ANOMALY_EXPLANATION, STATUS, RESOLVED_BY,
            RESOLVED_AT, CREATED_AT
        FROM TRADE_COMPLIANCE.ENTRY_LINE_EXCEPTIONS
        WHERE LINE_ID = %(line_id)s
    """
    
    try:
        row = execute_query_single(sql, {"line_id": line_id})
        if not row:
            raise HTTPException(status_code=404, detail=f"Exception {line_id} not found")
        
        return ExceptionDetail(
            line_id=row["LINE_ID"],
            entry_number=row["ENTRY_NUMBER"],
            entry_summary_line=row["ENTRY_SUMMARY_LINE"],
            broker_name=row["BROKER_NAME"],
            broker_id=row["BROKER_ID"],
            entry_date=row["ENTRY_DATE"],
            part_number=row["PART_NUMBER"],
            declared_value=float(row["DECLARED_VALUE"]),
            country_of_origin=row["COUNTRY_OF_ORIGIN"],
            broker_hts_code=row["BROKER_HTS_CODE"],
            gtm_hts_code=row["GTM_HTS_CODE"],
            part_validation=ValidationResult(row["PART_VALIDATION"]),
            hts_validation=ValidationResult(row["HTS_VALIDATION"]),
            add_cvd_validation=ValidationResult(row["ADD_CVD_VALIDATION"]),
            preferential_program=row["PREFERENTIAL_PROGRAM"],
            audit_comments=row["AUDIT_COMMENTS"],
            anomaly_score=float(row["ANOMALY_SCORE"]) if row["ANOMALY_SCORE"] else None,
            anomaly_explanation=row["ANOMALY_EXPLANATION"],
            status=ExceptionStatus(row["STATUS"]),
            resolved_by=row["RESOLVED_BY"],
            resolved_at=row["RESOLVED_AT"],
            created_at=row["CREATED_AT"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{line_id}/resolve")
async def resolve_exception(line_id: str, request: ResolveRequest):
    """
    Mark an exception as resolved.
    
    Updates the exception status and records resolution details.
    """
    sql = """
        UPDATE TRADE_COMPLIANCE.ENTRY_LINE_EXCEPTIONS
        SET 
            STATUS = 'RESOLVED',
            RESOLVED_BY = %(resolved_by)s,
            RESOLVED_AT = CURRENT_TIMESTAMP(),
            AUDIT_COMMENTS = COALESCE(AUDIT_COMMENTS, '') || ' | Resolution: ' || %(notes)s
        WHERE LINE_ID = %(line_id)s
    """
    
    try:
        execute_query(sql, {
            "line_id": line_id,
            "resolved_by": request.resolved_by,
            "notes": request.resolution_notes,
        })
        return {"status": "success", "message": f"Exception {line_id} resolved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
