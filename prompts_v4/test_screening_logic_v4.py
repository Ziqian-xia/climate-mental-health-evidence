import importlib.util
import pathlib
import sys
import types
import unittest


# The aggregation tests are offline and do not need the optional runtime dependencies.
sys.modules.setdefault("openpyxl", types.ModuleType("openpyxl"))
openai_stub = types.ModuleType("openai")
openai_stub.OpenAI = object
sys.modules.setdefault("openai", openai_stub)

MODULE_PATH = pathlib.Path(__file__).with_name("screen_excel_v4_deepseek.py")
SPEC = importlib.util.spec_from_file_location("screen_excel_v4_deepseek", MODULE_PATH)
screening = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(screening)


def module(topic, decision, code="NA", reason="test"):
    return {
        "topic": topic,
        "raw": {
            "decision": decision,
            "exclusion_code": code,
            "one_line_reason": reason,
        },
    }


class AggregationTests(unittest.TestCase):
    def test_unnamed_plausible_hazard_routes_to_review(self):
        router = {
            "candidate_topics": [],
            "needs_human_topic_review": True,
            "one_line_reason": "Unnamed natural disaster with mental-health outcome.",
        }
        decision, _ = screening.aggregate_screening(router, [])
        self.assertEqual(decision, "REVIEW")

    def test_empty_unflagged_router_result_excludes(self):
        router = {"candidate_topics": [], "needs_human_topic_review": False}
        decision, _ = screening.aggregate_screening(router, [])
        self.assertEqual(decision, "EXCLUDE")

    def test_string_false_is_not_truthy(self):
        router = {"candidate_topics": [], "needs_human_topic_review": "false"}
        decision, _ = screening.aggregate_screening(router, [])
        self.assertEqual(decision, "EXCLUDE")

    def test_clean_include_is_included(self):
        router = {"candidate_topics": ["temperature"]}
        decision, _ = screening.aggregate_screening(
            router, [module("temperature", "INCLUDE")]
        )
        self.assertEqual(decision, "INCLUDE")

    def test_include_plus_review_is_review(self):
        router = {"candidate_topics": ["temperature", "flood"]}
        modules = [
            module("temperature", "INCLUDE"),
            module("flood", "REVIEW"),
        ]
        decision, _ = screening.aggregate_screening(router, modules)
        self.assertEqual(decision, "REVIEW")

    def test_include_plus_module_error_is_review(self):
        router = {"candidate_topics": ["temperature", "flood"]}
        modules = [
            module("temperature", "INCLUDE"),
            {"topic": "flood", "raw": {"_error": "timeout"}},
        ]
        decision, _ = screening.aggregate_screening(router, modules)
        self.assertEqual(decision, "REVIEW")

    def test_unsupported_topic_is_review(self):
        router = {"candidate_topics": ["heavy_precipitation"]}
        decision, _ = screening.aggregate_screening(router, [])
        self.assertEqual(decision, "REVIEW")

    def test_missing_module_result_is_review(self):
        router = {"candidate_topics": ["drought"]}
        decision, _ = screening.aggregate_screening(router, [])
        self.assertEqual(decision, "REVIEW")

    def test_all_topic_exclusions_exclude(self):
        router = {"candidate_topics": ["wildfire", "flood"]}
        modules = [
            module("wildfire", "EXCLUDE", "wrong_exposure"),
            module("flood", "EXCLUDE", "wrong_outcome"),
        ]
        decision, _ = screening.aggregate_screening(router, modules)
        self.assertEqual(decision, "EXCLUDE")

    def test_invalid_non_exclude_code_forces_review(self):
        router = {"candidate_topics": ["cyclone"]}
        modules = [module("cyclone", "INCLUDE", "wrong_design")]
        decision, _ = screening.aggregate_screening(router, modules)
        self.assertEqual(decision, "REVIEW")

    def test_exclude_without_valid_code_forces_review(self):
        router = {"candidate_topics": ["cyclone"]}
        modules = [module("cyclone", "EXCLUDE")]
        decision, _ = screening.aggregate_screening(router, modules)
        self.assertEqual(decision, "REVIEW")


if __name__ == "__main__":
    unittest.main()
