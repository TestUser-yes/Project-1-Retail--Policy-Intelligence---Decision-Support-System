"""Test end-to-end orchestrator flow for SQL queries."""

import sys
from pathlib import Path
from sqlalchemy.orm import Session

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database.session import SessionLocal
from app.orchestrator import Orchestrator
from app.evaluation.golden_set import GOLDEN_SET


def test_orchestrator_sql_flow():
    """Test orchestrator with SQL queries."""
    print("=" * 80)
    print("TESTING ORCHESTRATOR END-TO-END FLOW - SQL QUERIES")
    print("=" * 80)

    # Get database session
    db = SessionLocal()

    try:
        # Create orchestrator
        orchestrator = Orchestrator(db)

        # Extract SQL queries from golden set
        sql_queries = [q for q in GOLDEN_SET if q.get("expected", {}).get("route") == "sql"]

        print(f"\nTesting {len(sql_queries)} SQL queries through orchestrator\n")

        passed = 0
        failed = 0

        for i, test_case in enumerate(sql_queries[:5], 1):  # Test first 5 for brevity
            query = test_case["query"]
            expected = test_case["expected"]

            print(f"Test {i}: {query}")

            # Run through orchestrator
            response = orchestrator.run(query)

            print(f"  Route: {response.get('route')} (expected: {expected['route']})")
            print(f"  Risk: {response.get('risk', {}).get('risk_level')} (expected: {expected['risk']})")
            print(f"  Escalate: {response.get('escalate')} (expected: {expected['escalate']})")
            print(f"  Confidence: {response.get('confidence_score')}")
            print(f"  Result: {response.get('result', {}).get('result', '')[:80]}...")

            # Check routing
            if response.get('route') == expected['route']:
                print("  [PASS] Correct routing")
                passed += 1
            else:
                print(f"  [FAIL] Wrong route. Expected {expected['route']}, got {response.get('route')}")
                failed += 1

            # Check if result is not generic fallback
            result_text = response.get('result', {}).get('result', '')
            if "No specific matches found for the query criteria" in result_text:
                print("  [FAIL] Got generic fallback response")
                failed += 1
            elif "Database query executed" in result_text and "No specific matches" in result_text:
                print("  [FAIL] Got generic database response")
                failed += 1
            else:
                print("  [PASS] Got specific result")
                passed += 1

            print()

        print("=" * 80)
        print(f"RESULTS: {passed} passed, {failed} failed")
        print("=" * 80)

        return failed == 0

    finally:
        db.close()


if __name__ == "__main__":
    try:
        success = test_orchestrator_sql_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
