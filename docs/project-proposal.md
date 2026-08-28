# Project Proposal: Shadow AI Sentinel

**System Version**: 1.0.0-PROD  
**Author**: Traceforce Cybersecurity Operations Team  
**Date**: August 24, 2026  
**Target Environment**: Enterprise Hybrid Cloud (Docker, Kubernetes, AWS/GCP, Local Dev)

---

## 1. Executive Summary & Problem Statement

Modern enterprises face an unprecedented security blindspot: the unauthorized and unmonitored adoption of Generative AI tools and browser extensions by employees—collectively termed **Shadow AI**.

While these tools augment workforce productivity, they present severe enterprise vulnerabilities:
- **Data Exfiltration & Confidentiality Leaks**: Proprietary code, PII, financial spreadsheets, and trade secrets pasted into third-party AI interfaces lacking enterprise data protection agreements.
- **Unvetted Browser Extensions**: AI writing assistants and prompt helpers requesting aggressive browser permissions (`<all_urls>`, `webRequest`, `clipboardRead`, `storage`, `cookies`), intercepting internal SaaS workflows.
- **Regulatory Non-Compliance**: Violation of GDPR, HIPAA, SOC 2, and EU AI Act mandates due to untracked algorithmic processing of protected data.
- **SecOps Fatigue**: Overwhelmed security operations teams unable to manually triage thousands of DNS queries and endpoint extension inventories daily.

**Shadow AI Sentinel** solves this challenge by providing continuous asset discovery, explainable multi-signal heuristic risk scoring, strict role-based access control (RBAC), and autonomous LLM-agent triage.

---

## 2. System Architecture

Shadow AI Sentinel is architected as an enterprise-grade decoupled system:

```
+-----------------------------------------------------------------------------------+
|                            VITE + REACT 18 FRONTEND                               |
|  - Dark Cyber Glassmorphism UI (Dashboard, Findings Inventory, Triage Reports)   |
|  - Dynamic Role-Based Route Protection (Admin, Analyst, Viewer)                   |
|  - Real-time Risk Distribution & Explainable Signal Breakdown Visualizations     |
+------------------------------------------+----------------------------------------+
                                           |  HTTPS / JWT Bearer Tokens
                                           v
+-----------------------------------------------------------------------------------+
|                            FASTAPI PYTHON BACKEND                                 |
|  - RBAC Middleware & Security Dependencies (Strict 403 enforcement)               |
|  - Telemetry Ingestion Engine (Proxy DNS Logs, Browser Extension Audits)          |
|  - AI Fingerprint Matcher (36+ Known Domains, 16+ Browser Extensions)             |
|  - Unknown Entity Classifier (N-Gram & Heuristic Feature Scorer)                  |
|  - 4-Signal Explainable Risk Scoring Engine                                       |
|  - Anthropic Claude Autonomous LLM Investigator Agent                             |
|  - Multi-Channel Alerts Dispatcher (Email & Webhook Notifications)               |
+------------------------------------------+----------------------------------------+
                                           |  Supabase Python SDK
                                           v
+-----------------------------------------------------------------------------------+
|                        DATABASE & PERSISTENCE LAYER                               |
|  - Supabase (PostgreSQL)                                                          |
+-----------------------------------------------------------------------------------+
```

---

## 3. Risk Engine Formulation (AI-Assisted Weighted Heuristic Model)

To guarantee auditability, governance compliance, and zero "black-box" decision opacity, the risk scoring engine calculates a deterministic **Risk Score ($R \in [0, 100]$)** across four orthogonal security vectors:

$$R = \left( w_{\text{cat}} \cdot S_{\text{cat}} \right) + \left( w_{\text{sanc}} \cdot S_{\text{sanc}} \right) + \left( w_{\text{exp}} \cdot S_{\text{exp}} \right) + \left( w_{\text{use}} \cdot S_{\text{use}} \right)$$

### Signal Weights and Definitions

