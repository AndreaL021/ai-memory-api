import unittest

from app.config.memory_capture import AUTO_PROMOTE_CONFIDENCE
from app.services.memory.memory_capture_service import extract_memory_candidate_drafts
from app.services.security.security_service import validate_normal_memory_content
from tests.quality_cases import CANDIDATE_CASES, SECRET_CASES


class MemoryQualityTests(unittest.TestCase):
    def test_candidate_cases(self):
        for case in CANDIDATE_CASES:
            with self.subTest(case=case["name"]):
                drafts = extract_memory_candidate_drafts(case["input"])
                actual_types = [draft.memory_type for draft in drafts]

                self.assertEqual(case["expected_count"], len(drafts))
                for expected_type in case["expected_types"]:
                    self.assertIn(expected_type, actual_types)

                if case.get("expected_promotable") is True:
                    self.assertTrue(
                        any(draft.confidence >= AUTO_PROMOTE_CONFIDENCE for draft in drafts)
                    )

    def test_secret_cases(self):
        for case in SECRET_CASES:
            with self.subTest(case=case["name"]):
                result = validate_normal_memory_content(case["input"])

                self.assertEqual(case["expected_can_store"], result["can_store"])
                self.assertEqual(case["expected_security_level"], result["security_level"])

                if case["expected_redacted"]:
                    self.assertIn("[REDACTED_SECRET]", result["content"])

                self.assertNotIn(case["forbidden_text"], result["content"])


if __name__ == "__main__":
    unittest.main()
