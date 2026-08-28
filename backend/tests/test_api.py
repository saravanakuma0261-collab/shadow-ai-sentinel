import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.db.models import User, Finding, Scan
from app.auth.security import get_password_hash, create_access_token

client = TestClient(app)

class TestAPI(unittest.TestCase):
    def setUp(self):
        # Create 3 test users in memory
        self.mock_users = {
            "u1": User(
                id="u1", name="Test Admin", email="admin@test.com",
                password_hash=get_password_hash("AdminPass123!"), role="admin", is_active=True
            ),
            "u2": User(
                id="u2", name="Test Analyst", email="analyst@test.com",
                password_hash=get_password_hash("AnalystPass123!"), role="analyst", is_active=True
            ),
            "u3": User(
                id="u3", name="Test Viewer", email="viewer@test.com",
                password_hash=get_password_hash("ViewerPass123!"), role="viewer", is_active=True
            )
        }
        
        self.mock_scans = {}
        self.mock_findings = {
            "f1": Finding(id="f1", scan_id="s1", entity_type="domain", entity_value="test.com", 
                          category="test", vendor="test", sanction_status="unknown", 
                          data_exposure_bytes=0, users_affected=0, event_count=0, risk_score=50.0, risk_tier="medium")
        }

    def _mock_get_user_by_email(self, email: str):
        return next((u for u in self.mock_users.values() if u.email == email), None)

    def _mock_get_user_by_id(self, user_id: str):
        return self.mock_users.get(user_id)

    @staticmethod
    def get_token(email: str, role: str, user_id: str = "u1") -> str:
        return create_access_token({"sub": user_id, "email": email, "role": role, "name": email})

    @patch("app.auth.routes_auth.repository")
    def test_01_auth_login_and_jwt_role(self, mock_repo):
        mock_repo.get_user_by_email.side_effect = self._mock_get_user_by_email
        resp = client.post("/auth/login", json={"email": "viewer@test.com", "password": "ViewerPass123!"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["role"], "viewer")

    @patch("app.auth.dependencies.repository")
    def test_02_rbac_viewer_blocked_from_scan(self, mock_repo):
        mock_repo.get_user_by_id.side_effect = self._mock_get_user_by_id
        token = self.get_token("viewer@test.com", "viewer", user_id="u3")
        resp = client.post("/scan", json={"source_type": "combined"}, headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 403)
        self.assertIn("Access denied", resp.json()["detail"])

    @patch("app.auth.dependencies.repository")
    @patch("app.api.routes_scan.repository")
    def test_03_rbac_analyst_can_trigger_scan(self, mock_scan_repo, mock_auth_repo):
        mock_auth_repo.get_user_by_id.side_effect = self._mock_get_user_by_id
        test_scan = Scan(id="new_scan", source_type="combined", status="running", triggered_by="u2")
        mock_scan_repo.create_scan.return_value = test_scan
        mock_scan_repo.get_scan.return_value = test_scan
        mock_scan_repo.get_fingerprint_domains.return_value = []
        mock_scan_repo.get_fingerprint_extensions.return_value = []
        
        token = self.get_token("analyst@test.com", "analyst", user_id="u2")
        resp = client.post("/scan", json={"source_type": "combined"}, headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 202)

    @patch("app.auth.dependencies.repository")
    @patch("app.api.routes_findings.repository")
    def test_04_get_findings_accessible_by_viewer(self, mock_findings_repo, mock_auth_repo):
        mock_auth_repo.get_user_by_id.side_effect = self._mock_get_user_by_id
        mock_findings_repo.list_findings.return_value = list(self.mock_findings.values())

        token = self.get_token("viewer@test.com", "viewer", user_id="u3")
        resp = client.get("/findings", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 200)
        findings = resp.json()
        self.assertGreater(len(findings), 0)

    @patch("app.auth.dependencies.repository")
    @patch("app.api.routes_agent.repository")
    @patch("app.api.routes_agent.analyze_finding_with_ai")
    def test_05_investigate_finding_analyst(self, mock_ai, mock_agent_repo, mock_auth_repo):
        mock_auth_repo.get_user_by_id.side_effect = self._mock_get_user_by_id
        mock_agent_repo.get_finding.return_value = self.mock_findings["f1"]
        
        mock_ai.return_value = {
            "summary": "Mock summary",
            "recommendation": "monitor",
            "rationale": "Mock rationale",
            "confidence": 0.95
        }
        
        # We also need to mock create_agent_investigation since the endpoint saves it.
        from app.db.models import AgentInvestigation
        mock_agent_repo.create_agent_investigation.return_value = AgentInvestigation(
            id="inv1", finding_id="f1", summary="Mock summary", 
            recommendation="monitor", rationale="Mock rationale", confidence=0.95
        )

        token = self.get_token("analyst@test.com", "analyst", user_id="u2")
        resp = client.post("/agent/investigate/f1", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["recommendation"], "monitor")

    @patch("app.auth.dependencies.repository")
    @patch("app.admin.routes_users.repository")
    def test_06_admin_user_management_access(self, mock_users_repo, mock_auth_repo):
        mock_auth_repo.get_user_by_id.side_effect = self._mock_get_user_by_id
        mock_users_repo.list_users.return_value = list(self.mock_users.values())

        admin_token = self.get_token("admin@test.com", "admin", user_id="u1")
        viewer_token = self.get_token("viewer@test.com", "viewer", user_id="u3")

        # Viewer should receive 403 Forbidden
        resp_viewer = client.get("/admin/users", headers={"Authorization": f"Bearer {viewer_token}"})
        self.assertEqual(resp_viewer.status_code, 403)

        # Admin should receive 200 OK
        resp_admin = client.get("/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(resp_admin.status_code, 200)
        self.assertEqual(len(resp_admin.json()), 3)

    @patch("app.auth.dependencies.repository")
    @patch("app.admin.routes_users.repository")
    def test_07_admin_change_user_role(self, mock_users_repo, mock_auth_repo):
        mock_auth_repo.get_user_by_id.side_effect = self._mock_get_user_by_id
        mock_users_repo.get_user_by_id.return_value = self.mock_users["u3"]

        admin_token = self.get_token("admin@test.com", "admin", user_id="u1")
        resp = client.patch("/admin/users/u3/role", json={"role": "analyst"}, headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["role"], "analyst")


if __name__ == "__main__":
    unittest.main()
