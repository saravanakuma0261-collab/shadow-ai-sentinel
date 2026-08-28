import csv
import io
import json
import logging
from collections import defaultdict
from typing import List, Dict, Any, Tuple
from app.fingerprint.matcher import matcher
from app.classifier.unknown_classifier import unknown_classifier
from app.scoring.risk_engine import risk_engine

logger = logging.getLogger(__name__)


def parse_network_logs(content: str) -> List[Dict[str, Any]]:
    """
    Parses network/proxy logs in CSV or JSON format.
    Aggregates events by domain to calculate total exposure, affected users, and risk scores.
    """
    cleaned_content = content.strip()
    records: List[Dict[str, Any]] = []

    if cleaned_content.startswith("[") or cleaned_content.startswith("{"):
        # JSON format
        try:
            data = json.loads(cleaned_content)
            if isinstance(data, dict) and "logs" in data:
                records = data["logs"]
            elif isinstance(data, list):
                records = data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON logs: {e}")
            return []
    else:
        # CSV format
        reader = csv.DictReader(io.StringIO(cleaned_content))
        for row in reader:
            records.append(row)

    # Domain Aggregator
    # Key: normalized_domain -> dict of aggregated stats
    aggregated: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "domain": "",
        "bytes_sent": 0,
        "bytes_received": 0,
        "users": set(),
        "event_count": 0,
        "sample_paths": [],
    })

    for row in records:
        raw_domain = row.get("domain") or row.get("host") or row.get("url") or ""
        if not raw_domain:
            continue
        
        domain = matcher.normalize_domain(raw_domain)
        if not domain:
            continue

        try:
            b_sent = int(row.get("bytes_sent") or row.get("bytes_out") or 0)
        except (ValueError, TypeError):
            b_sent = 0

        try:
            b_recv = int(row.get("bytes_received") or row.get("bytes_in") or 0)
        except (ValueError, TypeError):
            b_recv = 0

        user = row.get("user_email") or row.get("user") or row.get("client_ip") or "unknown_user"
        path = row.get("path") or row.get("uri") or ""

        agg = aggregated[domain]
        agg["domain"] = domain
        agg["bytes_sent"] += b_sent
        agg["bytes_received"] += b_recv
        agg["users"].add(user)
        agg["event_count"] += 1
        if path and len(agg["sample_paths"]) < 5:
            agg["sample_paths"].append(path)

    # Now evaluate each domain for Shadow AI detection
    findings_data: List[Dict[str, Any]] = []

    for domain, stats in aggregated.items():
        total_bytes = stats["bytes_sent"] + stats["bytes_received"]
        users_count = len(stats["users"])
        event_count = stats["event_count"]

        # 1. Check Fingerprint DB
        fp_match = matcher.match_domain(domain)

        if fp_match:
            category = fp_match.get("category", "Generative AI")
            vendor = fp_match.get("vendor", "Unknown Vendor")
            is_sanctioned = fp_match.get("sanctioned", False)
            sanction_status = "sanctioned" if is_sanctioned else "unsanctioned"

            score, tier, breakdown = risk_engine.calculate(
                category=category,
                sanction_status=sanction_status,
                data_exposure_bytes=total_bytes,
                users_affected=users_count,
                event_count=event_count,
            )

            findings_data.append({
                "entity_type": "domain",
                "entity_value": domain,
                "category": category,
                "vendor": vendor,
                "sanction_status": sanction_status,
                "data_exposure_bytes": total_bytes,
                "users_affected": users_count,
                "event_count": event_count,
                "risk_score": score,
                "risk_tier": tier,
                "breakdown": breakdown,
            })
        else:
            # 2. Run Unknown Classifier
            sample_path = stats["sample_paths"][0] if stats["sample_paths"] else ""
            classification = unknown_classifier.classify_domain(domain, path=sample_path)

            if classification["is_likely_ai"]:
                category = classification["inferred_category"]
                vendor = "Uncataloged AI Vendor"
                sanction_status = "unknown"

                score, tier, breakdown = risk_engine.calculate(
                    category=category,
                    sanction_status=sanction_status,
                    data_exposure_bytes=total_bytes,
                    users_affected=users_count,
                    event_count=event_count,
                )

                findings_data.append({
                    "entity_type": "domain",
                    "entity_value": domain,
                    "category": category,
                    "vendor": vendor,
                    "sanction_status": sanction_status,
                    "data_exposure_bytes": total_bytes,
                    "users_affected": users_count,
                    "event_count": event_count,
                    "risk_score": score,
                    "risk_tier": tier,
                    "breakdown": breakdown,
                })

    return findings_data
