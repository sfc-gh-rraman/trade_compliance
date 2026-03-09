from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class ExceptionStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"


class ValidationResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class RuleStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    REJECTED = "REJECTED"


class RuleSource(str, Enum):
    MANUAL = "MANUAL"
    AI_DISCOVERED = "AI_DISCOVERED"


class ExceptionSummary(BaseModel):
    line_id: str
    entry_number: str
    broker_name: str
    entry_date: datetime
    part_number: str
    part_validation: ValidationResult
    hts_validation: ValidationResult
    add_cvd_validation: ValidationResult
    status: ExceptionStatus
    created_at: datetime


class ExceptionDetail(BaseModel):
    line_id: str
    entry_number: str
    entry_summary_line: int
    broker_name: str
    broker_id: str
    entry_date: datetime
    part_number: str
    declared_value: float
    country_of_origin: str
    broker_hts_code: str
    gtm_hts_code: Optional[str] = None
    part_validation: ValidationResult
    hts_validation: ValidationResult
    add_cvd_validation: ValidationResult
    preferential_program: Optional[str] = None
    audit_comments: Optional[str] = None
    anomaly_score: Optional[float] = None
    anomaly_explanation: Optional[str] = None
    status: ExceptionStatus
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime


class ExceptionListResponse(BaseModel):
    exceptions: list[ExceptionSummary]
    total: int
    page: int
    page_size: int


class ResolveRequest(BaseModel):
    resolution_notes: str
    resolved_by: str


class RuleResponse(BaseModel):
    rule_id: str
    rule_name: str
    description: str
    rule_type: str
    condition_sql: str
    severity: str
    source: RuleSource
    status: RuleStatus
    confidence: Optional[float] = None
    discovery_date: Optional[datetime] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime


class RuleListResponse(BaseModel):
    rules: list[RuleResponse]
    total: int


class RuleApprovalRequest(BaseModel):
    approved_by: str
    notes: Optional[str] = None


class BrokerSummary(BaseModel):
    broker_id: str
    broker_name: str
    region: str
    total_entries: int
    exception_rate: float
    avg_processing_time_hours: float
    quality_score: float
    status: str


class BrokerDetail(BaseModel):
    broker_id: str
    broker_name: str
    region: str
    contact_email: Optional[str] = None
    schema_mapping: Optional[dict[str, str]] = None
    total_entries: int
    total_exceptions: int
    exception_rate: float
    part_fail_rate: float
    hts_fail_rate: float
    add_cvd_fail_rate: float
    avg_processing_time_hours: float
    quality_score: float
    onboarding_date: datetime
    status: str


class BrokerListResponse(BaseModel):
    brokers: list[BrokerSummary]
    total: int


class OnboardingRequest(BaseModel):
    broker_name: str
    region: str
    contact_email: str
    sample_file_path: str


class OnboardingResponse(BaseModel):
    broker_id: str
    status: str
    inferred_schema: dict[str, str]
    confidence_scores: dict[str, float]
    message: str


class AnalystQueryRequest(BaseModel):
    query: str
    include_sql: bool = False


class AnalystQueryResponse(BaseModel):
    answer: str
    sql: Optional[str] = None
    results: Optional[list[dict[str, Any]]] = None
    visualization: Optional[dict[str, Any]] = None


class KPISummary(BaseModel):
    total_entries: int
    total_exceptions: int
    exception_rate: float
    resolution_rate: float
    avg_resolution_time_hours: float
    active_brokers: int
    discovered_rules: int
    ai_detected_anomalies: int


class TrendPoint(BaseModel):
    date: datetime
    value: float


class KPITrends(BaseModel):
    exception_trend: list[TrendPoint]
    resolution_trend: list[TrendPoint]
    volume_trend: list[TrendPoint]
    period: str


class AgentMessage(BaseModel):
    role: str
    content: str


class AgentRequest(BaseModel):
    message: str
    conversation_history: list[AgentMessage] = Field(default_factory=list)


class AgentResponse(BaseModel):
    response: str
    sources: Optional[list[str]] = None
    context: Optional[dict[str, Any]] = None
    intent: Optional[str] = None
    visualization: Optional[dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    snowflake_connected: bool
    timestamp: datetime
