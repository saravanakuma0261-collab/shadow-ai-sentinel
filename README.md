# Shadow AI Sentinel 🛡️⚡

> **Enterprise Cybersecurity Threat Discovery, Explainable Risk-Scoring, and LLM-Agent Triage Platform for Unsanctioned AI Services and Browser Extensions.**

[![Backend CI](https://github.com/traceforce/shadow-ai-sentinel/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/traceforce/shadow-ai-sentinel/actions)
[![Frontend CI](https://github.com/traceforce/shadow-ai-sentinel/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/traceforce/shadow-ai-sentinel/actions)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.13-blue.svg)](https://www.python.org/)
[![React Version](https://img.shields.io/badge/react-18.3.1-61dafb.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688.svg)](https://fastapi.tiangolo.com/)

---

## 📖 Overview

**Shadow AI Sentinel** empowers Security Operations (SecOps), CISO teams, and compliance officers to continuously detect, classify, and mitigate unvetted AI tools across the organization. It combines:

1. **Ingestion & Telemetry Parser**: Ingests enterprise network/DNS proxy logs (CSV/JSON) and browser extension inventory audits (JSON).
2. **Curated Fingerprint Engine**: High-fidelity signatures for 36+ known AI domains (ChatGPT, Claude, Gemini, DeepSeek, Otter, Jasper, Groq, etc.) and 16+ browser extensions.
3. **Unknown Entity Classifier**: Heuristic and n-gram keyword classification for newly spawned AI platforms.
4. **4-Signal Explainable Heuristic Risk Engine**: Formulates transparent, deterministic risk scores based on *Category Sensitivity (35%)*, *Sanction Status (25%)*, *Data Exposure (25%)*, and *Usage Spread (15%)*.
5. **Autonomous LLM Investigator Agent**: Powered by Anthropic Claude to deliver in-depth threat synthesis, confidence ratings, and prescriptive SecOps remediation steps (`BLOCK`, `MONITOR`, `ESCALATE`).
6. **Strict Role-Based Access Control (RBAC)**: Backend-enforced authorization for `Admin`, `Analyst`, and `Viewer` roles.
7. **Cyber Glassmorphism UI**: High-density React interface with live risk distribution charts, filterable tables, and instant triage reports.

---

## 🏗️ Architecture & Technology Stack

```
shadow-ai-sentinel/
├── backend/
│   ├── app/
│   │   ├── admin/          # Admin-only user mutation endpoints
│   │   ├── agent/          # Anthropic Claude investigator agent
│   │   ├── alerts/         # Email & webhook alert dispatchers
│   │   ├── api/            # Scan, findings, and history routes
│   │   ├── auth/           # JWT, Bcrypt, RBAC dependencies, Google OAuth
│   │   ├── classifier/     # Unknown AI entity heuristic classifier
│   │   ├── db/             # Supabase client, Pydantic models, Repository pattern
│   │   ├── fingerprint/    # Known AI domain & extension signature DBs
│   │   ├── ingestion/      # DNS proxy & browser extension parsers
│   │   ├── scoring/        # 4-signal explainable heuristic risk engine
│   │   ├── config.py       # Pydantic v2 settings loader
│   │   ├── main.py         # FastAPI application entrypoint
│   │   └── schemas.py      # Pydantic request/response schemas
│   ├── sample_data/        # Synthetic enterprise audit logs
│   ├── tests/              # Pytest test suite (15 unit/integration tests)
│   ├── seed_db.py          # Supabase data initialization & admin seeding
│   ├── requirements.txt    # Python backend dependencies
│   └── Dockerfile          # Backend container image
├── frontend/
│   ├── src/
│   │   ├── api/            # Axios client with JWT & error interceptors
│   │   ├── auth/           # AuthContext, ProtectedRoute, RoleRoute
│   │   ├── components/     # NavBar, RiskBadge, RiskDistributionChart, FindingsTable, ScanModal
│   │   ├── pages/          # Dashboard, Findings, FindingDetail, ScanHistory, UserManagement, Login
│   │   ├── styles/         # Modern cybersecurity glassmorphic design system
│   │   ├── App.jsx         # Route tree and layout
│   │   └── main.jsx        # React root entrypoint
│   ├── package.json        # Frontend dependencies (React, Vite, Lucide)
│   ├── vite.config.js      # Vite build & proxy configuration
│   ├── nginx.conf          # Production container reverse proxy config
│   └── Dockerfile          # Multi-stage production frontend image
├── docs/
│   └── project-proposal.md # Formal architecture & mathematical specification
├── docker-compose.yml      # Multi-container orchestration (Backend, Frontend)
└── README.md
```

---

## 🚀 Quickstart Guide

### Option 1: Full-Stack Docker Compose (Recommended for Production / Staging)

> **Important**: You must set up Supabase before running the application.

#### Supabase Setup
1. Go to [Supabase](https://database.new) and create a project.
2. Navigate to the SQL Editor and run the SQL script found at `backend/app/db/init_supabase.sql` to create all the required tables.
3. Go to **Project Settings -> API** to get your **Project URL** and **Service Role Key**.
4. Update `backend/.env` with these values.

Run the backend and frontend with a single command:

```bash
docker-compose up --build
```

- **Frontend Console**: [http://localhost:5173](http://localhost:5173)
- **Backend API & Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option 2: Local Development

If you prefer to run outside of Docker:

#### 1. Backend Setup

```bash
cd backend

# Create & activate virtual environment (Python 3.11+ or 3.13)
py -3.13 -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed database and demo users
python seed_db.py

# Start FastAPI dev server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧹 Reset Local Environment

If you need to reset the environment (e.g. you have old tokens from a previous database migration), run the reset script:

**macOS/Linux**:
```bash
./backend/scripts/reset_local_env.sh
```

**Windows**:
```powershell
.\backend\scripts\reset_local_env.ps1
```

> **Note**: Supabase uses UUID strings for document IDs. If you see authentication errors, clear your browser's `localStorage`.

---

## 🔐 Default Demo Accounts

The database seed script automatically provisions three role-tailored accounts for testing:

| Role | Email | Password | Privileges |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@enterprise.com` | `AdminSecure2026!` | Full access, user management, role mutation, scanning, agent triage |
| **Analyst** | `analyst@enterprise.com` | `AnalystPass2026!` | Telemetry log ingestion, scan execution, LLM agent triage |
| **Viewer** | `viewer@enterprise.com` | `ViewerPass2026!` | Read-only access to dashboard, findings, and scan history |

*(You can also use the 1-click **Instant Demo Login** buttons directly on the Login page!)*

---

## 🧪 Running Automated Tests

Run the full pytest suite covering authentication, RBAC boundaries, fingerprint matching, and risk scoring:

```bash
cd backend
.venv\Scripts\pytest -v
```

Output:
```text
tests/test_api.py::TestAPI::test_01_auth_login_and_jwt_role PASSED
tests/test_api.py::TestAPI::test_02_rbac_viewer_blocked_from_scan PASSED
tests/test_api.py::TestAPI::test_03_rbac_analyst_can_trigger_scan PASSED
tests/test_api.py::TestAPI::test_04_get_findings_accessible_by_viewer PASSED
tests/test_api.py::TestAPI::test_05_investigate_finding_analyst PASSED
tests/test_api.py::TestAPI::test_06_admin_user_management_access PASSED
tests/test_api.py::TestAPI::test_07_admin_change_user_role PASSED
tests/test_matcher.py::TestMatcher::test_domain_exact_match PASSED
tests/test_matcher.py::TestMatcher::test_domain_normalization PASSED
tests/test_matcher.py::TestMatcher::test_domain_subdomain_match PASSED
tests/test_matcher.py::TestMatcher::test_domain_unknown PASSED
tests/test_matcher.py::TestMatcher::test_extension_matching PASSED
tests/test_risk_engine.py::TestRiskEngine::test_risk_score_calculation_critical PASSED
tests/test_risk_engine.py::TestRiskEngine::test_risk_score_calculation_low_sanctioned PASSED
tests/test_risk_engine.py::TestRiskEngine::test_risk_tier_boundaries PASSED

============================= 15 passed in 2.71s ==============================
```

Frontend production bundle verification:
```bash
cd frontend
npm run build
```

---

## ⚙️ Environment Configuration (`.env`)

Copy `backend/.env.example` to `backend/.env` to configure external integrations:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `SUPABASE_URL` | Your Supabase Project URL | `https://your-project.supabase.co` |
| `SUPABASE_SERVICE_KEY` | Supabase Service Role Key | `your-service-role-key` |
| `SECRET_KEY` | JWT Signing Secret | `shadow_ai_sentinel_super_secret_jwt_key_2026...` |
| `ADMIN_EMAIL` | Initial Admin Email | `admin@enterprise.com` |
| `ADMIN_PASSWORD` | Initial Admin Password | `AdminSecure2026!` |
| `ANTHROPIC_API_KEY` | Anthropic API Key for LLM Agent | `""` (Falls back to deterministic agent emulator) |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | `""` (Falls back to demo flow if not provided) |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | `""` |
| `ENABLE_EMAIL_ALERTS` | Enable SMTP Critical Alerts | `False` |

---

## 🛡️ Key Security Features

- **Strict RBAC Enforcement**: Roles are embedded directly in the cryptographically signed JWT payload and verified server-side on every request via FastAPI dependencies (`require_role(...)`).
- **Zero Raw Secret Logging**: Password reset tokens are generated using cryptographically secure PRNG (`secrets.token_urlsafe`) and stored as SHA-256 hashes in the database.
- **Fail-Safe LLM Integration**: The Anthropic Claude Investigator Agent includes built-in timeout handling, structured schema enforcement, and an intelligent offline deterministic fallback so scans never fail if API keys are absent.

---

## 📄 License & Attribution

Developed for enterprise cybersecurity defense and AI governance. Built with modern FastAPI and React.
