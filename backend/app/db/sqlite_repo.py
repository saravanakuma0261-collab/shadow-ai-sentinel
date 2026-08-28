"""
SQLite Fallback Repository
==========================
Provides reliable local database storage using SQLite (shadow_ai_sentinel.db)
when Supabase is unavailable, unseeded, or operates with restricted permissions.
"""

import sqlite3
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

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

DB_PATH = Path(__file__).resolve().parent.parent.parent / "shadow_ai_sentinel.db"


def _get_connection():
    con = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    if "id" in d and d["id"] is not None:
        d["id"] = str(d["id"])
    if "is_active" in d and d["is_active"] is not None:
        d["is_active"] = bool(d["is_active"])
    if "sanctioned" in d and d["sanctioned"] is not None:
        d["sanctioned"] = bool(d["sanctioned"])
    if "used" in d and d["used"] is not None:
        d["used"] = bool(d["used"])
    if "scan_id" in d and d["scan_id"] is not None:
        d["scan_id"] = str(d["scan_id"])
    if "user_id" in d and d["user_id"] is not None:
        d["user_id"] = str(d["user_id"])
    if "finding_id" in d and d["finding_id"] is not None:
        d["finding_id"] = str(d["finding_id"])
    if "triggered_by" in d and d["triggered_by"] is not None:
        d["triggered_by"] = str(d["triggered_by"])
    return d


# =============================================================================
# Users
# =============================================================================

def get_user_by_email(email: str) -> Optional[User]:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE LOWER(email) = ? LIMIT 1", (email.lower().strip(),))
        row = cur.fetchone()
        if row:
            return User.model_validate(_row_to_dict(row))
        return None
    finally:
        con.close()


def get_user_by_id(user_id: str) -> Optional[User]:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE id = ? LIMIT 1", (user_id,))
        row = cur.fetchone()
        if row:
            return User.model_validate(_row_to_dict(row))
        return None
    finally:
        con.close()


def get_user_by_google_id(google_id: str) -> Optional[User]:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE google_id = ? LIMIT 1", (google_id,))
        row = cur.fetchone()
        if row:
            return User.model_validate(_row_to_dict(row))
        return None
    finally:
        con.close()


