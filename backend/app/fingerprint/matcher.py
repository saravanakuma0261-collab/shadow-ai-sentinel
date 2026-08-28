import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

CURRENT_DIR = Path(__file__).resolve().parent
DOMAIN_DB_PATH = CURRENT_DIR / "ai_domain_db.json"
EXTENSION_DB_PATH = CURRENT_DIR / "ai_extension_db.json"


class FingerprintMatcher:
    def __init__(self):
        self.domains: List[Dict[str, Any]] = []
        self.extensions: List[Dict[str, Any]] = []
        self._load_databases()

    def _load_databases(self):
        """Loads domain and extension fingerprint definitions from JSON files."""
        if DOMAIN_DB_PATH.exists():
            with open(DOMAIN_DB_PATH, "r", encoding="utf-8") as f:
                self.domains = json.load(f)
        
        if EXTENSION_DB_PATH.exists():
            with open(EXTENSION_DB_PATH, "r", encoding="utf-8") as f:
                self.extensions = json.load(f)

    @staticmethod
    def normalize_domain(raw_domain: str) -> str:
        """Cleans and extracts the hostname from URLs or raw domain inputs."""
        d = raw_domain.lower().strip()
        if "://" in d:
            d = d.split("://", 1)[1]
        if "/" in d:
            d = d.split("/", 1)[0]
        if ":" in d:
            d = d.split(":", 1)[0]
        if d.startswith("www."):
            d = d[4:]
        return d

    def match_domain(self, raw_domain: str) -> Optional[Dict[str, Any]]:
        """
        Matches a domain or URL against the AI domain fingerprint database.
        Checks exact matches and root/subdomain suffixes (e.g. api.openai.com -> openai.com).
        """
        cleaned = self.normalize_domain(raw_domain)
        if not cleaned:
            return None

        # 1. Exact match
        for entry in self.domains:
            fp_domain = self.normalize_domain(entry["domain"])
            if cleaned == fp_domain:
                return entry

        # 2. Subdomain / suffix match (e.g. "api.openai.com" ends with ".openai.com")
        for entry in self.domains:
            fp_domain = self.normalize_domain(entry["domain"])
            if cleaned.endswith("." + fp_domain):
                return entry

        # 3. Path-specific match (e.g. github.com/copilot, notion.so/product/ai)
        raw_lower = raw_domain.lower().strip()
        for entry in self.domains:
            if "/" in entry["domain"]:
                if entry["domain"].lower() in raw_lower:
                    return entry

        return None

    def match_extension(self, raw_name: str) -> Optional[Dict[str, Any]]:
        """
        Matches an extension name or ID against known AI browser extensions.
        Checks normalized substring matches and keyword tokens.
        """
        if not raw_name:
            return None
        
        name_lower = raw_name.lower().strip()
        
        # 1. Exact or strong substring match
        for entry in self.extensions:
            fp_name = entry["name"].lower()
            if fp_name in name_lower or name_lower in fp_name:
                return entry
            
            # Split keywords
            keywords = [w for w in fp_name.split() if len(w) > 3 and w not in {"extension", "chrome", "assistant", "for", "the"}]
            if any(kw in name_lower for kw in keywords):
                return entry

        return None


matcher = FingerprintMatcher()
