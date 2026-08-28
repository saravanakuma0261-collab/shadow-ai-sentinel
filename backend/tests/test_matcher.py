import unittest
from app.fingerprint.matcher import FingerprintMatcher


class TestMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = FingerprintMatcher()

    def test_domain_exact_match(self):
        match = self.matcher.match_domain("chatgpt.com")
        self.assertIsNotNone(match)
        self.assertEqual(match["vendor"], "OpenAI")
        self.assertFalse(match["sanctioned"])

    def test_domain_subdomain_match(self):
        match = self.matcher.match_domain("api.openai.com")
        self.assertIsNotNone(match)
        self.assertEqual(match["vendor"], "OpenAI")

        match_deep = self.matcher.match_domain("us-east.v1.claude.ai")
        self.assertIsNotNone(match_deep)
        self.assertEqual(match_deep["vendor"], "Anthropic")

    def test_domain_normalization(self):
        match = self.matcher.match_domain("https://www.deepseek.com:443/chat")
        self.assertIsNotNone(match)
        self.assertEqual(match["vendor"], "DeepSeek")

    def test_domain_unknown(self):
        match = self.matcher.match_domain("random-corp-internal-portal.local")
        self.assertIsNone(match)

    def test_extension_matching(self):
        match = self.matcher.match_extension("Harpa AI Automation Agent")
        self.assertIsNotNone(match)
        self.assertEqual(match["vendor"], "HARPA AI")

        match_sub = self.matcher.match_extension("Monica - Your AI Copilot v6.0")
        self.assertIsNotNone(match_sub)
        self.assertFalse(match_sub["sanctioned"])


if __name__ == "__main__":
    unittest.main()