def create_user(user: User) -> User:
    con = _get_connection()
    try:
        cur = con.cursor()
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cur.execute(
            """
            INSERT INTO users (name, email, password_hash, auth_provider, google_id, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user.name,
                user.email.lower().strip(),
                user.password_hash,
                user.auth_provider,
                user.google_id,
                user.role,
                1 if user.is_active else 0,
                now,
            )
        )
        con.commit()
        user_id = cur.lastrowid
        return get_user_by_id(str(user_id))
    finally:
        con.close()


def update_user(user_id: str, fields: Dict[str, Any]) -> None:
    con = _get_connection()
    try:
        cur = con.cursor()
        set_clauses = []
        values = []
        for k, v in fields.items():
            set_clauses.append(f"{k} = ?")
            if isinstance(v, bool):
                values.append(1 if v else 0)
            else:
                values.append(v)
        values.append(user_id)
        cur.execute(f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?", tuple(values))
        con.commit()
    finally:
        con.close()


def count_users() -> int:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        return cur.fetchone()[0]
    finally:
        con.close()


def count_active_admins() -> int:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1")
        return cur.fetchone()[0]
    finally:
        con.close()


def list_users() -> List[User]:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM users ORDER BY id ASC")
        return [User.model_validate(_row_to_dict(r)) for r in cur.fetchall()]
    finally:
        con.close()


# =============================================================================
# Password Resets
# =============================================================================

def create_password_reset(reset: PasswordReset) -> PasswordReset:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO password_resets (user_id, token_hash, expires_at, used, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                reset.user_id,
                reset.token_hash,
                reset.expires_at.isoformat() if hasattr(reset.expires_at, "isoformat") else reset.expires_at,
                1 if reset.used else 0,
                reset.created_at.isoformat() if hasattr(reset.created_at, "isoformat") else reset.created_at,
            )
        )
        con.commit()
        row_id = cur.lastrowid
        cur.execute("SELECT * FROM password_resets WHERE id = ?", (row_id,))
        return PasswordReset.model_validate(_row_to_dict(cur.fetchone()))
    finally:
        con.close()


def get_password_reset_by_token_hash(token_hash: str) -> Optional[PasswordReset]:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM password_resets WHERE token_hash = ? AND used = 0 LIMIT 1", (token_hash,))
        row = cur.fetchone()
        if row:
            return PasswordReset.model_validate(_row_to_dict(row))
        return None
    finally:
        con.close()


def mark_password_reset_used(reset_id: str) -> None:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("UPDATE password_resets SET used = 1 WHERE id = ?", (reset_id,))
        con.commit()
    finally:
        con.close()


# =============================================================================
# Scans
# =============================================================================

def create_scan(scan: Scan) -> Scan:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO scans (started_at, finished_at, source_type, status, triggered_by)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                scan.started_at.isoformat() if hasattr(scan.started_at, "isoformat") else scan.started_at,
                scan.finished_at.isoformat() if scan.finished_at and hasattr(scan.finished_at, "isoformat") else scan.finished_at,
                scan.source_type,
                scan.status,
                scan.triggered_by,
            )
        )
        con.commit()
        row_id = cur.lastrowid
        cur.execute("SELECT * FROM scans WHERE id = ?", (row_id,))
        return Scan.model_validate(_row_to_dict(cur.fetchone()))
    finally:
        con.close()


def get_scan(scan_id: str) -> Optional[Scan]:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM scans WHERE id = ? LIMIT 1", (scan_id,))
        row = cur.fetchone()
        if row:
            return Scan.model_validate(_row_to_dict(row))
        return None
    finally:
        con.close()


def update_scan(scan_id: str, fields: Dict[str, Any]) -> None:
    con = _get_connection()
    try:
        cur = con.cursor()
        set_clauses = []
        values = []
        for k, v in fields.items():
            set_clauses.append(f"{k} = ?")
            if isinstance(v, (datetime.datetime, datetime.date)):
                values.append(v.isoformat())
            else:
                values.append(v)
        values.append(scan_id)
        cur.execute(f"UPDATE scans SET {', '.join(set_clauses)} WHERE id = ?", tuple(values))
        con.commit()
    finally:
        con.close()


def list_scans(limit: Optional[int] = None) -> List[Scan]:
    con = _get_connection()
    try:
        cur = con.cursor()
        sql = "SELECT * FROM scans ORDER BY started_at DESC"
        if limit:
            sql += f" LIMIT {int(limit)}"
        cur.execute(sql)
        return [Scan.model_validate(_row_to_dict(r)) for r in cur.fetchall()]
    finally:
        con.close()


# =============================================================================
# Findings
# =============================================================================

def create_finding(finding: Finding) -> Finding:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO findings (scan_id, entity_type, entity_value, category, vendor, sanction_status,
                                  data_exposure_bytes, users_affected, event_count, risk_score, risk_tier, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                finding.scan_id,
                finding.entity_type,
                finding.entity_value,
                finding.category,
                finding.vendor,
                finding.sanction_status,
                finding.data_exposure_bytes,
                finding.users_affected,
                finding.event_count,
                finding.risk_score,
                finding.risk_tier,
                finding.created_at.isoformat() if hasattr(finding.created_at, "isoformat") else finding.created_at,
            )
        )
        con.commit()
        row_id = cur.lastrowid
        cur.execute("SELECT * FROM findings WHERE id = ?", (row_id,))
        return Finding.model_validate(_row_to_dict(cur.fetchone()))
    finally:
        con.close()


def get_finding(finding_id: str) -> Optional[Finding]:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM findings WHERE id = ? LIMIT 1", (finding_id,))
        row = cur.fetchone()
        if row:
            return Finding.model_validate(_row_to_dict(row))
        return None
    finally:
        con.close()


def list_findings(
    scan_id: Optional[str] = None,
    risk_tier: Optional[str] = None,
    sanction_status: Optional[str] = None,
    entity_type: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Finding]:
    con = _get_connection()
    try:
        cur = con.cursor()
        where_clauses = []
        params = []

        if scan_id:
            where_clauses.append("scan_id = ?")
            params.append(scan_id)
        if risk_tier:
            where_clauses.append("LOWER(risk_tier) = ?")
            params.append(risk_tier.lower())
        if sanction_status:
            where_clauses.append("LOWER(sanction_status) = ?")
            params.append(sanction_status.lower())
        if entity_type:
            where_clauses.append("LOWER(entity_type) = ?")
            params.append(entity_type.lower())
        if category:
            where_clauses.append("LOWER(category) LIKE ?")
            params.append(f"%{category.lower()}%")
        if search:
            s = f"%{search.lower()}%"
            where_clauses.append("(LOWER(entity_value) LIKE ? OR LOWER(vendor) LIKE ? OR LOWER(category) LIKE ?)")
            params.extend([s, s, s])

        where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        sql = f"SELECT * FROM findings{where_sql} ORDER BY risk_score DESC"
        cur.execute(sql, tuple(params))
        return [Finding.model_validate(_row_to_dict(r)) for r in cur.fetchall()]
    finally:
        con.close()


def count_findings_by_tier(tier: str) -> int:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM findings WHERE LOWER(risk_tier) = ?", (tier.lower(),))
        return cur.fetchone()[0]
    finally:
        con.close()


def count_findings_by_sanction_statuses(statuses: List[str]) -> int:
    con = _get_connection()
    try:
        cur = con.cursor()
        placeholders = ",".join(["?" for _ in statuses])
        cur.execute(f"SELECT COUNT(*) FROM findings WHERE LOWER(sanction_status) IN ({placeholders})", tuple(s.lower() for s in statuses))
        return cur.fetchone()[0]
    finally:
        con.close()


def count_all_findings() -> int:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM findings")
        return cur.fetchone()[0]
    finally:
        con.close()


def sum_findings_field(field: str) -> int:
    con = _get_connection()
    try:
        cur = con.cursor()
        if field not in ("data_exposure_bytes", "users_affected", "event_count"):
            return 0
        cur.execute(f"SELECT SUM({field}) FROM findings")
        val = cur.fetchone()[0]
        return int(val) if val else 0
    finally:
        con.close()


def top_findings(limit: int = 5) -> List[Finding]:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM findings ORDER BY risk_score DESC LIMIT ?", (limit,))
        return [Finding.model_validate(_row_to_dict(r)) for r in cur.fetchall()]
    finally:
        con.close()


def count_findings_for_scan(scan_id: str) -> int:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM findings WHERE scan_id = ?", (scan_id,))
        return cur.fetchone()[0]
    finally:
        con.close()


def list_findings_for_scan_sorted(scan_id: str) -> List[Finding]:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM findings WHERE scan_id = ? ORDER BY risk_score DESC", (scan_id,))
        return [Finding.model_validate(_row_to_dict(r)) for r in cur.fetchall()]
    finally:
        con.close()


# =============================================================================
# Fingerprint Domains / Extensions
# =============================================================================

def get_fingerprint_domains() -> List[FingerprintDomain]:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM fingerprint_domains ORDER BY id ASC")
        return [FingerprintDomain.model_validate(_row_to_dict(r)) for r in cur.fetchall()]
    finally:
        con.close()


def get_fingerprint_extensions() -> List[FingerprintExtension]:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM fingerprint_extensions ORDER BY id ASC")
        return [FingerprintExtension.model_validate(_row_to_dict(r)) for r in cur.fetchall()]
    finally:
        con.close()


def count_fingerprint_domains() -> int:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM fingerprint_domains")
        return cur.fetchone()[0]
    finally:
        con.close()


def count_fingerprint_extensions() -> int:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM fingerprint_extensions")
        return cur.fetchone()[0]
    finally:
        con.close()


def create_fingerprint_domain(domain: FingerprintDomain) -> FingerprintDomain:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO fingerprint_domains (domain, category, vendor, sanctioned) VALUES (?, ?, ?, ?)",
            (domain.domain, domain.category, domain.vendor, 1 if domain.sanctioned else 0)
        )
        con.commit()
        row_id = cur.lastrowid
        cur.execute("SELECT * FROM fingerprint_domains WHERE id = ?", (row_id,))
        return FingerprintDomain.model_validate(_row_to_dict(cur.fetchone()))
    finally:
        con.close()


def create_fingerprint_extension(ext: FingerprintExtension) -> FingerprintExtension:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO fingerprint_extensions (name, category, vendor, sanctioned) VALUES (?, ?, ?, ?)",
            (ext.name, ext.category, ext.vendor, 1 if ext.sanctioned else 0)
        )
        con.commit()
        row_id = cur.lastrowid
        cur.execute("SELECT * FROM fingerprint_extensions WHERE id = ?", (row_id,))
        return FingerprintExtension.model_validate(_row_to_dict(cur.fetchone()))
    finally:
        con.close()


# =============================================================================
# Agent Investigations
# =============================================================================

def create_agent_investigation(inv: AgentInvestigation) -> AgentInvestigation:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO agent_investigations (finding_id, summary, recommendation, rationale, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                inv.finding_id,
                inv.summary,
                inv.recommendation,
                inv.rationale,
                inv.confidence,
                inv.created_at.isoformat() if hasattr(inv.created_at, "isoformat") else inv.created_at,
            )
        )
        con.commit()
        row_id = cur.lastrowid
        cur.execute("SELECT * FROM agent_investigations WHERE id = ?", (row_id,))
        return AgentInvestigation.model_validate(_row_to_dict(cur.fetchone()))
    finally:
        con.close()


def get_investigations_for_finding(finding_id: str) -> List[AgentInvestigation]:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM agent_investigations WHERE finding_id = ? ORDER BY id DESC", (finding_id,))
        return [AgentInvestigation.model_validate(_row_to_dict(r)) for r in cur.fetchall()]
    finally:
        con.close()


# =============================================================================
# Alert Log
# =============================================================================

def create_alert_log(alert: AlertLog) -> AlertLog:
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO alerts_log (finding_id, channel, sent_at, status) VALUES (?, ?, ?, ?)",
            (
                alert.finding_id,
                alert.channel,
                alert.sent_at.isoformat() if hasattr(alert.sent_at, "isoformat") else alert.sent_at,
                alert.status,
            )
        )
        con.commit()
        row_id = cur.lastrowid
        cur.execute("SELECT * FROM alerts_log WHERE id = ?", (row_id,))
        return AlertLog.model_validate(_row_to_dict(cur.fetchone()))
    finally:
        con.close()
