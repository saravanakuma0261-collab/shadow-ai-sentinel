import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings
from app.auth.dependencies import require_role

# Force initialization of Supabase SDK before other modules import repository
from app.db import supabase_client  # noqa
from app.db.supabase_client import verify_connection
from app.db import repository
from app.db.models import User, FingerprintDomain, FingerprintExtension
from app.auth.security import get_password_hash
from app.fingerprint.matcher import matcher
from app.auth.routes_auth import router as auth_router
from app.admin.routes_users import router as admin_router
from app.api.routes_scan import router as scan_router
from app.api.routes_findings import router as findings_router
from app.api.routes_agent import router as agent_router
from app.api.routes_history import router as history_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("shadow_ai_sentinel")


def init_supabase_seed():
    """Initializes collections and seeds initial admin user + fingerprints if empty."""
    try:
        # Seed initial admin user if not exists
        admin_count = repository.count_active_admins()
        if admin_count == 0:
            existing_admin = repository.get_user_by_email(settings.ADMIN_EMAIL.lower())
            if not existing_admin:
                admin_user = User(
                    name=settings.ADMIN_NAME,
                    email=settings.ADMIN_EMAIL.lower(),
                    password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                    auth_provider="local",
                    role="admin",
                    is_active=True,
                )
                repository.create_user(admin_user)
                logger.info(f"Initialized seed admin user: {settings.ADMIN_EMAIL}")

        # Seed domain fingerprints if collection is empty
        if repository.count_fingerprint_domains() == 0:
            for item in matcher.domains:
                domain_rec = FingerprintDomain(
                    domain=item["domain"],
                    category=item["category"],
                    vendor=item["vendor"],
                    sanctioned=item.get("sanctioned", False),
                )
                repository.create_fingerprint_domain(domain_rec)
            logger.info(f"Seeded {len(matcher.domains)} domain fingerprints into Supabase.")

        # Seed extension fingerprints if collection is empty
        if repository.count_fingerprint_extensions() == 0:
            for item in matcher.extensions:
                ext_rec = FingerprintExtension(
                    name=item["name"],
                    category=item["category"],
                    vendor=item["vendor"],
                    sanctioned=item.get("sanctioned", False),
                )
                repository.create_fingerprint_extension(ext_rec)
            logger.info(f"Seeded {len(matcher.extensions)} extension fingerprints into Supabase.")

    except Exception as e:
        logger.error(f"Error during Supabase initialization/seeding: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Shadow AI Sentinel Backend...")
    # Verify DB connectivity immediately so we fail fast if env vars are wrong
    verify_connection()
    init_supabase_seed()
    yield
    # Shutdown
    logger.info("Shutting down Shadow AI Sentinel Backend...")


app = FastAPI(
    title="Shadow AI Sentinel API",
    description="Detecting Unauthorized AI Tools and Browser Extensions with Heuristic Risk Scoring and LLM Agent Triage",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Session middleware (for Google OAuth flow state)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:80",
    "http://localhost",
    settings.FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(scan_router)
app.include_router(findings_router)
app.include_router(agent_router)
app.include_router(history_router)

# Direct alias for frontend scan list
from app.api.routes_scan import list_all_scans
from app.schemas import ScanResponse
from typing import List

@app.get("/scans", response_model=List[ScanResponse], tags=["Scanning & Ingestion"])
def get_scans_alias(current_user=Depends(require_role("admin", "analyst", "viewer"))):
    return list_all_scans(current_user=current_user)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "Shadow AI Sentinel API",
        "status": "online",
        "version": "1.0.0",
        "description": "AI-assisted shadow AI discovery, 4-signal heuristic risk scoring, and LLM triage agent."
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
