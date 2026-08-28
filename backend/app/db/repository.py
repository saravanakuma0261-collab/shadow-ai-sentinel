"""
Database Repository (Hybrid Supabase + SQLite Fallback)
======================================================
Centralised data-access layer. Attempts Supabase cloud storage first.
Gracefully falls back to local SQLite database when Supabase is empty, unconfigured,
or operating under restricted RLS policies.
"""

import logging
from typing import Dict, List, Optional, Any

from app.db.supabase_client import get_supabase
from app.db import sqlite_repo
from app.db.models import (
    User,
    PasswordReset,
    Scan,
    Finding,
    FingerprintDomain,
    FingerprintExtension,
    AgentInvestigation,
    AlertLog,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Users
# =============================================================================

def get_user_by_email(email: str) -> Optional[User]:
    try:
        supabase = get_supabase()
        res = supabase.table("users").select("*").eq("email", email.lower().strip()).limit(1).execute()
        if res.data:
            return User.from_supabase_row(res.data[0])
    except Exception as e:
        logger.debug(f"Supabase get_user_by_email fallback: {e}")
    return sqlite_repo.get_user_by_email(email)


def get_user_by_id(user_id: str) -> Optional[User]:
    try:
        supabase = get_supabase()
        res = supabase.table("users").select("*").eq("id", user_id).limit(1).execute()
        if res.data:
            return User.from_supabase_row(res.data[0])
    except Exception as e:
        logger.debug(f"Supabase get_user_by_id fallback: {e}")
    return sqlite_repo.get_user_by_id(user_id)


def get_user_by_google_id(google_id: str) -> Optional[User]:
    try:
        supabase = get_supabase()
        res = supabase.table("users").select("*").eq("google_id", google_id).limit(1).execute()
        if res.data:
            return User.from_supabase_row(res.data[0])
    except Exception as e:
        logger.debug(f"Supabase get_user_by_google_id fallback: {e}")
    return sqlite_repo.get_user_by_google_id(google_id)


def create_user(user: User) -> User:
    local_user = sqlite_repo.create_user(user)
    try:
        supabase = get_supabase()
        res = supabase.table("users").insert(user.to_supabase_dict()).execute()
        if res.data:
            return User.from_supabase_row(res.data[0])
    except Exception as e:
        logger.debug(f"Supabase create_user failed, using local: {e}")
    return local_user


def update_user(user_id: str, fields: Dict[str, Any]) -> None:
    sqlite_repo.update_user(user_id, fields)
    try:
        supabase = get_supabase()
        supabase.table("users").update(fields).eq("id", user_id).execute()
    except Exception as e:
        logger.debug(f"Supabase update_user fallback: {e}")


def count_users() -> int:
    try:
        supabase = get_supabase()
        res = supabase.table("users").select("*", count="exact").limit(1).execute()
        if res.count is not None and res.count > 0:
            return res.count
    except Exception:
        pass
    return sqlite_repo.count_users()


def count_active_admins() -> int:
    try:
        supabase = get_supabase()
        res = supabase.table("users").select("*", count="exact").eq("role", "admin").eq("is_active", True).limit(1).execute()
        if res.count is not None and res.count > 0:
            return res.count
    except Exception:
        pass
    return sqlite_repo.count_active_admins()


def list_users() -> List[User]:
    try:
        supabase = get_supabase()
        res = supabase.table("users").select("*").execute()
        if res.data:
            return [User.from_supabase_row(d) for d in res.data]
    except Exception:
        pass
    return sqlite_repo.list_users()


# =============================================================================
# Password Resets
# =============================================================================

def create_password_reset(reset: PasswordReset) -> PasswordReset:
    local_reset = sqlite_repo.create_password_reset(reset)
    try:
        supabase = get_supabase()
        res = supabase.table("password_resets").insert(reset.to_supabase_dict()).execute()
        if res.data:
            return PasswordReset.from_supabase_row(res.data[0])
    except Exception:
        pass
    return local_reset


def get_password_reset_by_token_hash(token_hash: str) -> Optional[PasswordReset]:
    try:
        supabase = get_supabase()
        res = supabase.table("password_resets").select("*").eq("token_hash", token_hash).eq("used", False).limit(1).execute()
        if res.data:
            return PasswordReset.from_supabase_row(res.data[0])
    except Exception:
        pass
    return sqlite_repo.get_password_reset_by_token_hash(token_hash)


def mark_password_reset_used(reset_id: str) -> None:
    sqlite_repo.mark_password_reset_used(reset_id)
    try:
        supabase = get_supabase()
        supabase.table("password_resets").update({"used": True}).eq("id", reset_id).execute()
    except Exception:
        pass


# =============================================================================
# Scans
# =============================================================================

def create_scan(scan: Scan) -> Scan:
    local_scan = sqlite_repo.create_scan(scan)
    try:
        supabase = get_supabase()
        res = supabase.table("scans").insert(scan.to_supabase_dict()).execute()
        if res.data:
            return Scan.from_supabase_row(res.data[0])
    except Exception:
        pass
    return local_scan


def get_scan(scan_id: str) -> Optional[Scan]:
    try:
        supabase = get_supabase()
        res = supabase.table("scans").select("*").eq("id", scan_id).limit(1).execute()
        if res.data:
            return Scan.from_supabase_row(res.data[0])
    except Exception:
        pass
    return sqlite_repo.get_scan(scan_id)


def update_scan(scan_id: str, fields: Dict[str, Any]) -> None:
    sqlite_repo.update_scan(scan_id, fields)
    try:
        supabase = get_supabase()
        supabase.table("scans").update(fields).eq("id", scan_id).execute()
    except Exception:
        pass


def list_scans(limit: Optional[int] = None) -> List[Scan]:
    try:
        supabase = get_supabase()
        query = supabase.table("scans").select("*").order("started_at", desc=True)
        if limit:
            query = query.limit(limit)
        res = query.execute()
        if res.data:
            return [Scan.from_supabase_row(d) for d in res.data]
    except Exception:
        pass
    return sqlite_repo.list_scans(limit)


# =============================================================================
# Findings
# =============================================================================

def create_finding(finding: Finding) -> Finding:
    local_finding = sqlite_repo.create_finding(finding)
    try:
        supabase = get_supabase()
        res = supabase.table("findings").insert(finding.to_supabase_dict()).execute()
        if res.data:
            return Finding.from_supabase_row(res.data[0])
    except Exception:
        pass
    return local_finding


def get_finding(finding_id: str) -> Optional[Finding]:
    try:
        supabase = get_supabase()
        res = supabase.table("findings").select("*").eq("id", finding_id).limit(1).execute()
        if res.data:
            return Finding.from_supabase_row(res.data[0])
    except Exception:
        pass
    return sqlite_repo.get_finding(finding_id)


def list_findings(
    scan_id: Optional[str] = None,
    risk_tier: Optional[str] = None,
    sanction_status: Optional[str] = None,
    entity_type: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Finding]:
    try:
        supabase = get_supabase()
        query = supabase.table("findings").select("*")

        if scan_id:
            query = query.eq("scan_id", scan_id)
        if risk_tier:
            query = query.eq("risk_tier", risk_tier.lower())
        if sanction_status:
            query = query.eq("sanction_status", sanction_status.lower())
        if entity_type:
            query = query.eq("entity_type", entity_type.lower())
        if category:
            query = query.ilike("category", f"%{category}%")
        if search:
            s = search.strip()
            query = query.or_(f"entity_value.ilike.%{s}%,vendor.ilike.%{s}%,category.ilike.%{s}%")

        query = query.order("risk_score", desc=True)
        res = query.execute()
        if res.data:
            return [Finding.from_supabase_row(d) for d in res.data]
    except Exception:
        pass
    return sqlite_repo.list_findings(
        scan_id=scan_id,
        risk_tier=risk_tier,
        sanction_status=sanction_status,
        entity_type=entity_type,
        category=category,
        search=search,
    )


def count_findings_by_tier(tier: str) -> int:
    try:
        supabase = get_supabase()
        res = supabase.table("findings").select("*", count="exact").eq("risk_tier", tier.lower()).limit(1).execute()
        if res.count is not None and res.count > 0:
            return res.count
    except Exception:
        pass
    return sqlite_repo.count_findings_by_tier(tier)


def count_findings_by_sanction_statuses(statuses: List[str]) -> int:
    try:
        supabase = get_supabase()
        res = supabase.table("findings").select("*", count="exact").in_("sanction_status", statuses).limit(1).execute()
        if res.count is not None and res.count > 0:
            return res.count
    except Exception:
        pass
    return sqlite_repo.count_findings_by_sanction_statuses(statuses)


def count_all_findings() -> int:
    try:
        supabase = get_supabase()
        res = supabase.table("findings").select("*", count="exact").limit(1).execute()
        if res.count is not None and res.count > 0:
            return res.count
    except Exception:
        pass
    return sqlite_repo.count_all_findings()


def sum_findings_field(field: str) -> int:
    try:
        supabase = get_supabase()
        res = supabase.table("findings").select(field).execute()
        if res.data:
            return sum(d.get(field, 0) for d in res.data)
    except Exception:
        pass
    return sqlite_repo.sum_findings_field(field)


def top_findings(limit: int = 5) -> List[Finding]:
    try:
        supabase = get_supabase()
        res = supabase.table("findings").select("*").order("risk_score", desc=True).limit(limit).execute()
        if res.data:
            return [Finding.from_supabase_row(d) for d in res.data]
    except Exception:
        pass
    return sqlite_repo.top_findings(limit)


def count_findings_for_scan(scan_id: str) -> int:
    try:
        supabase = get_supabase()
        res = supabase.table("findings").select("*", count="exact").eq("scan_id", scan_id).limit(1).execute()
        if res.count is not None and res.count > 0:
            return res.count
    except Exception:
        pass
    return sqlite_repo.count_findings_for_scan(scan_id)


def list_findings_for_scan_sorted(scan_id: str) -> List[Finding]:
    try:
        supabase = get_supabase()
        res = supabase.table("findings").select("*").eq("scan_id", scan_id).order("risk_score", desc=True).execute()
        if res.data:
            return [Finding.from_supabase_row(d) for d in res.data]
    except Exception:
        pass
    return sqlite_repo.list_findings_for_scan_sorted(scan_id)


# =============================================================================
# Fingerprint Domains / Extensions
# =============================================================================

def get_fingerprint_domains() -> List[FingerprintDomain]:
    try:
        supabase = get_supabase()
        res = supabase.table("fingerprint_domains").select("*").execute()
        if res.data:
            return [FingerprintDomain.from_supabase_row(d) for d in res.data]
    except Exception:
        pass
    return sqlite_repo.get_fingerprint_domains()


def get_fingerprint_extensions() -> List[FingerprintExtension]:
    try:
        supabase = get_supabase()
        res = supabase.table("fingerprint_extensions").select("*").execute()
        if res.data:
            return [FingerprintExtension.from_supabase_row(d) for d in res.data]
    except Exception:
        pass
    return sqlite_repo.get_fingerprint_extensions()


def count_fingerprint_domains() -> int:
    try:
        supabase = get_supabase()
        res = supabase.table("fingerprint_domains").select("*", count="exact").limit(1).execute()
        if res.count is not None and res.count > 0:
            return res.count
    except Exception:
        pass
    return sqlite_repo.count_fingerprint_domains()


def count_fingerprint_extensions() -> int:
    try:
        supabase = get_supabase()
        res = supabase.table("fingerprint_extensions").select("*", count="exact").limit(1).execute()
        if res.count is not None and res.count > 0:
            return res.count
    except Exception:
        pass
    return sqlite_repo.count_fingerprint_extensions()


def create_fingerprint_domain(domain: FingerprintDomain) -> FingerprintDomain:
    local_d = sqlite_repo.create_fingerprint_domain(domain)
    try:
        supabase = get_supabase()
        res = supabase.table("fingerprint_domains").insert(domain.to_supabase_dict()).execute()
        if res.data:
            return FingerprintDomain.from_supabase_row(res.data[0])
    except Exception:
        pass
    return local_d


def create_fingerprint_extension(ext: FingerprintExtension) -> FingerprintExtension:
    local_e = sqlite_repo.create_fingerprint_extension(ext)
    try:
        supabase = get_supabase()
        res = supabase.table("fingerprint_extensions").insert(ext.to_supabase_dict()).execute()
        if res.data:
            return FingerprintExtension.from_supabase_row(res.data[0])
    except Exception:
        pass
    return local_e


# =============================================================================
# Agent Investigations
# =============================================================================

def create_agent_investigation(inv: AgentInvestigation) -> AgentInvestigation:
    local_inv = sqlite_repo.create_agent_investigation(inv)
    try:
        supabase = get_supabase()
        res = supabase.table("agent_investigations").insert(inv.to_supabase_dict()).execute()
        if res.data:
            return AgentInvestigation.from_supabase_row(res.data[0])
    except Exception:
        pass
    return local_inv


def get_investigations_for_finding(finding_id: str) -> List[AgentInvestigation]:
    try:
        supabase = get_supabase()
        res = supabase.table("agent_investigations").select("*").eq("finding_id", finding_id).execute()
        if res.data:
            return [AgentInvestigation.from_supabase_row(d) for d in res.data]
    except Exception:
        pass
    return sqlite_repo.get_investigations_for_finding(finding_id)


# =============================================================================
# Alert Log
# =============================================================================

def create_alert_log(alert: AlertLog) -> AlertLog:
    local_alert = sqlite_repo.create_alert_log(alert)
    try:
        supabase = get_supabase()
        res = supabase.table("alerts_log").insert(alert.to_supabase_dict()).execute()
        if res.data:
            return AlertLog.from_supabase_row(res.data[0])
    except Exception:
        pass
    return local_alert
