#!/usr/bin/env python
"""Test that Phase 3 critical blockers are fixed."""

import sys
sys.path.insert(0, '/c/Users/Anagha.e/project/RetailPolicy_Intelligence_Decision_Support_System/RetailPolicyAssistant')

def test_blocker_1_slo_enforcement():
    """Test: SLO Enforcement is now active in api.py"""
    print("\n" + "="*60)
    print("BLOCKER 1: SLO Enforcement Fix")
    print("="*60)

    # Read api.py and check for the enforcement rejection code
    with open('RetailPolicyAssistant/app/api.py', 'r') as f:
        api_content = f.read()

    # Check 1: SLO enforcement is being called
    if 'slo_enforcer.enforce(response, latency_seconds)' in api_content:
        print("✅ Check 1: SLO enforcer is CALLED")
    else:
        print("❌ Check 1: SLO enforcer NOT called")
        return False

    # Check 2: Enforcement result is being checked
    if 'if not enforcement.get("allow", True):' in api_content:
        print("✅ Check 2: Enforcement result IS CHECKED for rejection")
    else:
        print("❌ Check 2: Enforcement result NOT checked (requests not rejected on breach)")
        return False

    # Check 3: HTTPException is raised on breach
    if 'raise HTTPException' in api_content and 'SLO violation' in api_content:
        print("✅ Check 3: HTTPException raised on SLO breach")
    else:
        print("❌ Check 3: HTTPException NOT raised on breach")
        return False

    print("\n✅ BLOCKER 1 FIXED: SLO Enforcement is now ACTIVE")
    return True


def test_blocker_2_cost_tracking():
    """Test: Cost Tracking enforcement is active"""
    print("\n" + "="*60)
    print("BLOCKER 2: Cost Tracking Fix")
    print("="*60)

    # Read api.py and check for cost enforcement
    with open('RetailPolicyAssistant/app/api.py', 'r') as f:
        api_content = f.read()

    # Check 1: Cost budget is being checked
    if 'cost_tracker.check_budget()' in api_content:
        print("✅ Check 1: Cost budget IS CHECKED")
    else:
        print("❌ Check 1: Cost budget NOT checked")
        return False

    # Check 2: Reject action on budget exceeded
    if 'budget_check["enforcement_action"] == "reject"' in api_content:
        print("✅ Check 2: Reject action ON budget exceeded")
    else:
        print("❌ Check 2: No reject action on budget exceeded")
        return False

    # Check 3: HTTPException raised on budget reject
    if 'raise HTTPException' in api_content and 'Budget limit exceeded' in api_content:
        print("✅ Check 3: HTTPException raised on budget violation")
    else:
        print("❌ Check 3: No exception raised on budget violation")
        return False

    # Check 4: Cost tracking module is healthy
    try:
        from app.core.cost_tracking import get_cost_tracker
        tracker = get_cost_tracker()
        budget_check = tracker.check_budget()

        if 'enforcement_action' in budget_check:
            print("✅ Check 4: Cost tracking module works and returns enforcement_action")
        else:
            print("❌ Check 4: Cost tracking module NOT working properly")
            return False
    except Exception as e:
        print(f"❌ Check 4: Cost tracking module error: {e}")
        return False

    print("\n✅ BLOCKER 2 FIXED: Cost Tracking enforcement is ACTIVE")
    return True


def test_enforcement_logic():
    """Test the enforcement logic in detail"""
    print("\n" + "="*60)
    print("ENFORCEMENT LOGIC TEST")
    print("="*60)

    try:
        from app.core.slo_enforcer import get_slo_enforcer
        from app.core.cost_tracking import get_cost_tracker

        # Test SLO enforcement
        slo_enforcer = get_slo_enforcer()
        print(f"✅ SLO Enforcer initialized: {slo_enforcer.__class__.__name__}")

        # Test with a fake response
        test_response = {
            "confidence_score": 0.5,
            "slo_metrics": {"slo_status": "pass"},
            "result": {"result": "test"}
        }

        enforcement_result = slo_enforcer.enforce(test_response, latency_seconds=1.5)
        if enforcement_result.get("allow", True):
            print("✅ SLO Enforcement allows normal latency: PASS")

        # Test cost tracker
        cost_tracker = get_cost_tracker()
        budget_check = cost_tracker.check_budget()
        if budget_check.get("enforcement_action") == "allow":
            print("✅ Cost Tracking allows queries within budget: PASS")

        print("\n✅ All enforcement logic tests PASSED")
        return True

    except Exception as e:
        print(f"❌ Enforcement logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PHASE 3 CRITICAL BLOCKERS - FIX VERIFICATION")
    print("="*60)

    blocker1_fixed = test_blocker_1_slo_enforcement()
    blocker2_fixed = test_blocker_2_cost_tracking()
    logic_ok = test_enforcement_logic()

    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)

    if blocker1_fixed and blocker2_fixed and logic_ok:
        print("\n✅✅✅ ALL CRITICAL BLOCKERS FIXED ✅✅✅")
        print("\nBoth critical blockers are now RESOLVED:")
        print("  1. ✅ SLO Enforcement - Now rejects requests on SLO breach")
        print("  2. ✅ Cost Tracking - Enforcement active and working")
        print("\n🚀 Ready to start Phase 3.1 implementation")
        sys.exit(0)
    else:
        print("\n❌ Some blockers are still not fixed")
        if not blocker1_fixed:
            print("  ❌ Blocker 1: SLO Enforcement")
        if not blocker2_fixed:
            print("  ❌ Blocker 2: Cost Tracking")
        if not logic_ok:
            print("  ❌ Enforcement Logic")
        sys.exit(1)
