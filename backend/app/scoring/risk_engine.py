import math
from typing import Dict, Any, Tuple
from app.config import settings

# Sensitivity baseline mapping (0.0 to 1.0 scale)
CATEGORY_SENSITIVITY_MAP = {
    "code assistant": 0.95,
    "ai code editor": 0.95,
    "code completion ai": 0.90,
    "meeting assistant & transcription": 0.90,
    "meeting transcriber": 0.90,
    "generative chat & code llm": 0.88,
    "generative chat & llm api": 0.85,
    "generative chat": 0.80,
    "web automation & scraping ai": 0.85,
    "ai workspace & notes": 0.75,
    "prompt management extension": 0.75,
    "voice & audio synthesis": 0.70,
    "writing assistant": 0.65,
    "writing & grammar assistant": 0.65,
    "paraphrasing & writing ai": 0.65,
    "marketing & content ai": 0.60,
    "search & research ai": 0.55,
    "image generation": 0.50,
    "video generation & editing": 0.50,
    "model hub & ml hosting": 0.45,
    "cloud ml inference": 0.45,
    "default": 0.60,
}

SANCTION_STATUS_SCORES = {
    "unsanctioned": 1.0,
    "unknown": 0.70,
    "sanctioned": 0.10,
}


class RiskScoringEngine:
    """
    AI-assisted risk classification using a weighted heuristic model.
    Evaluates 4 transparent and explainable signals to calculate a deterministic risk score (0-100).
    """

    def __init__(
        self,
        weight_category: float = None,
        weight_sanction: float = None,
        weight_exposure: float = None,
        weight_usage: float = None,
    ):
        self.w_cat = weight_category if weight_category is not None else settings.WEIGHT_CATEGORY_SENSITIVITY
        self.w_sanc = weight_sanction if weight_sanction is not None else settings.WEIGHT_SANCTION_STATUS
        self.w_exp = weight_exposure if weight_exposure is not None else settings.WEIGHT_DATA_EXPOSURE
        self.w_use = weight_usage if weight_usage is not None else settings.WEIGHT_USAGE_SPREAD

        # Normalize weights to sum to 1.0
        total_w = self.w_cat + self.w_sanc + self.w_exp + self.w_use
        if total_w > 0:
            self.w_cat /= total_w
            self.w_sanc /= total_w
            self.w_exp /= total_w
            self.w_use /= total_w

    def _calculate_category_score(self, category: str) -> float:
        cat_lower = (category or "").lower().strip()
        for key, score in CATEGORY_SENSITIVITY_MAP.items():
            if key in cat_lower or cat_lower in key:
                return score
        return CATEGORY_SENSITIVITY_MAP["default"]

    def _calculate_sanction_score(self, sanction_status: str) -> float:
        s_lower = (sanction_status or "unknown").lower().strip()
        return SANCTION_STATUS_SCORES.get(s_lower, 0.70)

    def _calculate_exposure_score(self, data_exposure_bytes: int) -> float:
        """
        Logarithmic normalization for data volume exposure (0 bytes -> 0.0, 100MB+ -> 1.0).
        """
        if data_exposure_bytes <= 0:
            return 0.05
        # log10(1KB)=3, log10(1MB)=6, log10(100MB)=8
        log_bytes = math.log10(max(data_exposure_bytes, 10))
        # Map 3 (1KB) to 8 (100MB) into [0.1, 1.0]
        score = (log_bytes - 3.0) / (8.0 - 3.0)
        return max(0.05, min(1.0, score))

    def _calculate_usage_score(self, users_affected: int, event_count: int) -> float:
        """
        Evaluates organizational blast radius based on user count and frequency.
        """
        user_weight = min(users_affected / 25.0, 1.0)  # 25+ users = max user spread
        event_weight = min(event_count / 200.0, 1.0)   # 200+ events = max activity
        return 0.6 * user_weight + 0.4 * event_weight

    @staticmethod
    def get_tier(score: float) -> str:
        if score >= 80.0:
            return "critical"
        elif score >= 60.0:
            return "high"
        elif score >= 30.0:
            return "medium"
        else:
            return "low"

    def calculate(
        self,
        category: str,
        sanction_status: str,
        data_exposure_bytes: int,
        users_affected: int,
        event_count: int,
    ) -> Tuple[float, str, Dict[str, Any]]:
        """
        Calculates risk score (0-100), tier, and full signal breakdown.
        """
        s_cat = self._calculate_category_score(category)
        s_sanc = self._calculate_sanction_score(sanction_status)
        s_exp = self._calculate_exposure_score(data_exposure_bytes)
        s_use = self._calculate_usage_score(users_affected, event_count)

        raw_score = (
            (s_cat * self.w_cat) +
            (s_sanc * self.w_sanc) +
            (s_exp * self.w_exp) +
            (s_use * self.w_use)
        ) * 100.0

        score = round(max(0.0, min(100.0, raw_score)), 1)
        tier = self.get_tier(score)

        breakdown = {
            "category_sensitivity_score": round(s_cat * 100, 1),
            "category_sensitivity_weight": round(self.w_cat, 2),
            "sanction_status_score": round(s_sanc * 100, 1),
            "sanction_status_weight": round(self.w_sanc, 2),
            "data_exposure_score": round(s_exp * 100, 1),
            "data_exposure_weight": round(self.w_exp, 2),
            "usage_spread_score": round(s_use * 100, 1),
            "usage_spread_weight": round(self.w_use, 2),
            "explanation": (
                f"Risk score {score} ({tier.upper()}) computed via 4-signal heuristic model: "
                f"Category Sensitivity ({round(s_cat*100)}%), Sanction Risk ({round(s_sanc*100)}%), "
                f"Data Volume Exposure ({round(s_exp*100)}%), and Enterprise Usage Spread ({round(s_use*100)}%)."
            ),
        }

        return score, tier, breakdown


class RiskEngine:
    """
    Legacy wrapper class for RiskScoringEngine to preserve compatibility with 
    routes_scan.py and routes_findings.py.
    """
    def __init__(
        self,
        w_sensitivity: float,
        w_sanction: float,
        w_exposure: float,
        w_usage: float
    ):
        self.scoring_engine = RiskScoringEngine(
            weight_category=w_sensitivity,
            weight_sanction=w_sanction,
            weight_exposure=w_exposure,
            weight_usage=w_usage
        )

    def calculate_risk_score(
        self,
        category: str,
        sanction_status: str,
        data_exposure_bytes: int,
        users_affected: int,
        event_count: int = 0
    ) -> float:
        score, _, _ = self.scoring_engine.calculate(
            category=category,
            sanction_status=sanction_status,
            data_exposure_bytes=data_exposure_bytes,
            users_affected=users_affected,
            event_count=event_count
        )
        return score

    def get_risk_tier(self, score: float) -> str:
        return self.scoring_engine.get_tier(score)

    def get_breakdown_factors(
        self,
        category: str,
        sanction_status: str,
        data_exposure_bytes: int,
        users_affected: int,
        event_count: int = 0
    ) -> Dict[str, float]:
        _, _, breakdown = self.scoring_engine.calculate(
            category=category,
            sanction_status=sanction_status,
            data_exposure_bytes=data_exposure_bytes,
            users_affected=users_affected,
            event_count=event_count
        )
        return {
            "category_score": breakdown["category_sensitivity_score"],
            "sanction_score": breakdown["sanction_status_score"],
            "exposure_score": breakdown["data_exposure_score"],
            "usage_score": breakdown["usage_spread_score"]
        }


risk_engine = RiskScoringEngine()
