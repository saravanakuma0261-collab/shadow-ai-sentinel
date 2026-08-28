import logging
from supabase import create_client, Client
from app.config import settings

# ---------------------------------------------------------------------------
# Supabase Client — Security Separation
# ---------------------------------------------------------------------------
# get_supabase()      → Uses SUPABASE_SERVICE_KEY (bypasses RLS).
#                       SERVER-SIDE ONLY. Never expose this client or the key
#                       in any response body, frontend bundle, or client code.
#
# get_supabase_anon() → Uses SUPABASE_ANON_KEY (respects RLS policies).
#                       Safe for operations scoped to authenticated users.
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)

# Supabase client singletons (lazy-initialised)
_supabase_service: Client | None = None
_supabase_anon: Client | None = None

def get_supabase() -> Client:
    """
    Returns the Supabase client initialised with the SERVICE ROLE key.

    ⚠️  SERVER-SIDE ONLY — this client bypasses Row Level Security (RLS).
    Never pass this client, its key, or any response from it directly to
    an end-user or include it in a frontend/client payload.
    Used for: admin operations, seed scripts, background jobs.
    """
    global _supabase_service
    if _supabase_service is None:
        url = settings.SUPABASE_URL
        key = settings.SUPABASE_SERVICE_KEY or settings.supabase_safe_key
        
        if not url or not key:
            logger.warning("SUPABASE_URL or Supabase Key not set. Client will fail.")
            
        try:
            _supabase_service = create_client(url, key)
            logger.info("Supabase client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise e
            
    return _supabase_service

def get_supabase_anon() -> Client:
    """
    Returns the Supabase client initialised with the safe public key.
    Automatically resolves SUPABASE_PUBLISHABLE_KEY (newer projects) or
    falls back to SUPABASE_ANON_KEY (legacy projects). Respects RLS policies.
    """
    global _supabase_anon
    if _supabase_anon is None:
        url = settings.SUPABASE_URL
        key = settings.supabase_safe_key

        if not url or not key:
            logger.warning(
                "SUPABASE_URL or a publishable/anon key is not set. "
                "Set SUPABASE_PUBLISHABLE_KEY (or SUPABASE_ANON_KEY) in your .env."
            )

        try:
            _supabase_anon = create_client(url, key)
            logger.info("Supabase anon/publishable client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase anon/publishable client: {e}")
            raise e

    return _supabase_anon

def verify_connection():
    """Pings the database to ensure environment variables and connection are valid."""
    try:
        client = get_supabase_anon()
        # Simple query to check connectivity (limit 1 to be lightweight)
        res = client.table("users").select("id").limit(1).execute()
        logger.info("Supabase connectivity check passed.")
    except Exception as e:
        logger.error(f"CRITICAL: Failed to connect to Supabase. Check your .env configuration. Error: {e}")
        raise RuntimeError(f"Database connectivity failed: {e}")

def query_recent_scans():
    """
    Example function to query the 'scans' table from the live Supabase schema.
    Uses the anon client to confirm connection.
    Columns queried: id, status, items_scanned, threats_found, started_at, completed_at
    """
    try:
        client = get_supabase_anon()
        response = (
            client.table("scans")
            .select("id, status, items_scanned, threats_found, started_at, completed_at")
            .order("started_at", desc=True)
            .limit(5)
            .execute()
        )
        logger.info(f"Successfully retrieved {len(response.data)} recent scans.")
        return response.data
    except Exception as e:
        logger.error(f"Failed to query recent scans: {e}")
        raise e
