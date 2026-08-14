# Shadow AI Sentinel — Prototype

A lightweight system to **discover**, **classify**, and **risk-score** unauthorized
("Shadow") AI usage inside an organization, using telemetry most orgs already have —
no new network taps, agents, or DLP suite required.

## Why this exists

Existing tools mostly do network monitoring *or* DLP. Neither answers the specific
question security teams increasingly need answered: *which AI tools are our people
actually using, unofficially, and how risky is each one?* This prototype answers that
by correlating two cheap-to-obtain data sources against a small, maintainable
fingerprint database, and producing a ranked, explainable risk score per tool.

## Architecture (this prototype)

```
sample_data/                 <- stand-in for real telemetry exports
  extensions_export.json     <- e.g. Chrome/Edge admin API or MDM export
  network_dns_log.csv        <- e.g. existing proxy / firewall / DNS resolver log

databases/                   <- the "brain": maintained fingerprint DB
  ai_domain_db.json           <- known AI service domains + category + sanctioned flag
  ai_extension_db.json        <- known AI browser extensions + permissions + sanctioned flag

core/
  scanner.py                 <- Module 1+2: discovery + classification + risk scoring
  dashboard.py                <- Module 3: renders reports/risk_report.json -> HTML

reports/
  risk_report.json           <- machine-readable findings (for SIEM/ticketing ingestion)
  dashboard.html              <- human-readable risk dashboard
```

## Run it

```bash
python3 core/scanner.py      # produces reports/risk_report.json
python3 core/dashboard.py    # produces reports/dashboard.html
```

No third-party dependencies — pure Python 3 standard library, so it runs anywhere,
including an air-gapped security lab.

## Risk scoring model

Each discovered tool gets a 0–100 heuristic score from four weighted signals:

| Signal | Network-log findings | Extension findings |
|---|---|---|
| Category sensitivity | e.g. code assistants / meeting transcription score higher than image generation | fixed base weight |
| Sanctioned status | +25 if NOT on the org's approved list | +25 if NOT approved |
| Exposure volume | bytes uploaded to the service (proxy for data leaving the org) | sum of requested permission risk (e.g. "read/write all sites") |
| Spread | number of interaction events | number of distinct users running the extension |

Score bands: **0–24 Low · 25–49 Medium · 50–74 High · 75–100 Critical**

The formula lives in `core/scanner.py` (`analyze_network_log`, `analyze_extensions`) —
every weight is a named constant so a security team can tune it to their own risk
appetite without touching the discovery logic.

## Extending this to production data

- Replace `sample_data/network_dns_log.csv` with a real proxy/DNS export (Squid,
  Zscaler, Cisco Umbrella, or even router-level DNS logs all export similar columns).
- Replace `sample_data/extensions_export.json` with a real Chrome/Edge Enterprise
  admin API pull (`chrome.management` API via Google Admin SDK, or an MDM's
  extension inventory export).
- Grow `databases/ai_domain_db.json` and `ai_extension_db.json` over time — this is
  the main maintenance burden, and is intentionally kept as flat, readable JSON so
  a security analyst can add entries without touching code.
- `reports/risk_report.json` is designed to be ingestible by a SIEM or ticketing
  system as a scheduled job (e.g. nightly cron -> alert on any new Critical finding).

## Known limitations (be upfront about these in a report/demo)

- Fingerprint-based discovery misses AI tools not yet in the database — it is a
  detection *floor*, not a guarantee, and the DB needs ongoing curation.
- Domain-only network matching can be evaded by proxies/VPNs; a production version
  should also watch for TLS SNI patterns and known API endpoint paths.
- Risk weights are heuristic starting points, not a validated actuarial model —
  tune against your own incident history if available.
