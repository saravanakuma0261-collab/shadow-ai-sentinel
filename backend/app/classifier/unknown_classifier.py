import re
from typing import Dict, Any, Optional, List, Tuple

AI_KEYWORDS = {
    # High-confidence triggers (weight 0.45)
    "high": [
        "gpt", "llm", "genai", "copilot", "chatgpt", "openai", "claude", "gemini",
        "deepseek", "midjourney", "anthropic", "langchain", "llama", "mistral",
        "embeddings", "completions", "whisper", "dall-e", "stablediffusion",
        "transformer", "neural", "prompt"
    ],
    # Medium-confidence triggers (weight 0.25)
    "medium": [
        "assistant", "bot", "transcribe", "transcription", "summariz", "summarize",
        "paraphrase", "autocomplete", "voicegen", "synth", "synthes", "avatar",
        "copilot", "writer", "codegen", "intellicode", "autocode", "rephrase"
    ],
    # Contextual keywords (weight 0.15)
    "context": [
        "ai", "smart", "magic", "auto", "insight", "generate", "generative", "agent"
    ]
}

HIGH_RISK_PERMISSIONS = [
    "<all_urls>",
    "*://*/*",
    "webRequest",
    "webRequestBlocking",
    "nativeMessaging",
    "clipboardRead",
    "tabs",
    "activeTab",
    "cookies",
    "storage"
]


class UnknownClassifier:
    """
    Lightweight heuristic classifier that analyzes unknown domains and browser extensions
    to detect emerging / uncataloged Shadow AI tools.
    Prioritizes low false negatives (flags aggressively for LLM agent verification).
    """

    def __init__(self):
        pass

    def classify_domain(self, domain: str, path: str = "", query: str = "") -> Dict[str, Any]:
        """
        Analyzes an uncataloged domain and request context to determine if it is likely an AI service.
        """
        text = f"{domain.lower()} {path.lower()} {query.lower()}"
        
        score = 0.0
        detected_signals: List[str] = []

        # 1. High confidence triggers
        for kw in AI_KEYWORDS["high"]:
            if re.search(r'\b' + re.escape(kw) + r'\b', text) or kw in domain.lower():
                score += 0.45
                detected_signals.append(f"High-confidence AI keyword: '{kw}'")
                break

        # 2. Medium confidence triggers
        for kw in AI_KEYWORDS["medium"]:
            if kw in text:
                score += 0.25
                detected_signals.append(f"AI-associated term: '{kw}'")
                break

        # 3. Contextual triggers
        for kw in AI_KEYWORDS["context"]:
            if re.search(r'\b' + re.escape(kw) + r'\b', text) or domain.lower().endswith(f".{kw}") or domain.lower().startswith(f"{kw}."):
                score += 0.20
                detected_signals.append(f"Contextual marker: '{kw}'")
                break

        # 4. AI TLDs (e.g. .ai, .io, .dev with tech prefixes)
        if domain.lower().endswith(".ai"):
            score += 0.30
            detected_signals.append(".ai top-level domain")

        # 5. Common AI API path endpoints
        if any(p in path.lower() for p in ["/v1/chat", "/v1/completions", "/api/generate", "/predict", "/infer", "/agent"]):
            score += 0.35
            detected_signals.append("AI Inference API endpoint pattern")

        confidence = round(min(1.0, max(0.0, score)), 2)
        is_likely_ai = confidence >= 0.35

        # Infer category
        category = "Unclassified AI Tool"
        if any(k in text for k in ["code", "dev", "git"]):
            category = "Suspected Code Assistant"
        elif any(k in text for k in ["meet", "transcribe", "voice", "audio", "call"]):
            category = "Suspected Meeting / Audio Assistant"
        elif any(k in text for k in ["chat", "gpt", "talk", "bot"]):
            category = "Suspected Generative Chat"
        elif any(k in text for k in ["image", "video", "photo", "art"]):
            category = "Suspected Media Generation"
        elif any(k in text for k in ["write", "edit", "grammar", "draft"]):
            category = "Suspected Writing Assistant"

        return {
            "is_likely_ai": is_likely_ai,
            "confidence": confidence,
            "detected_signals": detected_signals,
            "inferred_category": category if is_likely_ai else "Non-AI Service",
        }

    def classify_extension(self, name: str, permissions: List[str] = None) -> Dict[str, Any]:
        """
        Analyzes an uncataloged browser extension to determine if it has AI capabilities or high-risk permissions.
        """
        text = name.lower()
        score = 0.0
        detected_signals: List[str] = []

        for kw in AI_KEYWORDS["high"]:
            if kw in text:
                score += 0.50
                detected_signals.append(f"AI keyword in extension title: '{kw}'")
                break

        for kw in AI_KEYWORDS["medium"] + AI_KEYWORDS["context"]:
            if kw in text:
                score += 0.25
                detected_signals.append(f"Productivity/AI term: '{kw}'")
                break

        # Check permissions
        if permissions:
            risky = [p for p in permissions if p in HIGH_RISK_PERMISSIONS]
            if risky:
                score += 0.20
                detected_signals.append(f"High-risk browser permissions: {', '.join(risky[:3])}")

        confidence = round(min(1.0, max(0.0, score)), 2)
        is_likely_ai = confidence >= 0.35

        return {
            "is_likely_ai": is_likely_ai,
            "confidence": confidence,
            "detected_signals": detected_signals,
            "inferred_category": "Suspected AI Browser Copilot" if is_likely_ai else "Standard Browser Extension",
        }


unknown_classifier = UnknownClassifier()
