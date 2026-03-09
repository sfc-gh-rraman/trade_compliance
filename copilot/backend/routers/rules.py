from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from models.schemas import (
    RuleListResponse,
    RuleResponse,
    RuleStatus,
    RuleSource,
    RuleApprovalRequest,
)
from database import execute_query, execute_query_single

router = APIRouter(prefix="/rules", tags=["rules"])


@router.get("", response_model=RuleListResponse)
async def list_rules(
    status: Optional[RuleStatus] = Query(None, description="Filter by status"),
    rule_type: Optional[str] = Query(None, description="Filter by rule type"),
):
    """
    List all active validation rules.
    
    Returns rules used for entry line validation including both manual and AI-discovered rules.
    """
    where_clauses = ["STATUS = 'ACTIVE'"]
    if status:
        where_clauses = [f"STATUS = '{status.value}'"]
    if rule_type:
        where_clauses.append(f"RULE_TYPE = '{rule_type}'")
    
    where_sql = " AND ".join(where_clauses)
    
    sql = f"""
        SELECT 
            RULE_ID, RULE_NAME, DESCRIPTION, RULE_TYPE, CONDITION_SQL,
            SEVERITY, SOURCE, STATUS, CONFIDENCE, DISCOVERY_DATE,
            APPROVED_BY, APPROVED_AT, CREATED_AT
        FROM RULES.VALIDATION_RULES
        WHERE {where_sql}
        ORDER BY CREATED_AT DESC
    """
    
    try:
        rows = execute_query(sql)
        rules = [
            RuleResponse(
                rule_id=row["RULE_ID"],
                rule_name=row["RULE_NAME"],
                description=row["DESCRIPTION"],
                rule_type=row["RULE_TYPE"],
                condition_sql=row["CONDITION_SQL"],
                severity=row["SEVERITY"],
                source=RuleSource(row["SOURCE"]),
                status=RuleStatus(row["STATUS"]),
                confidence=float(row["CONFIDENCE"]) if row["CONFIDENCE"] else None,
                discovery_date=row["DISCOVERY_DATE"],
                approved_by=row["APPROVED_BY"],
                approved_at=row["APPROVED_AT"],
                created_at=row["CREATED_AT"],
            )
            for row in rows
        ]
        
        return RuleListResponse(rules=rules, total=len(rules))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/discovered", response_model=RuleListResponse)
async def list_discovered_rules():
    """
    List AI-discovered validation rules pending approval.
    
    These rules were discovered by analyzing correction patterns and anomalies.
    """
    sql = """
        SELECT 
            RULE_ID, RULE_NAME, DESCRIPTION, RULE_TYPE, CONDITION_SQL,
            SEVERITY, SOURCE, STATUS, CONFIDENCE, DISCOVERY_DATE,
            APPROVED_BY, APPROVED_AT, CREATED_AT
        FROM RULES.DISCOVERED_RULES
        WHERE STATUS = 'PENDING'
        ORDER BY CONFIDENCE DESC, DISCOVERY_DATE DESC
    """
    
    try:
        rows = execute_query(sql)
        rules = [
            RuleResponse(
                rule_id=row["RULE_ID"],
                rule_name=row["RULE_NAME"],
                description=row["DESCRIPTION"],
                rule_type=row["RULE_TYPE"],
                condition_sql=row["CONDITION_SQL"],
                severity=row["SEVERITY"],
                source=RuleSource.AI_DISCOVERED,
                status=RuleStatus(row["STATUS"]),
                confidence=float(row["CONFIDENCE"]) if row["CONFIDENCE"] else None,
                discovery_date=row["DISCOVERY_DATE"],
                approved_by=row["APPROVED_BY"],
                approved_at=row["APPROVED_AT"],
                created_at=row["CREATED_AT"],
            )
            for row in rows
        ]
        
        return RuleListResponse(rules=rules, total=len(rules))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{rule_id}/approve")
async def approve_rule(rule_id: str, request: RuleApprovalRequest):
    """
    Approve an AI-discovered rule for production use.
    
    Moves the rule from discovered to active validation rules.
    """
    check_sql = """
        SELECT RULE_ID FROM RULES.DISCOVERED_RULES
        WHERE RULE_ID = %(rule_id)s AND STATUS = 'PENDING'
    """
    
    try:
        existing = execute_query_single(check_sql, {"rule_id": rule_id})
        if not existing:
            raise HTTPException(status_code=404, detail=f"Pending rule {rule_id} not found")
        
        update_sql = """
            UPDATE RULES.DISCOVERED_RULES
            SET 
                STATUS = 'ACTIVE',
                APPROVED_BY = %(approved_by)s,
                APPROVED_AT = CURRENT_TIMESTAMP()
            WHERE RULE_ID = %(rule_id)s
        """
        execute_query(update_sql, {
            "rule_id": rule_id,
            "approved_by": request.approved_by,
        })
        
        insert_sql = """
            INSERT INTO RULES.VALIDATION_RULES (
                RULE_ID, RULE_NAME, DESCRIPTION, RULE_TYPE, CONDITION_SQL,
                SEVERITY, SOURCE, STATUS, CONFIDENCE, DISCOVERY_DATE,
                APPROVED_BY, APPROVED_AT, CREATED_AT
            )
            SELECT 
                RULE_ID, RULE_NAME, DESCRIPTION, RULE_TYPE, CONDITION_SQL,
                SEVERITY, 'AI_DISCOVERED', 'ACTIVE', CONFIDENCE, DISCOVERY_DATE,
                %(approved_by)s, CURRENT_TIMESTAMP(), CREATED_AT
            FROM RULES.DISCOVERED_RULES
            WHERE RULE_ID = %(rule_id)s
        """
        execute_query(insert_sql, {
            "rule_id": rule_id,
            "approved_by": request.approved_by,
        })
        
        return {"status": "success", "message": f"Rule {rule_id} approved and activated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{rule_id}/reject")
async def reject_rule(rule_id: str, request: RuleApprovalRequest):
    """
    Reject an AI-discovered rule.
    
    Marks the rule as rejected so it won't be suggested again.
    """
    sql = """
        UPDATE RULES.DISCOVERED_RULES
        SET 
            STATUS = 'REJECTED',
            APPROVED_BY = %(approved_by)s,
            APPROVED_AT = CURRENT_TIMESTAMP()
        WHERE RULE_ID = %(rule_id)s AND STATUS = 'PENDING'
    """
    
    try:
        execute_query(sql, {
            "rule_id": rule_id,
            "approved_by": request.approved_by,
        })
        return {"status": "success", "message": f"Rule {rule_id} rejected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