1. **Category Sensitivity ($S_{\text{cat}}$, Weight $w_{\text{cat}} = 0.35$)**:
   - Scores the innate data-ingestion risk of the AI class.
   - Autonomous Screen Scrapers / Prompt Injectors: $100$
   - Code Assistants & Terminal AI: $85$
   - LLM Chat & Generative Text: $75$
   - Audio Transcription / Meeting AI: $70$
   - Image & Multimodal Generation: $50$
   - Translation / Spellcheck: $30$

2. **Sanction Status ($S_{\text{sanc}}$, Weight $w_{\text{sanc}} = 0.25$)**:
   - Unsanctioned / Blacklisted AI: $100$
   - Unknown / Unreviewed Entity: $70$
   - Sanctioned & Approved Corporate AI: $10$

3. **Data Exposure Potential ($S_{\text{exp}}$, Weight $w_{\text{exp}} = 0.25$)**:
   - Evaluates outbound payload volume and extension permissions.
   - High Exposure ($>10 \text{ MB}$ or `<all_urls>` / `clipboardRead` permissions): $100$
   - Medium Exposure ($1 - 10 \text{ MB}$ or `activeTab` / `storage`): $60$
   - Low Exposure ($<1 \text{ MB}$ or benign read-only permissions): $20$

4. **Usage Spread & Frequency ($S_{\text{use}}$, Weight $w_{\text{use}} = 0.15$)**:
   - Calculates organizational blast radius based on distinct user/endpoint adoption.
   - Formula: $\min\left(100, 20 \cdot \log_2(\text{event\_count} + 1) + 10 \cdot \text{users\_affected}\right)$

### Risk Tiers
- **Critical Risk ($R \ge 80$)**: Immediate block and incident ticket generation.
- **High Risk ($65 \le R < 80$)**: Rapid SecOps escalation and policy enforcement.
- **Medium Risk ($40 \le R < 65$)**: Active monitoring and DLP inspection.
- **Low Risk ($R < 40$)**: Normal logging and periodic re-evaluation.

---

## 4. Autonomous LLM Investigator Agent Workflow

When a finding is flagged for deep triage, the backend invokes the **Anthropic Claude Investigator Agent**:
1. **Context Extraction**: Gathers full telemetry—query counts, transferred payload sizes, extracted browser permissions, matched signatures, and heuristic breakdown.
2. **Threat Assessment**: Evaluates compliance risk against standard frameworks (NIST AI RMF, ISO 42001, SOC 2).
3. **Structured Triage Verdict**: Returns a structured remediation response:
   - **Recommendation**: `BLOCK`, `MONITOR`, or `ESCALATE`
   - **Confidence Score**: Quantitative model certainty ($0.0 - 1.0$)
   - **Investigative Rationale**: Step-by-step reasoning for the security verdict
   - **Prescribed Remediation Actions**: Ordered list of actionable SecOps steps (e.g. firewall domain block, Chrome enterprise policy push, employee awareness notice).

---

## 5. Role-Based Access Control (RBAC) Specification

| Capability | Admin | Analyst | Viewer |
| :--- | :---: | :---: | :---: |
| View Dashboard & Metrics | ✅ | ✅ | ✅ |
| View Findings & Details | ✅ | ✅ | ✅ |
| View Scan History | ✅ | ✅ | ✅ |
| Ingest Network & Extension Logs (`POST /scan`) | ✅ | ✅ | ❌ (403) |
| Trigger LLM Agent Triage (`POST /findings/:id/investigate`) | ✅ | ✅ | ❌ (403) |
| Manage Users & Mutate Roles (`GET/PATCH /admin/users`) | ✅ | ❌ (403) | ❌ (403) |
| Activate / Deactivate Accounts | ✅ | ❌ (403) | ❌ (403) |

---

## 6. Verification and Acceptance Criteria

1. **Backend Test Suite**: 100% pass on all unit and integration tests covering JWT creation, strict RBAC authorization, matcher accuracy, heuristic scoring boundaries, and admin endpoints.
2. **Zero-Config Developer Experience**: Out-of-the-box Supabase integration with auto-seeding allows running the platform locally in seconds.
3. **Turnkey Multi-Container Orchestration**: Production-ready `docker-compose.yml` deploying FastAPI and React Vite.
