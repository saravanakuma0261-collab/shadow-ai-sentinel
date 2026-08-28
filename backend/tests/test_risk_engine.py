import unittest
from app.scoring.risk_engine import RiskScoringEngine


class TestRiskEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RiskScoringEngine()

    def test_risk_score_calculation_critical(self):
        # Unsanctioned code assistant with high data exposure and usage spread
        score, tier, breakdown = self.engine.calculate(
            category="Code Assistant",
            sanction_status="unsanctioned",
            data_exposure_bytes=80000000,  # 80 MB
            users_affected=30,
            event_count=250,
        )
        self.assertGreaterEqual(score, 80.0)
        self.assertEqual(tier, "critical")
        self.assertIn("explanation", breakdown)
        self.assertGreater(breakdown["category_sensitivity_score"], 80.0)
        self.assertEqual(breakdown["sanction_status_score"], 100.0)

    def test_risk_score_calculation_low_sanctioned(self):
        # Sanctioned tool with low volume
        score, tier, breakdown = self.engine.calculate(
            category="Writing Assistant",
            sanction_status="sanctioned",
            data_exposure_bytes=5000,
            users_affected=1,
            event_count=2,
        )
        self.assertLess(score, 30.0)
        self.assertEqual(tier, "low")
        self.assertEqual(breakdown["sanction_status_score"], 10.0)

    def test_risk_tier_boundaries(self):
        self.assertEqual(self.engine.get_tier(85.0), "critical")
        self.assertEqual(self.engine.get_tier(80.0), "critical")
        self.assertEqual(self.engine.get_tier(79.9), "high")
        self.assertEqual(self.engine.get_tier(60.0), "high")
        self.assertEqual(self.engine.get_tier(59.9), "medium")
        self.assertEqual(self.engine.get_tier(30.0), "medium")
        self.assertEqual(self.engine.get_tier(29.9), "low")
        self.assertEqual(self.engine.get_tier(0.0), "low")


if __name__ == "__main__":
    unittest.main()
