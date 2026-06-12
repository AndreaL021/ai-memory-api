import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config.memory_capture import AUTO_PROMOTE_CONFIDENCE
from app.services.memory.memory_capture_service import extract_memory_candidate_drafts
from app.services.security.security_service import validate_normal_memory_content
from tests.quality_cases import CANDIDATE_CASES, SECRET_CASES


def print_section(title: str):
    print("")
    print("=" * 80)
    print(title)
    print("=" * 80)


def print_result(passed: bool):
    print(f"RESULT: {'PASS' if passed else 'FAIL'}")


def run_candidate_case(case: dict):
    drafts = extract_memory_candidate_drafts(case["input"])
    actual_types = [draft.memory_type for draft in drafts]
    passed = len(drafts) == case["expected_count"]

    for expected_type in case["expected_types"]:
        passed = passed and expected_type in actual_types

    if case.get("expected_promotable") is True:
        passed = passed and any(
            draft.confidence >= AUTO_PROMOTE_CONFIDENCE
            for draft in drafts
        )

    print_section(case["name"])
    print(f"INPUT: {case['input']}")
    print(
        "EXPECTED: "
        f"candidates={case['expected_count']}, "
        f"types={case['expected_types']}"
    )
    print(
        "ACTUAL: "
        f"candidates={len(drafts)}, "
        f"types={actual_types}"
    )

    for draft in drafts:
        print(
            "- "
            f"type={draft.memory_type}, "
            f"confidence={draft.confidence}, "
            f"promotable={draft.confidence >= AUTO_PROMOTE_CONFIDENCE}, "
            f"content={draft.content}, "
            f"signals={draft.signals}"
        )

    print_result(passed)
    return passed


def run_secret_case():
    case = SECRET_CASES[0]
    result = validate_normal_memory_content(case["input"])
    passed = (
        result["can_store"] == case["expected_can_store"]
        and result["security_level"] == case["expected_security_level"]
        and (not case["expected_redacted"] or "[REDACTED_SECRET]" in result["content"])
        and case["forbidden_text"] not in result["content"]
    )

    print_section(case["name"])
    print(f"INPUT: {case['input']}")
    print("EXPECTED: can_store=False, security_level=blocked_secret, raw secret removed")
    print(
        "ACTUAL: "
        f"can_store={result['can_store']}, "
        f"security_level={result['security_level']}, "
        f"content={result['content']}, "
        f"secret_count={result['secret_count']}"
    )
    print_result(passed)
    return passed


def main():
    results = [
        run_candidate_case(case)
        for case in CANDIDATE_CASES
    ]
    results.extend(run_secret_case() for _case in SECRET_CASES)

    passed = sum(1 for result in results if result)
    failed = len(results) - passed

    print_section("Summary")
    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
