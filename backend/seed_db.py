import os
import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Make sure supabase_client initializes before other imports
from app.db import supabase_client  # noqa
from app.config import settings
from app.db import repository
from app.db.models import User, FingerprintDomain, FingerprintExtension
from app.auth.security import get_password_hash
from app.fingerprint.matcher import matcher


def seed():
    print("[INFO] Initializing Supabase seed process...")

    try:
        # Check / Create Admin
        admin_email = settings.ADMIN_EMAIL.lower().strip()
        admin_user = repository.get_user_by_email(admin_email)

        if not admin_user:
            admin_user = User(
                name=settings.ADMIN_NAME,
                email=admin_email,
                password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                auth_provider="local",
                role="admin",
                is_active=True,
            )
            repository.create_user(admin_user)
            print(f"[SUCCESS] Admin user created: {admin_email} (Password: {settings.ADMIN_PASSWORD})")
        else:
            print(f"[INFO] Admin user already exists: {admin_email}")

        # Seed AI Threat Intelligence Fingerprints (Real-World Signatures)

        # Seed Domains
        dom_count = repository.count_fingerprint_domains()
        if dom_count == 0:
            for item in matcher.domains:
                rec = FingerprintDomain(
                    domain=item["domain"],
                    category=item["category"],
                    vendor=item["vendor"],
                    sanctioned=item.get("sanctioned", False),
                )
                repository.create_fingerprint_domain(rec)
            print(f"[SUCCESS] Seeded {len(matcher.domains)} AI domain fingerprints.")
        else:
            print(f"[INFO] {dom_count} domain fingerprints already present in Supabase.")

        # Seed Extensions
        ext_count = repository.count_fingerprint_extensions()
        if ext_count == 0:
            for item in matcher.extensions:
                rec = FingerprintExtension(
                    name=item["name"],
                    category=item["category"],
                    vendor=item["vendor"],
                    sanctioned=item.get("sanctioned", False),
                )
                repository.create_fingerprint_extension(rec)
            print(f"[SUCCESS] Seeded {len(matcher.extensions)} AI extension fingerprints.")
        else:
            print(f"[INFO] {ext_count} extension fingerprints already present in Supabase.")

        print("[SUCCESS] Supabase seeding completed successfully.")

    except Exception as e:
        print(f"[ERROR] Error during seeding: {e}")
        sys.exit(1)


if __name__ == "__main__":
    seed()
