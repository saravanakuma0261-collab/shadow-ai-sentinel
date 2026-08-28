"""
Shadow AI Sentinel - Core Engine
=================================
Lightweight discovery, classification, and risk-assessment engine for
unauthorized ("Shadow") AI usage across two low-friction telemetry sources:

  1. Browser extension inventories  (e.g. pulled from Chrome/Edge admin API,
     an MDM tool, or a local browser-policy export)
  2. Network/proxy/DNS logs         (e.g. pulled from an existing proxy,
     firewall, or DNS resolver - no new network taps required)

Design goal: correlate against a small, maintainable fingerprint database
instead of deep packet inspection or a full DLP stack, so the system stays
"lightweight" and deployable without new infrastructure.

Usage:
    python scanner.py
"""
import json
import csv
import os
from collections import defaultdict
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "databases")
DATA_DIR = os.path.join(BASE_DIR, "sample_data")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

DOMAIN_DB_PATH = os.path.join(DB_DIR, "ai_domain_db.json")
EXT_DB_PATH = os.path.join(DB_DIR, "ai_extension_db.json")
EXT_EXPORT_PATH = os.path.join(DATA_DIR, "extensions_export.json")
DNS_LOG_PATH = os.path.join(DATA_DIR, "network_dns_log.csv")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def risk_level(score):
    if score >= 75:
        return "Critical"
    if score >= 50:
        return "High"
    if score >= 25:
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# Module 1: Network-log based discovery + classification
# ---------------------------------------------------------------------------
def analyze_network_log(domain_db):
    domain_index = {d["domain"]: d for d in domain_db["domains"]}
    weights = domain_db["_meta"]["category_sensitivity_weight"]

    hits = defaultdict(lambda: {"events": [], "users": set(), "bytes_up": 0})

    with open(DNS_LOG_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            domain = row["domain"]
            if domain in domain_index:
                bucket = hits[domain]
                bucket["events"].append(row)
                bucket["users"].add(row["user"])
                bucket["bytes_up"] += int(row["bytes_uploaded"])

    findings = []
    for domain, bucket in hits.items():
        meta = domain_index[domain]
        category = meta["category"]
        base = weights.get(category, 15)
        sanction_penalty = 0 if meta["sanctioned"] else 25
        volume_score = min(25, bucket["bytes_up"] / 100000)  # 100KB -> 1pt
        frequency_score = min(20, len(bucket["events"]) * 4)
        score = min(100, round(base + sanction_penalty + volume_score + frequency_score, 1))

        findings.append({
            "source": "network_log",
            "service": meta["service"],
            "vendor": meta["vendor"],
            "domain": domain,
            "category": category,
            "sanctioned": meta["sanctioned"],
            "affected_users": sorted(bucket["users"]),
            "event_count": len(bucket["events"]),
            "total_bytes_uploaded": bucket["bytes_up"],
            "risk_score": score,
            "risk_level": risk_level(score),
        })
    return findings


# ---------------------------------------------------------------------------
# Module 2: Browser-extension based discovery + classification
# ---------------------------------------------------------------------------
def analyze_extensions(ext_db):
    ext_index = {e["extension_id"]: e for e in ext_db["extensions"]}
    perm_weights = ext_db["_meta"]["permission_risk_weight"]

    export = load_json(EXT_EXPORT_PATH)
    hits = defaultdict(lambda: {"users": set(), "devices": set()})

    for row in export:
        ext_id = row["extension_id"]
        if ext_id in ext_index:
            bucket = hits[ext_id]
            bucket["users"].add(row["user"])
            bucket["devices"].add(row["device"])

    findings = []
    for ext_id, bucket in hits.items():
        meta = ext_index[ext_id]
        if meta["category"] == "non_ai_utility":
            continue  # control entry, not an AI tool
        base = 15
        sanction_penalty = 0 if meta["sanctioned"] else 25
        permission_score = min(40, sum(perm_weights.get(p, 0) for p in meta["permissions"]))
        spread_score = min(15, len(bucket["users"]) * 5)
        score = min(100, round(base + sanction_penalty + permission_score + spread_score, 1))

        findings.append({
            "source": "browser_extension",
            "service": meta["name"],
            "vendor": meta["publisher"],
            "extension_id": ext_id,
            "category": meta["category"],
            "sanctioned": meta["sanctioned"],
            "permissions": meta["permissions"],
            "affected_users": sorted(bucket["users"]),
            "affected_devices": sorted(bucket["devices"]),
            "risk_score": score,
            "risk_level": risk_level(score),
        })
    return findings


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------
def build_report():
    domain_db = load_json(DOMAIN_DB_PATH)
    ext_db = load_json(EXT_DB_PATH)

    network_findings = analyze_network_log(domain_db)
    extension_findings = analyze_extensions(ext_db)
    all_findings = network_findings + extension_findings
    all_findings.sort(key=lambda x: x["risk_score"], reverse=True)

    unsanctioned = [f for f in all_findings if not f["sanctioned"]]
    all_users = set()
    for f in all_findings:
        all_users.update(f["affected_users"])

    level_counts = defaultdict(int)
    for f in all_findings:
        level_counts[f["risk_level"]] += 1

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_tools_discovered": len(all_findings),
            "unsanctioned_tools_discovered": len(unsanctioned),
            "distinct_users_involved": len(all_users),
            "risk_level_breakdown": dict(level_counts),
        },
        "findings": all_findings,
    }

    os.makedirs(REPORT_DIR, exist_ok=True)
    out_path = os.path.join(REPORT_DIR, "risk_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report, out_path


if __name__ == "__main__":
    report, out_path = build_report()
    print(f"Discovered {report['summary']['total_tools_discovered']} AI tools "
          f"({report['summary']['unsanctioned_tools_discovered']} unsanctioned) "
          f"across {report['summary']['distinct_users_involved']} users.")
    print(f"Report written to: {out_path}")
