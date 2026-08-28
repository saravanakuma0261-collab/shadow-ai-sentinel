import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator


# -----------------------------------------------------------------------------
# Common
# -----------------------------------------------------------------------------
class MessageResponse(BaseModel):
    message: str


# -----------------------------------------------------------------------------
# Auth Schemas
# -----------------------------------------------------------------------------
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=6, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    auth_provider: str
    role: str
    is_active: bool
    created_at: datetime.datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserUpdateRole(BaseModel):
    role: str = Field(..., pattern="^(admin|analyst|viewer)$")


class UserUpdateActive(BaseModel):
    is_active: bool


# -----------------------------------------------------------------------------
# Risk & Finding Schemas
# -----------------------------------------------------------------------------
class RiskFactorBreakdown(BaseModel):
    category_risk: float
    sanction_risk: float
    data_exposure_risk: float
    usage_spread_risk: float


class AgentInvestigationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    finding_id: str
    summary: str
    recommendation: str  # 'block' | 'monitor' | 'escalate'
    rationale: str
    confidence: float
    created_at: datetime.datetime


class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    scan_id: str
    entity_type: str
    entity_value: str
    category: str
    vendor: str
    sanction_status: str
    data_exposure_bytes: int = 0
    users_affected: int = 1
    event_count: int = 1
    risk_score: float = 0.0
    risk_tier: str = "low"
    created_at: datetime.datetime

    # Frontend-friendly compatibility aliases
    service_name: Optional[str] = None
    entity_identifier: Optional[str] = None
    user_or_host: Optional[str] = None
    data_transferred_bytes: Optional[int] = None
    occurrence_count: Optional[int] = None
    first_seen: Optional[datetime.datetime] = None

    @model_validator(mode="before")
    @classmethod
    def populate_frontend_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            vendor = data.get("vendor") or ""
            entity_val = data.get("entity_value") or ""
            data["service_name"] = data.get("service_name") or (vendor if vendor and vendor != "Unknown Vendor" else entity_val)
            data["entity_identifier"] = data.get("entity_identifier") or entity_val
            users = data.get("users_affected", 1)
            data["user_or_host"] = data.get("user_or_host") or (f"{users} user{'s' if users != 1 else ''}")
            data["data_transferred_bytes"] = data.get("data_transferred_bytes", data.get("data_exposure_bytes", 0))
            data["occurrence_count"] = data.get("occurrence_count", data.get("event_count", 1))
            data["first_seen"] = data.get("first_seen") or data.get("created_at")
            return data
        elif hasattr(data, "__dict__") or hasattr(data, "entity_value"):
            d = dict(data) if isinstance(data, dict) else (data.model_dump() if hasattr(data, "model_dump") else data.__dict__)
            vendor = getattr(data, "vendor", "") or ""
            entity_val = getattr(data, "entity_value", "") or ""
            d["service_name"] = d.get("service_name") or (vendor if vendor and vendor != "Unknown Vendor" else entity_val)
            d["entity_identifier"] = d.get("entity_identifier") or entity_val
            users = getattr(data, "users_affected", 1) or 1
            d["user_or_host"] = d.get("user_or_host") or (f"{users} user{'s' if users != 1 else ''}")
            d["data_transferred_bytes"] = getattr(data, "data_exposure_bytes", 0) or 0
            d["occurrence_count"] = getattr(data, "event_count", 1) or 1
            d["first_seen"] = getattr(data, "created_at", None)
            return d
        return data


class FindingDetailResponse(FindingResponse):
    risk_breakdown: Optional[RiskFactorBreakdown] = None
    explanation_breakdown: Optional[Dict[str, Any]] = None
    investigation: Optional[AgentInvestigationResponse] = None
    investigations: List[AgentInvestigationResponse] = []


# -----------------------------------------------------------------------------
# Scan Schemas
# -----------------------------------------------------------------------------
class ScanTriggerRequest(BaseModel):
    source_type: Optional[str] = "combined"  # network_dns_log | extensions_export | combined
    scan_type: Optional[str] = None          # network | extension | combined
    name: Optional[str] = None
    raw_data: Optional[str] = None
    custom_log_content: Optional[str] = None  # Optional raw CSV/JSON override


class ScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: Optional[str] = None
    scan_type: Optional[str] = None
    total_events: Optional[int] = 0
    findings_count: int = 0
    started_at: datetime.datetime
    created_at: Optional[datetime.datetime] = None
    finished_at: Optional[datetime.datetime] = None
    source_type: str = "combined"
    status: str = "completed"
    triggered_by: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def populate_scan_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            src = data.get("source_type") or "combined"
            data["scan_type"] = data.get("scan_type") or ("extension" if "extension" in src else "network")
            data["name"] = data.get("name") or f"{'Extension' if 'extension' in src else 'Network DNS'} Scan #{data.get('id', '')}"
            data["created_at"] = data.get("created_at") or data.get("started_at")
            return data
        elif hasattr(data, "__dict__") or hasattr(data, "source_type"):
            d = dict(data) if isinstance(data, dict) else (data.model_dump() if hasattr(data, "model_dump") else data.__dict__)
            src = getattr(data, "source_type", "combined") or "combined"
            d["scan_type"] = d.get("scan_type") or ("extension" if "extension" in src else "network")
            d["name"] = d.get("name") or f"{'Extension' if 'extension' in src else 'Network DNS'} Scan #{getattr(data, 'id', '')}"
            d["created_at"] = d.get("created_at") or getattr(data, "started_at", None)
            return d
        return data


class ScanDetailResponse(ScanResponse):
    findings: List[FindingResponse] = []


# -----------------------------------------------------------------------------
# Dashboard & Metrics Schemas
# -----------------------------------------------------------------------------
class ScanHistoryItemResponse(BaseModel):
    scan: ScanResponse
    total_findings: int


class TopRiskEntity(BaseModel):
    id: str
    entity_value: str
    category: str
    risk_score: float
    risk_tier: str


class DashboardSummaryResponse(BaseModel):
    total_findings: int
    critical_risk_count: int
    high_risk_count: int
    unsanctioned_apps_count: int
    total_data_exposure_bytes: int
    top_risks: List[TopRiskEntity]
    recent_scans: List[ScanResponse]
