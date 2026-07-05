#!/usr/bin/env python
"""Run golden set evaluation against 50 test queries."""

import sys
sys.path.insert(0, '/c/Users/Anagha.e/project/RetailPolicy_Intelligence_Decision_Support_System/RetailPolicyAssistant')

from app.evaluation.golden_evaluator import GoldenSetEvaluator


if __name__ == "__main__":
    evaluator = GoldenSetEvaluator()
    results = evaluator.run()

    # Exit with error code if too many failures
    if results["accuracy"] < 80:
        sys.exit(1)
