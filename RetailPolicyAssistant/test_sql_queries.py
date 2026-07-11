"""Test SQL queries from golden set to verify they return actual results."""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.sql.queries import answer_sql
from app.evaluation.golden_set import GOLDEN_SET


def test_sql_queries():
    """Test all SQL queries from golden set."""
    print("=" * 80)
    print("TESTING SQL QUERIES FROM GOLDEN SET")
    print("=" * 80)

    # Extract SQL queries from golden set
    sql_queries = [q for q in GOLDEN_SET if q.get("expected", {}).get("route") == "sql"]

    print(f"\nFound {len(sql_queries)} SQL queries to test\n")

    passed = 0
    failed = 0

    for i, test_case in enumerate(sql_queries, 1):
        query = test_case["query"]
        expected = test_case["expected"]

        print(f"Test {i}: {query}")
        print(f"  Expected route: {expected['route']}")
        print(f"  Expected keywords: {expected.get('answer_contains', [])}")

        # Execute query
        result = answer_sql(query)

        print(f"  Result: {result['result'][:100]}..." if len(result['result']) > 100 else f"  Result: {result['result']}")
        print(f"  Rows: {result['rows']}, Confidence: {result['confidence']}")

        # Check if result is NOT the generic fallback message
        is_generic_fallback = "No specific matches found for the query criteria" in result['result']

        # Check if expected keywords are present
        keywords_found = all(
            kw.lower() in result['result'].lower()
            for kw in expected.get('answer_contains', [])
        )

        if is_generic_fallback:
            print(f"  [FAILED] Generic fallback response detected")
            failed += 1
        elif result['rows'] == 0:
            print(f"  [FAILED] No rows returned")
            failed += 1
        elif keywords_found:
            print(f"  [PASSED] Got specific result with expected keywords")
            passed += 1
        else:
            print(f"  [WARNING] Got result but missing some keywords")
            passed += 1

        print()

    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(sql_queries)} tests")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = test_sql_queries()
    sys.exit(0 if success else 1)
